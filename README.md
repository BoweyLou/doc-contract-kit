# repo-contract-kit

`repo-contract-kit` is an installable repository contract kit for local-first
agentic development. It adds documentation contracts, agent instruction hygiene,
evidence receipts, local verification commands, and optional workflow profiles
to target repositories.

Documentation freshness is still the core contract. The scope has grown because
agent-heavy repositories also need explicit local rules for prompts, reviewers,
tests, receipts, and tool-agnostic workflows.

## What this repo contains

- templates for repo-local operating guardrails
- a lightweight documentation impact checker
- a simple installer for bootstrapping target repositories
- local-first agent workflow files that work without GitHub Actions or hosted CI
- agent instruction linting for local prompt/rule files
- instruction budgets so `AGENTS.md` and tool-specific rule files stay concise
- explicit permission policies for read-only review, untrusted PRs, browser
  research, and scoped write workers
- review-risk and trust-profile startup context
- targeted research commands for source-specific backlog, review, design, and
  architecture discovery
- evidence receipt and safe-output schemas
- TDD/executable-spec workflow profiles
- safe local kit updates with managed-file conflict reports
- prompt snapshot provenance for vendored `agent-workflow-kit` files
- default local SemVer files and version commands for agentic target repos
- beginner-friendly docs explaining PRs, CI, hooks, ADRs, and agent instructions
- a Hermes skill stub for later automation

## Where This Fits

This repository is the install layer:

- `AGENTS.md` and `REVIEW.md` templates
- docs-impact checks and waivers
- local `make` targets
- profile installation, managed manifests, and update receipts
- local agent workflow files under `.agent-workflows/`
- tool-agnostic schemas and safe-output boundaries
- installed provenance for both `repo-contract-kit` and the vendored
  `agent-workflow-kit` prompt snapshot
- optional fork-safe read-only PR workflow adapter

The companion workflow layer is
[agent-workflow-kit](https://github.com/BoweyLou/agent-workflow-kit). That repo
owns the prompt library, reviewer personas, learning-comments workflows, TDD
prompts, synthesis prompts, and research backlog.

## Core idea

A code change is not complete until the repository has either:

1. updated the relevant documentation, or
2. explicitly declared why no documentation update is needed

## Current Scope

This project aims to be:

- simple
- understandable
- easy to install locally
- easy to iterate on
- useful without hosted CI or a specific coding agent

It does not yet try to solve every language, build system, or CI pattern.

## Quick start

From inside this repo:

```bash
python3 scripts/install.py /path/to/target/repo
```

For the opinionated agentic setup:

```bash
python3 scripts/install.py /path/to/target/repo --preset agentic
```

The `agentic` preset is local-first and agent-tool agnostic. It can be used from
AmpCode, Codex, Claude Code, Aider, Cline, or a manual shell workflow. It does
not require GitHub Actions and is suitable for locked-down on-prem Git servers
such as older Bitbucket deployments.

If you are already inside the target repo and this kit is cloned locally:

```bash
python3 /path/to/repo-contract-kit/scripts/install.py "$(pwd)" --preset agentic
```

If you do not have the kit cloned yet and internet access is available:

```bash
tmp="$(mktemp -d)" && git clone --depth 1 https://github.com/BoweyLou/repo-contract-kit "$tmp/repo-contract-kit" && python3 "$tmp/repo-contract-kit/scripts/install.py" "$(pwd)" --preset agentic
```

Then inside the target repo:

```bash
make workflow-help
make agent-start
make kit-status
make kit-refresh KIT=/path/to/repo-contract-kit
make docs-check
make agent-docs-lint
make agent-docs-localize
make agent-review
make agent-run-review AGENT=manual
make agent-run-review AGENT=manual AGENT_TRUST_PROFILE=untrusted-pr
make agent-research-plan
make agent-research-run RESEARCH_SOURCE=github
make agent-research-synthesize
make agent-research-to-task-packet
make agent-receipt-verify
make agent-task-packet
make agent-task-prepare TASK=<id> SCOPE=<paths>
make agent-test-first
make version-check
```

The everyday rhythm is four moves: orient, review, scope, execute. Use
`make workflow-help` or `docs/working-rhythm.md` in the target repo before
digging into the lower-level command reference.
The research commands require the `review-prompts` profile, which is included
in the `agentic` preset.

## Start an Agent in an Existing Repo

After installing the `agentic` preset, generate a local session packet:

```bash
make agent-start
```

Use `MODE` when you already know the session type:

```bash
make agent-start MODE=drift
make agent-start MODE=test-first
```

The command writes an ignored local packet under `.agent-workflows/runs/` with
an agent brief, machine-readable startup context, and a receipt template. It
records failed discovery checks as warnings instead of blocking startup.
The packet includes a `review_risk` block with the risk tier, selected trust
profile, trigger rules, policy docs, and guidance for whether specialist
reviewers are needed.

If you want to start manually, point Codex, AmpCode, or another local coding
agent at the target repo and give it this brief:

```text
Read AGENTS.md, REVIEW.md, and .agent-workflows/README.md.
Then follow .agent-workflows/repo-review.md in bootstrap mode.
Use the installed personas and prompts under .codex/prompts/ where useful.
Start by running make agent-verify and make agent-docs-localize.
Produce a findings backlog before editing code.
```

You can also run `make agent-review` in the target repo to print this brief
locally.

To materialize a read-only review run, use:

```bash
make agent-run-review AGENT=manual
```

Manual mode creates prompts and placeholder JSON artifacts under the latest
`.agent-workflows/runs/<id>/review-run/` directory. When Amp is installed and
signed in, use:

```bash
make agent-run-review AGENT=amp
```

The Amp adapter calls `amp --execute --stream-json`, saves raw output, extracts
JSON findings, runs synthesis, and fails the run if git status changes during a
read-only reviewer or synthesis call.

Review runs use `.agent-workflows/agent-permission-policy.json`; the default is
`read-only-review`, and `AGENT_TRUST_PROFILE=untrusted-pr` keeps fork-origin or
otherwise untrusted changes artifact-only with no write-back, PR mutation,
browser account mutation, or secret access.

Validate completed run evidence with:

```bash
make agent-receipt-verify
make agent-receipt-verify RECEIPT=.agent-workflows/runs/<run-id>/review-run/receipt.json
```

Strict receipt validation fails when required local evidence is missing or
malformed.

The installer copies a vendored snapshot of the prompt library into the target
repo under `.codex/prompts/`. The companion
[agent-workflow-kit](https://github.com/BoweyLou/agent-workflow-kit) repo is the
canonical place to improve those prompts, but target repos do not need to clone
or fetch it at runtime.

## Updating An Installed Repo

Installs write `.doc-contract-kit/install.json` and
`.doc-contract-kit/manifest.json`. The manifest records the managed files,
their source templates, hashes, installed kit version, source ref, and the
vendored `agent-workflow-kit` prompt snapshot ref/hash.

From the target repo, check what is installed:

```bash
make kit-status
```

To compare the installed target against a local kit checkout:

```bash
make kit-status KIT=/path/to/repo-contract-kit
```

That prints whether the install kit or prompt snapshot has an update available.

To update from a local kit checkout:

```bash
make kit-update KIT=/path/to/repo-contract-kit
```

The updater is safe by default. It overwrites a kit-managed file only when the
target file still matches the last installed hash. If the target file was
customized, it is preserved and a proposed replacement plus report is written
under `.doc-contract-kit/updates/`.

To refresh the local kit checkout first and then run the safe update:

```bash
make kit-refresh KIT=/path/to/repo-contract-kit
```

`kit-refresh` verifies that `KIT` is a clean git checkout, runs
`git pull --ff-only`, prints `kit-status` with the refreshed checkout, and then
runs `kit-update`. If the kit checkout has local changes, commit or stash them
first, or run `kit-update` explicitly when you intentionally want to use that
local working tree.

For internet-enabled repos that do not keep the kit cloned:

```bash
tmp="$(mktemp -d)" && git clone --depth 1 https://github.com/BoweyLou/repo-contract-kit "$tmp/repo-contract-kit" && make kit-update KIT="$tmp/repo-contract-kit"
```

If a legacy install has no manifest, the first update run adopts current file
hashes without overwriting. Re-run the update command after adoption to apply
safe updates.

## Versioning

The kit itself uses root `VERSION` plus `CHANGELOG.md`. Release tags should use
SemVer names such as `v0.3.0` when tags are available, but tags are not required
for locked-down environments.

The `agentic` preset includes the `versioning` profile. It creates target repo
`VERSION`, `CHANGELOG.md`, `docs/versioning.md`, and these commands:

```bash
make version-status
make version-check
make version-bump BUMP=patch
```

`VERSION` and `CHANGELOG.md` are target-owned after creation, so kit updates do
not overwrite the project version history.

If the target repo uses pre-commit hooks:

```bash
pre-commit install
```

To install the test-first executable-spec profile:

```bash
python3 scripts/install.py /path/to/target/repo --profile test-first
```

To compose profiles directly:

```bash
python3 scripts/install.py /path/to/target/repo --profiles review-prompts,test-first
```

## Presets

Presets are the easiest way to install a coherent operating mode:

- `minimal`: documentation contract only.
- `learning`: documentation contract plus review and learning prompts.
- `test-first`: documentation contract plus TDD/executable-spec prompts.
- `agentic`: documentation contract, local agent workflows, review prompts,
  learning prompts, test-first prompts, and local versioning.

## What gets installed

The kit currently installs:

- `doc-contract.json`
- `AGENTS.md`
- `REVIEW.md`
- `docs/documentation-contract.md`
- `docs/working-rhythm.md`
- `docs/ops/agent-workflow.md`
- `docs/ops/agent-instruction-hygiene.md`
- `docs/adr/0000-template.md`
- `.github/pull_request_template.md`
- `.github/workflows/docs.yml`
- `.github/workflows/agent-review-readonly.yml`
- `.pre-commit-config.yaml`
- `Makefile`
- `scripts/check_doc_impact.py`
- `scripts/agent_start.py`
- `scripts/kit_status.py`
- `scripts/lint_agent_docs.py`
- `scripts/verify_agent_receipt.py`
- `scripts/localize_doc_impact.py`
- `scripts/version.py`
- `schemas/task-packet.schema.json`
- `.agent-workflows/instruction-budgets.json`
- `.agent-workflows/schemas/safe-output.schema.json`
- `.agent-workflows/runs/.gitignore`
- `.doc-contract-kit/install.json`
- `.doc-contract-kit/manifest.json`
- `.doc-contract-kit/updates/.gitignore`

The default profile is `minimal`, which keeps target repos portable and does not
assume a local knowledge-base tool.

The `review-prompts` profile also installs:

- `.codex/prompts/multi-agent-repo-review.md`
- `.codex/prompts/codebase-learning-comments.md`
- `.codex/prompts/task-packet.md`
- `.codex/prompts/personas/`
- `.codex/prompts/policies/`
- `.codex/prompts/templates/`
- remediation and verification prompts

The `local-agentic` profile also installs:

- `.agent-workflows/README.md`
- `.agent-workflows/repo-review.md`
- `.agent-workflows/tdd-red-green-receipt.md`
- `.agent-workflows/schemas/session-receipt.schema.json`

Use this profile when the repo must work with local tools only and cannot assume
GitHub Actions, cloud CI, or one specific agent runtime.

The `versioning` profile also installs:

- `VERSION`
- `CHANGELOG.md`
- `docs/versioning.md`

These files are included by the `agentic` preset. Existing target `VERSION` and
`CHANGELOG.md` files are preserved.

## Configuration

`doc-contract.json` lets each target repository customize:

- required documentation contract files
- paths that count as documentation
- ignored paths such as tests
- source paths that imply documentation impact
- expected documentation paths for each impact category

The checker fails when it detects doc-impacting changes without matching
documentation updates. If a change genuinely needs no docs, the PR body must
include `No docs needed: <reason>`, or CI/local automation must provide
`DOC_CONTRACT_NO_DOCS_NEEDED`.

The `test-first` profile also installs:

- `.codex/prompts/tdd/`
- `docs/testing-strategy.md`
- `docs/adr/0001-testing-philosophy.md`
- a PR template with test-first evidence checks

Use it when a repository should treat tests as executable documentation for
features, bug fixes, refactors, API contracts, and high-risk cleanup.

## Installed commands

Installed target repos get Makefile entrypoints:

- `make help` / `make workflow-help`: print the orient, review, scope, execute
  rhythm and point to `docs/working-rhythm.md`.
- `make agent-start`: write an ignored local session packet with an agent
  brief, startup context, latest ADR context, review-risk tier, kit/version
  context, recommended prompts/personas, and a receipt template.
- `make kit-status`: show installed kit version, source ref, prompt snapshot
  ref/hash, profiles, managed manifest status, managed-file cleanliness, and
  target repo version.
- `make kit-status KIT=/path/to/repo-contract-kit`: compare installed
  provenance against a local kit checkout and report whether an update is
  available.
- `make kit-update KIT=/path/to/repo-contract-kit`: safely update managed files
  from a newer local kit checkout.
- `make kit-refresh KIT=/path/to/repo-contract-kit`: fast-forward pull a clean
  local kit checkout, show update status, then run the safe managed update.
- `make docs-check`: run the documentation contract checks.
- `make agent-docs-lint`: check local agent instruction files for hidden
  Unicode, stale paths, unsafe references, contradictions, and instruction
  budget drift.
- `make agent-docs-localize`: emit JSON that maps changed files to likely
  documentation impact.
- `make agent-review`: point the agent at the multi-agent repo review prompt.
- `make agent-run-review AGENT=manual|amp`: generate persona review artifacts,
  or execute them through Amp CLI when `AGENT=amp`.
- `make agent-research-plan`, `make agent-research-run`,
  `make agent-research-synthesize`, and
  `make agent-research-to-task-packet`: create read-only targeted-research
  artifacts when the `review-prompts` profile is installed.
- `make agent-learn`: point the agent at the learner-focused comment prompt.
- `make agent-task-packet`: point the agent at the task-packet prompt for
  backlog items, issues, accepted findings, and broad human requests.
- `make agent-task-prepare TASK=<id> SCOPE=<paths>`: create a
  worktree-per-task branch, local task packet, receipt template, and in-flight
  metadata for an approved write-capable task.
- `make agent-test-first`: point the agent at the TDD/executable-spec prompt chooser.
- `make agent-verify`: run the verification checks currently available in the installed profile.
- `make version-status`: print the target repo version.
- `make version-check`: validate local SemVer.
- `make version-bump BUMP=patch|minor|major`: update `VERSION` and add a
  changelog stub.

The installer writes `.doc-contract-kit/install.json` and
`.doc-contract-kit/manifest.json` so later updates can see which profiles or
preset were installed and which files are safe to manage. The compatibility path
keeps existing installations stable even though the public project name is
repo-contract-kit.

## Recommended rollout

1. Start with one test repo.
2. Install the kit.
3. Let an agent make a small change.
4. See what feels useful or annoying.
5. Adjust the templates and iterate.
6. Only later roll it out widely.

## Philosophy

- docs as code
- explicit documentation obligations
- hooks for local feedback
- optional CI adapters, never required for the core local workflow
- ADRs for important architectural decisions
- gentle adoption path for solo developers
- agent-tool agnostic workflow files before tool-specific adapters
- evidence receipts before trusted automation

## Roadmap

See:

- `docs/vision.md`
- `docs/concepts-for-beginners.md`
- `docs/rollout-guide.md`
- `docs/roadmap.md`

## Development

Run the test suite with:

```bash
make workflow-help
make test
make docs-check
make version-check
```

## Development status

This repository is intentionally early and iterative.
The goal is to create a calm, reusable repository operating system for local
agentic software development.

## Public Repository

This repo is published as
[BoweyLou/repo-contract-kit](https://github.com/BoweyLou/repo-contract-kit).
