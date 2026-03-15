# ARC-AGI-3 Game Strategy

Accumulated knowledge from playing. Updated after each experiment cycle.

## Game: ls20-cb3b57cc (7 levels)

### Confirmed Mechanics
- 64x64 grid, actions U/D/L/R (1-4), S(5) is no-op, X(6) errors
- 5x5 colored block: c(12) top 2 rows, 9 bottom 3 rows
- Block moves by 5 cells per action within workspace of 3-colored regions
- Each move costs 2 b(11) cells from resource bar; failed moves cost 0
- Moving block ONTO 0/1 marker transforms the lower-left box (answer) pattern
- Each marker hit applies alternating H-flip / V-flip (4-hit cycle back to start)
- Block CAN move through corridors narrower than 5 cols (tested: 4-wide works)

### Level Completion (SOLVED for Level 1)
1. Hit the 0/1 marker to transform the answer to match the target
2. Navigate block UP into the target box (upper box with 9-pattern)
3. Push block FURTHER UP inside the box → level completes, grid resets for next level

The trigger is: block enters the target box from below AND the answer matches.
NOT just matching the answer. NOT pressing S. NOT returning to start.

### Level 1 Summary
- Target: 999/..9/9.9 (upper box at rows 8-16, cols 30-38)
- Answer start: 999/9../9.9 → needs 1 H-flip (1 marker hit)
- Marker at rows 31-33, cols 20-22 in workspace
- Path: 9 moves to marker, D to hit, then 6 moves to upper box, U to enter = ~16 total
- Used ~18 b-cells to complete

### Level 2 (IN PROGRESS)
- Levels completed: 1
- Much larger/more complex workspace with multiple corridors and chambers
- Target box at rows 38-46, cols 12-20. Target pattern: 999/9../9.9
- Answer (lower-left box): 999/..9/9.9 → needs transformation to 999/9../9.9
- This is the REVERSE of level 1 (need H-flip again, but in opposite direction)
- Block starts at rows 40-44, cols 29-33
- Marker (0/1) at rows 46-48, cols 50-52 (FAR from target box)
- NEW: Two b(11) "donut" patterns (bbb/b.b/bbb) at rows 16-18 cols 15-17 and rows 51-53 cols 30-32
  - Unknown purpose — could be gates, additional markers, or obstacles
- Resource bar: 84 b-cells (refilled from level 1 amount? actually 100 total b-cells now)

## Reflection (~20+ game actions taken)

### What patterns keep recurring?
- The answer and target are always 3x3 patterns (9s in 5-fill) displayed at different scales
- The 0/1 marker encodes a transformation (H-flip/V-flip cycle)
- The workspace is a maze of 3-valued corridors; need to navigate to marker AND to target box
- Level completion requires BOTH correct answer AND physical block placement in target box

### What's slowing me down?
- Spent many actions testing hypotheses about S-button, returning to start, etc.
- Didn't discover the "enter the target box" trigger until late
- Over-analyzed the 0/1 marker pattern meaning instead of exploring more
- Didn't test if block could enter narrow corridors earlier (wrong assumption about 5-col minimum)

### Is my approach wrong at a higher level?
- MUCH better now that I know the completion trigger
- For level 2+: should immediately identify target, answer, marker, then plan shortest path
- Path: start → marker → target box (minimize total moves)
- Need to figure out what b(11) donut patterns do

### Helper function ideas
- `find_target_pattern(grid)`: auto-detect the 9-pattern in the reference box
- `find_answer_pattern(grid)`: auto-detect current answer from lower-left box
- `map_workspace(grid)`: identify all navigable 5x5-block positions
