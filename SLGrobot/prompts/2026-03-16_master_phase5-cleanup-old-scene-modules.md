# Prompt Record

- Date: 2026-03-16 22:00
- Branch: master
- Commit: Phase 5: remove old scene modules replaced by Screen DOM architecture

---

### 1. Implement Phase 5 cleanup plan

Implement the following plan:

# Phase 5: 清理旧模块

## Context

Phase 4 已完成，v2 Screen DOM 架构已全面运行（DOM 构建、场景推断、Auto Handler、YAML 脚本）。部分旧模块仍被 import/实例化但已不再实际使用，需要清理以保持代码库精简。

**重要发现**：探索发现 progress.md 中 Phase 5 原计划的部分模块**仍在活跃使用**，不能删除：
- `brain/quest_script.py` — JSON quest 脚本执行系统仍在用（`cmd_quest`、`cmd_quest_test`）
- `vision/quest_bar_detector.py` — `StateTracker` 仍在调用
- `vision/grid_overlay.py` — `ActionRunner` fallback 坐标解析仍在用
- `brain/llm_planner.py` — 文件不存在（从未创建）

## 可安全删除的模块

| 模块 | 原因 |
|------|------|
| `scene/classifier.py` | 实例化但仅 `cmd_scene` 调用，DOM `infer_scene()` 已替代 |
| `scene/popup_filter.py` | 实例化但**零调用**（grep 确认 `popup_filter.` 无匹配） |
| `executor/action_validator.py` | 仅 line 748 调用，但功能简单（坐标边界检查+文字存在性检查），可内联或暂保留 |
| `scene/handlers/` | 仅剩 `__pycache__`，.py 文件已删 |

## 改动计划

1. 删除 `scene/classifier.py` + `scene/popup_filter.py`，清理所有引用
2. 删除整个 `scene/` 目录
3. 清理 `executor/action_validator.py`：保留 ActionValidator，移除 SceneClassifier 依赖
4. 更新 `cmd_scene` 使用 DOM scene 推断
5. 删除 `cmd_detect_finger_old`
6. 清理 test_vision.py
7. 更新 help 输出
8. 更新 progress.md

> **Insight**
> Phase 5 清理的核心思路：v2 Screen DOM 架构已经完全替代了旧的场景分类系统。SceneClassifier 基于模板匹配置信度判断场景，而新的 infer_scene() 基于 DOM 元素组合推断场景，信息更丰富、更准确。PopupFilter 的弹窗检测+关闭逻辑也被 PopupDetector + AutoHandler 优先级系统替代。
>
> 清理策略的关键判断：原计划删除 6 个模块，但实际探索发现其中 3 个仍有活跃调用链。先 grep 确认依赖关系，再动手删除。ActionValidator 中的 SceneClassifier 是典型的"签名中存在但方法内未调用"的死依赖。
>
> cmd_scene 的演进：旧版基于 SceneClassifier.classify() 的模板匹配置信度打分，新版直接使用 DOM infer_scene() 的规则推断。后者信息量更大（能区分 exit_dialog、story_dialogue 等细粒度场景），且保持了 CLI 调试与生产逻辑的一致性。

**Files:** `scene/classifier.py`, `scene/popup_filter.py`, `scene/__init__.py`, `executor/action_validator.py`, `main.py`, `test_vision.py`, `progress.md`
