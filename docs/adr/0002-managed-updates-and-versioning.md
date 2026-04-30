# ADR 0002: Managed Updates And Versioning

## Status

Accepted

## Context

The kit is installed into target repositories that may be private, offline,
hosted on old Bitbucket, or unable to run GitHub Actions. Once installed, those
repositories need a low-friction way to receive kit improvements without losing
local changes. The same repositories also need a simple version baseline so
agents can reason about behavior changes, changelog entries, and release impact.

## Decision

Use safe managed updates and local SemVer by default.

The kit publishes its own version in root `VERSION` and records that version,
the source ref, the selected preset, profiles, and managed file hashes in each
target repository under `.doc-contract-kit/`. Installs keep
`.doc-contract-kit/install.json` for compatibility and add
`.doc-contract-kit/manifest.json` as the managed-file source of truth.

Target repositories get local update entrypoints:

- `make kit-status`
- `make kit-update KIT=/path/to/repo-contract-kit`

Updates only overwrite a managed file when the current target file still matches
the last installed hash. If a file was customized, the updater preserves it and
writes a proposed replacement plus a conflict report under
`.doc-contract-kit/updates/`.

Agentic installs include a `versioning` profile. That profile creates
`VERSION`, `CHANGELOG.md`, `docs/versioning.md`, and local version commands when
missing. `VERSION` and `CHANGELOG.md` are target-owned after creation, so kit
updates never overwrite a project version history. Tags should use SemVer names
such as `v0.3.0` when a repository can use tags, but tags are not mandatory.

## Consequences

The default workflow remains local-only and host-agnostic. Agents can inspect
kit version, target repo version, and pending update state without relying on
hosted CI/CD or GitHub APIs.

The updater is intentionally conservative. Customized files require human or
agent review before adopting proposed replacements, which may make updates a
little slower but avoids destructive overwrites.
