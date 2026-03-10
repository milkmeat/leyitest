"""坐标编码/解码工具

游戏后台使用单个整数表示坐标: pos = x * 100_000_000 + y * 100
"""

POS_X_FACTOR = 100_000_000
POS_Y_FACTOR = 100


def encode_pos(x: int, y: int) -> int:
    """坐标 (x, y) → 后台 pos 整数"""
    return x * POS_X_FACTOR + y * POS_Y_FACTOR


def decode_pos(pos: int) -> tuple[int, int]:
    """后台 pos 整数 → (x, y)"""
    x = pos // POS_X_FACTOR
    y = (pos % POS_X_FACTOR) // POS_Y_FACTOR
    return x, y
