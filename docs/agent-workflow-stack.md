# Agent Workflow Stack

Use this page when it is unclear whether a change belongs in
`agent-workflow-kit`, `repo-contract-kit`, or a target repo that has the kit
installed.

This repo is the install layer. It should make target repos easier to operate,
but it should not become the canonical prompt source.

## Layers

| Layer | Location | Owns | Handoff |
| --- | --- | --- | --- |
| Workflow source | `agent-workflow-kit` | Canonical prompts, personas, schemas, task-packet guidance, research workflows, regression fixtures, generated adapter source, and source-side docs. | Export adapters and refresh the vendored prompt snapshot when target repos need new prompt content. |
| Install layer | `repo-contract-kit` | Installer profiles, managed templates, update/conflict behavior, target-repo Make targets, docs-contract scripts, linting, startup packets, receipts, and installed provenance. | Install or update target repos with `make kit-update` or `make kit-refresh`. |
| Installed target repo | Any repo with this kit installed | Day-to-day local workflow commands and repository-specific docs/version decisions. | Report drift with `make kit-status` and apply explicit updates from a local kit checkout. |

Keep the layers separate. The link between them is a recorded snapshot and an
explicit update command, not a runtime dependency on both repos.

## Change Routing

| Change | Start in | Also check | Done when |
| --- | --- | --- | --- |
| Prompt, persona, TDD, research, synthesis, or schema source changes | `agent-workflow-kit` | Whether this repo needs a refreshed vendored snapshot or target-repo docs. | Source validation passes and this repo records any required snapshot or installer-doc update. |
| Installed Make targets, scripts, templates, profiles, manifests, or update behavior | `repo-contract-kit` | Whether `agent-workflow-kit` docs/backlog should mention the new workflow. | Install/update tests pass, `CHANGELOG.md` and `VERSION` are current, and target docs explain the command. |
| Target-repo operator confusion | Usually `repo-contract-kit` templates | Whether the target repo has local overrides that should stay target-owned. | `docs/working-rhythm.md`, `.agent-workflows/README.md`, or `make workflow-help` points to the next command. |
| Source-repo self-dogfood behavior | `agent-workflow-kit` source repo | This repo only if the install layer needs a general template or updater change. | The source repo's `make self-check` still protects prompt-source ownership. |
| Release or provenance pairing | Both repos independently | `make kit-status KIT=/path/to/repo-contract-kit` in targets and `make stack-status KIT=/path/to/repo-contract-kit` in the source repo. | The target records the installed kit version/ref and vendored prompt snapshot. |

## Installed Target Guidance

An installed target repo normally needs only one checkout: the target repo
itself. It can run:

```bash
make workflow-help
make agent-start
make kit-status
```

If the local kit checkout is available, the target can compare and update
explicitly:

```bash
make kit-status KIT=/path/to/repo-contract-kit
make kit-update KIT=/path/to/repo-contract-kit
make kit-refresh KIT=/path/to/repo-contract-kit
```

`kit-update` applies files from the local checkout. `kit-refresh` first verifies
that the local checkout is clean, pulls it fast-forward, then runs the same safe
update path.

## Release Pairing

Keep releases independent:

- `agent-workflow-kit` version means the workflow source changed.
- `repo-contract-kit` version means the installer or installed target-repo
  surface changed.
- each installed target records both the `repo-contract-kit` version/ref and
  the vendored `agent-workflow-kit` prompt snapshot.

Do not make target repos fetch `agent-workflow-kit` at runtime. If prompt source
changes need to reach targets, refresh the vendored snapshot in this repo and
ship that through a normal kit update.
