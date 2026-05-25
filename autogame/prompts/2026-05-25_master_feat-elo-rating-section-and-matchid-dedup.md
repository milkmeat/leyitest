# Prompt Record

- Date: 2026-05-25 19:30
- Branch: master
- Commit: feat: Elo 等级分排名 Section + match_id 时间戳去重

---

### 1

@ava_results.csv 把得分为0的场次删掉（对战过程未正常执行）

> **Insight**
> 按"MATCH_START 到下一个 MATCH_START"分组来识别每场比赛的边界，而非仅靠 match_id——因为同一个 match_id（如 `default_vs_attack_r5m1`）会在不同运行批次中重复出现，单纯按 ID 分组会错误合并不同时间的场次。

**Files:** `ava_results.csv`

### 2

@visualize_ava.py 在html文件的开头加上一个section是等级分的计算，包括每个策略的胜负统计。虽然目前只有两个策略，以后会有多个策略，两两之间都会执行若干场次的对战

**Files:** `visualize_ava.py`

### 3

> **Q:** 计划是否可以执行？

还有一个要修复的：matchid（例如default_vs_attack_r1m1）现在会重复出现，要修改 ava_simulate.sh 让他在保存数据时，加上一个时间戳使得matchid唯一

> **Insight**
> 1. **Elo Rating 逐场更新**：按时间顺序遍历每场 MATCH_END，用期望胜率公式 `E = 1/(1+10^(Δ/400))` 和 K=32 更新双方分数。这比简单胜率更准确地反映策略实力——如果 A 在已经领先很多分后仍能赢 B，得分变化会更小（因为期望胜率已经很高）。
> 2. **match_id 时间戳前缀**：`RUN_TS=$(date +%Y%m%d_%H%M%S)` 在脚本启动时生成一次，确保同一批次的所有 match 共享前缀但跨批次唯一。比在每场单独生成时间戳更整洁（同批次可以按前缀归组）。

**Files:** `ava_simulate.sh`, `visualize_ava.py`
