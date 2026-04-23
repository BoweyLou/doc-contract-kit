# AGENTS.md

## Purpose

This repository uses docs-as-code and forced Keryx project-state sync.
Documentation is part of the definition of done.

If you change code, you must consider whether documentation also needs to
change, then sync the staged repository state through Keryx before committing.

## Where documentation lives

- `README.md` - high-level overview and getting started
- `docs/` - project documentation
- `docs/backlog.md` - repository mirror of the Keryx backlog
- `docs/architecture.md` - repository mirror of the Keryx architecture view
- `docs/plan.md` - repository mirror of the Keryx execution plan
- `docs/adr/` - architecture decision records
- `doc-contract.json` - repository-specific documentation impact rules
- `.keryx/config.json` - forced Keryx sync configuration
- `.keryx/sync.json` - generated Keryx sync receipt for the staged state
- `.github/pull_request_template.md` - PR checklist and change classification

## Keryx sync rule

Keryx is the working cockpit for backlog, architecture, plan, and handoff state.
The repo keeps a durable mirror so fresh clones, CI, Codex, Claude Code, and
GitHub still have the same context.

Before committing, sync the current staged state through Keryx and stage the
updated `.keryx/sync.json` receipt. The pre-commit hook must block stale or
missing Keryx receipts.

## Documentation contract

If you change any of the following, update the relevant docs in the same change:

- public behavior
- API
- CLI commands or flags
- config or environment variables
- schema or data contracts
- deployment or operations workflow
- architecture or major design decisions
- backlog, plan, or project-state expectations

If no documentation update is needed, explicitly say why in the PR summary.
Use the exact marker `No docs needed: <reason>`.

## ADR rules

Create or update an ADR when the change affects:

- architecture
- major dependencies
- service boundaries
- data flow or storage strategy
- security/privacy tradeoffs
- deployment/runtime model

Do not create ADRs for small bug fixes or routine internal refactors.

## Commands

Before finishing work, run:

- `make docs-lint`
- `make docs-build`
- `make docs-generate`
- `python3 scripts/check_doc_impact.py`
- `python3 scripts/check_keryx_sync.py --staged`

If these fail, fix the issue before considering the task complete.

## Pull request expectations

Every PR must clearly state:

1. what changed
2. whether docs were updated
3. whether Keryx was synced
4. whether an ADR was added or updated
5. if no docs changed, why not

## Important rule

Never leave generated docs stale.
Never change externally visible behavior without considering documentation impact.
Never commit in a forced-Keryx repository with a stale Keryx sync receipt.
