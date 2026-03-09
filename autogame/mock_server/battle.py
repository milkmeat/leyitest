"""战斗结算模块

简化战斗模型:
- 兵力比例决定胜负
- 兵种克制: archer > infantry > cavalry > archer (克制系数1.3/0.7)
- 多路攻击按到达顺序逐次结算
- 兵力归零 → WOUNDED状态
"""
