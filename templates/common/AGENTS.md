# AGENTS.md

## Purpose

This repository uses docs-as-code. Documentation is part of the definition of done.

If you change code, you must consider whether documentation also needs to change.

## Agent self-start

If asked to review, understand, clean up, or formalize this repo, start here:

1. Read `AGENTS.md`, `REVIEW.md`, and `.agent-workflows/README.md`.
2. Follow `.agent-workflows/repo-review.md` in the requested mode. Use
   `bootstrap` for the first review of an inherited or newly instrumented repo.
3. Use the installed personas and prompts under `.codex/prompts/` where useful.
4. Run `make agent-verify` and `make agent-docs-localize` before proposing code
   changes.
5. Produce a findings backlog before editing code.

The prompts under `.codex/prompts/` are local copies installed by
`repo-contract-kit`. Do not fetch prompts from another repo during normal work
unless the user explicitly asks you to refresh the kit.

## Where documentation lives

- `README.md` — high-level overview and getting started
- `docs/` — project documentation
- `docs/adr/` — architecture decision records
- `doc-contract.json` — repository-specific documentation impact rules
- `.github/pull_request_template.md` — PR checklist and change classification

## Documentation contract

If you change any of the following, update the relevant docs in the same change:

- public behavior
- API
- CLI commands or flags
- config or environment variables
- schema or data contracts
- deployment or operations workflow
- architecture or major design decisions

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

If these fail, fix the issue before considering the task complete.

## Pull request expectations

Every PR must clearly state:

1. what changed
2. whether docs were updated
3. whether an ADR was added or updated
4. if no docs changed, why not

## Important rule

Never leave generated docs stale.
Never change externally visible behavior without considering documentation impact.
