#!/usr/bin/env python3

import argparse
import json
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
    rule_id: str = "agent-docs"


SECRET_PATTERNS = [
    ("secret-token", re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
]

UNSAFE_COMMAND_PATTERNS = [
    ("destructive-rm", re.compile(r"\brm\s+-[^\n]*r[^\n]*f\b|\brm\s+-[^\n]*f[^\n]*r\b")),
    ("git-reset-hard", re.compile(r"\bgit\s+reset\s+--hard\b")),
    ("git-checkout-path", re.compile(r"\bgit\s+checkout\s+--\b")),
    ("git-clean-force", re.compile(r"\bgit\s+clean\s+-[^\n]*[fd][^\n]*\b")),
    ("force-push", re.compile(r"\bgit\s+push\s+--force(?:-with-lease)?\b")),
    ("curl-pipe-shell", re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(sh|bash)\b")),
    ("world-writable", re.compile(r"\bchmod\s+-R\s+777\b")),
]

WILDCARD_PERMISSION_PATTERNS = [
    ("danger-full-access", re.compile(r"\bdanger-full-access\b|--dangerously-skip-permissions")),
    ("unrestricted-tools", re.compile(r"(?i)\b(unrestricted|allow all|all tools|any tool|wildcard)\b.{0,40}\b(tool|permission|network|filesystem|mcp|shell)\b")),
]

ACCOUNT_MUTATION_PATTERNS = [
    ("browser-account-mutation", re.compile(r"(?i)\b(post|like|follow|bookmark|dm|direct message|send message|comment)\b.{0,40}\b(account|browser|social|x\.com|twitter)\b")),
    ("captcha-bypass", re.compile(r"(?i)\b(captcha|2fa|two-factor)\b.{0,30}\b(bypass|avoid|work around)\b")),
]

RULE_WORD_RE = re.compile(r"\b(must|always|never|required|require|should)\b", re.IGNORECASE)
PROVENANCE_WORD_RE = re.compile(r"\b(because|when|if|unless|so that|to prevent|risk|failure|regression|evidence)\b", re.IGNORECASE)
MAKE_TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?![=])")
COMMAND_BLOCK_RE = re.compile(r"```(?:bash|sh|shell|zsh|text)?\n(.*?)```", re.DOTALL)
COMMAND_LINE_RE = re.compile(r"^\s*(?:[$]\s*)?(make|python3?|uv|npm|pnpm|yarn|git)\b(.+)$")
CONTRADICTION_PAIRS = [
    (
        "git-commit",
        re.compile(r"\b(do not|never|deny|must not)\b.{0,40}\b(commit|git commit)\b", re.IGNORECASE),
        re.compile(r"\b(may|can|should|must|allow)\b.{0,40}\b(commit|git commit)\b", re.IGNORECASE),
    ),
    (
        "git-push",
        re.compile(r"\b(do not|never|deny|must not)\b.{0,40}\b(push|git push)\b", re.IGNORECASE),
        re.compile(r"\b(may|can|should|must|allow)\b.{0,40}\b(push|git push)\b", re.IGNORECASE),
    ),
    (
        "file-edits",
        re.compile(r"\b(do not|never|deny|must not)\b.{0,40}\b(edit|write|modify)\b.{0,20}\b(file|files|repo|repository)\b", re.IGNORECASE),
        re.compile(r"\b(may|can|should|must|allow)\b.{0,40}\b(edit|write|modify)\b.{0,20}\b(file|files|repo|repository)\b", re.IGNORECASE),
    ),
    (
        "network",
        re.compile(r"\b(do not|never|deny|must not)\b.{0,40}\b(network|internet|curl|wget)\b", re.IGNORECASE),
        re.compile(r"\b(may|can|should|must|allow)\b.{0,40}\b(network|internet|curl|wget)\b", re.IGNORECASE),
    ),
]


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
                issues.append(Issue("error", path, f"hidden Unicode {name} at line {line_number}", "hidden-unicode"))
    return issues


def line_has_placeholder(line: str):
    lowered = line.lower()
    return any(value in lowered for value in ("example", "placeholder", "<", ">", "your_", "changeme", "redacted"))


def check_secrets_and_unsafe_guidance(path: Path, text: str):
    issues = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line_has_placeholder(line):
            continue
        for rule_id, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                issues.append(Issue("error", path, f"possible secret or credential at line {line_number}", rule_id))
        for rule_id, pattern in UNSAFE_COMMAND_PATTERNS:
            if pattern.search(line):
                issues.append(Issue("error", path, f"unsafe command guidance at line {line_number}", rule_id))
        for rule_id, pattern in WILDCARD_PERMISSION_PATTERNS:
            if pattern.search(line):
                issues.append(Issue("error", path, f"wildcard or unrestricted permission guidance at line {line_number}", rule_id))
        for rule_id, pattern in ACCOUNT_MUTATION_PATTERNS:
            if "do not" in line.lower() or "deny" in line.lower() or "no " in line.lower():
                continue
            if pattern.search(line):
                issues.append(Issue("error", path, f"unsafe account-mutation guidance at line {line_number}", rule_id))
    return issues


def make_targets(root: Path):
    targets = set()
    makefile = root / "Makefile"
    if not makefile.exists():
        return targets
    try:
        text = makefile.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return targets
    for line in text.splitlines():
        match = MAKE_TARGET_RE.match(line)
        if match and not match.group(1).startswith("."):
            targets.add(match.group(1))
    return targets


def command_lines(text: str):
    for block in COMMAND_BLOCK_RE.finditer(text):
        for line in block.group(1).splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                yield stripped
    for value in CODE_SPAN_RE.finditer(text):
        candidate = value.group(1).strip()
        if COMMAND_LINE_RE.match(candidate):
            yield candidate


def check_command_references(root: Path, path: Path, text: str):
    issues = []
    targets = make_targets(root)
    for line in command_lines(text):
        match = COMMAND_LINE_RE.match(line)
        if not match:
            continue
        command, rest = match.group(1), match.group(2).strip()
        parts = rest.split()
        if command == "make":
            explicit_targets = [part for part in parts if "=" not in part and not part.startswith("-")]
            for target in explicit_targets:
                if targets and target not in targets:
                    issues.append(Issue("error", path, f"referenced Make target does not exist: {target}", "stale-command"))
        if command in {"python", "python3"}:
            script = next((part.strip("'\"") for part in parts if part.endswith(".py") and not part.startswith("$")), None)
            if script:
                candidate = (root / script).resolve()
                try:
                    candidate.relative_to(root.resolve())
                except ValueError:
                    continue
                if not candidate.exists():
                    issues.append(Issue("error", path, f"referenced Python script does not exist: {script}", "stale-command"))
    return issues


def check_rule_bloat_and_provenance(path: Path, text: str):
    issues = []
    lines = text.splitlines()
    if len(lines) > 900:
        issues.append(Issue("warning", path, f"instruction file is long ({len(lines)} lines); consider splitting scoped rules", "rule-bloat"))
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if len(stripped) > 260:
            issues.append(Issue("warning", path, f"long instruction line at {line_number}", "rule-bloat"))
        if stripped.startswith(("-", "*")) and RULE_WORD_RE.search(stripped) and not PROVENANCE_WORD_RE.search(stripped):
            issues.append(Issue("warning", path, f"rule-like bullet lacks context/provenance at line {line_number}", "rule-provenance"))
    return issues


def check_contradictions(path: Path, text: str):
    issues = []
    normalized = " ".join(text.split())
    for topic, deny_re, allow_re in CONTRADICTION_PAIRS:
        if deny_re.search(normalized) and allow_re.search(normalized):
            issues.append(
                Issue(
                    "warning",
                    path,
                    f"possible contradictory instruction about {topic}; split by trust profile or approval state",
                    "contradiction",
                )
            )
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
                issues.append(Issue("error", path, f"path reference escapes repo: {candidate}", "path-escape"))
        else:
            severity = "error" if strict_paths else "warning"
            issues.append(Issue(severity, path, f"referenced path does not exist: {candidate}", "missing-path"))
    return issues


def check_file(root: Path, path: Path, strict_paths: bool):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Issue("error", path, "file is not valid UTF-8")]

    issues = []
    issues.extend(check_hidden_chars(path, text))
    issues.extend(check_referenced_paths(root, path, text, strict_paths))
    issues.extend(check_command_references(root, path, text))
    issues.extend(check_secrets_and_unsafe_guidance(path, text))
    issues.extend(check_contradictions(path, text))
    issues.extend(check_rule_bloat_and_provenance(path, text))
    return issues


def issue_dict(issue: Issue, root: Path):
    return {
        "severity": issue.severity,
        "rule_id": issue.rule_id,
        "path": str(issue.path.relative_to(root)),
        "message": issue.message,
    }


def sarif_payload(issues: list[Issue], root: Path):
    rules = {}
    results = []
    for issue in issues:
        rules.setdefault(issue.rule_id, {"id": issue.rule_id, "name": issue.rule_id})
        results.append(
            {
                "ruleId": issue.rule_id,
                "level": "error" if issue.severity == "error" else "warning",
                "message": {"text": issue.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": str(issue.path.relative_to(root))}
                        }
                    }
                ],
            }
        )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "repo-contract-kit agent instruction linter",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }


def print_issues(issues: list[Issue], root: Path, output_format: str, file_count: int):
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    if output_format == "json":
        print(
            json.dumps(
                {
                    "status": "fail" if errors else "pass",
                    "files_checked": file_count,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "issues": [issue_dict(issue, root) for issue in issues],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return
    if output_format == "sarif":
        print(json.dumps(sarif_payload(issues, root), indent=2, sort_keys=True))
        return
    for issue in issues:
        rel = issue.path.relative_to(root)
        print(f"{issue.severity.upper()} {rel}: [{issue.rule_id}] {issue.message}")


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
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Output format for local use or code-scanning adapters.",
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

    print_issues(all_issues, root, args.format, len(files))

    errors = [issue for issue in all_issues if issue.severity == "error"]
    if errors:
        if args.format == "text":
            print(f"Agent instruction lint failed with {len(errors)} error(s).")
        return 1

    warnings = [issue for issue in all_issues if issue.severity == "warning"]
    if warnings:
        if args.format == "text":
            print(f"Agent instruction lint passed with {len(warnings)} warning(s).")
        return 0

    if args.format == "text":
        print(f"Agent instruction lint passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
