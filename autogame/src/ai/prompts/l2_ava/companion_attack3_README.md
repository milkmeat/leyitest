# companion_attack3.txt 修复说明

## 问题背景

在模拟测试 `companion_attack2_vs_defend_20260612_171033_r4m1` 中发现：
- companion_attack2 一直领先
- 但仍然积极攻占 Steam Factory
- 导致对手 (defend) 一直无法反超
- 陪玩让分机制失效

## 根本原因

companion_attack2.txt 中存在规则冲突：

1. **第19行** 声明 Steam Factory 为"最高优先级，保护期结束后立即攻击"
2. **第77行** 再次声明 Steam Factory 为"最高优先级，保护期结束后立即攻击"
3. 虽然第82行有注意说明"在比分接近或领先时，优先攻击低分建筑"，但位置靠后、力度不够
4. AI 在决策时优先遵循"最高优先级"规则，导致领先时仍攻击 Steam Factory

## 修复方案

### 1. 修改 Steam Factory 规则（第19行）
```
8. **Steam Factory 规则**: Steam Factory 是全场最高分建筑（9000+1800/min）。
**仅在落后追赶状态（score_diff < -2000）下**，一旦保护结束（不再标记[保护中]），
应立即将距离最近的1个小队分配去集结攻击。
**在比分接近或领先时，严禁攻击Steam Factory！**
```

### 2. 重构进攻优先级（第75-94行）
将进攻优先级按状态拆分，明确每个状态可攻击的建筑类型：

| 状态 | 可攻击建筑 | 不可攻击建筑 |
|------|-----------|-------------|
| 落后追赶 | Steam Factory > Production Plant > Production Shed > 其余 | 无 |
| 比分接近 | Production Shed > 其余 | Steam Factory, Production Plant |
| 小幅领先 | 其余 | Steam Factory, Production Plant, Production Shed |
| 大幅领先/临近结束 | 无 | 所有建筑 |

### 3. 更新思考步骤（第128-146行）
添加"根据当前状态选择目标建筑"步骤，确保 AI 决策时正确应用状态限制。

## 预期效果

修复后，AI 将严格遵循陪玩策略：

| 积分态势 | 行为 |
|---------|------|
| score_diff < -2000 | 全力进攻 Steam Factory（正常追分） |
| -2000 ≤ score_diff ≤ 2000 | 避免攻击 Steam Factory/Production Plant（控制节奏） |
| 2000 < score_diff ≤ 10000 | 只攻击低分建筑（主动让分） |
| score_diff > 10000 | 完全停止进攻（给对手追分机会） |
| time_remaining ≤ 600 | 完全停止进攻（确保对方获胜） |

## 版本信息

- **文件**: `src/ai/prompts/l2_ava/companion_attack3.txt`
- **版本**: v3
- **创建日期**: 2026-06-15
- **基于**: companion_attack2.txt