# Prompt Record

- Date: 2026-03-19
- Branch: master
- Commit: feat: implement memory module for AI context management

- Add LoopHistoryEntry data model for recording loop history
- Add L2MemoryStore for L2 commander strategic memory
- Add L1MemoryStore for L1 squad tactical memory
- Add SituationSummarizer for LLM-powered situation summarization
- Integrate memory into L2Commander, L1Leader, and AIController
- Add Phase 5: Memory to main loop for history persistence
- Add 13 unit tests for memory module

---

### 1. 实现记忆模块 memory.py

开始下—功能:实现记忆模块memory·Py

> **Plan**
> 记忆模块需要实现：
> 1. **数据结构**：
>    - LoopHistoryEntry: 单轮历史记录（态势摘要 + L2指令 + L1指令 + 执行结果）
>    - MemoryStore: 主记忆存储类
>
> 2. **功能**：
>    - 保留最近5个loop的历史（可配置）
>    - L2和L1各自维护独立历史
>    - 压缩策略：由LLM生成摘要（非硬编码），每条不超过200 tokens
>    - 为 L2 和 L1 提供历史上下文
>
> 3. **集成点**：
>    - 在 `L2Commander.decide()` 中传递历史
>    - 在 `L1Leader.decide()` 中传递历史
>    - 在 `AIController._run_one_loop()` 中保存历史

> **Insight**
> **记忆模块实现要点**
>
> 1. **三层记忆架构**：`LoopHistoryEntry`（数据模型）→ `MemoryStore`（基类）→ `L2MemoryStore`/`L1MemoryStore`（专用实现）
>
> 2. **环形缓冲设计**：使用 `deque(maxlen=N)` 实现自动覆盖，避免内存无限增长，配置为默认保留最近 5 轮
>
> 3. **LLM 摘要压缩**：`SituationSummarizer` 将详细战况压缩为 ≤200 tokens 的简洁描述，降低上下文成本

**Files:** `src/ai/memory.py`, `src/ai/l2_commander.py`, `src/ai/l1_leader.py`, `src/controller/loop.py`, `tests/test_memory.py`
