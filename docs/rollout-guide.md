# Rollout Guide

If this is all new to you, adopt it in layers.

## Suggested order

1. Install the templates only with `--preset minimal`.
2. Get used to AGENTS.md and the documentation contract.
3. Start running `make docs-check` locally.
4. Add `--preset learning` when you want review and learning prompts in the repo.
5. Add `--preset test-first` or `--preset agentic` when you want executable-spec prompts.
6. Add hooks if you want faster feedback.
7. Add CI enforcement when the local flow feels understandable.
8. Later, add generated docs and executable doc tests.

## Forced Keryx mode

Use the `keryx-forced` profile only for repositories where Keryx should be the
mandatory cockpit for backlog, architecture, plan, and handoff state.

In that mode, Keryx writes a staged-state receipt and pre-commit blocks the
commit if the receipt is missing or stale.

Use `--preset strict-agentic` when you want the review prompts, test-first
prompts, and forced Keryx profile together.

## Installed command surface

After install, use these target-repo commands:

- `make docs-check`
- `make agent-review`
- `make agent-learn`
- `make agent-test-first`
- `make agent-verify`

The agent commands print the prompt path to use. They deliberately avoid binding
the repository to one agent runtime.

## Start small

Pick one repository first.
Do not attempt to standardize everything at once.

## Expect iteration

The first version will probably be too weak in some places and too strict in others.
That is normal.
The point of doc-contract-kit is to give you a versioned place to improve the system.
