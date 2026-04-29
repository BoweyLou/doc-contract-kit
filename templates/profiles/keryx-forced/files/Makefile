.PHONY: docs-lint docs-build docs-generate docs-check keryx-check agent-docs-lint agent-docs-localize agent-review agent-learn agent-test-first agent-verify

docs-lint:
	@echo "Running basic docs lint checks..."
	@test -f AGENTS.md || (echo "Missing AGENTS.md" && exit 1)
	@test -f REVIEW.md || (echo "Missing REVIEW.md" && exit 1)
	@test -f docs/documentation-contract.md || (echo "Missing docs/documentation-contract.md" && exit 1)
	@test -d docs/adr || (echo "Missing docs/adr/" && exit 1)
	@test -f docs/backlog.md || (echo "Missing docs/backlog.md" && exit 1)
	@test -f docs/architecture.md || (echo "Missing docs/architecture.md" && exit 1)
	@test -f docs/plan.md || (echo "Missing docs/plan.md" && exit 1)
	@test -f .keryx/config.json || (echo "Missing .keryx/config.json" && exit 1)
	@echo "Basic docs lint checks passed."

docs-build:
	@echo "No docs site configured yet. Skipping build."

docs-generate:
	@echo "No generated docs configured yet. Skipping generation."

keryx-check:
	@python3 scripts/check_keryx_sync.py --staged

docs-check: docs-lint docs-build docs-generate keryx-check
	@python3 scripts/check_doc_impact.py --working-tree

agent-docs-lint:
	@python3 scripts/lint_agent_docs.py --strict-paths

agent-docs-localize:
	@python3 scripts/localize_doc_impact.py --working-tree --json

agent-review:
	@if test -f .agent-workflows/repo-review.md; then \
		printf "%s\n" \
			"Read AGENTS.md, REVIEW.md, and .agent-workflows/README.md." \
			"Then follow .agent-workflows/repo-review.md in bootstrap mode." \
			"Use the installed personas and prompts under .codex/prompts/ where useful." \
			"Start by running make agent-verify and make agent-docs-localize." \
			"Produce a findings backlog before editing code."; \
	elif test -f .codex/prompts/multi-agent-repo-review.md; then \
		printf "%s\n" \
			"Read AGENTS.md and REVIEW.md." \
			"Then follow .codex/prompts/multi-agent-repo-review.md in bootstrap mode." \
			"Start by running make agent-verify and make agent-docs-localize." \
			"Produce a findings backlog before editing code."; \
	else \
		echo "Missing local review workflow; install the local-agentic or review-prompts profile."; exit 1; \
	fi

agent-learn:
	@test -f .codex/prompts/codebase-learning-comments.md || (echo "Missing .codex/prompts/codebase-learning-comments.md; install the review-prompts profile." && exit 1)
	@echo "Use .codex/prompts/codebase-learning-comments.md for learner-focused comments."

agent-test-first:
	@test -f .codex/prompts/tdd/README.md || (echo "Missing .codex/prompts/tdd/README.md; install the test-first profile." && exit 1)
	@echo "Use .codex/prompts/tdd/README.md to pick the executable-spec prompt."

agent-verify: docs-check agent-docs-lint
	@echo "Agent verification checks passed."
