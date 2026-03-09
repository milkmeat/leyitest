"""模拟引擎 — Tick 驱动

每秒更新世界状态:
- 行军模拟: 检查MARCHING部队是否到达目标
- 战斗结算: 按兵力比例+兵种克制计算损失
- 集结状态机: GATHERING(5分钟) → MARCHING → FIGHTING → COMPLETED
- 积分更新: 每分钟按据点归属累加积分
"""
