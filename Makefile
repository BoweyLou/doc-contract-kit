.PHONY: help workflow-help test docs-check version-check

help: workflow-help

workflow-help:
	@printf "%s\n" \
		"repo-contract-kit maintainer commands" \
		"" \
		"Install into a target repo:" \
		"   python3 scripts/install.py /path/to/target/repo --preset agentic" \
		"" \
		"In the installed target repo, use the four-move rhythm:" \
		"1. Orient" \
		"   make agent-start" \
		"   make kit-status" \
		"2. Review" \
		"   make agent-run-review AGENT=manual" \
		"3. Scope" \
		"   make agent-task-packet" \
		"4. Execute" \
		"   make agent-task-prepare TASK=<id> SCOPE=<paths>" \
		"   make agent-verify" \
		"" \
		"Maintainer checks:" \
		"   make test" \
		"   make docs-check" \
		"   make version-check"

test:
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

docs-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_doc_impact.py --working-tree

version-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py check
