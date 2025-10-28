# ai_modules/eval_fn.py
# Evaluation combining positional weights, mobility, parity, and stability

from .stability import stability_score
from .util import BOARD_WEIGHTS, opponent

def positional_score(board, color, board_name='board4'):
    # Lấy trọng số tương ứng board hiện tại
    weights = BOARD_WEIGHTS.get(
        board_name,
        BOARD_WEIGHTS.get(getattr(
            board, 'board_id',
            'default'
        ), BOARD_WEIGHTS['default'])
    )
    s = 0
    for y in range(8):
        for x in range(8):
            c = board.grid[y][x]
            if c == color:
                s += weights[y][x]
            elif c == opponent(color):
                s -= weights[y][x]
    return s

def mobility_score(board, color):
    my_moves = len(board.legal_moves(color))
    opp_moves = len(board.legal_moves(opponent(color)))
    if my_moves + opp_moves == 0:
        return 0
    return 100 * (my_moves - opp_moves) // (my_moves + opp_moves)

def parity_score(board, color):
    black, white = board.count()
    return black - white if color == 'black' else white - black

def evaluate(board, color, board_name='board4'):
    # composite evaluation, tuned for phases by weighting components
    black, white = board.count()
    total = black + white
    phase = 'early' if total <= 20 else 'mid' if total <= 50 else 'end'

    pos = positional_score(board, color, board_name)
    mob = mobility_score(board, color)
    par = parity_score(board, color)
    stab = stability_score(board, color)

    if phase == 'early':
        return pos * 2 + mob * 10 + par * 1 + stab * 5
    elif phase == 'mid':
        return pos * 2 + mob * 12 + par * 2 + stab * 10
    else:
        # endgame: parity (disc count) is dominant
        return par * 100 + pos * 1 + mob * 5 + stab * 50