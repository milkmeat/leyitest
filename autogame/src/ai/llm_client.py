"""LLM 客户端 — 智谱 GLM / OpenAI 兼容接口

通过 openai.AsyncOpenAI 调用智谱 API (OpenAI 兼容模式)。

功能:
- chat_json(): system+user prompt → JSON mode → parsed dict
- 超时控制 (asyncio.wait_for)
- 简单重试 (max_retries)
- dry_run 模式: 返回预设 JSON，测试无需 API key

用法:
    client = LLMClient(config.system.llm)
    result = await client.chat_json(system_prompt, user_prompt)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from src.config.schemas import LLMConfig

logger = logging.getLogger(__name__)

# dry_run 模式下返回的预设响应
_DRY_RUN_RESPONSE = {
    "thinking": "dry_run 模式，跳过 LLM 调用",
    "instructions": [
        {
            "action": "SCOUT",
            "uid": 0,
            "target_uid": 0,
            "target_x": 500,
            "target_y": 500,
            "reason": "dry_run 预设指令",
        }
    ],
}


class LLMClient:
    """OpenAI 兼容 LLM 客户端

    支持智谱 GLM、OpenAI、以及任何兼容 OpenAI Chat Completions 接口的服务。
    """

    def __init__(self, config: LLMConfig, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self._client = None

        if not dry_run:
            api_key = config.api_key or os.environ.get("ZHIPU_API_KEY", "")
            if not api_key:
                raise ValueError(
                    "LLM API key 未配置: 请设置 config.llm.api_key "
                    "或环境变量 ZHIPU_API_KEY"
                )
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError(
                    "openai 包未安装，请运行: pip install openai>=1.10"
                )
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=config.base_url,
            )

    async def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """发送 chat 请求并解析 JSON 响应

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 生成温度

        Returns:
            解析后的 JSON dict

        Raises:
            asyncio.TimeoutError: 超时
            ValueError: JSON 解析失败
        """
        if self.dry_run:
            logger.info("[dry_run] 返回预设 JSON")
            return _DRY_RUN_RESPONSE

        last_error = None
        attempts = 1 + self.config.max_retries

        for attempt in range(attempts):
            try:
                result = await asyncio.wait_for(
                    self._call_api(system_prompt, user_prompt, temperature),
                    timeout=self.config.timeout_seconds,
                )
                return result
            except asyncio.TimeoutError:
                last_error = asyncio.TimeoutError(
                    f"LLM 调用超时 ({self.config.timeout_seconds}s)"
                )
                logger.warning(
                    "LLM 超时 (attempt %d/%d)", attempt + 1, attempts
                )
            except Exception as e:
                last_error = e
                logger.warning(
                    "LLM 调用失败 (attempt %d/%d): %s", attempt + 1, attempts, e
                )

        raise last_error  # type: ignore[misc]

    async def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> dict[str, Any]:
        """实际 API 调用"""
        assert self._client is not None

        # 记录输入
        logger.info(
            "=== LLM 请求 ===\n"
            "[system_prompt] (%d chars):\n%s\n\n"
            "[user_prompt] (%d chars):\n%s",
            len(system_prompt), system_prompt,
            len(user_prompt), user_prompt,
        )

        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM 返回空内容")

        # 记录原始输出
        usage = response.usage
        usage_str = ""
        if usage:
            usage_str = (
                f" (tokens: prompt={usage.prompt_tokens}, "
                f"completion={usage.completion_tokens}, "
                f"total={usage.total_tokens})"
            )
        logger.info(
            "=== LLM 响应 ===%s\n%s",
            usage_str, content,
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("JSON 解析失败: %s\n原始内容: %s", e, content[:500])
            raise ValueError(f"LLM 返回非法 JSON: {e}") from e

    async def close(self):
        """关闭底层 HTTP 客户端"""
        if self._client is not None:
            await self._client.close()
