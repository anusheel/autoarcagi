# ARC-AGI-3 Game Strategy

This is the mutable strategy file. **This is what gets iterated on during the research loop.**

## General Approach

1. **Classify the game** by available actions and frame layout
2. **Explore systematically** — try each action once, track frame diffs
3. **Form a hypothesis** about the win condition within 5-10 actions
4. **Execute purposefully** once you have a model
5. **Track progress** — watch levels_completed, state changes, indicators

## LS20: Pattern Rotation Puzzle (SOLVED)

**Actions**: [1,2,3,4] = UP/DOWN/LEFT/RIGHT. Block moves 5 cells per action.

**Elements**:
- **Block**: Purple(c) + Maroon(9), 5x5, the thing you control
- **Cross marker**: The 1/. pattern at rows 31-33 — fixed trigger point
- **Upper display**: Bordered box at rows 8-16 — shows TARGET pattern
- **Lower-left display**: Box at rows 53-62 — shows CURRENT pattern (rotates)
- **Progress bar**: Bottom-right area — TIMER that depletes 1 col per action
- **Teal rings**: Time pickups that extend the progress bar by ~11 cols
- **Cyan indicators**: Lives — losing timer = lose a life

**Win condition (confirmed)**:
1. Navigate block to cross marker and overlap it
2. Each overlap rotates the lower-left pattern 90° CW
3. Rotate until lower-left matches upper display target
4. When matched, display borders turn BLACK (passable)
5. Navigate block INTO the upper display through black borders
6. Entering display interior = level completion (1000+ cells change)

**Level 1 procedure** (~16 actions):
- Block starts rows 45-49, cross at rows 31-33 cols 20-22
- Route: 4 UP + 4 LEFT → reach cross area
- 1 DOWN onto cross → rotation (1 needed for L1)
- 1 UP off cross
- Navigate RIGHT and UP to upper display at rows 8-16
- Enter through black borders → level complete

**Level 2 notes**:
- Larger maze with internal walls, 3 rotations needed
- Teal ring pickups available for timer extension
- Border toggle rule may differ per level but ALWAYS black when matched

## VC33: Click Puzzle (UNSOLVED)

**Actions**: [6] = click only
- Clicking bb in purple band progresses header bar
- Can GAME_OVER from wrong clicks
- Need to understand actual win condition
- **TODO**: Try clicking in specific order, track header bar progress

## FT09: Tile Puzzle (UNSOLVED)

**Actions**: [1,2,3,4,5,6] = all available
- Grid of colored tiles (yellow=9, blue=8) on both sides
- Dotted patterns may be rotatable/swappable
- Can GAME_OVER from bad moves
- **TODO**: Classify tile interaction type, try ACTION5 with different positions

## Cross-Game Patterns

- **Wall hit**: 0-2 cells changed (vs normal ~52 for 5x5 block)
- **Level transition**: 1000+ cells changed
- **Progress bars**: Usually timers (depleting = bad), not goals
- **Color 0 (black)**: Often passable borders or empty space
- **Loop detection**: If repeating same 2-4 actions, STOP and rethink
