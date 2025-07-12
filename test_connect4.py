import pytest

from connect4 import H1, MCTS, Board, Negamax, has_won


def board(*cols):
    b = Board()
    for c in cols:
        b.play(c)
    return b


def test_horizontal():
    b = board(0, 0, 1, 1, 2, 2, 3)
    assert b.last_won()


def test_vertical():
    b = board(4, 5, 4, 5, 4, 5, 4)
    assert b.last_won()


def test_diagonals():
    # X climbs 0..3 going up-right
    assert board(0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3).last_won()
    # mirrored: X climbs 6..3 going up-left
    assert board(6, 5, 5, 4, 4, 3, 4, 3, 3, 0, 3).last_won()


def bits(*cells):
    return sum(1 << (c * H1 + r) for c, r in cells)


def test_no_wraparound():
    # top three of column 0 + bottom of column 1 would be contiguous without the sentinel row
    assert not has_won(bits((0, 3), (0, 4), (0, 5), (1, 0)))
    assert not has_won(bits((0, 3), (1, 4), (2, 5), (4, 0)))  # diagonal over the top
    assert has_won(bits((0, 2), (0, 3), (0, 4), (0, 5)))
    assert not board(0, 1, 2, 4, 5, 6).last_won()


@pytest.mark.parametrize("ai", [Negamax(6), MCTS(2000, seed=1)], ids=["negamax", "mcts"])
def test_takes_immediate_win(ai):
    b = board(0, 0, 1, 1, 2, 6)  # X to move, 3 wins
    assert ai.choose(b) == 3


@pytest.mark.parametrize("ai", [Negamax(6), MCTS(2000, seed=1)], ids=["negamax", "mcts"])
def test_blocks_immediate_loss(ai):
    b = board(0, 6, 1, 6, 2)  # O to move, X threatens 3
    assert ai.choose(b) == 3
