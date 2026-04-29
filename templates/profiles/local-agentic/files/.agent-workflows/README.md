# Local Agent Workflows

These workflows are local-first and agent-tool agnostic. They do not require
GitHub Actions, hosted CI, or a specific coding assistant.

Use them from AmpCode, Codex, Claude Code, Aider, Cline, another local agent, or
a human terminal session.

## Files

- `REVIEW.md`: local review rules and evidence bar.
- `.agent-workflows/repo-review.md`: focused local repo-review workflow.
- `.agent-workflows/tdd-red-green-receipt.md`: TDD evidence format.
- `.agent-workflows/schemas/session-receipt.schema.json`: JSON receipt schema.
- `.agent-workflows/schemas/safe-output.schema.json`: safe agent output schema.

## Local Commands

Run these from the repository root:

```bash
make docs-check
make agent-docs-lint
make agent-docs-localize
```

If your repo does not use `make`, run the scripts directly:

```bash
python3 scripts/check_doc_impact.py --working-tree
python3 scripts/lint_agent_docs.py --strict-paths
python3 scripts/localize_doc_impact.py --working-tree --json
```

## Tool-Neutral Rule

Native folders like `.codex/prompts/`, `.cursor/rules/`, or `CLAUDE.md` are
optional adapters. The local workflow must still be understandable from this
folder, `AGENTS.md`, `REVIEW.md`, and the scripts.
