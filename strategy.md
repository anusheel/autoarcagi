# ARC-AGI-3 Game Strategy

This is the mutable strategy file. **This is what gets iterated on during the research loop.**
Read this before playing any game. Update it with learnings after each evaluation round.

## General Approach

1. **Observe first**: Look at the initial frame carefully. Note the grid dimensions,
   colors used, and any patterns (symmetry, clusters, borders, moving objects).

2. **Explore systematically**: Try each available action once to understand what it does.
   Watch what changes in the frame after each action.

3. **Build a mental model**: After a few actions, hypothesize what the game rules are.
   Common game types: maze navigation, pattern matching, sorting, painting, pushing objects.

4. **Act on your model**: Once you understand the rules, take purposeful actions
   toward the win condition.

5. **Use undo (ACTION7)**: If an action makes things worse, undo it immediately.

## Action Reference

- ACTION1: Usually up / primary action
- ACTION2: Usually down / secondary action
- ACTION3: Usually left
- ACTION4: Usually right
- ACTION5: Select / interact / rotate
- ACTION6: Click at coordinates (x, y) in range 0-63
- ACTION7: Undo last action

## Frame Reading

- `.` (0) = black/empty background
- `1-f` = colors (hex digits, 1-15)
- Grid is up to 64x64
- Rows shown as `YY|cells...` (only non-empty rows displayed)

## Learnings

(empty — will be filled as games are played and patterns discovered)
