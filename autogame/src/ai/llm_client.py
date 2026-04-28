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

import yaml

from src.config.schemas import LLMConfig

logger = logging.getLogger(__name__)

# dry_run 模式下返回的预设响应
_DRY_RUN_RESPONSE = {
    "instructions": [
        {
            "action": "SCOUT",
            "uid": 0,
            "target_uid": 0,
            "target_x": 500,
            "target_y": 500,
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
            api_key = (
                config.api_key
                or os.environ.get("ZHIPU_API_KEY", "")
            )
            if not api_key:
                raise ValueError(
                    "LLM API key 未配置: 请创建 config/llm_secret.yaml "
                    "或设置环境变量 ZHIPU_API_KEY"
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
        context: str = "",
    ) -> dict[str, Any]:
        """发送 chat 请求并解析 JSON 响应

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 生成温度
            context: 调用上下文（用于日志，如 "L1 squad=1"）

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

        # 构建上下文信息用于日志
        ctx_prefix = f"[{context}] " if context else ""

        for attempt in range(attempts):
            try:
                logger.info("%s开始 LLM 调用 (attempt %d/%d, timeout=%ds)",
                           ctx_prefix, attempt + 1, attempts, self.config.timeout_seconds)

                result = await asyncio.wait_for(
                    self._call_api(system_prompt, user_prompt, temperature, ctx_prefix, output_format="json"),
                    timeout=self.config.timeout_seconds,
                )
                return result
            except asyncio.TimeoutError:
                last_error = asyncio.TimeoutError(
                    f"LLM 调用超时 ({self.config.timeout_seconds}s)"
                )
                # 超时时显示请求摘要
                user_preview = user_prompt[:200] + "..." if len(user_prompt) > 200 else user_prompt
                logger.warning(
                    "%sLLM 超时 (attempt %d/%d, timeout=%ds)\n"
                    "  发送内容摘要:\n"
                    "    system_prompt: %d chars\n"
                    "    user_prompt: %s",
                    ctx_prefix, attempt + 1, attempts, self.config.timeout_seconds,
                    len(system_prompt), user_preview,
                )
            except Exception as e:
                last_error = e
                # 429 速率限制: 指数退避
                is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
                backoff = (2 ** attempt) * (3 if is_rate_limit else 1)
                logger.warning(
                    "%sLLM 调用失败 (attempt %d/%d): %s — 等待 %ds",
                    ctx_prefix, attempt + 1, attempts, e, backoff,
                )
                if attempt < attempts - 1:
                    await asyncio.sleep(backoff)

        raise last_error  # type: ignore[misc]

    async def chat_yaml(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        context: str = "",
    ) -> dict[str, Any]:
        """发送 chat 请求并解析 YAML 响应（比 JSON 节省 30-40% output tokens）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 生成温度
            context: 调用上下文（用于日志，如 "L1 squad=1"）

        Returns:
            解析后的 dict

        Raises:
            asyncio.TimeoutError: 超时
            ValueError: YAML 解析失败
        """
        if self.dry_run:
            logger.info("[dry_run] 返回预设 YAML")
            return _DRY_RUN_RESPONSE

        last_error = None
        attempts = 1 + self.config.max_retries

        # 构建上下文信息用于日志
        ctx_prefix = f"[{context}] " if context else ""

        for attempt in range(attempts):
            try:
                logger.info("%s开始 LLM 调用 (attempt %d/%d, timeout=%ds)",
                           ctx_prefix, attempt + 1, attempts, self.config.timeout_seconds)

                result = await asyncio.wait_for(
                    self._call_api(system_prompt, user_prompt, temperature, ctx_prefix, output_format="yaml"),
                    timeout=self.config.timeout_seconds,
                )
                return result
            except asyncio.TimeoutError:
                last_error = asyncio.TimeoutError(
                    f"LLM 调用超时 ({self.config.timeout_seconds}s)"
                )
                user_preview = user_prompt[:200] + "..." if len(user_prompt) > 200 else user_prompt
                logger.warning(
                    "%sLLM 超时 (attempt %d/%d, timeout=%ds)\n"
                    "  发送内容摘要:\n"
                    "    system_prompt: %d chars\n"
                    "    user_prompt: %s",
                    ctx_prefix, attempt + 1, attempts, self.config.timeout_seconds,
                    len(system_prompt), user_preview,
                )
            except Exception as e:
                last_error = e
                is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
                backoff = (2 ** attempt) * (3 if is_rate_limit else 1)
                logger.warning(
                    "%sLLM 调用失败 (attempt %d/%d): %s — 等待 %ds",
                    ctx_prefix, attempt + 1, attempts, e, backoff,
                )
                if attempt < attempts - 1:
                    await asyncio.sleep(backoff)

        raise last_error  # type: ignore[misc]

    async def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        ctx_prefix: str = "",
        output_format: str = "json",
    ) -> dict[str, Any]:
        """实际 API 调用

        Args:
            output_format: "json" 或 "yaml"，决定解析方式
        """
        assert self._client is not None

        import time
        start_time = time.time()

        # 记录输入
        logger.info(
            "%s=== LLM 请求开始 ===\n"
            "  [system_prompt] (%d chars)\n"
            "  [user_prompt] (%d chars)\n"
            "  [model] %s\n"
            "  [temperature] %.1f\n"
            "  [output_format] %s",
            ctx_prefix,
            len(system_prompt),
            len(user_prompt),
            self.config.model,
            temperature,
            output_format,
        )
        logger.debug("%ssystem_prompt:\n%s", ctx_prefix, system_prompt)
        logger.debug("%suser_prompt:\n%s", ctx_prefix, user_prompt)

        # Ollama 检测
        is_ollama = "localhost" in (self.config.base_url or "") or "11434" in (self.config.base_url or "")

        try:
            import sys as _sys

            if is_ollama:
                # Ollama: 使用原生 /api/chat（支持 think:false），不走 OpenAI 兼容端点
                content = await self._call_ollama_native(
                    system_prompt, user_prompt, temperature, ctx_prefix,
                )
            else:
                # 云端 API (zhipu/openai/deepseek): OpenAI SDK 流式调用
                stream = await self._client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    stream=True,
                )
                chunks = []
                _sys.stderr.write(f"{ctx_prefix}[stream] ")
                async for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices[0].delta else None
                    if delta and delta.content:
                        chunks.append(delta.content)
                        _sys.stderr.write(delta.content)
                        _sys.stderr.flush()
                _sys.stderr.write("\n")
                content = "".join(chunks)

            elapsed = time.time() - start_time
            if not content:
                raise ValueError("LLM 返回空内容")

            logger.info(
                "%s=== LLM 响应成功 ===\n"
                "  [耗时] %.2fs\n"
                "  [内容长度] %d chars",
                ctx_prefix, elapsed, len(content),
            )
            logger.debug("%s完整响应内容:\n%s", ctx_prefix, content)

            if output_format == "yaml":
                return self._extract_yaml(content)
            else:
                return self._extract_json(content)
        except Exception as e:
            elapsed = time.time() - start_time
            error_type = type(e).__name__
            error_detail = str(e)

            # 提取有用的错误信息
            if "timeout" in error_detail.lower() or "timed out" in error_detail.lower():
                error_hint = "请求超时，可能是网络问题或 API 响应慢"
            elif "connection" in error_detail.lower():
                error_hint = "连接失败，请检查网络或 base_url 配置"
            elif "api_key" in error_detail.lower() or "auth" in error_detail.lower():
                error_hint = "API 密钥问题，请检查 llm_secret.yaml"
            elif "rate" in error_detail.lower() or "429" in error_detail:
                error_hint = "请求过于频繁，触发速率限制"
            else:
                error_hint = "未知错误"

            logger.error(
                "%s=== LLM API 异常 ===\n"
                "  [耗时] %.2fs\n"
                "  [错误类型] %s\n"
                "  [错误详情] %s\n"
                "  [提示] %s\n"
                "  [base_url] %s\n"
                "  [model] %s",
                ctx_prefix, elapsed, error_type, error_detail, error_hint,
                self.config.base_url, self.config.model,
            )
            raise

    async def _call_ollama_native(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        ctx_prefix: str = "",
    ) -> str:
        """Ollama 原生 API 调用（/api/chat），支持 think:false 禁用 thinking

        不走 OpenAI 兼容端点，因为 /v1/ 不转发 think 参数。
        使用 aiohttp 直接调用，流式输出到 stderr。
        """
        import sys as _sys
        import aiohttp
        import json as _json

        # 从 base_url 提取 Ollama host（去掉 /v1 后缀）
        base = (self.config.base_url or "").rstrip("/")
        if base.endswith("/v1"):
            base = base[:-3]
        url = f"{base}/api/chat"

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 16384,
            },
        }

        chunks = []
        _sys.stderr.write(f"{ctx_prefix}[ollama stream] ")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.content:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = _json.loads(line)
                    except _json.JSONDecodeError:
                        continue
                    msg = data.get("message", {})
                    content = msg.get("content", "")
                    if content:
                        chunks.append(content)
                        _sys.stderr.write(content)
                        _sys.stderr.flush()
                    if data.get("done"):
                        break
        _sys.stderr.write("\n")
        return "".join(chunks)

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """从 LLM 文本响应中提取 JSON

        支持三种格式：
        1. 纯 JSON 文本
        2. ```json ... ``` 代码块
        3. 混合文本中的第一个 { ... } 块
        """
        import re

        stripped = text.strip()

        # 1) 纯 JSON
        if stripped.startswith("{"):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass

        # 2) ```json ... ``` 代码块
        m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", stripped, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 3) 第一个 { ... } 块（贪婪匹配最外层大括号）
        brace_start = stripped.find("{")
        if brace_start >= 0:
            depth = 0
            for i in range(brace_start, len(stripped)):
                if stripped[i] == "{":
                    depth += 1
                elif stripped[i] == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(stripped[brace_start:i + 1])
                        except json.JSONDecodeError:
                            break

        logger.error("JSON 提取失败，原始内容: %s", stripped[:500])
        raise ValueError(f"无法从 LLM 响应中提取 JSON")

    @staticmethod
    def _extract_yaml(text: str) -> dict[str, Any]:
        """从 LLM 文本响应中提取 YAML

        支持三种格式：
        1. 纯 YAML 文本（以 thinking: 或 instructions: 开头）
        2. ```yaml ... ``` 代码块
        3. 混合文本中的第一个完整 YAML 结构
        """
        import re

        stripped = text.strip()

        # 1) ```yaml ... ``` 代码块
        m = re.search(r"```(?:yaml|yml)?\s*\n?(.*?)\n?```", stripped, re.DOTALL)
        if m:
            try:
                result = yaml.safe_load(m.group(1).strip())
                if isinstance(result, dict):
                    return result
            except yaml.YAMLError:
                pass

        # 2) 纯 YAML（以常见 key 开头）
        yaml_keys = ["thinking:", "instructions:", "action:", "orders:"]
        for key in yaml_keys:
            if stripped.startswith(key):
                try:
                    result = yaml.safe_load(stripped)
                    if isinstance(result, dict):
                        return result
                except yaml.YAMLError:
                    break

        # 3) 查找第一个 YAML 块（从 thinking: 或 instructions: 开始）
        for key in ["thinking:", "instructions:", "orders:"]:
            start = stripped.find(key)
            if start >= 0:
                # 尝试解析从该位置到末尾的内容
                yaml_content = stripped[start:]
                try:
                    result = yaml.safe_load(yaml_content)
                    if isinstance(result, dict):
                        return result
                except yaml.YAMLError:
                    # 尝试截断到下一个 Markdown 标记
                    end_patterns = ["\n\n# ", "\n\n---", "```"]
                    for pattern in end_patterns:
                        end = yaml_content.find(pattern)
                        if end > 0:
                            try:
                                result = yaml.safe_load(yaml_content[:end])
                                if isinstance(result, dict):
                                    return result
                            except yaml.YAMLError:
                                continue

        logger.error("YAML 提取失败，原始内容: %s", stripped[:500])
        raise ValueError(f"无法从 LLM 响应中提取 YAML")

    async def close(self):
        """关闭底层 HTTP 客户端"""
        if self._client is not None:
            await self._client.close()
