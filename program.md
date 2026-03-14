# ARC-AGI-3 Play-Learn Protocol

## Objective

Play each game many times to discover its rules, then use that knowledge to win.
The games have NO instructions by design — you must explore and learn.
**Speed is critical.** The faster you play, the faster you learn.

## The Loop

```
FOREVER:
  1. Pick a game
  2. Open scorecard, reset game
  3. PLAY: take actions, observe what changes
  4. Game ends (WIN, GAME_OVER, or timer expires)
  5. LEARN: append observations to run.log
  6. If you discovered something new, update strategy.md and commit
  7. Go to 1
```

## run.log

Append after every play session. Keep it terse:
- What you tried
- What happened (positions, cell changes, level transitions)
- What you learned
- What to try next

This is your working memory between plays. Review it before each new attempt.

## strategy.md

Confirmed knowledge only. For each game, record:
- What each action does
- What objects exist and how they behave
- Win condition
- Level-specific strategies and action sequences
- Map of corridors/paths/walls

Commit when you learn something significant.

## How to Play Fast

- Use `seq` for known sequences (one API call per action, but fast output)
- For exploration: individual actions, check the diff
- Don't render full frames — filter for rows that matter
- Track positions numerically via block/cross coordinates
- Reset freely — timer expiry is fine, you keep your knowledge

## Frame Analysis

- 0-2 cells changed = wall hit (blocked)
- ~50 cells changed = normal movement
- ~100+ cells changed = special event (cross overlap, pickup)
- ~200 cells changed = timer expired (life lost, level resets)
- 1000+ cells changed = level transition

## Files

- **strategy.md** — Confirmed knowledge (committed)
- **run.log** — Working observations (gitignored)
- **play.py** — CLI tool (modify if needed)
- **program.md** — This file (do not modify)

## NEVER STOP

Keep playing indefinitely. The human might be sleeping.
