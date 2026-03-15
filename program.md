# ARC-AGI-3

Complete ALL levels in ALL games using minimum total actions.
No instructions — learn by playing.

## How

You play directly by calling play.py functions from the shell. One action at a time. Think between each action.

```
FOREVER:
  1. Read strategy.md — what do you know?
  2. State a hypothesis.
  3. Take 1-3 actions to test it. Read the output. Think.
  4. Update strategy.md with what you learned.

  HARD RULES:
  - Never run more than 3 game actions in a single shell command.
  - You MUST read strategy.md before every cycle.
  - You MUST write to strategy.md after every cycle.
  - If you haven't updated strategy.md in your last 3 messages, STOP and update it now.

  EVERY ~10 ACTIONS, or after completing/failing a game:
  5. REFLECT — step back and ask:
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
