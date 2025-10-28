# ai_modules/stability.py
from typing import List
from .common import in_bounds

BOARD_ANCHORS = {
    "board1": [(0, 0), (0, 7), (7, 0), (7, 7)],
    "board2": [(0, 2), (0, 5), (2, 0), (2, 7), (5, 0), (5, 7), (7, 2), (7, 5)],
    "board3": [(0, 0), (0, 7), (7, 0), (7, 7)],
    "board4": [(0, 2), (0, 5), (2, 0), (2, 7), (5, 0), (5, 7), (7, 2)],
    "default": []
}

DIRECTIONS = [
    (1, 0), (-1, 0),
    (0, 1), (0, -1),
    (1, 1), (1, -1),
    (-1, 1), (-1, -1)
]

def _cell(board, y, x):
    if 0 <= y < 8 and 0 <= x < 8:
        return board.grid[y][x]
    return None

def compute_stable_map(board) -> List[List[bool]]:
    b_id = getattr(board, "board_id", "default")
    anchors = BOARD_ANCHORS.get(b_id, BOARD_ANCHORS["default"])
    stable = [[False] * 8 for _ in range(8)]

    for (ay, ax) in anchors:
        val = _cell(board, ay, ax)
        if val in ("black", "white"):
            stable[ay][ax] = True

    changed = True
    while changed:
        changed = False
        for y in range(8):
            for x in range(8):
                c = _cell(board, y, x)
                if c not in ("black", "white") or stable[y][x]:
                    continue

                all_dirs_safe = True
                for dy, dx in DIRECTIONS:
                    ny, nx = y + dy, x + dx
                    dir_safe = False
                    while in_bounds(nx, ny):
                        q = _cell(board, ny, nx)
                        if q == "blocked":
                            dir_safe = True
                            break
                        if q is None:
                            dir_safe = False
                            break
                        if q == c and stable[ny][nx]:
                            dir_safe = True
                            break
                        ny += dy
                        nx += dx
                    else:
                        dir_safe = True

                    if not dir_safe:
                        all_dirs_safe = False
                        break

                if all_dirs_safe:
                    stable[y][x] = True
                    changed = True
    return stable

def stability_score(board, color: str) -> int:
    stable_map = compute_stable_map(board)
    my, opp = 0, 0
    for y in range(8):
        for x in range(8):
            if not stable_map[y][x]:
                continue
            c = _cell(board, y, x)
            if c == color:
                my += 1
            elif c == ("white" if color == "black" else "black"):
                opp += 1
    return my - opp