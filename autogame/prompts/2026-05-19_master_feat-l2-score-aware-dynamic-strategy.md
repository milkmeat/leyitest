# Prompt Record

- Date: 2026-05-19 10:30
- Branch: master
- Commit: feat: L2 积分感知动态策略（落后激进进攻/领先防守巩固）

---

### 1

在 @src\ai\prompts\l2_system_ava.txt 中加入以下功能：
1. 将当前敌我双方的得分信息注入
2. 若我方得分落后时，采用更激进的策略，主动夺取更多建筑，优先是中立建筑，其次是敌方已控制但未驻防的建筑，高分建筑优先
3. 若我方得分领先，则以防守为主，在确保最高分建筑控制权的情况下，丢了哪个建筑就夺回来。

**Files:** `src/ai/prompts/l2_system_ava.txt`, `src/perception/l2_view.py`

### 2

> **Q:** 本次修改是否也包括 l2_view.py 的代码改动（让积分数据实际出现在 LLM 输入中），还是只改 prompt 模板文件？

两者都改 (Recommended)

**Files:** `src/perception/l2_view.py`

> **Insight**
> - **Prompt 与数据管道分离设计**: 系统 prompt 定义"如何解读数据"和"如何决策"，而实际数据通过 user message（`format_text()` 输出的 markdown）注入。这种分离让策略规则可以独立于数据采集迭代。
> - **`getattr` 兼容模式**: `build()` 中用 `getattr(snapshot, 'score', None)` 而非直接访问，确保在 `SyncSnapshot` 尚未添加 `score` 字段时不会崩溃——这是渐进式集成的常见模式。
> - **条件输出**: `format_text()` 中 `if view.ally_score or view.enemy_score` 确保在没有积分数据时不输出空行，避免 LLM 看到 "积分: 0 vs 0" 产生误判。
