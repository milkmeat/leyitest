# Open-AutoGLM + Claude Code 协作指南

## 项目简介

这是一个 AI 驱动的手机自动化框架。采用 **Claude Code 主控 + AutoGLM 分析执行** 的架构：

- **Claude Code (主控大脑)**：理解用户需求、规划步骤、做决策
- **AutoGLM (视觉引擎)**：分析界面内容、定位 UI 元素坐标、执行具体操作

## 重要原则

**让 AutoGLM 负责所有视觉相关的工作！**

- ✅ 正确：`analyze_screen()` - 让 AutoGLM 分析界面内容
- ✅ 正确：`locate_and_tap(description="微信图标")` - 让 AutoGLM 定位并点击
- ❌ 错误：Claude 直接分析截图图片 - 浪费 token，不如 AutoGLM 准确
- ❌ 一般错误：`execute_action(tap, element=[150, 450])` - Claude 估算坐标容易失败


## 快速参考：元素定位决策树

```
遇到元素需要点击
    │
    ├─ 是普通按钮/图标？
    │   └─ YES → 用 locate_and_tap(description="具体描述")
    │        │
    │        ├─ 成功 ✅
    │        │
    │        └─ 失败 ❌
    │             ├─ 1. 优化描述重试（添加位置+颜色+功能）
    │             ├─ 2. 改用位置描述 locate_and_tap("底部中央区域")
    │             └─ 3. 最后用 execute_action(tap, [估算坐标])
    │
    └─ 是系统操作？
        └─ YES → 用 execute_action (back/home/wait/launch)
```

## 架构图

```
用户请求 → Claude Code (主控大脑)
              │
              ├── 1. create_task_session() → 创建任务会话
              │        ↓
              ├── 2. analyze_screen() → AutoGLM 分析界面，返回结构化描述
              │        ↓
              ├── 3. Claude 决策：基于分析结果，决定要点击/输入什么
              │        ↓
              ├── 4. locate_and_tap() / locate_and_type() → AutoGLM 定位并执行
              │        ↓
              ├── 5. 循环 2-4 直到完成
              │        ↓
              └── 6. end_task_session() → 生成报告
                       ↓
                  任务日志 (phone-agent-tasks/)
                  ├── task_20260202_001/
                  │   ├── task.json      # 完整数据
                  │   ├── report.md      # 可读报告
                  │   └── screenshots/   # 截图文件
                  └── ...
```

## 可用工具

### 任务管理

| 工具 | 说明 |
|-----|------|
| `create_task_session` | 创建新任务会话，返回 task_id |
| `end_task_session` | 结束任务会话，生成报告 |
| `list_tasks` | 列出历史任务记录 |

### 截图与分析

| 工具 | 说明 | 推荐度 |
|-----|------|-------|
| `analyze_screen` | **AutoGLM 分析界面（强烈推荐！）** | ⭐⭐⭐ |

**重要**：始终使用 `analyze_screen` 让 AutoGLM 分析界面！

### 操作执行（全部使用 AutoGLM）

| 工具 | 说明 | 推荐度 |
|-----|------|-------|
| `locate_and_tap` | AutoGLM 定位并点击（推荐！） | ⭐⭐⭐ |
| `locate_and_type` | AutoGLM 定位输入框并输入文本（推荐！） | ⭐⭐⭐ |
| `locate_and_swipe` | AutoGLM 定位元素并滑动 | ⭐⭐⭐ |
| `execute_action` | 直接执行操作（用于 back/home/wait/launch ） | ⭐⭐ |
| `locate_element` | 仅定位元素返回坐标（一般不需要单独使用） | ⭐ |

**重要**：
- 一般情况：点击和输入操作请使用 `locate_and_*` 系列工具

### 辅助工具

| 工具 | 说明 |
|-----|------|
| `list_supported_apps` | 列出支持的应用 |
| `set_debug_mode` | 开启/关闭触摸可视化 |

### 兼容旧版

| 工具 | 说明 |
|-----|------|
| `run_phone_task` | [旧版] AutoGLM 全权执行 |
| `get_phone_screenshot` | [旧版] 只返回当前应用名 |

## 使用命令

使用 `/phone` 命令来执行手机任务：

```
/phone 打开微信，给张三发消息说"今晚聚餐"
```

## 任务执行流程

### 推荐流程（AutoGLM 分析 + AutoGLM 执行）

```
1. create_task_session(user_request="打开微信给张三发消息")
   → 返回 task_id

2. analyze_screen(task_id, step_number=1, task_context="需要打开微信")
   → AutoGLM 返回：
   {
     "current_screen": "手机主屏幕",
     "visible_elements": ["微信图标", "支付宝图标", "设置图标", ...],
     "suggested_actions": ["点击微信图标打开微信"]
   }

3. locate_and_tap(task_id, step_number=1, description="微信图标",
     claude_analysis="AutoGLM 分析显示当前在主屏幕，微信图标可见",
     claude_decision="点击微信图标启动应用")
   → AutoGLM 定位并点击

4. analyze_screen(task_id, step_number=2, task_context="需要给张三发消息")
   → AutoGLM 返回界面分析...

5. ... 循环执行直到完成 ...

N. end_task_session(task_id, final_result="已发送消息", success=True)
   → 生成报告
```

### 工具选择指南

| 场景 | 使用工具 | 示例 |
|-----|---------|------|
| 了解当前界面 | `analyze_screen` | `analyze_screen(task_context="需要找到设置入口")` |
| 点击按钮/图标 | `locate_and_tap` | `locate_and_tap(description="发送按钮")` |
| 输入文本 | `locate_and_type` | `locate_and_type(input_description="搜索框", text="关键词")` |
| 滑动屏幕 | `locate_and_swipe` | `locate_and_swipe(description="列表区域", direction="up")` |
| 返回上一页 | `execute_action` | `execute_action(action="back")` |
| 回到桌面 | `execute_action` | `execute_action(action="home")` |
| 等待加载 | `execute_action` | `execute_action(action="wait", duration=2)` |
| 启动应用 | `execute_action` | `execute_action(action="launch", app="微信")` |


### 推荐的方式
```python
# ✅ 让 AutoGLM 分析界面
analyze_screen()  # AutoGLM 分析更准确，返回结构化数据

# ✅ 让 AutoGLM 来定位（普通元素）
locate_and_tap(description="微信图标")  # AutoGLM 精确定位


### 不推荐的方式（容易失败或浪费资源）

```python
# ❌ 普通元素不要自己估算坐标
execute_action(action="tap", element=[320, 450])  # Claude 估算的坐标经常不准

```

## 坐标系统

所有坐标使用 **绝对像素坐标**：
- `[0, 0]` = 屏幕左上角
- `[屏幕宽度, 屏幕高度]` = 屏幕右下角
- `[屏幕宽度/2, 屏幕高度/2]` = 屏幕中心

直接使用设备的实际像素坐标，无需转换。例如，1080x1920 的屏幕：
- 屏幕中央：`[540, 960]`
- 右下角：`[1080, 1920]`

## 任务日志

每个任务会自动保存到 `phone-agent-tasks/` 目录：

```
phone-agent-tasks/
├── task_20260202_001/
│   ├── task.json        # 完整 JSON 数据
│   ├── report.md        # Markdown 报告
│   └── screenshots/     # 截图
│       ├── step_001_before.png
│       ├── step_001_after.png
│       └── ...
└── task_20260202_002/
```

## 任务规划原则

### 职责分工

| 角色 | 职责 | 示例 |
|-----|------|------|
| **Claude** | 理解需求、规划步骤、做决策 | "根据 AutoGLM 分析，需要点击微信图标" |
| **AutoGLM** | 分析界面、定位元素、执行操作 | 分析界面内容、找到元素坐标、执行点击 |

### Claude 的工作流程

1. **让 AutoGLM 分析** → `analyze_screen(task_context="当前任务目标")`
2. **理解分析结果** → 基于 AutoGLM 返回的结构化数据做决策
3. **让 AutoGLM 执行** → `locate_and_tap(description="xxx")`
4. **验证结果** → 再次调用 `analyze_screen()` 确认操作成功
5. **错误恢复** → 如果失败，分析原因并调整策略

### 描述元素的技巧

#### 优先级规则

**1. 稳定元素（优先用 locate_and_tap）**
- 位置 + 颜色 + 功能：`"右上角蓝色的确认按钮"`
- 位置 + 功能：`"底部的发送按钮"`
- 功能 + 特征：`"关闭按钮X"`

**2. 动态/临时元素（优先用 execute_action）**
- ⚠️ 高亮提示/动画：可能识别不稳定
- ⚠️ 临时弹窗/浮层：优先使用位置描述

#### 好的描述（具体、明确）

- ✅ "微信图标" - 图标类，稳定
- ✅ "右上角的搜索按钮" - 位置 + 功能
- ✅ "发送按钮" - 明确功能
- ✅ "底部的远征按钮" - 位置 + 功能
- ✅ "关闭按钮X" - 功能 + 形状
- ✅ "底部中央蓝色按钮" - 位置 + 颜色

#### 不好的描述（模糊或不稳定）

- ❌ "那个按钮" - 太模糊
- ❌ "左边的东西" - 太模糊
- ❌ "高亮的地方" - 动态效果，不稳定

### 单步操作粒度

好的粒度：
- 点击微信图标
- 在搜索框输入文字
- 点击发送按钮
- 向下滑动列表

不好的粒度：
- 完成整个购物流程（太粗，应该拆分）
- 点击坐标 (500, 300)（不要自己估算坐标）

## 元素定位失败的应对策略

### 失败降级流程

当 `locate_and_tap` 返回 `"未找到元素"` 时，按以下顺序尝试：

```
1️⃣ 优化描述词重试
   locate_and_tap(description="具体描述")
   ↓ 失败

2️⃣ 使用位置描述
   locate_and_tap(description="屏幕底部中央区域")
   ↓ 失败

3️⃣ 直接点击估算坐标（最后手段）
   execute_action(action="tap", element=[估算坐标])
```

### 常见失败场景及对策

#### 场景1：描述词不够精确

**症状**：
- 元素确实存在
- 描述太模糊或不准确

**对策**：
```python
# ❌ 模糊描述
locate_and_tap(description="按钮")

# ✅ 精确描述（位置 + 颜色 + 功能）
locate_and_tap(description="底部蓝色的确认按钮")
```

#### 场景2：动态UI元素

**症状**：
- 高亮效果、动画、临时提示
- 不稳定，有时能识别，有时不能

**对策**（以 1080x1920 屏幕为例）：
```python
# ✅ 优先使用位置描述
locate_and_tap(description="屏幕右上角区域")

# 或直接点击坐标（根据实际屏幕调整）
execute_action(action="tap", element=[972, 192])  # 右上角约90%宽度、10%高度位置
```

### 描述词优化示例

| 原描述（失败） | 优化后描述 | 说明 |
|--------------|-----------|------|
| "按钮" | "底部蓝色的确认按钮" | 添加位置+颜色+功能 |
| "图标" | "右上角的设置图标" | 添加位置+功能 |
| "那个地方" | "屏幕底部中央区域" | 使用具体位置 |
| "高亮的按钮" | "底部中央的按钮" | 去掉动态描述，用位置 |

### 何时使用 execute_action 点击坐标

**必须使用场景**（不要用 locate_and_tap）：
1. ✅ 返回键、Home键等系统操作
2. ✅ 等待、启动应用

**可以使用场景**（locate 失败后的降级方案）：
1. ⚠️ locate_and_tap 多次失败后
2. ⚠️ 元素位置非常固定（如固定的导航栏）

**不要使用场景**（优先用 locate_and_tap）：
1. ❌ 普通按钮、图标
2. ❌ 可滚动列表中的元素
3. ❌ 不同设备位置可能不同的元素

## 设备配置

当前配置（可通过环境变量覆盖）：

| 配置项 | 默认值 | 环境变量 |
|-------|-------|---------|
| 设备 ID | emulator-5554 | PHONE_DEVICE_ID |
| API 地址 | https://api.z.ai/... | AUTOGLM_BASE_URL |
| 模型 | AutoGLM-Phone-Multilingual | AUTOGLM_MODEL |

## 注意事项

1. **敏感操作**：涉及支付、删除等敏感操作时，ActionHandler 会请求确认
2. **验证码**：遇到验证码等需要人工介入时，会触发 Take_over
3. **最大步数**：使用旧版 run_phone_task 时默认最多执行 50 步
4. **界面分析**：优先使用 `analyze_screen()` 让 AutoGLM 分析，比 Claude 直接看图更准确
5. **元素定位失败**：如果 `locate_and_tap` 失败，先优化描述词重试，多次失败后再考虑直接点击坐标

## 故障排除

### MCP 连接失败
```bash
pip install mcp
python phone_mcp_server.py
```

### ADB 连接失败
```bash
adb devices
adb connect localhost:5555
```

### 截图失败
某些敏感页面（如支付页面）可能无法截图，会返回黑色图片并标记 `is_sensitive: true`。


### 游戏UI说明
你的主要任务是操作我已经打开的 "Frozen Island" 游戏，以下是关于游戏界面的一些说明

- 任务提示栏：在屏幕下部，聊天信息框的上方，是任务提示栏。点击其左侧的“羊皮纸”图标（右上角有红色数字提示表示有已完成未领取奖励的任务）后，会打开任务列表，包括 章节任务、成长任务、每日任务。点击任务文字，会直接跳转到任务执行入口。
- 在完成任务或升级建筑时，如果有前置任务要求，点击“前往”按钮可以快速跳转到对应的任务。
- 建筑升级：
  - 升级建筑时，需要先升级家具
  - 建筑名称栏右侧有一个进度条，需要先升级家具使其达到100%才会出现升级按钮
  - 在这个进度条下方有一个较大的"升级"/"下一个"按钮用于升级家具,可以连续点击增加进度。
  - 进度条达到100%后，进度条消失，点击蓝色"升级"按钮，才可以升级建筑。
  - 如果""确认"/"升级"按钮上显示一个时间（如00:01:30），表示建造需要的时间，要点一下才会开始建造。
  - 建筑开始升级后，建筑中央会出现倒数计时，需要等待其完成。
- 新手指引：屏幕上如果有"手指"图示，需要点击指尖处完成新手指引，可能会切换到建筑升级、完成任务、奖励领取等界面。需要完成这些操作后继续下一指引。
- 按钮颜色：灰色按钮=条件不满足，现在无法点击；蓝色按钮=现在可以点击，很可能会跳转到下一界面；金色按钮=任务已完成，可以领取奖励；绿色对勾=奖励已领取，不需要再点击。
