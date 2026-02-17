# Workflow 架构设计

## 概念

Workflow 是与 TaskQueue 平级的独立概念，用于管理跨多个 auto_loop 迭代、有条件分支的复杂流程。

**命名约定：** 游戏内的"任务"统一用 **quest**（quest_bar, current_quest 等），与系统内部的 task（TaskQueue, Task）区分。

## Workflow 与 TaskQueue 的区别

| | TaskQueue | Workflow |
|---|---|---|
| 执行模型 | 单迭代完成：取出 → plan → execute → done | 跨迭代状态机：每次 step() 推进一步 |
| 并发 | 队列中可堆积多个 task | 同一时间只能有一个活跃 workflow |
| 来源 | LLM 生成或手动添加 | auto_loop 空闲时自动启动，或 CLI 手动启动 |
| 状态 | pending/running/done/failed | 状态机 phase（如 IDLE → EXECUTE → VERIFY） |
| CLI 操作 | `task <name> [priority]` — 加入队列 | `workflow start <name>` / `workflow stop` / `workflow status` |

## auto_loop 决策层优先级

```
popup/loading         → 现有处理
Workflow 活跃         → workflow.step() 返回 actions    ← 新增
TaskQueue 有任务      → rule_engine.plan() 返回 actions  ← 现有
LLM 咨询              → llm_planner 生成任务加入 queue   ← 现有
空闲 + 可启动 workflow → 启动 Workflow                   ← 新增
空闲                  → auto_handler                     ← 现有
```

Workflow 活跃时优先执行；空闲时 TaskQueue 正常工作。两者互不干扰。

## Workflow 基础接口

每个具体 Workflow 需实现以下接口：

- `name: str` — workflow 名称标识
- `phase: str` — 当前阶段
- `is_active() -> bool` — 是否正在运行（phase != IDLE）
- `start()` — 启动 workflow
- `abort()` — 中止并重置到 IDLE
- `step(screenshot, scene) -> list[dict]` — 每次 auto_loop 调用，返回当前阶段的 actions

## 状态机实现模式

状态和转移逻辑定义在具体 Workflow 类内部（如 `brain/quest_workflow.py`），不抽到外部配置，因为每个 phase 的处理逻辑与转移条件紧耦合。

```python
class SomeWorkflow:
    IDLE = "idle"
    STEP_A = "step_a"
    STEP_B = "step_b"

    def step(self, screenshot, scene) -> list[dict]:
        handler = getattr(self, f"_step_{self.phase}", None)
        return handler(screenshot, scene) if handler else []

    def _step_step_a(self, screenshot, scene):
        # 执行逻辑 + 转移条件
        if some_condition:
            self.phase = self.STEP_B
        return [{"type": "tap", ...}]
```

## WorkflowManager（多 workflow 时引入）

同一时间只能有一个活跃 workflow。如果未来有多种 workflow，通过 `WorkflowManager` 统一管理：

```python
class WorkflowManager:
    active: Workflow | None = None

    def start(self, workflow):
        if self.active and self.active.is_active():
            raise RuntimeError(f"'{self.active.name}' is running, stop it first")
        self.active = workflow
        workflow.start()

    def stop(self):
        if self.active:
            self.active.abort()
            self.active = None

    def step(self, screenshot, scene) -> list[dict]:
        if self.active and self.active.is_active():
            return self.active.step(screenshot, scene)
        self.active = None
        return []
```

auto_loop 只与 manager 交互，不直接引用具体 workflow。

## 已有 / 计划中的 Workflow

| Workflow | 文件 | 设计文档 | 状态 |
|----------|------|----------|------|
| complete_current_quest | `brain/quest_workflow.py` | [workflow_complete_current_quest.md](workflow_complete_current_quest.md) | 设计中 |
