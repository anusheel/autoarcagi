# ARC-AGI-3

Complete ALL levels in ALL games using minimum total actions.
No instructions — learn by playing.

## How

Play by calling play.py functions from the shell. Think between each invocation.

```
LOOP:
  1. Read strategy.md. Paste key facts into your thinking.
  2. State hypothesis OUT LOUD.
  3. Take 1-3 actions to test it. Read output. Think.
  4. Update strategy.md with what you learned.
  5. Every ~10 actions or after completing/failing: REFLECT (see below),
     update play.py and program.md (generic only), commit and push.

RULES:
  - Max 3 act()/seq() per shell command. NEVER chain moves.
  - No strategy.md update in last 3 messages? STOP and update now.
  - Never open a new scorecard without recording learnings first.
  - Same experiment twice? Change approach.
```

## Principles

- Think before acting, but never theorize when one action would answer it.
- Every action tests a hypothesis. Curiosity counts — "what does this do?" is valid.
- Something unexpected? Stop. That's the learning.
- Explore before optimizing. Find the win condition first, perfect mechanics later.
- Don't reset prematurely. A "wasted" action that teaches beats restarting blind.
- Think something is impossible? Spend 1 action to check. Untested constraints are the costliest assumptions.
- Stuck 3+ times on the same idea? ESCALATE — try something qualitatively different.
- Poke every interesting object. Nothing is decoration until proven otherwise.
- Zoom out periodically. Better tools and methodology compound.

## Self-Reflection

Every ~10 actions, score yourself on each dimension. Note one concrete change per dimension.

- **Process** — Did you follow the loop? Skipping steps means repeating mistakes.
- **Action economy** — Can you say what each action taught you? If not, it was waste.
- **Assumptions** — What did you "know" without testing? Name them to catch them.
- **Exploration** — What haven't you tried? Avoidance is usually a hidden assumption.
- **Stuck detection** — How many actions before you changed approach? What signal did you miss?
- **Tools** — Done the same thing 3 times by hand? Write a helper.

## play.py

`source .env && uv run python -c "from play import *; ..."`

State resets between invocations. Capture `card_id`, `guid`, `game_id` from `start()` and pass as literals.

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
