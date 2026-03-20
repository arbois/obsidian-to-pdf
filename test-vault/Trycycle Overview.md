---
title: Trycycle Overview
tags: [trycycle, ai-coding, hill-climbing]
aliases: [Trycycle, trycycle-skill]
date: 2026-03-15
status: published
---

# Trycycle

**Trycycle** is a skill for [[Claude Code]] and [[Codex CLI]] that plans, strengthens, and reviews your code — automatically. It was created by [[Dan Shapiro]].

## How It Works

Trycycle is a *hill climber*. The process follows these stages:

1. **Planning** — A subagent writes an implementation plan
2. **Plan editing** — Fresh editors critique and improve the plan (up to 5 rounds)
3. **Test planning** — A subagent builds a concrete test plan
4. **Execution** — A dedicated subagent implements the code
5. **Review** — Fresh reviewers find issues; the executor fixes them (up to 8 rounds)

Each review uses a new reviewer with no memory of previous rounds, so stale context never accumulates.[^1]

> [!tip] Key Insight
> The hill-climbing approach means each round starts fresh. This prevents the "sunk cost" problem where agents defend earlier decisions instead of improving them.

## Architecture

| Component | Role | Lifecycle |
|-----------|------|-----------|
| Planning agent | Writes initial plan | Ephemeral |
| Plan editor | Critiques and revises | Ephemeral per round |
| Implementation agent | Writes code | Persistent across fix rounds |
| Review agent | Finds issues | Ephemeral per round |
| Test strategy agent | Proposes test approach | Ephemeral |

## Relationship to Superpowers

Trycycle's planning, execution, and worktree management skills are adapted from [[Superpowers]] by [[Jesse Vincent|Jesse]]. See [[Superpowers#Architecture]] for the original design.

The key differences are:

- [x] Hill-climbing review loop
- [x] Ephemeral plan editors
- [x] Bundled Python orchestrator
- [ ] Native MCP integration (planned)
- [ ] Multi-repo support (planned)

## Performance Metrics

The planning phase typically takes $30$–$60$ minutes per round. For a plan that converges in $n$ rounds, total planning time is approximately:

$$T_{\text{plan}} = n \times (30 + \epsilon) \text{ minutes}$$

where $\epsilon$ accounts for workspace hygiene checks between rounds.

Similarly, the review loop has complexity $O(r)$ where $r \leq 8$ is the number of review rounds needed.

[^1]: This is inspired by the work of Justin McCarthy, Jay Taylor, and Navan Chauhan at StrongDM.

---
*See also: [[Planning Deep Dive]], [[Review Loop Mechanics]]*
