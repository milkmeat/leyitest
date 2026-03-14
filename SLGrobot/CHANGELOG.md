# SLGrobot v1 开发总结

SLGrobot 第一版开发完成。本文档总结从项目启动到 v1 完成的所有工作。

---

## 项目概况

- **总提交数**: 201 次
- **代码文件**: 35+ Python 源文件，跨 7 个模块层
- **支持游戏**: 2 款 — Frozen Island Pro (`frozenisland`)、West Game 2 (`westgame2`)
- **模板库**: 50+ 个 PNG 模板（按钮、图标、导航栏、场景、弹窗）
- **Quest 脚本**: 6 个预定义任务脚本（westgame2）
- **测试**: 5 个测试文件（test_phase1, test_vision, test_state, test_quest_script, test_hardening）

---

## 开发阶段

### Phase 1: 基础设施 — "Make It Move"

ADB 连接、截图捕获、交互式 CLI。

- `device/adb_controller.py` — ADB 连接、截图、点击、滑动、按键
- `device/input_actions.py` — 长按、拖拽、点击中心
- `vision/screenshot.py` — 截图管理（捕获、保存、历史记录）
- `utils/logger.py` — 日志系统（控制台 + 文件 + JSONL）
- `utils/image_utils.py` — 图像处理工具（裁剪、缩放、base64）
- `main.py` — 交互式 CLI 入口
- `config.py` — 全局配置（支持蓝叠/夜神模拟器预设切换）

### Phase 2: 视觉感知 — "Make It See"

模板匹配、OCR、网格标注、场景分类、弹窗过滤。

- `vision/template_matcher.py` — OpenCV 模板匹配（支持 Alpha 透明遮罩）
- `vision/ocr_locator.py` — RapidOCR 文字检测与定位
- `vision/grid_overlay.py` — 8×6 标签网格（A1-H6），用于 LLM 坐标语义化
- `vision/element_detector.py` — 统一元素检测入口（模板→OCR→轮廓→网格回退）
- `scene/classifier.py` — 场景分类器（右下角图标判定法）
- `scene/popup_filter.py` — 弹窗自动检测与关闭

### Phase 3: 状态与本地决策 — "Make It Think Locally"

游戏状态追踪、持久化、规则引擎。

- `state/game_state.py` — GameState 数据模型（资源、建筑、行军、Quest 状态）
- `state/state_tracker.py` — 从截图 OCR 提取游戏状态
- `state/persistence.py` — JSON 原子化持久化
- `brain/auto_handler.py` — 自动操作处理器（弹窗关闭、奖励领取）
- `scene/handlers/` — 场景处理器（main_city, world_map, battle）

### Phase 4: LLM 集成 — "Make It Think Strategically"

Claude/GLM 大模型接入，三层决策架构闭环。

- `brain/llm_planner.py` — LLM 战略规划器（网格标注截图 + 状态摘要）
- `model_presets.py` — 多模型预设系统（智谱 GLM / Anthropic Claude / DeepSeek）
- `executor/action_validator.py` — 执行前验证
- `executor/action_runner.py` — 动作执行器
- `executor/result_checker.py` — 执行后截图确认

### Phase 5: 加固 — "Make It Reliable"

错误恢复、卡死检测、应用重启。

- `brain/stuck_recovery.py` — 卡死检测与恢复（连续相同场景→逐级升级→重启应用）
- ADB 断连自动重连
- 动作执行重试机制（最多 3 次）
- 结构化日志（.log + .jsonl + 每动作截图）

### Phase 6: Quest Workflow 状态机

跨迭代的任务执行生命周期。

- `vision/quest_bar_detector.py` — Quest 栏检测（卷轴图标、红色徽标、OCR 文本、绿色对勾、手指引导）
- `brain/quest_workflow.py` — 8 阶段状态机（IDLE→ENSURE_MAIN_CITY→READ_QUEST→CLICK_QUEST→EXECUTE_QUEST→CHECK_COMPLETION→CLAIM_REWARD→VERIFY）

### Phase 7-9: 弹窗修复与全面加固

- Alpha 透明遮罩支持（close_x 跨背景色匹配）
- close_popup 三阶段安全策略（模板→OCR→BACK）
- close_x 假阳性过滤（右上角位置验证）
- Unknown 场景 popup_filter 回退
- 弹窗逐级升级机制（OCR→close_x→BACK→屏幕中心→LLM→兜底）
- 按钮优先级排序与单按钮返回

### Quest Scripting 系统

JSON 驱动的多步骤任务脚本。

- `brain/quest_script.py` — QuestScriptRunner（5 个动词：tap_xy, tap_text, tap_icon, read_text, eval）
- 变量系统（read_text 写入、eval 计算、{var} 引用）
- 支持 repeat 重复和条件分支
- CLI 双语匹配（英文 name 或中文 pattern）

### 多游戏支持

- `game_profile.py` — GameProfile 数据类，从 `games/<id>/game.json` 加载
- `games/frozenisland/` — 冰封家园配置、模板、导航路径
- `games/westgame2/` — West Game 2 配置、模板、导航路径、6 个 Quest 脚本
- 所有模块通过 `game_profile` 参数注入游戏配置，回退到类级别默认值

### Building Finder

- `vision/building_finder.py` — 滚动城市地图找建筑（press-drag-read 技术）
- ADB swipe 滚动 + 并发截图 OCR + 位置补偿

### Finger Detector

- `brain/finger_detector.py` — 教程手指检测（NCC 阈值、边界对比度验证、水平翻转检测）
- 假阳性过滤：fill ratio、max width ratio、boundary contrast

### 其他改进

- 禁止使用 Android BACK 键（SLG 游戏不响应）
- 自适应循环等待（相同场景时倍增，检测到手指时重置）
- 灰色（禁用）按钮 HSV 饱和度检测跳过
- 快速切换游戏支持
- LLM 凭证分离到 gitignored 的 `llm_secret.yaml`

---

## 项目架构

```
SLGrobot/
├── config.py              # 全局配置
├── main.py                # CLI + 自动循环入口
├── game_profile.py        # 多游戏配置加载
├── model_presets.py       # LLM 模型预设
├── device/                # ADB 设备控制层
├── vision/                # 视觉感知层（模板、OCR、网格、建筑查找）
├── scene/                 # 场景理解层（分类、弹窗、处理器）
├── state/                 # 状态管理层（数据模型、追踪、持久化）
├── brain/                 # 决策层（自动处理、脚本、手指检测、卡死恢复）
├── executor/              # 执行管线（验证→执行→确认）
├── utils/                 # 工具（日志、图像）
├── games/                 # 游戏配置目录
│   ├── frozenisland/      # 冰封家园
│   └── westgame2/         # West Game 2
└── docs/                  # 设计文档
```

## 核心设计原则

1. **LLM 选网格，不选像素** — CV 解析坐标，LLM 只选 A1-H6
2. **LLM 无状态** — 游戏状态 JSON 持久化，每次调用传入上下文
3. **场景优先派发** — 每轮先分类场景，再决策
4. **90% 本地处理** — AutoHandler + Quest Scripts 覆盖大部分操作
5. **验证-执行-确认** — 三阶段执行管线
6. **禁止 BACK 键** — SLG 游戏内嵌 UI 不响应系统返回键

---

## 历史文档索引

开发过程的详细阶段记录保留在以下文件中（仅供历史参考）：

| 文件 | 内容 |
|------|------|
| `archive/design.md` | 原始架构设计文档 |
| `archive/phase1.md` | Phase 1 完成报告 |
| `archive/phase2.md` | Phase 2 完成报告 |
| `archive/phase3.md` | Phase 3 完成报告 |
| `archive/phase4.md` | Phase 4 完成报告 |
| `archive/phase5.md` | Phase 5/6 游戏适配报告 |
| `archive/phase6.md` | Phase 6 Quest Workflow 报告 |
| `archive/multiple_games.md` | 多游戏支持设计文档 |
| `archive/example_quest_session.*` | Quest 执行示例日志 |
| `quest_scripting.md` | Quest 脚本系统设计文档 |
| `quickstart.md` | 快速上手指南 |
| `how_to_change_game.md` | 切换游戏指南 |
