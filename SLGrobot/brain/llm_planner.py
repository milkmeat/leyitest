"""LLM Planner - Strategic planning via LLM (3-10s, called infrequently).

Supports multiple LLM providers:
- Anthropic (Claude): native SDK
- OpenAI-compatible (Zhipu GLM, DeepSeek, etc.): OpenAI SDK

Sends grid-annotated screenshots + concise state summaries to LLM.
Parses JSON response into Task list for the task queue.
Called every ~30 minutes or when encountering unknown situations.
"""

import json
import logging
import time
from datetime import datetime

import numpy as np

import config
from vision.grid_overlay import GridOverlay
from state.game_state import GameState
from utils.image_utils import to_base64, resize
from .task_queue import Task

logger = logging.getLogger(__name__)

# System prompt for strategic planning
STRATEGIC_PROMPT = """\
You are an AI advisor for a mobile SLG game called "Frozen Island" (冰封岛屿).
You see a grid-annotated screenshot of the game. The grid uses column letters (A-H) \
and row numbers (1-6). You also receive a game state summary.

Your job: analyze the current situation and produce a prioritized task plan.

Rules:
- Output ONLY valid JSON, no markdown fences, no explanation outside JSON.
- Each task must use one of these types: collect_resources, upgrade_building, \
train_troops, claim_rewards, navigate_main_city, navigate_world_map, \
close_popup, check_mail, collect_daily, gather_resource, scout_enemy, \
send_troops, custom.
- For "custom" tasks, provide an "actions" array with step-by-step action dicts.
- Prioritize: immediate rewards > building upgrades > troop training > exploration.
- Do NOT produce more than 10 tasks.

Output format:
{
    "reasoning": "Brief explanation of your strategy",
    "tasks": [
        {"name": "task_type", "priority": 10, "params": {}},
        {"name": "upgrade_building", "priority": 8, "params": {"building_name": "barracks"}},
        {"name": "custom", "priority": 5, "params": {}, "actions": [
            {"type": "tap", "target_text": "Upgrade", "fallback_grid": "C4"},
            {"type": "wait", "seconds": 1}
        ]}
    ]
}
"""

# System prompt for unknown scene analysis
UNKNOWN_SCENE_PROMPT = """\
You are an AI advisor for a mobile SLG game called "Frozen Island" (冰封岛屿).
You see a grid-annotated screenshot of an UNKNOWN or unexpected game screen.
The grid uses column letters (A-H) and row numbers (1-6).

Your job: analyze what is on screen and suggest actions to handle it.

Rules:
- Output ONLY valid JSON, no markdown fences.
- Suggest 1-5 actions to navigate back to a known state.
- Prefer safe actions: close buttons, back buttons, confirm buttons.
- Use grid cells (e.g., "C4") for fallback positions.

Output format:
{
    "scene_description": "What you see on screen",
    "actions": [
        {"type": "tap", "target_text": "Close", "fallback_grid": "H1"},
        {"type": "tap", "target_text": "确定", "fallback_grid": "D4"}
    ]
}
"""

# System prompt for quest execution analysis
QUEST_EXECUTION_PROMPT = """\
You are an AI advisor for a mobile SLG game called "Frozen Island" (冰封岛屿).
The player is currently executing a quest: "{quest_name}".
You see a grid-annotated screenshot of the game. The grid uses column letters (A-H) \
and row numbers (1-6).

Your job: analyze the screenshot and suggest 1-5 actions to progress or complete the quest.

Rules:
- Output ONLY valid JSON, no markdown fences, no explanation outside JSON.
- If the quest looks completed, suggest actions to return to main city.
- Prefer safe, minimal actions: tap visible buttons, follow UI prompts.
- Use grid cells (e.g., "C4") for fallback positions.

Output format:
{{
    "scene_description": "What you see on screen",
    "quest_status": "in_progress | completed | unclear",
    "actions": [
        {{"type": "tap", "target_text": "Button text", "fallback_grid": "C4"}},
        {{"type": "key_event", "keycode": 4}}
    ]
}}
"""


class LLMPlanner:
    """Multi-provider LLM strategic planner.

    Supports Anthropic (Claude) and OpenAI-compatible APIs (Zhipu GLM, etc.).
    Sends annotated screenshot + state summary to LLM.
    Parses JSON response into Task list.
    Called every ~30 minutes or when encountering unknown situations.
    """

    def __init__(self, api_key: str = None, model: str = None,
                 grid_overlay: GridOverlay = None,
                 provider: str = None, base_url: str = None,
                 vision_model: str = None) -> None:
        self.api_key = api_key if api_key is not None else config.LLM_API_KEY
        self.model = model if model is not None else config.LLM_MODEL
        self.vision_model = vision_model if vision_model is not None else getattr(config, "LLM_VISION_MODEL", self.model)
        self.max_tokens = config.LLM_MAX_TOKENS
        self.provider = provider if provider is not None else getattr(config, "LLM_PROVIDER", "anthropic")
        self.base_url = base_url if base_url is not None else getattr(config, "LLM_BASE_URL", "")
        self.grid = grid_overlay
        self.consult_interval = config.LLM_CONSULT_INTERVAL
        self._client = None

    def _get_client(self):
        """Lazy-initialize the API client based on provider."""
        if self._client is not None:
            return self._client

        if not self.api_key:
            raise RuntimeError(
                "LLM API key not set. Configure it in model_presets.py "
                "or set the appropriate environment variable."
            )

        if self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise RuntimeError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
        elif self.provider == "openai_compatible":
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except ImportError:
                raise RuntimeError(
                    "openai package not installed. Run: pip install openai"
                )
        else:
            raise RuntimeError(f"Unknown LLM provider: '{self.provider}'")

        return self._client

    def get_plan(self, screenshot: np.ndarray,
                 game_state: GameState) -> list[Task]:
        """Send annotated screenshot + state summary to LLM.

        Parse JSON response into Task list.
        Called every ~30 minutes or when encountering unknown situations.

        Args:
            screenshot: BGR numpy array of current game screen.
            game_state: Current game state.

        Returns:
            List of Task objects for the task queue.
        """
        logger.info(f"Consulting LLM ({self.provider}/{self.vision_model}) for strategic plan...")

        # Prepare annotated screenshot
        annotated = self._prepare_screenshot(screenshot)
        image_b64 = to_base64(annotated)

        # Prepare state summary
        state_summary = game_state.summary_for_llm()

        user_text = (
            f"Current game state:\n{state_summary}\n\n"
            f"Analyze the screenshot and produce a strategic task plan."
        )

        # Call LLM API
        try:
            response = self._call_vision_api(
                STRATEGIC_PROMPT, image_b64, user_text
            )
            tasks = self._parse_plan_response(response)
            game_state.last_llm_consult = datetime.now().isoformat()
            logger.info(f"LLM plan: {len(tasks)} tasks generated")
            return tasks
        except Exception as e:
            logger.error(f"LLM planning failed: {e}")
            return []

    def analyze_unknown_scene(self, screenshot: np.ndarray,
                               game_state: GameState) -> list[dict]:
        """Ask LLM to analyze an unknown/unexpected screen and suggest actions.

        Args:
            screenshot: BGR numpy array.
            game_state: Current game state.

        Returns:
            List of action dicts.
        """
        logger.info(f"Consulting LLM ({self.provider}/{self.vision_model}) for unknown scene...")

        annotated = self._prepare_screenshot(screenshot)
        image_b64 = to_base64(annotated)

        state_summary = game_state.summary_for_llm()
        user_text = (
            f"Current game state:\n{state_summary}\n\n"
            f"This is an unknown/unexpected screen. "
            f"What do you see? How should I handle it?"
        )

        try:
            response = self._call_vision_api(
                UNKNOWN_SCENE_PROMPT, image_b64, user_text
            )
            actions = self._parse_scene_response(response)
            logger.info(f"LLM scene analysis: {len(actions)} actions suggested")
            return actions
        except Exception as e:
            logger.error(f"LLM scene analysis failed: {e}")
            return []

    def analyze_quest_execution(self, screenshot: np.ndarray,
                                quest_name: str,
                                game_state: GameState) -> list[dict]:
        """Ask LLM to analyze the screen and suggest actions to progress a quest.

        Args:
            screenshot: BGR numpy array.
            quest_name: Name of the quest being executed.
            game_state: Current game state.

        Returns:
            List of action dicts.
        """
        logger.info(
            f"Consulting LLM ({self.provider}/{self.vision_model}) "
            f"for quest execution: '{quest_name}'"
        )

        annotated = self._prepare_screenshot(screenshot)
        image_b64 = to_base64(annotated)

        state_summary = game_state.summary_for_llm()
        system_prompt = QUEST_EXECUTION_PROMPT.format(quest_name=quest_name)
        user_text = (
            f"Current game state:\n{state_summary}\n\n"
            f"I am executing quest: \"{quest_name}\". "
            f"What actions should I take to progress or complete this quest?"
        )

        try:
            response = self._call_vision_api(
                system_prompt, image_b64, user_text
            )
            actions = self._parse_scene_response(response)
            logger.info(f"LLM quest analysis: {len(actions)} actions suggested")
            return actions
        except Exception as e:
            logger.error(f"LLM quest analysis failed: {e}")
            return []

    def should_consult(self, game_state: GameState) -> bool:
        """Check if enough time has passed since last LLM consultation.

        Returns True if:
        - No API key configured -> returns False
        - Never consulted before -> True
        - More than consult_interval seconds since last -> True
        """
        if not self.api_key:
            return False

        if not game_state.last_llm_consult:
            return True

        try:
            last = datetime.fromisoformat(game_state.last_llm_consult)
            elapsed = (datetime.now() - last).total_seconds()
            return elapsed >= self.consult_interval
        except (ValueError, TypeError):
            return True

    def _prepare_screenshot(self, screenshot: np.ndarray) -> np.ndarray:
        """Prepare screenshot for LLM: add grid overlay and resize.

        Resizes to max 1024px on the long side to reduce token usage
        while keeping grid labels readable.
        """
        # Add grid overlay
        if self.grid:
            annotated = self.grid.annotate(screenshot)
        else:
            annotated = screenshot.copy()

        # Resize to reduce API token cost
        h, w = annotated.shape[:2]
        max_dim = 1024
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            annotated = resize(annotated, new_w, new_h)

        return annotated

    def _call_vision_api(self, system_prompt: str, image_b64: str,
                          user_text: str) -> str:
        """Call LLM API with a vision (image + text) request.

        Dispatches to the appropriate provider implementation.

        Args:
            system_prompt: System-level instruction.
            image_b64: Base64-encoded PNG image.
            user_text: User text message.

        Returns:
            Raw text response from LLM.
        """
        if self.provider == "anthropic":
            return self._call_anthropic(system_prompt, image_b64, user_text)
        elif self.provider == "openai_compatible":
            return self._call_openai_compatible(system_prompt, image_b64, user_text)
        else:
            raise RuntimeError(f"Unknown provider: '{self.provider}'")

    def _call_anthropic(self, system_prompt: str, image_b64: str,
                         user_text: str) -> str:
        """Call Anthropic Claude API."""
        client = self._get_client()

        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_b64,
                },
            },
            {
                "type": "text",
                "text": user_text,
            },
        ]

        start_time = time.time()
        response = client.messages.create(
            model=self.vision_model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_content},
            ],
        )
        elapsed = time.time() - start_time

        text = ""
        for block in response.content:
            if block.type == "text":
                text += block.text

        logger.info(
            f"Anthropic API: {elapsed:.1f}s, "
            f"input_tokens={response.usage.input_tokens}, "
            f"output_tokens={response.usage.output_tokens}"
        )
        logger.debug(f"LLM response: {text[:500]}")
        return text

    def _call_openai_compatible(self, system_prompt: str, image_b64: str,
                                 user_text: str) -> str:
        """Call OpenAI-compatible API (Zhipu GLM, DeepSeek, etc.)."""
        client = self._get_client()

        # OpenAI vision format: image_url with base64 data URI
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": user_text,
                    },
                ],
            },
        ]

        start_time = time.time()
        response = client.chat.completions.create(
            model=self.vision_model,
            max_tokens=self.max_tokens,
            messages=messages,
        )
        elapsed = time.time() - start_time

        text = response.choices[0].message.content or ""
        usage = response.usage
        logger.info(
            f"OpenAI-compat API: {elapsed:.1f}s, "
            f"input_tokens={usage.prompt_tokens if usage else '?'}, "
            f"output_tokens={usage.completion_tokens if usage else '?'}"
        )
        logger.debug(f"LLM response: {text[:500]}")
        return text

    def _parse_plan_response(self, response: str) -> list[Task]:
        """Parse LLM strategic plan JSON into Task objects.

        Handles common JSON issues: markdown fences, extra text.
        """
        data = self._extract_json(response)
        if data is None:
            logger.error("Failed to parse LLM plan response as JSON")
            return []

        tasks = []
        reasoning = data.get("reasoning", "")
        if reasoning:
            logger.info(f"LLM reasoning: {reasoning}")

        for i, task_data in enumerate(data.get("tasks", [])):
            name = task_data.get("name", "custom")
            priority = task_data.get("priority", 5 - i)  # Decreasing priority
            params = task_data.get("params", {})

            # If it's a custom task with inline actions, store them in params
            if "actions" in task_data:
                params["actions"] = task_data["actions"]

            task = Task(
                name=name,
                priority=priority,
                params=params,
            )
            tasks.append(task)

        return tasks

    def _parse_scene_response(self, response: str) -> list[dict]:
        """Parse LLM unknown scene analysis into action dicts."""
        data = self._extract_json(response)
        if data is None:
            logger.error("Failed to parse LLM scene response as JSON")
            return []

        scene_desc = data.get("scene_description", "")
        if scene_desc:
            logger.info(f"LLM scene description: {scene_desc}")

        return data.get("actions", [])

    def _extract_json(self, text: str) -> dict | None:
        """Extract JSON from LLM response, handling common issues.

        Handles:
        - Pure JSON response
        - JSON inside markdown code fences
        - Extra text before/after JSON
        """
        text = text.strip()

        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strip markdown fences
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                # Remove language identifier (e.g., "json\n")
                if part.startswith("json"):
                    part = part[4:].strip()
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    continue

        # Try to find JSON object in text
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        return None
