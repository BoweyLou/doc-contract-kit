# Keryx Forced Profile

The `keryx-forced` profile is for repositories where Keryx is the mandatory
working cockpit for backlog, architecture, plan, and handoff state.

The repository remains the durable mirror. The mirror lets fresh clones, local
checks, Codex, AmpCode, Claude Code, and other local agents read the same state
even when they cannot access the local Keryx workspace directly.

Keryx owns backlog prioritisation. `docs/backlog.md` mirrors that queue for Git
history and clone portability. The executable surface is a task packet: select
one backlog item, then use `.codex/prompts/task-packet.md` or
`make agent-task-packet` to define scope, acceptance criteria, validation,
documentation impact, risk, and approval before implementation.

## Installed Files

The profile installs:

- `.keryx/config.json`
- `.keryx/sync.example.json`
- `docs/backlog.md`
- `docs/architecture.md`
- `docs/plan.md`
- `scripts/check_keryx_sync.py`
- `scripts/lint_agent_docs.py`
- `scripts/localize_doc_impact.py`
- `REVIEW.md`
- `.agent-workflows/`
- `.codex/prompts/task-packet.md` when the review-prompts profile is composed
- a Keryx-aware `Makefile`
- a Keryx-aware `AGENTS.md`
- a local-only pre-commit config with doc-contract, Keryx sync, and agent
  instruction checks

## Commit Lifecycle

1. Update code and repository docs.
2. If work came from a backlog item, convert it into a task packet before
   implementation.
3. Stage the intended commit contents.
4. Sync the staged state through Keryx.
5. Keryx writes `.keryx/sync.json`.
6. Stage `.keryx/sync.json`.
7. Commit after pre-commit passes.

The Keryx hook validates that the staged project files, configured mirror docs,
current `HEAD`, and sync receipt agree.

## Mirror Files

The default mirror paths are:

- `README.md`
- `AGENTS.md`
- `docs/backlog.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/documentation-contract.md`

Adjust `.keryx/config.json` when a repository needs a different mirror.

## Why The Repo Still Keeps A Copy

Keryx is the interface the developer uses day to day. The repository mirror is
what makes the workflow portable, reviewable, and enforceable outside the local
Keryx environment.
