# Prompt Record

- Date: 2026-04-29 17:30
- Branch: master
- Commit: perf: L1 整体超时 90s + 无重试 + 部分结果恢复（asyncio.wait 替代 gather）

---

### 1. 分析 logs 日志中 LLM 调用耗时

看一下logs/日志，列出每次llm调用的耗时，进行统计

> **Insight**
> - L1 的耗时波动极大（21s ~ 334s），因为 L1 是 4 个 LLM 并行调用取最慢的那个，任何一个 LLM 响应慢都会拖长整体时间
> - L2 相对稳定（10~46s），因为只有 1 次 LLM 调用
> - LLM 占每轮总耗时的 65%~98%，是绝对瓶颈

### 2. L1 超过 200s 的原因分析

L1耗时有几次超过200s，可能原因是什么，应如何改进？

> **Insight**
> - 核心问题不是 LLM "慢"，而是 LLM 超时后重试叠加。timeout=120s × max_retries=2 意味着单个 squad 最坏情况可达 363s
> - asyncio.gather 取所有并行 squad 中最慢的那个，一个 squad 超时重试就拖垮整轮
> - 当前用的是智谱 GLM-4.5-Air，云端 API 响应时间不稳定是常态

### 3. 制定 L1 超时改造方案

L1缩短超时到60s，不再retry，当60s到达时，直接执行已完成响应的squad，超时的squad跳过本轮，等下轮再决策。如果未完成的squad在流式返回中已有部分内容，也可以只执行部分指令。

> **Plan**
> 1. `llm_client.py` — 流式 chunks 从局部变量提升到实例级 `_streaming_chunks` dict，新增 `chat_yaml_once()`（无重试无超时）和 `get_partial_content()`（读取超时调用的部分内容）
> 2. `l1_leader.py` — `decide()` 切换到 `chat_yaml_once()`，新增 `try_parse_partial()` 从部分流式内容恢复指令，`decide_all()` 用 `asyncio.wait(timeout=N)` 替代 `asyncio.gather`
> 3. `config/system.yaml` — timeout_seconds: 60, max_retries: 0

> **Insight**
> - `asyncio.wait` vs `asyncio.gather` 的关键区别：wait 返回 (done, pending) 两个集合，可以对已完成和未完成的任务分别处理；gather 必须等所有任务完成
> - 流式 chunks 提升到实例级是实现"部分内容恢复"的关键——asyncio.wait_for 取消协程时，局部变量随栈帧销毁，但实例属性会保留

**Files:** `src/ai/llm_client.py`, `src/ai/l1_leader.py`, `config/system.yaml`

### 4. 60s 测试后调整为 90s

> **Q:** 60s 测试结果显示 65% 轮次触发超时，用户要求调整

把60s的超时改成90s，再测试一次

> **Insight**
> - 90s 上限下只有 25% 的轮次触发超时（vs 60s 的 65%），说明大部分 LLM 调用在 60-90s 之间完成
> - 平均耗时几乎一样（50.4s vs 51.1s），因为快的轮次不受上限影响
> - 62% 的轮次在 60s 内完成——这是 LLM 响应的"自然速度"

**Files:** `src/ai/l1_leader.py`
