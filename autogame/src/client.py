"""轻量级游戏服务器 HTTP 客户端

连接真实测试服务器，使用 GET + URL 拼接 JSON 的协议。
协议格式: GET {base_url}?{json_body}

json_body 结构:
  {"header": {...}, "request": {"cmd": "xxx", "param": {...}}, "extra_info": {...}}
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml


def _load_env_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parent.parent / "config" / "env_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_cmd_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parent / "config" / "cmd_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("commands", {})


class GameClient:
    """同步 HTTP 客户端，连接真实游戏服务器后台"""

    def __init__(self, env: Optional[str] = None):
        self._env_config = _load_env_config()
        self._cmd_config = _load_cmd_config()

        env = env or self._env_config["current_env"]
        env_info = self._env_config["environments"][env]
        self.base_url = env_info["url"]
        self.default_header = dict(self._env_config["default_header"])
        self.extra_info = dict(self._env_config["extra_info"])

    def send_cmd(self, cmd_name: str, uid: int, param_overrides: Optional[Dict] = None) -> Dict[str, Any]:
        """发送命令并返回响应 JSON

        Args:
            cmd_name: cmd_config.yaml 中的命令名
            uid: 玩家 UID
            param_overrides: 覆盖 default_param 的参数
        """
        cmd_info = self._cmd_config[cmd_name]
        param = dict(cmd_info.get("default_param", {}))
        if param_overrides:
            param.update(param_overrides)

        header = dict(self.default_header)
        header["uid"] = uid

        body = {
            "header": header,
            "request": {"cmd": cmd_info["cmd"], "param": param},
            "extra_info": self.extra_info,
        }

        url = f"{self.base_url}?{json.dumps(body, separators=(',', ':'), ensure_ascii=False)}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()


def get_player_pos(uid: int, env: str = None) -> Optional[tuple]:
    """查询玩家坐标，返回 (x, y) 或 None"""
    client = GameClient(env=env)
    data = client.send_cmd("get_player_pos", uid)

    # 解析路径: res_data[0].push_list[0].data[] -> name='svr_lord_info_new'
    #          -> data (JSON str) -> lord_info_data.lord_info.city_pos
    try:
        res_data = data.get("res_data", [])
        push_list = res_data[0]["push_list"]
        for item in push_list[0]["data"]:
            if item.get("name") == "svr_lord_info_new":
                parsed = json.loads(item["data"])
                city_pos = int(parsed["lord_info_data"]["lord_info"]["city_pos"])
                x = city_pos // 100_000_000
                y = (city_pos % 100_000_000) // 100
                return (x, y)
    except (KeyError, IndexError, TypeError, ValueError) as e:
        print(f"解析坐标失败: {e}")
    return None
