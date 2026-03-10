"""获取每个命令在 test 服务器的实际完整响应，用于理解数据结构

用法: python scripts/dump_responses.py [uid]
"""

import asyncio
import json
import os
import sys

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.executor.game_api import GameAPIClient
from src.utils.coords import encode_pos


async def dump_all(uid: int):
    client = GameAPIClient(env="test")

    # 查询类命令 — 安全获取完整响应
    queries = {
        "get_all_player_data": {},
        "get_map_overview": {"sid": 0},
        "get_map_detail": {"sid": 0, "bid_list": [0]},
        "get_battle_report": {"id": "test"},
        "add_gem": {},
        "add_soldiers": {},
        "add_resource": {},
        "scout_player": {"tar_pos": encode_pos(500, 500)},
        "move_city": {"tar_pos": encode_pos(123, 234)},
        "recall_troop": {"march_info": {"ids": ["nonexist"]}},
        "recall_reinforce": {"unique_id": "nonexist"},
    }

    for cmd_name, overrides in queries.items():
        print(f"\n{'='*60}")
        print(f"CMD: {cmd_name}")
        print(f"{'='*60}")
        try:
            resp = await client.send_cmd(cmd_name, uid, **overrides)
            # 只打印前2000字符避免太长
            text = json.dumps(resp, indent=2, ensure_ascii=False)
            if len(text) > 2000:
                print(text[:2000] + "\n... [truncated]")
            else:
                print(text)
        except Exception as e:
            print(f"ERROR: {e}")

    await client.close()


if __name__ == "__main__":
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 20001946
    asyncio.run(dump_all(uid))
