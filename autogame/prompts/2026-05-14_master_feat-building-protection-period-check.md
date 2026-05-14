# Prompt Record

- Date: 2026-05-14 17:22
- Branch: master
- Commit: feat: AVA 建筑保护期检测（openTime/etime 未到期时阻止攻击）

---

### 1

看一下 @ava_simulate.sh 最近一次的执行日志（未全部执行完，被我中断了）。在ava战场的开始几分钟，中立建筑会有保护状态，此时无法发起进攻（部队行军到达后会直接返回，无法占领）。请正确处理这种情况，只有在建筑的保护消失后才进攻。如果要进行测试的话，可以新建一个ava战场并读取建筑状态。小建筑会保护3分钟，大建筑保护10分钟

> **Insight**
> **问题根因**：服务器对保护期建筑的攻击命令不返回错误码，而是让部队行军到达后直接返回。这意味着从 API 层面无法通过错误码检测保护状态，必须在发送命令前主动检查 `etime` 字段。
>
> **分层防御设计**：方案采用两层防护 — L0 硬拦截（保证不浪费出征槽位）+ L1/L2 视图标记（让 AI 不浪费规划周期在保护建筑上）。即使 LLM 忽略了 `[PROTECTED]` 标记，L0 也会拦截。
>
> **时间戳对比的正确性**：`etime` 是服务器返回的绝对时间戳（ms），L0 执行时用 `time.time() * 1000` 做实时比较。即使 L1 视图构建时建筑还在保护期，到 L0 执行时保护可能已过期，此时会正确放行。
>
> **关键发现**：建筑保护不是通过 `etime` 字段实现的，而是通过 `openTime` 字段。`openTime > now_ms` 表示建筑尚未开放，无法攻击。`etime` 在当前数据中全为 0。最终实现同时检查两个字段以覆盖所有情况。

**Files:** `src/models/building.py`, `src/executor/l0_executor.py`, `src/perception/l1_view.py`, `src/perception/l2_view.py`, `src/ai/prompts/l1_system_ava.txt`, `src/ai/prompts/l2_system_ava.txt`

### 2

给 @src\ai\prompts\l2_system_ava.txt 加上一个逻辑：在战场刚刚开始时，中央的 "steam factory"会处于保护状态暂时不能争夺。在保护状态结束后，应将考虑其作为优先级最高的争夺目标（其分值最高）

**Files:** `src/ai/prompts/l2_system_ava.txt`

### 3

再加上一条策略，如果有空闲的的中立建筑（不在保护中），可以派出单个队员抢占，争取首占积分

**Files:** `src/ai/prompts/l2_system_ava.txt`
