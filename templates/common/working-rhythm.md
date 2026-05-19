# Working Rhythm

Use this page when the command list feels wider than the workflow.

This repository has local guardrails installed by `repo-contract-kit`. The
prompts under `.codex/prompts/` are a vendored snapshot of the companion
`agent-workflow-kit` prompt library, but normal work should happen from this
checkout with local commands.

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
make agent-task-prepare TASK=<id> SCOPE=<paths>
make agent-verify
```

`agent-task-prepare` creates a task branch and sibling worktree, writes task
artifacts, and records local in-flight metadata. The worker edits in the task
worktree, then validation evidence is captured before handoff.

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
make agent-task-prepare TASK=<id> SCOPE=<paths>
```

For kit maintenance:

```bash
make kit-status KIT=/path/to/repo-contract-kit
make kit-update KIT=/path/to/repo-contract-kit
```

Keep kit updates explicit. Normal validation should not update installed
guardrails automatically.
