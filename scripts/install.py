#!/usr/bin/env python3

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "common"
PROFILES = ROOT / "templates" / "profiles"
DEFAULT_PROFILE = "minimal"

FILE_MAP = {
    "doc-contract.json": "doc-contract.json",
    "AGENTS.md": "AGENTS.md",
    "documentation-contract.md": "docs/documentation-contract.md",
    "adr-template.md": "docs/adr/0000-template.md",
    "pull_request_template.md": ".github/pull_request_template.md",
    "docs-workflow.yml": ".github/workflows/docs.yml",
    "pre-commit-config.yaml": ".pre-commit-config.yaml",
    "Makefile": "Makefile",
}


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
        copy_file(src, dst, force or dst in written_targets)


def main():
    parser = argparse.ArgumentParser(description="Install doc-contract-kit into a target repo")
    parser.add_argument("target", help="Path to target repository")
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help=f"Template profile to install. Defaults to {DEFAULT_PROFILE}.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    ensure_git_repo(target)

    written_targets = set()
    for src_name, dst_name in FILE_MAP.items():
        dst = target / dst_name
        if copy_file(TEMPLATES / src_name, dst, args.force):
            written_targets.add(dst)

    check_doc_dst = target / "scripts/check_doc_impact.py"
    if copy_file(ROOT / "scripts" / "check_doc_impact.py", check_doc_dst, args.force):
        written_targets.add(check_doc_dst)

    install_profile_files(args.profile, target, args.force, written_targets)

    print("\nInstall complete.")
    print(f"Profile: {args.profile}")
    print("Next steps:")
    print(f"  cd {target}")
    print("  make docs-check")
    print("  pre-commit install")
    if args.profile == "keryx-forced":
        print("  sync staged changes through Keryx before committing")
    if args.profile == "test-first":
        print("  review docs/testing-strategy.md and .codex/prompts/tdd/ before the next behavior change")
    print("  git status")


if __name__ == "__main__":
    main()
