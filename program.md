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
  1. Read run.log — what do you know? what's the next experiment?
  2. Pick a game and play it
  3. Observe: what changed? what did each action do?
  4. Log to run.log: what you tried, what happened, what you learned
  5. If you confirmed something new, update strategy.md and commit
  6. Go to 1
```

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
