# Rollout Guide

This guide refers to **repo-contract-kit**. Existing install receipts still use
the `.doc-contract-kit/` directory for compatibility.

If this is all new to you, adopt it in layers.

## Suggested order

1. Install the templates only with `--preset minimal`.
2. Get used to AGENTS.md and the documentation contract.
3. Start running `make docs-check` locally.
4. Add `--preset learning` when you want review and learning prompts in the repo.
5. Add `--preset test-first` or `--preset agentic` when you want executable-spec prompts and local agent workflows.
6. Run `make kit-status`, optionally
   `make kit-status KIT=/path/to/repo-contract-kit`, and `make version-check`
   so the repo has an update, prompt-snapshot, and target SemVer baseline.
7. Add hooks if you want faster local feedback.
8. Add CI adapters only if your host supports them. The core workflow must still run locally.
9. Later, add generated docs and executable doc tests.

## Installed command surface

After install, use these target-repo commands:

- `make help`
- `make workflow-help`
- `make agent-start`
- `make kit-status`
- `make kit-status KIT=/path/to/repo-contract-kit`
- `make kit-update KIT=/path/to/repo-contract-kit`
- `make docs-check`
- `make agent-docs-lint`
- `make agent-docs-localize`
- `make agent-review`
- `make agent-run-review AGENT=manual`
- `make agent-learn`
- `make agent-task-packet`
- `make agent-task-prepare TASK=<id> SCOPE=<paths>`
- `make agent-test-first`
- `make agent-verify`
- `make version-status`
- `make version-check`
- `make version-bump BUMP=patch`

The agent commands print the local workflow or prompt path to use. They
deliberately avoid binding the repository to one agent runtime.

Use `make workflow-help` first when the command list is unfamiliar. It presents
the everyday rhythm as four moves: orient, review, scope, and execute. The same
model is documented in `docs/working-rhythm.md` inside installed target repos.

Use `make agent-start` first when you want the least friction. It creates an
ignored session packet with the current repo state, docs-impact result, latest
ADR context, review-risk tier, selected trust profile, recommended
prompts/personas, and a receipt template for the agent's final evidence.

Before using browser research, hosted CI adapters, external models, or
write-capable workers, read `docs/ops/agent-tool-network-allowlist.md` and the
selected trust profile in `.agent-workflows/agent-permission-policy.json`.

Use `make agent-run-review AGENT=manual` to turn the latest session packet into
one prompt per selected reviewer plus review-run JSON artifacts. Use
`AGENT=amp` only when Amp CLI is available and you want the wrapper to execute
the read-only personas with `amp --execute --stream-json`.

Use `make agent-task-packet` when a backlog row, issue, accepted finding,
external planning item, or broad request needs to become one executable unit of
work before an agent edits files.

Use `make agent-task-prepare TASK=<id> SCOPE=<paths>` after the task packet is
approved and before a write-capable worker edits files. It creates a
`codex/task-...` branch in a sibling worktree, writes local task artifacts, and
records in-flight metadata so overlapping task scopes can warn or block.

Use `make kit-status` when returning to a repo after some time. It shows the
installed kit version, source ref, selected profiles, vendored
`agent-workflow-kit` prompt snapshot ref/hash, target repo version, whether the
managed manifest exists, and whether managed files are clean.

Use `make kit-status KIT=/path/to/repo-contract-kit` when you have a local kit
checkout and want an explicit `current`/`available` update signal for both the
install kit and the prompt snapshot.

Use `make kit-update KIT=/path/to/repo-contract-kit` to update from a local kit
checkout. Clean managed files are updated automatically. Customized files are
preserved, and proposed replacements are written under
`.doc-contract-kit/updates/` for review. If the repo is a legacy install without
a manifest, the first run adopts current hashes without overwriting files.

The `agentic` preset includes the `versioning` profile. That profile creates
local SemVer files when missing and keeps `VERSION` and
`CHANGELOG.md` target-owned so updates never overwrite project release history.

## Start small

Pick one repository first.
Do not attempt to standardize everything at once.

## Expect iteration

The first version will probably be too weak in some places and too strict in others.
That is normal.
The point of repo-contract-kit is to give you a versioned place to improve the
system.
