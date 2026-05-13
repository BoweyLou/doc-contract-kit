# Repo Boundary With agent-workflow-kit

`repo-contract-kit` is the install and target-repo governance layer. Before
changing agentic workflow behavior, check the companion `agent-workflow-kit`
checkout as well as this repo.

## Ownership

`repo-contract-kit` owns:

- installer presets, profiles, update, and migration behavior
- target-repo managed files such as `AGENTS.md`, `REVIEW.md`,
  `.agent-workflows/`, `.codex/prompts/`, `.doc-contract-kit/`, and Make targets
- docs-contract checks, instruction linting, receipt verification, versioning
  profile, local review runners, and optional CI/PR/runtime adapters

`agent-workflow-kit` owns:

- canonical prompts, personas, workflow manifests, TDD prompts, learning-comment
  prompts, task packets, receipt schemas, synthesis schemas, eval fixtures, and
  adapter source definitions

## Working Rule

For any AGW backlog item, check both local repos before implementation. If the
change crosses the boundary, update both repos or record why the companion repo
does not need a change.

Do not duplicate prompt or schema source in this repo when it should be vendored
from `agent-workflow-kit`. This repo should install, validate, and update those
artifacts in target repos.
