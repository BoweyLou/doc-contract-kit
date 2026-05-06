MODE ?= bootstrap
BUMP ?= patch
KIT ?=
AGENT ?= manual
AMP ?= amp

.PHONY: docs-lint docs-build docs-generate docs-check agent-start agent-run-review agent-docs-lint agent-docs-localize agent-review agent-learn agent-task-packet agent-test-first agent-verify kit-status kit-update version-status version-check version-bump

docs-lint:
	@echo "Running basic docs lint checks..."
	@test -f AGENTS.md || (echo "Missing AGENTS.md" && exit 1)
	@test -f REVIEW.md || (echo "Missing REVIEW.md" && exit 1)
	@test -f docs/documentation-contract.md || (echo "Missing docs/documentation-contract.md" && exit 1)
	@test -d docs/adr || (echo "Missing docs/adr/" && exit 1)
	@echo "Basic docs lint checks passed."

docs-build:
	@echo "No docs site configured yet. Skipping build."

docs-generate:
	@echo "No generated docs configured yet. Skipping generation."

docs-check: docs-lint docs-build docs-generate
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_doc_impact.py

agent-start:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_start.py --mode "$(MODE)"

agent-run-review:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_review_run.py --mode "$(MODE)" --agent "$(AGENT)" --amp-command "$(AMP)"

kit-status:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_status.py

kit-update:
	@test -n "$(KIT)" || (echo "Set KIT=/path/to/repo-contract-kit"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 "$(KIT)/scripts/update.py" "$(CURDIR)"

version-status:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py status

version-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py check

version-bump:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py bump --bump "$(BUMP)"

agent-docs-lint:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/lint_agent_docs.py --strict-paths

agent-docs-localize:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/localize_doc_impact.py --working-tree --json

agent-review:
	@if test -f .agent-workflows/repo-review.md; then \
		printf "%s\n" \
			"Read AGENTS.md, REVIEW.md, and .agent-workflows/README.md." \
			"Then follow .agent-workflows/repo-review.md in bootstrap mode." \
			"Use the installed personas and prompts under .codex/prompts/ where useful." \
			"Start by running make agent-verify and make agent-docs-localize." \
			"Optionally run make agent-run-review AGENT=manual to generate review artifacts." \
			"Produce a findings backlog before editing code."; \
	elif test -f .codex/prompts/multi-agent-repo-review.md; then \
		printf "%s\n" \
			"Read AGENTS.md and REVIEW.md." \
			"Then follow .codex/prompts/multi-agent-repo-review.md in bootstrap mode." \
			"Start by running make agent-verify and make agent-docs-localize." \
			"Optionally run make agent-run-review AGENT=manual to generate review artifacts." \
			"Produce a findings backlog before editing code."; \
	else \
		echo "Missing local review workflow; install the local-agentic or review-prompts profile."; exit 1; \
	fi

agent-learn:
	@test -f .codex/prompts/codebase-learning-comments.md || (echo "Missing .codex/prompts/codebase-learning-comments.md; install the review-prompts profile." && exit 1)
	@echo "Use .codex/prompts/codebase-learning-comments.md for learner-focused comments."

agent-task-packet:
	@test -f .codex/prompts/task-packet.md || (echo "Missing .codex/prompts/task-packet.md; install the review-prompts profile." && exit 1)
	@echo "Use .codex/prompts/task-packet.md to convert a backlog item, issue, accepted finding, or human request into executable agent work."

agent-test-first:
	@test -f .codex/prompts/tdd/README.md || (echo "Missing .codex/prompts/tdd/README.md; install the test-first profile." && exit 1)
	@echo "Use .codex/prompts/tdd/README.md to pick the executable-spec prompt."

agent-verify: docs-check agent-docs-lint
	@echo "Agent verification checks passed."
