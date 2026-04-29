# Local Repo Review Workflow

Use this workflow for a local agentic code review in a locked-down repository.

## Inputs

- User request or review goal
- Current branch or changed files
- `AGENTS.md`
- `REVIEW.md`
- `doc-contract.json`
- `docs/documentation-contract.md`
- Latest ADRs under `docs/adr/`, when present

## Steps

1. Establish scope: bootstrap, drift, pull-request, release-gate, learning, or
   test-first.
2. Run local discovery:

   ```bash
   git status --short
   python3 scripts/localize_doc_impact.py --working-tree --json
   python3 scripts/lint_agent_docs.py --strict-paths
   ```

3. Select the smallest reviewer set needed. Prefer one focused reviewer for
   normal drift and add specialists only for high-risk areas.
4. Produce at most five findings per reviewer.
5. Require file evidence, command evidence, docs/ADR evidence, or runtime
   evidence for every finding.
6. Record false-positive notes for every finding.
7. Use `.agent-workflows/schemas/session-receipt.schema.json` when JSON output
   is possible.

## Default Reviewer Set

- Documentation/code delta
- AI code slop
- Test and behavior risk
- Reuse and architecture

Add security, API/data contracts, dependencies/build, runtime, duplication, dead
code, or frontend UX reviewers only when the changed files justify them.

## Output

Return:

- summary
- findings table with priority, area, confidence, evidence, recommendation, and
  disposition
- docs-impact result
- commands run
- tests run or skipped with reasons
- next local command the human should run
