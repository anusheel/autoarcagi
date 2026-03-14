# ARC-AGI-3 Autonomous Research Program

## Overview

You are an autonomous research agent improving an ARC-AGI-3 game solver.
You ARE the reasoning engine — you call `play.py` CLI commands, read frames, and decide actions.
Your goal: maximize **win_rate** and **avg_levels** across evaluation games.

## Files

- **CAN modify**: `strategy.md` (your game-playing strategy — the main thing to iterate on)
- **CAN modify**: `play.py` (frame rendering, CLI interface — rarely needs changes)
- **CANNOT modify**: `program.md`

## Setup (do once at start)

1. Confirm `ARC_API_KEY` is set
2. Create branch: `git checkout -b autoresearch/<tag>` (e.g. `autoresearch/mar13`)
3. Read all files: this file, `strategy.md`, `play.py`
4. Initialize `results.tsv` with header:
   ```
   commit	win_rate	avg_levels	games	status	description
   ```
5. List games: `uv run play.py games`
6. Pick EVAL_GAMES (start with 3-5 games)
7. Run baseline evaluation (see "Playing Games" below)
8. Record baseline in `results.tsv`

## Playing Games

For each evaluation round, play the same set of games:

```
1. uv run play.py scorecard-open                    → get card_id
2. For each game in eval set:
   a. uv run play.py reset <game_id> <card_id>      → get guid, see frame
   b. Read strategy.md, reason about the frame
   c. uv run play.py action <CMD> <game_id> <guid>  → see new frame
   d. Repeat (c) until state=WIN or state=GAME_OVER (max 200 steps)
   e. Record: game_id, levels_completed, state, steps
3. uv run play.py scorecard-close <card_id>          → get summary
4. Compute win_rate and avg_levels
```

## Experiment Loop (repeat forever)

```
1. Look at results.tsv to understand current performance
2. Analyze: which games did you lose? Why? What patterns did you miss?
3. Form a hypothesis for improvement
4. Update strategy.md with new insights/approach
5. git commit -am "description of change"
6. Play the same eval games again (see "Playing Games")
7. Record in results.tsv:
   commit  win_rate  avg_levels  games  status  description
8. If win_rate improved (or equal but higher avg_levels): KEEP
9. If worse: git reset --hard HEAD~1
10. Go to step 1
```

## Metrics

Print after each evaluation round:
```
win_rate:    0.4000
avg_levels:  15.60
```

## What to Iterate On

The main lever is `strategy.md`. Improve it by:
- Adding game-type-specific strategies you discover
- Refining the exploration approach
- Adding pattern recognition heuristics
- Recording what action sequences work for what situations
- Noting common failure modes and how to avoid them

You can also modify `play.py` if the frame rendering needs improvement.

## Simplicity Principle

- Small improvement from deleting strategy text? Keep!
- Small improvement from a page of hacky heuristics? Skip.
- Equal results but cleaner strategy? Definitely keep.

## NEVER STOP

Once the loop begins, keep going indefinitely. The human might be sleeping.
