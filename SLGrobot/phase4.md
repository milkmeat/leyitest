# Phase 4: LLM Integration - "Make It Think Strategically"

## 目标

将 LLM 大模型接入游戏决策循环，实现三层决策架构的完整闭环：
1. **战略层 (Strategic)** - LLM 每 ~30 分钟规划长期策略
2. **战术层 (Tactical)** - 本地规则引擎分解任务为操作序列
3. **执行层 (Execution)** - CV + ADB 毫秒级截图→识别→点击

同时构建完整的执行管线：**验证 → 执行 → 确认**。

---

## 新增文件

| 文件 | 职责 |
|------|------|
| `model_presets.py` | 模型预设系统，支持多 LLM 提供商切换（智谱 / Anthropic / DeepSeek 等） |
| `brain/llm_planner.py` | LLM 战略规划器，发送网格标注截图 + 状态摘要，解析 JSON 响应为任务列表 |
| `executor/__init__.py` | 执行器包初始化 |
| `executor/action_validator.py` | 执行前验证：目标元素是否存在、坐标是否越界、场景是否匹配 |
| `executor/action_runner.py` | 动作执行器：将验证后的 action dict 翻译为 ADB 命令 |
| `executor/result_checker.py` | 执行后确认：截图对比验证操作效果（场景变化、元素消失/出现） |
| `test_llm.py` | Phase 4 测试套件（11 离线 + 2 在线测试） |

## 修改文件

| 文件 | 变更 |
|------|------|
| `config.py` | 从 `model_presets.py` 加载 LLM 配置，新增 `LLM_PROVIDER` / `LLM_BASE_URL` / `LLM_VISION_MODEL` 等字段 |
| `main.py` | 集成三层决策循环：LLM 战略层 + 执行验证管线 + `llm` CLI 命令 |
| `requirements.txt` | 新增 `anthropic`、`openai` 依赖 |

---

## 架构设计

### 三层决策循环（auto_loop）

```
screenshot → classify scene →
  popup   → auto-close → continue
  loading → wait → continue
  unknown → LLM analyze_unknown_scene → execute → continue
  other   → update game_state →
    有待执行任务 → rule_engine.plan(task) → validate → execute → verify
    无任务 + LLM 到期 → llm_planner.get_plan() → 加入队列 → continue
    无任务 → auto_handler.get_actions() → execute
  → persist state → sleep → repeat
```

### 执行管线

每个 action 都经过三阶段处理：

```
ActionValidator.validate()  →  ActionRunner.execute()  →  ResultChecker.check()
     预验证                        ADB 执行                  截图确认
```

- **Validator**: 拒绝坐标越界、目标不存在的操作
- **Runner**: 支持 text 定位 → template/OCR 查找 → grid 回退
- **Checker**: 对比执行前后截图，确认场景变化或元素状态变化

### 多模型提供商支持

通过 `model_presets.py` 实现即插即用的模型切换：

```python
# model_presets.py
PRESETS = {
    "zhipu": {
        "provider": "openai_compatible",
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "model_name": "GLM-4.6",       # 文本模型
        "vision_model": "GLM-4.6V",    # 视觉模型
        ...
    },
    "anthropic": {
        "provider": "anthropic",
        "model_name": "claude-sonnet-4-20250514",
        ...
    },
}
ACTIVE_PRESET = "zhipu"  # 修改此处切换提供商
```

`LLMPlanner` 内部根据 `provider` 字段自动分发到对应的 SDK 调用：
- `"anthropic"` → Anthropic 原生 SDK（`anthropic.Anthropic`）
- `"openai_compatible"` → OpenAI SDK（`openai.OpenAI`），兼容智谱、DeepSeek 等

### LLM 输入/输出格式

**输入**: 网格标注截图（A1-H6, 缩放至 1024px）+ 游戏状态摘要文本

**输出**（强制 JSON）:
```json
{
    "reasoning": "Castle upgrade requires barracks at level 12 first",
    "tasks": [
        {"name": "close_popup", "priority": 10, "params": {}},
        {"name": "upgrade_building", "priority": 8, "params": {"building_name": "barracks"}},
        {"name": "custom", "priority": 5, "params": {}, "actions": [
            {"type": "tap", "target_text": "Upgrade", "fallback_grid": "C4"},
            {"type": "wait", "seconds": 1}
        ]}
    ]
}
```

---

## 测试结果

### 离线测试（11/11 通过）

```
Test: LLMPlanner initialization                    PASS
Test: Multi-provider initialization                 PASS
Test: should_consult logic                          PASS (4 sub-tests)
Test: Screenshot preparation                        PASS (576x1024)
Test: Parse strategic plan JSON                     PASS (3 sub-tests)
Test: Parse scene analysis JSON                     PASS
Test: ActionValidator                               PASS (7 sub-tests)
Test: ActionRunner class                            PASS
Test: ResultChecker class                           PASS
Test: JSON extraction edge cases                    PASS (3 sub-tests)
Test: Model presets system                          PASS (3 sub-tests)
```

### 在线测试（2/2 通过）

**测试 1 - 合成截图（纯绿色背景 + 网格）**:
- 提供商: `openai_compatible` / `GLM-4.6V`
- 耗时: 38.3s, 输入 1145 tokens, 输出 1326 tokens
- LLM 返回 5 个任务:
  ```
  [10] claim_rewards       - 领取奖励（最高优先级）
  [ 9] collect_daily       - 每日签到
  [ 8] upgrade_building    - 升级兵营
  [ 7] train_troops        - 训练部队
  [ 6] check_mail          - 查看邮件
  ```
- LLM 推理: "玩家资源充足，优先领取奖励和每日签到，然后升级兵营、训练部队"

**测试 2 - 真实模拟器截图（1080x1920 游戏画面）**:
- 从 Nox 模拟器抓取实际游戏画面
- 耗时: 38.3s, 输入 1145 tokens, 输出 1281 tokens
- LLM 正确识别出屏幕上有弹窗，返回 3 个任务:
  ```
  [10] close_popup         - 关闭公会弹窗（最高优先级）
  [ 9] claim_rewards       - 领取 830 金奖励
  [ 8] upgrade_building    - 升级兵营
  ```
- LLM 推理: "公会弹窗阻挡了操作，最高优先级关闭它。然后领取 830 金奖励，再升级兵营"

---

## CLI 新增命令

| 命令 | 说明 |
|------|------|
| `llm` | 手动触发 LLM 战略咨询，打印返回的任务计划 |

`status` 命令现在也会显示 `Last LLM consult` 时间。

---

## 运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 离线测试
python test_llm.py

# 在线测试（需要 API key 配置在 model_presets.py）
python test_llm.py --live

# 启动完整三层决策循环
python main.py --auto

# 手动触发 LLM 咨询
python main.py llm
```

## 切换 LLM 提供商

编辑 `model_presets.py`，修改 `ACTIVE_PRESET`:
```python
ACTIVE_PRESET = "zhipu"      # 智谱 GLM-4.6V
ACTIVE_PRESET = "anthropic"  # Claude Sonnet
```

或添加新的预设到 `PRESETS` 字典，任何 OpenAI 兼容 API 均可直接使用。
