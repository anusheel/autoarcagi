# ARC-AGI-3 Autonomous Research Program

## Overview

You are an autonomous research agent improving an ARC-AGI-3 game solver.
Your goal: maximize **win_rate** and **avg_levels** across evaluation games.

## Files

- **CAN modify**: `play.py` (everything — prompts, strategy, rendering, game selection, model)
- **CANNOT modify**: `program.md`, ARC API endpoints, output format (the grep-able lines)

## Setup (do once at start)

1. Confirm `ARC_API_KEY` and `ANTHROPIC_API_KEY` are set in environment
2. Create branch: `git checkout -b autoresearch/<tag>` (e.g. `autoresearch/mar13`)
3. Read all in-scope files: this file, `play.py`
4. Initialize `results.tsv` with header:
   ```
   commit	win_rate	avg_levels	status	description
   ```
5. Run baseline: `uv run play.py > run.log 2>&1` (timeout: 15 min)
6. Parse: `grep "^win_rate:\|^avg_levels:" run.log`
7. If crashed: `tail -n 50 run.log` to debug
8. Record baseline in `results.tsv`

## Experiment Loop (repeat forever)

```
1. Look at git log and results.tsv to understand current state
2. Form a hypothesis (e.g. "better frame rendering will help Claude reason")
3. Modify play.py
4. git commit -am "description of change"
5. Run: uv run play.py > run.log 2>&1  (timeout: 15 minutes, kill if exceeds)
6. Parse: grep "^win_rate:\|^avg_levels:" run.log
7. If crashed (grep empty): tail -n 50 run.log, debug, try again
8. Record in results.tsv (DO NOT commit results.tsv)
9. If win_rate improved (or equal win_rate but higher avg_levels): KEEP
10. If worse: git reset --hard HEAD~1
11. Go to step 1
```

## Metrics

- **Primary**: `win_rate` (fraction of games won, higher is better)
- **Secondary**: `avg_levels` (average levels completed per game, higher is better)
- Both are printed by play.py in grep-able format

## Ideas to Explore

These are starting suggestions. Form your own hypotheses based on results.

- Better frame rendering (highlight changes between steps, compress sparse regions)
- Smarter prompting (chain-of-thought, few-shot examples from early levels)
- Exploration strategies (systematic action testing to discover game mechanics)
- Multi-step planning (think multiple actions ahead)
- Game-type detection (identify the kind of puzzle and adapt strategy)
- History compression (summarize game state instead of raw action log)
- Model selection (faster model for exploration, smarter model for decisions)
- Undo strategies (when to use ACTION7 to backtrack)

## Simplicity Principle

- Small improvement from deleting code? Keep!
- Small improvement from 20 lines of hacky code? Skip.
- Equal results but simpler code? Definitely keep.
- Weigh complexity cost against improvement magnitude.

## NEVER STOP

Once the loop begins, keep going indefinitely. The human might be sleeping.
