"""游戏服务器 HTTP 客户端

从 cmd_config.yaml 动态加载命令字定义，自动生成对应方法。
- 异步 HTTP 客户端，基于 aiohttp
- 每个命令字自动注册为方法，参数从 YAML default_param 获取默认值
- 支持链式调用 + execute 批量发送
- 坐标编码: pos = x * 100_000_000 + y * 100
"""

from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import yaml

from src.utils.coords import encode_pos, decode_pos  # noqa: F401

logger = logging.getLogger(__name__)


def _load_cmd_config() -> Dict[str, Any]:
    """加载 cmd_config.yaml 并返回 commands 字典"""
    config_path = Path(__file__).resolve().parent.parent / "config" / "cmd_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("commands", {})


# 模块级别加载一次
CMD_CONFIG: Dict[str, Any] = _load_cmd_config()


class GameAPIClient:
    """异步游戏 API 客户端

    从 cmd_config.yaml 读取命令字定义，为每个命令提供：
    - send_<cmd_name>(): 立即发送单条命令
    - queue_<cmd_name>(): 加入待发送队列（链式调用）
    - execute(): 批量发送队列中所有命令
    """

    def __init__(self, base_url: str, session: Optional[aiohttp.ClientSession] = None):
        """
        Args:
            base_url: 游戏服务器地址，如 "http://127.0.0.1:8080"
            session: 可复用的 aiohttp session，为 None 时按需创建
        """
        self.base_url = base_url.rstrip("/")
        self._external_session = session
        self._session: Optional[aiohttp.ClientSession] = session
        self._queue: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """关闭内部创建的 session（外部传入的不关闭）"""
        if self._session and not self._external_session:
            await self._session.close()
            self._session = None

    # ------------------------------------------------------------------
    # 底层发送
    # ------------------------------------------------------------------

    async def _send(self, uid: int, cmd: str, param: Dict[str, Any]) -> Dict[str, Any]:
        """发送单条命令到游戏服务器

        Args:
            uid: 玩家 UID
            cmd: 后台命令字（如 "fixed_move_city_new"）
            param: 命令参数

        Returns:
            服务器响应 dict，格式 {"code": 0, "msg": "ok", "data": {...}}
        """
        session = await self._ensure_session()
        payload = {
            "uid": str(uid),
            "cmd": cmd,
            "params": param,
        }
        url = f"{self.base_url}/api/game"
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            logger.debug("cmd=%s uid=%s code=%s", cmd, uid, result.get("code"))
            return result

    # ------------------------------------------------------------------
    # 通用命令发送（基于 cmd_config.yaml）
    # ------------------------------------------------------------------

    def get_cmd_info(self, cmd_name: str) -> Dict[str, Any]:
        """获取命令字定义，不存在则抛出 KeyError"""
        if cmd_name not in CMD_CONFIG:
            raise KeyError(f"未知命令字: {cmd_name}，请检查 cmd_config.yaml")
        return CMD_CONFIG[cmd_name]

    def build_param(self, cmd_name: str, **overrides) -> Dict[str, Any]:
        """基于 cmd_config.yaml 的 default_param 构建参数，用 overrides 覆盖"""
        info = self.get_cmd_info(cmd_name)
        param = copy.deepcopy(info.get("default_param", {}))
        param.update(overrides)
        return param

    async def send_cmd(self, cmd_name: str, uid: int, **overrides) -> Dict[str, Any]:
        """立即发送一条命令

        Args:
            cmd_name: 命令名（cmd_config.yaml 中的 key，如 "move_city"）
            uid: 玩家 UID
            **overrides: 覆盖 default_param 中的参数

        Returns:
            服务器响应 dict
        """
        info = self.get_cmd_info(cmd_name)
        param = self.build_param(cmd_name, **overrides)
        return await self._send(uid, info["cmd"], param)

    def queue_cmd(self, cmd_name: str, uid: int, **overrides) -> "GameAPIClient":
        """将命令加入队列，返回 self 支持链式调用"""
        info = self.get_cmd_info(cmd_name)
        param = self.build_param(cmd_name, **overrides)
        self._queue.append({
            "cmd_name": cmd_name,
            "cmd": info["cmd"],
            "uid": uid,
            "param": param,
            "description": info.get("description", cmd_name),
        })
        return self

    async def execute(self) -> List[Dict[str, Any]]:
        """批量发送队列中的所有命令并清空队列

        Returns:
            响应列表，顺序与入队顺序一致
        """
        results = []
        for action in self._queue:
            try:
                resp = await self._send(action["uid"], action["cmd"], action["param"])
                results.append(resp)
                code = resp.get("code", -1)
                if code == 0:
                    logger.info("[成功] uid=%s %s", action["uid"], action["description"])
                else:
                    logger.warning("[失败] uid=%s %s code=%s", action["uid"], action["description"], code)
            except Exception as e:
                logger.error("[异常] uid=%s %s: %s", action["uid"], action["description"], e)
                results.append({"code": -1, "msg": str(e), "data": None})
        self._queue.clear()
        return results

    @property
    def pending_count(self) -> int:
        return len(self._queue)

    def clear_queue(self) -> "GameAPIClient":
        self._queue.clear()
        return self

    # ------------------------------------------------------------------
    # 便捷方法：对高频操作提供带语义参数的快捷接口
    # 内部全部委托给 send_cmd / queue_cmd，参数从 YAML 读取
    # ------------------------------------------------------------------

    async def move_city(self, uid: int, x: int, y: int) -> Dict[str, Any]:
        """移城到 (x, y)"""
        return await self.send_cmd("move_city", uid, tar_pos=encode_pos(x, y))

    def queue_move_city(self, uid: int, x: int, y: int) -> "GameAPIClient":
        return self.queue_cmd("move_city", uid, tar_pos=encode_pos(x, y))

    async def attack_player(
        self, uid: int, target_uid: int, target_x: int, target_y: int,
        march_info: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """攻击敌方玩家主城"""
        pos = str(encode_pos(target_x, target_y))
        target_id = f"2_{target_uid}_1"
        target_info = {"id": target_id, "pos": pos}
        overrides: Dict[str, Any] = {"target_info": target_info}
        if march_info:
            overrides["march_info"] = march_info
        return await self.send_cmd("attack_player", uid, **overrides)

    async def scout_player(
        self, uid: int, target_uid: int, target_x: int, target_y: int,
    ) -> Dict[str, Any]:
        """侦察目标玩家"""
        tar_pos = encode_pos(target_x, target_y)
        unique_id = f"2_{target_uid}_1"
        tar_info = {
            "unique_id": unique_id,
            "type": 2,
            "id": target_uid,
            "lv": 1,
        }
        return await self.send_cmd("scout_player", uid, tar_pos=tar_pos, tar_info=tar_info)

    async def create_rally(
        self, uid: int, target_info: Dict[str, Any],
        march_info: Dict[str, Any], prepare_time: int = 300,
    ) -> Dict[str, Any]:
        """发起集结"""
        return await self.send_cmd(
            "create_rally", uid,
            target_info=target_info,
            march_info=march_info,
            prepare_time=prepare_time,
        )

    async def join_rally(
        self, uid: int, target_info: Dict[str, Any], march_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """加入集结"""
        return await self.send_cmd("join_rally", uid, target_info=target_info, march_info=march_info)

    async def recall_troop(self, uid: int, troop_ids: List[str]) -> Dict[str, Any]:
        """召回行军中的部队"""
        return await self.send_cmd("recall_troop", uid, march_info={"ids": troop_ids})

    async def recall_reinforce(self, uid: int, unique_id: str) -> Dict[str, Any]:
        """召回增援/集结部队"""
        return await self.send_cmd("recall_reinforce", uid, unique_id=unique_id)

    async def reinforce_building(
        self, uid: int, target_info: Dict[str, Any], march_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """驻防/增援建筑"""
        return await self.send_cmd("reinforce_building", uid, target_info=target_info, march_info=march_info)

    async def attack_building(
        self, uid: int, target_info: Dict[str, Any], march_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """攻击建筑"""
        return await self.send_cmd("attack_building", uid, target_info=target_info, march_info=march_info)

    async def get_player_pos(self, uid: int) -> Dict[str, Any]:
        """获取玩家地图坐标"""
        return await self.send_cmd("get_player_pos", uid)

    async def get_all_player_data(self, uid: int) -> Dict[str, Any]:
        """获取玩家全量数据"""
        return await self.send_cmd("get_all_player_data", uid)

    async def get_map_overview(self, uid: int, sid: int = 0) -> Dict[str, Any]:
        """获取地图缩略信息"""
        return await self.send_cmd("get_map_overview", uid, sid=sid)

    async def get_map_detail(self, uid: int, sid: int = 0, bid_list: List = None) -> Dict[str, Any]:
        """获取地图详细信息"""
        return await self.send_cmd("get_map_detail", uid, sid=sid, bid_list=bid_list or [])

    async def get_battle_report(self, uid: int, report_id: str) -> Dict[str, Any]:
        """获取战报"""
        return await self.send_cmd("get_battle_report", uid, id=report_id)

    # --- GM 指令 ---

    async def add_gem(self, uid: int, gem_num: int = None) -> Dict[str, Any]:
        """GM: 添加宝石"""
        overrides = {}
        if gem_num is not None:
            overrides["gem_num"] = gem_num
        return await self.send_cmd("add_gem", uid, **overrides)

    async def add_soldiers(self, uid: int, soldier_id: int = None, soldier_num: int = None) -> Dict[str, Any]:
        """GM: 添加士兵"""
        overrides = {}
        if soldier_id is not None:
            overrides["soldier_id"] = soldier_id
        if soldier_num is not None:
            overrides["soldier_num"] = soldier_num
        return await self.send_cmd("add_soldiers", uid, **overrides)

    async def add_resource(self, uid: int, op_type: int = None) -> Dict[str, Any]:
        """GM: 添加资源"""
        overrides = {}
        if op_type is not None:
            overrides["op_type"] = op_type
        return await self.send_cmd("add_resource", uid, **overrides)
