"""L1 小队队长 — 战术指挥（10个并行实例）

输入: L2战略指令 + 本组10人×3部队详细状态 + 局部地图 + 历史记忆
输出: 每个账号每支部队的具体行动指令 (MOVE_CITY / ATTACK_TARGET /
      GARRISON_BUILDING / JOIN_RALLY / INITIATE_RALLY / SCOUT / RETREAT / STANDBY)
刷新: 每1分钟
"""
