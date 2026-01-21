# AGENTS.md for Coding Agents

Today I learned how an AGENTS.md file sets expectations for AI coding agents.

## What it is

AGENTS.md is a lightweight, repo-local contract. It tells an agent how to behave in this codebase: where to look for context, how to run tests, style conventions, and any do-or-don't rules that matter for safe changes.

## What it usually contains

- Scope and expectations for tasks in this repo.
- Required workflows (build steps, lint, tests, review checklist).
- Code style rules or project conventions.
- Safety constraints (what not to touch, secrets, or deployment gates).
- Pointers to other docs and the fastest path to context.

## Why it helps

- Saves time by eliminating guesswork on setup and workflow.
- Reduces risky changes by stating non-negotiable constraints.
- Keeps agent output consistent with repo norms.

## How I plan to use it

1. Put AGENTS.md at the repo root so it is easy to discover.
2. Keep instructions short and specific to this project.
3. Update it alongside tooling changes to avoid drift.

## Quick tip

Write AGENTS.md like onboarding notes for a new teammate. Clarity beats completeness.
