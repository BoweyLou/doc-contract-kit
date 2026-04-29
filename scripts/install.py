#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "common"
PROFILES = ROOT / "templates" / "profiles"
DEFAULT_PROFILE = "minimal"
KIT_VERSION = "0.2.0"
PRESETS = {
    "minimal": ["minimal"],
    "learning": ["minimal", "review-prompts"],
    "test-first": ["minimal", "test-first"],
    "agentic": ["minimal", "local-agentic", "review-prompts", "test-first"],
    "strict-agentic": ["minimal", "local-agentic", "review-prompts", "test-first", "keryx-forced"],
}

FILE_MAP = {
    "doc-contract.json": "doc-contract.json",
    "AGENTS.md": "AGENTS.md",
    "REVIEW.md": "REVIEW.md",
    "documentation-contract.md": "docs/documentation-contract.md",
    "adr-template.md": "docs/adr/0000-template.md",
    "pull_request_template.md": ".github/pull_request_template.md",
    "docs-workflow.yml": ".github/workflows/docs.yml",
    "pre-commit-config.yaml": ".pre-commit-config.yaml",
    "Makefile": "Makefile",
    "session-receipt.schema.json": "schemas/session-receipt.schema.json",
    "persona-manifest.schema.json": "schemas/persona-manifest.schema.json",
    "safe-output.schema.json": ".agent-workflows/schemas/safe-output.schema.json",
}

CORE_SCRIPTS = [
    "check_doc_impact.py",
    "lint_agent_docs.py",
    "localize_doc_impact.py",
]


def ensure_git_repo(target: Path):
    if not (target / ".git").exists():
        raise SystemExit(f"Target is not a git repository: {target}")


def copy_file(src: Path, dst: Path, force: bool):
    if dst.exists() and not force:
        print(f"SKIP {dst} (already exists)")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"WRITE {dst}")
    return True


def load_profile(name: str):
    profile_dir = PROFILES / name
    manifest_path = profile_dir / "manifest.json"
    if not manifest_path.exists():
        available = ", ".join(sorted(path.name for path in PROFILES.iterdir() if path.is_dir()))
        raise SystemExit(f"Unknown profile: {name}. Available profiles: {available}")

    try:
        with manifest_path.open(encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid profile manifest: {manifest_path}: {exc}") from exc

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


def install_profile_files(profile_name: str, target: Path, force: bool, written_targets: set[Path]):
    profile_dir, files = load_profile(profile_name)
    for entry in files:
        if not isinstance(entry, dict) or "source" not in entry or "target" not in entry:
            raise SystemExit(f"Invalid file entry in profile: {profile_name}")

        dst = target / entry["target"]
        src = resolve_profile_source(profile_dir, entry["source"])
        if copy_file(src, dst, force or dst in written_targets):
            written_targets.add(dst)


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
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def write_install_receipt(target: Path, profiles: list[str], preset: str | None):
    receipt = {
        "schema_version": 1,
        "kit_version": KIT_VERSION,
        "installed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "preset": preset,
        "profiles": profiles,
        "source_commits": {
            "doc-contract-kit": current_git_commit(),
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

    written_targets = set()
    for src_name, dst_name in FILE_MAP.items():
        dst = target / dst_name
        if copy_file(TEMPLATES / src_name, dst, args.force):
            written_targets.add(dst)

    for script_name in CORE_SCRIPTS:
        script_dst = target / "scripts" / script_name
        if copy_file(ROOT / "scripts" / script_name, script_dst, args.force):
            written_targets.add(script_dst)

    for profile in profiles:
        install_profile_files(profile, target, args.force, written_targets)

    write_install_receipt(target, profiles, args.preset)

    print("\nInstall complete.")
    print(f"Profiles: {', '.join(profiles)}")
    if args.preset:
        print(f"Preset: {args.preset}")
    print("Next steps:")
    print(f"  cd {target}")
    print("  make docs-check")
    print("  pre-commit install")
    if "keryx-forced" in profiles:
        print("  sync staged changes through Keryx before committing")
    if "review-prompts" in profiles:
        print("  run make agent-review or make agent-learn when you want agent guidance")
    if "test-first" in profiles:
        print("  review docs/testing-strategy.md and .codex/prompts/tdd/ before the next behavior change")
    if "local-agentic" in profiles:
        print("  run make agent-docs-lint and make agent-docs-localize for local-only agent checks")
    print("  git status")


if __name__ == "__main__":
    main()
