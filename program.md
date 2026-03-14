# ARC-AGI-3 Play-Learn Protocol

## Goal

Complete ALL levels in ALL games using the minimum total actions.
No instructions — you learn by playing.

## Mindset

Play many times. Each play teaches you something. Resets are free.
Don't try to solve in one attempt — understand the rules first, then execute.

## Rules Discovery

- Don't memorize paths. Understand WHY a path works.
- Interact with every object on the board, even if its purpose isn't clear yet.
- Visual changes may be functional. Test them, don't assume cosmetic.
- If the game uses two different values where one would suffice, ask why.
  Don't collapse distinctions — they're probably meaningful.

## The Loop

```
FOREVER:
  1. Read run.log and strategy.md — what do you know? what's unknown?
  2. Pick a game. Identify 2-4 hypotheses to test.
  3. Launch parallel agents — one per hypothesis — each plays independently
  4. Merge findings into run.log
  5. Update strategy.md with confirmed discoveries, commit
  6. Go to 1
```

## Parallel Hypothesis Testing

One game at a time. Multiple agents in parallel, each testing a different hypothesis.

Example:
- Agent A: "What happens if I go LEFT from every row?" → maps corridors
- Agent B: "Where is the display box?" → reads the frame
- Agent C: "Can I reach X from Y via the bottom?" → tests a route

Each agent gets its own scorecard and session (independent API state).

**How many agents?** Early exploration when everything is unknown — go wide (10+).
As knowledge grows and work becomes sequential, narrow down.
API rate limit: 600 requests/minute.

## What to Learn (per game)

- What does each action do?
- What objects are on the grid? Which move, which are fixed?
- Win condition? What triggers level completion?
- Map layout — where can you go, where are walls?
- Pickups, triggers, special zones?
- Minimum action sequence per level?

## How to Play Fast

- `seq` command runs action strings in one call — use it
- Don't print full frames — grep for positions and cell changes
- Reset freely. Playing the wrong path costs more than resetting.

## Files

- **run.log** — Working memory. Append after every play. Review before next play.
- **strategy.md** — A game manual, not a log. Update rules, don't append walkthroughs.
  Ask: "would this help solve a level I haven't seen?" If not, it's too specific.
- **play.py** — CLI tool. Modify if you need better output.
- **program.md** — This file. The detailed protocol.
- Only the main conversation updates strategy.md — sub-agents report findings,
  they don't write to shared files. This prevents concurrent overwrites.

## NEVER STOP

Keep playing indefinitely. The human might be sleeping.
