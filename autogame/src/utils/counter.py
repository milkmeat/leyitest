"""兵种克制计算工具

兵种类别 (id // 100):
  0 = Basher (近战)  — 克 Piercer, 被 Shooter 克
  1 = Shooter (远程) — 克 Basher,  被 Piercer 克
  2 = Piercer (长枪) — 克 Shooter, 被 Basher 克

克制链: Shooter(1) > Basher(0) > Piercer(2) > Shooter(1)
"""

from __future__ import annotations

from src.models.player_state import Soldier

# 类别常量
CATEGORY_BASHER = 0
CATEGORY_SHOOTER = 1
CATEGORY_PIERCER = 2

# counter_of[defender_cat] = 应派出的攻击方类别
COUNTER_OF = {
    CATEGORY_BASHER: CATEGORY_SHOOTER,
    CATEGORY_SHOOTER: CATEGORY_PIERCER,
    CATEGORY_PIERCER: CATEGORY_BASHER,
}

# defender 各类别数量相等时的优先级（Shooter 最安全）
TIEBREAK_ORDER = [CATEGORY_SHOOTER, CATEGORY_BASHER, CATEGORY_PIERCER]


def soldier_category(sid: int) -> int:
    return sid // 100


def dominant_category(comp: dict[int, int]) -> int:
    """从 {soldier_id: count} 中找主导类别

    数量差距 < 5% 总量时视为平局，按 TIEBREAK_ORDER 决胜负。
    防止 _from_uniform 的舍入偏差导致错误主导。
    """
    by_cat: dict[int, int] = {}
    for sid, cnt in comp.items():
        by_cat[soldier_category(sid)] = by_cat.get(soldier_category(sid), 0) + cnt

    if not by_cat:
        return CATEGORY_SHOOTER  # fallback

    total = sum(by_cat.values())
    max_cnt = max(by_cat.values())
    threshold = max_cnt - max(1, total * 5 // 100)
    candidates = [cat for cat, cnt in by_cat.items() if cnt >= threshold]
    if len(candidates) == 1:
        return candidates[0]

    for cat in TIEBREAK_ORDER:
        if cat in candidates:
            return cat
    return candidates[0]


def pick_counter_soldier(
    defender_comp: dict[int, int],
    attacker_soldiers: list[Soldier],
) -> tuple[int, int]:
    """选最佳克制兵种

    Returns:
        (soldier_id, available_count) — attacker 没对应类别时返回 (0, 0)
    """
    if not defender_comp:
        return 0, 0

    def_cat = dominant_category(defender_comp)
    atk_cat = COUNTER_OF[def_cat]

    # 从 attacker 库存中挑同类 value 最大的
    candidates = [s for s in attacker_soldiers
                  if soldier_category(s.id) == atk_cat and s.value > 0]
    if not candidates:
        return 0, 0

    best = max(candidates, key=lambda s: s.value)
    return best.id, best.value
