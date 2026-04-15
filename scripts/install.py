#!/usr/bin/env python3

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "common"

FILE_MAP = {
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
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"WRITE {dst}")


def main():
    parser = argparse.ArgumentParser(description="Install doc-contract-kit into a target repo")
    parser.add_argument("target", help="Path to target repository")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    ensure_git_repo(target)

    for src_name, dst_name in FILE_MAP.items():
        copy_file(TEMPLATES / src_name, target / dst_name, args.force)

    copy_file(ROOT / "scripts" / "check_doc_impact.py", target / "scripts/check_doc_impact.py", args.force)

    print("\nInstall complete.")
    print("Next steps:")
    print(f"  cd {target}")
    print("  make docs-check")
    print("  git status")


if __name__ == "__main__":
    main()
