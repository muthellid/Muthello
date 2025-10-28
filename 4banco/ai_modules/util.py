# ai_modules/util.py
# utilities: weights, coordinate helpers
from typing import Optional, List, Tuple
from contextlib import suppress
from .mobility import mobility_score
from .stability import stability_score
from .common import in_bounds, opponent  # tránh vòng import

SIZE = 8

# --- Board 1: Rìa trên/dưới + trái/phải bị blocked ---
BOARD1_WEIGHTS = [
    [-1000, -1000, 100, 5, 5, 100, -1000, -1000],
    [-1000, -1000, -5, -5, -5, -5, -1000, -1000],
    [100, -5, 15, 3, 3, 15, -5, 100],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [100, -5, 15, 3, 3, 15, -5, 100],
    [-1000, -1000, -5, -5, -5, -5, -1000, -1000],
    [-1000, -1000, 100, 5, 5, 100, -1000, -1000],
]

# --- Board 2: 4 blocked ở giữa rìa (B2,G2,B7,G7) ---
BOARD2_WEIGHTS = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -1000, -5, -5, -5, -5, -1000, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 3, 15, -5, 20],
    [-20, -1000, -5, -5, -5, -5, -1000, -20],
    [120, -20, 20, 5, 5, 20, -20, 120],
]

# --- Board 3: Blocked ở viền dọc và ngang (A1,A2,A7,A8,B1,B8,G1,G8,H1,H2,H7,H8) ---
BOARD3_WEIGHTS = [
    [-1000, -1000, 100, 5, 5, 100, -1000, -1000],
    [-1000, 15, -5, -5, -5, -5, 15, -1000],
    [100, -5, 15, 3, 3, 15, -5, 100],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [100, -5, 15, 3, 3, 15, -5, 100],
    [-1000, 15, -5, -5, -5, -5, -15, -1000],
    [-1000, -1000, 100, 5, 5, 100, -1000, -1000],
]

# --- Board 4: Không blocked (classic) ---
BOARD4_WEIGHTS = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120],
]

# Map để eval_fn gọi nhanh
BOARD_WEIGHTS = {
    'board1': BOARD1_WEIGHTS,
    'board2': BOARD2_WEIGHTS,
    'board3': BOARD3_WEIGHTS,
    'board4': BOARD4_WEIGHTS,
    'default': BOARD4_WEIGHTS
}

# --- Strategy mapping ---
STRATEGY_MAP = {
    'aggressive': 'board1',
    'defensive': 'board2',
    'corner_focus': 'board3',
    'balanced': 'board4'
}

def weights_for_board(board=None, strategy: Optional[str] = None):
    if strategy:
        bid = STRATEGY_MAP.get(strategy, 'default')
    else:
        bid = getattr(board, "board_id", None) or 'default'
    return BOARD_WEIGHTS.get(bid, BOARD_WEIGHTS['default'])


# --- New: convert grid -> bitboards ---
def grid_to_bitboards(grid: List[List[Optional[str]]]) -> Tuple[int, int, int]:
    bb_b = bb_w = bb_blk = 0
    for y in range(SIZE):
        for x in range(SIZE):
            v = grid[y][x]
            idx = y * SIZE + x
            if v == "black":
                bb_b |= 1 << idx
            elif v == "white":
                bb_w |= 1 << idx
            elif v == "blocked":
                bb_blk |= 1 << idx
    return bb_b, bb_w, bb_blk


# --- New: main evaluation ---
def evaluate_grid(
    grid: List[List[Optional[str]]],
    color: str,
    board_obj=None
) -> float:
    weights = weights_for_board(board_obj)
    pos = 0
    for y in range(SIZE):
        for x in range(SIZE):
            c = grid[y][x]
            if c == color:
                pos += weights[y][x]
            elif c == opponent(color):
                pos -= weights[y][x]

    mob = mobility_score(grid, color)
    stab = 0
    with suppress(Exception):
        stab = stability_score(grid, color)

    black = sum(1 for r in grid for c in r if c == "black")
    white = sum(1 for r in grid for c in r if c == "white")
    par = (black - white) if color == "black" else (white - black)

    total = black + white
    if total <= 20:
        phase = "early"
    elif total <= 50:
        phase = "mid"
    else:
        phase = "end"

    if phase == "early":
        return pos * 2 + mob * 10 + par * 1 + stab * 5
    if phase == "mid":
        return pos * 2 + mob * 12 + par * 2 + stab * 10
    return par * 100 + pos * 1 + mob * 5 + stab * 50