# Prompt Record

- Date: 2026-03-10 20:00
- Branch: master
- Commit: implement L0 executor: AI instruction models, validation, and CLI debug command

---

### 1. Implement L0 executor from plan

Implement the following plan:

# L0 执行器实现计划

## Context

L0 执行层是 AI 指令到游戏命令的翻译层。`game_api.py` 已有完整的 HTTP 客户端（18个命令的便捷方法），`main.py` 已有 CLI 框架。L0 需要在此基础上增加：**AI 指令数据结构 + 参数校验 + 统一执行接口**，并扩展 CLI 支持 `l0` 子命令用于单条调试。

用户要求：先在命令行上将常用命令调试通过（单条），再做主循环。

## 要创建/修改的文件（2个）

### 1. `src/executor/l0_executor.py` — L0 执行器核心

**AI 指令数据结构**（Pydantic 模型，L1 LLM 输出的 JSON 直接反序列化）：

```python
class ActionType(str, Enum):
    MOVE_CITY = "MOVE_CITY"
    ATTACK_TARGET = "ATTACK_TARGET"
    SCOUT = "SCOUT"
    GARRISON_BUILDING = "GARRISON_BUILDING"
    INITIATE_RALLY = "INITIATE_RALLY"
    JOIN_RALLY = "JOIN_RALLY"
    RETREAT = "RETREAT"

class AIInstruction(BaseModel):
    action: ActionType
    uid: int
    target_x: int = 0
    target_y: int = 0
    target_uid: int = 0
    building_id: str = ""
    rally_id: str = ""
    troop_ids: list[str] = []
    prepare_time: int = 300
    reason: str = ""

class ExecutionResult(BaseModel):
    success: bool
    action: ActionType
    uid: int
    message: str = ""
    error: str = ""
    server_response: dict = {}
```

**L0Executor 类**: validate → execute → execute_batch

**execute 内部映射**: 复用 game_api.py 已有方法

**校验规则**: UID ∈ config, 坐标 0≤x<map_width, 各指令必填参数

### 2. `src/main.py` — 扩展 CLI 支持 `l0` 子命令

JSON 模式 + 简写模式双入口

> **Insight**
> 1. **Pydantic 双重利用** — `AIInstruction` 既是 L1 LLM JSON 输出的反序列化目标（`model_validate_json`），也承担参数校验。
> 2. **校验与执行分离** — `validate()` 可独立用于 dry-run 调试，`execute()` 内部先调 validate 再翻译执行，形成两层防护。
> 3. **复用 game_api 便捷方法** — L0 不直接拼底层命令字参数，而是委托给 `GameAPIClient` 已有的 `move_city()` 等方法，保持单一职责。

> **Insight**
> 1. **JSON 模式** 模拟真实的 L1→L0 链路——L1 LLM 输出 JSON，L0 用 `model_validate_json` 反序列化，端到端验证整个 pipeline。
> 2. **简写模式** 用位置参数快速调试单条命令，无需手写 JSON。
> 3. 检测第一个参数是否以 `{` 开头来自动区分两种模式，简洁无歧义。

**Files:** `src/executor/l0_executor.py`, `src/main.py`
