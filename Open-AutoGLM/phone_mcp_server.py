#!/usr/bin/env python3
"""
Phone Agent MCP Server
让 Claude Code 可以控制手机执行自动化任务

架构：Claude Code (主控) + AutoGLM (执行)
- Claude Code：理解用户需求、分析截图、规划步骤
- AutoGLM：执行具体操作、定位 UI 元素
"""

import asyncio
import base64
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any

# 设置编码，避免中文乱码
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

from phone_agent.model import ModelConfig
from phone_agent.device_factory import get_device_factory
from phone_agent.task_tracker import TaskTracker, TaskStep, get_tracker
from phone_agent.locator import AutoGLMLocator
from phone_agent.actions.handler import ActionHandler, parse_action

# ============ 配置区域（支持环境变量覆盖）============
from phone_agent.config.model_presets import get_preset, DEFAULT_PROVIDER

_provider = os.environ.get("MODEL_PROVIDER", DEFAULT_PROVIDER)
_preset = get_preset(_provider)

MODEL_CONFIG = ModelConfig(
    base_url=os.environ.get("AUTOGLM_BASE_URL", _preset["base_url"]),
    api_key=os.environ.get("AUTOGLM_API_KEY", _preset["api_key"]),
    model_name=os.environ.get("AUTOGLM_MODEL", _preset["model_name"]),
    max_tokens=int(os.environ.get("AUTOGLM_MAX_TOKENS", str(_preset["max_tokens"]))),
)

print(f"[phone-agent] provider={_provider}, model={MODEL_CONFIG.model_name}, base_url={MODEL_CONFIG.base_url}", file=sys.stderr)

# 夜神模拟器默认端口是 62001，蓝栈是 5555
DEFAULT_DEVICE_ID = os.environ.get("PHONE_DEVICE_ID", "127.0.0.1:62001")
DEFAULT_MAX_STEPS = int(os.environ.get("PHONE_MAX_STEPS", "50"))
# ====================================================

# 全局实例
_locator: AutoGLMLocator | None = None
_action_handler: ActionHandler | None = None
_debug_mode_enabled = True


def convert_autoglm_coords_to_absolute(
    relative_coords: tuple[int, int] | list[int],
    screen_width: int,
    screen_height: int
) -> tuple[int, int]:
    """
    将 AutoGLM 的相对坐标（0-1000 范围）转换为绝对像素坐标。

    Args:
        relative_coords: 0-1000 范围的坐标 [x, y]
        screen_width: 屏幕宽度（像素）
        screen_height: 屏幕高度（像素）

    Returns:
        绝对像素坐标 (x, y)

    Note:
        AutoGLM 返回归一化坐标：
        - [0, 0] = 屏幕左上角
        - [1000, 1000] = 屏幕右下角
        - [500, 500] = 屏幕中心
    """
    # 限制在有效范围内，防止异常值
    x_rel = max(0, min(1000, relative_coords[0]))
    y_rel = max(0, min(1000, relative_coords[1]))

    # 转换为绝对像素
    x = int(x_rel / 1000 * screen_width)
    y = int(y_rel / 1000 * screen_height)
    return x, y


def get_locator() -> AutoGLMLocator:
    """获取或创建 AutoGLMLocator 实例"""
    global _locator
    if _locator is None:
        _locator = AutoGLMLocator(MODEL_CONFIG)
    return _locator


def get_action_handler() -> ActionHandler:
    """获取或创建 ActionHandler 实例"""
    global _action_handler
    if _action_handler is None:
        _action_handler = ActionHandler(device_id=DEFAULT_DEVICE_ID)
    return _action_handler


def _get_adb_prefix(device_id: str | None = None) -> list[str]:
    """获取 ADB 命令前缀"""
    adb_path = os.environ.get("ADB_PATH", "adb")
    if device_id:
        return [adb_path, "-s", device_id]
    return [adb_path]


def set_touch_visualization(enabled: bool, device_id: str | None = None) -> tuple[bool, str]:
    """开启/关闭 Android 触摸可视化调试功能"""
    adb_prefix = _get_adb_prefix(device_id)
    value = "1" if enabled else "0"

    try:
        subprocess.run(
            adb_prefix + ["shell", "settings", "put", "system", "show_touches", value],
            capture_output=True, text=True, check=True
        )
        subprocess.run(
            adb_prefix + ["shell", "settings", "put", "system", "pointer_location", value],
            capture_output=True, text=True, check=True
        )

        status = "开启" if enabled else "关闭"
        return True, f"触摸可视化调试已{status}"
    except subprocess.CalledProcessError as e:
        return False, f"设置失败：{e}"
    except Exception as e:
        return False, f"错误：{str(e)}"


# 创建 MCP Server
server = Server("phone-agent")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        # ============ 任务管理工具 ============
        Tool(
            name="create_task_session",
            description="""创建新的任务会话，开始追踪任务执行过程。

在执行任何手机操作之前调用此工具。它会：
1. 创建任务目录用于保存截图和日志
2. 返回 task_id 用于后续操作
3. 记录用户的原始请求""",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_request": {
                        "type": "string",
                        "description": "用户的原始请求描述",
                    },
                },
                "required": ["user_request"],
            },
        ),
        Tool(
            name="end_task_session",
            description="""结束任务会话，生成 Markdown 报告。

在任务完成或失败后调用此工具。它会：
1. 保存完整的 task.json 数据
2. 生成可读的 report.md 报告
3. 汇总执行统计""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务会话 ID",
                    },
                    "final_result": {
                        "type": "string",
                        "description": "最终执行结果描述",
                    },
                    "success": {
                        "type": "boolean",
                        "description": "任务是否成功完成",
                    },
                },
                "required": ["task_id", "final_result", "success"],
            },
        ),
        Tool(
            name="list_tasks",
            description="列出历史任务记录",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回的最大任务数量（默认20）",
                        "default": 20,
                    },
                },
            },
        ),

        # ============ 截图工具 ============
        Tool(
            name="analyze_screen",
            description="""使用 AutoGLM 分析当前屏幕内容（推荐使用）。

让 AutoGLM 分析屏幕截图，返回：
1. 当前界面描述（如：微信聊天列表页）
2. 可见的 UI 元素列表
3. 建议的下一步操作

这比 Claude 直接分析截图更准确，因为 AutoGLM 专门针对手机界面进行了优化。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务会话 ID（可选）",
                    },
                    "step_number": {
                        "type": "integer",
                        "description": "当前步骤号",
                    },
                    "task_context": {
                        "type": "string",
                        "description": "任务背景描述，帮助 AutoGLM 更好地理解当前任务",
                    },
                },
            },
        ),

        # ============ 操作执行工具 ============
        Tool(
            name="execute_action",
            description="""执行手机操作并记录到任务日志。

支持的操作类型：
- tap: 点击指定坐标 (需要 element: [x, y])
- double_tap: 双击 (需要 element: [x, y])
- long_press: 长按 (需要 element: [x, y], 可选 duration)
- swipe: 滑动 (需要 start: [x, y], end: [x, y])
- type: 输入文本 (需要 text)
- back: 返回键
- home: 主页键
- launch: 启动应用 (需要 app)
- wait: 等待 (需要 duration，单位秒)

坐标使用绝对像素坐标（例如：1080x1920屏幕的中心点是 [540, 960]）""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务会话 ID（可选）",
                    },
                    "step_number": {
                        "type": "integer",
                        "description": "当前步骤号（提供 task_id 时使用）",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["tap", "double_tap", "long_press", "swipe", "type", "back", "home", "launch", "wait"],
                        "description": "要执行的操作类型",
                    },
                    "element": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "点击/长按/双击的绝对像素坐标 [x, y]",
                    },
                    "start": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "滑动起点 [x, y]",
                    },
                    "end": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "滑动终点 [x, y]",
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文本",
                    },
                    "app": {
                        "type": "string",
                        "description": "要启动的应用名称",
                    },
                    "duration": {
                        "type": "number",
                        "description": "持续时间（秒）",
                    },
                    "claude_analysis": {
                        "type": "string",
                        "description": "Claude 对当前界面的分析",
                    },
                    "claude_decision": {
                        "type": "string",
                        "description": "Claude 的决策说明",
                    },
                },
                "required": ["action"],
            },
        ),

        # ============ AutoGLM 定位工具 ============
        Tool(
            name="locate_element",
            description="""使用 AutoGLM 定位 UI 元素。

根据自然语言描述找到目标元素的坐标。适用于：
- 找不到明确坐标时
- 需要找到特定图标/按钮/文本

返回元素的绝对像素坐标。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "要定位的元素描述，如：'微信图标'、'搜索按钮'、'发送按钮'",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="locate_and_tap",
            description="""使用 AutoGLM 定位元素并点击。

结合定位和点击操作：
1. 截图分析
2. AutoGLM 定位目标元素
3. 自动点击找到的位置

适用于知道要点什么但不确定具体位置的情况。支持连续点击多次（如连点升级按钮）。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务会话 ID（可选）",
                    },
                    "step_number": {
                        "type": "integer",
                        "description": "当前步骤号",
                    },
                    "description": {
                        "type": "string",
                        "description": "要点击的元素描述",
                    },
                    "tap_count": {
                        "type": "integer",
                        "description": "连续点击次数（默认1次）",
                        "default": 1,
                        "minimum": 1,
                    },
                    "tap_interval": {
                        "type": "number",
                        "description": "每次点击之间的间隔（秒，默认0.3秒）",
                        "default": 0.3,
                        "minimum": 0.1,
                    },
                    "claude_analysis": {
                        "type": "string",
                        "description": "Claude 的界面分析",
                    },
                    "claude_decision": {
                        "type": "string",
                        "description": "Claude 的决策说明",
                    },
                },
                "required": ["description"],
            },
        ),
        Tool(
            name="locate_and_type",
            description="""使用 AutoGLM 定位输入框并输入文本。

流程：
1. 定位指定的输入框
2. 点击输入框
3. 输入文本

适用于需要在特定输入框中输入内容的场景。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务会话 ID（可选）",
                    },
                    "step_number": {
                        "type": "integer",
                        "description": "当前步骤号",
                    },
                    "input_description": {
                        "type": "string",
                        "description": "输入框的描述，如：'搜索框'、'消息输入框'",
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文本",
                    },
                    "claude_analysis": {
                        "type": "string",
                        "description": "Claude 的界面分析",
                    },
                    "claude_decision": {
                        "type": "string",
                        "description": "Claude 的决策说明",
                    },
                },
                "required": ["input_description", "text"],
            },
        ),
        Tool(
            name="locate_and_swipe",
            description="""使用 AutoGLM 定位元素区域并滑动。

流程：
1. 定位指定的区域/元素
2. 在该区域执行滑动操作

适用于需要在特定区域滑动的场景，如滚动列表、切换页面等。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "任务会话 ID（可选）",
                    },
                    "step_number": {
                        "type": "integer",
                        "description": "当前步骤号",
                    },
                    "description": {
                        "type": "string",
                        "description": "要滑动的区域描述，如：'列表区域'、'图片轮播'、'屏幕中央'",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "滑动方向",
                    },
                    "distance": {
                        "type": "string",
                        "enum": ["short", "medium", "long"],
                        "description": "滑动距离（默认 medium）",
                        "default": "medium",
                    },
                    "claude_analysis": {
                        "type": "string",
                        "description": "Claude 的界面分析",
                    },
                    "claude_decision": {
                        "type": "string",
                        "description": "Claude 的决策说明",
                    },
                },
                "required": ["description", "direction"],
            },
        ),

        # ============ 辅助工具 ============
        Tool(
            name="list_supported_apps",
            description="列出支持直接启动的应用列表",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="set_debug_mode",
            description="""开启或关闭触摸可视化调试模式。

开启后点击位置会显示圆点，便于调试。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "true 开启，false 关闭",
                    },
                },
                "required": ["enabled"],
            },
        ),

        # ============ 兼容旧工具（保留） ============
        Tool(
            name="run_phone_task",
            description="""[旧版] 让 AutoGLM 全权执行手机任务。

注意：推荐使用新的分步工具（create_task_session + analyze_screen + locate_and_* + execute_action）
以获得更好的控制和日志记录。

此工具会让 AutoGLM 自动完成整个任务，Claude 无法介入中间过程。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "要执行的手机任务描述（中文）",
                    },
                    "max_steps": {
                        "type": "integer",
                        "description": "最大执行步数（默认50）",
                        "default": 50,
                    },
                },
                "required": ["task"],
            },
        ),
        Tool(
            name="get_phone_screenshot",
            description="[旧版] 获取手机当前状态。推荐使用 analyze_screen。",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    """处理工具调用"""
    tracker = get_tracker()
    device_factory = get_device_factory()

    # ============ 任务管理 ============
    if name == "create_task_session":
        user_request = arguments.get("user_request", "")
        if not user_request:
            return [TextContent(type="text", text="错误：user_request 不能为空")]

        # 获取设备信息
        try:
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )
            device_info = {
                "id": DEFAULT_DEVICE_ID,
                "screen_width": screenshot.width,
                "screen_height": screenshot.height,
            }
        except Exception:
            device_info = {"id": DEFAULT_DEVICE_ID}

        session = tracker.create_session(user_request, device_info)
        return [TextContent(
            type="text",
            text=json.dumps({
                "task_id": session.task_id,
                "task_dir": str(session.task_dir),
                "message": f"任务会话已创建：{session.task_id}"
            }, ensure_ascii=False)
        )]

    elif name == "end_task_session":
        task_id = arguments.get("task_id", "")
        final_result = arguments.get("final_result", "")
        success = arguments.get("success", False)

        if not task_id:
            return [TextContent(type="text", text="错误：task_id 不能为空")]

        try:
            report_path = tracker.end_session(task_id, final_result, success)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "report_path": str(report_path),
                    "message": f"任务报告已生成：{report_path}"
                }, ensure_ascii=False)
            )]
        except ValueError as e:
            return [TextContent(type="text", text=f"错误：{str(e)}")]

    elif name == "list_tasks":
        limit = arguments.get("limit", 20)
        tasks = tracker.list_tasks(limit)
        return [TextContent(
            type="text",
            text=json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2)
        )]

    # ============ 截图 ============
    if name == "analyze_screen":
        task_id = arguments.get("task_id")
        step_number = arguments.get("step_number", 1)
        task_context = arguments.get("task_context", "")

        try:
            # 获取截图
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )
            current_app = await asyncio.to_thread(
                device_factory.get_current_app, DEFAULT_DEVICE_ID
            )

            # 保存截图
            saved_path = None
            if task_id:
                try:
                    saved_path = tracker.save_screenshot(
                        task_id,
                        step_number,
                        "before",
                        base64.b64decode(screenshot.base64_data)
                    )
                except ValueError:
                    pass

            # 使用 AutoGLM 分析屏幕（真正的异步，无需线程池）
            locator = get_locator()
            analysis = await locator.aanalyze_screen(screenshot.base64_data, task_context)

            result = {
                "current_app": current_app,
                "screen_size": {"width": screenshot.width, "height": screenshot.height},
                "is_sensitive": screenshot.is_sensitive,
                "debug_model_info": {
                    "provider": _provider,
                    "model_name": MODEL_CONFIG.model_name,
                    "base_url": MODEL_CONFIG.base_url,
                },
                "analysis": {
                    "current_screen": analysis.current_screen,
                    "interactive_elements": [
                        {
                            "name": e.name, "type": e.type,
                            "location": e.location, "state": e.state,
                            "center": e.center,
                        }
                        for e in analysis.interactive_elements
                    ],
                    "visible_elements": analysis.visible_elements,
                    "finger_guide": analysis.finger_guide,
                    "suggested_actions": analysis.suggested_actions,
                },
            }
            if saved_path:
                result["screenshot_saved_to"] = saved_path
            if analysis.error:
                result["analysis"]["error"] = analysis.error

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            import traceback
            return [TextContent(type="text", text=f"分析屏幕失败：{str(e)}\n{traceback.format_exc()}")]

    # ============ 操作执行 ============
    elif name == "execute_action":
        task_id = arguments.get("task_id")
        step_number = arguments.get("step_number", 1)
        action_type = arguments.get("action", "")
        claude_analysis = arguments.get("claude_analysis", "")
        claude_decision = arguments.get("claude_decision", "")

        if not action_type:
            return [TextContent(type="text", text="错误：action 不能为空")]

        try:
            # 获取屏幕尺寸
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )
            screen_width = screenshot.width
            screen_height = screenshot.height

            # 构建操作参数
            action_result = None
            action_detail = {"type": action_type}

            if action_type == "tap":
                element = arguments.get("element", [])
                if not element or len(element) != 2:
                    return [TextContent(type="text", text="错误：tap 需要 element: [x, y]")]
                action_detail["element"] = element
                # 直接使用绝对像素坐标
                x = int(element[0])
                y = int(element[1])
                await asyncio.to_thread(device_factory.tap, x, y, DEFAULT_DEVICE_ID)
                action_result = {"success": True}

            elif action_type == "double_tap":
                element = arguments.get("element", [])
                if not element or len(element) != 2:
                    return [TextContent(type="text", text="错误：double_tap 需要 element: [x, y]")]
                action_detail["element"] = element
                x = int(element[0])
                y = int(element[1])
                await asyncio.to_thread(device_factory.double_tap, x, y, DEFAULT_DEVICE_ID)
                action_result = {"success": True}

            elif action_type == "long_press":
                element = arguments.get("element", [])
                duration = arguments.get("duration", 3)
                if not element or len(element) != 2:
                    return [TextContent(type="text", text="错误：long_press 需要 element: [x, y]")]
                action_detail["element"] = element
                action_detail["duration"] = duration
                x = int(element[0])
                y = int(element[1])
                await asyncio.to_thread(
                    device_factory.long_press, x, y, int(duration * 1000), DEFAULT_DEVICE_ID
                )
                action_result = {"success": True}

            elif action_type == "swipe":
                start = arguments.get("start", [])
                end = arguments.get("end", [])
                if not start or not end or len(start) != 2 or len(end) != 2:
                    return [TextContent(type="text", text="错误：swipe 需要 start 和 end: [x, y]")]
                action_detail["start"] = start
                action_detail["end"] = end
                start_x = int(start[0])
                start_y = int(start[1])
                end_x = int(end[0])
                end_y = int(end[1])
                await asyncio.to_thread(
                    device_factory.swipe, start_x, start_y, end_x, end_y, None, DEFAULT_DEVICE_ID
                )
                action_result = {"success": True}

            elif action_type == "type":
                text = arguments.get("text", "")
                if not text:
                    return [TextContent(type="text", text="错误：type 需要 text")]
                action_detail["text"] = text

                # 使用 ActionHandler 处理输入（包含键盘切换逻辑）
                handler = get_action_handler()
                result = handler.execute(
                    {"_metadata": "do", "action": "Type", "text": text},
                    screen_width,
                    screen_height
                )
                action_result = {"success": result.success, "message": result.message}

            elif action_type == "back":
                await asyncio.to_thread(device_factory.back, DEFAULT_DEVICE_ID)
                action_result = {"success": True}

            elif action_type == "home":
                await asyncio.to_thread(device_factory.home, DEFAULT_DEVICE_ID)
                action_result = {"success": True}

            elif action_type == "launch":
                app = arguments.get("app", "")
                if not app:
                    return [TextContent(type="text", text="错误：launch 需要 app")]
                action_detail["app"] = app
                success = await asyncio.to_thread(
                    device_factory.launch_app, app, DEFAULT_DEVICE_ID
                )
                action_result = {"success": success, "message": None if success else f"未找到应用: {app}"}

            elif action_type == "wait":
                duration = arguments.get("duration", 1)
                action_detail["duration"] = duration
                await asyncio.sleep(duration)
                action_result = {"success": True}

            else:
                return [TextContent(type="text", text=f"未知操作类型：{action_type}")]

            # 记录到任务日志
            if task_id:
                try:
                    current_app = await asyncio.to_thread(
                        device_factory.get_current_app, DEFAULT_DEVICE_ID
                    )
                    step = TaskStep(
                        step_number=step_number,
                        timestamp=datetime.now().isoformat(),
                        current_app=current_app,
                        claude_analysis=claude_analysis,
                        claude_decision=claude_decision,
                        action=action_detail,
                        result=action_result,
                    )
                    tracker.add_step(task_id, step)
                except ValueError:
                    pass  # Session not found

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": action_result.get("success", False),
                    "action": action_detail,
                    "message": action_result.get("message"),
                }, ensure_ascii=False)
            )]

        except Exception as e:
            import traceback
            return [TextContent(
                type="text",
                text=f"执行操作失败：{str(e)}\n{traceback.format_exc()}"
            )]

    # ============ AutoGLM 定位 ============
    elif name == "locate_element":
        description = arguments.get("description", "")
        if not description:
            return [TextContent(type="text", text="错误：description 不能为空")]

        try:
            # 获取截图
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )

            # 使用 AutoGLM 定位（真正的异步，无需线程池）
            locator = get_locator()
            result = await locator.alocate(screenshot.base64_data, description)

            if result.found:
                # 转换为绝对像素坐标
                abs_x, abs_y = convert_autoglm_coords_to_absolute(
                    result.element,
                    screenshot.width,
                    screenshot.height
                )

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "found": True,
                        "element": [abs_x, abs_y],
                        "thinking": result.thinking,
                    }, ensure_ascii=False)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "found": False,
                        "thinking": result.thinking,
                        "error": result.error,
                    }, ensure_ascii=False)
                )]

        except Exception as e:
            return [TextContent(type="text", text=f"定位失败：{str(e)}")]

    elif name == "locate_and_tap":
        task_id = arguments.get("task_id")
        step_number = arguments.get("step_number", 1)
        description = arguments.get("description", "")
        tap_count = arguments.get("tap_count", 1)
        tap_interval = arguments.get("tap_interval", 0.3)
        claude_analysis = arguments.get("claude_analysis", "")
        claude_decision = arguments.get("claude_decision", "")

        if not description:
            return [TextContent(type="text", text="错误：description 不能为空")]

        try:
            # 获取截图
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )

            # 定位元素（真正的异步，无需线程池）
            locator = get_locator()
            result = await locator.alocate(screenshot.base64_data, description)

            if not result.found:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "message": f"未找到元素: {description}",
                        "thinking": result.thinking,
                    }, ensure_ascii=False)
                )]

            # 执行连续点击（转换 AutoGLM 的相对坐标为绝对像素）
            x, y = convert_autoglm_coords_to_absolute(
                result.element,
                screenshot.width,
                screenshot.height
            )

            for i in range(tap_count):
                await asyncio.to_thread(device_factory.tap, x, y, DEFAULT_DEVICE_ID)
                # 如果不是最后一次点击，等待间隔时间
                if i < tap_count - 1:
                    await asyncio.sleep(tap_interval)

            # 记录到任务
            action_detail = {
                "type": "tap",
                "element": list(result.element),
                "x_y":[x,y],
                "description": description,
                "tap_count": tap_count,
            }
            if tap_count > 1:
                action_detail["tap_interval"] = tap_interval

            action_result = {"success": True}

            if task_id:
                try:
                    current_app = await asyncio.to_thread(
                        device_factory.get_current_app, DEFAULT_DEVICE_ID
                    )
                    step = TaskStep(
                        step_number=step_number,
                        timestamp=datetime.now().isoformat(),
                        current_app=current_app,
                        claude_analysis=claude_analysis,
                        claude_decision=claude_decision,
                        action=action_detail,
                        autoglm_response={
                            "thinking": result.thinking,
                            "raw": result.raw_response,
                        },
                        result=action_result,
                    )
                    tracker.add_step(task_id, step)
                except ValueError:
                    pass

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "element": list(result.element),
                    "tap_count": tap_count,
                    "thinking": result.thinking,
                }, ensure_ascii=False)
            )]

        except Exception as e:
            return [TextContent(type="text", text=f"定位点击失败：{str(e)}")]

    elif name == "locate_and_type":
        task_id = arguments.get("task_id")
        step_number = arguments.get("step_number", 1)
        input_description = arguments.get("input_description", "")
        text = arguments.get("text", "")
        claude_analysis = arguments.get("claude_analysis", "")
        claude_decision = arguments.get("claude_decision", "")

        if not input_description or not text:
            return [TextContent(type="text", text="错误：input_description 和 text 不能为空")]

        try:
            # 获取截图
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )

            # 定位输入框（真正的异步，无需线程池）
            locator = get_locator()
            result = await locator.alocate(screenshot.base64_data, input_description)

            if not result.found:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "message": f"未找到输入框: {input_description}",
                        "thinking": result.thinking,
                    }, ensure_ascii=False)
                )]

            # 点击输入框（转换 AutoGLM 的相对坐标为绝对像素）
            x, y = convert_autoglm_coords_to_absolute(
                result.element,
                screenshot.width,
                screenshot.height
            )
            await asyncio.to_thread(device_factory.tap, x, y, DEFAULT_DEVICE_ID)

            # 等待键盘弹出
            await asyncio.sleep(0.5)

            # 输入文本
            handler = get_action_handler()
            type_result = handler.execute(
                {"_metadata": "do", "action": "Type", "text": text},
                screenshot.width,
                screenshot.height
            )

            action_detail = {
                "type": "locate_and_type",
                "input_description": input_description,
                "element": list(result.element),
                "text": text,
            }
            action_result = {"success": type_result.success, "message": type_result.message}

            if task_id:
                try:
                    current_app = await asyncio.to_thread(
                        device_factory.get_current_app, DEFAULT_DEVICE_ID
                    )
                    step = TaskStep(
                        step_number=step_number,
                        timestamp=datetime.now().isoformat(),
                        current_app=current_app,
                        claude_analysis=claude_analysis,
                        claude_decision=claude_decision,
                        action=action_detail,
                        autoglm_response={
                            "thinking": result.thinking,
                            "raw": result.raw_response,
                        },
                        result=action_result,
                    )
                    tracker.add_step(task_id, step)
                except ValueError:
                    pass

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": type_result.success,
                    "element": list(result.element),
                    "thinking": result.thinking,
                }, ensure_ascii=False)
            )]

        except Exception as e:
            return [TextContent(type="text", text=f"定位输入失败：{str(e)}")]

    elif name == "locate_and_swipe":
        task_id = arguments.get("task_id")
        step_number = arguments.get("step_number", 1)
        description = arguments.get("description", "")
        direction = arguments.get("direction", "")
        distance = arguments.get("distance", "medium")
        claude_analysis = arguments.get("claude_analysis", "")
        claude_decision = arguments.get("claude_decision", "")

        if not description or not direction:
            return [TextContent(type="text", text="错误：description 和 direction 不能为空")]

        try:
            # 获取截图
            screenshot = await asyncio.to_thread(
                device_factory.get_screenshot, DEFAULT_DEVICE_ID
            )

            # 定位区域中心点（真正的异步，无需线程池）
            locator = get_locator()
            result = await locator.alocate(screenshot.base64_data, description)

            if not result.found:
                # 如果没找到特定元素，使用屏幕中心
                center_x = screenshot.width // 2
                center_y = screenshot.height // 2
            else:
                # 转换 AutoGLM 的相对坐标为绝对像素
                center_x, center_y = convert_autoglm_coords_to_absolute(
                    result.element,
                    screenshot.width,
                    screenshot.height
                )

            # 计算滑动距离（基于屏幕高度的比例）
            # short: 15%, medium: 30%, long: 45%
            distance_map = {
                "short": int(screenshot.height * 0.15),
                "medium": int(screenshot.height * 0.30),
                "long": int(screenshot.height * 0.45)
            }
            dist = distance_map.get(distance, int(screenshot.height * 0.30))

            # 计算滑动起点和终点
            if direction == "up":
                start = [center_x, center_y + dist // 2]
                end = [center_x, center_y - dist // 2]
            elif direction == "down":
                start = [center_x, center_y - dist // 2]
                end = [center_x, center_y + dist // 2]
            elif direction == "left":
                start = [center_x + dist // 2, center_y]
                end = [center_x - dist // 2, center_y]
            elif direction == "right":
                start = [center_x - dist // 2, center_y]
                end = [center_x + dist // 2, center_y]
            else:
                return [TextContent(type="text", text=f"未知滑动方向：{direction}")]

            # 确保坐标在有效范围内（留出5%边距）
            margin_x = int(screenshot.width * 0.05)
            margin_y = int(screenshot.height * 0.05)
            start = [
                max(margin_x, min(screenshot.width - margin_x, start[0])),
                max(margin_y, min(screenshot.height - margin_y, start[1]))
            ]
            end = [
                max(margin_x, min(screenshot.width - margin_x, end[0])),
                max(margin_y, min(screenshot.height - margin_y, end[1]))
            ]

            # 执行滑动（直接使用绝对坐标）
            start_x = int(start[0])
            start_y = int(start[1])
            end_x = int(end[0])
            end_y = int(end[1])
            await asyncio.to_thread(
                device_factory.swipe, start_x, start_y, end_x, end_y, None, DEFAULT_DEVICE_ID
            )

            # 记录到任务
            action_detail = {
                "type": "swipe",
                "description": description,
                "direction": direction,
                "distance": distance,
                "start": start,
                "end": end,
            }
            action_result = {"success": True}

            if task_id:
                try:
                    current_app = await asyncio.to_thread(
                        device_factory.get_current_app, DEFAULT_DEVICE_ID
                    )
                    step = TaskStep(
                        step_number=step_number,
                        timestamp=datetime.now().isoformat(),
                        current_app=current_app,
                        claude_analysis=claude_analysis,
                        claude_decision=claude_decision,
                        action=action_detail,
                        autoglm_response={
                            "thinking": result.thinking if result.found else "使用屏幕中心",
                            "raw": result.raw_response if result.found else None,
                        },
                        result=action_result,
                    )
                    tracker.add_step(task_id, step)
                except ValueError:
                    pass

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "direction": direction,
                    "start": start,
                    "end": end,
                    "thinking": result.thinking if result.found else "使用屏幕中心作为滑动区域",
                }, ensure_ascii=False)
            )]

        except Exception as e:
            return [TextContent(type="text", text=f"定位滑动失败：{str(e)}")]

    # ============ 辅助工具 ============
    elif name == "list_supported_apps":
        try:
            from phone_agent.config.apps import APP_PACKAGES
            apps = list(APP_PACKAGES.keys())
            return [TextContent(
                type="text",
                text=f"支持的应用（共{len(apps)}个）：\n" + "\n".join(f"- {app}" for app in sorted(apps))
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"获取应用列表失败：{str(e)}")]

    elif name == "set_debug_mode":
        enabled = arguments.get("enabled", False)
        try:
            success, message = await asyncio.to_thread(
                set_touch_visualization, enabled, DEFAULT_DEVICE_ID
            )
            global _debug_mode_enabled
            if success:
                _debug_mode_enabled = enabled
            return [TextContent(type="text", text=message)]
        except Exception as e:
            return [TextContent(type="text", text=f"设置调试模式失败：{str(e)}")]

    # ============ 兼容旧工具 ============
    elif name == "run_phone_task":
        from phone_agent import PhoneAgent
        from phone_agent.agent import AgentConfig

        task = arguments.get("task", "")
        max_steps = arguments.get("max_steps", DEFAULT_MAX_STEPS)

        if not task:
            return [TextContent(type="text", text="错误：任务描述不能为空")]

        def run_with_realtime_output(task_desc: str, max_steps: int) -> str:
            original_stdout = sys.stdout
            sys.stdout = sys.stderr

            try:
                agent_config = AgentConfig(
                    device_id=DEFAULT_DEVICE_ID,
                    max_steps=max_steps,
                    lang="cn",
                    verbose=True,
                )
                agent = PhoneAgent(
                    model_config=MODEL_CONFIG,
                    agent_config=agent_config,
                )
                result = agent.run(task_desc)
                return result
            finally:
                sys.stdout = original_stdout

        timeout_seconds = max_steps * 10 + 60

        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(run_with_realtime_output, task, max_steps),
                timeout=timeout_seconds
            )
            return [TextContent(type="text", text=f"任务完成：{result}")]
        except asyncio.TimeoutError:
            return [TextContent(type="text", text=f"任务执行超时（{timeout_seconds}秒）")]
        except Exception as e:
            import traceback
            return [TextContent(type="text", text=f"任务执行失败：{str(e)}\n{traceback.format_exc()}")]

    elif name == "get_phone_screenshot":
        try:
            current_app = await asyncio.to_thread(
                device_factory.get_current_app, DEFAULT_DEVICE_ID
            )
            return [TextContent(type="text", text=f"当前应用：{current_app}")]
        except Exception as e:
            return [TextContent(type="text", text=f"获取状态失败：{str(e)}")]

    return [TextContent(type="text", text=f"未知工具：{name}")]


async def main():
    """启动 MCP Server"""
    async def init_touch_viz():
        try:
            await asyncio.to_thread(set_touch_visualization, True, DEFAULT_DEVICE_ID)
        except Exception:
            pass

    asyncio.create_task(init_touch_viz())

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
