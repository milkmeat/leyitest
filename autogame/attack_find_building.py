"""attack_test.sh 辅助脚本：从 briefObjs 按 key 找建筑 uniqueId"""
import asyncio, json, sys
from src.executor.game_api import GameAPIClient

AVA_ID = int(sys.argv[1])
TARGET_KEY = sys.argv[2]  # 保持字符串，briefObj 的 key 是 str
PROBE_UID = int(sys.argv[3])

async def main():
    c = GameAPIClient()
    try:
        resp = await c.lvl_battle_login_get(PROBE_UID, AVA_ID)
        for res in resp.get("res_data", []):
            for push in res.get("push_list", []):
                for item in push.get("data", []):
                    if item.get("name") == "svr_lvl_brief_objs":
                        raw = item.get("data", "")
                        data = json.loads(raw) if isinstance(raw, str) and raw else raw
                        for o in data.get("briefObjs", []):
                            if o.get("key") == TARGET_KEY:
                                print(o.get("uniqueId", ""))
                                return
    finally:
        await c.close()

asyncio.run(main())
