# Local Agent Workflows

These workflows are local-first and agent-tool agnostic. They do not require
GitHub Actions, hosted CI, or a specific coding assistant.

Use them from AmpCode, Codex, Claude Code, Aider, Cline, another local agent, or
a human terminal session.

## Start an Agent

Give the agent this brief from the repository root:

```text
Read AGENTS.md, REVIEW.md, and .agent-workflows/README.md.
Then follow .agent-workflows/repo-review.md in bootstrap mode.
Use the installed personas and prompts under .codex/prompts/ where useful.
Start by running make agent-verify and make agent-docs-localize.
Produce a findings backlog before editing code.
```

For ongoing work after the first bootstrap review, change `bootstrap mode` to
`drift mode`, `pull-request mode`, `release-gate mode`,
`learning-comments mode`, or `test-first mode`.

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

## Prompt Source

The prompts under `.codex/prompts/` are copied into this repo by
`repo-contract-kit` so local agents can work without fetching another
repository. The canonical prompt library lives in
the public `agent-workflow-kit` repository; refresh this repo by rerunning the
installer from a newer `repo-contract-kit` checkout.
