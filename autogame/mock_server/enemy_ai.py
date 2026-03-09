"""敌方模拟 AI

模式:
- passive:       不动，仅驻防据点
- simple_script: 每2分钟随机占领中立据点，被攻击时50%概率移城
- aggressive:    主动集结进攻，优先攻击最弱目标
- mirror:        镜像复制我方AI行为（延迟1轮）
"""
