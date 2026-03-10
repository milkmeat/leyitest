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
    AppConfig,
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
    """加载 squads.yaml"""
    return SquadsConfig(**load_yaml(path))


def load_activity(path: str | Path) -> ActivityConfig:
    """加载 activity.yaml"""
    return ActivityConfig(**load_yaml(path))


def load_system(path: str | Path) -> SystemConfig:
    """加载 system.yaml"""
    return SystemConfig(**load_yaml(path))


def load_all(config_dir: str | Path = "config") -> AppConfig:
    """一次加载全部配置并做交叉校验

    Args:
        config_dir: 配置目录路径，默认为 "config"

    Returns:
        AppConfig 聚合对象，包含所有子配置

    Raises:
        FileNotFoundError: 缺少必需的配置文件
        pydantic.ValidationError: 配置校验失败（格式/交叉引用）
    """
    d = Path(config_dir)
    return AppConfig(
        accounts=load_accounts(d / "accounts.yaml"),
        squads=load_squads(d / "squads.yaml"),
        activity=load_activity(d / "activity.yaml"),
        system=load_system(d / "system.yaml"),
    )
