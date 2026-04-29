# doc-contract-kit

doc-contract-kit is a reusable starter kit for repos that want documentation to stay in sync with code.

It is designed for agent-heavy development, where code can change quickly and documentation drift becomes a structural problem unless the repository enforces a documentation contract.

## What this repo contains

- templates for repo-local documentation guardrails
- a lightweight documentation impact checker
- a simple installer for bootstrapping another repository
- beginner-friendly docs explaining PRs, CI, hooks, ADRs, and agent instructions
- a Hermes skill stub for later automation

## Core idea

A code change is not complete until the repository has either:

1. updated the relevant documentation, or
2. explicitly declared why no documentation update is needed

## v0.1 scope

This version aims to be:

- simple
- understandable
- easy to install
- easy to iterate on

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

Then inside the target repo:

```bash
make docs-check
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
- `agentic`: documentation contract, review prompts, learning prompts, and test-first prompts.
- `strict-agentic`: `agentic` plus the forced Keryx cockpit profile.

## What gets installed

The starter kit currently installs:

- `doc-contract.json`
- `AGENTS.md`
- `docs/documentation-contract.md`
- `docs/adr/0000-template.md`
- `.github/pull_request_template.md`
- `.github/workflows/docs.yml`
- `.pre-commit-config.yaml`
- `Makefile`
- `scripts/check_doc_impact.py`

The default profile is `minimal`, which keeps the repo portable and does not
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
- `make agent-review`: point the agent at the multi-agent repo review prompt.
- `make agent-learn`: point the agent at the learner-focused comment prompt.
- `make agent-test-first`: point the agent at the TDD/executable-spec prompt chooser.
- `make agent-verify`: run the verification checks currently available in the installed profile.

The installer also writes `.doc-contract-kit/install.json` so later upgrades can
see which profiles or preset were installed.

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
- CI for non-bypassable enforcement
- ADRs for important architectural decisions
- gentle adoption path for solo developers

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
The goal is to create a calm, reusable documentation operating system for agentic software development.
