from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Union, cast
from copy import deepcopy

SIZE = 8
DIRECTIONS: List[Tuple[int, int]] = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),          (0, 1),
    (1, -1),  (1, 0), (1, 1),
]


def inside(x: int, y: int) -> bool:
    """Kiểm tra (x, y) có nằm trong bàn cờ không."""
    return 0 <= x < SIZE and 0 <= y < SIZE


def opponent(color: str) -> str:
    """Trả về đối thủ."""
    return "white" if color == "black" else "black"


def legal_moves_from_grid(
    grid: List[List[Optional[str]]],
    color: str
) -> List[Dict[str, Union[int, List[Tuple[int, int]]]]]:
    """Tìm tất cả các nước đi hợp lệ và các quân sẽ bị lật."""
    moves: List[Dict[str, Union[int, List[Tuple[int, int]]]]] = []
    opp = opponent(color)

    for y in range(SIZE):
        for x in range(SIZE):
            if grid[y][x] is not None:
                continue

            flips: List[Tuple[int, int]] = []

            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                path: List[Tuple[int, int]] = []

                while inside(nx, ny) and grid[ny][nx] == opp:
                    path.append((nx, ny))
                    nx += dx
                    ny += dy

                if inside(nx, ny) and grid[ny][nx] == color and path:
                    flips.extend(path)

            if flips:
                moves.append({"x": x, "y": y, "flips": flips})

    return moves


def apply_move_on_grid(
    grid: List[List[Optional[str]]],
    move: Union[Dict[str, Union[int, List[Tuple[int, int]]]], Tuple[int, int]],
    color: str
) -> List[List[Optional[str]]]:
    """Áp dụng nước đi lên grid, hỗ trợ cả dạng dict và tuple."""
    newg = deepcopy(grid)

    if isinstance(move, dict):
        # Dùng cast để Pyright hiểu chắc chắn là int và List[Tuple[int, int]]
        x = cast(int, move["x"])
        y = cast(int, move["y"])
        flips = cast(List[Tuple[int, int]], move.get("flips", []))
    else:
        x, y = move
        flips: List[Tuple[int, int]] = []

    newg[y][x] = color

    for fx, fy in flips:
        newg[fy][fx] = color

    return newg