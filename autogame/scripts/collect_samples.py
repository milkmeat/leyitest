"""从 test server 采集所有命令的完整 JSON 响应，保存到 docs/samples/

用法:
  python scripts/collect_samples.py [uid1 uid2 ...]

默认使用 uid=20001946。每个命令的响应保存为独立 JSON 文件，
文件名格式: {cmd_name}__{uid}.json

采集的命令:
  查询类:
  - get_player_info (login_get，含 5 个模块)
  - get_all_player_data (game_server_login_get，全量数据)
  - game_server_login_get (按 sid 分别采集)
  - get_map_detail (game_svr_map_get)
  - get_battle_report (get_city_battle_report)
  行动类（用无效参数触发，仅采集响应结构）:
  - add_gem, add_soldiers, add_resource
  - scout_player, move_city, recall_troop, recall_reinforce
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.executor.game_api import GameAPIClient
from src.utils.coords import encode_pos

# 输出目录
SAMPLE_DIR = Path(_project_root) / "docs" / "samples"


def save_json(name: str, data: dict):
    """保存 JSON 到 docs/samples/"""
    filepath = SAMPLE_DIR / f"{name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    size = filepath.stat().st_size
    print(f"  -> {filepath.name} ({size:,} bytes)")


async def collect_for_uid(client: GameAPIClient, uid: int):
    """对单个 uid 采集所有查询命令"""
    suffix = f"__{uid}"

    # 1. get_player_info — 分模块采集，也做一次全量
    print(f"\n[{uid}] get_player_info (all modules)...")
    try:
        resp = await client.send_cmd("get_player_info", uid)
        save_json(f"get_player_info{suffix}", resp)
    except Exception as e:
        print(f"  ERROR: {e}")

    # 逐模块采集，看每个模块单独返回的结构
    modules = [
        "svr_lord_info_new",
        "svr_player",
        "svr_soldier",
        "svr_hero_list",
        "svr_buff",
    ]
    for mod in modules:
        print(f"[{uid}] get_player_info (module={mod})...")
        try:
            resp = await client.send_cmd("get_player_info", uid, all=0, list=[mod])
            save_json(f"get_player_info__{mod}{suffix}", resp)
        except Exception as e:
            print(f"  ERROR: {e}")

    # 2. get_all_player_data — 全量数据（最重要，包含部队、行军等）
    print(f"\n[{uid}] get_all_player_data...")
    try:
        resp = await client.send_cmd("get_all_player_data", uid)
        save_json(f"get_all_player_data{suffix}", resp)
    except Exception as e:
        print(f"  ERROR: {e}")

    # 3. game_server_login_get — 尝试不同 sid 看地图数据
    for sid in [0, 1]:
        print(f"\n[{uid}] game_server_login_get (sid={sid})...")
        try:
            resp = await client.send_cmd(
                "get_all_player_data", uid,
                header_overrides={"sid": sid},
            )
            save_json(f"game_server_login_get__sid{sid}{suffix}", resp)
        except Exception as e:
            print(f"  ERROR: {e}")

    # 4. get_map_detail — 尝试不同 bid_list
    print(f"\n[{uid}] get_map_detail (bid_list=[0])...")
    try:
        resp = await client.send_cmd("get_map_detail", uid, sid=0, bid_list=[0])
        save_json(f"get_map_detail__bid0{suffix}", resp)
    except Exception as e:
        print(f"  ERROR: {e}")

    print(f"[{uid}] get_map_detail (bid_list=[])...")
    try:
        resp = await client.send_cmd("get_map_detail", uid, sid=0, bid_list=[])
        save_json(f"get_map_detail__empty{suffix}", resp)
    except Exception as e:
        print(f"  ERROR: {e}")

    # 5. get_battle_report — 用空 id 看报错结构
    print(f"\n[{uid}] get_battle_report (id='')...")
    try:
        resp = await client.send_cmd("get_battle_report", uid, id="")
        save_json(f"get_battle_report{suffix}", resp)
    except Exception as e:
        print(f"  ERROR: {e}")

    # 6. 行动类命令 — 用无效参数触发，仅采集响应结构
    action_cmds = {
        "add_gem": {},
        "add_soldiers": {},
        "add_resource": {},
        "scout_player": {"tar_pos": encode_pos(500, 500)},
        "move_city": {"tar_pos": encode_pos(123, 234)},
        "recall_troop": {"march_info": {"ids": ["nonexist"]}},
        "recall_reinforce": {"unique_id": "nonexist"},
    }
    for cmd_name, overrides in action_cmds.items():
        print(f"\n[{uid}] {cmd_name}...")
        try:
            resp = await client.send_cmd(cmd_name, uid, **overrides)
            save_json(f"{cmd_name}{suffix}", resp)
        except Exception as e:
            print(f"  ERROR: {e}")


async def main(uids: list[int]):
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    # 写入采集元信息
    meta = {
        "collected_at": datetime.now().isoformat(),
        "uids": uids,
        "env": "test",
    }
    save_json("_meta", meta)

    client = GameAPIClient(env="test")
    try:
        for uid in uids:
            print(f"\n{'='*60}")
            print(f"采集 UID: {uid}")
            print(f"{'='*60}")
            await collect_for_uid(client, uid)
    finally:
        await client.close()

    print(f"\n采集完成！所有样本保存在: {SAMPLE_DIR}")
    print(f"共 {len(list(SAMPLE_DIR.glob('*.json')))} 个文件")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        uids = [int(x) for x in sys.argv[1:]]
    else:
        uids = [20001946]
    asyncio.run(main(uids))
