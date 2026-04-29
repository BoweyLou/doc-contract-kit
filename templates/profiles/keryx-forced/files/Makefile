.PHONY: docs-lint docs-build docs-generate docs-check keryx-check agent-review agent-learn agent-test-first agent-verify

docs-lint:
	@echo "Running basic docs lint checks..."
	@test -f AGENTS.md || (echo "Missing AGENTS.md" && exit 1)
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

agent-review:
	@test -f .codex/prompts/multi-agent-repo-review.md || (echo "Missing .codex/prompts/multi-agent-repo-review.md; install the review-prompts profile." && exit 1)
	@echo "Use .codex/prompts/multi-agent-repo-review.md for the repo review."

agent-learn:
	@test -f .codex/prompts/codebase-learning-comments.md || (echo "Missing .codex/prompts/codebase-learning-comments.md; install the review-prompts profile." && exit 1)
	@echo "Use .codex/prompts/codebase-learning-comments.md for learner-focused comments."

agent-test-first:
	@test -f .codex/prompts/tdd/README.md || (echo "Missing .codex/prompts/tdd/README.md; install the test-first profile." && exit 1)
	@echo "Use .codex/prompts/tdd/README.md to pick the executable-spec prompt."

agent-verify: docs-check
	@echo "Agent verification checks passed."
