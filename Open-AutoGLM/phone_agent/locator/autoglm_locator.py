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
class ScreenAnalysis:
    """Result of screen analysis by AutoGLM."""

    current_screen: str  # Description of the current screen
    visible_elements: list[str]  # List of visible UI elements
    suggested_actions: list[str]  # Suggested next actions
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
- 坐标应该指向目标元素的中心位置
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
        if screen_width and screen_height:
            user_text = f"当前屏幕尺寸: {screen_width}x{screen_height} 像素\n\n{user_text}\n\n请返回绝对像素坐标（范围：x: 0-{screen_width}, y: 0-{screen_height}）"

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

    ANALYZE_SCREEN_PROMPT = """你是手机界面分析专家。用简洁的语言分析屏幕，包含以下信息：

**必须包含的信息：**
1. 当前界面：简短描述（如：微信聊天列表、淘宝商品详情）
2. 主要元素：列出5-10个可见的关键UI元素（如：搜索框、发送按钮、返回键等）
3. 如果屏幕上有手指图标，说明其指向的坐标位置
4. 建议操作：2-3个合理的下一步操作

**要求：**
- 描述简洁明了，每项信息1-2句话
- 聚焦可交互元素，忽略纯装饰性内容
- 避免冗长分析，直奔主题
- 总字数控制在200字以内"""

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
                visible_elements=[],
                suggested_actions=[],
                error=str(e),
            )

    def _parse_analysis_response(self, content: str) -> ScreenAnalysis:
        """
        Parse the screen analysis response.

        Args:
            content: Raw response content from the model.

        Returns:
            Parsed ScreenAnalysis.
        """
        import json as json_lib

        # Try to extract JSON from the response (for backward compatibility)
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if json_match:
            json_str = json_match.group(1)
            try:
                data = json_lib.loads(json_str)
                return ScreenAnalysis(
                    current_screen=data.get("current_screen", "") or data.get("current_app", "未知界面"),
                    visible_elements=data.get("visible_elements", []),
                    suggested_actions=data.get("suggested_actions", []),
                    raw_response=content,
                )
            except json_lib.JSONDecodeError:
                pass

        # Try to find raw JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                data = json_lib.loads(json_match.group(0))
                return ScreenAnalysis(
                    current_screen=data.get("current_screen", "") or data.get("current_app", "未知界面"),
                    visible_elements=data.get("visible_elements", []),
                    suggested_actions=data.get("suggested_actions", []),
                    raw_response=content,
                )
            except json_lib.JSONDecodeError:
                pass

        # Parse natural language response (new default)
        # Extract finish message if present
        finish_match = re.search(r'finish\(message=["\'](.+?)["\']\)', content, re.DOTALL)
        if finish_match:
            description = finish_match.group(1)
        else:
            # Use content after thinking, or full content
            parts = content.split('finish(', 1)
            if len(parts) > 1:
                description = parts[1].split(')', 1)[0]
                # Remove message= prefix if present
                description = re.sub(r'^message=["\']|["\']$', '', description)
            else:
                description = content

        # Clean up and limit length
        description = description.strip()
        if len(description) > 1000:
            description = description[:1000] + "..."

        return ScreenAnalysis(
            current_screen=description,
            visible_elements=[],
            suggested_actions=[],
            raw_response=content,
        )
