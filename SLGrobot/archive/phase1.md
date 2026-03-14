# Phase 1: Infrastructure - 完成情况

## 状态：已完成

## 目标

ADB 连接、截图捕获、基本点击操作、交互式命令行工具。

## 环境信息

| 项目 | 值 |
|------|-----|
| 模拟器 | 夜神模拟器 (Nox) |
| ADB 地址 | 127.0.0.1:62001 |
| ADB 路径 | `D:\Program Files\Nox\bin\nox_adb.exe` |
| 屏幕分辨率 | 1080x1920 (竖屏) |
| Python 依赖 | opencv-python, Pillow, numpy, adbutils |

## 已创建文件

```
SLGrobot/
  .gitignore                 # 排除 __pycache__/, data/screenshots/, logs/
  config.py                  # 全局配置 (ADB、分辨率、路径)
  requirements.txt           # Python 依赖
  main.py                    # 交互式 CLI 入口
  test_phase1.py             # Phase 1 测试脚本
  device/
    __init__.py
    adb_controller.py        # ADB 连接、截图、点击、滑动
    input_actions.py         # 长按、拖拽、点击中心、返回键
  vision/
    __init__.py
    screenshot.py            # 截图捕获、保存、历史记录
  utils/
    __init__.py
    logger.py                # 日志系统 (控制台 + 文件)
    image_utils.py           # 图像处理 (裁剪、缩放、base64)
  data/screenshots/          # 截图存储目录
  templates/                 # 模板图片目录 (buttons/, icons/, scenes/)
  logs/                      # 日志目录
```

## 各模块说明

### `config.py`
全局配置，包含 ADB 连接参数、屏幕分辨率、文件路径等。所有模块从此处读取配置。

### `device/adb_controller.py` — ADBController
通过 subprocess 调用 nox_adb.exe 实现 ADB 操作：
- `connect()` — 连接模拟器
- `screenshot()` — 截图，返回 BGR numpy 数组
- `tap(x, y)` — 点击指定坐标
- `swipe(x1, y1, x2, y2, duration_ms)` — 滑动
- `key_event(keycode)` — 发送按键 (返回=4, Home=3)
- `is_connected()` — 检测连接存活

### `device/input_actions.py` — InputActions
基于 ADBController 的高级输入封装：
- `long_press(x, y, ms)` — 长按
- `drag(x1, y1, x2, y2, ms)` — 拖拽
- `tap_center()` — 点击屏幕中心
- `press_back()` / `press_home()` — 返回/主页键

### `vision/screenshot.py` — ScreenshotManager
截图生命周期管理：
- `capture()` — 截图并存入历史
- `save(image, label)` — 带时间戳保存到磁盘
- `capture_and_save(label)` — 截图 + 保存
- `get_recent(count)` — 获取最近 N 张截图

### `utils/logger.py` — GameLogger
日志系统，初始化后自动配置 Python logging：
- 控制台输出 INFO 级别
- 文件输出 DEBUG 级别，存入 `logs/` 目录
- 支持附带截图记录 action/state/error

### `utils/image_utils.py`
图像处理工具函数：
- `crop_region` — 按 bbox 裁剪
- `resize` — 缩放
- `to_base64` — 转 base64 (供 Claude API 使用)
- `save_debug_image` — 调试图片保存

### `main.py` — 交互式 CLI
命令行交互工具，支持以下命令：

```
tap <x>,<y>                    点击坐标
swipe <x1>,<y1> <x2>,<y2> [ms] 滑动
longpress <x>,<y> [ms]         长按
screenshot [label]              截图保存
back                            返回键
home                            Home 键
center                          点击屏幕中心
status                          连接状态
help                            帮助
exit / quit                     退出
```

扩展方式：在 CLI 类中添加 `cmd_xxx` 方法即可自动注册新命令。

## 测试结果

`python test_phase1.py` 全部通过：

- **ADB 连接** — 成功连接 127.0.0.1:62001
- **截图捕获** — 1080x1920 BGR 图像，文件 ~2.2MB
- **截图管理** — 保存到 data/screenshots/，历史记录正常
- **点击执行** — tap/swipe 命令正常发送
- **图像工具** — crop/resize/base64/save 均正常

## Git 提交

- `5760989` — Implement Phase 1 infrastructure: ADB, screenshot, tap loop
- `4d1d990` — Rewrite main.py as interactive CLI for manual game control

## 下一步: Phase 2

视觉感知层 — 模板匹配、OCR、网格标注、场景分类、弹窗过滤。
