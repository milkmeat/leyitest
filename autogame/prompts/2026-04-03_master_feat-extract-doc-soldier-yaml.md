# Prompt Record

- Date: 2026-04-03
- Branch: master
- Commit: feat: 提取 document_english.json 兵种数据到 doc_soldier.yaml

---

### 1. 读取 doc_soldier 信息

载入document_english.json，读取里面的doc_soldier信息

> **Insight**
> 1. 三角克制体系：Basher(步兵) > Piercer(穿刺) > Shooter(射手) > Basher，对应 CLAUDE.md 中的 archer > infantry > cavalry > archer（名称不同但结构一致，系数 1.3/0.7）
> 2. 等级跨度 T0→T4：最高 T4 只有一级，而 T3 有 4 个子等级，意味着 T3 → T4 是质变而非量变，AI 决策时需特别关注敌方 T4 兵力
> 3. 210 条 vs 3 类型×55 = 165：多出的 45 条是 Other 类（僵尸/夜爪等），说明我方兵种表混入了 PVE 敌方单位，解析时需过滤

### 2. 保存兵种信息到 YAML

把这些兵种信息保存到yaml中

> **Insight**
> 1. JSON key → YAML list：原 JSON 用字符串 key（如 "1", "2"）做 ID，转为 YAML 时提取为 id 字段并存为列表，按 ID 排序更直观
> 2. HTML 标签保留：info 字段中的 `<color=...>` 和 grade 中的 `<b>` 标签原样保留，因为这些是游戏客户端渲染格式

**Files:** `docs/p10/doc_soldier.yaml`
