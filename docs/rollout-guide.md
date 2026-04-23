# Rollout Guide

If this is all new to you, adopt it in layers.

## Suggested order

1. Install the templates only.
2. Get used to AGENTS.md and the documentation contract.
3. Start running `make docs-check` locally.
4. Add hooks if you want faster feedback.
5. Add CI enforcement when the local flow feels understandable.
6. Later, add generated docs and executable doc tests.

## Forced Keryx mode

Use the `keryx-forced` profile only for repositories where Keryx should be the
mandatory cockpit for backlog, architecture, plan, and handoff state.

In that mode, Keryx writes a staged-state receipt and pre-commit blocks the
commit if the receipt is missing or stale.

## Start small

Pick one repository first.
Do not attempt to standardize everything at once.

## Expect iteration

The first version will probably be too weak in some places and too strict in others.
That is normal.
The point of doc-contract-kit is to give you a versioned place to improve the system.
