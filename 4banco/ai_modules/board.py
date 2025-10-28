from copy import deepcopy
from typing import Literal, Optional

Cell = Optional[Literal["black", "white", "blocked"]]
Move = dict[str, object]
Grid = list[list[Cell]]

SIZE = 8

BOARD_BLOCKS = {
    "board1": [
        "A1","A2","A7","A8","B1","B2","B7","B8",
        "G1","G2","G7","G8","H1","H2","H7","H8"
    ],
    "board2": ["B2","G2","B7","G7"],
    "board3": [
        "A1","A2","A7","A8","B1","B8",
        "G1","G8","H1","H2","H7","H8"
    ],
    "board4": [],
    "default": []
}

def pos_to_xy(pos: str) -> tuple[int, int]:
    col = ord(pos[0].upper()) - ord("A")
    row = int(pos[1]) - 1
    return col, row


class GridBoard:
    grid: Grid
    board_id: str
    strategy: Optional[dict]
    weights: Optional[list]

    def __init__(self, grid: Optional[Grid] = None, board_id: str = "board1"):
        self.board_id = board_id
        self.strategy = None
        self.weights = None

        if grid is None:
            self.grid = [[None] * SIZE for _ in range(SIZE)]
            for pos in BOARD_BLOCKS.get(board_id, []):
                x, y = pos_to_xy(pos)
                self.grid[y][x] = "blocked"

            if self.grid[3][3] != "blocked":
                self.grid[3][3] = "white"
            if self.grid[4][4] != "blocked":
                self.grid[4][4] = "white"
            if self.grid[3][4] != "blocked":
                self.grid[3][4] = "black"
            if self.grid[4][3] != "blocked":
                self.grid[4][3] = "black"
        else:
            self.grid = deepcopy(grid)

    def clone(self) -> "GridBoard":
        return GridBoard(self.grid, self.board_id)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < SIZE and 0 <= y < SIZE

    def count(self) -> tuple[int, int]:
        white = sum(1 for row in self.grid for c in row if c == "white")
        black = sum(1 for row in self.grid for c in row if c == "black")
        return black, white

    def is_full(self) -> bool:
        return all(c is not None for row in self.grid for c in row)

    def to_js_grid(self) -> Grid:
        return deepcopy(self.grid)

    def apply_move(
        self,
        x: int,
        y: int,
        color: Literal["black", "white"],
        flips: list[tuple[int, int]]
    ) -> None:
        self.grid[y][x] = color
        for fx, fy in flips:
            self.grid[fy][fx] = color

    def legal_moves(self, color: Literal["black", "white"]) -> list[Move]:
        DIRECTIONS = [
            (1, 0), (-1, 0),
            (0, 1), (0, -1),
            (1, 1), (1, -1),
            (-1, 1), (-1, -1)
        ]
        moves: list[Move] = []
        for y in range(SIZE):
            for x in range(SIZE):
                if self.grid[y][x] is not None:
                    continue
                flips: list[tuple[int, int]] = []
                for dy, dx in DIRECTIONS:
                    ny, nx = y + dy, x + dx
                    temp: list[tuple[int, int]] = []
                    while self.in_bounds(nx, ny):
                        p = self.grid[ny][nx]
                        if p is None or p == "blocked":
                            break
                        if p == color:
                            if temp:
                                flips.extend(temp)
                            break
                        temp.append((nx, ny))
                        nx += dx
                        ny += dy
                if flips:
                    moves.append({"x": x, "y": y, "flips": flips})
        return moves