from typing import List, Optional
from .legal_move import legal_moves_from_grid, opponent


def mobility_score(grid: List[List[Optional[str]]], color: str) -> int:
    """
    Tính mobility (số nước đi hợp lệ) của người chơi color so với đối thủ.
    Trả về giá trị từ -100 đến 100.
    """
    my_moves = len(legal_moves_from_grid(grid, color))
    opp_moves = len(legal_moves_from_grid(grid, opponent(color)))

    total = my_moves + opp_moves
    if total == 0:
        return 0

    return 100 * (my_moves - opp_moves) // total