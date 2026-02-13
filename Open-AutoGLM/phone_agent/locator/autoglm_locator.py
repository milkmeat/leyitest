"""AutoGLM-based UI element locator and screen analyzer.

This module uses AutoGLM to:
1. Locate UI elements on screen based on natural language descriptions
2. Analyze screen content and provide structured descriptions
"""

import re
from dataclasses import dataclass

from phone_agent.model import ModelClient, ModelConfig


@dataclass
class LocateResult:
    """Result of a UI element location attempt."""

    found: bool
    element: tuple[int, int] | None = None
    thinking: str = ""
    raw_response: str = ""
    error: str | None = None


@dataclass
class InteractiveElement:
    """A single interactive UI element on screen."""

    name: str
    type: str  # button, input, icon, tab, link, switch, other
    location: str  # e.g. "顶部居中", "底部右侧"
    state: str  # 可点击, 不可点击, 已选中, 已禁用
    center: list[int] | None = None  # 中心点坐标 [x, y]，0-1000 归一化


@dataclass
class ScreenAnalysis:
    """Result of screen analysis by AutoGLM."""

    current_screen: str  # Description of the current screen
    interactive_elements: list[InteractiveElement]  # Interactive UI elements
    visible_elements: list[str]  # Flat name list (for backward compat)
    suggested_actions: list[str]  # Suggested next actions
    finger_guide: str | None = None  # Finger guide icon description
    raw_response: str = ""
    error: str | None = None


class AutoGLMLocator:
    """
    Uses AutoGLM to locate UI elements on screen.

    This class sends screenshots to AutoGLM with a description
    of what to find, and parses the response to extract coordinates.
    """

    SYSTEM_PROMPT = """你是一个 UI 元素定位专家。你的任务是根据用户的描述找到目标元素的位置。

输出格式：
- 如果找到目标元素，输出：do(action="Tap", element=[x, y])
  - 坐标使用绝对像素坐标，直接表示屏幕上的像素位置
  - [0, 0] 是屏幕左上角
  - [屏幕宽度, 屏幕高度] 是屏幕右下角
  - 例如：1080x1920 屏幕的中心点是 [540, 960]
- 如果未找到目标元素，输出：finish(message="未找到: 原因说明")

重要：
- 只输出坐标定位结果，不要执行任何操作
- **坐标必须返回目标元素的中心位置（Center Point）**
  - 不是元素的边缘或角落，而是元素的几何中心
  - 对于矩形元素，返回 (left + width/2, top + height/2)
  - 对于圆形/椭圆元素，返回圆心坐标
- 如果有多个匹配项，选择最明显/最相关的一个
- 返回的坐标必须是实际的像素坐标，不是相对坐标"""

    def __init__(self, model_config: ModelConfig | None = None):
        """
        Initialize the locator.

        Args:
            model_config: Optional model configuration. Uses default if not provided.
        """
        self.config = model_config or ModelConfig()
        self.client = ModelClient(self.config)

    def locate(
        self,
        screenshot_b64: str,
        description: str,
        screen_width: int | None = None,
        screen_height: int | None = None
    ) -> LocateResult:
        """
        Locate a UI element based on description.

        Args:
            screenshot_b64: Base64-encoded screenshot.
            description: Natural language description of the element to find.
            screen_width: Optional screen width in pixels for context.
            screen_height: Optional screen height in pixels for context.

        Returns:
            LocateResult with coordinates if found.
        """
        # 构建用户提示，包含屏幕尺寸信息
        user_text = f"请定位: {description}"
        # if screen_width and screen_height:
        #     user_text = f"当前屏幕尺寸: {screen_width}x{screen_height} 像素\n\n{user_text}\n\n请返回绝对像素坐标（范围：x: 0-{screen_width}, y: 0-{screen_height}）"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
                    },
                    {"type": "text", "text": user_text},
                ],
            },
        ]

        try:
            response = self.client.request(messages)
            return self._parse_response(response.action, response.thinking)
        except Exception as e:
            return LocateResult(
                found=False,
                error=str(e),
                raw_response="",
            )

    def _parse_response(self, action: str, thinking: str) -> LocateResult:
        """
        Parse the model response to extract coordinates.

        Args:
            action: The action string from the model.
            thinking: The thinking/reasoning from the model.

        Returns:
            Parsed LocateResult.
        """
        # Try to find element coordinates in response
        # Pattern: element=[x, y] or element=[x,y]
        match = re.search(r'element=\[(\d+),\s*(\d+)\]', action)

        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            return LocateResult(
                found=True,
                element=(x, y),
                thinking=thinking,
                raw_response=action,
            )

        # Check for finish message (not found)
        if "finish" in action.lower() or "未找到" in action:
            return LocateResult(
                found=False,
                thinking=thinking,
                raw_response=action,
            )

        # Unknown response format
        return LocateResult(
            found=False,
            thinking=thinking,
            raw_response=action,
            error="Unable to parse response",
        )

    def locate_and_describe(
        self,
        screenshot_b64: str,
        description: str
    ) -> tuple[LocateResult, str]:
        """
        Locate an element and provide a description of what was found.

        This is useful for getting both the location and context.

        Args:
            screenshot_b64: Base64-encoded screenshot.
            description: What to look for.

        Returns:
            Tuple of (LocateResult, context_description).
        """
        result = self.locate(screenshot_b64, description)

        context = ""
        if result.found:
            context = f"找到 '{description}' 在位置 {result.element}"
        elif result.thinking:
            context = result.thinking
        else:
            context = f"未找到 '{description}'"

        return result, context

    ANALYZE_SCREEN_PROMPT = """你是手机界面分析专家。分析屏幕截图后，直接输出一个 JSON 对象。

禁止使用 finish()、do() 或任何函数调用格式。禁止输出 markdown。只输出纯 JSON。

输出格式：
{"current_screen": "当前界面简短描述", "interactive_elements": [{"name": "元素名称", "type": "button", "location": "位置描述", "state": "可点击", "center": [500, 300]}], "finger_guide": null, "suggested_actions": ["建议操作1"]}

字段说明：
- current_screen: 一句话描述当前界面（如"微信聊天列表"、"游戏主界面"）
- interactive_elements: 5-15 个可交互元素，每个包含：
  - name: 元素名称
  - type: button/input/icon/tab/link/switch/other
  - location: 方位描述（如"顶部居中"/"底部右侧"）
  - state: 可点击/不可点击/已选中/已禁用
  - center: 元素中心点坐标 [x, y]，使用 0-1000 归一化坐标（[0,0]=左上角，[1000,1000]=右下角，[500,500]=屏幕中心）
- finger_guide: 手指引导图标指向的位置（没有则为 null）
- suggested_actions: 2-3 个建议操作

只关注可交互元素，忽略装饰性内容。灰色按钮=不可点击，蓝色/金色按钮=可点击。
center 坐标必须精确标注每个元素的视觉中心位置。"""

    def analyze_screen(self, screenshot_b64: str, task_context: str = "") -> ScreenAnalysis:
        """
        Analyze the screen content using AutoGLM.

        Args:
            screenshot_b64: Base64-encoded screenshot.
            task_context: Optional context about the current task.

        Returns:
            ScreenAnalysis with structured screen information.
        """
        user_prompt = "请分析这个手机屏幕截图。"
        if task_context:
            user_prompt += f"\n\n当前任务背景：{task_context}"

        messages = [
            {"role": "system", "content": self.ANALYZE_SCREEN_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
                    },
                    {"type": "text", "text": user_prompt},
                ],
            },
        ]

        try:
            response = self.client.request(messages)
            return self._parse_analysis_response(response.raw_content)
        except Exception as e:
            return ScreenAnalysis(
                current_screen="分析失败",
                interactive_elements=[],
                visible_elements=[],
                suggested_actions=[],
                error=str(e),
            )

    @staticmethod
    def _try_parse_json(text: str) -> dict | None:
        """Try to extract a JSON dict from text. Returns None on failure."""
        import json as json_lib

        # Try ```json ... ``` block
        m = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if m:
            try:
                obj = json_lib.loads(m.group(1))
                if isinstance(obj, dict):
                    return obj
            except json_lib.JSONDecodeError:
                pass

        # Try raw JSON object (greedy match outermost braces)
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            try:
                obj = json_lib.loads(m.group(0))
                if isinstance(obj, dict):
                    return obj
            except json_lib.JSONDecodeError:
                pass

        return None

    def _parse_analysis_response(self, content: str) -> ScreenAnalysis:
        """
        Parse the screen analysis response.

        Args:
            content: Raw response content from the model.

        Returns:
            Parsed ScreenAnalysis.
        """
        # 1. Try to parse JSON directly from the full content
        data = self._try_parse_json(content)

        # 2. Fallback: extract content from finish(message="...") and try again
        if data is None:
            finish_match = re.search(
                r'finish\(message=["\'](.+?)["\']\)\s*$', content, re.DOTALL
            )
            if finish_match:
                inner = finish_match.group(1)
                data = self._try_parse_json(inner)

        if data and isinstance(data, dict):
            return self._build_analysis_from_dict(data, content)

        # Fallback: treat entire content as description
        description = content.strip()
        if len(description) > 1000:
            description = description[:1000] + "..."

        return ScreenAnalysis(
            current_screen=description,
            interactive_elements=[],
            visible_elements=[],
            suggested_actions=[],
            raw_response=content,
        )

    @staticmethod
    def _build_analysis_from_dict(data: dict, raw_content: str) -> ScreenAnalysis:
        """Build ScreenAnalysis from a parsed JSON dict."""
        current_screen = (
            data.get("current_screen", "")
            or data.get("current_app", "未知界面")
        )

        # Parse interactive_elements (new format)
        interactive_elements: list[InteractiveElement] = []
        for item in data.get("interactive_elements", []):
            if isinstance(item, dict):
                center = item.get("center")
                if isinstance(center, list) and len(center) == 2:
                    center = [int(c) for c in center]
                else:
                    center = None
                interactive_elements.append(InteractiveElement(
                    name=item.get("name", ""),
                    type=item.get("type", "other"),
                    location=item.get("location", ""),
                    state=item.get("state", "可点击"),
                    center=center,
                ))

        # Build flat visible_elements list for backward compat
        visible_elements = data.get("visible_elements", [])
        if not visible_elements and interactive_elements:
            visible_elements = [e.name for e in interactive_elements]

        return ScreenAnalysis(
            current_screen=current_screen,
            interactive_elements=interactive_elements,
            visible_elements=visible_elements,
            suggested_actions=data.get("suggested_actions", []),
            finger_guide=data.get("finger_guide"),
            raw_response=raw_content,
        )
