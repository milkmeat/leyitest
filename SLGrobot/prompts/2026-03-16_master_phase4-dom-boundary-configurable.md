# Prompt Record

- Date: 2026-03-16 00:00
- Branch: master
- Commit: add configurable dom_top_y/dom_bottom_y to GameProfile, complete Phase 4

---

### 1. Implement Phase 4 收尾 plan

Implement the following plan:

# Phase 4 收尾计划

## Context

Phase 4 的大部分工作已在之前的开发中完成：
- `auto_priorities` 字段已在 `game_profile.py` 中实现，两个游戏的 `game.json` 已配置完毕
- `infer_scene()` 硬编码逻辑运行良好，用户决定跳过 `scene_rules` 数据驱动化
- 唯一剩余：`dom_top_y` / `dom_bottom_y` 可配置化 + 更新 progress.md

## 改动

### 1. GameProfile 添加区域边界字段 (`game_profile.py`)

在 `auto_priorities` 字段后添加：
```python
dom_top_y: int = 200       # top_bar 下界
dom_bottom_y: int = 1700   # bottom_bar 上界
```

在 `load_game_profile()` 中从 JSON 读取（缺省用默认值）：
```python
dom_top_y=data.get("dom_top_y", 200),
dom_bottom_y=data.get("dom_bottom_y", 1700),
```

### 2. ScreenDOMBuilder 使用 GameProfile 的边界值 (`vision/screen_dom.py`)

`ScreenDOMBuilder.__init__` 添加可选参数 `top_y` 和 `bottom_y`，替代硬编码 200/1700。

### 3. main.py 中传递参数

在创建 `ScreenDOMBuilder` 的地方，从 `game_profile` 传入 `top_y` / `bottom_y`。

### 4. 更新 progress.md

- 4.1 标记为完成（auto_priorities 已有，dom 边界已补）
- 4.2 标记为完成
- 4.3 标记为完成
- scene_rules 标注为 skipped
- Phase 4 整体标为 Done

> **Insight**
> **为什么要把 `dom_top_y` / `dom_bottom_y` 配置化？**
> - `ScreenDOMBuilder` 用这两个 Y 坐标把屏幕元素分到 `top_bar`（状态栏区域）、`center`（主交互区域）、`bottom_bar`（底部导航）三个区域
> - 不同游戏的 UI 布局不同（例如顶栏高度、底部按钮位置），硬编码 200/1700 不一定适合所有游戏
> - 放入 `GameProfile` 后，每个游戏可以在 `game.json` 中自定义边界，且有合理默认值保持向后兼容

> **Insight**
> - **向后兼容设计**：`dom_top_y` / `dom_bottom_y` 在 JSON 中缺省时使用 dataclass 默认值 200/1700，现有的 `game.json` 无需任何修改即可正常工作
> - **参数传递路径**：`game.json` → `load_game_profile()` → `GameProfile` → `ScreenDOMBuilder.__init__` → `_assign_regions()` 中的 `self.top_y` / `self.bottom_y`，无需改动 `main.py`，因为 `game_profile` 对象已经通过构造函数传入

**Files:** `game_profile.py`, `vision/screen_dom.py`, `progress.md`
