# Prompt Record

- Date: 2026-03-17 23:30
- Branch: master
- Commit: feat: implement L2 Commander with LLM integration and wire into main loop

---

### 1. Implement L2 Commander and main loop integration

Implement the following plan:

# L2 军团指挥官 (`l2_commander.py`) + 主循环接入

## Context

Phase 3 进行中。L2 全局视图 (`l2_view.py`) 和 L2 系统提示词 (`l2_system.txt`) 已完成。
现在需要实现 L2 Commander — 接收 L2GlobalView，调用 LLM 生成战略指令，传给 L1。

当前 `loop.py` Phase 2 是 stub（`l2_orders = []`），Phase 3 传 `l2_orders={}` 给 L1Coordinator。

## 实现计划

### 文件 1: `src/ai/l2_commander.py`（新建，~120 行）

参考 `l1_leader.py` 的模式，但更简单（1 次 LLM 调用，无并行）：

```python
class L2Commander:
    def __init__(self, config: AppConfig, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
        self.system_prompt = _load_prompt("l2_system.txt")
        self.view_builder = L2ViewBuilder(config)

    async def decide(self, snapshot: SyncSnapshot) -> dict[int, str]:
        """全局决策 → {squad_id: order_text}"""
        # 1. 构建 L2 全局视图
        view = self.view_builder.build(snapshot)
        # 2. 格式化为 markdown user prompt
        user_prompt = self.view_builder.format_text(view)
        # 3. LLM 调用
        response = await self.llm.chat_json(self.system_prompt, user_prompt)
        # 4. 解析为 dict[int, str]
        return self._parse_orders(response)

    def _parse_orders(self, response: dict) -> dict[int, str]:
        """容错解析 LLM JSON → {squad_id: order}"""
        orders_raw = response.get("orders", [])
        valid_squad_ids = {s.squad_id for s in self.config.squads.squads}
        result = {}
        for item in orders_raw:
            sid = item.get("squad_id")
            order = item.get("order", "")
            if sid in valid_squad_ids and order:
                result[sid] = order
        # 记录缺失小队
        missing = valid_squad_ids - result.keys()
        if missing:
            logger.warning("L2 缺失小队指令: %s", missing)
        return result
```

**关键设计决策：**
- `decide()` 返回 `dict[int, str]`，直接对齐 `L1Coordinator.decide_all(l2_orders=...)` 的接口
- `_parse_orders()` 容错：跳过无效 squad_id，记录缺失小队
- system prompt 从 `l2_system.txt` 加载（已有完整内容含 JSON schema）
- 复用 `L2ViewBuilder`（已测试）构建 user prompt
- `_load_prompt()` 辅助函数复用 `l1_leader.py` 中相同的 prompt 加载模式

**dry_run 兼容：**
- `LLMClient(dry_run=True)` 返回预设 JSON `_DRY_RUN_RESPONSE`（L1 格式，无 `orders` 字段）
- `_parse_orders()` 找不到 `orders` 时返回空 dict — 天然兼容，无需改动 `llm_client.py`

### 文件 2: `src/controller/loop.py`（修改 ~15 行）

Phase 2 替换 stub，Phase 3 传递真实 l2_orders

### 文件 3: `tests/test_l2_commander.py`（新建，~80 行）

5 个单元测试，mock LLMClient

> **Plan**
> 上述完整实现计划由用户在 plan mode 中制定并审批。

> **Insight**
> - L2Commander 遵循与 L1Leader 相同的"构建视图 → LLM 调用 → 解析响应"模式，但更简单：只有 1 次 LLM 调用（L1 是 10 次并行）
> - `_parse_orders()` 的容错设计很关键：LLM 输出不可控，必须跳过非法 squad_id、处理缺失字段，同时记录 warning 便于调试
> - dry_run 兼容是零成本的：`LLMClient(dry_run=True)` 返回的 `_DRY_RUN_RESPONSE` 没有 `orders` 字段，`response.get("orders", [])` 自然返回空列表
> - **分层架构解耦**：L2Commander 只输出 `dict[int, str]`（squad_id → 自然语言指令），L1Leader 接收字符串后自行决策具体行动
> - **条件导入模式**：`loop.py` 用 `try/except ImportError` 将 L2Commander 设为可选依赖
> - **容错解析策略**：对 LLM 输出采用"尽力而为"策略 — 跳过坏数据、保留好数据、记录 warning

**Files:** `src/ai/l2_commander.py`, `src/controller/loop.py`, `tests/test_l2_commander.py`
