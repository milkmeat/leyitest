# 手指指引与 Quest 脚本的交互机制

## 背景

Quest workflow 加载 quest_scripts 中的多步脚本（如"将衣场升至2级"对应 10 步操作），但当教程手指指引连续出现时，手指 tap 能直接完成任务，脚本步骤不会执行。

## 优先级链

`_step_execute_quest`（quest_workflow.py）的处理优先级：

```
popup处理 → finger检测 → story_dialogue → main_city回城检测 → _match_quest_rule → action_buttons → primary_button
```

**finger 检测优先级高于 `_match_quest_rule`**，所以只要屏幕上有手指，脚本步骤就不会执行。

## 两层 finger 检测

1. **main.py 层**（auto_loop 步骤 2c）：在 `quest_workflow.step()` 之前检测 finger，检测到后直接 tap 并 `continue` 跳过当前 loop 剩余逻辑
2. **quest_workflow 层**（`_step_execute_quest` 第 656 行）：workflow step 内部也检测 finger，作为 EXECUTE_QUEST 阶段的最高优先级动作

## 实际执行时序示例

假设任务是"将衣场升至2级"，手指连续出现引导完成：

| Loop | Scene | 执行内容 | 说明 |
|------|-------|---------|------|
| L1 | main_city | main.py finger检测 → tap → fast-start workflow 到 EXECUTE_QUEST → `continue` | 跳过 workflow.step() |
| L2 | unknown | workflow.step() → _step_execute_quest → 检测到 finger → tap | finger 优先级 > _match_quest_rule，脚本不执行 |
| L3 | unknown | 同上，继续 follow finger | 脚本仍不执行 |
| L4 | main_city | _step_execute_quest → scene==main_city → 转 CHECK_COMPLETION | 回到主城 = 任务可能完成 |
| L5 | main_city | _step_check_completion → 读 quest bar → 任务文本变了 → IDLE | workflow 结束 |

**结果：10 步脚本虽然被 load 了，但一步都没执行。**

## 脚本何时真正执行

当 **没有手指指引** 且 scene 不是 main_city/popup/story_dialogue 时，`_match_quest_rule` 才会被调用，逐步执行脚本。典型场景：

- 教程手指只引导到某个界面，之后消失
- 需要在建筑面板上执行具体操作（如查找建筑、点击升级）
- 手指引导不完整，脚本补充剩余步骤

## 脚本重置机制

脚本不需要在 finger 完成任务后显式重置：

1. 回到 main_city → CHECK_COMPLETION 阶段
2. 读到新任务文本 → phase=IDLE，workflow 结束
3. 下次 `workflow.start()` → `_script_runner.reset()` 清掉旧脚本
4. 新任务匹配新 pattern → `_loaded_quest_pattern != pattern` → 重新 load 新脚本

## 注意事项

- `_loaded_quest_pattern` 是 pattern 正则字符串，不是任务文本。如果新旧任务匹配同一个 pattern（如"将衣场升至2级"和"将衣场升至3级"），pattern 相同，但 `start()` 时已 reset，所以不会有问题
- 如果脚本执行到一半手指突然出现，finger tap 接管后脚本状态可能脏了，但回到 main_city 后 workflow 会走 CHECK_COMPLETION → IDLE → reset，安全退出
