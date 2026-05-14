# Changelog

## 0.4.3 - 2026-05-14

- Add installed instruction-budget config and linter checks so `AGENTS.md`,
  `REVIEW.md`, and runtime-specific agent rules can stay concise as features
  are added.
- Add agent-instruction hygiene guidance that routes durable rules into scoped
  contracts, checkers, runbooks, ADRs, or receipts instead of stuffing them into
  root instruction files.

## 0.4.2 - 2026-05-14

- Add review-risk and trust-profile context to `make agent-start` packets and
  receipt templates.
- Install an agent tool/network allowlist doc and updated read-only review
  guidance for target repos.
- Refresh the vendored `agent-workflow-kit` prompt/schema snapshot with
  review-risk and local/private/browser policy prompts.

## 0.4.1 - 2026-05-14

- Add script-flow and function-guide comments across the repo-contract-kit
  scripts so maintainers can trace each command's execution path and helper
  roles.

## 0.4.0 - 2026-05-14

- Add agent permission policy templates for read-only review, untrusted PRs,
  browser research, and scoped write-worker profiles.
- Add a fork-safe read-only agent review workflow template and wire installed
  review runs to explicit trust profiles.
- Add strict local session receipt verification with `make agent-receipt-verify`.
- Record vendored `agent-workflow-kit` prompt snapshot provenance in install
  receipts and managed manifests.
- Refresh the vendored prompt/schema snapshot to `agent-workflow-kit`
  `0.2.0-beta.3`, generated from `workflows/prompts`.
- Expand agent instruction linting for secrets, unsafe commands, wildcard
  permissions, browser/account mutation guidance, contradictions, and JSON/SARIF
  output.
- Add repo-boundary documentation for coordinated `agent-workflow-kit` and
  `repo-contract-kit` changes.

## 0.3.0 - 2026-04-30

- Add local agent startup packets.
- Add managed install manifests and safe local update planning.
- Add default target-repo versioning support for agentic installs.

## 0.2.0

- Add local-first agentic profiles, review prompts, TDD prompts, and evidence
  receipt templates.

## 0.1.0

- Bootstrap documentation-contract installer, templates, and local checks.
