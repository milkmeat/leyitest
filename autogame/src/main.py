"""WestGame AI 全自动化团战系统 — 入口

用法:
  python src/main.py [--mock] <command> <args...>

主循环:
  run                                           启动 AI 主循环（无限）
  run --rounds 3                                跑 3 轮退出
  run --once                                    等价 --rounds 1
  run --loop.interval_seconds 0                 覆盖循环间隔（测试用）

查询命令:
  get_player_pos <uid>                          查询玩家坐标
  get_player_info <uid>                         查询玩家完整信息
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
  create_rally <uid> <target_id> [prepare_time] 发起集结
  join_rally <uid> <rally_id>                   加入集结
  recall_troop <uid> <troop_id...>              召回行军部队
  recall_reinforce <uid> <unique_id>            召回增援/集结

查询命令(简化输出):
  get_gem <uid>                                 查询宝石数量（纯数字）
  get_soldiers <uid> <soldier_id>               查询指定兵种数量（纯数字）

GM 命令:
  add_gem <uid> [amount]                        添加宝石
  add_soldiers <uid> [soldier_id] [num]         添加士兵
  add_resource <uid> [op_type]                  添加资源

数据同步:
  sync                                          同步所有账号+地图（摘要输出）
  sync --json                                   同步并输出完整 JSON
  sync <uid>                                    仅同步单个账号（调试用）

L0 执行器（AI 指令调试）:
  l0 '{"action":"MOVE_CITY","uid":123,...}'     JSON 模式（模拟 L1 输出）
  l0 MOVE_CITY <uid> <x> <y>                   移城
  l0 ATTACK_TARGET <uid> <target_uid> <x> <y>  攻击玩家
  l0 ATTACK_TARGET <uid> --building <id> <x> <y> 攻击建筑
  l0 SCOUT <uid> <target_uid> <x> <y>          侦察
  l0 GARRISON_BUILDING <uid> <building_id> <x> <y> 驻防建筑
  l0 INITIATE_RALLY <uid> <target_id> <x> <y> [prepare_time] 发起集结
  l0 JOIN_RALLY <uid> <rally_id>               加入集结
  l0 RETREAT <uid> <troop_id...>               召回部队
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
    """打印响应中的 ret_code，若非 0 则输出警告"""
    code = resp.get("res_header", {}).get("ret_code", -1)
    msg = resp.get("res_header", {}).get("err_msg", "")
    if code != 0:
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
        info = await client.get_player_info(uid)
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


async def cmd_get_map_detail(uid_str: str, *bid_args: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        bid_list = [int(b) for b in bid_args] if bid_args else []
        resp = await client.get_map_detail(uid, bid_list=bid_list)
        _print_ret_code(resp)
        _print_json(resp)
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


async def cmd_recall_reinforce(uid_str: str, unique_id: str, env: str = None):
    from src.executor.game_api import GameAPIClient
    client = GameAPIClient(env=env)
    try:
        uid = int(uid_str)
        resp = await client.recall_reinforce(uid, unique_id)
        code = _print_ret_code(resp)
        if code == 0:
            print(f"已召回增援 {unique_id}")
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
    from src.executor.game_api import GameAPIClient
    from src.config.loader import load_all
    from src.perception.data_sync import DataSyncer
    from src.ai.llm_client import LLMClient
    from src.ai.l1_leader import L1Leader

    remaining = [a for a in args if a not in ("--json", "--dry-run")]
    json_mode = "--json" in args
    dry_run = "--dry-run" in args

    if not remaining:
        print("用法: l1_decide <squad_id> [--dry-run] [--json]", file=sys.stderr)
        sys.exit(1)

    squad_id = int(remaining[0])
    config = load_all("config")

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

    # 创建 LLM 客户端
    if not dry_run and not _check_llm_config(config):
        sys.exit(1)

    try:
        llm = LLMClient(config.system.llm, dry_run=dry_run)
    except (ValueError, ImportError) as e:
        print(f"[FAIL] LLM 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)

    client = GameAPIClient(env=env)
    syncer = DataSyncer(client, config)
    try:
        # 同步数据
        snapshot = await syncer.sync(loop_id=0)
        print(f"同步完成: {len(snapshot.accounts)} 账号, "
              f"{len(snapshot.enemies)} 敌方, {len(snapshot.buildings)} 建筑")

        # L1 决策
        leader = L1Leader(config, llm, squad)
        instructions = await leader.decide(snapshot)

        print(f"\n小队 {squad_id} ({squad.name}) 生成 {len(instructions)} 条指令:")

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


# ---------------------------------------------------------------------------
# L1 视图命令
# ---------------------------------------------------------------------------


async def cmd_l1_view(*args: str, env: str = None):
    """构建并显示 L1 小队局部视图"""
    from src.executor.game_api import GameAPIClient
    from src.config.loader import load_all
    from src.perception.data_sync import DataSyncer
    from src.perception.l1_view import L1ViewBuilder

    remaining = [a for a in args if a not in ("--json",)]
    json_mode = "--json" in args

    if not remaining:
        print("用法: l1_view <squad_id> [--json]", file=sys.stderr)
        sys.exit(1)

    squad_id = int(remaining[0])
    config = load_all("config")

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
        snapshot = await syncer.sync(loop_id=0)
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
    from src.config.loader import load_all
    from src.ai.llm_client import LLMClient

    config = load_all("config")
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
    from src.config.loader import load_all
    from src.controller.loop import AIController

    config = load_all("config")

    # 解析参数
    max_rounds = 0
    dry_run = "--dry-run" in args
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
        i += 1

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
    controller = AIController(config, client, llm_client=llm_client)
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
    from src.config.loader import load_all
    from src.perception.data_sync import DataSyncer

    config = load_all("config")
    client = GameAPIClient(env=env)
    syncer = DataSyncer(client, config)

    try:
        # 判断模式: sync --json / sync <uid> / sync
        json_mode = "--json" in args
        remaining = [a for a in args if a != "--json"]

        if remaining:
            # 单账号模式
            uid = int(remaining[0])
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
        snapshot = await syncer.sync(loop_id=0)

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
    rest = args[2:]
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

    else:
        print(f"未知 action: {action}", file=sys.stderr)
        print("支持: MOVE_CITY, ATTACK_TARGET, SCOUT, GARRISON_BUILDING, "
              "INITIATE_RALLY, JOIN_RALLY, RETREAT", file=sys.stderr)
        sys.exit(1)

    return data


async def cmd_l0(*args: str, env: str = None):
    """L0 执行器 — 支持 JSON 模式和简写模式"""
    from src.executor.game_api import GameAPIClient
    from src.executor.l0_executor import AIInstruction, L0Executor
    from src.config.loader import load_all

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
    config = load_all("config")
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
        print()

        result = await executor.execute(instr)
        if result.success:
            print(f"[OK] {result.message}")
        else:
            print(f"[FAIL] {result.error}", file=sys.stderr)
        if result.server_response:
            _print_json(result.server_response)
    finally:
        await client.close()


# ---------------------------------------------------------------------------
# 命令注册
# ---------------------------------------------------------------------------

COMMANDS = {
    # L1
    "l1_view":              (cmd_l1_view,               "<squad_id> [--json]",                    "L1 小队局部视图"),
    "l1_decide":            (cmd_l1_decide,             "<squad_id> [--dry-run] [--json]",        "L1 单小队决策调试"),
    # LLM
    "llm_test":             (cmd_llm_test,              "[--dry-run]",                            "测试 LLM 连通性"),
    # 主循环
    "run":                  (cmd_run,                   "[--rounds N] [--once] [--loop.interval_seconds N]", "启动 AI 主循环"),
    # 查询
    "get_player_pos":       (cmd_get_player_pos,       "<uid>",                              "查询玩家坐标"),
    "get_player_info":      (cmd_get_player_info,      "<uid>",                              "查询玩家完整信息"),
    "get_all_player_data":  (cmd_get_all_player_data,  "<uid>",                              "查询玩家全量数据"),
    "get_map_overview":     (cmd_get_map_overview,      "<uid>",                              "查询地图缩略信息"),
    "get_map_detail":       (cmd_get_map_detail,        "<uid> [bid...]",                     "查询地图详细信息"),
    "get_battle_report":    (cmd_get_battle_report,     "<uid> <report_id>",                  "查询战报"),
    # 行动
    "move_city":            (cmd_move_city,             "<uid> <x> <y>",                      "移城到指定坐标"),
    "attack_player":        (cmd_attack_player,         "<uid> <target_uid> <x> <y> [soldier_id count]", "攻击玩家"),
    "attack_building":      (cmd_attack_building,       "<uid> <building_id> <x> <y>",        "攻击建筑"),
    "reinforce_building":   (cmd_reinforce_building,    "<uid> <building_id> <x> <y>",        "驻防建筑"),
    "scout_player":         (cmd_scout_player,          "<uid> <target_uid> <x> <y>",         "侦察玩家"),
    "create_rally":         (cmd_create_rally,          "<uid> <target_uid> <x> <y> [soldier_id count] [prepare_time]", "发起集结"),
    "join_rally":           (cmd_join_rally,            "<uid> <rally_id> [soldier_id count]", "加入集结"),
    "recall_troop":         (cmd_recall_troop,          "<uid> <troop_id...>",                "召回行军部队"),
    "recall_reinforce":     (cmd_recall_reinforce,      "<uid> <unique_id>",                  "召回增援/集结"),
    # 简化查询
    "get_gem":              (cmd_get_gem,               "<uid>",                              "查询宝石数量(纯数字)"),
    "get_soldiers":         (cmd_get_soldiers,          "<uid> <soldier_id>",                 "查询兵种数量(纯数字)"),
    # GM
    "add_gem":              (cmd_add_gem,               "<uid> [amount]",                     "GM: 添加宝石"),
    "add_soldiers":         (cmd_add_soldiers,          "<uid> [soldier_id] [num]",           "GM: 添加士兵"),
    "add_resource":         (cmd_add_resource,          "<uid> [op_type]",                    "GM: 添加资源"),
    # 数据同步
    "sync":                 (cmd_sync,                  "[--json] [uid]",                     "数据同步(全量/单账号)"),
    # L0 执行器
    "l0":                   (cmd_l0,                    "<ACTION|JSON> <args...>",            "L0 执行器调试"),
}


def main():
    args = sys.argv[1:]

    # 解析 --mock 参数
    env = None
    if "--mock" in args:
        env = "mock"
        args.remove("--mock")

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
        print("用法: python src/main.py [--mock] <command> <args...>\n")
        print("主循环:")
        _, a, desc = COMMANDS["run"]
        print(f"  {'run':25s} {a:40s} {desc}")
        print("  示例: run --once --loop.interval_seconds 0")
        print("\n查询命令:")
        for name in ["get_player_pos", "get_player_info", "get_all_player_data",
                      "get_map_overview", "get_map_detail", "get_battle_report"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        print("\n行动命令:")
        for name in ["move_city", "attack_player", "attack_building", "reinforce_building",
                      "scout_player", "create_rally", "join_rally", "recall_troop", "recall_reinforce"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        print("\n简化查询命令:")
        for name in ["get_gem", "get_soldiers"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        print("\nGM 命令:")
        for name in ["add_gem", "add_soldiers", "add_resource"]:
            _, a, desc = COMMANDS[name]
            print(f"  {name:25s} {a:40s} {desc}")
        print("\n数据同步:")
        _, a, desc = COMMANDS["sync"]
        print(f"  {'sync':25s} {a:40s} {desc}")
        print("  示例: sync                  # 全量同步摘要")
        print("  示例: sync --json           # 全量同步 JSON 输出")
        print("  示例: sync 20010366         # 单账号同步")
        print("\nL0 执行器:")
        _, a, desc = COMMANDS["l0"]
        print(f"  {'l0':25s} {a:40s} {desc}")
        print("  示例: l0 MOVE_CITY 20010413 500 500")
        print("  示例: l0 '{\"action\":\"MOVE_CITY\",\"uid\":20010413,\"target_x\":500,\"target_y\":500}'")
        sys.exit(1)

    cmd_name = args[0]
    func, _, _ = COMMANDS[cmd_name]
    asyncio.run(func(*args[1:], env=env))


if __name__ == "__main__":
    main()
