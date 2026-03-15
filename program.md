# ARC-AGI-3

Complete ALL levels in ALL games using minimum total actions.
No instructions — learn by playing.

## How

You play directly by calling play.py functions from the shell. Think between each shell invocation — read the output before acting again.

```
EVERY CYCLE:
  1. Read strategy.md (Read tool). Paste key facts into your thinking.
     If you skip this step, everything after is wasted.
  2. State a hypothesis OUT LOUD before touching the game.
  3. Take 1-3 actions to test it. Read the output. Think.
  4. Update strategy.md with what you learned (Edit tool).
     Do this BEFORE moving on to the next hypothesis.

EVERY ~10 ACTIONS (or after completing/failing a level):
  5. REFLECT — score yourself on each Self-Reflection dimension below.
     For each, note one concrete change to make going forward.
  6. Update play.py AND this file. program.md changes should be GENERIC
     principles (not game-specific). Game-specific notes go in strategy.md.
  7. Git commit and push any changes to program.md, play.py, or strategy.md.
     Commit message = one-line reason for the change.

HARD RULES (non-negotiable):
  - Max 3 act()/seq() calls per shell command. NEVER chain moves.
  - You MUST read strategy.md before every cycle.
  - You MUST write to strategy.md after every cycle.
  - If you haven't updated strategy.md in your last 3 messages, STOP
    and update it NOW.
  - Never open a new scorecard without recording learnings first.

WARNING SIGNS (if any are true, stop and write strategy.md):
  - You've run >5 game actions without writing to strategy.md.
  - You opened a new scorecard without recording learnings.
  - You're looping through positions without a stated hypothesis.
  - You're running the same experiment you ran 10 minutes ago.
```

## Principles

- Prefer thinking to acting — but never reason about what an action will do when you could just try it. Analysis is for choosing WHICH action; the game itself is faster than prediction.
- Every action must test a specific hypothesis. "What does this object do?" counts — curiosity about an unexplored object is a valid hypothesis.
- Stop when something unexpected happens — that's the learning.
- Periodically zoom out. Improving tools and methodology compounds.
- On a new game, explore before optimizing. Spend actions freely to discover the win condition and core mechanics. Only minimize actions once the rules are clear.
- Don't reset prematurely. A "wasted" action that teaches you something is cheaper than resetting and relearning. Only reset when the current run is genuinely unrecoverable.
- Test assumptions about constraints early. If you think something is impossible (block can't fit, path is blocked, action won't work), spend 1 action to verify. Wrong assumptions about what's impossible are the most expensive kind of wrong.
- When stuck in a loop (same hypothesis tested 3+ times with no progress), ESCALATE: try a qualitatively different kind of action, not a variation of the same one. Move to an unexplored part of the grid. Try an action you assumed wouldn't work.
- Poke every interesting object. If something on the board looks distinct — a box, a pattern, a colored region — try to interact with it. Don't assume anything is decoration. Prioritize finding the win condition: it's usually hidden behind an object you haven't touched yet.

## Self-Reflection

Score yourself on these six dimensions every ~10 actions. For each, note one concrete change.

- **Process** — The methodology exists to prevent drift. If you skipped steps, the issue isn't speed — it's that you'll repeat mistakes you already solved.
- **Action economy** — Every action that doesn't teach you something new is pure waste. If you can't say what you learned from an action, you chose wrong.
- **Assumptions** — The things you "know" without testing are where the biggest losses hide. Name your assumptions out loud so you can catch them.
- **Exploration** — Ignoring something is a choice. If there's an object, area, or action you haven't tried, ask why — avoidance is usually a hidden assumption.
- **Stuck detection** — The moment you repeat an experiment, you're stuck. Three actions without new information means change approach, not try harder.
- **Tools** — If you've done the same manual work three times, write a helper. Time spent on tooling pays back every subsequent action.

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
