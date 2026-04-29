# repo-contract-kit

Formerly **doc-contract-kit**.

`repo-contract-kit` is an installable repository contract kit for local-first
agentic development. It adds documentation contracts, agent instruction hygiene,
evidence receipts, local verification commands, and optional workflow profiles
to target repositories.

Documentation freshness is still the core contract. The scope has grown because
agent-heavy repositories also need explicit local rules for prompts, reviewers,
tests, receipts, and tool-agnostic workflows.

## What this repo contains

- templates for repo-local operating guardrails
- a lightweight documentation impact checker
- a simple installer for bootstrapping target repositories
- local-first agent workflow files that work without GitHub Actions or hosted CI
- agent instruction linting for local prompt/rule files
- evidence receipt and safe-output schemas
- TDD/executable-spec workflow profiles
- beginner-friendly docs explaining PRs, CI, hooks, ADRs, and agent instructions
- a Hermes skill stub for later automation

## Where This Fits

This repository is the install layer:

- `AGENTS.md` and `REVIEW.md` templates
- docs-impact checks and waivers
- local `make` targets
- profile installation and upgrade receipts
- local agent workflow files under `.agent-workflows/`
- tool-agnostic schemas and safe-output boundaries

The companion workflow layer is **agent-workflow-kit** (formerly
`Codex_CodeReview`). That repo owns the prompt library, reviewer personas,
learning-comments workflows, TDD prompts, synthesis prompts, and research
backlog.

## Core idea

A code change is not complete until the repository has either:

1. updated the relevant documentation, or
2. explicitly declared why no documentation update is needed

## Current Scope

This project aims to be:

- simple
- understandable
- easy to install locally
- easy to iterate on
- useful without hosted CI or a specific coding agent

It does not yet try to solve every language, build system, or CI pattern.

## Quick start

From inside this repo:

```bash
python3 scripts/install.py /path/to/target/repo
```

For the opinionated agentic setup:

```bash
python3 scripts/install.py /path/to/target/repo --preset agentic
```

The `agentic` preset is local-first and agent-tool agnostic. It can be used from
AmpCode, Codex, Claude Code, Aider, Cline, or a manual shell workflow. It does
not require GitHub Actions and is suitable for locked-down on-prem Git servers
such as older Bitbucket deployments.

Then inside the target repo:

```bash
make docs-check
make agent-docs-lint
make agent-docs-localize
make agent-review
make agent-test-first
```

If the target repo uses pre-commit hooks:

```bash
pre-commit install
```

To install the forced Keryx cockpit profile:

```bash
python3 scripts/install.py /path/to/target/repo --profile keryx-forced
```

To install the test-first executable-spec profile:

```bash
python3 scripts/install.py /path/to/target/repo --profile test-first
```

To compose profiles directly:

```bash
python3 scripts/install.py /path/to/target/repo --profiles review-prompts,test-first
```

## Presets

Presets are the easiest way to install a coherent operating mode:

- `minimal`: documentation contract only.
- `learning`: documentation contract plus review and learning prompts.
- `test-first`: documentation contract plus TDD/executable-spec prompts.
- `agentic`: documentation contract, local agent workflows, review prompts,
  learning prompts, and test-first prompts.
- `strict-agentic`: `agentic` plus the forced Keryx cockpit profile.

## What gets installed

The kit currently installs:

- `doc-contract.json`
- `AGENTS.md`
- `REVIEW.md`
- `docs/documentation-contract.md`
- `docs/adr/0000-template.md`
- `.github/pull_request_template.md`
- `.github/workflows/docs.yml`
- `.pre-commit-config.yaml`
- `Makefile`
- `scripts/check_doc_impact.py`
- `scripts/lint_agent_docs.py`
- `scripts/localize_doc_impact.py`
- `.agent-workflows/schemas/safe-output.schema.json`

The default profile is `minimal`, which keeps target repos portable and does not
assume a local knowledge-base tool.

The `keryx-forced` profile also installs:

- `.keryx/config.json`
- `.keryx/sync.example.json`
- `docs/backlog.md`
- `docs/architecture.md`
- `docs/plan.md`
- `scripts/check_keryx_sync.py`
- a stricter `AGENTS.md`
- a Keryx-aware `Makefile`
- a pre-commit config that runs both the docs contract and Keryx sync receipt checks

The `review-prompts` profile also installs:

- `.codex/prompts/multi-agent-repo-review.md`
- `.codex/prompts/codebase-learning-comments.md`
- `.codex/prompts/personas/`
- `.codex/prompts/templates/`
- remediation and verification prompts

The `local-agentic` profile also installs:

- `.agent-workflows/README.md`
- `.agent-workflows/repo-review.md`
- `.agent-workflows/tdd-red-green-receipt.md`
- `.agent-workflows/schemas/session-receipt.schema.json`

Use this profile when the repo must work with local tools only and cannot assume
GitHub Actions, cloud CI, or one specific agent runtime.

## Configuration

`doc-contract.json` lets each target repository customize:

- required documentation contract files
- paths that count as documentation
- ignored paths such as tests
- source paths that imply documentation impact
- expected documentation paths for each impact category

The checker fails when it detects doc-impacting changes without matching
documentation updates. If a change genuinely needs no docs, the PR body must
include `No docs needed: <reason>`, or CI/local automation must provide
`DOC_CONTRACT_NO_DOCS_NEEDED`.

## Forced Keryx profile

Use `--profile keryx-forced` when Keryx should be the mandatory operating
surface for backlog, architecture, plan, and handoff state.

In that profile, the repository still keeps a one-to-one Markdown mirror of the
Keryx state so fresh clones and CI can see the same context. Commits are blocked
locally unless `.keryx/sync.json` matches the current staged tree and configured
mirror docs.

See `docs/keryx-forced-profile.md` for the expected lifecycle.

The `test-first` profile also installs:

- `.codex/prompts/tdd/`
- `docs/testing-strategy.md`
- `docs/adr/0001-testing-philosophy.md`
- a PR template with test-first evidence checks

Use it when a repository should treat tests as executable documentation for
features, bug fixes, refactors, API contracts, and high-risk cleanup.

## Installed commands

Installed target repos get Makefile entrypoints:

- `make docs-check`: run the documentation contract checks.
- `make agent-docs-lint`: check local agent instruction files for hidden
  Unicode, stale paths, and unsafe references.
- `make agent-docs-localize`: emit JSON that maps changed files to likely
  documentation impact.
- `make agent-review`: point the agent at the multi-agent repo review prompt.
- `make agent-learn`: point the agent at the learner-focused comment prompt.
- `make agent-test-first`: point the agent at the TDD/executable-spec prompt chooser.
- `make agent-verify`: run the verification checks currently available in the installed profile.

The installer also writes `.doc-contract-kit/install.json` so later upgrades can
see which profiles or preset were installed. That compatibility path keeps
existing installations stable while the project name moves to repo-contract-kit.

## Recommended rollout

1. Start with one test repo.
2. Install the kit.
3. Let an agent make a small change.
4. See what feels useful or annoying.
5. Adjust the templates and iterate.
6. Only later roll it out widely.

## Philosophy

- docs as code
- explicit documentation obligations
- hooks for local feedback
- optional CI adapters, never required for the core local workflow
- ADRs for important architectural decisions
- gentle adoption path for solo developers
- agent-tool agnostic workflow files before tool-specific adapters
- evidence receipts before trusted automation

## Roadmap

See:

- `docs/vision.md`
- `docs/concepts-for-beginners.md`
- `docs/rollout-guide.md`
- `docs/roadmap.md`

## Development

Run the test suite with:

```bash
python3 -m unittest discover -s tests
```

## Development status

This repository is intentionally early and iterative.
The goal is to create a calm, reusable repository operating system for local
agentic software development.

## Naming Status

The intended project name is `repo-contract-kit`. The current repository path,
remote, installer metadata path, and some compatibility keys may still use
`doc-contract-kit` until the GitHub repository, local directory, and migration
story are renamed deliberately.
