#!/usr/bin/env python3

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"_error": str(exc)}


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None


def sha256_path(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_git_commit(root: Path):
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return current_git_commit_from_files(root)
    return result.stdout.strip() or current_git_commit_from_files(root)


def current_git_commit_from_files(root: Path):
    git_dir = root / ".git"
    if git_dir.is_file():
        value = read_text(git_dir) or ""
        if value.startswith("gitdir:"):
            candidate = Path(value.removeprefix("gitdir:").strip())
            git_dir = candidate if candidate.is_absolute() else (root / candidate)
    head = read_text(git_dir / "HEAD")
    if not head:
        return None
    if head.startswith("ref:"):
        ref = head.removeprefix("ref:").strip()
        ref_value = read_text(git_dir / ref)
        if ref_value:
            return ref_value
        packed_refs = git_dir / "packed-refs"
        try:
            for line in packed_refs.read_text(encoding="utf-8").splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                commit, _, name = line.partition(" ")
                if name == ref:
                    return commit
        except FileNotFoundError:
            return None
        return None
    return head


def local_prompt_snapshot(kit_root: Path):
    metadata = read_json(kit_root / "agent-workflow-kit.snapshot.json") or {}
    if isinstance(metadata, dict) and "_error" in metadata:
        return metadata
    return {
        "name": metadata.get("name") or "agent-workflow-kit",
        "version": metadata.get("version") or "unversioned",
        "source_ref": metadata.get("source_ref"),
        "snapshot_sha256": metadata.get("snapshot_sha256"),
    }


def local_kit_state(kit_root: Path):
    return {
        "version": read_text(kit_root / "VERSION") or "unknown",
        "source_ref": current_git_commit(kit_root),
        "prompt_snapshot": local_prompt_snapshot(kit_root),
    }


def short_ref(value):
    return value[:12] if isinstance(value, str) and value else "unknown"


def snapshot_from_install(receipt, manifest):
    if isinstance(receipt, dict) and isinstance(receipt.get("prompt_snapshot"), dict):
        return receipt["prompt_snapshot"]
    if isinstance(manifest, dict) and isinstance(manifest.get("prompt_snapshot"), dict):
        return manifest["prompt_snapshot"]
    components = receipt.get("source_components", {}) if isinstance(receipt, dict) else {}
    snapshot = components.get("agent-workflow-kit") if isinstance(components, dict) else None
    return snapshot if isinstance(snapshot, dict) else None


def managed_file_status(root: Path, manifest):
    if not isinstance(manifest, dict):
        return None
    files = manifest.get("files", [])
    managed = [item for item in files if isinstance(item, dict) and item.get("managed")]
    missing = []
    modified = []
    for item in managed:
        rel_path = item.get("path")
        expected = item.get("installed_sha256")
        if not rel_path:
            continue
        path = root / rel_path
        if not path.exists():
            missing.append(rel_path)
        elif expected and sha256_path(path) != expected:
            modified.append(rel_path)
    return {
        "managed": len(managed),
        "missing": missing,
        "modified": modified,
    }


def print_update_comparison(receipt, manifest, kit_root: Path | None):
    if not kit_root:
        print("update check: pass KIT=/path/to/repo-contract-kit to compare against a local checkout")
        return

    local = local_kit_state(kit_root)
    installed_version = receipt.get("source_version") or receipt.get("kit_version") or "unknown"
    installed_ref = receipt.get("source_ref") or receipt.get("source_commits", {}).get("repo-contract-kit")
    print(f"local kit version: {local['version']}")
    print(f"local kit source ref: {short_ref(local['source_ref'])}")
    if installed_version != local["version"]:
        print("kit update: available")
    elif installed_ref and local["source_ref"]:
        print(f"kit update: {'available' if installed_ref != local['source_ref'] else 'current'}")
    elif installed_ref and not local["source_ref"]:
        print("kit update: unknown (local source ref unavailable)")
    else:
        print("kit update: current")

    installed_snapshot = snapshot_from_install(receipt, manifest)
    local_snapshot = local["prompt_snapshot"]
    if not installed_snapshot:
        print("prompt snapshot update: unknown (installed metadata missing)")
        return
    if isinstance(local_snapshot, dict) and "_error" in local_snapshot:
        print(f"prompt snapshot update: unknown ({local_snapshot['_error']})")
        return
    snapshot_changed = (
        installed_snapshot.get("snapshot_sha256") != local_snapshot.get("snapshot_sha256")
        or installed_snapshot.get("source_ref") != local_snapshot.get("source_ref")
        or installed_snapshot.get("version") != local_snapshot.get("version")
    )
    print(f"local prompt snapshot ref: {short_ref(local_snapshot.get('source_ref'))}")
    if not local_snapshot.get("snapshot_sha256") and not local_snapshot.get("source_ref"):
        print("prompt snapshot update: unknown (local snapshot metadata incomplete)")
    else:
        print(f"prompt snapshot update: {'available' if snapshot_changed else 'current'}")


def main():
    parser = argparse.ArgumentParser(description="Show installed repo-contract-kit status")
    parser.add_argument("--kit", help="Optional local repo-contract-kit checkout to compare against")
    args = parser.parse_args()

    root = Path.cwd()
    receipt = read_json(root / ".doc-contract-kit" / "install.json")
    manifest = read_json(root / ".doc-contract-kit" / "manifest.json")
    version_path = root / "VERSION"
    target_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "missing"

    if not receipt:
        print("repo-contract-kit: not installed or missing .doc-contract-kit/install.json")
        return 1
    if isinstance(receipt, dict) and "_error" in receipt:
        print(f"repo-contract-kit: invalid install receipt: {receipt['_error']}")
        return 1

    print(f"repo-contract-kit installed version: {receipt.get('source_version') or receipt.get('kit_version') or 'unknown'}")
    print(f"source ref: {short_ref(receipt.get('source_ref') or receipt.get('source_commits', {}).get('repo-contract-kit'))}")
    print(f"preset: {receipt.get('preset') or 'none'}")
    print(f"profiles: {', '.join(receipt.get('profiles', [])) or 'none'}")
    print(f"target repo version: {target_version}")

    prompt_snapshot = snapshot_from_install(receipt, manifest)
    if prompt_snapshot:
        print(
            "agent-workflow-kit snapshot: "
            f"{prompt_snapshot.get('version') or 'unknown'} "
            f"ref {short_ref(prompt_snapshot.get('source_ref'))} "
            f"hash {short_ref(prompt_snapshot.get('snapshot_sha256'))}"
        )
    else:
        print("agent-workflow-kit snapshot: unknown")

    if not manifest:
        print("managed manifest: missing")
    elif isinstance(manifest, dict) and "_error" in manifest:
        print(f"managed manifest: invalid: {manifest['_error']}")
        return 1
    else:
        files = manifest.get("files", [])
        managed = sum(1 for item in files if item.get("managed"))
        target_owned = sum(1 for item in files if item.get("owner") == "target")
        print(f"managed manifest: present ({managed} kit-managed, {target_owned} target-owned files)")
        status = managed_file_status(root, manifest)
        if status:
            if status["missing"] or status["modified"]:
                print(
                    "managed file status: "
                    f"{len(status['modified'])} modified, {len(status['missing'])} missing"
                )
            else:
                print("managed file status: clean")

    kit_root = Path(args.kit).expanduser().resolve() if args.kit else None
    print_update_comparison(receipt, manifest, kit_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
