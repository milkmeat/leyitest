"""tests/test_find_empty_spot.py — _find_empty_spot 空位搜索算法单元测试"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_executor():
    """构造一个最小化的 L0Executor 实例用于测试 _find_empty_spot"""
    from src.executor.l0_executor import L0Executor

    executor = object.__new__(L0Executor)
    executor.map_width = 200
    executor.map_height = 200
    executor.client = MagicMock()
    executor.client.default_header = {"lvl_id": 40001}
    executor.client.lvl_get_map_area = AsyncMock(return_value=[])
    return executor


class TestFindEmptySpotSteamFactory:
    """steam factory 附近移城空位搜索"""

    def test_steam_factory_rect_bounds(self):
        """_STEAM_FACTORY_RECT 应为 (139,155,144,160) inclusive"""
        from src.executor.l0_executor import L0Executor
        assert L0Executor._STEAM_FACTORY_RECT == (139, 155, 144, 160)

    def test_blocked_point_inside_factory(self):
        """(139,159) 在 steam factory 占地内，应被判定为 blocked"""
        executor = _make_executor()
        rect = executor._STEAM_FACTORY_RECT
        bx1, by1, bx2, by2 = rect
        # (139, 159) 应在矩形内
        x, y = 139, 159
        assert bx1 <= x <= bx2 and by1 <= y <= by2

    @pytest.mark.parametrize("x,y", [
        (138, 159),
        (141, 161),
        (145, 159),
        (142, 153),
    ])
    def test_free_points_outside_factory(self, x, y):
        """用户确认的空闲坐标不在 steam factory 占地内"""
        executor = _make_executor()
        bx1, by1, bx2, by2 = executor._STEAM_FACTORY_RECT
        inside = bx1 <= x <= bx2 and by1 <= y <= by2
        assert not inside, f"({x},{y}) should be outside factory rect"

    def test_factory_always_injected_when_map_empty(self):
        """地图查询返回空结果时，steam factory 仍被注入 occupied"""
        executor = _make_executor()
        executor.client.lvl_get_map_area = AsyncMock(return_value=[])

        result = asyncio.run(executor._find_empty_spot(20010643, 139, 155))
        # 不应返回 (139, 155)（建筑中心，在占地内）
        bx1, by1, bx2, by2 = executor._STEAM_FACTORY_RECT
        rx, ry = result
        inside = bx1 <= rx <= bx2 and by1 <= ry <= by2
        assert not inside, (
            f"返回坐标 ({rx},{ry}) 在 steam factory 占地内，应选择外部空位"
        )

    def test_factory_injected_not_duplicated(self):
        """地图查询已返回 steam factory 时不重复注入"""
        executor = _make_executor()
        factory_obj = {
            "objs": [{
                "objBasic": {
                    "type": 10103,
                    "key": 10103,
                    "pos": 139 * 100_000_000 + 155 * 100,
                }
            }]
        }
        executor.client.lvl_get_map_area = AsyncMock(return_value=[factory_obj])

        result = asyncio.run(executor._find_empty_spot(20010643, 139, 155))
        rx, ry = result
        bx1, by1, bx2, by2 = executor._STEAM_FACTORY_RECT
        inside = bx1 <= rx <= bx2 and by1 <= ry <= by2
        assert not inside

    def test_selected_spot_is_nearest_free(self):
        """从 (139,155) 搜索，返回的空位应是最近的非占地点"""
        executor = _make_executor()
        executor.client.lvl_get_map_area = AsyncMock(return_value=[])

        rx, ry = asyncio.run(executor._find_empty_spot(20010643, 139, 155))
        # 结果应在 factory 外
        bx1, by1, bx2, by2 = executor._STEAM_FACTORY_RECT
        assert not (bx1 <= rx <= bx2 and by1 <= ry <= by2)
        # 距离应较近（切比雪夫距离 <= 5）
        dist = max(abs(rx - 139), abs(ry - 155))
        assert dist <= 5, f"空位 ({rx},{ry}) 距离目标过远: {dist}"

    def test_original_failure_case_139_159_blocked(self):
        """复现原始 bug：(139,159) 不应被选为空位"""
        executor = _make_executor()
        executor.client.lvl_get_map_area = AsyncMock(return_value=[])

        rx, ry = asyncio.run(executor._find_empty_spot(20010643, 139, 155))
        assert (rx, ry) != (139, 159), (
            "算法不应选择 (139,159)，该坐标在 steam factory 占地内"
        )


class TestFindEmptySpotOtherBuildings:
    """其他建筑类型的碰撞检测"""

    def test_player_city_blocks_point(self):
        """玩家主城 5×5 占地应阻挡其内部的点"""
        executor = _make_executor()
        # 模拟一个玩家主城在 (150, 150)，占地 (150,150)-(154,154)
        city_obj = {
            "objs": [{
                "objBasic": {
                    "type": 10101,
                    "key": 0,
                    "pos": 150 * 100_000_000 + 150 * 100,
                }
            }]
        }
        executor.client.lvl_get_map_area = AsyncMock(return_value=[city_obj])

        # 搜索 (152, 152) — 在主城中心
        rx, ry = asyncio.run(executor._find_empty_spot(20010643, 152, 152))
        # 不应返回主城内部的点
        assert not (150 <= rx <= 154 and 150 <= ry <= 154), (
            f"({rx},{ry}) 在主城占地 (150,150)-(154,154) 内"
        )

    def test_map_query_failure_returns_target(self):
        """地图查询异常时回退到原始坐标"""
        executor = _make_executor()
        executor.client.lvl_get_map_area = AsyncMock(
            side_effect=Exception("network error")
        )

        rx, ry = asyncio.run(executor._find_empty_spot(20010643, 100, 100))
        assert (rx, ry) == (100, 100)
