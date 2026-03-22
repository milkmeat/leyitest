"""敌方玩家数据模型

数据来源:
  - svr_map_brief_objs.briefList 中 type=2 对象 → 城市坐标、联盟
  - svr_user_objs 中 type=2 对象 → 战力(force)、城墙、增援信息
  - get_player_info(对敌方uid) → 兵种/英雄（需侦察或直接查询）

注意: 无战争迷雾，可实时获取所有敌方位置和基础信息，
但英雄等级/技能/科技等级需要侦察才能确认。
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from src.models.player_state import Soldier, Troop
from src.utils.coords import decode_pos


class Enemy(BaseModel):
    """敌方玩家"""
    uid: int
    name: str = ""
    city_pos: tuple[int, int] = (0, 0)
    city_level: int = 0
    power: int = 0                         # cityInfo.force
    alliance_id: int = 0
    alliance_name: str = ""
    alliance_nick: str = ""

    # --- 可见信息（地图概览即可获得） ---
    fight_flag: int = 0                    # 是否正在战斗

    # --- 侦察/查询后填充 ---
    soldiers: list[Soldier] = Field(default_factory=list)
    troops: list[Troop] = Field(default_factory=list)    # 在外行军部队

    @property
    def is_fighting(self) -> bool:
        return self.fight_flag != 0

    @classmethod
    def from_brief_obj(cls, obj: dict) -> Enemy:
        """从 svr_map_brief_objs.briefList 中 type=2 城市对象构建

        兼容两种格式:
        - 普通地图: {"uniqueId": "2_uid_1", "objBasic": {type:2, pos, uid, aid, ...}}
        - AVA 战场: 扁平结构 {type:10101, pos, uid, camp, ...}（无 objBasic 嵌套）

        Args:
            obj: briefList/briefObjs 中的一个元素
        """
        basic = obj.get("objBasic", obj)  # AVA 扁平结构回退到 obj 自身
        raw_pos = basic.get("pos")
        pos = decode_pos(int(raw_pos)) if raw_pos else (0, 0)
        # uid: 普通地图在 objBasic.uid，AVA 扁平结构在 id 字段
        uid = int(basic.get("uid", 0)) or int(basic.get("id", 0))

        # alliance_id: 普通地图用 aid，AVA 用 camp 字段
        alliance_id = int(basic.get("aid", 0)) or int(basic.get("camp", 0))

        return cls(
            uid=uid,
            city_pos=pos,
            alliance_id=alliance_id,
            fight_flag=basic.get("fightFlag", 0),
        )

    @classmethod
    def from_player_info(cls, info: dict) -> Enemy:
        """从 get_player_info() 返回的扁平 dict 构建

        Args:
            info: {uid, pos, name, alliance_id, alliance_name, soldiers, ...}
        """
        pos = info.get("pos", (0, 0))
        soldiers = [
            Soldier(id=s["id"], value=s["value"])
            for s in info.get("soldiers", [])
        ]
        return cls(
            uid=info["uid"],
            name=info.get("name", ""),
            city_pos=tuple(pos) if isinstance(pos, list) else pos,
            alliance_id=info.get("alliance_id", 0),
            alliance_name=info.get("alliance_name", ""),
            soldiers=soldiers,
        )

    @classmethod
    def from_user_obj(cls, obj: dict) -> Enemy:
        """从 svr_user_objs 中 type=2 对象构建（更详细）

        Args:
            obj: svr_user_objs.objs 中 type=2 的完整对象, 包含 cityInfo
        """
        basic = obj.get("objBasic", {})
        ci = obj.get("cityInfo", {})
        raw_pos = basic.get("pos")
        pos = decode_pos(int(raw_pos)) if raw_pos else (0, 0)

        return cls(
            uid=int(basic.get("uid", basic.get("id", 0))),
            name=ci.get("uname", ""),
            city_pos=pos,
            city_level=ci.get("level", 0),
            power=int(ci.get("force", 0)),
            alliance_id=int(basic.get("aid", 0)),
            alliance_name=ci.get("alName", ""),
            alliance_nick=ci.get("alNick", ""),
            fight_flag=obj.get("fightBasic", {}).get("isFight", 0),
        )
