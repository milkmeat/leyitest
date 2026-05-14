"""目标驻防兵种探测

v1: 仅两条路径（无 scout）:
  1. briefObj.troopUniqueIds → 反查我方 accounts 的 user_troops（零网络）
  2. briefObj.curTroopNum → 三等分兜底（敌方/无详情）
"""

from __future__ import annotations

import logging
from typing import Optional

from src.models.player_state import PlayerState

logger = logging.getLogger(__name__)


def probe_defender_composition(
    target_unique_id: str,
    target_cur_troop_num: int,
    target_troop_unique_ids: list[str],
    accounts: dict[int, PlayerState],
    my_camp: int,
    target_camp: int,
) -> Optional[dict[int, int]]:
    """探测目标驻防兵种构成

    Args:
        target_unique_id: 建筑 unique_id (如 "10001_1778203928536761")
        target_cur_troop_num: briefObj.curTroopNum
        target_troop_unique_ids: briefObj.troopUniqueIds
        accounts: 我方所有账号状态 {uid: PlayerState}
        my_camp: 我方阵营 id
        target_camp: 目标当前占领阵营

    Returns:
        {soldier_id: count} 或 None（无数据时）
    """
    # 路径 1: 我方占领 → 反查 user_troops
    if target_camp == my_camp and target_troop_unique_ids:
        comp = _from_user_troops(target_troop_unique_ids, accounts)
        if comp:
            logger.debug("defender probe: user_troops 命中 %s → %s", target_unique_id, comp)
            return comp

    # 路径 2: briefObj curTroopNum 三等分兜底
    if target_cur_troop_num > 0:
        comp = _from_uniform(target_cur_troop_num)
        logger.debug("defender probe: uniform 兜底 %s cur=%d → %s",
                      target_unique_id, target_cur_troop_num, comp)
        return comp

    return None


def _from_user_troops(
    troop_unique_ids: list[str],
    accounts: dict[int, PlayerState],
) -> Optional[dict[int, int]]:
    """从 accounts 的 user_troops 反查驻防兵种"""
    lookup = set(troop_unique_ids)
    merged: dict[int, int] = {}

    for uid, acct in accounts.items():
        for troop in acct.troops:
            if troop.unique_id in lookup:
                for sid, cnt in troop.soldiers.items():
                    merged[sid] = merged.get(sid, 0) + cnt

    return merged if merged else None


def _from_uniform(total: int) -> dict[int, int]:
    """三等分兜底: 用三个代表性 id (4=Basher T4, 104=Shooter T4, 204=Piercer T4)

    丢弃余数（最多 2），避免舍入偏差导致某一类"伪主导"。
    """
    third = total // 3
    return {4: third, 104: third, 204: third}
