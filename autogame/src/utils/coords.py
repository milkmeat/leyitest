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


# ------------------------------------------------------------------
# AVA 战场地块 (bid) 编码
# ------------------------------------------------------------------

def pos_to_bid(x: int, y: int) -> int:
    """坐标 (x, y) → 地块 bid (block ID)

    bid 编码: bid = (x//10 + 1) * 1000 + (y//10 + 1)
    每个 bid 覆盖 10x10 像素区域。
    """
    return (x // 10 + 1) * 1000 + (y // 10 + 1)


def make_bid_list(center_x: int, center_y: int, size: int = 10) -> list[int]:
    """生成以 (center_x, center_y) 为中心、size*size 范围的 bid 列表

    Args:
        center_x, center_y: 中心像素坐标
        size: 边长（以地块为单位，默认 10 = 10x10 = 100 个地块）

    Returns:
        bid 整数列表
    """
    center_bx = center_x // 10 + 1
    center_by = center_y // 10 + 1
    half = size // 2
    return [
        bx * 1000 + by
        for bx in range(center_bx - half, center_bx - half + size)
        for by in range(center_by - half, center_by - half + size)
    ]
