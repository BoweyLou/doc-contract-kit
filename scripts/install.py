#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import stat
from pathlib import Path

# Script flow:
# 1. Resolve the target git repo and requested install profiles.
# 2. Expand profile entries into concrete template files and script assets.
# 3. Copy or compare managed files, preserving metadata needed for updates.
# 4. Write install manifests and receipts so future status/update checks know what changed.
#
# Function guide:
# - ensure_git_repo/read_kit_version/sha256_path/read_json_file collect basic inputs.
# - prompt_snapshot_metadata/source_components/relative_source describe source kit state.
# - copy_path/git_blob_bytes/source_bytes/copy_file handle template copying and checksums.
# - load_profile/resolve_profile_source/common_entries/core_script_entries/profile_entries build install entries.
# - desired_entries/final_entries_by_target/split_profiles/unique_ordered/resolve_requested_profiles resolve requested profiles.
# - current_git_commit/current_source_ref/manifest_file_entry/write_manifest/write_install_receipt/main perform install bookkeeping.

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "common"
PROFILES = ROOT / "templates" / "profiles"
VERSION_FILE = ROOT / "VERSION"
PROMPT_SNAPSHOT_FILE = ROOT / "agent-workflow-kit.snapshot.json"
DEFAULT_PROFILE = "minimal"
PRESETS = {
    "minimal": ["minimal"],
    "learning": ["minimal", "review-prompts"],
    "test-first": ["minimal", "test-first"],
    "agentic": ["minimal", "local-agentic", "review-prompts", "test-first", "versioning"],
}

FILE_MAP = {
    "doc-contract.json": "doc-contract.json",
    "AGENTS.md": "AGENTS.md",
    "REVIEW.md": "REVIEW.md",
    "documentation-contract.md": "docs/documentation-contract.md",
    "ops-agent-workflow.md": "docs/ops/agent-workflow.md",
    "agent-instruction-hygiene.md": "docs/ops/agent-instruction-hygiene.md",
    "agent-tool-network-allowlist.md": "docs/ops/agent-tool-network-allowlist.md",
    "adr-template.md": "docs/adr/0000-template.md",
    "pull_request_template.md": ".github/pull_request_template.md",
    "docs-workflow.yml": ".github/workflows/docs.yml",
    "agent-review-readonly.yml": ".github/workflows/agent-review-readonly.yml",
    "pre-commit-config.yaml": ".pre-commit-config.yaml",
    "Makefile": "Makefile",
    "session-receipt.schema.json": "schemas/session-receipt.schema.json",
    "review-synthesis.schema.json": "schemas/review-synthesis.schema.json",
    "review-risk.schema.json": "schemas/review-risk.schema.json",
    "task-packet.schema.json": "schemas/task-packet.schema.json",
    "persona-manifest.schema.json": "schemas/persona-manifest.schema.json",
    "agent-permission-policy.schema.json": "schemas/agent-permission-policy.schema.json",
    "agent-permission-policy.json": ".agent-workflows/agent-permission-policy.json",
    "instruction-budgets.json": ".agent-workflows/instruction-budgets.json",
    "safe-output.schema.json": ".agent-workflows/schemas/safe-output.schema.json",
    "agent-runs.gitignore": ".agent-workflows/runs/.gitignore",
    "updates.gitignore": ".doc-contract-kit/updates/.gitignore",
}

CORE_SCRIPTS = [
    "agent_start.py",
    "agent_review_run.py",
    "classify_review_risk.py",
    "check_doc_impact.py",
    "kit_status.py",
    "lint_agent_docs.py",
    "localize_doc_impact.py",
    "verify_agent_receipt.py",
    "version.py",
]

TARGET_OWNED_PATHS = {
    "VERSION",
    "CHANGELOG.md",
}

PROMPT_SNAPSHOT_PATHS = [
    "templates/profiles/review-prompts/files/.codex/prompts",
    "templates/profiles/test-first/files/.codex/prompts",
    "templates/profiles/local-agentic/files/.agent-workflows",
    "templates/common/persona-manifest.schema.json",
    "templates/common/review-synthesis.schema.json",
    "templates/common/review-risk.schema.json",
    "templates/common/session-receipt.schema.json",
    "templates/common/task-packet.schema.json",
]


def ensure_git_repo(target: Path):
    if not (target / ".git").exists():
        raise SystemExit(f"Target is not a git repository: {target}")


def read_kit_version():
    try:
        value = VERSION_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "0.0.0-local"
    return value or "0.0.0-local"


def sha256_path(path: Path):
    return hashlib.sha256(source_bytes(path)).hexdigest()


def read_json_file(path: Path):
    try:
        return json.loads(source_bytes(path).decode("utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def prompt_snapshot_metadata():
    metadata = read_json_file(PROMPT_SNAPSHOT_FILE)
    paths = metadata.get("snapshot_paths") or PROMPT_SNAPSHOT_PATHS
    snapshot = {
        "name": metadata.get("name") or "agent-workflow-kit",
        "version": metadata.get("version") or "unversioned",
        "source_url": metadata.get("source_url") or "https://github.com/BoweyLou/agent-workflow-kit",
        "source_ref": metadata.get("source_ref"),
        "snapshot_sha256": metadata.get("snapshot_sha256"),
        "snapshot_paths": paths,
    }
    for key in ("source_prompt_root", "generated_adapter", "vendored_at", "notes"):
        if metadata.get(key):
            snapshot[key] = metadata[key]
    return snapshot


def source_components():
    kit_ref = current_source_ref()
    prompt_snapshot = prompt_snapshot_metadata()
    return {
        "repo-contract-kit": {
            "version": read_kit_version(),
            "source_ref": kit_ref,
        },
        "agent-workflow-kit": prompt_snapshot,
    }


def relative_source(path: Path):
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def copy_path(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = source_bytes(src)
    dst.write_bytes(data)
    shutil.copymode(src, dst)


def git_blob_bytes(src: Path):
    try:
        rel = src.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"HEAD:{rel}"],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def source_bytes(src: Path):
    flags = getattr(src.stat(), "st_flags", 0)
    # Some iCloud/FileProvider checkouts expose tracked vendored prompt files as
    # hidden placeholders that can block on normal reads. Git blobs are the
    # committed source of truth for those template snapshots.
    placeholder_flags = stat.UF_HIDDEN | stat.UF_COMPRESSED | getattr(stat, "SF_DATALESS", 0)
    if flags & placeholder_flags:
        data = git_blob_bytes(src)
        if data is not None:
            return data
        raise SystemExit(
            f"Source template appears to be a macOS placeholder and could not be materialized: {src}"
        )
    return src.read_bytes()


def copy_file(src: Path, dst: Path, force: bool):
    if dst.exists() and not force:
        print(f"SKIP {dst} (already exists)")
        return False
    copy_path(src, dst)
    print(f"WRITE {dst}")
    return True


def load_profile(name: str):
    profile_dir = PROFILES / name
    manifest_path = profile_dir / "manifest.json"
    if not manifest_path.exists():
        available = ", ".join(sorted(path.name for path in PROFILES.iterdir() if path.is_dir()))
        raise SystemExit(f"Unknown profile: {name}. Available profiles: {available}")

    manifest = read_json_file(manifest_path)

    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise SystemExit(f"Invalid profile manifest: {manifest_path}: files must be a list")

    return profile_dir, files


def resolve_profile_source(profile_dir: Path, source: str):
    src = (profile_dir / source).resolve()
    root = ROOT.resolve()
    if src != root and root not in src.parents:
        raise SystemExit(f"Profile source escapes kit root: {source}")
    if not src.exists():
        raise SystemExit(f"Profile source does not exist: {source}")
    return src


def common_entries():
    entries = []
    for src_name, dst_name in FILE_MAP.items():
        entries.append(
            {
                "profile": "common",
                "source": TEMPLATES / src_name,
                "source_name": src_name,
                "target": dst_name,
            }
        )
    return entries


def core_script_entries():
    return [
        {
            "profile": "core-scripts",
            "source": ROOT / "scripts" / script_name,
            "source_name": f"scripts/{script_name}",
            "target": f"scripts/{script_name}",
        }
        for script_name in CORE_SCRIPTS
    ]


def profile_entries(profile_name: str):
    profile_dir, files = load_profile(profile_name)
    entries = []
    for entry in files:
        if not isinstance(entry, dict) or "source" not in entry or "target" not in entry:
            raise SystemExit(f"Invalid file entry in profile: {profile_name}")

        src = resolve_profile_source(profile_dir, entry["source"])
        entries.append(
            {
                "profile": profile_name,
                "source": src,
                "source_name": entry["source"],
                "target": entry["target"],
            }
        )
    return entries


def desired_entries(profiles: list[str]):
    entries = []
    entries.extend(common_entries())
    entries.extend(core_script_entries())
    for profile in profiles:
        entries.extend(profile_entries(profile))
    return entries


def final_entries_by_target(entries: list[dict]):
    final = {}
    for entry in entries:
        final[entry["target"]] = entry
    return final


def split_profiles(value: str):
    profiles = [part.strip() for part in value.split(",") if part.strip()]
    if not profiles:
        raise SystemExit("No profiles specified")
    return profiles


def unique_ordered(items: list[str]):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def resolve_requested_profiles(args):
    if args.preset:
        if args.preset not in PRESETS:
            available = ", ".join(sorted(PRESETS))
            raise SystemExit(f"Unknown preset: {args.preset}. Available presets: {available}")
        profiles = list(PRESETS[args.preset])
    elif args.profiles:
        profiles = split_profiles(args.profiles)
    elif args.profile:
        profiles = [args.profile]
    else:
        profiles = [DEFAULT_PROFILE]

    return unique_ordered(profiles)


def current_git_commit():
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def current_source_ref():
    return current_git_commit()


def manifest_file_entry(target: Path, entry: dict, was_written: bool):
    rel_target = entry["target"]
    target_path = target / rel_target
    source_path = entry["source"]
    target_owned = rel_target in TARGET_OWNED_PATHS
    managed = bool(was_written and not target_owned)
    owner = "kit" if managed else "target"

    if not target_path.exists():
        return None

    return {
        "path": rel_target,
        "profile": entry["profile"],
        "source": relative_source(source_path),
        "source_sha256": sha256_path(source_path),
        "installed_sha256": sha256_path(target_path),
        "managed": managed,
        "owner": owner,
    }


def write_manifest(target: Path, entries: list[dict], written_targets: set[str], profiles: list[str], preset: str | None):
    final_entries = final_entries_by_target(entries)
    files = []
    for rel_target, entry in sorted(final_entries.items()):
        file_entry = manifest_file_entry(target, entry, rel_target in written_targets)
        if file_entry:
            files.append(file_entry)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "schema_version": 1,
        "kit_version": read_kit_version(),
        "source_version": read_kit_version(),
        "source_ref": current_source_ref(),
        "source_components": source_components(),
        "prompt_snapshot": prompt_snapshot_metadata(),
        "generated_at": generated_at,
        "preset": preset,
        "profiles": profiles,
        "files": files,
    }
    manifest_path = target / ".doc-contract-kit" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WRITE {manifest_path}")


def write_install_receipt(target: Path, profiles: list[str], preset: str | None):
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    receipt = {
        "schema_version": 1,
        "kit_version": read_kit_version(),
        "source_version": read_kit_version(),
        "source_ref": current_source_ref(),
        "source_components": source_components(),
        "prompt_snapshot": prompt_snapshot_metadata(),
        "installed_at": timestamp,
        "last_updated_at": timestamp,
        "preset": preset,
        "profiles": profiles,
        "source_commits": {
            "repo-contract-kit": current_source_ref(),
            "agent-workflow-kit": prompt_snapshot_metadata().get("source_ref"),
        },
    }
    receipt_path = target / ".doc-contract-kit" / "install.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WRITE {receipt_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Install repo-contract-kit files into a target repo"
    )
    parser.add_argument("target", help="Path to target repository")
    parser.add_argument(
        "--profile",
        default=None,
        help=f"Single template profile to install. Defaults to {DEFAULT_PROFILE}.",
    )
    parser.add_argument(
        "--profiles",
        help="Comma-separated template profiles to compose, for example review-prompts,test-first.",
    )
    parser.add_argument(
        "--preset",
        help=f"Named profile set. Available presets: {', '.join(sorted(PRESETS))}.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    ensure_git_repo(target)
    profiles = resolve_requested_profiles(args)

    written_target_paths = set()
    written_target_abs = set()
    entries = desired_entries(profiles)
    for entry in entries:
        dst = target / entry["target"]
        if copy_file(entry["source"], dst, args.force or dst in written_target_abs):
            written_target_abs.add(dst)
            written_target_paths.add(entry["target"])

    write_install_receipt(target, profiles, args.preset)
    write_manifest(target, entries, written_target_paths, profiles, args.preset)

    print("\nInstall complete.")
    print(f"Profiles: {', '.join(profiles)}")
    if args.preset:
        print(f"Preset: {args.preset}")
    print("Next steps:")
    print(f"  cd {target}")
    print("  make agent-start")
    print("  make kit-status")
    print("  make docs-check")
    print("  pre-commit install")
    if "review-prompts" in profiles:
        print("  run make agent-review, make agent-run-review, or make agent-learn when you want agent guidance")
    if "test-first" in profiles:
        print("  review docs/testing-strategy.md and .codex/prompts/tdd/ before the next behavior change")
    if "local-agentic" in profiles:
        print("  run make agent-docs-lint and make agent-docs-localize for local-only agent checks")
    if "versioning" in profiles:
        print("  run make version-check before release-impacting changes")
    print("  git status")


if __name__ == "__main__":
    main()
