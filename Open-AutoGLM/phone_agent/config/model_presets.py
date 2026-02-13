"""
模型预设配置

通过 MODEL_PROVIDER 环境变量选择预设，一键切换 base_url / model_name 等配置。
个别环境变量（AUTOGLM_BASE_URL、AUTOGLM_MODEL、AUTOGLM_MAX_TOKENS）仍可覆盖预设值。
"""

MODEL_PRESETS = {
    "autoglm": {
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "api_key": "6bf14117ee8944db8da1f9e459932ca3.woLcpLDjyW64Yp6O",
        "model_name": "AutoGLM-Phone-Multilingual-disabled",
        "max_tokens": 4096,
    },
    "zhipu": {
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "api_key": "6bf14117ee8944db8da1f9e459932ca3.woLcpLDjyW64Yp6O",
        "model_name": "GLM-4.6V-Flash",
        "max_tokens": 4096,
    },
    "aliyun": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": "",
        "model_name": "qwen-vl-max",
        "max_tokens": 4096,
    },
}

DEFAULT_PROVIDER = "zhipu"


def get_preset(provider: str) -> dict:
    """获取模型预设，不存在则抛出 ValueError。"""
    key = provider.lower()
    if key not in MODEL_PRESETS:
        available = ", ".join(sorted(MODEL_PRESETS.keys()))
        raise ValueError(
            f"未知的 MODEL_PROVIDER: {provider!r}，可选值: {available}"
        )
    return MODEL_PRESETS[key]
