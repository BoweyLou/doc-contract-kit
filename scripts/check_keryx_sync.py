#!/usr/bin/env python3

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CONFIG = ".keryx/config.json"
DEFAULT_RECEIPT = ".keryx/sync.json"
SCHEMA_VERSION = 1


def run(cmd, *, cwd=None, text=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=text)
    if result.returncode != 0:
        detail = result.stderr or result.stdout
        raise RuntimeError(detail.strip())
    return result.stdout


def normalize_path(path):
    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def git_root():
    return Path(run(["git", "rev-parse", "--show-toplevel"]).strip())


def current_head():
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "UNBORN"
    return result.stdout.strip()


def staged_changed_files():
    output = run(["git", "diff", "--cached", "--name-only"])
    return sorted({normalize_path(line) for line in output.splitlines() if line.strip()})


def read_index_bytes(path):
    result = subprocess.run(["git", "show", f":{path}"], capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout


def read_worktree_bytes(path):
    file_path = Path(path)
    if not file_path.is_file():
        return None
    return file_path.read_bytes()


def hash_paths(paths, *, prefer_index=False):
    digest = hashlib.sha256()
    digest.update(b"keryx-sync-v1\0")

    for path in sorted({normalize_path(path) for path in paths if normalize_path(path)}):
        data = read_index_bytes(path) if prefer_index else None
        if data is None:
            data = read_worktree_bytes(path)
        if data is None:
            data = b"<missing>"

        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")

    return digest.hexdigest()


def load_config(path):
    config_path = Path(path)
    if not config_path.exists():
        raise SystemExit(f"Missing Keryx config: {path}")

    try:
        with config_path.open(encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid Keryx config in {path}: {exc}") from exc

    if not isinstance(config, dict):
        raise SystemExit(f"Invalid Keryx config in {path}: top-level value must be an object")

    return config


def receipt_path_from_config(config, fallback):
    return normalize_path(config.get("receipt_path", fallback))


def mirror_paths_from_config(config):
    paths = config.get("mirror_paths", [])
    if not isinstance(paths, list):
        raise SystemExit("Invalid Keryx config: mirror_paths must be a list")
    return [normalize_path(path) for path in paths]


def build_state(config, receipt_path):
    staged_files = staged_changed_files()
    staged_without_receipt = [path for path in staged_files if path != receipt_path]
    mirror_paths = mirror_paths_from_config(config)

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "forced",
        "repo_head": current_head(),
        "staged_tree_hash": hash_paths(staged_without_receipt, prefer_index=True),
        "docs_hash": hash_paths(mirror_paths, prefer_index=True),
        "mirror_paths": mirror_paths,
        "staged_files": staged_without_receipt,
        "receipt_path": receipt_path,
    }


def write_receipt(config, receipt_path, source):
    state = build_state(config, receipt_path)
    receipt = {
        **state,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "keryx_vault_target": config.get("keryx_vault_target", ""),
        "source": source,
    }

    path = Path(receipt_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote Keryx sync receipt: {receipt_path}")


def load_receipt(path):
    receipt_file = Path(path)
    if not receipt_file.exists():
        raise SystemExit(f"Missing Keryx sync receipt: {path}")

    try:
        with receipt_file.open(encoding="utf-8") as f:
            receipt = json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid Keryx sync receipt in {path}: {exc}") from exc

    if not isinstance(receipt, dict):
        raise SystemExit(f"Invalid Keryx sync receipt in {path}: top-level value must be an object")

    return receipt


def validate_receipt(config, receipt_path):
    staged_files = staged_changed_files()
    staged_without_receipt = [path for path in staged_files if path != receipt_path]

    if not staged_without_receipt:
        print("No staged project files detected for Keryx sync.")
        return

    require_receipt_staged = config.get("require_receipt_staged", True)
    if require_receipt_staged and receipt_path not in staged_files:
        raise SystemExit(f"Keryx sync receipt must be staged: {receipt_path}")

    receipt = load_receipt(receipt_path)
    state = build_state(config, receipt_path)

    required_fields = [
        "schema_version",
        "mode",
        "repo_head",
        "staged_tree_hash",
        "docs_hash",
        "mirror_paths",
        "synced_at",
        "keryx_vault_target",
    ]
    missing = [field for field in required_fields if not receipt.get(field)]
    if missing:
        raise SystemExit(f"Keryx sync receipt is missing fields: {', '.join(missing)}")

    mismatches = []
    for field in ["schema_version", "mode", "repo_head", "staged_tree_hash", "docs_hash", "mirror_paths"]:
        if receipt.get(field) != state[field]:
            mismatches.append(field)

    if mismatches:
        print("Keryx sync receipt is stale.")
        for field in mismatches:
            print(f" - {field}")
        print("Sync the current staged repo state through Keryx, then stage the updated receipt.")
        sys.exit(1)

    print("Keryx sync receipt is current.")


def parse_args():
    parser = argparse.ArgumentParser(description="Validate the forced Keryx sync receipt")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help=f"Defaults to {DEFAULT_CONFIG}.")
    parser.add_argument("--receipt", default=None, help=f"Defaults to receipt_path from config or {DEFAULT_RECEIPT}.")
    parser.add_argument("--staged", action="store_true", help="Validate staged commit state.")
    parser.add_argument(
        "--write-receipt",
        action="store_true",
        help="Write a receipt for the current staged state. Intended for Keryx adapters.",
    )
    parser.add_argument("--source", default="keryx", help="Receipt source label used with --write-receipt.")
    return parser.parse_args()


def main():
    args = parse_args()
    root = git_root()
    try:
        import os

        os.chdir(root)
    except OSError as exc:
        raise SystemExit(str(exc)) from exc

    config = load_config(args.config)
    receipt_path = normalize_path(args.receipt or receipt_path_from_config(config, DEFAULT_RECEIPT))

    if args.write_receipt:
        write_receipt(config, receipt_path, args.source)
        return

    validate_receipt(config, receipt_path)


if __name__ == "__main__":
    main()
