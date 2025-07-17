# connect-four-ai

Connect Four on a bitboard with two computer players: a negamax search (alpha-beta, center-first move ordering, iterative deepening, transposition table) and a UCT Monte Carlo Tree Search. Pure standard library.

The board is two 64-bit ints, one per player, in the usual 7x6 column-major layout with an empty sentinel row on top of each column. The sentinel is what keeps the shift-and-AND win check from wrapping between columns.

## Setup

Python 3.10+ (for `int.bit_count`). The game itself only uses the standard library, so there's no requirements.txt; the tests need `pip install pytest`.

## Run

Play against the AI (columns are numbered 1-7):

```
python connect4.py play --first              # you move first, negamax depth 8
python connect4.py play --ai mcts --iters 5000
```

Self-play tournament, each negamax depth against MCTS, alternating who moves first:

```
python connect4.py tournament                 # depths 2 4 6 8 vs mcts-2000, 20 games each
```

My run of the default tournament (about 3 minutes):

```
  negamax-d2 vs mcts-2000  | negamax-d2   50%  mcts-2000   50%  draw    0%
  negamax-d4 vs mcts-2000  | negamax-d4   35%  mcts-2000   60%  draw    5%
  negamax-d6 vs mcts-2000  | negamax-d6   55%  mcts-2000   40%  draw    5%
  negamax-d8 vs mcts-2000  | negamax-d8   80%  mcts-2000   20%  draw    0%
```

With 2000 rollouts per move, MCTS plays roughly as well as a 4-6 ply search with a crude threat-counting eval. Depth 8 beats it most of the time.

## Test

```
python -m pytest -q
```

The tests cover horizontal, vertical, and both diagonal wins, check that no win wraps across a column boundary, and check that both AIs take an immediate win and block an immediate loss.
