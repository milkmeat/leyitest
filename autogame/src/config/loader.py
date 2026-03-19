"""配置文件加载与校验

加载 config/ 目录下的 YAML 配置文件并通过 Pydantic schema 校验:
- accounts.yaml  — 账号配置（UID、名称）
- squads.yaml    — 小队分配
- activity.yaml  — 活动规则（积分、地图、时限）
- system.yaml    — 系统参数（循环间隔、LLM配置）

典型用法:
    cfg = load_all("config")
    print(cfg.accounts.active_uids())
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.config.schemas import (
    AccountsConfig,
    ActivityConfig,
    AllianceSquadGroup,
    AppConfig,
    LLMProfile,
    SquadsConfig,
    SystemConfig,
)


def load_yaml(path: str | Path) -> dict:
    """读取 YAML 文件并返回 dict

    Raises:
        FileNotFoundError: 文件不存在
        yaml.YAMLError: YAML 语法错误
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"配置文件不存在: {p}")
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    return data


def load_accounts(path: str | Path) -> AccountsConfig:
    """加载 accounts.yaml"""
    return AccountsConfig(**load_yaml(path))


def load_squads(path: str | Path) -> SquadsConfig:
    """加载 squads.yaml — 支持新旧两种格式

    新格式 (alliances dict):
        alliances:
          ours: {aid, name, squads: [...]}
          enemy: {aid, name, squads: [...]}

    旧格式 (向后兼容):
        squads: [...]
    """
    data = load_yaml(path)
    if "alliances" in data:
        return SquadsConfig(**data)
    # 旧格式兼容: 包装为单联盟 "ours"
    return SquadsConfig(alliances={
        "ours": AllianceSquadGroup(aid=0, name="default", squads=[
            s if isinstance(s, dict) else s for s in data.get("squads", [])
        ]),
    })


def load_activity(path: str | Path) -> ActivityConfig:
    """加载 activity.yaml"""
    return ActivityConfig(**load_yaml(path))


def load_system(path: str | Path) -> SystemConfig:
    """加载 system.yaml"""
    return SystemConfig(**load_yaml(path))


def load_llm_secret(config_dir: str | Path = "config") -> dict | None:
    """加载 llm_secret.yaml（可选）

    支持两种格式:
    1. 旧格式（向后兼容）:
        model: "xxx"
        base_url: "xxx"
        api_key: "xxx"

    2. 新格式（多 profile）:
        active_profile: "ollama"
        profiles:
          ollama:
            model: "llama3.2"
            base_url: "http://localhost:11434/v1"
            api_key: "sk-xxx"
          zhipu:
            model: "GLM-4.5-Air"
            base_url: "..."
            api_key: "..."

    Returns:
        包含配置的 dict，文件不存在时返回 None
    """
    p = Path(config_dir) / "llm_secret.yaml"
    if not p.exists():
        return None
    return load_yaml(p)


def apply_llm_config(system: SystemConfig, llm_secret: dict) -> SystemConfig:
    """将 llm_secret 配置应用到 system.llm

    优先使用 profile 模式，如果不存在则回退到直接配置模式。
    """
    if not llm_secret:
        return system

    # 新格式: profiles 模式
    if "profiles" in llm_secret:
        # 构建 profiles 字典
        profiles = {}
        for name, cfg in llm_secret["profiles"].items():
            profiles[name] = LLMProfile(**cfg)
        system.llm.profiles = profiles

        # 应用 active_profile
        active = llm_secret.get("active_profile", "default")
        system.llm.active_profile = active

        # 如果存在对应的 profile，应用其配置到顶层（向后兼容）
        if active in profiles:
            profile = profiles[active]
            system.llm.model = profile.model
            system.llm.base_url = profile.base_url
            system.llm.api_key = profile.api_key

    # 旧格式/直接配置模式（向后兼容）
    else:
        for key in ("model", "base_url", "api_key"):
            if key in llm_secret:
                setattr(system.llm, key, llm_secret[key])

    return system


_LLM_SECRET_TEMPLATE = """
  请创建 config/llm_secret.yaml，内容如下:

  ┌─────────────────────────────────────────────┐
  │ model: "glm-4.7"                            │
  │ base_url: "https://open.bigmodel.cn/..."    │
  │ api_key: "your-api-key-here"                │
  └─────────────────────────────────────────────┘

  或复制模板: cp config/llm_secret.yaml.example config/llm_secret.yaml
""".rstrip()


def load_all(config_dir: str | Path = "config", alliance: str = "ours") -> AppConfig:
    """一次加载全部配置并做交叉校验

    Args:
        config_dir: 配置目录路径，默认为 "config"
        alliance: 活跃联盟 key，默认 "ours"

    Returns:
        AppConfig 聚合对象，包含所有子配置

    Raises:
        FileNotFoundError: 缺少必需的配置文件
        pydantic.ValidationError: 配置校验失败（格式/交叉引用）
    """
    d = Path(config_dir)
    system = load_system(d / "system.yaml")

    # 合并 llm_secret.yaml 到 system.llm（可选）
    llm_secret = load_llm_secret(d)
    system = apply_llm_config(system, llm_secret)

    squads = load_squads(d / "squads.yaml")
    if alliance in squads.alliances:
        squads.set_active(alliance)

    return AppConfig(
        accounts=load_accounts(d / "accounts.yaml"),
        squads=squads,
        activity=load_activity(d / "activity.yaml"),
        system=system,
    )
