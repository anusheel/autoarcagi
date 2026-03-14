# ARC-AGI-3 Play-Learn Protocol

## Goal

Complete ALL levels in ALL games using the minimum total number of actions.
You learn the rules by playing — there are no instructions.

## Mindset

You are a player learning a new game. You will play many times.
Each play teaches you something. Deaths, resets, timer expiry — all fine.
Knowledge accumulates across plays. Once you understand the rules,
you execute the optimal strategy.

**Do not try to solve a game in one attempt.** Play, learn, play again.

## The Loop

```
FOREVER:
  1. Read run.log and strategy.md — what do you know? what's still unknown?
  2. Pick a game to focus on
  3. Identify 2-4 hypotheses to test about that game
  4. Launch parallel agents — one per hypothesis — each plays independently
  5. Merge their findings into run.log
  6. Update strategy.md with confirmed discoveries, commit
  7. Go to 1
```

## Parallel Hypothesis Testing

Focus on ONE game at a time. For each learning round, launch multiple
agents in parallel, each testing a different hypothesis about the same game.

Example for a movement puzzle:
- Agent A: "What happens if I go LEFT from every row?" → maps corridors
- Agent B: "Where is the display box?" → reads the frame
- Agent C: "Can I reach X from Y via the bottom?" → tests a route

Each agent gets its own scorecard and session (independent API state).
Each agent reports back: what it tried, what it observed, what it learned.
You merge all findings, update strategy, and plan the next round.

This multiplies your learning rate — 3 agents = 3x the experiments per round.

**How many agents?** One per independent hypothesis. Early exploration (many
unknowns) → more agents. Later execution (sequential dependencies) → fewer.
ARC API rate limit is 600 requests/minute — you can comfortably run 4-5
parallel agents without hitting it. Go hard when there are many open questions.

## What to Learn (per game)

- What does each available action do?
- What objects are on the grid? Which move, which are fixed?
- What is the win condition? What triggers level completion?
- What is the map/layout? Where can you go, where are walls?
- Are there pickups, triggers, special zones?
- What's the minimum action sequence to complete each level?

## How to Play Fast

- `seq` command runs action strings in one call — use it
- Don't print full frames — grep for positions and cell changes
- Each action = one API call. Minimize wasted actions per play.
- Reset freely. Each reset is cheap. Playing the wrong path is expensive.

## Files

- **run.log** — Working memory. Append after every play. Review before next play.
- **strategy.md** — Confirmed knowledge. Commit when you learn something real.
- **play.py** — CLI tool. Modify if you need better output.
- **program.md** — This file. Do not modify.

## NEVER STOP

Keep playing indefinitely. The human might be sleeping.
