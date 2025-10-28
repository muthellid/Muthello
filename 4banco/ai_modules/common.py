# ai_modules/common.py
# các hàm cơ bản dùng chung để tránh vòng import

SIZE = 8

def in_bounds(x: int, y: int) -> bool:
    """Kiểm tra tọa độ có nằm trong phạm vi bàn 8x8 hay không."""
    return 0 <= x < SIZE and 0 <= y < SIZE

def opponent(color: str) -> str:
    """Trả về màu đối thủ."""
    return "white" if color == "black" else "black"