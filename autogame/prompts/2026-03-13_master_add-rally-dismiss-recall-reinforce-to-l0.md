# Prompt Record

- Date: 2026-03-13 22:00
- Branch: master
- Commit: add RALLY_DISMISS and RECALL_REINFORCE ActionTypes to L0 executor and L1 prompt

---

### 1. Implement L0 ActionType completion plan

Implement the following plan:

# L0 ActionType 补全计划

## Context

L0 执行器当前只有 7 种 ActionType，但 game_api.py 已支持 rally_dismiss 和 recall_reinforce。
这导致 LLM 无法通过 L0 下达"解散集结"或"撤回增援部队"的指令，形成功能断层。

## 需新增的 ActionType

| ActionType | game_api 方法 | 用途 |
|------------|--------------|------|
| `RALLY_DISMISS` | `rally_dismiss(uid, unique_id)` | 队长解散集结 |
| `RECALL_REINFORCE` | `recall_reinforce(uid, unique_id)` | 撤回增援/集结中的部队 |

**不需要**新增的：
- `attack_city`（简化攻击）— 已被 ATTACK_TARGET 覆盖
- GM/联盟/AVA 命令 — 属于准备阶段操作，不由 L1 LLM 决策

## 修改文件清单

### 1. `src/executor/l0_executor.py`

**ActionType 枚举** — 新增 2 项：
```python
RALLY_DISMISS = "RALLY_DISMISS"
RECALL_REINFORCE = "RECALL_REINFORCE"
```

**AIInstruction 模型** — 新增字段：
```python
reinforce_id: str = ""   # 增援部队 unique_id（RECALL_REINFORCE 用）
```
注：rally_dismiss 复用已有的 `rally_id` 字段

**validate()** — 新增校验：
- RALLY_DISMISS: `rally_id` 非空
- RECALL_REINFORCE: `reinforce_id` 非空

**_dispatch()** — 新增分发：
- RALLY_DISMISS → `self.client.rally_dismiss(uid, rally_id)`
- RECALL_REINFORCE → `self.client.recall_reinforce(uid, reinforce_id)`

**_success_message()** — 新增消息

### 2. `src/ai/prompts/l1_system.txt`

在"可用动作"区域新增 2 个动作说明，总计 9 种：

```
## RALLY_DISMISS — 解散集结
队长取消/解散已发起的集结。
必填: uid, rally_id

## RECALL_REINFORCE — 撤回增援
撤回在集结或建筑驻防中的本方部队。
必填: uid, reinforce_id
```

更新 `# 字段说明` 增加 `reinforce_id` 字段描述。

> **Plan**
> The plan was provided directly by the user as a structured implementation plan covering: ActionType enum additions, AIInstruction model field, validate() branches, _dispatch() routing, _success_message() entries, and L1 prompt updates.

> **Insight**
> 1. RALLY_DISMISS 和 JOIN_RALLY 复用 `rally_id` 字段 — 两个操作都以集结 ID 为目标，通过 action 枚举值区分语义，避免字段膨胀。
> 2. RECALL_REINFORCE 需要独立的 `reinforce_id` 字段 — 与 RETREAT 的 `troop_ids`（列表）不同，增援撤回操作的粒度是单个部队的 unique_id，且 API 签名也不同。
> 3. 新增动作不需要坐标校验 — needs_coords 集合无需修改，因为解散集结和撤回增援都是通过 ID 标识目标，不涉及地图坐标。

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system.txt`
