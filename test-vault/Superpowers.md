---
title: Superpowers
tags: [superpowers, ai-coding, worktrees, jesse-vincent]
aliases: [superpowers, obra-superpowers]
date: 2026-02-20
author: Jesse Vincent
repo: https://github.com/obra/superpowers
---

# Superpowers

![[superpowers-banner.png]]

**Superpowers** is a collection of skills for AI coding agents, created by [[Jesse Vincent|Jesse]]. It provides the foundational patterns that [[Trycycle Overview|Trycycle]] later adapted and extended.

## Architecture

The core skills include:

- **Git worktrees** — Isolated workspaces sharing a single repository
- **Planning** — Structured implementation plans with explicit contracts
- **Execution** — Disciplined code implementation following plans
- **Finishing** — Clean integration of completed work

> [!warning] Breaking Changes
> Superpowers v0.5 changed the worktree directory convention from `.trees/` to `.worktrees/`. If you're upgrading from an older version, rename your worktree directory and update any scripts.

> [!note] Compatibility
> Superpowers works with both Claude Code and Codex CLI. The skill files are format-compatible across both platforms.

## Worktree Convention

All worktrees live under `.worktrees/` in the project root. This directory must be listed in `.gitignore`:

```bash
echo ".worktrees" >> .gitignore
git add .gitignore && git commit -m "Ignore worktree directory"
```

The naming convention is `<branch-name>`, e.g., `.worktrees/add-dark-mode`.

## Installation

```bash
# Claude Code
git clone https://github.com/obra/superpowers.git ~/.claude/skills/superpowers

# Codex CLI
git clone https://github.com/obra/superpowers.git ~/.codex/skills/superpowers
```

## Nested Lists and Details

Superpowers organises skills in a hierarchy:

- **Core skills**
    - Worktree management
        - Creation and teardown
        - Branch naming conventions
        - Hygiene checks
    - Planning
        - Initial plan creation
        - Plan file format (Markdown with YAML frontmatter)
    - Execution
        - Step-by-step implementation
        - Commit discipline
- **Extension skills**
    - Review loops (added by [[Trycycle Overview|Trycycle]])
    - Test strategy (added by [[Trycycle Overview|Trycycle]])

## Key Metrics

Superpowers tracks several quality signals:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Worktree hygiene | Clean status after each phase | `git status --short` |
| Commit traceability | Each logical change in its own commit | `git log --oneline` |
| Plan fidelity | Implementation matches plan | Reviewer assessment |
| Branch isolation | No cross-contamination | `git diff main...HEAD` |

For large projects, worktree creation adds approximately $2$–$5$ seconds of overhead per branch, which is negligible compared to the $30$–$180$ minutes of agent work that follows.

---
*See also: [[Trycycle Overview]], [[Jesse Vincent]]*
