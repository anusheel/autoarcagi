# ARC-AGI-3 Game Strategy

Accumulated knowledge from playing. Updated after each session.

## LS20

### The Board
- You control a block that slides through corridors.
- The block moves exactly one block-width per step in 4 directions (U/D/L/R).
- Corridors are walkable. Walls stop the block. Hitting a wall still costs a move.
- Each level has a different maze layout — corridors, walls, and object positions change.

### Objects
- **Block**: the piece you move. It has a specific shape and color.
- **Shape key (cross marker)**: passing through it rotates the target shape 90° CW. Each pass = 1 rotation.
- **Color key**: passing through it cycles the target color. Different levels may need different numbers of passes.
- **Target display**: shows the shape+color you need to match. Position varies per level.
- **Working display (bottom-left)**: shows your current shape+color at 2x scale. This is what you're transforming.
- **Fuel bar (bottom)**: 42 moves per round, 3 lives total. Running out of moves resets the round.

### Win Condition
- The working display must match the target display in BOTH shape AND color.
- Shape is controlled by the shape key (cross). Color is controlled by the color key.
- Once matched, enter the target display to complete the level.
- The number of key passes needed varies per level — compare the displays to figure it out.

### What Matters
- Shape and color are INDEPENDENT — you may need to visit both keys.
- Cell values represent colors. Different values (9, c, e, 8...) are different colors. Don't treat them as interchangeable.
- Every level has the same core mechanic but with different maze layouts, key positions, and rotation/color counts.
- 7 levels total. Budget is tight — find efficient paths.

### Open Questions
- L3+: target display may be physically unreachable. How does completion work in that case?
- Do bbb markers serve a purpose beyond being obstacles?
- Can any state persist across round resets?
