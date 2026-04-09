# Prompt Record

- Date: 2026-04-09 16:00
- Branch: master
- Commit: fix: L2 prompt 小队数量改为动态替换，不再写死10个

---

### 1. L2 prompt 小队数量动态化

L2 decide 有这样的输出"thinking: 当前显示有2个小队（1-Alpha和2-Bravo），但需要为10个小队制定指令"，修改一下prompt，有几个小队就管理几个小队，不要写死10个

> **Insight**
> 这里用简单的 `str.replace` 而不是 `str.format` 或 Jinja2，是因为 prompt 文本中可能包含 YAML 的花括号 `{}`，用 `.format()` 会误匹配导致 `KeyError`。单个占位符用 `.replace()` 最安全。替换放在 `__init__` 而非每次 `decide()` 调用时，因为小队数量在运行期间不会变化，避免重复计算。

**Files:** `src/ai/prompts/l2_system.txt`, `src/ai/prompts/l2_system_ava.txt`, `src/ai/l2_commander.py`
