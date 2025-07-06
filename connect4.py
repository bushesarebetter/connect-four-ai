import argparse
import math
import random
import time

# Bit layout, column-major with a sentinel row on top of each column:
#   6 13 20 27 34 41 48   <- sentinel, always 0
#   5 12 19 26 33 40 47
#   ...
#   0  7 14 21 28 35 42
W, H = 7, 6
H1 = H + 1
TOP = sum(1 << (c * H1 + H) for c in range(W))
FULL = ((1 << (W * H1)) - 1) ^ TOP
CENTER = ((1 << H) - 1) << (3 * H1)
ORDER = [3, 2, 4, 1, 5, 0, 6]
WIN = 1000
INF = 10**9
EXACT, LOWER, UPPER = 0, 1, 2


def has_won(b):
    # vertical, horizontal, and both diagonals; the sentinel row stops wraparound
    for s in (1, H1, H1 - 1, H1 + 1):
        m = b & (b >> s)
        if m & (m >> 2 * s):
            return True
    return False


def threats(b):
    """Cells (empty or not) that would complete four-in-a-row for bitboard b."""
    r = (b << 1) & (b << 2) & (b << 3)
    for s in (H1, H1 - 1, H1 + 1):
        p = (b << s) & (b << 2 * s)
        r |= p & (b << 3 * s)
        r |= p & (b >> s)
        p = (b >> s) & (b >> 2 * s)
        r |= p & (b << s)
        r |= p & (b >> 3 * s)
    return r & FULL


class Board:
    def __init__(self):
        self.bb = [0, 0]
        self.height = [c * H1 for c in range(W)]
        self.moves = 0

    def copy(self):
        b = Board.__new__(Board)
        b.bb, b.height, b.moves = self.bb[:], self.height[:], self.moves
        return b

    def can_play(self, c):
        return self.height[c] < c * H1 + H

    def legal(self):
        return [c for c in ORDER if self.can_play(c)]

    def play(self, c):
        self.bb[self.moves & 1] |= 1 << self.height[c]
        self.height[c] += 1
        self.moves += 1

    def undo(self, c):
        self.moves -= 1
        self.height[c] -= 1
        self.bb[self.moves & 1] ^= 1 << self.height[c]

    def last_won(self):
        return self.moves > 0 and has_won(self.bb[(self.moves - 1) & 1])

    def full(self):
        return self.moves == W * H

    def evaluate(self):
        # ponytail: open-threat count + center pieces; a crude heuristic, fine for shallow depths
        me, opp = self.bb[self.moves & 1], self.bb[(self.moves + 1) & 1]
        empty = FULL & ~(me | opp)
        t = (threats(me) & empty).bit_count() - (threats(opp) & empty).bit_count()
        c = (me & CENTER).bit_count() - (opp & CENTER).bit_count()
        return 4 * t + c

    def __str__(self):
        rows = []
        for r in reversed(range(H)):
            row = []
            for c in range(W):
                bit = 1 << (c * H1 + r)
                row.append("X" if self.bb[0] & bit else "O" if self.bb[1] & bit else ".")
            rows.append(" ".join(row))
        return "\n".join(rows) + "\n" + " ".join(str(c + 1) for c in range(W))


class Negamax:
    def __init__(self, depth=8):
        self.depth = depth
        self.name = f"negamax-d{depth}"

    def choose(self, board):
        self.tt = {}
        b = board.copy()
        key = (b.bb[0], b.bb[1])
        move = b.legal()[0]
        for d in range(1, self.depth + 1):  # iterative deepening; shallow results order the deeper search
            score = self.negamax(b, d, -INF, INF)
            move = self.tt[key][3]
            if abs(score) > WIN - 100:  # forced win or loss found, deeper won't change it
                break
        return move

    def negamax(self, b, depth, alpha, beta):
        key = (b.bb[0], b.bb[1])
        alpha0 = alpha
        tt_move = None
        entry = self.tt.get(key)
        if entry:
            e_depth, flag, e_score, tt_move = entry
            if e_depth >= depth:
                if flag == EXACT:
                    return e_score
                if flag == LOWER:
                    alpha = max(alpha, e_score)
                else:
                    beta = min(beta, e_score)
                if alpha >= beta:
                    return e_score
        if b.full():
            return 0
        if depth == 0:
            return b.evaluate()

        moves = b.legal()
        if tt_move is not None:
            moves.remove(tt_move)
            moves.insert(0, tt_move)
        best, best_move = -INF, moves[0]
        for c in moves:
            b.play(c)
            # win score depends only on total move count, so it's safe to store in the TT
            score = WIN - b.moves if b.last_won() else -self.negamax(b, depth - 1, -beta, -alpha)
            b.undo(c)
            if score > best:
                best, best_move = score, c
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        flag = UPPER if best <= alpha0 else LOWER if best >= beta else EXACT
        self.tt[key] = (depth, flag, best, best_move)
        return best












