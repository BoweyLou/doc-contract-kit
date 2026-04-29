# TDD and Executable Specs Prompt Set

Use these prompts when the work should be driven by executable behavior, not just post-hoc tests.

## Default Choice

- New feature: `test-first-feature.md`
- Bug fix: `regression-first-bugfix.md`
- Refactor or cleanup: `characterization-before-refactor.md`
- API/schema boundary: `contract-test-design.md`
- Complex invariants: `property-and-invariant-tests.md`
- Final review: `test-quality-sentinel.md`

## Workflow

1. Start from user-visible behavior, a bug reproduction, or a contract.
2. Write the smallest failing test that proves the next slice of behavior.
3. Implement only enough code to pass.
4. Refactor under the protection of the tests.
5. Run the smallest meaningful verification loop before broad suites.

These prompts are deliberately compatible with the repo-review prompt set: use review prompts to find risk, then use these prompts to fix the accepted risk with executable evidence.

