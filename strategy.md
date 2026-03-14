# ARC-AGI-3 Game Strategy

This is the mutable strategy file. **This is what gets iterated on during the research loop.**
Read this before playing any game. Update it with learnings after each evaluation round.

## General Approach

1. **Observe the initial frame carefully**: Note grid dimensions, colors, distinct regions,
   borders, and any patterns (symmetry, shapes, corridors).

2. **Identify the game type from available actions**:
   - Actions [1,2,3,4] only → directional movement/sliding puzzle
   - Action [6] only → click-based puzzle
   - Actions [1-6] → hybrid (movement + click + interact)

3. **Explore systematically**: Try each available action once. After each action,
   compare the frame diff to understand what changed. Focus on:
   - What moved? (position changes)
   - What appeared/disappeared? (state changes)
   - Did any counter/indicator change? (progress tracking)

4. **Build a mental model fast**: After 5-10 exploratory actions, form a hypothesis
   about the objective. Look for:
   - Reference/target patterns (bordered boxes showing what to match)
   - Movable objects vs static background
   - Progress indicators (header bars, counters)

5. **Act purposefully once you have a model**.

6. **Use undo (ACTION7)** if available and an action makes things worse.

## Game-Specific Observations

### LS20 (actions: [1,2,3,4], levels: 0/7)
- **Type**: Maze/sliding puzzle
- **Movable object**: A colored block (ccccc/99999, 5 wide × 5 tall)
- **Mechanics**: Block slides through green (3) maze corridors. Movement follows
  corridors, not just straight lines — pressing UP may also shift horizontally.
- **Reference pattern**: Bordered box at rows 8-16 with 9-pattern inside
- **Player marker**: 1/. pattern at rows 31-32 (doesn't move with actions?)
- **Trail**: Each movement adds green (3) pixels at bottom of frame
- **No GAME_OVER**: Can't lose from bad moves (100 random actions survived)
- **TODO**: Figure out what the actual win condition is. Navigate block to match
  the reference pattern? Or navigate player to exit?

### VC33 (actions: [6], levels: 0/7)
- **Type**: Click puzzle
- **Layout**: Left green (3) area, right empty, purple (5) band with bb markers
  at rows 28-31, yellow (9) markers, arrow-shaped 44bb objects
- **Header bar**: Row 0 tracks progress (7 → 4 replacement from right)
- **Clicking bb in purple band**: Progresses header, changes green area dimensions
- **Clicking other areas**: May undo progress
- **CAN GAME_OVER**: Hit GAME_OVER at step 96 during random clicking
- **TODO**: Find the correct click sequence. Maybe need to click specific targets
  in order? Header bar might indicate level progress.

### FT09 (actions: [1,2,3,4,5,6], levels: 0/6)
- **Type**: Tile puzzle (hybrid actions)
- **Layout**: 3×3 grid of colored tiles on left, bordered grid on right
- **Tiles**: Yellow (9) and blue (8) blocks, dotted patterns (./2/8 symbols)
- **Left vs right**: Similar but not identical patterns — possible matching goal
- **Status bar**: Row 63 is all 'c', changes slightly with actions (bb at end)
- **ACTION5**: Minimal visible effect (changed 2 chars in status bar)
- **CAN GAME_OVER**: Hit at step 67 during random play
- **TODO**: Figure out tile interaction. Maybe need to swap/rotate tiles on left
  to match right pattern?

## Action Reference

- ACTION1: Up / primary
- ACTION2: Down / secondary
- ACTION3: Left
- ACTION4: Right
- ACTION5: Select / interact / rotate
- ACTION6: Click at (x, y) coordinates 0-63
- ACTION7: Undo

## Frame Reading

- `.` (0) = black/empty background
- `1-f` = colors (hex digits, 1-15)
- Grid: 64×64, rows shown as `YY|cells...` (only non-empty rows displayed)
