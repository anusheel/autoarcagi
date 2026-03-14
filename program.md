# ARC-AGI-3 Play-Learn Protocol

## Goal

Complete ALL levels in ALL games using minimum total actions.
No instructions — learn by playing. Resets are free. Understand rules first, then execute.

## Architecture

**Opus (main conversation)** — the brain. Reads run.log + strategy.md, forms hypotheses,
writes experiment scripts, analyzes results, updates strategy.

**Sonnet (sub-agents)** — the hands. Launched with `model: "sonnet"`.
Give exact commands, not goals. Minimal context — only game_id, card_id, specific facts.
They don't read/write run.log or strategy.md. Return raw output — Opus does analysis.

## The Loop

```
FOREVER:
  1. Read run.log and strategy.md — what do you know? what's unknown?
  2. Pick a game. Determine phase:
     - Exploration: batch scripts to map actions, walls, objects.
     - Hypothesis testing: adaptive scripts with Python if/else branching.
     - Solving: LLM in the loop, react to state with known rules.
  3. Phase 1-2: Write experiment scripts, launch Sonnet agents in parallel.
     Phase 3: Drive directly or use Sonnet with specific seq commands.
  4. Read results. Merge findings into run.log.
  5. Update strategy.md with confirmed discoveries.
  6. Commit and push when strategy.md, program.md, or play.py change.
  7. Go to 1.
```

## What to Learn (per game)

- What does each action do?
- What objects exist? Which move, which are fixed?
- Win condition — what triggers level completion?
- Map layout — walkable areas, walls, boundaries
- Pickups, triggers, special zones?
- Interact with EVERY object, even if purpose is unclear
- Visual changes may be functional — test them
- Don't memorize paths. Understand WHY a path works.

## Experiment Scripts

Put scripts in `experiments/`. Import helpers from `play.py`:

| Function | Purpose |
|---|---|
| `reset(game_id, card_id, guid=None)` | Reset game, get obs |
| `act(action_cmd, game_id, guid, x=None, y=None)` | Single action, get obs |
| `seq(game_id, guid, "UULLDR")` | Run move string, get list of obs |
| `frame_to_grid(obs)` | Extract 2D grid from obs |
| `find_objects(grid, val)` | Find all (row, col) with value |
| `find_blob(grid, val, min_size=3)` | Bounding box of largest region |
| `diff_frames(grid_a, grid_b)` | Dict of changed cells |
| `grid_summary(grid)` | Value counts |
| `run_sequences(game_id, card_id, ["UUU", "LLL", ...])` | Batch test sequences |
| `render(frame_data)` | Text render of frame |

Script guidelines: print structured output, reset between trials, one hypothesis per script, game_id/card_id as constants at top.

## Commands

```bash
source .env
uv run play.py games
uv run play.py scorecard-open
uv run play.py reset <game_id> <card_id>
uv run play.py action ACTION1 <game_id> <guid>
uv run play.py seq <game_id> <guid> UUUULLLLDR
uv run python experiments/exp_NNN.py
```

## Logging

Append to `run.log` after every experiment. Keep it terse:

```
=== LS20 exp #3 ===
Script: experiments/exp_003.py (test 20 L-first sequences)
Result: L moves blocked at col 4, U moves open to row 8
Learning: left wall at col 4, vertical corridor above start
Next: map vertical extent with U-sequences of length 5-15
```

## Meta

Never stop — keep playing indefinitely. Every ~5 iterations, reflect: is the process working? If not, update this file (program.md), play.py, or strategy.md (prune wrong/stale entries).
