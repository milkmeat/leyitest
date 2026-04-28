# Prompt Record

- Date: 2026-04-28 18:30
- Branch: master
- Commit: perf: 精简 AVA prompt 输出格式 + 裁剪 L1 input 冗余数据

---

### 1

@todo\speed_up_prompt.md

### 2

> **Q:** 主要是处理ava相关的prompt

主要是处理ava相关的prompt

**Files:** `src/ai/prompts/l2_system_ava.txt`, `src/ai/prompts/l1_system_ava.txt`, `src/ai/prompts/l1_system_ava_test.txt`, `src/ai/llm_client.py`, `src/ai/memory.py`

### 3

跑 "./ava_simulate.sh 20" 测试，将最新的日志与昨天的版本(logs.20260427_121911)进行对比，统计llm实际耗时的变化。

### 4

再运行一次测试

### 5

> **Q:** input token如何优化，三个方向：1.裁剪user message冗余数据 2.压缩L1 system prompt 3.Prompt caching。你想先做哪个方向？

1

**Files:** `src/perception/l1_view.py`, `src/ai/l1_leader.py`

### 6

> **Insight:**
> **Input token 裁剪效果显著**：L1 user message 平均从 4861 chars 降到 3087 chars（-36.5%），超出预期的 -15%。主要贡献来自：敌人从 20→10（且第一轮距离全 >100 格时为 0）、移除成员 name、移除 IDLE 部队、历史 3→2 轮。
> **LLM 耗时仍被 API 方差主导**：L2 本轮没有任何改动，但耗时从 23.7s 涨到 39.7s（+67.7%），说明这次 API 服务器负载偏高。

commit
