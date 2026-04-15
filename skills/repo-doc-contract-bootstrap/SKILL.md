---
name: repo-doc-contract-bootstrap
description: Bootstrap the doc-contract-kit starter files into a target repository and explain the installed system in beginner-friendly terms.
version: 0.1.0
author: Yannick Bowe and Hermes Agent
license: MIT
---

# repo-doc-contract-bootstrap

## Purpose

Install the doc-contract-kit starter files into a repository so documentation expectations become explicit and enforceable.

## When to use

Use this when:
- a repository has documentation drift
- coding agents are making changes without updating docs
- the user wants a calm first step toward hooks, CI, and PR-based workflows

## Procedure

1. Confirm the target path is a git repo.
2. Inspect whether docs/, .github/, and scripts/ already exist.
3. Install or update the starter files from doc-contract-kit.
4. Explain what was installed in beginner-friendly language.
5. Run `make docs-check` if the target repo has the installed files.
6. Summarize any collisions or manual follow-up.

## Important rule

Do not silently overwrite existing files unless the user asked for it or the workflow explicitly supports force mode.
