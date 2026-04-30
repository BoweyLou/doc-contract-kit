#!/usr/bin/env python3

import argparse
import re
from datetime import date
from pathlib import Path

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def version_path(root: Path):
    return root / "VERSION"


def changelog_path(root: Path):
    return root / "CHANGELOG.md"


def read_version(root: Path):
    path = version_path(root)
    if not path.exists():
        raise SystemExit("Missing VERSION")
    return path.read_text(encoding="utf-8").strip()


def validate_version(value: str):
    match = SEMVER_RE.match(value)
    if not match:
        raise SystemExit(f"Invalid SemVer in VERSION: {value}")
    return tuple(int(part) for part in match.groups())


def bump_version(value: str, bump: str):
    major, minor, patch = validate_version(value)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"Unknown bump: {bump}")


def ensure_changelog(root: Path):
    path = changelog_path(root)
    if not path.exists():
        path.write_text("# Changelog\n", encoding="utf-8")
    return path


def prepend_changelog_entry(root: Path, new_version: str, old_version: str):
    path = ensure_changelog(root)
    text = path.read_text(encoding="utf-8")
    heading = f"## {new_version} - {date.today().isoformat()}\n\n- TODO: describe changes since {old_version}.\n\n"
    if text.startswith("# Changelog\n\n"):
        text = text.replace("# Changelog\n\n", f"# Changelog\n\n{heading}", 1)
    elif text.startswith("# Changelog\n"):
        text = text.replace("# Changelog\n", f"# Changelog\n\n{heading}", 1)
    else:
        text = f"# Changelog\n\n{heading}{text}"
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Manage local repository SemVer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    subparsers.add_parser("check")
    bump_parser = subparsers.add_parser("bump")
    bump_parser.add_argument("--bump", choices=["patch", "minor", "major"], default="patch")
    args = parser.parse_args()

    root = Path.cwd()
    current = read_version(root)
    validate_version(current)

    if args.command == "status":
        print(f"version: {current}")
        return 0
    if args.command == "check":
        print(f"VERSION is valid SemVer: {current}")
        return 0

    new_version = bump_version(current, args.bump)
    version_path(root).write_text(new_version + "\n", encoding="utf-8")
    prepend_changelog_entry(root, new_version, current)
    print(f"Bumped version: {current} -> {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
