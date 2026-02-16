"""Model Presets - Pre-configured LLM provider settings.

Supports easy switching between different LLM providers.
Each preset contains connection info and model names for both
text and vision tasks.

Usage:
    from model_presets import PRESETS, get_preset
    preset = get_preset("zhipu")
    print(preset["base_url"], preset["model_name"])

To add a new provider, add an entry to the PRESETS dict below.
"""

import os

PRESETS: dict[str, dict] = {
    "zhipu": {
        "provider": "openai_compatible",
        "base_url": "https://api.z.ai/api/coding/paas/v4",
        "api_key": "6bf14117ee8944db8da1f9e459932ca3.woLcpLDjyW64Yp6O",
        "model_name": "GLM-4.6",       # Text model
        "vision_model": "GLM-4.6V",    # Vision model (for screenshots)
        "max_tokens": 4096,
    },
    "anthropic": {
        "provider": "anthropic",
        "base_url": "",  # Uses default Anthropic endpoint
        "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "model_name": "claude-sonnet-4-20250514",
        "vision_model": "claude-sonnet-4-20250514",  # Same model handles vision
        "max_tokens": 1024,
    },
    # Example: add more providers here
    # "openai": {
    #     "provider": "openai_compatible",
    #     "base_url": "https://api.openai.com/v1",
    #     "api_key": os.environ.get("OPENAI_API_KEY", ""),
    #     "model_name": "gpt-4o",
    #     "vision_model": "gpt-4o",
    #     "max_tokens": 4096,
    # },
    # "deepseek": {
    #     "provider": "openai_compatible",
    #     "base_url": "https://api.deepseek.com",
    #     "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
    #     "model_name": "deepseek-chat",
    #     "vision_model": "deepseek-chat",
    #     "max_tokens": 4096,
    # },
}

# Active preset name - change this to switch providers
ACTIVE_PRESET = "zhipu"


def get_preset(name: str = None) -> dict:
    """Get a model preset by name.

    Args:
        name: Preset name (e.g., "zhipu", "anthropic").
              Defaults to ACTIVE_PRESET.

    Returns:
        Preset configuration dict.

    Raises:
        KeyError: If preset name not found.
    """
    name = name or ACTIVE_PRESET
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]


def get_active_preset() -> dict:
    """Get the currently active model preset."""
    return get_preset(ACTIVE_PRESET)
