# Prompt Record

- Date: 2026-04-01 18:18
- Branch: master
- Commit: feat: 缩减阵容至2队×2方 + l2_decide 支持 AVA + 去除战力字段

---

### 1. Shrink lineup to 2 squads per side with reserves

编辑一下双方阵容，每方只保留2个小队10名队员，其余的放入后备名单

> **Insight**
> 从 20+20 缩到 10+10，L1 并行 LLM 调用从 4 路降到 2 路，单轮决策时间和 token 成本都减半

**Files:** `config/accounts.yaml`, `config/squads.yaml`

### 2. Add 20 accounts to AVA battlefield

使用cli工具，把20个账号都加入到ava战场中。不在名单中的账号移出战场

**Files:** (CLI operations only, no code changes)

### 3. Ask about l2_decide CLI for AVA

使用什么cli命令测试l2_decide

### 4. Ask about l2_decide AVA parameter

> **Q:** python src/main.py --llm ollama l2_decide 使用什么参数让cli读取ava的战场态势及人员配置

### 5. Add --ava parameter to l2_decide

加上（为 l2_decide 添加 --ava <lvl_id> 参数支持）

> **Insight**
> - lvl_id=0（默认）查询普通地图数据，lvl_id=29999 查询 AVA 战场数据——两者的建筑、部队、坐标完全不同
> - env_config.yaml 的 lvl_id: 29999 只影响 HTTP header，不影响 DataSyncer.sync() 的行为，sync 是靠参数控制同步模式的

**Files:** `src/main.py`

### 6. Add squad_id parsing tolerance for LLM output

> **Q:** LLM 输出 squad_id: 1-Alpha 导致解析失败，要我给 L2 解析器加上 1-Alpha → 1 的容错处理吗？

yes

> **Insight**
> - 容错用 re.match(r"(\d+)", str(sid)) 提取前导数字，对 "1"、"1-Alpha"、"2 (Bravo)" 等格式都能正确处理
> - 如果 squad_id 本身就是 int（正常情况），not isinstance(sid, int) 直接跳过正则，零开销

**Files:** `src/ai/l2_commander.py`

### 7. Remove 战力 from squad status table

把队员状态中的"战力"去掉，只要保留兵力就可以了

> **Insight**
> 战力(power)是个综合指标，对 LLM 决策帮助不大且浪费 token；兵力(soldiers)是实际可操作的数量，更实用

**Files:** `src/perception/l2_view.py`

### 8. Remove 战力 from enemy clusters and overall status

也去掉（敌方集群和总体态势中的战力）

**Files:** `src/perception/l2_view.py`

### 9. Remove 战力 from L2 prompt template

prompt里面关于战力的描述也去掉，如有

**Files:** `src/ai/prompts/l2_system.txt`
