# Prompt Index

Use these prompts as a multi-agent codebase review kit.

## Core Flow

- `multi-agent-repo-review.md`: Orchestrates repo mapping, reviewer dispatch, and review boundaries.
- `codebase-learning-comments.md`: Uses subagents to understand docs, ADRs, and code before adding learner-friendly comments.
- `review-synthesis.md`: Merges persona outputs into one ranked action plan.
- `fix-planner.md`: Converts accepted findings into scoped implementation batches.
- `fix-implementer.md`: Applies a selected batch without widening scope.
- `verification-sentinel.md`: Validates claims, tests, and residual risk after remediation.
- `tdd/`: Test-first and executable-spec prompt set for feature work, bug fixes, refactors, contracts, invariants, and test-quality review.

## Persona Reviewers

- `personas/doc-code-delta.md`: Finds drift between docs and implementation.
- `personas/ai-code-slop.md`: Finds generated-looking slop, brittle shortcuts, and shallow abstractions.
- `personas/reuse-architecture.md`: Finds missed reuse, misplaced responsibilities, and architecture drift.
- `personas/dead-code.md`: Finds unused code, stale entrypoints, abandoned config, and unreachable paths.
- `personas/duplication.md`: Finds repeated logic and inconsistent copies.
- `personas/test-behavior-risk.md`: Finds weak tests, missing regression coverage, and behavior risk.
- `personas/security-privacy.md`: Finds secrets, unsafe IO, auth gaps, and privacy leaks.
- `personas/api-data-contracts.md`: Finds API, schema, migration, and data-shape drift.
- `personas/dependencies-build.md`: Finds dependency, packaging, CI, and build-system risk.
- `personas/runtime-observability.md`: Finds runtime, logging, metrics, scheduling, and deployability gaps.
- `personas/frontend-ux.md`: Finds frontend quality, accessibility, state, and UX consistency issues.

## Output Templates

- `templates/review-finding.md`: Shared finding format for reviewer outputs.
- `templates/agent-brief.md`: Fill-in brief for launching a focused reviewer.

## Recommended Dispatch

For a small repo, run:

1. `doc-code-delta`
2. `ai-code-slop`
3. `test-behavior-risk`
4. `reuse-architecture`

For a mature repo or release gate, add:

1. `dead-code`
2. `duplication`
3. `security-privacy`
4. `api-data-contracts`
5. `dependencies-build`
6. `runtime-observability`
7. `frontend-ux` when applicable

For understanding a repo as a learner, run `codebase-learning-comments.md` instead of the defect-review flow.

For implementing accepted changes test-first, use `tdd/README.md` to choose the right executable-spec prompt.
