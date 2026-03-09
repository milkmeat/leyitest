"""L2 军团指挥官 — 全局战略决策

输入: 10个小队状态摘要 + 全局地图摘要 + 积分 + 管理员指令 + 历史记忆
输出: 10条小组级战略指令 (ATTACK_BUILDING / DEFEND_BUILDING / RALLY_ATTACK /
      RETREAT / SUPPORT_SQUAD / STANDBY / JOIN_CROSS_RALLY 等)
刷新: 每1-3分钟（可配置）
"""
