# Agent Workflow Operations

This repository is set up for local-first agentic development. The installed
workflow files are intended to work from a normal shell and from local coding
agents such as Codex, AmpCode, Claude Code, Aider, or Cline.

## Local Commands

Use these commands before committing agent-generated or agent-assisted work:

```bash
make docs-check
make agent-docs-lint
make agent-docs-localize
make agent-verify
```

`make agent-verify` is the default local gate. It runs the available
documentation and agent-instruction checks for the installed profile.

## Workflow Files

- `AGENTS.md` defines repo-local operating rules for coding agents.
- `REVIEW.md` defines the review contract.
- `.agent-workflows/` contains tool-agnostic workflow guidance and receipt
  schemas.
- `.codex/prompts/` contains reusable prompts. The files can be read by other
  agents or used manually; they are not limited to Codex.
- `.github/workflows/docs.yml` is an optional hosted adapter for repos that can
  use GitHub Actions. Local verification does not depend on it.

## Locked-Down Repositories

For older on-prem Git servers or work environments without hosted CI, keep the
local commands as the source of truth. The GitHub workflow file may be ignored,
removed, or replaced with a local server equivalent if the repository cannot use
GitHub Actions.

If the workflow, scripts, build gates, or operational runbooks change, update
this document or the relevant file under `docs/ops/`, `docs/deploy/`, or
`docs/runbooks/`.
