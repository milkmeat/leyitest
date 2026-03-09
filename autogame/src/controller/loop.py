"""AI 控制主循环 — 60秒一轮

Phase 1: Sync      (0-5s)   并发查询100账号状态 + 全图数据
Phase 2: L2 Strategy (5-15s)  军团指挥官生成10条小组级战略指令
Phase 3: L1 Tactics  (15-45s) 10个小队长并行生成具体行动指令 + L0校验
Phase 4: Action      (45-55s) 流水线发送HTTP指令
Phase 5: Sleep       (55-60s) 等待下一轮
"""
