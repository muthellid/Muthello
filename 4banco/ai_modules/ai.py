from .board import GridBoard
from .level import depth_for_phase, game_phase_from_board
from .search import Searcher
from .util import weights_for_board
from typing import Optional

# ánh xạ chiến lược tương ứng với từng bàn
strategy_map = {
    'board1': 'aggressive',
    'board2': 'defensive',
    'board3': 'corner_focus',
    'board4': 'balanced'
}

def get_strategy_for_board(board_name: str) -> str:
    """Trả về strategy tương ứng với board_name"""
    return strategy_map.get(board_name, 'balanced')


def get_best_move_from_grid(
    js_grid,
    ai_color,
    requested_depth: int = 4,
    board_name: str = 'board4',
    time_limit: Optional[float] = None
):
    """Hàm trung tâm — dùng trong Flask để lấy nước đi tốt nhất từ JS grid."""

    # 1️⃣ Tạo board thật với board_id
    board = GridBoard(js_grid, board_id=board_name)

    # 2️⃣ Lấy chiến lược phù hợp với bàn
    strategy = get_strategy_for_board(board_name)
    board.strategy = strategy  # gán strategy trực tiếp vào board_obj

    # 3️⃣ Gán trọng số chiến lược vào board luôn (để Searcher chỉ việc dùng)
    board.weights = weights_for_board(board, strategy)

    # 4️⃣ Xác định giai đoạn và độ sâu tối đa
    phase = game_phase_from_board(board)
    max_depth = depth_for_phase(requested_depth, phase)

    # 5️⃣ Tạo Searcher và gán đầy đủ thông tin
    searcher = Searcher(time_limit=time_limit)
    searcher.board_name = board_name
    searcher.board_obj = board  # truyền board thật (đã có weights + strategy)
    searcher.strategy = strategy

    # 6️⃣ Chạy tìm nước đi
    res = searcher.iterative_deepening(board, ai_color, max_depth, time_limit)
    if not res:
        return None

    move_dict = res.get("move")
    if not move_dict:
        return None

    # 7️⃣ Trả về move ở dạng list (để frontend JS dễ đọc)
    return list(move_dict) if isinstance(move_dict, tuple) else move_dict