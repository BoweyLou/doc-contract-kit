# Working Rhythm

Use this page when the command list feels wider than the workflow.

## Stack Map

This repository has local guardrails installed by `repo-contract-kit`. The
prompts under `.codex/prompts/` are a vendored snapshot of the companion
`agent-workflow-kit` prompt library, but normal work should happen from this
checkout with local commands.

The stack has three layers:

- `agent-workflow-kit` owns canonical prompts, personas, schemas, research
  workflows, and generated adapter source.
- `repo-contract-kit` owns installer profiles, managed templates, update
  behavior, target-repo scripts, and local Make targets.
- this target repo owns day-to-day work, local docs/version decisions, and any
  explicit local overrides.

When the prompt source changes, target repos receive it through a vendored
snapshot in a `repo-contract-kit` update. Target repos do not need to fetch
`agent-workflow-kit` at runtime.

## Four Moves

### 1. Orient

Use this when returning to the repo or starting a new agent session.

```bash
make agent-start
make kit-status
```

`agent-start` writes an ignored local packet with changed files, docs impact,
latest ADR context, kit/version state, review risk, recommended prompts, and a
receipt template. `kit-status` explains the installed kit version, prompt
snapshot, managed-file status, and target repo version.

### 2. Review

Use this when the goal is understanding, review, or finding risk before edits.

```bash
make agent-run-review AGENT=manual
```

Manual mode writes reviewer prompts and local JSON artifacts under
`.agent-workflows/runs/`. If the runner is not useful for the current tool, read
the prompts under `.codex/prompts/` directly.

### 3. Scope

Use this when a backlog row, issue, accepted finding, or broad human request
needs to become executable work.

```bash
make agent-task-packet
```

The packet should name scope, non-goals, docs impact, validation, risk, and
approval state before implementation starts.

### 4. Execute

Use this after the task is approved for write-capable work.

```bash
make agent-task-status
make agent-task-prepare TASK=<id> SCOPE=<paths>
make agent-verify
```

`agent-task-status` shows active local tasks, registered git worktrees, dirty
task worktrees, stale or missing metadata, unknown scopes, and declared scope
overlaps. `agent-task-prepare` creates a task branch and sibling worktree,
writes task artifacts, and records local in-flight metadata. The worker edits in
the task worktree, checks `agent-task-status` before handoff, then validation
evidence is captured before review.

When using multiple Codex terminals, run the prepare command from the main
checkout in each terminal, then `cd` into the worktree path printed for that
task. You keep using the same Codex terminal after the `cd`; the main checkout
is only the coordination point.

## Common Paths

For quick orientation:

```bash
make workflow-help
make agent-start
make kit-status
```

For read-only review:

```bash
make agent-start MODE=drift
make agent-run-review AGENT=manual
make agent-receipt-verify
```

For approved implementation:

```bash
make agent-task-packet
make agent-task-status
make agent-task-prepare TASK=<id> SCOPE=<paths>
```

For kit maintenance:

```bash
make kit-status KIT=/path/to/repo-contract-kit
make kit-update KIT=/path/to/repo-contract-kit
make kit-refresh KIT=/path/to/repo-contract-kit
```

Use `kit-update` when the local kit checkout is already at the version you want.
Use `kit-refresh` when the first step should be a clean fast-forward pull of the
kit checkout. Keep kit updates explicit. Normal validation should not update
installed guardrails automatically.

## Change Routing

| Change | Start in |
| --- | --- |
| Prompt wording, personas, schemas, research prompts, TDD prompts, synthesis prompts | `agent-workflow-kit` |
| Installed commands, templates, scripts, manifests, update behavior, docs-contract checks | `repo-contract-kit` |
| Target-specific docs, version notes, local overrides, product behavior | this target repo |
