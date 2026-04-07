"""游戏服务器 HTTP 客户端（统一异步客户端）

从 cmd_config.yaml 动态加载命令字定义，自动生成对应方法。
- 异步 HTTP 客户端，基于 aiohttp
- GET 协议: GET {base_url}?{json_body}
- 环境驱动: 从 env_config.yaml 加载服务器地址
- 每个命令字自动注册为方法，参数从 YAML default_param 获取默认值
- 支持链式调用 + execute 批量发送
- 坐标编码: pos = x * 100_000_000 + y * 100
"""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import yaml

from src.utils.coords import encode_pos, decode_pos, make_bid_list

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).resolve().parent.parent


def _load_cmd_config() -> Dict[str, Any]:
    """加载 cmd_config.yaml 并返回 commands 字典"""
    config_path = _CONFIG_DIR / "config" / "cmd_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("commands", {})


def _load_env_config() -> Dict[str, Any]:
    """加载 env_config.yaml"""
    config_path = _CONFIG_DIR.parent / "config" / "env_config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 模块级别加载一次
CMD_CONFIG: Dict[str, Any] = _load_cmd_config()


class GameAPIClient:
    """异步游戏 API 客户端

    从 cmd_config.yaml 读取命令字定义，为每个命令提供：
    - send_cmd(): 立即发送单条命令
    - queue_cmd(): 加入待发送队列（链式调用）
    - execute(): 批量发送队列中所有命令

    使用 GET 协议与游戏后台通信，格式: GET {base_url}?{json_body}
    """

    def __init__(self, env: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None):
        """
        Args:
            env: 环境名（"test", "mock" 等），为 None 时使用 env_config.yaml 的 current_env
            session: 可复用的 aiohttp session，为 None 时按需创建
        """
        self._env_config = _load_env_config()
        env = env or self._env_config["current_env"]
        env_info = self._env_config["environments"][env]
        self.base_url = env_info["url"]
        self.default_header = dict(self._env_config["default_header"])
        self.extra_info = dict(self._env_config["extra_info"])

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

    async def _send(
        self, uid: int, cmd: str, param: Dict[str, Any],
        header_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """发送单条命令到游戏服务器（GET 协议）

        协议格式: GET {base_url}?{json_body}
        json_body: {"header": {...}, "request": {"cmd": "xxx", "param": {...}}, "extra_info": {...}}

        Args:
            uid: 玩家 UID
            cmd: 后台命令字（如 "fixed_move_city_new"）
            param: 命令参数
            header_overrides: 覆盖请求头字段（如 aid 用于切换联盟视角）

        Returns:
            服务器响应 dict
        """
        session = await self._ensure_session()
        header = dict(self.default_header)
        header["uid"] = uid
        if header_overrides:
            header.update(header_overrides)

        body = {
            "header": header,
            "request": {"cmd": cmd, "param": param},
            "extra_info": self.extra_info,
        }

        url = f"{self.base_url}?{json.dumps(body, separators=(',', ':'), ensure_ascii=False)}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                resp.raise_for_status()
                result = await resp.json()
                logger.debug("cmd=%s uid=%s resp_keys=%s", cmd, uid, list(result.keys()))
                return result
        except aiohttp.ClientError as e:
            # 请求失败时打印完整的请求信息
            logger.error(
                "【请求失败】cmd=%s uid=%s error=%s\n"
                "Header: %s\n"
                "Request: %s\n"
                "URL: %s",
                cmd, uid, type(e).__name__,
                json.dumps(header, ensure_ascii=False),
                json.dumps({"cmd": cmd, "param": param}, ensure_ascii=False),
                url[:200] + "..." if len(url) > 200 else url,
            )
            raise

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

    async def send_cmd(self, cmd_name: str, uid: int,
                       param_overrides: Optional[Dict[str, Any]] = None,
                       header_overrides: Optional[Dict[str, Any]] = None,
                       **overrides) -> Dict[str, Any]:
        """立即发送一条命令

        Args:
            cmd_name: 命令名（cmd_config.yaml 中的 key，如 "move_city"）
            uid: 玩家 UID（header 中的调用者身份）
            param_overrides: 协议参数覆盖（dict 形式），用于协议字段名与
                             Python 关键字冲突的场景（如字段名也叫 "uid"）
            header_overrides: 覆盖请求头字段（如 aid 用于切换联盟视角、lvl_id 等）
            **overrides: 覆盖 default_param 中的参数（便捷写法）

        Returns:
            服务器响应 dict
        """
        info = self.get_cmd_info(cmd_name)
        all_overrides = dict(param_overrides or {})
        all_overrides.update(overrides)
        param = self.build_param(cmd_name, **all_overrides)

        # 合并 extra_header：从配置中获取需要的额外 header 字段
        final_header_overrides = dict(header_overrides or {})
        extra_header_config = info.get("extra_header", {})
        if extra_header_config:
            # 检查必需的 extra_header 字段是否已提供
            for key, desc in extra_header_config.items():
                if key not in final_header_overrides:
                    logger.warning(
                        "cmd=%s 缺少 extra_header 字段: %s (描述: %s)，可能导致请求失败",
                        cmd_name, key, desc
                    )

        # 构建请求用于日志
        header = dict(self.default_header)
        header["uid"] = uid
        header.update(final_header_overrides)

        result = await self._send(uid, info["cmd"], param, header_overrides=final_header_overrides)

        # 业务失败时打印详细信息
        code = result.get("res_header", {}).get("ret_code", result.get("code", -1))
        if code != 0:
            logger.warning(
                "[业务失败] cmd_name=%s cmd=%s uid=%s code=%s\n"
                "Header: %s\n"
                "Param: %s\n"
                "Response: %s",
                cmd_name, info["cmd"], uid, code,
                json.dumps(header, ensure_ascii=False),
                json.dumps(param, ensure_ascii=False),
                json.dumps(result, ensure_ascii=False)[:500]
            )

        return result

    def queue_cmd(self, cmd_name: str, uid: int,
                  param_overrides: Optional[Dict[str, Any]] = None,
                  **overrides) -> "GameAPIClient":
        """将命令加入队列，返回 self 支持链式调用"""
        info = self.get_cmd_info(cmd_name)
        all_overrides = dict(param_overrides or {})
        all_overrides.update(overrides)
        param = self.build_param(cmd_name, **all_overrides)
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
                code = resp.get("res_header", {}).get("ret_code", resp.get("code", -1))
                if code == 0:
                    logger.info("[成功] uid=%s %s", action["uid"], action["description"])
                else:
                    # 业务失败：打印请求详情
                    logger.warning(
                        "[失败] uid=%s %s code=%s\n"
                        "Request: cmd=%s param=%s",
                        action["uid"], action["description"], code,
                        action["cmd"], json.dumps(action["param"], ensure_ascii=False)
                    )
            except Exception as e:
                # 网络异常：_send 已打印详细信息，这里只记录摘要
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
        target_type: int = 2,
        **kwargs,
    ) -> Dict[str, Any]:
        """发起集结"""
        return await self.send_cmd(
            "create_rally", uid,
            target_type=target_type,
            target_info=target_info,
            march_info=march_info,
            prepare_time=prepare_time,
            **kwargs,
        )

    async def join_rally(
        self, uid: int, target_info: Dict[str, Any], march_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """加入集结"""
        return await self.send_cmd("join_rally", uid, target_info=target_info, march_info=march_info)

    async def recall_troop(self, uid: int, troop_ids: List[str]) -> Dict[str, Any]:
        """召回行军中的部队"""
        return await self.send_cmd("recall_troop", uid, march_info={"ids": troop_ids})

    async def rally_dismiss(self, uid: int, unique_id: str) -> Dict[str, Any]:
        """队长解散整个集结 (unique_id 格式: 107_xxx_1)"""
        return await self.send_cmd("rally_dismiss", uid, unique_id=unique_id)

    async def recall_reinforce(self, uid: int, unique_id: str) -> Dict[str, Any]:
        """撤回本人在集结中的部队 (unique_id 格式: 101_xxx_1)"""
        return await self.send_cmd("recall_reinforce", uid, unique_id=unique_id)

    async def reinforce_building(
        self, uid: int, target_info: Dict[str, Any], march_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """驻防/增援建筑

        自动从 target_info["id"] 提取 target_type。
        """
        building_id = target_info.get("id", "")
        target_type = int(building_id.split("_")[0]) if "_" in building_id else 13
        return await self.send_cmd(
            "reinforce_building", uid,
            target_type=target_type,
            target_info=target_info,
            march_info=march_info,
        )

    async def attack_building(
        self, uid: int, target_info: Dict[str, Any], march_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """攻击建筑

        自动从 target_info["id"] 提取 target_type（建筑ID格式: {type}_{id}_{level}）。
        """
        building_id = target_info.get("id", "")
        target_type = int(building_id.split("_")[0]) if "_" in building_id else 13
        return await self.send_cmd(
            "attack_building", uid,
            target_type=target_type,
            target_info=target_info,
            march_info=march_info,
        )

    async def get_player_info(
        self, uid: int, modules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """获取玩家信息，返回结构化 dict

        Args:
            uid: 玩家 UID
            modules: 要请求的数据模块列表，如 ["svr_lord_info_new"]。
                     为 None 时使用 cmd_config.yaml 中定义的全部模块。
                     可选模块: svr_lord_info_new, svr_player, svr_soldier,
                              svr_hero_list, svr_buff

        返回字段取决于请求的模块:
            svr_lord_info_new → pos, name, city_level, lord_level, alliance_id
            svr_player        → vip_level, alliance_name, status, dead, level
            svr_soldier       → soldiers
            svr_hero_list     → heroes
            svr_buff          → buffs

        注: 战力(power)在 game_server 的 svr_user_objs.cityInfo.force 中，
            需通过 game_server_login_get 单独获取。
        """
        overrides = {}
        if modules is not None:
            overrides["list"] = modules
        data = await self.send_cmd("get_player_info", uid, **overrides)
        result: Dict[str, Any] = {"uid": uid}

        try:
            items = data["res_data"][0]["push_list"][0]["data"]
        except (KeyError, IndexError, TypeError):
            logger.warning("get_player_info 响应结构异常 uid=%s", uid)
            return result

        for item in items:
            name = item.get("name")
            raw = item.get("data", "")
            if not raw:
                continue
            try:
                parsed = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue

            if name == "svr_lord_info_new":
                lord = parsed.get("lord_info_data", {}).get("lord_info", {})
                city_pos_raw = lord.get("city_pos")
                if city_pos_raw:
                    result["pos"] = decode_pos(int(city_pos_raw))
                result["name"] = lord.get("uname", "")
                result["city_level"] = lord.get("city_level", 0)
                result["lord_level"] = lord.get("lord_level", 0)
                result["alliance_id"] = lord.get("aid", 0)

            elif name == "svr_player":
                result["vip_level"] = parsed.get("vip_level", 0)
                result["alliance_name"] = parsed.get("al_name", "")
                result["status"] = parsed.get("status", 0)
                result["dead"] = parsed.get("dead", 0)
                result["level"] = parsed.get("level", 0)

            elif name == "svr_soldier":
                result["soldiers"] = parsed.get("list", [])

            elif name == "svr_hero_list":
                result["heroes"] = parsed.get("heros", [])

            elif name == "svr_buff":
                result["buffs"] = parsed.get("buff_item", [])

        return result

    async def get_player_pos(self, uid: int) -> Optional[Tuple[int, int]]:
        """获取玩家地图坐标，返回 (x, y) 或 None

        内部调用 get_player_info 仅请求 svr_lord_info_new 以减少数据传输。
        """
        info = await self.get_player_info(uid, modules=["svr_lord_info_new"])
        return info.get("pos")

    async def get_player_lvl_info(self, uid: int) -> int:
        """获取玩家当前所在的 AVA 战场 ID

        Returns:
            lvl_id: 0 表示在普通地图，非0 为 AVA 战场副本 ID
        """
        data = await self.send_cmd("get_player_lvl_info", uid)
        try:
            for item in data["res_data"][0]["push_list"][0]["data"]:
                if item.get("name") == "svr_player_lvl_info":
                    raw = item.get("data", "")
                    parsed = json.loads(raw) if isinstance(raw, str) else raw
                    return parsed.get("lvl_id", 0)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            logger.warning("get_player_lvl_info 响应结构异常 uid=%s", uid)
        return 0

    async def get_all_player_data(self, uid: int) -> Dict[str, Any]:
        """获取玩家全量数据"""
        return await self.send_cmd("get_all_player_data", uid)


    async def get_map_detail(self, uid: int, sid: int = 1, bid_list: List = None) -> Dict[str, Any]:
        """获取普通地图详细信息（非 AVA 战场）"""
        return await self.send_cmd(
            "get_map_detail", uid, sid=sid, bid_list=bid_list or [],
            header_overrides={"lvl_id": 0},
        )

    async def get_map_area(
        self, uid: int,
        center_x: int, center_y: int, size: int = 10, sid: int = 1,
    ) -> List[Dict[str, Any]]:
        """获取指定区域的地块详细内容（自动计算 bid_list）

        Args:
            uid: 查询账号 UID
            center_x, center_y: 中心像素坐标
            size: 范围边长（以地块为单位，默认 10x10=100 块）
            sid: 服务器 ID（test环境为 1）

        Returns:
            mapBidObjs 列表，每项含 bid 和 objs；失败返回空列表
        """
        bid_list = make_bid_list(center_x, center_y, size)
        resp = await self.get_map_detail(uid, sid=sid, bid_list=bid_list)

        try:
            data_list = resp["res_data"][0]["push_list"][0]["data"]
            for item in data_list:
                if item.get("name") == "svr_map_objs_new":
                    raw = item.get("data", "{}")
                    parsed = json.loads(raw) if isinstance(raw, str) else raw
                    map_objs = parsed.get("mapBidObjs", [])
                    obj_count = sum(len(b.get("objs", [])) for b in map_objs)
                    logger.info(
                        "get_map_area: size=%d, blocks=%d, objects=%d",
                        size, len(map_objs), obj_count,
                    )
                    return map_objs
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.warning("get_map_area 响应解析失败 uid=%s: %s", uid, e)

        return []

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

    # ------------------------------------------------------------------
    # AVA 战场内操作
    # ------------------------------------------------------------------

    async def lvl_move_city(self, uid: int, x: int, y: int, lvl_id: int) -> Dict[str, Any]:
        """AVA 战场内移城到 (x, y)

        Args:
            uid: 玩家 UID
            x: 目标坐标 X
            y: 目标坐标 Y
            lvl_id: 战场 ID（必须传入，用于 header 验证）
        """
        return await self.send_cmd("lvl_move_city", uid, tar_pos=encode_pos(x, y), header_overrides={"lvl_id": lvl_id})

    # sync_all=False 时请求的数据段列表
    _SYNC_SECTIONS = [
        "svr_lvl_brief_objs",
        "svr_lvl_rally_brief_objs",
        "svr_lvl_user_objs",
    ]

    async def lvl_battle_login_get(
        self, uid: int, lvl_id: int, *, sync_all: bool = True,
    ) -> Dict[str, Any]:
        """获取 AVA 战场队伍信息

        Args:
            sync_all: True → all=1（服务器返回全量）；
                      False → all=0 + list 指定 3 个 section
        """
        overrides: Dict[str, Any] = {"lvl_id": lvl_id}
        if sync_all:
            overrides["all"] = 1
        else:
            overrides["all"] = 0
            overrides["list"] = self._SYNC_SECTIONS
        return await self.send_cmd(
            "lvl_battle_login_get", uid,
            header_overrides={"lvl_id": lvl_id},
            **overrides,
        )

    async def lvl_scout_player(
        self, uid: int, lvl_id: int, target_uid: int, target_pos: int,
    ) -> Dict[str, Any]:
        """AVA 战场内侦查玩家

        Args:
            lvl_id: 战场 ID
            target_uid: 目标玩家 UID
            target_pos: 编码后的坐标（x*100000000+y*100）
        """
        target_info = {
            "id": target_uid,
            "pos": target_pos,
            "type": 10101,
            "unique_id": "",
            "lv": 20,
        }
        return await self.send_cmd("lvl_dispatch_scout_player", uid, target_info=target_info, header_overrides={"lvl_id": lvl_id})

    async def lvl_scout_building(
        self, uid: int, lvl_id: int, building_id: int, building_pos: int, key: int = 0,
    ) -> Dict[str, Any]:
        """AVA 战场内侦查建筑

        Args:
            lvl_id: 战场 ID
            building_id: 建筑 ID
            building_pos: 编码后的坐标
            key: 建筑 key
        """
        target_info = {
            "id": building_id,
            "pos": building_pos,
            "type": 10001,
            "unique_id": "",
            "key": key,
        }
        return await self.send_cmd("lvl_dispatch_scout_building", uid, target_info=target_info, header_overrides={"lvl_id": lvl_id})

    async def lvl_attack_player(
        self, uid: int, lvl_id: int, target_id: str, target_pos: int,
        march_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AVA 战场内攻打玩家

        Args:
            lvl_id: 战场 ID
            target_id: 目标唯一 ID
            target_pos: 编码后的坐标
            march_info: 出征部队信息（可选，为 None 时使用 YAML 默认值）
        """
        overrides: Dict[str, Any] = {
            "target_info": {"id": target_id, "pos": target_pos},
        }
        if march_info:
            overrides["march_info"] = march_info
        return await self.send_cmd("lvl_dispatch_troop", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_attack_building(
        self, uid: int, lvl_id: int, target_id: str, target_pos: int, key: int = 0,
        target_type: int = 10001, march_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AVA 战场内攻打建筑

        Args:
            lvl_id: 战场 ID
            target_id: 建筑唯一 ID (如 "27_4_1")
            target_pos: 编码后的坐标
            key: 建筑 key
            target_type: 目标类型（默认10001，可设为10006等）
            march_info: 出征部队信息
        """
        overrides: Dict[str, Any] = {
            "march_type": 15,
            "target_info": {"id": target_id, "pos": target_pos, "key": key},
            "target_type": target_type,
        }
        if march_info:
            overrides["march_info"] = march_info
        return await self.send_cmd("lvl_dispatch_troop", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_collect_cart(
        self, uid: int, lvl_id: int, target_id: str,
    ) -> Dict[str, Any]:
        """AVA 战场内搜集资源车 (coal cart, type=10300)

        使用 lvl_dispatch_pick 命令字，march_type=21，不需要兵力信息。

        Args:
            lvl_id: 战场 ID
            target_id: 资源车唯一 ID (如 "10300_xxx")
        """
        overrides: Dict[str, Any] = {
            "march_type": 21,
            "target_info": {"type": 10300, "id": target_id},
            "queue_id": 6001,
        }
        return await self.send_cmd("lvl_collect_cart", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_reinforce_building(
        self, uid: int, lvl_id: int, target_id: str, key: int = 0,
        target_type: int = 10006, march_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AVA 战场内驻防/增援我方建筑

        与 lvl_attack_building 的区别:
        - march_type=11 (驻防) 而非 15 (攻打)
        - leader=0 (援军身份，不占主帅)
        - target_info.pos="nil" (只需建筑 ID 定位)

        Args:
            lvl_id: 战场 ID
            target_id: 建筑唯一 ID (如 "10006_1773137411102403")
            key: 建筑 key
            target_type: 目标类型（默认10006）
            march_info: 出征部队信息
        """
        # 驻防用 leader=0（援军身份，不占主帅英雄）
        # 需要保留 default_param 中 march_info 的完整结构（soldier/hero 等），仅覆盖 leader
        if march_info:
            march_info = {**march_info, "leader": 0}
        else:
            # CLI 直接调用时无 march_info，从 default_param 获取并 patch leader
            default_march = copy.deepcopy(
                self.get_cmd_info("lvl_dispatch_troop").get("default_param", {}).get("march_info", {})
            )
            default_march["leader"] = 0
            march_info = default_march
        overrides: Dict[str, Any] = {
            "march_type": 11,
            "target_info": {"id": target_id, "pos": "nil", "key": key},
            "target_type": target_type,
            "march_info": march_info,
        }
        return await self.send_cmd("lvl_dispatch_troop", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_create_rally(
        self, uid: int, lvl_id: int, target_id: str,
        march_info: Optional[Dict[str, Any]] = None,
        prepare_time: int = 60, tn_limit: int = 1,
    ) -> Dict[str, Any]:
        """AVA 战场内对玩家发起集结

        Args:
            lvl_id: 战场 ID
            target_id: 目标唯一 ID (如 "10101_20010669")
            march_info: 队长出征部队信息
            prepare_time: 集结准备时间（默认60秒）
            tn_limit: 部队数量限制
        """
        import time as _time
        timestamp = str(int(_time.time() * 1_000_000))
        overrides: Dict[str, Any] = {
            "march_type": 13,
            "target_info": {"id": target_id},
            "target_type": 10101,
            "prepare_time": prepare_time,
            "tn_limit": tn_limit,
            "timestamp": timestamp,
        }
        if march_info:
            overrides["march_info"] = march_info
        return await self.send_cmd("lvl_create_rally_war", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_create_rally_building(
        self, uid: int, lvl_id: int, target_id: str,
        march_info: Optional[Dict[str, Any]] = None,
        prepare_time: int = 60, tn_limit: int = 15,
    ) -> Dict[str, Any]:
        """AVA 战场内对建筑发起集结

        Args:
            lvl_id: 战场 ID
            target_id: 建筑 unique_id (如 "27_4_1")
            march_info: 队长出征部队信息
            prepare_time: 集结准备时间（默认60秒）
            tn_limit: 部队数量限制
        """
        # 从 target_id 提取 target_type（格式: "{type}_{id}_{...}"）
        target_type = int(target_id.split("_")[0]) if "_" in target_id else 10001
        import time as _time
        timestamp = str(int(_time.time() * 1_000_000))
        overrides: Dict[str, Any] = {
            "march_type": 14,
            "target_info": {"id": target_id},
            "target_type": target_type,
            "prepare_time": prepare_time,
            "tn_limit": tn_limit,
            "timestamp": timestamp,
        }
        if march_info:
            overrides["march_info"] = march_info
        return await self.send_cmd("lvl_create_rally_war", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_rally_dismiss(self, uid: int, lvl_id: int, unique_id: str) -> Dict[str, Any]:
        """AVA 战场内解散集结 (unique_id 格式: 107_xxx)"""
        return await self.send_cmd("lvl_rally_dismiss", uid, unique_id=unique_id, header_overrides={"lvl_id": lvl_id})

    async def lvl_join_rally(
        self, uid: int, lvl_id: int, target_id: str, target_pos: int = 0,
        march_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """AVA 战场内参与集结

        Args:
            lvl_id: 战场 ID
            target_id: 集结唯一 ID
            target_pos: 集结目标编码坐标
            march_info: 队员出征部队信息
        """
        overrides: Dict[str, Any] = {
            "target_info": {"id": target_id, "pos": target_pos},
        }
        if march_info:
            overrides["march_info"] = march_info
        return await self.send_cmd("lvl_join_rally_war", uid, header_overrides={"lvl_id": lvl_id}, **overrides)

    async def lvl_speed_up_troop(self, uid: int, lvl_id: int, unique_id: str) -> Dict[str, Any]:
        """AVA 战场内行军加速 (unique_id 如 102_xxx 或 101_xxx)"""
        return await self.send_cmd("lvl_use_troop_speed_up_item", uid, unique_id=unique_id, header_overrides={"lvl_id": lvl_id})

    async def lvl_recall_reinforce(self, uid: int, lvl_id: int, unique_id: str) -> Dict[str, Any]:
        """AVA 战场内取消参与集结 (unique_id 格式: 101_xxx)"""
        return await self.send_cmd("lvl_recall_reinforce", uid, unique_id=unique_id, header_overrides={"lvl_id": lvl_id})

    async def lvl_recall_troop(self, uid: int, lvl_id: int, unique_id: str) -> Dict[str, Any]:
        """AVA 战场内召回普通队伍 (unique_id 格式: 101_xxx)"""
        return await self.send_cmd("lvl_use_troop_return_item", uid, unique_id=unique_id, header_overrides={"lvl_id": lvl_id})

    async def lvl_recall_from_building(
        self, uid: int, lvl_id: int, troop_ids: List[str], pos: int = 0,
    ) -> Dict[str, Any]:
        """AVA 战场内从建筑中召回队伍

        Args:
            lvl_id: 战场 ID
            troop_ids: 队伍 ID 列表
            pos: 队伍当前位置（编码坐标）
        """
        return await self.send_cmd(
            "lvl_change_troop", uid, header_overrides={"lvl_id": lvl_id},
            march_info={"ids": troop_ids},
            target_info={"pos": pos},
        )

    async def lvl_svr_map_get(
        self, uid: int, lvl_id: int, bid_list: List[int],
    ) -> Dict[str, Any]:
        """AVA 战场内获取地块详细内容（按 bid 分块查询）

        与 lvl_battle_login_get (brief view) 的区别:
        - brief: 返回 svr_lvl_brief_objs，扁平概要列表
        - detail: 返回 svr_lvl_map_objs.mapBidObjs，按地块分组，
          含城市等级/兵力/camp、建筑驻军数、行军类型等详细信息

        Args:
            uid: 查询账号 UID
            lvl_id: 战场 ID
            bid_list: 地块 ID 列表 (bid = (x//10+1)*1000 + (y//10+1))
        """
        return await self.send_cmd(
            "lvl_svr_map_get", uid,
            bid_list=bid_list,
            header_overrides={"lvl_id": lvl_id},
        )

    async def lvl_get_map_area(
        self, uid: int, lvl_id: int,
        center_x: int, center_y: int, size: int = 10,
    ) -> List[Dict[str, Any]]:
        """AVA 战场内获取指定区域的地块详细内容（自动计算 bid_list）

        Args:
            uid: 查询账号 UID
            lvl_id: 战场 ID
            center_x, center_y: 中心像素坐标
            size: 范围边长（以地块为单位，默认 10x10=100 块）

        Returns:
            mapBidObjs 列表，每项含 bid 和 objs；失败返回空列表
        """
        bid_list = make_bid_list(center_x, center_y, size)
        resp = await self.lvl_svr_map_get(uid, lvl_id, bid_list)

        try:
            data_list = resp["res_data"][0]["push_list"][0]["data"]
            for item in data_list:
                if item.get("name") == "svr_lvl_map_objs":
                    raw = item.get("data", "{}")
                    parsed = json.loads(raw) if isinstance(raw, str) else raw
                    map_objs = parsed.get("mapBidObjs", [])
                    obj_count = sum(len(b.get("objs", [])) for b in map_objs)
                    logger.info(
                        "lvl_get_map_area: size=%d, blocks=%d, objects=%d",
                        size, len(map_objs), obj_count,
                    )
                    return map_objs
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            logger.warning("lvl_get_map_area 响应解析失败 uid=%s: %s", uid, e)

        return []
