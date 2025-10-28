from __future__ import annotations

import math
import time
from typing import Dict, Optional, Tuple
from contextlib import suppress

from .stability import stability_score
from .mobility import mobility_score
from .legal_move import apply_move_on_grid, legal_moves_from_grid, opponent
from .util import BOARD_WEIGHTS, STRATEGY_MAP, weights_for_board, evaluate_grid, grid_to_bitboards

SIZE = 8


TTEntry = Tuple[int, float, Optional[Tuple[int, int]]]


class Searcher:
    def __init__(
        self,
        time_limit: Optional[float] = None,
        board_name: Optional[str] = None,
        strategy: Optional[str] = None
    ):
        self.tt: Dict[Tuple[int, int, int, str], TTEntry] = {}
        self.nodes = 0
        self.time_limit = time_limit
        self.start_time: Optional[float] = None
        self.board_name = board_name or "default"
        self.strategy = strategy
        self.killer = {}
        self.history = {}
        self.board_obj: Optional[object] = None

    def time_exceeded(self) -> bool:
        if self.time_limit is None or self.start_time is None:
            return False
        return (time.time() - self.start_time) > self.time_limit

    def key_from_bitboards(self, bb_b: int, bb_w: int, bb_blk: int, color: str):
        return bb_b, bb_w, bb_blk, color

    def build_from_boardobj(self, board_obj):
        grid = getattr(board_obj, "grid", board_obj)
        bb_b, bb_w, bb_blk = grid_to_bitboards(grid)
        return grid, bb_b, bb_w, bb_blk

    def move_score_egaroucid(self, grid, move, color):
        corners = {(0, 0), (0, 7), (7, 0), (7, 7)}
        x, y = move["x"], move["y"]
        score = 0
        if (x, y) in corners:
            score += 1000

        weights = weights_for_board(getattr(self, "board_obj", None), self.strategy)
        score += len(move["flips"]) * 5

        newg = apply_move_on_grid(grid, move, color)
        score += len(legal_moves_from_grid(newg, color)) * 3

        with suppress(Exception):
            score += stability_score(newg, color) * 10

        return score

    def negamax(
        self,
        grid,
        color: str,
        depth: int,
        alpha: float,
        beta: float
    ) -> Tuple[float, Optional[Tuple[int, int]]]:
        if self.time_exceeded():
            raise TimeoutError()
        self.nodes += 1

        bb_b, bb_w, bb_blk = grid_to_bitboards(grid)
        key = self.key_from_bitboards(bb_b, bb_w, bb_blk, color)

        tt = self.tt.get(key)
        if tt and tt[0] >= depth:
            return tt[1], tt[2]

        moves = legal_moves_from_grid(grid, color)
        if depth == 0 or not moves:
            v = evaluate_grid(grid, color, getattr(self, "board_obj", None))
            self.tt[key] = (depth, v, None)
            return v, None

        moves.sort(
            key=lambda m: self.move_score_egaroucid(grid, m, color),
            reverse=True
        )

        best_val = -math.inf
        best_move_xy: Optional[Tuple[int, int]] = None

        for m in moves:
            if not m.get("flips"):
                continue

            newg = apply_move_on_grid(grid, m, color)
            val, _ = self.negamax(newg, opponent(color), depth - 1, -beta, -alpha)
            val = -val

            if val > best_val:
                best_val = val
                best_move_xy = (m["x"], m["y"])

            alpha = max(alpha, val)
            if alpha >= beta:
                break

        self.tt[key] = (depth, best_val, best_move_xy)
        return best_val, best_move_xy

    def iterative_deepening(
        self,
        board_obj,
        color: str,
        max_depth: int,
        time_limit: Optional[float] = None
    ) -> Optional[dict]:
        if time_limit is not None:
            self.time_limit = time_limit
        self.start_time = time.time()
        self.board_obj = board_obj

        # đảm bảo board có weights phù hợp
        if not hasattr(board_obj, "weights"):
            board_obj.weights = weights_for_board(board_obj, self.strategy)

        grid, bb_b, bb_w, bb_blk = self.build_from_boardobj(board_obj)
        best: Optional[dict] = None

        try:
            for d in range(1, max_depth + 1):
                val, mv = self.negamax(grid, color, d, -math.inf, math.inf)
                if mv is not None:
                    best = {"move": mv, "value": val, "depth": d}
                if self.time_exceeded():
                    break
        except TimeoutError:
            pass

        return best