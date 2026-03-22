"""建筑/据点数据模型

数据来源（test server 实际返回）:
  - get_map_brief_obj → svr_map_brief_objs.briefList
  - 不同 type 含义:
      type=8   联盟要塞 (key=10000 大型, 10100 小型)
      type=27  地图据点/节点 (key=656~676, 不同等级)
      type=48  王座 (地图中心 59700,59700)
      type=64  通道建筑 (key=1302~1317)
      type=121 联盟旗帜 (key=10600)
      type=156 王座周边建筑 (key=2371~2374)
"""

from __future__ import annotations

from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.coords import decode_pos


class MapObjectType(IntEnum):
    """地图对象类型 — 来自 svr_map_brief_objs.objBasic.type"""
    CITY = 2               # 玩家城市
    ALLIANCE_FORT = 8      # 联盟要塞
    NODE = 27              # 地图据点（可占领）
    THRONE = 48            # 王座
    PASSAGE = 64           # 通道建筑
    BARBARIAN = 71         # 野怪
    MARCH = 108            # 行军队列
    ALLIANCE_FLAG = 121    # 联盟旗帜
    THRONE_WING = 156      # 王座侧翼建筑


class Building(BaseModel):
    """地图建筑/据点

    统一表示 type=27 据点、type=48 王座、type=64 通道、type=156 侧翼等
    可被占领的地图对象。联盟要塞(type=8)和旗帜(type=121)通常不需要 AI 操作。

    数据来自 svr_map_brief_objs.briefList 中的单个对象。
    """
    unique_id: str                           # 如 "27_4_1", "48_82_1"
    obj_type: int                            # MapObjectType 值
    key: int = 0                             # 建筑模板 ID
    pos: tuple[int, int] = (0, 0)            # 解码后 (x, y)
    sid: int = 1                             # 服务器 ID

    # --- 归属 ---
    alliance_id: int = 0                     # 占领联盟 ID, 0=中立
    alliance_name: str = ""
    alliance_nick: str = ""
    alliance_flag: int = 0                   # 联盟旗帜样式

    # --- 状态 ---
    status: int = 0                          # 0=可占, 1=已激活/已占领
    fight_flag: int = 0                      # 0=无战斗, >0=战斗中
    etime: int = 0                           # 保护/过期时间戳 (ms)
    open_time: int = 0                       # 开放时间
    change_owner_time: int = 0               # 上次易手时间戳

    # --- KVK 专属 (type=48, 156) ---
    kvk_winner: int = 0

    @property
    def is_neutral(self) -> bool:
        return self.alliance_id == 0

    @property
    def is_fighting(self) -> bool:
        return self.fight_flag != 0

    @classmethod
    def from_brief_obj(cls, obj: dict) -> Building:
        """从 svr_map_brief_objs.briefList 中的单个对象构建

        兼容两种格式:
        - 普通地图: {"uniqueId": "27_4_1", "objBasic": {type, pos, key, aid, ...}}
        - AVA 战场: 扁平结构 {type, id, pos, camp, uniqueId, ...}（无 objBasic 嵌套）

        Args:
            obj: briefList/briefObjs 中的一个元素
        """
        basic = obj.get("objBasic", obj)  # AVA 扁平结构回退到 obj 自身
        raw_pos = basic.get("pos")
        pos = decode_pos(int(raw_pos)) if raw_pos else (0, 0)

        # alliance_id: 普通地图用 aid，AVA 用 camp 字段
        alliance_id = int(basic.get("aid", 0)) or int(basic.get("camp", 0))

        return cls(
            unique_id=obj.get("uniqueId", ""),
            obj_type=basic.get("type", 0),
            key=basic.get("key", 0),
            pos=pos,
            sid=basic.get("sid", 1),
            alliance_id=alliance_id,
            alliance_name=basic.get("alName", ""),
            alliance_nick=basic.get("alNick", ""),
            alliance_flag=basic.get("alFlag", 0),
            status=basic.get("status", 0),
            fight_flag=basic.get("fightFlag", 0),
            etime=int(basic.get("etime", 0)),
            open_time=basic.get("openTime", 0),
            change_owner_time=int(basic.get("changeOwnerTime", 0)),
            kvk_winner=basic.get("kvkWinner", 0),
        )

    def owner_side(self, my_alliance_id: int) -> str:
        """判断归属方: 'neutral' / 'ally' / 'enemy'"""
        if self.alliance_id == 0:
            return "neutral"
        if self.alliance_id == my_alliance_id:
            return "ally"
        return "enemy"
