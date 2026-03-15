# ARC-AGI-3

Complete ALL levels in ALL games using minimum total actions.
No instructions — learn by playing.

## How

You play directly by calling play.py functions from the shell. One action at a time. Think between each action.

```
FOREVER:
  1. Read strategy.md (use the Read tool). Paste key facts into your thinking.
     If you skip this step, everything after is wasted.
  2. State a hypothesis OUT LOUD before touching the game.
  3. Take 1-3 actions to test it. Read the output. Think.
  4. Update strategy.md with what you learned (use the Edit tool).
     Do this BEFORE moving on to the next hypothesis.

  HARD RULES (non-negotiable):
  - Never run more than 3 act()/seq() calls in a single shell command.
    NEVER chain moves like `for m in 'UUULLLD'`. Each shell invocation
    calls act() at most 3 times.
  - You MUST read strategy.md (Read tool) before every cycle.
  - You MUST write to strategy.md (Edit tool) after every cycle.
  - If you haven't updated strategy.md in your last 3 messages, STOP
    and update it NOW. Do not take another game action.
  - Never open a new scorecard without first recording what you learned
    from the current one in strategy.md.

  WARNING SIGNS (if any are true, stop and write strategy.md):
  - You've run >5 game actions without writing to strategy.md.
  - You opened a new scorecard without recording learnings.
  - You're looping through positions without a stated hypothesis.
  - You're running the same experiment you ran 10 minutes ago.

  EVERY ~10 TOTAL GAME ACTIONS (count them), or after completing/failing:
  5. REFLECT — stop playing and write a ## Reflection section:
     - What patterns keep recurring?
     - What's slowing me down?
     - Is there a helper function that would save repeated work?
     - Is my approach wrong at a higher level?
  6. Update play.py and/or this file if the tools or methodology should change.
  7. Git commit and push any changes to program.md, play.py, or strategy.md.
     Commit message = one-line reason for the change.
```

## Principles

- Think more, act less. Understand the grid before moving.
- Every action must test a specific hypothesis.
- Stop when something unexpected happens — that's the learning.
- Periodically zoom out. Improving tools and methodology compounds.
- Separate learning from scoring. On a new game, play a full exploratory run — spend actions freely to understand mechanics. Only optimize for minimum actions once the rules are clear.
- Don't reset prematurely. A "wasted" action that teaches you something is cheaper than resetting and relearning. Only reset when the current run is genuinely unrecoverable.

## play.py

Call functions directly: `source .env && uv run python -c "from play import *; ..."`

**State persistence:** Python state resets between invocations. After calling `start()`, capture `card_id`, `guid`, and `game_id` from the output. Pass them as literals in all subsequent `act()`/`seq()`/`reset()` calls.

| Function | Purpose |
|---|---|
| `start(game_id)` | Open scorecard + reset, returns (card_id, obs) |
| `reset(game_id, card_id, guid=None)` | Reset game, get obs |
| `act(action_cmd, game_id, guid, x=None, y=None)` | Single action, get obs |
| `seq(game_id, guid, "UULLDR")` | Run move string, get final obs |
| `frame_to_grid(obs)` | Extract 2D grid from obs |
| `find_objects(grid, val)` | Find all (row, col) with value |
| `diff_frames(grid_a, grid_b)` | Dict of changed cells |
| `grid_summary(grid)` | Value counts |
| `render(frame_data)` | Text render of frame |
