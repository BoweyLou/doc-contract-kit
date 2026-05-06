# Agent Workflow Operations

This repository is set up for local-first agentic development. The installed
workflow files are intended to work from a normal shell and from local coding
agents such as Codex, AmpCode, Claude Code, Aider, or Cline.

## Local Commands

Use these commands before committing agent-generated or agent-assisted work:

```bash
make agent-start
make kit-status
make docs-check
make agent-docs-lint
make agent-docs-localize
make agent-task-packet
make agent-verify
make version-check
```

`make agent-verify` is the default local gate. It runs the available
documentation and agent-instruction checks for the installed profile.

`make agent-start` is the lowest-friction session entrypoint. It writes an
ignored packet under `.agent-workflows/runs/` containing the agent brief,
machine-readable startup context, latest ADR context, discovery check results,
recommended prompts/personas, kit version context, target repo version context,
and a receipt template. Discovery check failures are recorded as warnings so
inherited or messy repos can still be reviewed.

`make kit-status` shows the installed kit version, source ref, selected profiles,
manifest status, and target repo version.

`make kit-update KIT=/path/to/repo-contract-kit` updates local kit-managed files
from a newer local checkout. Clean managed files are replaced. Customized managed
files are preserved and proposed replacements are written under
`.doc-contract-kit/updates/`.

`make agent-task-packet` points the agent at the task-packet prompt. Use it when
a backlog row, issue, accepted review finding, external planning item, or broad
human request needs to become scoped executable work before implementation
starts.

`make version-check` validates the target repo `VERSION` file when the
versioning profile is installed. Use `make version-bump BUMP=patch|minor|major`
only when the accepted change needs a target repo version bump.

## Workflow Files

- `AGENTS.md` defines repo-local operating rules for coding agents.
- `REVIEW.md` defines the review contract.
- `.agent-workflows/` contains tool-agnostic workflow guidance and receipt
  schemas.
- `.codex/prompts/` contains reusable prompts. The files can be read by other
  agents or used manually; they are not limited to Codex.
- `schemas/task-packet.schema.json` defines the machine-readable handoff from
  backlog item to agent task.
- `.github/workflows/docs.yml` is an optional hosted adapter for repos that can
  use GitHub Actions. Local verification does not depend on it.
- `.doc-contract-kit/manifest.json` records managed files and hashes for safe
  local updates.
- `VERSION`, `CHANGELOG.md`, and `docs/versioning.md` define local target repo
  versioning when the versioning profile is installed.

## Locked-Down Repositories

For older on-prem Git servers or work environments without hosted CI, keep the
local commands as the source of truth. The GitHub workflow file may be ignored,
removed, or replaced with a local server equivalent if the repository cannot use
GitHub Actions.

If the workflow, scripts, build gates, or operational runbooks change, update
this document or the relevant file under `docs/ops/`, `docs/deploy/`, or
`docs/runbooks/`.
