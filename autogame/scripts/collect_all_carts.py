"""批量采集 AVA 战场内所有 coal cart (type=10300)

用法:
  python scripts/collect_all_carts.py <uid> [--ava <lvl_id>] [--interval <秒>]

示例:
  python scripts/collect_all_carts.py 20010643
  python scripts/collect_all_carts.py 20010643 --ava 29999
  python scripts/collect_all_carts.py 20010643 --interval 15

流程:
  1. 自动检测 lvl_id（若未指定）
  2. 查询 AVA 地图，找到所有 coal cart
  3. 派兵采集最近的 cart
  4. 轮询等待采集完成
  5. 重复 2-4 直到地图上无 cart
"""

import asyncio
import argparse
import json
import math
import sys
import os
import time

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.executor.game_api import GameAPIClient
from src.utils.coords import decode_pos


def parse_resp(resp: dict, uid: int) -> tuple:
    """从 lvl_battle_login_get 响应中解析玩家坐标、coal cart 列表和采集队列状态

    通过 svr_lvl_brief_objs 获取地图对象（玩家城 + cart），
    通过 svr_lvl_user_objs 获取当前玩家的部队队列状态（queueId=6003 或 marchType=21）。

    Returns:
        (player_pos, carts, busy_collect)
        player_pos: (x, y) or None
        carts: [(cart_id, x, y), ...]
        busy_collect: 采集队列是否被占用
    """
    player_pos = None
    carts = []
    busy_collect = False

    for res in resp.get("res_data", []):
        for push in res.get("push_list", []):
            for item in push.get("data", []):
                name = item.get("name", "")
                raw = item.get("data", "")
                try:
                    parsed = json.loads(raw) if isinstance(raw, str) else raw
                except (json.JSONDecodeError, TypeError):
                    continue

                # 地图对象：玩家城 + coal cart
                if "svr_lvl_brief_objs" in name:
                    brief_list = parsed.get("briefObjs", parsed.get("briefList", []))
                    for obj in brief_list:
                        obj_type = obj.get("type", 0)
                        raw_pos = obj.get("pos")
                        if not raw_pos:
                            continue
                        ox, oy = decode_pos(int(raw_pos))

                        if obj_type == 10101:
                            obj_uid = int(obj.get("uid", 0)) or int(obj.get("id", 0))
                            if obj_uid == uid:
                                player_pos = (ox, oy)

                        elif obj_type == 10300:
                            cart_id = (
                                obj.get("uniqueId", "")
                                or obj.get("unique_id", "")
                                or f"10300_{obj.get('id', 0)}"
                            )
                            carts.append((cart_id, ox, oy))

                # 玩家部队详情：检查采集队列 (queueId=6003 / marchType=27) 是否被占用
                # 采集部队 type=132, marchType=27, queueId=6003
                # marchType 在 marchBasic 中，queueId 在 troopInfo 中
                elif "svr_lvl_user_objs" in name:
                    for obj in parsed.get("objs", []):
                        march = obj.get("marchBasic", {})
                        troop_info = obj.get("troopInfo", {})
                        queue_id = int(troop_info.get("queueId", march.get("queueId", 0)))
                        march_type = int(march.get("marchType", 0))
                        if queue_id == 6003 or march_type == 27:
                            busy_collect = True

    return player_pos, carts, busy_collect


async def collect_all_carts(uid: int, lvl_id: int = None, poll_interval: int = 10):
    """主流程：循环采集所有 coal cart"""
    client = GameAPIClient()
    try:
        # 1. 自动检测 lvl_id
        if not lvl_id:
            print(f"[*] 正在检测 uid={uid} 的 AVA 战场状态...")
            lvl_id = await client.get_player_lvl_info(uid)
            if not lvl_id:
                print("[!] 该账号当前不在 AVA 战场中，请用 --ava <lvl_id> 指定", file=sys.stderr)
                return
        print(f"[*] AVA 战场 lvl_id={lvl_id}")

        round_num = 0
        total_collected = 0

        while True:
            round_num += 1
            print(f"\n{'='*50}")
            print(f"[轮次 {round_num}] 查询 AVA 地图...")

            # 2. 查询地图
            resp = await client.lvl_battle_login_get(uid, lvl_id)
            code = resp.get("res_header", {}).get("ret_code", -1)
            if code != 0:
                print(f"[!] 查询 AVA 地图失败 ret_code={code}", file=sys.stderr)
                break

            player_pos, carts, busy_collect = parse_resp(resp, uid)

            if not player_pos:
                print(f"[!] 未找到 uid={uid} 的城市位置", file=sys.stderr)
                break

            px, py = player_pos
            print(f"[*] 玩家位置: ({px}, {py})")
            print(f"[*] 发现 {len(carts)} 个 coal cart")

            # 如果正在采集中，等待完成
            if busy_collect:
                print(f"[~] 采集队列忙，等待 {poll_interval}s 后重试...")
                await asyncio.sleep(poll_interval)
                continue

            # 没有 cart 了，结束
            if not carts:
                print(f"\n[✓] 地图上已无 coal cart，共采集 {total_collected} 个")
                break

            # 3. 按距离排序，采集最近的
            carts_sorted = sorted(carts, key=lambda c: math.hypot(c[1] - px, c[2] - py))
            cart_id, cx, cy = carts_sorted[0]
            dist = math.hypot(cx - px, cy - py)

            print(f"[→] 采集最近 cart: id={cart_id} ({cx},{cy}) 距离={dist:.1f}格")

            # 列出剩余 cart
            if len(carts_sorted) > 1:
                print(f"    剩余 {len(carts_sorted)-1} 个待采集:")
                for i, (cid, ccx, ccy) in enumerate(carts_sorted[1:6], 1):
                    d = math.hypot(ccx - px, ccy - py)
                    print(f"      {i}. {cid} ({ccx},{ccy}) 距离={d:.1f}")
                if len(carts_sorted) > 6:
                    print(f"      ... 还有 {len(carts_sorted)-6} 个")

            # 4. 派遣采集
            collect_resp = await client.lvl_collect_cart(uid, lvl_id, cart_id)
            ret = collect_resp.get("res_header", {}).get("ret_code", -1)

            if ret == 0:
                total_collected += 1
                print(f"[✓] 采集派遣成功 #{total_collected}")
            else:
                print(f"[!] 采集派遣失败 ret_code={ret}", file=sys.stderr)
                # 失败也继续尝试下一个，可能是这个 cart 已被别人采了
                await asyncio.sleep(3)
                continue

            # 5. 轮询等待采集完成
            print(f"[~] 等待采集完成 (每 {poll_interval}s 检查一次)...")
            wait_start = time.time()
            while True:
                await asyncio.sleep(poll_interval)
                elapsed = time.time() - wait_start

                check_resp = await client.lvl_battle_login_get(uid, lvl_id)
                check_code = check_resp.get("res_header", {}).get("ret_code", -1)
                if check_code != 0:
                    print(f"[!] 轮询查询失败 ret_code={check_code}")
                    break

                _, _, still_busy = parse_resp(check_resp, uid)
                if not still_busy:
                    print(f"[✓] 采集完成 (耗时 {elapsed:.0f}s)")
                    break
                else:
                    print(f"    ... 采集中 ({elapsed:.0f}s)")

    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(description="批量采集 AVA 战场内所有 coal cart")
    parser.add_argument("uid", type=int, help="玩家 UID")
    parser.add_argument("--ava", type=int, default=None, help="AVA 战场 lvl_id（不指定则自动检测）")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数（默认10）")
    args = parser.parse_args()

    asyncio.run(collect_all_carts(args.uid, lvl_id=args.ava, poll_interval=args.interval))


if __name__ == "__main__":
    main()
