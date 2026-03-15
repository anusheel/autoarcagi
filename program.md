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
     - What assumption cost me the most actions? Could a principle change prevent it next time?
     - Did I get stuck in a loop? What would have broken me out sooner?
  6. Update play.py AND this file. program.md changes should be GENERIC
     principles (not game-specific). Game-specific notes go in strategy.md.
  7. Git commit and push any changes to program.md, play.py, or strategy.md.
     Commit message = one-line reason for the change.
```

## Principles

- Think more, act less. Understand the grid before moving — BUT don't over-analyze when a single action would answer the question faster than 5 minutes of reasoning. If you're staring at grid coordinates trying to predict what will happen, just try it.
- Every action must test a specific hypothesis.
- Stop when something unexpected happens — that's the learning.
- Periodically zoom out. Improving tools and methodology compounds.
- Separate learning from scoring. On a new game, play a full exploratory run — spend actions freely to understand mechanics. Only optimize for minimum actions once the rules are clear.
- Don't reset prematurely. A "wasted" action that teaches you something is cheaper than resetting and relearning. Only reset when the current run is genuinely unrecoverable.
- Test assumptions about constraints early. If you think something is impossible (block can't fit, path is blocked, action won't work), spend 1 action to verify. Wrong assumptions about what's impossible are the most expensive kind of wrong.
- When stuck in a loop (same hypothesis tested 3+ times with no progress), ESCALATE: try a qualitatively different kind of action, not a variation of the same one. Move to an unexplored part of the grid. Try an action you assumed wouldn't work.
- Discover the win condition early. On a new game, once you can cause ANY change, immediately prioritize figuring out what triggers level completion. Don't perfect your understanding of every mechanic before testing what "winning" looks like.
- Reflection must examine methodology, not just game facts. Ask: "What principle led me astray?" not just "What did I learn about the grid?"

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
| `answer_pattern(grid)` | Read 3x3 answer from lower-left box (2x scale) |
| `target_pattern(grid)` | Find & read 3x3 target from reference box |
| `level_status(obs)` | Print block pos, marker, answer vs target, resources |

## ls20 Game Notes

Level completion requires TWO things:
1. Transform answer to match target by moving block ONTO the 0/1 marker (each hit = H-flip or V-flip, 4-hit cycle)
2. Navigate block UP INTO the target reference box from below

Workflow per level:
1. `level_status(obs)` to see answer, target, marker, block position
2. Determine how many marker hits needed (1 H-flip usually)
3. Plan shortest path: start → marker → target box
4. Execute, entering target box from below with final U move
