# Prompt Record

- Date: 2026-04-06 20:30
- Branch: master
- Commit: docs: 补充 AVA 建筑速查表到 L2 战场 prompt（含 map_type/得分/效果/波次/优先级）

---

### 1. 提取建筑摘要补充到 L2 AVA prompt

阅读 doc_lvl_building.yaml 中的 doc_lvl_building一节，为ava地图中的每个建筑信息，提取最简短的摘要，补充到l2_prompt_ava中

> **Insight**
> 建筑信息对 L2 指挥官至关重要——它需要知道哪些建筑得分高（优先抢占）、哪些有增益效果（战略价值）、以及开放波次（时间规划）。摘要要极简，因为 prompt token 很贵，但信息量要够 L2 做出正确的优先级判断。

> **Insight**
> 表格按得分从高到低排列，让 L2 一眼看出 Steam Factory(9000) >> Production Plant(6000) >> 其余，做资源分配时自然倾向高价值目标。末尾的两行优先级总结是给 LLM 的"决策锚点"——当多个建筑同时可争夺时，它不需要自己从表格推算，直接参考排序即可，减少推理负担和幻觉风险。

**Files:** `src/ai/prompts/l2_system_ava.txt`

### 2. 添加 map_type 列

把建筑map_type加到prompt表格里

> **Insight**
> 注意 Arsenal 和 Boiler House 共享 map_type: 10002（都属于 Boost Building 类别）。L2 在感知层拿到的建筑数据会用 map_type 标识类型，有了这列它就能直接将感知数据与速查表对应上，不需要靠名字做模糊匹配。

**Files:** `src/ai/prompts/l2_system_ava.txt`
