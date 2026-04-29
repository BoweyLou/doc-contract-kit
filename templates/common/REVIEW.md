# REVIEW.md

This repository is reviewed locally first. Do not assume GitHub Actions,
hosted CI, or a specific coding agent is available.

## Local Review Rules

- Start from the diff or explicitly requested scope.
- Read `AGENTS.md`, `doc-contract.json`, and `docs/documentation-contract.md`
  before making findings.
- Run local commands from the checkout when available.
- Treat `scripts/check_doc_impact.py` as the local docs-contract gate.
- Use `scripts/localize_doc_impact.py --json` to map changed source paths to
  likely docs before asking an agent to reason broadly.
- Use `scripts/lint_agent_docs.py --strict-paths` before trusting local agent
  instructions.

## Tool-Agnostic Agent Use

Any local coding tool can use this file: AmpCode, Codex, Claude Code, Aider,
Cline, or a human reviewer. If a tool has native prompt folders, those are
optional convenience layers. The source of truth is the checked-in Markdown,
schemas, scripts, and local command output.

## Evidence Required

Every serious agent run should leave either a JSON receipt or a Markdown handoff
with:

- agent tool used
- mode: bootstrap, drift, pull-request, release-gate, learning-comments,
  test-first, or verification
- files inspected
- commands run and results
- docs-impact result
- TDD red/green evidence when behavior changed
- findings with priority, confidence, evidence, recommendation, and disposition
- skipped checks and reasons

## Review Quality Bar

- Cap normal reviews at five findings per reviewer.
- Do not report nits unless they affect correctness, security, docs drift, or
  maintainability.
- Include the most plausible false-positive explanation for each finding.
- Keep auto-merge and write-back out of scope unless a human explicitly opts in.
