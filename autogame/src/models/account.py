"""账号与部队数据模型

数据来源（test server 实际返回）:
  - svr_lord_info_new  → 基础信息（uid, 坐标, 名字, 等级, 联盟）
  - svr_player         → 扩展信息（VIP, 状态, 击杀数）
  - svr_soldier        → 士兵列表 [{id, value}]
  - svr_hero_list      → 英雄列表 [{id, lv, state, skill_lv, ...}]
  - svr_buff           → Buff列表 [{id, buff_num}]
  - svr_user_objs      → 城市对象 type=2（战力, 城墙, 增援信息）
"""

from __future__ import annotations

from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.coords import decode_pos


# ------------------------------------------------------------------
# 子模型
# ------------------------------------------------------------------

class Soldier(BaseModel):
    """士兵条目 — 来自 svr_soldier.list"""
    id: int              # 兵种ID: 101=步兵, 201=骑兵, 204=弓兵, 1=预留
    value: int           # 数量


class Hero(BaseModel):
    """英雄 — 来自 svr_hero_list.heros"""
    id: int
    lv: int = 0
    real_lv: int = 0
    state: int = 0                        # 0=空闲
    skill_lv: list[int] = Field(default_factory=list)
    slg_skill_lv: list[int] = Field(default_factory=list)
    stage: int = 0
    exp: int = 0
    exclusive_equip_lv: int = 0


class Buff(BaseModel):
    """Buff 条目 — 来自 svr_buff.buff_item"""
    id: int
    buff_num: int


class TroopState(IntEnum):
    """部队状态（映射 marchBasic.status + marchType）"""
    IDLE = 0            # 城内待命
    MARCHING = 1        # 行军中
    STATIONED = 2       # 驻扎（到达目标点）
    FIGHTING = 3        # 战斗中
    RETURNING = 5       # 回城中
    GARRISON = 11       # 增援/驻防建筑
    RALLYING = 13       # 集结中


class Troop(BaseModel):
    """在外部队 — 来自 svr_user_objs 中的行军对象

    注: 测试账号当前无部署部队，字段基于 marchBasic 结构和 cmd_config 推断，
    后续用实际行军数据校验。
    """
    unique_id: str = ""                   # 如 "108_xxx_1"
    soldiers: dict[int, int] = Field(default_factory=dict)  # {兵种id: 数量}
    hero_main: int = 0                    # 主英雄 id
    hero_vice: int = 0                    # 副英雄 id
    state: TroopState = TroopState.IDLE
    march_type: int = 0                   # 行军类型 (2=攻击, 5=回城, 11=增援, 13=集结)
    pos: tuple[int, int] = (0, 0)         # 当前/目标坐标
    target_unique_id: str = ""            # 目标 unique_id
    btime: int = 0                        # 出发时间戳
    etime: int = 0                        # 到达时间戳


class WallInfo(BaseModel):
    """城墙信息 — 来自 svr_user_objs.cityInfo.wallInfo"""
    durability: int = 1
    max_durability: int = 1
    fire_cpu_time: int = 0
    fire_etime: int = 0


# ------------------------------------------------------------------
# 主模型
# ------------------------------------------------------------------

class Account(BaseModel):
    """我方账号完整数据

    聚合自多个 svr_* 模块，由感知层（data_sync）负责填充。
    """
    # --- 基础 (svr_lord_info_new) ---
    uid: int
    name: str = ""
    city_pos: tuple[int, int] = (0, 0)    # 解码后 (x, y)
    city_level: int = 0
    lord_level: int = 0
    alliance_id: int = 0
    alliance_name: str = ""
    alliance_nick: str = ""

    # --- 扩展 (svr_player) ---
    vip_level: int = 0
    status: int = 0                        # 0=正常
    dead: int = 0                          # 累计死亡兵力

    # --- 战力 (svr_user_objs.cityInfo.force) ---
    power: int = 0

    # --- 城墙 (svr_user_objs.cityInfo.wallInfo) ---
    wall: WallInfo = Field(default_factory=WallInfo)

    # --- 增援 (svr_user_objs.cityInfo) ---
    reinforce_size: int = 5                # 最大增援槽位
    reinforced_num: int = 0                # 当前增援数

    # --- 兵力 (svr_soldier) ---
    soldiers: list[Soldier] = Field(default_factory=list)

    # --- 英雄 (svr_hero_list) ---
    heroes: list[Hero] = Field(default_factory=list)

    # --- Buff (svr_buff) ---
    buffs: list[Buff] = Field(default_factory=list)

    # --- 在外部队（运行时填充） ---
    troops: list[Troop] = Field(default_factory=list)

    # --- AI 分组 ---
    group_id: int = 0                      # L1 小队编号 (0-9)

    # ------------------------------------------------------------------
    # 工厂方法: 从服务器原始数据构建
    # ------------------------------------------------------------------

    @classmethod
    def from_server_modules(
        cls,
        uid: int,
        lord_info: Optional[dict] = None,
        player: Optional[dict] = None,
        soldier: Optional[dict] = None,
        hero_list: Optional[dict] = None,
        buff: Optional[dict] = None,
        city_obj: Optional[dict] = None,
    ) -> Account:
        """从各 svr_* 模块的已解析 dict 构建 Account

        Args:
            uid: 玩家 UID
            lord_info: svr_lord_info_new 解析后的 dict
            player: svr_player 解析后的 dict
            soldier: svr_soldier 解析后的 dict
            hero_list: svr_hero_list 解析后的 dict
            buff: svr_buff 解析后的 dict
            city_obj: svr_user_objs 中 type=2 的城市对象 dict
        """
        data: dict = {"uid": uid}

        # svr_lord_info_new
        if lord_info:
            lord = lord_info.get("lord_info_data", {}).get("lord_info", {})
            raw_pos = lord.get("city_pos")
            if raw_pos:
                data["city_pos"] = decode_pos(int(raw_pos))
            data["name"] = lord.get("uname", "")
            data["city_level"] = lord.get("city_level", 0)
            data["lord_level"] = lord.get("lord_level", 0)
            data["alliance_id"] = lord.get("aid", 0)
            data["alliance_name"] = lord.get("al_name", "")
            data["alliance_nick"] = lord.get("al_nick", "")

        # svr_player
        if player:
            data["vip_level"] = player.get("vip_level", 0)
            data["status"] = player.get("status", 0)
            data["dead"] = player.get("dead", 0)

        # svr_soldier
        if soldier:
            data["soldiers"] = [
                Soldier(id=s["id"], value=s["value"])
                for s in soldier.get("list", [])
            ]

        # svr_hero_list
        if hero_list:
            data["heroes"] = [
                Hero(
                    id=h["id"],
                    lv=h.get("lv", 0),
                    real_lv=h.get("real_lv", 0),
                    state=h.get("state", 0),
                    skill_lv=h.get("skill_lv", []),
                    slg_skill_lv=h.get("slg_skill_lv", []),
                    stage=h.get("stage", 0),
                    exp=h.get("exp", 0),
                    exclusive_equip_lv=h.get("exclusive_equip_lv", 0),
                )
                for h in hero_list.get("heros", [])
            ]

        # svr_buff
        if buff:
            data["buffs"] = [
                Buff(id=b["id"], buff_num=b["buff_num"])
                for b in buff.get("buff_item", [])
            ]

        # svr_user_objs — type=2 城市对象
        if city_obj:
            ci = city_obj.get("cityInfo", {})
            data["power"] = int(ci.get("force", 0))
            data["reinforce_size"] = ci.get("reinforceSize", 5)
            data["reinforced_num"] = ci.get("reinforcedNum", 0)
            wi = ci.get("wallInfo", {})
            if wi:
                data["wall"] = WallInfo(
                    durability=wi.get("durability", 1),
                    max_durability=wi.get("maxDurability", 1),
                    fire_cpu_time=int(wi.get("fireCpuTime", 0)),
                    fire_etime=int(wi.get("fireEtime", 0)),
                )

        return cls(**data)

    @classmethod
    def from_sync_info(cls, info: dict, group_id: int = 0) -> Account:
        """从 GameAPIClient.get_player_info() 返回的扁平 dict 构建 Account

        get_player_info 返回的结构:
            {uid, pos, name, city_level, lord_level, alliance_id,
             vip_level, alliance_name, status, dead, level,
             soldiers: [{id, value}], heroes: [{id, lv, ...}], buffs: [{id, buff_num}]}

        相比 from_server_modules，此方法更简洁，适用于批量同步场景。
        """
        data: dict = {
            "uid": info["uid"],
            "group_id": group_id,
        }

        if "pos" in info:
            data["city_pos"] = info["pos"]
        if "name" in info:
            data["name"] = info["name"]
        if "city_level" in info:
            data["city_level"] = info["city_level"]
        if "lord_level" in info:
            data["lord_level"] = info["lord_level"]
        if "alliance_id" in info:
            data["alliance_id"] = info["alliance_id"]
        if "alliance_name" in info:
            data["alliance_name"] = info["alliance_name"]
        if "vip_level" in info:
            data["vip_level"] = info["vip_level"]
        if "status" in info:
            data["status"] = info["status"]
        if "dead" in info:
            data["dead"] = info["dead"]

        if "soldiers" in info:
            data["soldiers"] = [
                Soldier(id=s["id"], value=s["value"])
                for s in info["soldiers"]
            ]

        if "heroes" in info:
            data["heroes"] = [
                Hero(
                    id=h["id"],
                    lv=h.get("lv", 0),
                    real_lv=h.get("real_lv", 0),
                    state=h.get("state", 0),
                    skill_lv=h.get("skill_lv", []),
                    slg_skill_lv=h.get("slg_skill_lv", []),
                    stage=h.get("stage", 0),
                    exp=h.get("exp", 0),
                    exclusive_equip_lv=h.get("exclusive_equip_lv", 0),
                )
                for h in info["heroes"]
            ]

        if "buffs" in info:
            data["buffs"] = [
                Buff(id=b["id"], buff_num=b["buff_num"])
                for b in info["buffs"]
            ]

        return cls(**data)
