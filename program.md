# ARC-AGI-3 Play-Learn Protocol

## Objective

Play each game many times to discover its rules, then use that knowledge to win.
The games have NO instructions by design — you must explore and learn.
**Speed is critical.** The faster you play, the faster you learn.

## The Loop

```
FOREVER:
  1. Pick a game (rotate between games, or focus on one)
  2. Open scorecard, reset game
  3. PLAY: take actions, observe frame changes
     - After each action, note what changed (block moved? tile toggled? pattern rotated?)
     - If you already know the rules, execute your strategy
     - If exploring, try untested actions to discover mechanics
  4. Game ends (WIN, GAME_OVER, or you decide to reset)
  5. LEARN: update strategy.md with new discoveries
     - What did each action do?
     - What is the win condition?
     - What patterns/corridors/objects exist?
     - What sequence of actions makes progress?
  6. Commit strategy.md if you learned something significant
  7. Go to 1
```

## How to Play Fast

- **Use `seq` for known sequences.** If you know UUUULLLL works, run it in one call.
- **Use individual actions for exploration.** When learning, take one action, read the frame diff, decide the next.
- **Don't render full frames.** Filter for the rows that matter (where objects are, where changes happen).
- **Track positions numerically.** Use block/cross coordinates, not visual inspection.
- **Reset freely.** Timer expired? Fine — you learned something. Reset and try a different path.
- **Parallelize exploration.** Try different routes in separate game sessions.

## What to Record in strategy.md

For each game, build up knowledge:

```
### Game: <id>
**Actions**: what each action does
**Objects**: what's on the grid, what moves, what's fixed
**Win condition**: what triggers level completion
**Level N strategy**: specific action sequence or approach
**Corridors/paths**: where you can and can't go
**Traps**: what causes GAME_OVER, what wastes time
```

## Files

- **strategy.md** — Your accumulated knowledge. THE key artifact. Update constantly.
- **play.py** — CLI tool. Modify if you need better frame analysis or new commands.
- **program.md** — This file. Do not modify.

## Playing Multiple Games

Three games available: LS20, VC33, FT09. Each is different:
- Some use directional movement (ACTION1-4)
- Some use clicks (ACTION6)
- Some use both

Rotate between games. If stuck on one, try another. Cross-game patterns may transfer.

## Frame Analysis Tips

- Compare frames before/after each action to understand what changed
- Hash frames (excluding timer rows) to detect true state changes vs timer-only changes
- Count pixels changed: 0-2 = wall hit, ~50 = normal move, ~100+ = special event (overlap, pickup, level transition)
- 1000+ pixels changed = level transition

## NEVER STOP

Once the loop begins, keep playing indefinitely. The human might be sleeping.
Every play teaches you something. Even failed attempts build knowledge.
