#!/usr/bin/env python3

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FILES = [
    "AGENTS.md",
    "REVIEW.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
]

DEFAULT_GLOBS = [
    ".agent-workflows/**/*.md",
    ".codex/prompts/**/*.md",
    ".cursor/rules/**/*",
    ".continue/rules/**/*.md",
    ".windsurf/rules/**/*.md",
]

IGNORED_PATH_PARTS = {
    ".agent-workflows/runs",
}

HIDDEN_CODEPOINTS = {
    "\u200b": "zero width space",
    "\u200c": "zero width non-joiner",
    "\u200d": "zero width joiner",
    "\ufeff": "byte-order mark",
    "\u202a": "left-to-right embedding",
    "\u202b": "right-to-left embedding",
    "\u202c": "pop directional formatting",
    "\u202d": "left-to-right override",
    "\u202e": "right-to-left override",
    "\u2066": "left-to-right isolate",
    "\u2067": "right-to-left isolate",
    "\u2068": "first-strong isolate",
    "\u2069": "pop directional isolate",
}

CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PATH_LIKE_RE = re.compile(
    r"(^\.?/)|(/)|(\.(md|json|py|ya?ml|toml|txt|ini|cfg|sh)$)|"
    r"^(AGENTS|REVIEW|CLAUDE|GEMINI|Makefile)(\.md)?$"
)

OPTIONAL_AGENT_ADAPTERS = (
    "README.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursor/rules/",
    ".continue/rules/",
    ".windsurf/rules/",
)

GENERATED_OUTPUT_EXAMPLES = {
    "session-receipt.json",
}


@dataclass
class Issue:
    severity: str
    path: Path
    message: str


def normalize_candidate(value: str):
    candidate = value.strip().strip(",:;)(").strip()
    if not candidate:
        return None
    if candidate.startswith(("http://", "https://", "mailto:")):
        return None
    if candidate.startswith(("path/to/", "/path/to/")):
        return None
    if candidate.endswith(":line") or candidate.endswith(":line-number"):
        return None
    if candidate in GENERATED_OUTPUT_EXAMPLES:
        return None
    if candidate in OPTIONAL_AGENT_ADAPTERS:
        return None
    if " " in candidate:
        return None
    if candidate.startswith(("$", "<", "{")):
        return None
    if any(marker in candidate for marker in ("<", ">", "*")):
        return None
    return candidate


def is_path_like(value: str):
    return bool(PATH_LIKE_RE.search(value))


def candidate_path_roots(root: Path, instruction_file: Path):
    roots = [root, instruction_file.parent]
    for prompt_root in (root / ".codex" / "prompts", root / ".agent-workflows"):
        try:
            instruction_file.relative_to(prompt_root)
        except ValueError:
            continue
        roots.append(prompt_root)
    return roots


def discover_files(root: Path, explicit_files: list[str]):
    paths = []
    for value in explicit_files or DEFAULT_FILES:
        path = root / value
        if path.is_file():
            paths.append(path)

    if not explicit_files:
        for pattern in DEFAULT_GLOBS:
            for path in root.glob(pattern):
                rel = str(path.relative_to(root))
                if any(rel == ignored or rel.startswith(f"{ignored}/") for ignored in IGNORED_PATH_PARTS):
                    continue
                if path.is_file():
                    paths.append(path)

    return sorted({path.resolve() for path in paths})


def check_hidden_chars(path: Path, text: str):
    issues = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for char, name in HIDDEN_CODEPOINTS.items():
            if char in line:
                issues.append(Issue("error", path, f"hidden Unicode {name} at line {line_number}"))
    return issues


def referenced_paths(text: str):
    values = []
    values.extend(match.group(1) for match in CODE_SPAN_RE.finditer(text))
    values.extend(match.group(1) for match in MARKDOWN_LINK_RE.finditer(text))

    for value in values:
        candidate = normalize_candidate(value)
        if candidate and is_path_like(candidate):
            yield candidate


def check_referenced_paths(root: Path, path: Path, text: str, strict_paths: bool):
    issues = []
    for candidate in referenced_paths(text):
        normalized = candidate.rstrip("/")
        if not normalized:
            continue
        if normalized.startswith("#"):
            continue
        if "://" in normalized:
            continue

        possible_targets = []
        escaped = False
        for base in candidate_path_roots(root, path):
            target = (base / normalized).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                escaped = True
                continue
            possible_targets.append(target)

        if possible_targets and any(target.exists() for target in possible_targets):
            continue

        if not possible_targets and escaped:
            issues.append(Issue("error", path, f"path reference escapes repo: {candidate}"))
        else:
            severity = "error" if strict_paths else "warning"
            issues.append(Issue(severity, path, f"referenced path does not exist: {candidate}"))
    return issues


def check_file(root: Path, path: Path, strict_paths: bool):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Issue("error", path, "file is not valid UTF-8")]

    issues = []
    issues.extend(check_hidden_chars(path, text))
    issues.extend(check_referenced_paths(root, path, text, strict_paths))
    return issues


def parse_args():
    parser = argparse.ArgumentParser(description="Lint local agent instruction files")
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument(
        "--file",
        action="append",
        dest="files",
        help="Specific instruction file to inspect, relative to root. Repeat as needed.",
    )
    parser.add_argument(
        "--strict-paths",
        action="store_true",
        help="Fail when path-like references do not exist. Without this flag, missing references are warnings.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    files = discover_files(root, args.files)

    if not files:
        print("No agent instruction files found.")
        return 0

    all_issues = []
    for path in files:
        all_issues.extend(check_file(root, path, args.strict_paths))

    for issue in all_issues:
        rel = issue.path.relative_to(root)
        print(f"{issue.severity.upper()} {rel}: {issue.message}")

    errors = [issue for issue in all_issues if issue.severity == "error"]
    if errors:
        print(f"Agent instruction lint failed with {len(errors)} error(s).")
        return 1

    warnings = [issue for issue in all_issues if issue.severity == "warning"]
    if warnings:
        print(f"Agent instruction lint passed with {len(warnings)} warning(s).")
        return 0

    print(f"Agent instruction lint passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
