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

- [ ] **1.6 单元测试**
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

- [ ] **2.1 脚本加载器**
  - 从 `games/<id>/scripts/<name>.yaml` 读取脚本
  - YAML 解析 + 基本 schema 校验（必要字段检查）
  - 列出所有可用脚本

- [ ] **2.2 元素查找算法** (`find_element`)
  - 按 type（button/text/icon/red_dot/green_check/finger）匹配
  - 多匹配时按距离原始 pos 最近排序
  - 文字匹配支持子串包含

- [ ] **2.3 条件求值引擎** (`evaluate_condition`)
  - 支持 `exists` / `not_exists` / `scene` 条件
  - 支持 `all`（AND）/ `any`（OR）组合
  - 条件求值前自动截图 + 构建 DOM

- [ ] **2.4 ScriptRunner 核心** (`brain/script_runner.py`)
  - `tap` 动作：坐标直接点击 → 验证（target 消失？） → fallback 元素定位重试（最多 3 次）
  - `swipe` 动作：from → to，duration_ms
  - `wait` 动作：静态等待 N 秒
  - `wait_for` 动作：轮询 DOM 直到目标元素出现（timeout + poll_interval）
  - `if` 动作：条件求值 → 执行 then / else 分支（支持嵌套）
  - 执行日志：每步打印动作、坐标、结果
  - 错误处理：重试耗尽后抛异常并输出当前 DOM 快照

- [ ] **2.5 Script CLI 命令** (`main.py`)
  - `python main.py run <script_name>` — 执行脚本
  - `python main.py run <name> --dry` — 干跑模式（打印步骤，不执行）
  - `python main.py scripts` — 列出所有可用脚本

- [ ] **2.6 测试**
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

- [ ] **3.1 优先级匹配引擎** (`find_priority_match`)
  - 按 type 匹配（finger / icon / button / red_dot / green_check / text）
  - button 支持 `text_match`（正则）和 `color` 匹配
  - icon 支持 `name` 精确匹配
  - 返回第一个匹配的元素

- [ ] **3.2 AutoHandler 重写** (`brain/auto_handler.py`)
  - `__init__` 接收 `dom_builder` 和 `game_profile`
  - `get_action(dom) -> dict | None`：按场景查优先级表 → 匹配元素 → 返回 tap 动作
  - 无匹配时返回 None（循环等待）
  - 日志：每次决策记录场景、优先级命中项、元素坐标

- [ ] **3.3 Auto 循环重写** (`main.py` 中的 auto_loop)
  - 每次迭代：截图 → DOM → AutoHandler.get_action → 执行 → 等待
  - 支持 `--loops N` 限制循环次数
  - stuck 检测：连续 N 次 DOM 无变化 → 尝试 stuck_recovery

- [ ] **3.4 测试**
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

- [ ] **4.1 GameProfile 新字段** (`game_profile.py`)
  - `dom_top_y: int` — top_bar 下界（默认 200）
  - `dom_bottom_y: int` — bottom_bar 上界（默认 1700）
  - `scene_rules: list[dict]` — 场景识别规则（顺序匹配）
  - `auto_priorities: dict[str, list[dict]]` — 各场景点击优先级
  - 加载时从 game.json 读取，缺省用默认值

- [ ] **4.2 frozenisland game.json 更新**
  - 添加 `scene_rules`（popup / loading / main_city / world_map / hero / story_dialogue）
  - 添加 `auto_priorities`（popup / main_city / world_map / story_dialogue / loading / _default）
  - 可选：`dom_top_y`、`dom_bottom_y`（如果默认值不适用）

- [ ] **4.3 westgame2 game.json 更新**
  - 同 frozenisland，但适配 westgame2 的场景模板名和按钮文字
  - 包含 exit_dialog、shoot_mini_game 等特有场景

- [ ] **4.4 DOM 场景推断集成**
  - ScreenDOMBuilder 的 `_classify_scene` 使用 game_profile.scene_rules
  - 规则顺序匹配，首条命中即返回
  - 无命中时 fallback 到 "unknown"

- [ ] **4.5 测试**
  - 验证两个游戏的 game.json 可正常加载
  - 验证场景规则对各种 DOM 正确识别场景
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

- [ ] **5.1 删除旧文件**
  - `scene/classifier.py` → 由 DOM scene_rules 替代
  - `scene/popup_filter.py` → 由 popup_detector + auto_handler 替代
  - `brain/quest_script.py` → 由 brain/script_runner.py 替代
  - `brain/llm_planner.py` → 不再需要 LLM
  - `vision/quest_bar_detector.py` → DOM 文字/指示器检测覆盖
  - `vision/grid_overlay.py` → LLM grid 不再需要

- [ ] **5.2 清理 scene/ 目录**
  - 如果 `scene/` 下只剩 `__init__.py`，考虑整个删除
  - 或将任何仍有价值的工具函数迁移到 vision/ 或 brain/

- [ ] **5.3 清理 imports**
  - 全局搜索所有 `from scene.` / `from brain.quest_script` / `from brain.llm_planner` / `from vision.grid_overlay` 的引用
  - 更新或删除这些 import
  - 更新 `__init__.py` 导出列表

- [ ] **5.4 清理 executor/**
  - `ActionRunner` 简化：移除 grid_overlay 相关逻辑
  - `ActionValidator` 简化：移除旧 action type 校验（如 navigate 等，如果不再使用）
  - 评估 executor/ 是否仍需要独立存在，或可合并到 script_runner

- [ ] **5.5 清理 main.py**
  - 移除旧 CLI 命令：`scene`、`detect_finger`、`detect_close_x`、`quest`、`quest_rules`、`quest_test`
  - 更新 `help` 输出
  - GameBot.__init__ 中移除对已删除模块的初始化

- [ ] **5.6 清理配置**
  - `config.py`：移除 `GRID_COLS`、`GRID_ROWS` 等不再使用的常量
  - `game.json`：移除旧 `quest_scripts` section（如已被 scripts/ 目录替代）

- [ ] **5.7 验证**
  - 运行 `python -c "import main"` 确认无 import 错误
  - 运行 `python main.py dom` 确认功能正常
  - 运行 `python main.py run <script>` 确认功能正常
  - 运行 `python main.py auto --loops 5` 确认功能正常

### 验收标准

1. 所有列出的旧文件已删除
2. 全项目无 broken import（`python -c "import main"` 无报错）
3. `dom`、`run`、`scripts`、`auto` 四个核心命令正常工作
4. 无残留的死代码引用（grep 搜索确认）
5. `python main.py help` 输出反映新的命令集

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

## Progress Summary

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Phase 1: DOM Builder | In progress | 2026-03-14 | — |
| Phase 2: Script Runner | Not started | — | — |
| Phase 3: Auto Handler | Not started | — | — |
| Phase 4: Game Config | Not started | — | — |
| Phase 5: Cleanup | Not started | — | — |
| Phase 6: Integration | Not started | — | — |
