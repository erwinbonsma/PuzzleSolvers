# StickPuzzleSolver

This is a simple solver for angled stick puzzles. In particular, it has been written to solve Stewart Coffin's
"Too Hard" puzzle. The easier "Pineapple Pile" puzzle also designed by him was used to test the solver.

The difficulty with solving these puzzles (both manually as well as computer-assisted) is that the sticks do not
intersect the rods at an orthogonal angle. This results in a distorted coordinate system where pieces cannot be
rotated as freely as would otherwise be possible. Also, when attempting a manual solve, it adds a lot of
confusion.

An additional difficulty is that the assembled shape is not known. It is only known that in the assembled state,
all holes in the rod should be filled with sticks.

The solver only checks how the puzzle pieces can fit together. It does not actually check if the solutions it
generates can actually be assembled.
