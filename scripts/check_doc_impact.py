#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

DOC_FILES = {
    "contract": "docs/documentation-contract.md",
    "agents": "AGENTS.md",
}

DOC_PATH_PREFIXES = [
    "docs/",
    "README.md",
    "AGENTS.md",
]

IMPACT_PATH_RULES = {
    "api": ["api/", "openapi/", "schema/"],
    "cli": ["cli/"],
    "config": ["config/", ".env", "settings"],
    "ops": ["deploy/", ".github/workflows/", "infra/", "terraform/", "helm/"],
}


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def get_changed_files():
    attempts = [
        ["git", "merge-base", "HEAD", "origin/main"],
        ["git", "merge-base", "HEAD", "origin/master"],
    ]

    for merge_base_cmd in attempts:
        try:
            base = run(merge_base_cmd)
            output = run(["git", "diff", "--name-only", f"{base}...HEAD"])
            files = [line.strip() for line in output.splitlines() if line.strip()]
            if files:
                return files
        except Exception:
            pass

    try:
        output = run(["git", "diff", "--name-only", "HEAD~1..HEAD"])
        files = [line.strip() for line in output.splitlines() if line.strip()]
        if files:
            return files
    except Exception:
        pass

    return []


def file_exists(path):
    return Path(path).exists()


def touches_docs(files):
    for f in files:
        if f == "README.md":
            return True
        for prefix in DOC_PATH_PREFIXES:
            if f.startswith(prefix):
                return True
    return False


def classify_changes(files):
    categories = set()
    for f in files:
        lower = f.lower()
        if lower.startswith("docs/") or lower == "readme.md" or lower == "agents.md":
            continue
        if lower.startswith("tests/"):
            continue
        for category, patterns in IMPACT_PATH_RULES.items():
            for pattern in patterns:
                if pattern in lower:
                    categories.add(category)
    return categories


def main():
    for _, path in DOC_FILES.items():
        if not file_exists(path):
            print(f"Missing required file: {path}")
            sys.exit(1)

    changed_files = get_changed_files()
    if not changed_files:
        print("No changed files detected.")
        return

    categories = classify_changes(changed_files)
    docs_changed = touches_docs(changed_files)

    print("Changed files:")
    for f in changed_files:
        print(f" - {f}")

    if not categories:
        print("No doc-impacting paths detected.")
        print("If this is an internal-only change, make sure the PR says so.")
        return

    print(f"Detected possible doc-impact categories: {', '.join(sorted(categories))}")

    if not docs_changed:
        print("\nDocumentation impact detected, but no docs files changed.")
        print("Please update relevant docs, or explicitly declare why no docs are needed.")
        sys.exit(1)

    print("Documentation impact check passed.")


if __name__ == "__main__":
    main()
