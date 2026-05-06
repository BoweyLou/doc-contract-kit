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
6. Run `make kit-status` and `make version-check` so the repo has an update
   baseline and target SemVer baseline.
7. Add hooks if you want faster local feedback.
8. Add CI adapters only if your host supports them. The core workflow must still run locally.
9. Later, add generated docs and executable doc tests.

## Installed command surface

After install, use these target-repo commands:

- `make agent-start`
- `make kit-status`
- `make kit-update KIT=/path/to/repo-contract-kit`
- `make docs-check`
- `make agent-docs-lint`
- `make agent-docs-localize`
- `make agent-review`
- `make agent-run-review AGENT=manual`
- `make agent-learn`
- `make agent-task-packet`
- `make agent-test-first`
- `make agent-verify`
- `make version-status`
- `make version-check`
- `make version-bump BUMP=patch`

The agent commands print the local workflow or prompt path to use. They
deliberately avoid binding the repository to one agent runtime.

Use `make agent-start` first when you want the least friction. It creates an
ignored session packet with the current repo state, docs-impact result, latest
ADR context, recommended prompts/personas, and a receipt template for the
agent's final evidence.

Use `make agent-run-review AGENT=manual` to turn the latest session packet into
one prompt per selected reviewer plus review-run JSON artifacts. Use
`AGENT=amp` only when Amp CLI is available and you want the wrapper to execute
the read-only personas with `amp --execute --stream-json`.

Use `make agent-task-packet` when a backlog row, issue, accepted finding,
external planning item, or broad request needs to become one executable unit of
work before an agent edits files.

Use `make kit-status` when returning to a repo after some time. It shows the
installed kit version, source ref, selected profiles, target repo version, and
whether the managed manifest exists.

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
