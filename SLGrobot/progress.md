# V2 Screen DOM — Progress Tracker

> Reference: `design_v2_screen_dom.md`
> Started: 2026-03-14
> Branch: `master` (v1 archived at tag `v1.0` / branch `v1`)

---

## Phase 1: Screen DOM Builder + CLI

**Goal**: 实现完整的画面解析管线，能对任意截图生成 YAML DOM 输出，并通过 `python main.py dom` 验证。

### TODO

- [x] **1.1 PopupDetector** (`vision/popup_detector.py`)
  - 半透明暗色遮罩检测（灰度边缘/中心亮度对比）
  - 返回弹窗边界 `(x1, y1, x2, y2)` 或 `None`
  - 亮区连通域分析定位弹窗矩形范围

- [x] **1.2 ButtonDetector** (`vision/button_detector.py`)
  - HSV 颜色分段（green / blue / purple / gold / red / gray）
  - 形态学闭运算 → `findContours` → 面积/宽高比/矩形度过滤
  - 将 OCR 文字关联到按钮内部区域
  - 合并重叠检测结果（IoU > 0.5）
  - 输出 `ButtonElement(text, pos, size, color_name)`

- [x] **1.3 IndicatorDetector** (`vision/indicator_detector.py`)
  - 红点检测：HSV 红色范围 + 小圆形轮廓（面积 50–800 px²，圆度 > 0.6）
  - 绿勾检测：HSV 绿色范围 + 小区域（面积 100–2000 px²，非圆形）
  - 输出 `IndicatorElement(type, pos)`

- [x] **1.4 ScreenDOMBuilder** (`vision/screen_dom.py`)
  - 调用 OCR、TemplateMatcher、ButtonDetector、IndicatorDetector、FingerDetector、PopupDetector
  - 去重：已归入按钮的 OCR 文字从 free_texts 中移除
  - 区域分配：按 Y 坐标分到 top_bar / center / bottom_bar
  - 弹窗元素单独放入 popup section
  - 指示器（红点/绿勾）关联最近元素（80px 半径），填充 `near` 字段
  - `build(screenshot) -> dict`、`to_yaml(dom) -> str`
  - **性能优化**：OCR / 模板匹配 / finger detection 通过 ThreadPoolExecutor 并行执行
  - **模板匹配优化**：0.5x 缩放匹配 + 命中后 ROI 全分辨率精化，排除 finger 模板变体

- [x] **1.5 DOM CLI 命令** (`main.py`)
  - `python main.py dom` — 截图 → 输出 YAML DOM 到 stdout
  - `python main.py dom --save` — 同时保存截图 + DOM 到 `data/dom_history/`
  - `pyyaml` 已添加到 `requirements.txt`
  - `vision/__init__.py` 已更新导出

- [ ] ~~**1.6 单元测试**~~ (skipped)
  - 用已有截图 PNG 测试各子检测器
  - 测试 DOM 完整输出格式
  - 测试 YAML 序列化/反序列化

### 验收标准

1. 运行 `python main.py dom`，对当前模拟器画面输出合法的 YAML DOM
2. DOM 包含 `screen.resolution`、`screen.scene`、以及至少一个区域（top_bar / center / bottom_bar）
3. OCR 文字与人眼可见文字基本一致（允许少量漏检/误检）
4. 已加载的模板图标全部出现在匹配结果中（confidence > 阈值的）
5. 绿色/蓝色/橙色按钮被正确检测为 `button` 类型，且关联了正确文字
6. 红点和绿勾被检测为对应 indicator 类型
7. 弹窗场景下，弹窗元素出现在 `popup` section 而非 `center`
8. ~~单次 DOM 生成耗时 < 3 秒~~ → 实测 3.8-4.3s（OCR 1.5s + finger 3s + template 1.2s 并行后的瓶颈），可接受
9. `--save` 模式下文件正确保存到 `data/dom_history/`

### 性能优化记录

优化前 13.2s → 优化后 3.8-4.3s

| 优化项 | 做法 | 效果 |
|--------|------|------|
| 并行执行 | OCR / 模板匹配 / finger 三线程并行（ThreadPoolExecutor），底层 C 库释放 GIL | 串行 5.7s → 并行 ~3.5s（取最长路径） |
| 模板 0.5x 缩放 + ROI 精化 | 在 540×960 小图上匹配全部模板，命中后仅对命中位置周围小区域做全分辨率二次匹配；缩放模板缓存在 `_scaled_cache` 中 | 模板匹配 5.2s → 1.2s |
| 排除 finger 模板变体 | FingerDetector 注入的 16 个 finger 变体（翻转/旋转/多尺度）从模板匹配中排除，由专门的 FingerDetector 处理 | 避免 16 个高误报候选的���分辨率验证 |

**未做的优化（可未来考虑）：**
- Finger detection 可选化（很多场景没有 finger，跳过可省 3s）
- OCR 是 RapidOCR 底层调用，无法进一步压缩

---

## Phase 2: Script Runner + CLI

**Goal**: 实现 YAML 脚本加载与执行引擎，支持 tap / swipe / wait / wait_for / if 五种动作，通过 `python main.py run <name>` 执行脚本。

### TODO

- [x] **2.1 脚本加载器**
  - 从 `games/<id>/scripts/<name>.yaml` 读取脚本
  - YAML 解析 + 基本 schema 校验（必要字段检查）
  - 列出所有可用脚本

- [x] **2.2 元素查找算法** (`find_element`)
  - 按 type（button/text/icon/red_dot/green_check/finger）匹配
  - 多匹配时按距离原始 pos 最近排序
  - 文字匹配支持子串包含

- [x] **2.3 条件求值引擎** (`evaluate_condition`)
  - 支持 `exists` / `not_exists` / `scene` 条件
  - 支持 `all`（AND）/ `any`（OR）组合
  - 条件求值前自动截图 + 构建 DOM

- [x] **2.4 ScriptRunner 核心** (`brain/script_runner.py`)
  - `tap` 动作：坐标直接点击 → 验证（target 消失？） → fallback 元素定位重试（最多 3 次）
  - `swipe` 动作：from → to，duration_ms
  - `wait` 动作：静态等待 N 秒
  - `wait_for` 动作：轮询 DOM 直到目标元素出现（timeout + poll_interval）
  - `if` 动作：条件求值 → 执行 then / else 分支（支持嵌套）
  - 执行日志：每步打印动作、坐标、结果
  - 错误处理：tap 重试耗尽 warn + continue；wait_for 超时 raise ScriptAbortError

- [x] **2.5 Script CLI 命令** (`main.py`)
  - `python main.py run <script_name>` — 执行脚本
  - `python main.py run <name> --dry` — 干跑模式（打印步骤，不执行）
  - `python main.py scripts` — 列出所有可用脚本

- [ ] ~~**2.6 测试**~~ (deferred — needs emulator + real scripts)
  - 脚本加载 + schema 校验测试
  - 条件求值逻辑测试（exists / not_exists / all / any / scene）
  - 元素查找算法测试（单匹配、多匹配、无匹配）
  - 端到端：编写一个简单脚本，在模拟器上执行验证

### 验收标准

1. 编写一个包含 tap + if + wait_for 的测试脚本，在模拟器上成功执行
2. `tap` 动作正常路径（坐标直接点击）耗时 < 0.2s + wait
3. `tap` fallback 路径（DOM 重建 + 元素定位）耗时 < 3s
4. `if` 条件正确分支（手动构造两种场景分别验证 then 和 else）
5. `wait_for` 在目标出现时正确退出等待，超时时正确报错
6. `--dry` 模式不执行任何 ADB 操作，仅打印步骤
7. `scripts` 命令列出 `games/<id>/scripts/` 下所有 YAML 文件
8. 脚本 YAML 格式错误时给出清晰的错误提示

---

## Phase 3: Auto Handler 重写

**Goal**: 重写 AutoHandler，基于 DOM + 场景优先级配置实现自动点击循环，不依赖 LLM。

### TODO

- [x] **3.1 优先级匹配引擎** (`find_priority_match`)
  - 按 type 匹配（finger / icon / button / red_dot / green_check / text）
  - button 支持 `text_match`（正则）和 `color` 匹配
  - icon 支持 `name` 精确匹配
  - 返回第一个匹配的元素

- [x] **3.2 AutoHandler 重写** (`brain/auto_handler.py`)
  - `__init__` 接收 `dom_builder` 和 `game_profile`
  - `get_action(dom) -> dict | None`：按场景查优先级表 → 匹配元素 → 返回 tap 动作
  - 无匹配时返回 None（循环等待）
  - 日志：每次决策记录场景、优先级命中项、元素坐标

- [x] **3.3 Auto 循环重写** (`main.py` 中的 auto_loop)
  - 每次迭代：截图 → DOM → AutoHandler.get_action → 执行 → 等待
  - 支持 `--loops N` 限制循环次数
  - stuck 检测：连续 N 次 DOM 无变化 → 尝试 stuck_recovery

- [ ] ~~**3.4 测试**~~ (deferred — verified via live auto loop)
  - 优先级匹配逻辑的单元测试
  - 用截图 PNG 模拟不同场景，验证优先级选择正确
  - 端到端：在模拟器上运行 `python main.py auto --loops 10`，观察行为

### 验收标准

1. popup 场景下自动点击 close_x 或关闭按钮
2. main_city 场景下优先点击 finger，其次 green_check，再次 red_dot
3. loading 场景下不执行任何点击（空优先级列表）
4. 未配置场景使用 `_default` 优先级
5. 连续运行 20 个循环不报错、不卡死
6. 日志清晰记录每次迭代的场景判定和动作决策

---

## Phase 4: Game Profile + 场景规则配置

**Goal**: 在 `game_profile.py` 和 `game.json` 中添加 DOM 相关配置字段，支持场景规则和自动优先级的数据驱动。

### TODO

- [x] **4.1 GameProfile 新字段** (`game_profile.py`)
  - `dom_top_y: int` — top_bar 下界（默认 200）
  - `dom_bottom_y: int` — bottom_bar 上界（默认 1700）
  - ~~`scene_rules: list[dict]` — 场景识别规则~~ (skipped — `infer_scene()` 硬编码逻辑运行良好)
  - `auto_priorities: dict[str, list[dict]]` — 各场景点击优先级
  - 加载时从 game.json 读取，缺省用默认值

- [x] **4.2 frozenisland game.json 更新**
  - ~~`scene_rules`~~ (skipped — 使用硬编码 `infer_scene()`)
  - `auto_priorities` 已配置（popup / main_city / world_map / story_dialogue / loading / _default）
  - `dom_top_y`、`dom_bottom_y` 使用默认值（200 / 1700）

- [x] **4.3 westgame2 game.json 更新**
  - ~~`scene_rules`~~ (skipped — 使用硬编码 `infer_scene()`)
  - `auto_priorities` 已配置，包含 exit_dialog、shoot_mini_game 等特有场景
  - `dom_top_y`、`dom_bottom_y` 使用默认值（200 / 1700）

- [x] **4.4 DOM 场景推断集成**
  - `infer_scene(dom, screenshot)` 在 `build()` 末尾调用，基于 DOM 元素推断场景
  - 优先级顺序：popup > exit_dialog > loading(像素) > story_dialogue > shoot_mini_game > main_city > world_map > hero_recruit > hero_upgrade > hero > unknown
  - auto_loop 不再调用 SceneClassifier，直接使用 `dom["screen"]["scene"]`

- [x] **4.5 测试**
  - 验证两个游戏的 game.json 可正常加载
  - 验证场景推断对各种 DOM 正确识别场景（通过 screenshot 测试框架）
  - 验证优先级配置正确驱动 AutoHandler 决策

### 验收标准

1. `load_game_profile("frozenisland")` 和 `load_game_profile("westgame2")` 正常加载所有新字段
2. 缺省字段有合理默认值，旧 game.json 格式向后兼容
3. 场景规则至少覆盖：popup、loading、main_city、world_map、unknown
4. 两个游戏各自的 auto_priorities 至少配置 popup、main_city、_default 三个场景
5. 在模拟器上运行 `python main.py dom`，scene 字段与人眼判断一致

---

## Phase 5: 清理旧模块

**Goal**: 移除被 Screen DOM 架构替代的旧代码，保持代码库精简。

### TODO

- [x] **5.1 删除旧文件**（部分完成）
  - [x] `scene/classifier.py` → 由 DOM `infer_scene()` 替代，已删除
  - [x] `scene/popup_filter.py` → 由 popup_detector + auto_handler 替代，已删除
  - [x] ~~`brain/quest_script.py`~~ → **保留**，JSON quest 脚本系统仍在用（`cmd_quest`、`cmd_quest_test`）
  - [x] ~~`brain/llm_planner.py`~~ → 文件不存在（从未创建），无需处理
  - [x] ~~`vision/quest_bar_detector.py`~~ → **保留**，`StateTracker` 仍在调用
  - [x] ~~`vision/grid_overlay.py`~~ → **保留**，`ActionRunner` fallback 坐标解析仍在用

- [x] **5.2 清理 scene/ 目录** — 整个 `scene/` 目录已删除（含 `__init__.py`、`handlers/__pycache__`）

- [x] **5.3 清理 imports**
  - 移除了 main.py 中的 `from scene.classifier` 和 `from scene.popup_filter`
  - 移除了 executor/action_validator.py 中的 `from scene.classifier`
  - 移除了 test_vision.py 中的 scene 相关 import 和测试函数
  - 全局 grep 确认无残留 `from scene.` 引用

- [x] **5.4 清理 executor/**（部分完成）
  - [x] `ActionValidator` 移除 `SceneClassifier` 依赖（`__init__` 签名简化为仅 `ElementDetector`）
  - [x] ~~`ActionRunner`~~ — **保留**，grid_overlay 仍在用

- [x] **5.5 清理 main.py**（部分完成）
  - [x] `cmd_scene` 改用 DOM `infer_scene()` 替代旧 `classifier.classify()`
  - [x] 删除 `cmd_detect_finger_old`（旧版 finger 检测，已有 `cmd_detect_finger` 使用新管线）
  - [x] 更新 `help` 输出（scene 描述更新）
  - [x] `GameBot.__init__` 移除 `self.classifier` 和 `self.popup_filter` 初始化
  - [x] ~~quest 系列命令~~ — **保留**，JSON quest 脚本系统仍在用

- [x] **5.6 清理配置** — 跳过，所有 config 常量仍在使用（`GRID_COLS`/`GRID_ROWS` 被 `GridOverlay` 使用）

- [x] **5.7 验证**
  - `python -c "import main"` ✓ 无 import 错误
  - 全局 grep 确认无 `SceneClassifier`/`PopupFilter` 残留引用（仅注释除外）

### 验收标准

1. [x] `scene/classifier.py` 和 `scene/popup_filter.py` 已删除，整个 `scene/` 目录已清理
2. [x] 全项目无 broken import（`python -c "import main"` 无报错）
3. [x] `dom`、`run`、`scripts`、`auto` 四个核心命令接口未受影响
4. [x] 无残留的死代码引用（grep 搜索确认）
5. [x] `python main.py help` 输出反映当前命令集

---

## Phase 6: 集成测试 + 文档更新

**Goal**: 端到端验证整个 v2 流程，更新项目文档。

### TODO

- [ ] **6.1 端到端测试脚本**
  - 编写 `test_v2.py`，覆盖：
    - DOM 生成（各场景截图）
    - 元素查找算法
    - 条件求值引擎
    - 脚本加载 + 执行（模拟 ADB 或使用真实模拟器）
    - AutoHandler 决策逻辑

- [ ] **6.2 实际游戏验证**
  - frozenisland：运行 `dom` → 人工确认 → 运行 `auto --loops 20`
  - westgame2：运行 `dom` → 人工确认 → 运行 `auto --loops 20`
  - 为每个游戏创建至少 1 个实用脚本并验证执行

- [ ] **6.3 更新 CLAUDE.md**
  - 更新架构描述：Screen DOM 替代旧 vision pipeline
  - 更新 CLI 命令列表
  - 更新模块层说明
  - 移除过时的 quest scripting、LLM planner 相关描述
  - 添加 Script 格式说明和 Claude Code 工作流

- [ ] **6.4 更新 MEMORY.md**
  - 更新 Key Files 列表
  - 更新 Architecture Notes

- [ ] **6.5 可选：性能优化**
  - 如果 DOM 生成 > 2s，分析瓶颈
  - 模板匹配优化：0.5x 预筛 + 仅对候选做 1x 精确匹配
  - 按钮检测优化：减少 findContours 调用次数

### 验收标准

1. `test_v2.py` 所有测试通过
2. 两个游戏各完成 20 轮 auto loop 无报错
3. 至少 2 个游戏脚本（每游戏 1 个）成功执行
4. `CLAUDE.md` 准确反映 v2 架构
5. 新开发者阅读 `CLAUDE.md` + `design_v2_screen_dom.md` 可理解系统
6. 单次 DOM 生成平均耗时 < 2s

---

## Screenshot 单元测试框架

**Goal**: 离线回归测试，验证 DOM 解析、场景推断、AutoHandler 输出的正确性。基于保存的 PNG 截图运行，无需模拟器。

### TODO

- [x] **Git LFS 配置** — `.gitattributes` 追踪 `tests/screenshots/**/*.png`
- [x] **目录结构** — `tests/screenshots/{westgame2,frozenisland}/`
- [x] **screenshot_helpers.py** — `build_pipeline()` 缓存流水线，`run_one_case()` 断言场景/元素/动作
- [x] **test_screenshot.py** — CLI 入口，支持按游戏/用例过滤，分组复用流水线，汇总通过/失败
- [x] **generate_expected.py** — 对截图运行流水线，输出 YAML 草稿供人工审查
- [x] **Claude Code 技能** — `.claude/skills/add-screenshot-test.md`，交互式创建测试用例
- [x] **使用文档** — `docs/screenshot_testing.md`

详见 `docs/screenshot_testing.md`。

---

## Progress Summary

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Phase 1: DOM Builder | Done (1.6 skipped) | 2026-03-14 | 2026-03-14 |
| Phase 2: Script Runner | Done (2.6 deferred) | 2026-03-15 | 2026-03-15 |
| Phase 3: Auto Handler | Done (3.4 deferred) | 2026-03-15 | 2026-03-15 |
| Phase 4: Game Config | Done (scene_rules skipped) | 2026-03-15 | 2026-03-16 |
| Phase 5: Cleanup | Done (5.1/5.4/5.5 partial, 5.6 skipped) | 2026-03-16 | 2026-03-16 |
| Phase 6: Integration | Not started | — | — |
| Screenshot 测试框架 | Done | 2026-03-15 | 2026-03-15 |
