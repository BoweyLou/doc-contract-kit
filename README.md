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

Then inside the target repo:

```bash
make docs-check
```

## What gets installed

The starter kit currently installs:

- `AGENTS.md`
- `docs/documentation-contract.md`
- `docs/adr/0000-template.md`
- `.github/pull_request_template.md`
- `.github/workflows/docs.yml`
- `.pre-commit-config.yaml`
- `Makefile`
- `scripts/check_doc_impact.py`

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

## Development status

This repository is intentionally early and iterative.
The goal is to create a calm, reusable documentation operating system for agentic software development.
