.PHONY: docs-lint docs-build docs-generate docs-check keryx-check

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
