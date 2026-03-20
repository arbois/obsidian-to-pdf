---
title: Jesse Vincent
tags: [people, superpowers]
aliases: [obra, Jesse]
date: 2026-02-20
role: creator
github: https://github.com/obra
---

# Jesse Vincent

Creator of [[Superpowers]], the foundational skill set that [[Trycycle Overview|Trycycle]] later adapted. Known in the open-source community as **obra**.

## Key Design Decisions

Jesse's original [[Superpowers#Architecture|architecture]] made several decisions that proved foundational:

- **Worktree isolation** — Every task gets its own git worktree, preventing cross-contamination between concurrent work streams
- **Plan-first execution** — Agents write a plan before touching code, reducing wasted effort
- **Commit discipline** — Each logical change gets its own commit, making review and rollback tractable

> [!note] On Worktrees
> The `.worktrees/` convention was not the original choice. Early versions used `.trees/`, but this was changed in v0.5 for clarity. See [[Superpowers#Worktree Convention]].

## Embedded Note

![[Trycycle Overview#How It Works]]

## The Dark Factory Inspiration

The "dark factory" metaphor — fully autonomous manufacturing with no human on the floor — was central to Jesse's thinking. In this model:

$$\text{Quality} = f(\text{independent reviewers}, \text{fresh context}, \text{iteration count})$$

The insight was that quality improves *more* with independent reviewers than with a single reviewer given more time. This is analogous to the bias-variance tradeoff in statistics:

- A single long review has low variance but potentially high bias (the reviewer develops blind spots)
- Multiple independent short reviews have higher variance per review but lower aggregate bias

## Related

- [[Superpowers]] — The skill set Jesse created
- [[Trycycle Overview]] — The project that adapted superpowers
- [[Dan Shapiro]] — Who extended Jesse's work with hill-climbing

#people #superpowers #ai-coding
