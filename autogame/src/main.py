"""WestGame AI 全自动化团战系统 — 入口

用法:
  python src/main.py [--mock] [--verbose|--debug] [--llm <profile>] <command> <args...>

主循环:
  run                                           启动 AI 主循环（无限）
  run --rounds 3                                跑 3 轮退出
  run --once                                    等价 --rounds 1
  run --loop.interval_seconds 0                 覆盖循环间隔（测试用）

AI 决策调试:
  l2_decide [--ava <lvl_id>] [--dry-run] [--json]  L2 军团指挥官决策调试(AVA时自动切换prompt)
  l1_decide <squad_id> [--dry-run] [--json]     L1 单小队决策调试(--ava时自动切换prompt)
  l1_view <squad_id> [--json]                   L1 小队局部视图
  llm_test [--dry-run]                          测试 LLM 连通性

查询命令:
  get_player_pos <uid>                          查询玩家坐标
  get_player_info <uid>                         查询玩家完整信息(自动检测AVA状态)
  get_all_player_data <uid>                     查询玩家全量数据
  get_map_overview <uid>                        查询地图缩略信息
  get_map_detail <uid> [bid...]                 查询地图详细信息
  get_battle_report <uid> <report_id>           查询战报

行动命令:
  move_city <uid> <x> <y>                       移城到指定坐标
  attack_player <uid> <target_uid> <x> <y> [soldier_id count]  攻击玩家
  attack_building <uid> <building_id> <x> <y>   攻击建筑
  reinforce_building <uid> <building_id> <x> <y> 驻防建筑
  scout_player <uid> <target_uid> <x> <y>       侦察玩家
  create_rally <uid> <target_uid> <x> <y> [soldier_id count] [prepare_time]  发起集结
  join_rally <uid> <rally_id> <rally_x> <rally_y> [soldier_id count]  加入集结
  rally_dismiss <uid> <rally_unique_id>         解散集结 (107_xxx_1)
  recall_troop <uid> <troop_id...>              召回行军部队
  recall_reinforce <uid> <troop_unique_id>      撤回增援部队 (101_xxx_1)

AVA 战场行动:
  lvl_move_city <uid> <lvl_id> <x> <y>          AVA移城到指定坐标
  lvl_scout_player <uid> <lvl_id> <target_uid> <x> <y>  AVA侦查玩家
  lvl_scout_building <uid> <lvl_id> <building_id> <x> <y>  AVA侦查建筑
  lvl_attack_player <uid> <lvl_id> <target_uid> <x> <y>  AVA攻打玩家
  lvl_attack_building <uid> <lvl_id> <building_id> <x> <y>  AVA攻打建筑
  lvl_reinforce_building <uid> <lvl_id> <building_id>      AVA驻防/增援我方建筑
  lvl_create_rally <uid> <lvl_id> <target_id> <x> <y> [prepare_time]  AVA发起集结(建筑/玩家)
  lvl_battle_login_get <uid> <lvl_id>                    AVA战场登录数据查询
  lvl_rally_dismiss <uid> <lvl_id> <unique_id>  AVA解散集结

简化查询命令:
  get_gem <uid>                                 查询宝石数量（纯数字）
  get_soldiers <uid> <soldier_id>               查询指定兵种数量（纯数字）

GM 命令:
  add_gem <uid> [amount]                        添加宝石
  add_soldiers <uid> [soldier_id] [num]         添加士兵
  add_resource <uid> [op_type]                  添加资源

数据同步:
  sync [--json] [--ava <lvl_id>] [uid]          数据同步(全量/单账号,单账号自动检测AVA)

L0 执行器（AI 指令调试）:
  l0 <ACTION|JSON> <args...>                    执行器调试
  l0 MOVE_CITY <uid> <x> <y>                   移城
  l0 ATTACK_TARGET <uid> <target_uid> <x> <y>  攻击玩家
  l0 ATTACK_TARGET <uid> --building <id> <x> <y> 攻击建筑
  l0 SCOUT <uid> <target_uid> <x> <y>          侦察
  l0 GARRISON_BUILDING <uid> <building_id> <x> <y> 驻防建筑
  l0 INITIATE_RALLY <uid> <target_id> <x> <y> [prepare_time] 发起集结
  l0 JOIN_RALLY <uid> <rally_id>               加入集结
  l0 RETREAT <uid> <troop_id...>               召回部队

  所有 l0 指令支持可选参数 --soldier <soldier_id> <count>:
    手动指定出征兵种和数量（不指定则自动选择数量最多的兵种，默认5000）
    示例: l0 LVL_ATTACK_BUILDING <uid> <bid> <x> <y> --soldier 204 3000

uid_helper (测试环境账号准备):
  uid_copy <src_uid> <tar_uid>                  复制账号数据
  uid_create_al <name> <nick>                   创建联盟
  uid_join_al <aid> <uid1> [uid2...]            加入联盟+改名
  uid_members <aid>                             查看联盟成员
  uid_setup <alliance_key> <src_uid> <tar_uid...>  一站式账号准备

uid_helper (AVA 战场):
  uid_ava_add <lvl_id> <uid> <camp_id>          添加到AVA战场名单
  uid_ava_enter <lvl_id> <uid>                  进入AVA战场
  uid_ava_status <uid>                          查询AVA战场状态
  uid_ava_leave <uid>                           离开AVA战场
"""

import asyncio
import json as _json
import logging
import os
import sys

# 确保项目根目录在 sys.path 中，支持 python src/main.py 和 python -m src.main 两种方式
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 模块级变量：由 main() 解析全局参数后设置
_llm_profile: str | None = None
_team: int = 1  # 1=我方(accounts), 2=敌方(enemies)  NOTE: 模块级可变状态，不支持多 team 并行


def _apply_team_swap(config: "AppConfig") -> None:
    """Team=2 模式下交换 accounts/enemies 和 alliances 配置

    交换后:
      - active_uids() 返回敌方 UID
      - enemy_uids() 返回原我方 UID
      - alliances.ours 指向原 alliances.enemy (lvl_aid=2)
      - squads.squads 返回敌方小队（由 load_all 已设置）
    """
    # 交换账号列表
    config.accounts.accounts, config.accounts.enemies = (
        config.accounts.enemies, config.accounts.accounts
    )
    # 交换联盟信息
    if config.accounts.alliances:
        config.accounts.alliances.ours, config.accounts.alliances.enemy = (
            config.accounts.alliances.enemy, config.accounts.alliances.ours
        )
    ally = config.accounts.alliances
    alliance_name = ally.ours.name if ally else "?"
    camp_id = ally.ours.lvl_aid if ally else "?"
    print(f"[config] Team 2 模式: 管理敌方联盟 {alliance_name} (camp_id={camp_id})")


def _load_config(config_dir: str = "config") -> "AppConfig":
    """加载配置并应用 --llm profile 和 --team 切换"""
    from src.config.loader import load_all
    alliance = "ours" if _team == 1 else "enemy"
    config = load_all(config_dir, alliance=alliance)
    if _llm_profile:
        if not config.system.llm.switch_profile(_llm_profile):
            available = ", ".join(config.system.llm.profiles.keys()) or "(无)"
            print(f"[warn] LLM profile '{_llm_profile}' 不存在 (可用: {available})", file=sys.stderr)
        else:
            print(f"[config] LLM profile: {_llm_profile} → {config.system.llm.model}")
    # Team=2 时交换配置视角
    if _team == 2:
        _apply_team_swap(config)
    return config


def _check_llm_config(config) -> bool:
    """检查 LLM 配置是否可用，缺失时打印友好提示

    Returns:
        True 如果 LLM 已配置，False 如果缺失
    """
    llm = config.system.llm
    if llm.api_key and llm.model:
        return True

    from src.config.loader import _LLM_SECRET_TEMPLATE
    print("[info] LLM 配置缺失 — config/llm_secret.yaml 未找到或不完整")
    print(_LLM_SECRET_TEMPLATE)
    return False


def _print_json(data):
    """格式化打印 JSON"""
    print(_json.dumps(data, indent=2, ensure_ascii=False))


def _print_ret_code(resp):
    """打印响应中的 ret_code，成功输出 [OK]，失败输出 [warn]"""
    code = resp.get("res_header", {}).get("ret_code", -1)
    msg = resp.get("res_header", {}).get("err_msg", "")
    if code == 0:
        print("[OK]")
    else:
        print(f"[warn] ret_code={code} {msg}", file=sys.stderr)
    return code


# ---------------------------------------------------------------------------
# 查询命令
# ---------------------------------------------------------------------------


async def cmd_get_player_pos(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        pos = await client.get_player_pos(uid)
        if pos:
            print(f"({pos[0]},{pos[1]})")
        else:
            print(f"无法获取 uid={uid} 的坐标", file=sys.stderr)
            sys.exit(1)
    finally:
        await client.close()


async def cmd_get_player_info(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        # 并发查询玩家信息和 AVA 状态
        info, lvl_id = await asyncio.gather(
            client.get_player_info(uid),
            client.get_player_lvl_info(uid),
        )
        if lvl_id:
            print(f"[地图] uid={uid} 当前在 AVA 战场 lvl_id={lvl_id}")
        else:
            print(f"[地图] uid={uid} 当前在普通地图")
        _print_json(info)
    finally:
        await client.close()


async def cmd_get_all_player_data(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.get_all_player_data(uid)
        _print_ret_code(resp)
        # 解析 push_list 中的每个 data item
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            summary = {}
            for item in items:
                name = item.get("name", "")
                raw = item.get("data", "")
                try:
                    parsed = _json.loads(raw)
                    summary[name] = parsed
                except (_json.JSONDecodeError, TypeError):
                    summary[name] = raw
            _print_json(summary)
        except (KeyError, IndexError, TypeError):
            _print_json(resp)
    finally:
        await client.close()


async def cmd_get_map_overview(uid_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.get_map_overview(uid)
        _print_ret_code(resp)
        _print_json(resp)
    finally:
        await client.close()


async def cmd_get_map_detail(uid_str: str, x_str: str, y_str: str, *extra: str, env: str = None):
    """普通地图地块详情查询（以 x,y 为中心，默认 10x10 范围）

    用法:
      get_map_detail <uid> <center_x> <center_y> [size]
      get_map_detail 20001946 154 170       # 默认 10x10
      get_map_detail 20001946 154 170 3     # 3x3

    返回 mapBidObjs: 每个地块含玩家城/建筑/行军等详细对象。
    """
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        x, y = int(x_str), int(y_str)
        size = int(extra[0]) if extra else 10

        map_objs = await client.get_map_area(uid, x, y, size)

        if not map_objs:
            print("[无数据] 未获取到地块内容")
            return

        # 统计
        type_names = {2: '玩家城', 6: '资源点', 12: '联盟资源点'}
        total_objs = 0
        for block in map_objs:
            total_objs += len(block.get("objs", []))
        empty = sum(1 for b in map_objs if not b.get("objs"))
        print(f"范围={size}x{size}, 地块={len(map_objs)}, 有对象={total_objs}, 空地块={empty}\n")

        # 逐地块打印
        for block in map_objs:
            objs = block.get("objs", [])
            if not objs:
                continue
            bid = block["bid"]
            for obj in objs:
                basic = obj.get("objBasic", {})
                obj_type = basic.get("type", 0)
                uid_val = basic.get("uid", "0")
                pos_val = basic.get("pos", "0")
                obj_id = basic.get("id", "")
                type_name = type_names.get(obj_type, f"type={obj_type}")

                detail = ""
                if obj_type == 2:
                    city = obj.get("cityInfo", {})
                    detail = (f" 等级={city.get('level', '?')} 战力={city.get('force', 0)}"
                              f" {city.get('uname', '')}")
                elif obj_type == 6:
                    res = obj.get("resourceInfo", {})
                    detail = f" key={basic.get('key', '?')} 资源={res.get('resourceCount', 0)}"
                elif obj_type == 12:
                    al = obj.get("alResourcePointInfo", {})
                    al_name = al.get("alNick") or al.get("alName") or "无"
                    detail = f" key={basic.get('key', '?')} 联盟={al_name}"

                print(f"  bid={bid} {type_name} uid={uid_val} pos={pos_val} id={obj_id}{detail}")

    finally:
        await client.close()


async def cmd_get_battle_report(uid_str: str, report_id: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.get_battle_report(uid, report_id)
        _print_ret_code(resp)
        _print_json(resp)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 行动命令
# ---------------------------------------------------------------------------


async def cmd_move_city(uid_str: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, x, y = int(uid_str), int(x_str), int(y_str)
        resp = await client.move_city(uid, x, y)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"移城成功 → ({x},{y})")
        else:
            print(f"移城失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_move_city(uid_str: str, lvl_id_str: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id, x, y = int(uid_str), int(lvl_id_str), int(x_str), int(y_str)
        resp = await client.lvl_move_city(uid, x, y, lvl_id)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA移城成功 → lvl_id={lvl_id} ({x},{y})")
        else:
            print(f"AVA移城失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_scout_player(uid_str: str, lvl_id_str: str, target_uid_str: str, x_str: str, y_str: str, env: str = None):
    """AVA 战场内侦查玩家"""
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id, target_uid = int(uid_str), int(lvl_id_str), int(target_uid_str)
        x, y = int(x_str), int(y_str)
        target_pos = encode_pos(x, y)
        resp = await client.lvl_scout_player(uid, lvl_id, target_uid, target_pos)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA侦查玩家成功 → uid={target_uid} ({x},{y})")
        else:
            print(f"AVA侦查玩家失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_scout_building(uid_str: str, lvl_id_str: str, building_id_str: str, x_str: str, y_str: str, env: str = None):
    """AVA 战场内侦查建筑"""
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id, building_id = int(uid_str), int(lvl_id_str), int(building_id_str)
        x, y = int(x_str), int(y_str)
        building_pos = encode_pos(x, y)
        resp = await client.lvl_scout_building(uid, lvl_id, building_id, building_pos)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA侦查建筑成功 → building_id={building_id} ({x},{y})")
        else:
            print(f"AVA侦查建筑失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_attack_player(uid_str: str, lvl_id_str: str, target_uid_str: str, x_str: str, y_str: str, env: str = None):
    """AVA 战场内攻打玩家"""
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id, target_uid = int(uid_str), int(lvl_id_str), int(target_uid_str)
        x, y = int(x_str), int(y_str)
        target_pos = encode_pos(x, y)
        target_id = f"2_{target_uid}_1"
        resp = await client.lvl_attack_player(uid, lvl_id, target_id, target_pos)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA攻打玩家成功 → target_uid={target_uid} ({x},{y})")
        else:
            print(f"AVA攻打玩家失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_attack_building(uid_str: str, lvl_id_str: str, building_id_str: str, x_str: str, y_str: str, env: str = None):
    """AVA 战场内攻打建筑

    用法: lvl_attack_building <uid> <lvl_id> <building_id> <x> <y>
    - target_type 自动从 building_id 提取（如 "10006_xxx" → 10006）
    """
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id = int(uid_str), int(lvl_id_str)
        building_id = building_id_str
        x, y = int(x_str), int(y_str)

        parts = building_id.split("_")
        target_type = int(parts[0]) if parts and parts[0].isdigit() else 10001

        building_pos = encode_pos(x, y)
        resp = await client.lvl_attack_building(uid, lvl_id, building_id, building_pos, target_type=target_type)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA攻打建筑成功 → building_id={building_id} type={target_type} ({x},{y})")
        else:
            print(f"AVA攻打建筑失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_reinforce_building(uid_str: str, lvl_id_str: str, building_id_str: str, env: str = None):
    """AVA 战场内驻防/增援我方建筑 (march_type=11, leader=0)

    用法: lvl_reinforce_building <uid> <lvl_id> <building_id>
    - target_type 自动从 building_id 提取（如 "10006_xxx" → 10006）
    - 驻防不需要坐标，target_info.pos 固定为 "nil"
    """
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id = int(uid_str), int(lvl_id_str)
        building_id = building_id_str

        parts = building_id.split("_")
        target_type = int(parts[0]) if parts and parts[0].isdigit() else 10006

        resp = await client.lvl_reinforce_building(uid, lvl_id, building_id, target_type=target_type)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA驻防建筑成功 → building_id={building_id} type={target_type}")
        else:
            print(f"AVA驻防建筑失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_rally_dismiss(uid_str: str, lvl_id_str: str, unique_id_str: str, env: str = None):
    """AVA 战场内解散集结"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id = int(uid_str), int(lvl_id_str)
        unique_id = unique_id_str  # 格式如 "107_xxx"
        resp = await client.lvl_rally_dismiss(uid, lvl_id, unique_id)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA解散集结成功 → unique_id={unique_id}")
        else:
            print(f"AVA解散集结失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_lvl_battle_login_get(uid_str: str, lvl_id_str: str, env: str = None):
    """AVA 战场登录数据查询（含部队、集结、建筑等完整信息）"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id = int(uid_str), int(lvl_id_str)
        resp = await client.lvl_battle_login_get(uid, lvl_id)
        code = _print_ret_code(resp)
        # 解析并打印每个 push data 的 name + 摘要
        try:
            for res_idx, res in enumerate(resp.get("res_data", [])):
                for push in res.get("push_list", []):
                    for item in push.get("data", []):
                        name = item.get("name", "?")
                        raw = item.get("data", "")
                        parsed = _json.loads(raw) if isinstance(raw, str) and raw else raw
                        # 摘要：大对象只打印 key 和数组长度
                        if isinstance(parsed, dict):
                            summary = {}
                            for k, v in parsed.items():
                                if isinstance(v, list):
                                    summary[k] = f"[{len(v)} items]"
                                elif isinstance(v, dict):
                                    summary[k] = f"{{...{len(v)} keys}}"
                                else:
                                    summary[k] = v
                            print(f"\n[{name}] {_json.dumps(summary, ensure_ascii=False)}")
                        else:
                            print(f"\n[{name}] {str(parsed)[:200]}")
                        # 对关键数据打印完整内容
                        if any(k in name for k in ("objs", "troop", "rally")):
                            _print_json(parsed)
        except (KeyError, IndexError, TypeError, _json.JSONDecodeError) as e:
            print(f"[warn] 解析异常: {e}")
            _print_json(resp)
    finally:
        await client.close()


async def cmd_lvl_svr_map_get(uid_str: str, lvl_id_str: str, x_str: str, y_str: str, *extra: str, env: str = None):
    """AVA 战场地块详情查询（以 x,y 为中心，默认 10x10 范围）

    用法:
      lvl_svr_map_get <uid> <lvl_id> <center_x> <center_y> [size]
      lvl_svr_map_get 20010366 29999 154 170       # 默认 10x10
      lvl_svr_map_get 20010366 29999 154 170 3     # 3x3

    返回 mapBidObjs: 每个地块含玩家城/建筑/行军等详细对象。
    """
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id = int(uid_str), int(lvl_id_str)
        x, y = int(x_str), int(y_str)
        size = int(extra[0]) if extra else 10

        map_objs = await client.lvl_get_map_area(uid, lvl_id, x, y, size)

        if not map_objs:
            print("[无数据] 未获取到地块内容")
            return

        # 统计
        type_names = {10101: '玩家城', 10001: '建筑', 101: '行军队伍'}
        total_objs = 0
        for block in map_objs:
            total_objs += len(block.get("objs", []))
        empty = sum(1 for b in map_objs if not b.get("objs"))
        print(f"范围={size}x{size}, 地块={len(map_objs)}, 有对象={total_objs}, 空地块={empty}\n")

        # 逐地块打印
        for block in map_objs:
            objs = block.get("objs", [])
            if not objs:
                continue
            bid = block["bid"]
            for obj in objs:
                basic = obj.get("objBasic", {})
                obj_type = basic.get("type", 0)
                uid_val = basic.get("uid", "0")
                pos_val = basic.get("pos", "0")
                obj_id = basic.get("id", "")
                type_name = type_names.get(obj_type, f"type={obj_type}")

                detail = ""
                if obj_type == 10101:
                    city = obj.get("cityInfo", {})
                    detail = (f" 等级={city.get('level', '?')} 兵力={city.get('curTroopNum', 0)}"
                              f" camp={basic.get('camp', '?')} {city.get('uname', '')}")
                elif obj_type == 10001:
                    bld = obj.get("building", {})
                    detail = f" 驻军={bld.get('curTroopNum', 0)} camp={basic.get('camp', '?')}"
                elif obj_type == 101:
                    march = obj.get("marchBasic", {})
                    detail = f" marchType={march.get('marchType', '?')}"

                print(f"  bid={bid} {type_name} uid={uid_val} pos={pos_val} id={obj_id}{detail}")

    finally:
        await client.close()


async def cmd_lvl_create_rally(uid_str: str, lvl_id_str: str, target_id_str: str, x_str: str, y_str: str, *extra: str, env: str = None):
    """AVA 战场内发起集结（对建筑或玩家）

    用法:
      lvl_create_rally <uid> <lvl_id> <building_id> <x> <y> [prepare_time]
      lvl_create_rally <uid> <lvl_id> <target_uid> <x> <y> [prepare_time]

    target_id 为纯数字时视为玩家 UID，否则视为建筑 unique_id。
    """
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid, lvl_id = int(uid_str), int(lvl_id_str)
        x, y = int(x_str), int(y_str)
        prepare_time = int(extra[0]) if extra else 60

        # 判断目标类型：纯数字=玩家，否则=建筑
        is_player = target_id_str.isdigit()
        if is_player:
            target_uid = int(target_id_str)
            target_id = f"2_{target_uid}_1"
            print(f"AVA发起集结(玩家) uid={uid} → target_uid={target_uid} ({x},{y}) prepare={prepare_time}s")
            resp = await client.lvl_create_rally(uid, lvl_id, target_id, prepare_time=prepare_time)
        else:
            building_id = target_id_str
            print(f"AVA发起集结(建筑) uid={uid} → building={building_id} ({x},{y}) prepare={prepare_time}s")
            resp = await client.lvl_create_rally_building(uid, lvl_id, building_id, prepare_time=prepare_time)

        code = _print_ret_code(resp)
        if code == 0:
            print(f"AVA集结发起成功")
        else:
            print(f"AVA集结发起失败", file=sys.stderr)
        # 打印完整响应（调试用）
        _print_json(resp)
    finally:
        await client.close()


async def cmd_attack_player(uid_str: str, target_uid_str: str, x_str: str, y_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        target_uid = int(target_uid_str)
        x, y = int(x_str), int(y_str)
        # 可选参数: soldier_id count (指定出征兵种和数量)
        march_info = None
        if len(extra) >= 2:
            soldier_id = extra[0]
            soldier_count = int(extra[1])
            march_info = {
                "hero": {"vice": {}},
                "over_defend": False,
                "leader": 1,
                "soldier_total_num": soldier_count,
                "heros": {},
                "queue_id": 6001,
                "soldier": {soldier_id: soldier_count},
                "carry_lord": 1,
            }
        resp = await client.attack_player(uid, target_uid, x, y, march_info=march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"部队已出发攻击 uid={target_uid} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_attack_building(uid_str: str, building_id: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        x, y = int(x_str), int(y_str)
        target_info = {"id": building_id, "pos": str(encode_pos(x, y))}
        march_info = {}  # 使用默认部队
        resp = await client.attack_building(uid, target_info, march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"部队已出发攻击建筑 {building_id} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_reinforce_building(uid_str: str, building_id: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        x, y = int(x_str), int(y_str)
        target_info = {"id": building_id, "pos": str(encode_pos(x, y))}
        march_info = {}
        resp = await client.reinforce_building(uid, target_info, march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"部队已出发驻防建筑 {building_id} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_scout_player(uid_str: str, target_uid_str: str, x_str: str, y_str: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        target_uid = int(target_uid_str)
        x, y = int(x_str), int(y_str)
        resp = await client.scout_player(uid, target_uid, x, y)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"侦察 uid={target_uid} @ ({x},{y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_create_rally(uid_str: str, target_uid_str: str, x_str: str, y_str: str, *extra: str, env: str = None):
    import time as _time
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        target_uid = int(target_uid_str)
        x, y = int(x_str), int(y_str)
        # 可选参数: soldier_id count [prepare_time]
        march_info = {}
        prepare_time = 300
        if len(extra) >= 2:
            soldier_id = extra[0]
            soldier_count = int(extra[1])
            march_info = {
                "hero": {"vice": []},
                "over_defend": False,
                "leader": 1,
                "soldier_total_num": soldier_count,
                "heros": {},
                "queue_id": 6001,
                "soldier": {soldier_id: soldier_count},
                "carry_lord": 1,
            }
            if len(extra) >= 3:
                prepare_time = int(extra[2])
        elif len(extra) == 1:
            prepare_time = int(extra[0])
        target_id = f"2_{target_uid}_1"
        target_info = {"id": target_id}
        timestamp = str(int(_time.time() * 1_000_000))
        resp = await client.create_rally(uid, target_info, march_info, prepare_time,
                                         timestamp=timestamp)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"集结已发起 target_uid={target_uid} @ ({x},{y}) 准备时间={prepare_time}s")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_join_rally(uid_str: str, rally_id: str, rally_x_str: str, rally_y_str: str, *extra: str, env: str = None):
    """加入集结: join_rally <uid> <rally_id> <rally_x> <rally_y> [soldier_id count]"""
    from src.executor.game_api import GameAPIClient
    from src.utils.coords import encode_pos
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        rally_x, rally_y = int(rally_x_str), int(rally_y_str)
        rally_pos = encode_pos(rally_x, rally_y)
        target_info = {"id": rally_id, "pos": rally_pos}
        # 可选参数: soldier_id count
        march_info = {}
        if len(extra) >= 2:
            soldier_id = extra[0]
            soldier_count = int(extra[1])
            march_info = {
                "hero": {"vice": []},
                "over_defend": False,
                "leader": 0,
                "soldier_total_num": soldier_count,
                "heros": {},
                "queue_id": 6001,
                "soldier": {soldier_id: soldier_count},
                "carry_lord": 1,
            }
        resp = await client.join_rally(uid, target_info, march_info)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已加入集结 {rally_id} @ ({rally_x},{rally_y})")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_recall_troop(uid_str: str, *troop_ids: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        if not troop_ids:
            print("请提供至少一个 troop_id", file=sys.stderr)
            sys.exit(1)
        resp = await client.recall_troop(uid, list(troop_ids))
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已召回部队 {list(troop_ids)}")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_rally_dismiss(uid_str: str, unique_id: str = "", env: str = None):
    """解散集结: rally_dismiss <uid> <rally_unique_id>  (107_xxx_1)"""
    if not unique_id or not unique_id.strip():
        print("[error] unique_id 不能为空，用法: rally_dismiss <uid> <rally_unique_id>  (例: 107_xxx_1)")
        return
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.rally_dismiss(uid, unique_id)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已解散集结 {unique_id}")
        _print_json(resp)
    finally:
        await client.close()


async def cmd_recall_reinforce(uid_str: str, unique_id: str, env: str = None):
    """撤回增援部队: recall_reinforce <uid> <troop_unique_id>  (101_xxx_1)"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.recall_reinforce(uid, unique_id)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已撤回增援 {unique_id}")
        _print_json(resp)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 简化输出查询（供脚本解析）
# ---------------------------------------------------------------------------


async def cmd_get_gem(uid_str: str, env: str = None):
    """查询宝石数量，输出纯数字"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.send_cmd("get_player_info", uid, list=["svr_gem_stat"])
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_gem_stat":
                    gem_data = _json.loads(item["data"])
                    print(gem_data.get("gem", 0))
                    return
        except (KeyError, IndexError, TypeError):
            pass
        print(0)
    finally:
        await client.close()


async def cmd_get_soldiers(uid_str: str, soldier_id_str: str, env: str = None):
    """查询指定兵种数量，输出纯数字"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        soldier_id = int(soldier_id_str)
        info = await client.get_player_info(uid, modules=["svr_soldier"])
        for s in info.get("soldiers", []):
            if s.get("id") == soldier_id:
                print(s.get("value", 0))
                return
        print(0)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# GM 命令
# ---------------------------------------------------------------------------


async def cmd_add_gem(uid_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        gem_num = int(extra[0]) if extra else None
        resp = await client.add_gem(uid, gem_num)
        code = _print_ret_code(resp)
        # 解析返回的宝石数量
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_gem_stat":
                    gem_data = _json.loads(item["data"])
                    print(f"当前宝石: {gem_data.get('gem', 'N/A')}")
                    break
        except (KeyError, IndexError, TypeError):
            if code == 0:
                print("宝石设置成功")
    finally:
        await client.close()


async def cmd_add_soldiers(uid_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        soldier_id = int(extra[0]) if len(extra) > 0 else None
        soldier_num = int(extra[1]) if len(extra) > 1 else None
        resp = await client.add_soldiers(uid, soldier_id, soldier_num)
        code = _print_ret_code(resp)
        # 解析返回的士兵数据
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_soldier":
                    soldier_data = _json.loads(item["data"])
                    soldiers = soldier_data.get("list", [])
                    print("当前士兵:")
                    for s in soldiers:
                        if s.get("value", 0) > 0:
                            print(f"  id={s['id']} 数量={s['value']}")
                    break
        except (KeyError, IndexError, TypeError):
            if code == 0:
                print("士兵添加成功")
    finally:
        await client.close()


async def cmd_add_resource(uid_str: str, *extra: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        op_type = int(extra[0]) if extra else None
        resp = await client.add_resource(uid, op_type)
        code = _print_ret_code(resp)
        if code == 0:
            print("资源添加成功")
        _print_json(resp)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# L1 决策命令
# ---------------------------------------------------------------------------


async def cmd_l1_decide(*args: str, env: str = None):
    """单小队 L1 决策调试"""
    import re as _re
    from src.executor.game_api import GameAPIClient
    from src.perception.data_sync import DataSyncer
    from src.ai.llm_client import LLMClient
    from src.ai.l1_leader import L1Leader

    # 解析参数
    remaining = list(args)
    json_mode = "--json" in args
    dry_run = "--dry-run" in args
    l1_prompt = None  # type: str | None
    mock_l2 = None  # type: str | None

    # 检查 --l1-prompt 参数 (支持 --l1-prompt=value 和 --l1-prompt value)
    prompt_args = [a for a in args if a.startswith("--l1-prompt")]
    if prompt_args:
        parts = prompt_args[0].split("=", 1)
        if len(parts) == 2:
            l1_prompt = parts[1]
        else:
            idx = args.index(prompt_args[0])
            if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
                l1_prompt = args[idx + 1]

    # 检查 --mock-l2 参数 (支持 --mock-l2=value 和 --mock-l2 value)
    mock_l2_args = [a for a in args if a.startswith("--mock-l2")]
    if mock_l2_args:
        parts = mock_l2_args[0].split("=", 1)
        if len(parts) == 2:
            mock_l2 = parts[1]
        else:
            idx = args.index(mock_l2_args[0])
            if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
                mock_l2 = args[idx + 1]

    # 清理 remaining：移除所有已知 flag 和它们的值
    remaining = []
    skip_next = False
    lvl_id = 0  # AVA 战场 ID
    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a in ("--json", "--dry-run"):
            continue
        if a.startswith("--l1-prompt") or a.startswith("--mock-l2"):
            if "=" not in a:
                skip_next = True
            continue
        if a == "--ava":
            skip_next = True
            if i + 1 < len(args):
                lvl_id = int(args[i + 1])
            continue
        remaining.append(a)

    if not remaining:
        print("Usage: l1_decide <squad_id> [--dry-run] [--json] [--l1-prompt <name>] [--mock-l2 <order>]", file=sys.stderr)
        sys.exit(1)

    squad_id = int(remaining[0])
    config = _load_config()

    # 查找小队
    squad = None
    for sq in config.squads.squads:
        if sq.squad_id == squad_id:
            squad = sq
            break
    if squad is None:
        print(f"[FAIL] Squad not found: squad_id={squad_id}", file=sys.stderr)
        available = [sq.squad_id for sq in config.squads.squads]
        print(f"  Available: {available}", file=sys.stderr)
        sys.exit(1)

    # 创建 LLM 客户端
    if not dry_run and not _check_llm_config(config):
        sys.exit(1)

    try:
        llm = LLMClient(config.system.llm, dry_run=dry_run)
    except (ValueError, ImportError) as e:
        print(f"[FAIL] LLM init failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 调试命令：启用 AI 模块完整日志（打印 prompt 和 response 全文）
    ai_logger = logging.getLogger("src.ai")
    ai_logger.setLevel(logging.DEBUG)
    if not ai_logger.handlers:
        _h = logging.StreamHandler()
        _h.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S"))
        ai_logger.addHandler(_h)
        ai_logger.propagate = False

    client = GameAPIClient(env=env)
    syncer = DataSyncer(client, config)
    try:
        # 同步数据
        snapshot = await syncer.sync(loop_id=0, lvl_id=lvl_id)
        print(f"Sync complete: {len(snapshot.accounts)} accounts, "
              f"{len(snapshot.enemies)} enemies, {len(snapshot.buildings)} buildings"
              + (f" (AVA lvl_id={lvl_id})" if lvl_id else ""))

        # 解析 mock L2 指令（提取本小队的 order）
        l2_order = ""
        if mock_l2:
            # 支持 "[小队 N (Name)] ..." 格式
            m = _re.search(r'\[小队\s+(\d+)\s*\([^)]*\)\]\s*(.+)', mock_l2)
            if m:
                if int(m.group(1)) == squad_id:
                    l2_order = m.group(2).strip()
                else:
                    print(f"[warn] mock-l2 指定的小队 {m.group(1)} 与当前小队 {squad_id} 不匹配，忽略")
            else:
                # 无小队前缀，直接作为通用指令
                l2_order = mock_l2.strip()
            if l2_order:
                print(f"L2 order: {l2_order}")

        # L1 决策
        # --ava 时如果没有显式指定 --l1-prompt，自动使用 ava prompt
        effective_l1_prompt = l1_prompt if l1_prompt else ("ava" if lvl_id else None)
        leader = L1Leader(config, llm, squad, prompt_template=effective_l1_prompt)
        instructions = await leader.decide(snapshot, l2_order=l2_order)

        print(f"\nSquad {squad_id} ({squad.name}) generated {len(instructions)} instructions:")

        if json_mode:
            _print_json([i.model_dump(mode="json") for i in instructions])
        else:
            for i, instr in enumerate(instructions):
                print(f"  [{i+1}] {instr.action.value} uid={instr.uid}", end="")
                if instr.target_x or instr.target_y:
                    print(f" → ({instr.target_x},{instr.target_y})", end="")
                if instr.target_uid:
                    print(f" target={instr.target_uid}", end="")
                if instr.building_id:
                    print(f" building={instr.building_id}", end="")
                if instr.reason:
                    print(f" ({instr.reason})", end="")
                print()
    finally:
        await llm.close()
        await client.close()


async def cmd_l2_decide(*args: str, env: str = None):
    """L2 军团指挥官决策调试"""
    from src.executor.game_api import GameAPIClient
    from src.perception.data_sync import DataSyncer
    from src.ai.llm_client import LLMClient
    from src.ai.l2_commander import L2Commander

    remaining = [a for a in args if a not in ("--json", "--dry-run")]
    json_mode = "--json" in args
    dry_run = "--dry-run" in args

    # 解析 --ava <lvl_id>
    lvl_id = 0
    if "--ava" in remaining:
        ava_idx = remaining.index("--ava")
        if ava_idx + 1 < len(remaining):
            lvl_id = int(remaining[ava_idx + 1])
            remaining = remaining[:ava_idx] + remaining[ava_idx + 2:]
        else:
            remaining = remaining[:ava_idx]

    config = _load_config()

    # 创建 LLM 客户端
    if not dry_run and not _check_llm_config(config):
        sys.exit(1)

    try:
        llm = LLMClient(config.system.llm, dry_run=dry_run)
    except (ValueError, ImportError) as e:
        print(f"[FAIL] LLM 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 调试命令：启用 AI 模块完整日志（打印 prompt 和 response 全文）
    ai_logger = logging.getLogger("src.ai")
    ai_logger.setLevel(logging.DEBUG)
    if not ai_logger.handlers:
        _h = logging.StreamHandler()
        _h.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S"))
        ai_logger.addHandler(_h)
        ai_logger.propagate = False

    client = GameAPIClient(env=env)
    syncer = DataSyncer(client, config)
    try:
        # 同步数据
        snapshot = await syncer.sync(loop_id=0, lvl_id=lvl_id)
        print(f"同步完成: {len(snapshot.accounts)} 账号, "
              f"{len(snapshot.enemies)} 敌方, {len(snapshot.buildings)} 建筑"
              + (f" (AVA lvl_id={lvl_id})" if lvl_id else ""))

        # L2 决策
        l2_prompt = "ava" if lvl_id else None
        commander = L2Commander(config, llm, prompt_template=l2_prompt)
        orders = await commander.decide(snapshot)

        print(f"\nL2 军团指挥官生成 {len(orders)} 条指令:")

        if json_mode:
            # 输出为 JSON 数组格式
            orders_json = [
                {"squad_id": sid, "order": order}
                for sid, order in orders.items()
            ]
            _print_json(orders_json)
        else:
            for sid, order in sorted(orders.items()):
                # 查找小队名称
                squad_name = next(
                    (sq.name for sq in config.squads.squads if sq.squad_id == sid),
                    f"squad_{sid}"
                )
                print(f"  [小队 {sid} ({squad_name})] {order}")

            # 显示未收到指令的小队
            all_squad_ids = {sq.squad_id for sq in config.squads.squads}
            missing = all_squad_ids - orders.keys()
            if missing:
                print(f"\n  [未分配指令的小队] {sorted(missing)}")
    finally:
        await llm.close()
        await client.close()


# ---------------------------------------------------------------------------
# L1 视图命令
# ---------------------------------------------------------------------------


async def cmd_l1_view(*args: str, env: str = None):
    """构建并显示 L1 小队局部视图"""
    from src.executor.game_api import GameAPIClient
    from src.perception.data_sync import DataSyncer
    from src.perception.l1_view import L1ViewBuilder

    remaining = [a for a in args if a not in ("--json",)]
    json_mode = "--json" in args

    # 解析 --ava <lvl_id>
    lvl_id = 0
    if "--ava" in remaining:
        ava_idx = remaining.index("--ava")
        if ava_idx + 1 < len(remaining):
            lvl_id = int(remaining[ava_idx + 1])
            remaining = remaining[:ava_idx] + remaining[ava_idx + 2:]
        else:
            remaining = remaining[:ava_idx]

    if not remaining:
        print("用法: l1_view <squad_id> [--json] [--ava <lvl_id>]", file=sys.stderr)
        sys.exit(1)

    squad_id = int(remaining[0])
    config = _load_config()

    # 查找小队
    squad = None
    for sq in config.squads.squads:
        if sq.squad_id == squad_id:
            squad = sq
            break
    if squad is None:
        print(f"[FAIL] 未找到 squad_id={squad_id}", file=sys.stderr)
        available = [sq.squad_id for sq in config.squads.squads]
        print(f"  可用: {available}", file=sys.stderr)
        sys.exit(1)

    client = GameAPIClient(env=env)
    syncer = DataSyncer(client, config)
    try:
        snapshot = await syncer.sync(loop_id=0, lvl_id=lvl_id)
        builder = L1ViewBuilder(config)
        view = builder.build(snapshot, squad)

        if json_mode:
            _print_json(view.model_dump(mode="json"))
        else:
            text = builder.format_text(view)
            print(text)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# LLM 命令
# ---------------------------------------------------------------------------


async def cmd_llm_test(*args: str, env: str = None):
    """测试 LLM 连通性"""
    from src.ai.llm_client import LLMClient

    config = _load_config()
    dry_run = "--dry-run" in args

    if not dry_run and not _check_llm_config(config):
        sys.exit(1)

    try:
        client = LLMClient(config.system.llm, dry_run=dry_run)
    except (ValueError, ImportError) as e:
        print(f"[FAIL] LLM 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = await client.chat_json(
            system_prompt="你是一个测试助手。请用 JSON 格式回答。",
            user_prompt='回答 {"status": "ok", "message": "连接成功"}',
        )
        print(f"[OK] LLM 响应:")
        _print_json(result)
    except Exception as e:
        print(f"[FAIL] LLM 调用失败: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 主循环命令
# ---------------------------------------------------------------------------


async def cmd_run(*args: str, env: str = None):
    """启动 AI 主循环"""
    from src.executor.game_api import GameAPIClient
    from src.controller.loop import AIController

    config = _load_config()

    # 解析参数
    max_rounds = 0
    dry_run = "--dry-run" in args
    mock_l2 = None  # type: str | None
    l1_prompt = None  # type: str | None
    llm_timeout = None  # type: int | None
    lvl_id = 0  # AVA 战场 ID
    remaining = list(args)
    i = 0
    while i < len(remaining):
        arg = remaining[i]
        if arg == "--once":
            max_rounds = 1
        elif arg == "--dry-run":
            pass  # 已处理
        elif arg == "--rounds" and i + 1 < len(remaining):
            max_rounds = int(remaining[i + 1])
            i += 1
        elif arg.startswith("--loop.interval_seconds") and i + 1 < len(remaining):
            config.system.loop.interval_seconds = int(remaining[i + 1])
            i += 1
        elif arg == "--mock-l2" and i + 1 < len(remaining):
            mock_l2 = remaining[i + 1]
            i += 1
        elif arg == "--l1-prompt" and i + 1 < len(remaining):
            l1_prompt = remaining[i + 1]
            i += 1
        elif arg == "--llm-timeout" and i + 1 < len(remaining):
            llm_timeout = int(remaining[i + 1])
            config.system.llm.timeout_seconds = llm_timeout
            i += 1
        elif arg == "--ava" and i + 1 < len(remaining):
            lvl_id = int(remaining[i + 1])
            i += 1
        i += 1

    # 显示 LLM 配置
    if llm_timeout is not None:
        print(f"[config] LLM 超时已覆盖为 {llm_timeout}s")

    # 创建 LLM 客户端（可选）
    llm_client = None
    if dry_run:
        try:
            from src.ai.llm_client import LLMClient
            llm_client = LLMClient(config.system.llm, dry_run=True)
        except ImportError as e:
            print(f"[warn] LLM 未启用: {e}", file=sys.stderr)
    elif _check_llm_config(config):
        try:
            from src.ai.llm_client import LLMClient
            llm_client = LLMClient(config.system.llm)
        except (ValueError, ImportError) as e:
            print(f"[warn] LLM 未启用: {e}", file=sys.stderr)
    else:
        print("[info] L1/L2 AI 决策将被跳过，主循环仅执行 Sync 阶段")

    client = GameAPIClient(env=env)
    controller = AIController(config, client, llm_client=llm_client,
                             mock_l2=mock_l2, l1_prompt=l1_prompt,
                             lvl_id=lvl_id)
    try:
        await controller.run(max_rounds=max_rounds)
    finally:
        if llm_client:
            await llm_client.close()
        await client.close()


# ---------------------------------------------------------------------------
# 数据同步命令
# ---------------------------------------------------------------------------


async def cmd_sync(*args: str, env: str = None):
    """数据同步 — 并发获取所有账号 + 地图数据"""
    from src.executor.game_api import GameAPIClient
    from src.perception.data_sync import DataSyncer

    config = _load_config()
    client = GameAPIClient(env=env)
    syncer = DataSyncer(client, config)

    try:
        # 判断模式: sync --json / sync --ava <lvl_id> / sync <uid> / sync
        json_mode = "--json" in args
        remaining = [a for a in args if a != "--json"]

        # 解析 --ava <lvl_id>
        lvl_id = 0
        if "--ava" in remaining:
            ava_idx = remaining.index("--ava")
            if ava_idx + 1 < len(remaining):
                lvl_id = int(remaining[ava_idx + 1])
                remaining = remaining[:ava_idx] + remaining[ava_idx + 2:]
            else:
                remaining = remaining[:ava_idx]

        if remaining:
            # 单账号模式
            uid = int(remaining[0])
            # 自动检测 AVA 状态（除非已通过 --ava 指定）
            if not lvl_id:
                detected_lvl = await client.get_player_lvl_info(uid)
                if detected_lvl:
                    lvl_id = detected_lvl
                    print(f"[自动检测] uid={uid} 当前在 AVA 战场 lvl_id={lvl_id}")
                else:
                    print(f"[自动检测] uid={uid} 当前在普通地图")
            else:
                print(f"[AVA] 使用指定 lvl_id={lvl_id}")

            result = await syncer.sync_single_account(uid)
            from src.perception.data_sync import SyncError
            if isinstance(result, SyncError):
                print(f"[FAIL] 同步失败 uid={uid}: {result.message}", file=sys.stderr)
                sys.exit(1)
            elif json_mode:
                _print_json(result.model_dump(mode="json"))
            else:
                print(f"同步完成 uid={uid}")
                print(f"  名称: {result.name}")
                print(f"  坐标: ({result.city_pos[0]},{result.city_pos[1]})")
                print(f"  联盟: {result.alliance_name} (id={result.alliance_id})")
                print(f"  兵种: {len(result.soldiers)} 种, 总兵力 {sum(s.value for s in result.soldiers)}")
                print(f"  英雄: {len(result.heroes)} 个")
                print(f"  小队: {result.group_id}")
            return

        # 全量同步
        snapshot = await syncer.sync(loop_id=0, lvl_id=lvl_id)

        if json_mode:
            _print_json(snapshot.model_dump(mode="json"))
        else:
            # 摘要输出
            print(f"同步完成 (耗时 {snapshot.sync_time}s)")
            print(f"  账号: {len(snapshot.accounts)} 个")
            print(f"  建筑: {len(snapshot.buildings)} 个")
            print(f"  敌方: {len(snapshot.enemies)} 个")
            print(f"  错误: {len(snapshot.errors)} 个")

            # 前几个账号详情
            if snapshot.accounts:
                print("\n  账号列表 (前5):")
                for i, (uid, acct) in enumerate(snapshot.accounts.items()):
                    if i >= 5:
                        print(f"    ... 还有 {len(snapshot.accounts) - 5} 个")
                        break
                    total_soldiers = sum(s.value for s in acct.soldiers)
                    print(f"    uid={uid} {acct.name} ({acct.city_pos[0]},{acct.city_pos[1]}) "
                          f"兵力={total_soldiers} 小队={acct.group_id}")

            if snapshot.buildings:
                print(f"\n  建筑列表:")
                for b in snapshot.buildings:
                    side = "中立" if b.alliance_id == 0 else f"联盟{b.alliance_id}"
                    print(f"    {b.unique_id} type={b.obj_type} ({b.pos[0]},{b.pos[1]}) {side}")

            if snapshot.enemies:
                print(f"\n  敌方列表:")
                for e in snapshot.enemies:
                    print(f"    uid={e.uid} ({e.city_pos[0]},{e.city_pos[1]}) 联盟={e.alliance_id}")

            if snapshot.errors:
                print(f"\n  错误详情:")
                for err in snapshot.errors:
                    print(f"    uid={err.uid} [{err.step}] {err.message}")
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# L0 执行器命令
# ---------------------------------------------------------------------------


def _parse_l0_shorthand(args: list[str]):
    """将简写模式参数解析为 AIInstruction 的 dict

    简写格式:
      MOVE_CITY <uid> <x> <y>
      ATTACK_TARGET <uid> <target_uid> <x> <y>
      ATTACK_TARGET <uid> --building <building_id> <x> <y>
      SCOUT <uid> <target_uid> <x> <y>
      GARRISON_BUILDING <uid> <building_id> <x> <y>
      INITIATE_RALLY <uid> <target_id> <x> <y> [prepare_time]
      JOIN_RALLY <uid> <rally_id>
      RETREAT <uid> <troop_id...>
    """
    if len(args) < 2:
        print("用法: l0 <ACTION> <uid> <args...>", file=sys.stderr)
        sys.exit(1)

    action = args[0].upper()
    uid = int(args[1])
    # 过滤掉 --soldier 及其参数，避免干扰位置参数解析
    raw_rest = args[2:]
    rest = []
    i = 0
    while i < len(raw_rest):
        if raw_rest[i] == "--soldier":
            i += 3  # 跳过 --soldier <id> <count>
        else:
            rest.append(raw_rest[i])
            i += 1
    data: dict = {"action": action, "uid": uid}

    if action == "MOVE_CITY":
        if len(rest) < 2:
            print("用法: l0 MOVE_CITY <uid> <x> <y>", file=sys.stderr)
            sys.exit(1)
        data["target_x"] = int(rest[0])
        data["target_y"] = int(rest[1])

    elif action == "ATTACK_TARGET":
        if rest and rest[0] == "--building":
            # 攻击建筑模式
            if len(rest) < 4:
                print("用法: l0 ATTACK_TARGET <uid> --building <building_id> <x> <y>", file=sys.stderr)
                sys.exit(1)
            data["building_id"] = rest[1]
            data["target_x"] = int(rest[2])
            data["target_y"] = int(rest[3])
        else:
            # 攻击玩家模式
            if len(rest) < 3:
                print("用法: l0 ATTACK_TARGET <uid> <target_uid> <x> <y>", file=sys.stderr)
                sys.exit(1)
            data["target_uid"] = int(rest[0])
            data["target_x"] = int(rest[1])
            data["target_y"] = int(rest[2])

    elif action == "SCOUT":
        if len(rest) < 3:
            print("用法: l0 SCOUT <uid> <target_uid> <x> <y>", file=sys.stderr)
            sys.exit(1)
        data["target_uid"] = int(rest[0])
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])

    elif action == "GARRISON_BUILDING":
        if len(rest) < 3:
            print("用法: l0 GARRISON_BUILDING <uid> <building_id> <x> <y>", file=sys.stderr)
            sys.exit(1)
        data["building_id"] = rest[0]
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])

    elif action == "INITIATE_RALLY":
        if len(rest) < 3:
            print("用法: l0 INITIATE_RALLY <uid> <target_id> <x> <y> [prepare_time]", file=sys.stderr)
            sys.exit(1)
        # target_id: 如果像整数则认为是 target_uid，否则是 building_id
        target_id = rest[0]
        try:
            data["target_uid"] = int(target_id)
        except ValueError:
            data["building_id"] = target_id
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])
        if len(rest) > 3:
            data["prepare_time"] = int(rest[3])

    elif action == "JOIN_RALLY":
        if len(rest) < 1:
            print("用法: l0 JOIN_RALLY <uid> <rally_id>", file=sys.stderr)
            sys.exit(1)
        data["rally_id"] = rest[0]

    elif action == "RETREAT":
        if len(rest) < 1:
            print("用法: l0 RETREAT <uid> <troop_id...>", file=sys.stderr)
            sys.exit(1)
        data["troop_ids"] = list(rest)

    # --- AVA 战场指令 ---
    elif action == "LVL_MOVE_CITY":
        if len(rest) < 2:
            print("用法: l0 LVL_MOVE_CITY <uid> <x> <y>", file=sys.stderr)
            sys.exit(1)
        data["target_x"] = int(rest[0])
        data["target_y"] = int(rest[1])

    elif action == "LVL_ATTACK_BUILDING":
        if len(rest) < 3:
            print("用法: l0 LVL_ATTACK_BUILDING <uid> <building_id> <x> <y> [building_key]", file=sys.stderr)
            sys.exit(1)
        data["building_id"] = rest[0]
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])
        if len(rest) > 3:
            data["building_key"] = int(rest[3])

    elif action == "LVL_REINFORCE_BUILDING":
        if len(rest) < 1:
            print("用法: l0 LVL_REINFORCE_BUILDING <uid> <building_id> [building_key]", file=sys.stderr)
            sys.exit(1)
        data["building_id"] = rest[0]
        if len(rest) > 1:
            data["building_key"] = int(rest[1])

    elif action == "LVL_ATTACK_PLAYER":
        if len(rest) < 3:
            print("用法: l0 LVL_ATTACK_PLAYER <uid> <target_uid> <x> <y>", file=sys.stderr)
            sys.exit(1)
        data["target_uid"] = int(rest[0])
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])

    elif action == "LVL_SCOUT_PLAYER":
        if len(rest) < 3:
            print("用法: l0 LVL_SCOUT_PLAYER <uid> <target_uid> <x> <y>", file=sys.stderr)
            sys.exit(1)
        data["target_uid"] = int(rest[0])
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])

    elif action == "LVL_SCOUT_BUILDING":
        if len(rest) < 3:
            print("用法: l0 LVL_SCOUT_BUILDING <uid> <building_id> <x> <y> [building_key]", file=sys.stderr)
            sys.exit(1)
        data["building_id"] = rest[0]
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])
        if len(rest) > 3:
            data["building_key"] = int(rest[3])

    elif action == "LVL_INITIATE_RALLY":
        if len(rest) < 3:
            print("用法: l0 LVL_INITIATE_RALLY <uid> <target_uid> <x> <y> [prepare_time]", file=sys.stderr)
            sys.exit(1)
        data["target_uid"] = int(rest[0])
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])
        if len(rest) > 3:
            data["prepare_time"] = int(rest[3])

    elif action == "LVL_INITIATE_RALLY_BUILDING":
        if len(rest) < 3:
            print("用法: l0 LVL_INITIATE_RALLY_BUILDING <uid> <building_id> <x> <y> [prepare_time]", file=sys.stderr)
            sys.exit(1)
        data["building_id"] = rest[0]
        data["target_x"] = int(rest[1])
        data["target_y"] = int(rest[2])
        if len(rest) > 3:
            data["prepare_time"] = int(rest[3])

    elif action == "LVL_JOIN_RALLY":
        if len(rest) < 1:
            print("用法: l0 LVL_JOIN_RALLY <uid> <rally_id> [x] [y]", file=sys.stderr)
            sys.exit(1)
        data["rally_id"] = rest[0]
        if len(rest) > 2:
            data["target_x"] = int(rest[1])
            data["target_y"] = int(rest[2])

    elif action == "LVL_RALLY_DISMISS":
        if len(rest) < 1:
            print("用法: l0 LVL_RALLY_DISMISS <uid> <rally_id>", file=sys.stderr)
            sys.exit(1)
        data["rally_id"] = rest[0]

    elif action == "LVL_RECALL_TROOP":
        if len(rest) < 1:
            print("用法: l0 LVL_RECALL_TROOP <uid> <troop_unique_id>", file=sys.stderr)
            sys.exit(1)
        data["troop_unique_id"] = rest[0]

    elif action == "LVL_RECALL_REINFORCE":
        if len(rest) < 1:
            print("用法: l0 LVL_RECALL_REINFORCE <uid> <troop_unique_id>", file=sys.stderr)
            sys.exit(1)
        data["troop_unique_id"] = rest[0]

    elif action == "LVL_SPEED_UP":
        if len(rest) < 1:
            print("用法: l0 LVL_SPEED_UP <uid> <troop_unique_id>", file=sys.stderr)
            sys.exit(1)
        data["troop_unique_id"] = rest[0]

    elif action == "LVL_RECALL_FROM_BUILDING":
        if len(rest) < 1:
            print("用法: l0 LVL_RECALL_FROM_BUILDING <uid> <troop_id...> [x] [y]", file=sys.stderr)
            sys.exit(1)
        # 最后两个参数如果是数字，可能是坐标
        data["troop_ids"] = list(rest)

    else:
        _all_actions = [e.value for e in __import__('src.executor.l0_executor', fromlist=['ActionType']).ActionType]
        print(f"未知 action: {action}", file=sys.stderr)
        print(f"支持: {', '.join(_all_actions)}", file=sys.stderr)
        sys.exit(1)

    # 统一解析 --soldier <id> <count>（所有 action 通用）
    if "--soldier" in args:
        idx = args.index("--soldier")
        if idx + 2 < len(args):
            data["soldier_id"] = int(args[idx + 1])
            data["soldier_count"] = int(args[idx + 2])
        else:
            print("用法: --soldier <soldier_id> <count>", file=sys.stderr)
            sys.exit(1)

    return data


async def cmd_l0(*args: str, env: str = None):
    """L0 执行器 — 支持 JSON 模式和简写模式"""
    from src.executor.game_api import GameAPIClient
    from src.executor.l0_executor import AIInstruction, L0Executor

    if not args:
        print("用法:", file=sys.stderr)
        print("  JSON 模式:  l0 '{\"action\":\"MOVE_CITY\",\"uid\":123,...}'", file=sys.stderr)
        print("  简写模式:  l0 MOVE_CITY <uid> <x> <y>", file=sys.stderr)
        sys.exit(1)

    # 判断是 JSON 模式还是简写模式
    first = args[0].strip()
    if first.startswith("{"):
        # JSON 模式: 直接反序列化
        try:
            instr = AIInstruction.model_validate_json(first)
        except Exception as e:
            print(f"JSON 解析失败: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # 简写模式: 解析位置参数
        try:
            data = _parse_l0_shorthand(list(args))
        except (ValueError, IndexError) as e:
            print(f"参数解析失败: {e}", file=sys.stderr)
            sys.exit(1)
        try:
            instr = AIInstruction.model_validate(data)
        except Exception as e:
            print(f"指令构造失败: {e}", file=sys.stderr)
            sys.exit(1)

    # 加载配置 + 创建执行器
    config = _load_config()
    client = GameAPIClient(env=env)
    executor = L0Executor(client, config)
    try:
        # 先打印解析后的指令（方便确认）
        print(f"[L0] {instr.action.value} uid={instr.uid}", end="")
        if instr.target_x or instr.target_y:
            print(f" → ({instr.target_x},{instr.target_y})", end="")
        if instr.target_uid:
            print(f" target_uid={instr.target_uid}", end="")
        if instr.building_id:
            print(f" building={instr.building_id}", end="")
        if instr.rally_id:
            print(f" rally={instr.rally_id}", end="")
        if instr.troop_ids:
            print(f" troops={instr.troop_ids}", end="")
        if instr.soldier_id:
            print(f" soldier_id={instr.soldier_id} count={instr.soldier_count}", end="")
        print()

        # 拉取玩家状态用于 Smart L0 预处理（距离检查 + 部队去重）
        accounts: dict[int, "PlayerState"] = {}
        try:
            from src.models.player_state import PlayerState
            info = await client.get_player_info(instr.uid)
            ps = PlayerState.from_sync_info(info)
            accounts[instr.uid] = ps
            print(f"[L0] 已加载玩家状态: city_pos={ps.city_pos}, troops={len(ps.troops)}")
        except Exception as e:
            print(f"[L0] 加载玩家状态失败（跳过预处理）: {e}")

        results = await executor.execute_batch([instr], accounts=accounts)
        result = results[0]
        if result.success:
            print(f"[OK] {result.message}")
        else:
            print(f"[FAIL] {result.error}", file=sys.stderr)
        if result.server_response:
            _print_json(result.server_response)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# uid_helper 命令 — 测试环境账号准备工具
# ---------------------------------------------------------------------------


def _find_squad_for_uid(squads_config, uid: int, alliance_key: str = None):
    """在 squads 配置中查找 uid 所属小队，返回 (squad, seq_index)"""
    groups = squads_config.alliances
    keys = [alliance_key] if alliance_key and alliance_key in groups else list(groups.keys())
    for key in keys:
        for sq in groups[key].squads:
            if uid in sq.member_uids:
                idx = sq.member_uids.index(uid)
                return sq, idx
    return None, 0


async def cmd_uid_copy(src_uid_str: str, tar_uid_str: str, env: str = None):
    """复制账号数据: uid_copy <src_uid> <tar_uid>"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        src_uid = int(src_uid_str)
        tar_uid = int(tar_uid_str)
        # 1) 复制
        resp = await client.send_cmd("copy_player", src_uid,
                                     src_uid=src_uid, src_sid=1,
                                     tar_uid=tar_uid, tar_sid=1)
        code = _print_ret_code(resp)
        if code != 0:
            print(f"[FAIL] copy_player 失败", file=sys.stderr)
            return

        # 2) 验证: 读取目标账号信息
        src_info = await client.get_player_info(src_uid, modules=["svr_soldier"])
        tar_info = await client.get_player_info(tar_uid, modules=["svr_soldier"])
        src_total = sum(s.get("value", 0) for s in src_info.get("soldiers", []))
        tar_total = sum(s.get("value", 0) for s in tar_info.get("soldiers", []))
        print(f"复制完成: {src_uid} → {tar_uid}")
        print(f"  源兵力: {src_total}  目标兵力: {tar_total}")
        if src_total > 0 and tar_total == src_total:
            print("  [OK] 兵力匹配")
        elif src_total > 0:
            print(f"  [warn] 兵力不匹配 (src={src_total} tar={tar_total})")
    finally:
        await client.close()


async def cmd_uid_create_al(name: str, nick: str, env: str = None):
    """创建联盟: uid_create_al <name> <nick>"""
    from src.executor.game_api import GameAPIClient
    config = _load_config()
    # 用第一个 accounts uid 作为创建者
    creator_uid = config.accounts.active_uids()[0]
    client = GameAPIClient(env=env)
    try:
        resp = await client.send_cmd("create_alliance", creator_uid,
                                     name=name, nick=nick)
        code = _print_ret_code(resp)
        if code == 0:
            # 解析返回的 aid
            try:
                items = resp["res_data"][0]["push_list"][0]["data"]
                for item in items:
                    if item.get("name") == "svr_alliance_create":
                        data = _json.loads(item["data"])
                        aid = data.get("aid", "N/A")
                        print(f"联盟创建成功: name='{name}' nick='{nick}' aid={aid}")
                        return
            except (KeyError, IndexError, TypeError):
                pass
            print(f"联盟创建成功 (uid={creator_uid})")
        else:
            print("[FAIL] 创建联盟失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_uid_join_al(aid_str: str, *uid_args: str, env: str = None):
    """加入联盟并改名: uid_join_al <aid> <uid1> [uid2...]"""
    from src.executor.game_api import GameAPIClient
    if not uid_args:
        print("用法: uid_join_al <aid> <uid1> [uid2...]", file=sys.stderr)
        sys.exit(1)

    aid = int(aid_str)
    config = _load_config()
    client = GameAPIClient(env=env)
    try:
        for uid_str in uid_args:
            uid = int(uid_str)
            # 1) 加入联盟
            resp = await client.send_cmd("join_alliance", uid, target_aid=aid)
            code = _print_ret_code(resp)
            if code != 0:
                print(f"  [FAIL] uid={uid} 加入联盟失败", file=sys.stderr)
                continue

            # 2) 生成昵称
            squad, idx = _find_squad_for_uid(config.squads, uid)
            if squad:
                nickname = f"{squad.name}{idx+1:03d}_{uid}"
            else:
                nickname = f"Member_{uid}"

            # 3) 改名
            resp = await client.send_cmd("change_name", uid, name=nickname)
            code2 = _print_ret_code(resp)
            if code2 == 0:
                print(f"  uid={uid} 加入联盟 {aid}, 昵称='{nickname}'")
            else:
                print(f"  uid={uid} 加入联盟 {aid}, 改名失败", file=sys.stderr)

        # 4) 验证: 查看成员列表
        any_uid = int(uid_args[0])
        resp = await client.send_cmd("get_al_members", any_uid,
                                     header_overrides={"aid": aid})
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_al_members":
                    data = _json.loads(item["data"])
                    count = data.get("count", len(data.get("list", [])))
                    print(f"\n联盟 {aid} 当前成员数: {count}")
                    for m in data.get("list", []):
                        print(f"  uid={m['uid']} {m.get('name', '')}")
                    break
        except (KeyError, IndexError, TypeError):
            pass
    finally:
        await client.close()


async def cmd_uid_members(aid_str: str, env: str = None):
    """查看联盟成员: uid_members <aid>"""
    from src.executor.game_api import GameAPIClient
    config = _load_config()
    any_uid = config.accounts.active_uids()[0]
    aid = int(aid_str)
    client = GameAPIClient(env=env)
    try:
        resp = await client.send_cmd("get_al_members", any_uid,
                                     header_overrides={"aid": aid})
        _print_ret_code(resp)
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_al_members":
                    data = _json.loads(item["data"])
                    count = data.get("count", len(data.get("list", [])))
                    print(f"联盟 {aid} 成员数: {count}")
                    for m in data.get("list", []):
                        print(f"  uid={m['uid']} {m.get('name', '')}")
                    return
        except (KeyError, IndexError, TypeError):
            pass
        _print_json(resp)
    finally:
        await client.close()


async def cmd_uid_setup(alliance_key: str, src_uid_str: str, *uid_args: str, env: str = None):
    """一站式账号准备: uid_setup <alliance_key> <src_uid> <tar_uid1> [tar_uid2...]

    对每个 tar_uid 执行: copy_player → join_alliance → change_name
    """
    from src.executor.game_api import GameAPIClient
    if not uid_args:
        print("用法: uid_setup <alliance_key> <src_uid> <tar_uid1> [tar_uid2...]", file=sys.stderr)
        sys.exit(1)

    src_uid = int(src_uid_str)
    config = _load_config()
    squads = config.squads

    # 获取目标联盟 aid
    if alliance_key not in squads.alliances:
        print(f"[FAIL] 未知联盟 key: {alliance_key}", file=sys.stderr)
        print(f"  可用: {list(squads.alliances.keys())}", file=sys.stderr)
        sys.exit(1)
    target_aid = squads.alliances[alliance_key].aid

    client = GameAPIClient(env=env)
    try:
        ok_count = 0
        fail_count = 0
        for uid_str in uid_args:
            tar_uid = int(uid_str)
            print(f"\n--- {tar_uid} ---")

            # 1) copy_player
            resp = await client.send_cmd("copy_player", src_uid,
                                         src_uid=src_uid, src_sid=1,
                                         tar_uid=tar_uid, tar_sid=1)
            code = _print_ret_code(resp)
            if code != 0:
                print(f"  [FAIL] copy_player 失败", file=sys.stderr)
                fail_count += 1
                continue

            # 2) join_alliance
            resp = await client.send_cmd("join_alliance", tar_uid, target_aid=target_aid)
            code = _print_ret_code(resp)
            if code != 0:
                print(f"  [FAIL] join_alliance 失败", file=sys.stderr)
                fail_count += 1
                continue

            # 3) change_name
            squad, idx = _find_squad_for_uid(squads, tar_uid, alliance_key)
            if squad:
                nickname = f"{squad.name}{idx+1:03d}_{tar_uid}"
            else:
                nickname = f"Member_{tar_uid}"
            resp = await client.send_cmd("change_name", tar_uid, name=nickname)
            code = _print_ret_code(resp)
            if code == 0:
                print(f"  复制+加入+改名完成: 昵称='{nickname}'")
                ok_count += 1
            else:
                print(f"  复制+加入完成, 改名失败", file=sys.stderr)
                ok_count += 1

        print(f"\n=== 完成: {ok_count} 成功, {fail_count} 失败 ===")

        # 验证摘要
        any_uid = int(uid_args[0])
        resp = await client.send_cmd("get_al_members", any_uid,
                                     header_overrides={"aid": target_aid})
        try:
            items = resp["res_data"][0]["push_list"][0]["data"]
            for item in items:
                if item.get("name") == "svr_al_members":
                    data = _json.loads(item["data"])
                    count = data.get("count", len(data.get("list", [])))
                    print(f"联盟 {target_aid} 当前成员数: {count}")
                    break
        except (KeyError, IndexError, TypeError):
            pass
    finally:
        await client.close()


async def cmd_uid_ava_add(lvl_id_str: str, uid_str: str, camp_id_str: str, env: str = None):
    """将玩家添加到AVA战场名单: uid_ava_add <lvl_id> <uid> <camp_id>"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        lvl_id = int(lvl_id_str)
        uid = int(uid_str)
        camp_id = int(camp_id_str)
        print(f"将 uid={uid} 添加到 AVA 战场 lvl_id={lvl_id} 阵营={camp_id}")
        # 使用 param_overrides 避免 uid 参数冲突（header uid vs 命令参数 uid）
        resp = await client.send_cmd("ava_add_player", uid,
                                     param_overrides={"lvl_id": lvl_id, "uid": uid, "camp_id": camp_id})
        code = _print_ret_code(resp)
        if code == 0:
            print(f"  [OK] uid={uid} 已添加到战场 {lvl_id} 阵营 {camp_id}")
        else:
            print(f"  [FAIL] 添加失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_uid_ava_enter(lvl_id_str: str, uid_str: str, env: str = None):
    """进入AVA战场: uid_ava_enter <lvl_id> <uid>"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        lvl_id = int(lvl_id_str)
        uid = int(uid_str)
        print(f"uid={uid} 进入 AVA 战场 lvl_id={lvl_id}")

        # 进入战场前先检查当前战场状态
        before_lvl = await client.get_player_lvl_info(uid)
        print(f"  进入前: lvl_id={before_lvl}")

        resp = await client.send_cmd("ava_enter_battle", uid, lvl_id=lvl_id)
        code = _print_ret_code(resp)
        if code == 0:
            # 验证: 读取进入后的战场信息
            after_lvl = await client.get_player_lvl_info(uid)
            print(f"  进入后: lvl_id={after_lvl}")
            if after_lvl == lvl_id:
                print(f"  [OK] uid={uid} 成功进入战场 {lvl_id}")
            else:
                print(f"  [warn] 战场ID不匹配 (预期={lvl_id} 实际={after_lvl})", file=sys.stderr)
        else:
            print(f"  [FAIL] 进入战场失败", file=sys.stderr)
    finally:
        await client.close()


async def cmd_uid_ava_status(uid_str: str, env: str = None):
    """查询玩家AVA战场状态: uid_ava_status <uid>"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        lvl_id = await client.get_player_lvl_info(uid)
        if lvl_id == 0:
            print(f"uid={uid} 当前在普通地图 (未进入AVA战场)")
        else:
            print(f"uid={uid} 当前在 AVA 战场 lvl_id={lvl_id}")
    finally:
        await client.close()


async def cmd_uid_ava_leave(uid_str: str, env: str = None):
    """离开AVA战场: uid_ava_leave <uid>"""
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        print(f"uid={uid} 离开 AVA 战场")

        # 离开战场前先检查当前战场状态
        before_lvl = await client.get_player_lvl_info(uid)
        print(f"  离开前: lvl_id={before_lvl}")

        if before_lvl == 0:
            print(f"  [info] uid={uid} 当前不在任何战场，无需离开")
            return

        # 调用离开战场命令，需要在 header 中传入 lvl_id
        resp = await client.send_cmd("ava_leave_battle", uid, header_overrides={"lvl_id": before_lvl})
        code = _print_ret_code(resp)
        if code == 0:
            # 验证: 读取离开后的战场信息
            after_lvl = await client.get_player_lvl_info(uid)
            print(f"  离开后: lvl_id={after_lvl}")
            if after_lvl == 0:
                print(f"  [OK] uid={uid} 成功离开战场")
            else:
                print(f"  [warn] 仍在战场中 (lvl_id={after_lvl})", file=sys.stderr)
        else:
            print(f"  [FAIL] 离开战场失败", file=sys.stderr)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 命令注册
# ---------------------------------------------------------------------------

COMMANDS = {
    # L2
    "l2_decide":            (cmd_l2_decide,             "[--ava <lvl_id>] [--dry-run] [--json]",  "L2 军团指挥官决策调试(AVA自动切换prompt)"),
    # L1
    "l1_view":              (cmd_l1_view,               "<squad_id> [--json]",                    "L1 小队局部视图"),
    "l1_decide":            (cmd_l1_decide,             "<squad_id> [--ava <lvl_id>] [--dry-run] [--json]", "L1 单小队决策调试(AVA自动切换prompt)"),
    # LLM
    "llm_test":             (cmd_llm_test,              "[--dry-run]",                            "测试 LLM 连通性"),
    # 主循环
    "run":                  (cmd_run,                   "[--rounds N] [--once] [--loop.interval_seconds N]", "启动 AI 主循环"),
    # 查询
    "get_player_pos":       (cmd_get_player_pos,       "<uid>",                              "查询玩家坐标"),
    "get_player_info":      (cmd_get_player_info,      "<uid>",                              "查询玩家完整信息(自动检测AVA)"),
    "get_all_player_data":  (cmd_get_all_player_data,  "<uid>",                              "查询玩家全量数据"),
    "get_map_overview":     (cmd_get_map_overview,      "<uid>",                              "查询地图缩略信息"),
    "get_map_detail":       (cmd_get_map_detail,        "<uid> <x> <y> [size]",               "普通地图地块详情查询"),
    "get_battle_report":    (cmd_get_battle_report,     "<uid> <report_id>",                  "查询战报"),
    # 行动
    "move_city":            (cmd_move_city,             "<uid> <x> <y>",                      "移城到指定坐标"),
    "lvl_move_city":        (cmd_lvl_move_city,         "<uid> <lvl_id> <x> <y>",             "AVA移城到指定坐标"),
    "lvl_scout_player":     (cmd_lvl_scout_player,      "<uid> <lvl_id> <target_uid> <x> <y>", "AVA侦查玩家"),
    "lvl_scout_building":   (cmd_lvl_scout_building,    "<uid> <lvl_id> <building_id> <x> <y>", "AVA侦查建筑"),
    "lvl_attack_player":    (cmd_lvl_attack_player,     "<uid> <lvl_id> <target_uid> <x> <y>", "AVA攻打玩家"),
    "lvl_attack_building":    (cmd_lvl_attack_building,     "<uid> <lvl_id> <building_id> <x> <y>", "AVA攻打建筑"),
    "lvl_reinforce_building": (cmd_lvl_reinforce_building,  "<uid> <lvl_id> <building_id>",         "AVA驻防/增援我方建筑"),
    "lvl_battle_login_get": (cmd_lvl_battle_login_get,   "<uid> <lvl_id>",                     "AVA战场登录数据查询"),
    "lvl_svr_map_get":      (cmd_lvl_svr_map_get,       "<uid> <lvl_id> <x> <y> [size]",      "AVA战场地块详情查询"),
    "lvl_create_rally":     (cmd_lvl_create_rally,      "<uid> <lvl_id> <target_id> <x> <y> [prepare_time]", "AVA发起集结(建筑/玩家)"),
    "lvl_rally_dismiss":    (cmd_lvl_rally_dismiss,     "<uid> <lvl_id> <unique_id>",         "AVA解散集结"),
    "attack_player":        (cmd_attack_player,         "<uid> <target_uid> <x> <y> [soldier_id count]", "攻击玩家"),
    "attack_building":      (cmd_attack_building,       "<uid> <building_id> <x> <y>",        "攻击建筑"),
    "reinforce_building":   (cmd_reinforce_building,    "<uid> <building_id> <x> <y>",        "驻防建筑"),
    "scout_player":         (cmd_scout_player,          "<uid> <target_uid> <x> <y>",         "侦察玩家"),
    "create_rally":         (cmd_create_rally,          "<uid> <target_uid> <x> <y> [soldier_id count] [prepare_time]", "发起集结"),
    "join_rally":           (cmd_join_rally,            "<uid> <rally_id> <rally_x> <rally_y> [soldier_id count]", "加入集结"),
    "rally_dismiss":        (cmd_rally_dismiss,         "<uid> <rally_unique_id>",            "解散集结 (107_xxx_1)"),
    "recall_troop":         (cmd_recall_troop,          "<uid> <troop_id...>",                "召回行军部队"),
    "recall_reinforce":     (cmd_recall_reinforce,      "<uid> <troop_unique_id>",            "撤回增援部队 (101_xxx_1)"),
    # 简化查询
    "get_gem":              (cmd_get_gem,               "<uid>",                              "查询宝石数量(纯数字)"),
    "get_soldiers":         (cmd_get_soldiers,          "<uid> <soldier_id>",                 "查询兵种数量(纯数字)"),
    # GM
    "add_gem":              (cmd_add_gem,               "<uid> [amount]",                     "GM: 添加宝石"),
    "add_soldiers":         (cmd_add_soldiers,          "<uid> [soldier_id] [num]",           "GM: 添加士兵"),
    "add_resource":         (cmd_add_resource,          "<uid> [op_type]",                    "GM: 添加资源"),
    # 数据同步
    "sync":                 (cmd_sync,                  "[--json] [--ava <lvl_id>] [uid]",    "数据同步(单账号自动检测AVA)"),
    # L0 执行器
    "l0":                   (cmd_l0,                    "<ACTION|JSON> <args...>",            "L0 执行器调试"),
    # uid_helper — 测试环境账号准备
    "uid_copy":             (cmd_uid_copy,              "<src_uid> <tar_uid>",                "复制账号数据"),
    "uid_create_al":        (cmd_uid_create_al,         "<name> <nick>",                      "创建联盟"),
    "uid_join_al":          (cmd_uid_join_al,           "<aid> <uid1> [uid2...]",             "加入联盟+改名"),
    "uid_members":          (cmd_uid_members,           "<aid>",                              "查看联盟成员"),
    "uid_setup":            (cmd_uid_setup,             "<alliance_key> <src_uid> <tar_uid...>", "一站式账号准备"),
    "uid_ava_add":          (cmd_uid_ava_add,           "<lvl_id> <uid> <camp_id>",           "添加到AVA战场名单"),
    "uid_ava_enter":        (cmd_uid_ava_enter,         "<lvl_id> <uid>",                     "进入AVA战场"),
    "uid_ava_status":       (cmd_uid_ava_status,        "<uid>",                              "查询AVA战场状态"),
    "uid_ava_leave":        (cmd_uid_ava_leave,         "<uid>",                              "离开AVA战场"),
}


def main():
    args = sys.argv[1:]

    # 解析 --mock 参数
    env = None
    if "--mock" in args:
        env = "mock"
        args.remove("--mock")

    # 解析 --llm <profile> 参数（全局 LLM profile 切换）
    llm_profile = None
    if "--llm" in args:
        idx = args.index("--llm")
        if idx + 1 < len(args):
            llm_profile = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            args = args[:idx]

    # 解析 --team <1|2> 参数（全局队伍切换）
    if "--team" in args:
        idx = args.index("--team")
        if idx + 1 < len(args):
            team_val = args[idx + 1]
            if team_val not in ("1", "2"):
                print(f"Error: --team 必须为 1 或 2, 收到 '{team_val}'", file=sys.stderr)
                sys.exit(1)
            global _team
            _team = int(team_val)
            args = args[:idx] + args[idx + 2:]
        else:
            args = args[:idx]

    # 解析 --verbose / -v 参数，控制日志级别
    log_level = logging.WARNING  # 默认只显示警告
    if "--verbose" in args or "-v" in args:
        log_level = logging.INFO
        if "--verbose" in args:
            args.remove("--verbose")
        if "-v" in args:
            args.remove("-v")
    if "--debug" in args:
        log_level = logging.DEBUG
        args.remove("--debug")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if len(args) < 1 or args[0] not in COMMANDS:
        # 打印模块 docstring 作为主帮助信息
        print(__doc__)
        print("全局参数:")
        print("  --mock                  使用 mock server")
        print("  --verbose / -v          INFO 级别日志")
        print("  --debug                 DEBUG 级别日志")
        print("  --llm <profile>         切换 LLM profile (如: zhipu / ollama)")
        print("  --team <1|2>            管理指定方 (1=我方, 2=敌方, 默认=1)")
        print()
        print("AI 决策调试 (l1_decide / l2_decide 自动打印完整 prompt 和 LLM 响应):")
        print("  l2_decide 参数:  [--ava <lvl_id>] [--dry-run] [--json]  (--ava 时自动使用 AVA 战场 prompt)")
        print("  l1_decide 参数:  <squad_id> [--ava <lvl_id>] [--mock-l2 \"<指令>\"] [--l1-prompt <name>] [--dry-run] [--json]")
        print("  run 额外参数:    [--ava <lvl_id>] [--mock-l2 \"<指令>\"] [--l1-prompt <name>] [--llm-timeout N] [--dry-run]")
        print()
        print("AVA 自动检测:")
        print("  get_player_info / sync <uid> 会自动检测玩家是否在 AVA 战场，无需手动指定 --ava")
        print()
        print("示例:")
        print("  python src/main.py sync 20001946                  # 单账号同步(自动检测AVA)")
        print("  python src/main.py sync --ava 29999")
        print("  python src/main.py l2_decide --ava 29999          # L2 使用 AVA prompt")
        print("  python src/main.py l1_view 1 --ava 29999")
        print("  python src/main.py l1_decide 1 --ava 29999 --mock-l2 \"[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )\" --l1-prompt ava")
        print("  python src/main.py --llm ollama l1_decide 1 --dry-run")
        print("  python src/main.py run --once --ava 29999 --mock-l2 \"...\" --l1-prompt ava --loop.interval_seconds 0")
        sys.exit(1)

    cmd_name = args[0]
    func, _, _ = COMMANDS[cmd_name]

    # 将 llm_profile 存入模块级变量，供 cmd_* 函数中 load_all 后切换
    global _llm_profile
    _llm_profile = llm_profile

    asyncio.run(func(*args[1:], env=env))


if __name__ == "__main__":
    main()
