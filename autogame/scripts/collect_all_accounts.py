"""所有账号并发采集 AVA 战场 coal cart (type=10300)

用法:
  python scripts/collect_all_accounts.py [--ava <lvl_id>] [--interval <秒>]

流程:
  1. 从 accounts.yaml 加载所有账号
  2. 自动检测 AVA lvl_id（用第一个账号探测）
  3. 所有账号并发采集：每人找最近且未被其他人认领的 cart
  4. 轮询等待 → 采完继续下一个，直到地图无 cart
"""

import asyncio
import argparse
import json
import math
import sys
import os
import time

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.executor.game_api import GameAPIClient
from src.utils.coords import decode_pos


def parse_resp(resp: dict, uid: int) -> tuple:
    """解析 lvl_battle_login_get 响应 → (player_pos, carts, busy_collect)"""
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

                elif "svr_lvl_user_objs" in name:
                    for obj in parsed.get("objs", []):
                        march = obj.get("marchBasic", {})
                        troop_info = obj.get("troopInfo", {})
                        queue_id = int(troop_info.get("queueId", march.get("queueId", 0)))
                        march_type = int(march.get("marchType", 0))
                        if queue_id == 6003 or march_type == 27:
                            busy_collect = True

    return player_pos, carts, busy_collect


# 全局已认领 cart 集合，避免多账号抢同一个
claimed_carts: set[str] = set()
claimed_lock = asyncio.Lock()


async def worker(uid: int, name: str, lvl_id: int, client: GameAPIClient,
                 poll_interval: int, stats: dict):
    """单账号采集 worker：循环采集直到无可用 cart"""
    collected = 0

    while True:
        # 查询地图
        resp = await client.lvl_battle_login_get(uid, lvl_id)
        code = resp.get("res_header", {}).get("ret_code", -1)
        if code != 0:
            print(f"  [{name}] 查询地图失败 ret_code={code}")
            break

        player_pos, carts, busy_collect = parse_resp(resp, uid)

        if not player_pos:
            print(f"  [{name}] 未找到城市位置，跳过")
            break

        # 采集队列忙，等待
        if busy_collect:
            print(f"  [{name}] 采集中，等待 {poll_interval}s...")
            await asyncio.sleep(poll_interval)
            continue

        px, py = player_pos

        # 按距离排序，跳过已被认领的 cart
        carts_sorted = sorted(carts, key=lambda c: math.hypot(c[1] - px, c[2] - py))

        target = None
        async with claimed_lock:
            for cart_id, cx, cy in carts_sorted:
                if cart_id not in claimed_carts:
                    claimed_carts.add(cart_id)
                    target = (cart_id, cx, cy)
                    break

        if not target:
            # 没有可认领的 cart 了
            print(f"  [{name}] 无可用 cart，结束 (已采集 {collected} 个)")
            break

        cart_id, cx, cy = target
        dist = math.hypot(cx - px, cy - py)
        print(f"  [{name}] → cart {cart_id} ({cx},{cy}) 距离={dist:.1f}")

        # 派遣采集
        collect_resp = await client.lvl_collect_cart(uid, lvl_id, cart_id)
        ret = collect_resp.get("res_header", {}).get("ret_code", -1)

        if ret != 0:
            print(f"  [{name}] 派遣失败 ret_code={ret}，释放 cart")
            async with claimed_lock:
                claimed_carts.discard(cart_id)
            await asyncio.sleep(3)
            continue

        collected += 1
        print(f"  [{name}] 派遣成功 #{collected}")

        # 轮询等待采集完成
        wait_start = time.time()
        while True:
            await asyncio.sleep(poll_interval)
            check_resp = await client.lvl_battle_login_get(uid, lvl_id)
            check_code = check_resp.get("res_header", {}).get("ret_code", -1)
            if check_code != 0:
                break
            _, _, still_busy = parse_resp(check_resp, uid)
            if not still_busy:
                elapsed = time.time() - wait_start
                print(f"  [{name}] 采集完成 ({elapsed:.0f}s)")
                break

    stats[uid] = collected


async def main_loop(lvl_id: int, poll_interval: int):
    # 加载账号
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "accounts.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    accounts = [(a["uid"], a["name"]) for a in cfg["accounts"]]
    print(f"[*] 加载 {len(accounts)} 个账号")

    client = GameAPIClient()
    try:
        # 自动检测 lvl_id
        if not lvl_id:
            probe_uid = accounts[0][0]
            print(f"[*] 用 {probe_uid} 检测 AVA 战场...")
            lvl_id = await client.get_player_lvl_info(probe_uid)
            if not lvl_id:
                print("[!] 账号不在 AVA 战场中，请用 --ava <lvl_id> 指定")
                return
        print(f"[*] AVA lvl_id={lvl_id}")

        # 先查一次地图看有多少 cart
        resp = await client.lvl_battle_login_get(accounts[0][0], lvl_id)
        _, carts, _ = parse_resp(resp, accounts[0][0])
        print(f"[*] 地图上共 {len(carts)} 个 coal cart，{len(accounts)} 个账号并发采集")
        print(f"{'='*60}")

        # 启动所有 worker
        stats: dict[int, int] = {}
        tasks = [
            worker(uid, name, lvl_id, client, poll_interval, stats)
            for uid, name in accounts
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        # 汇总
        total = sum(stats.values())
        print(f"\n{'='*60}")
        print(f"[完成] 共采集 {total} 个 coal cart")
        for uid, name in accounts:
            cnt = stats.get(uid, 0)
            if cnt > 0:
                print(f"  {name} (uid={uid}): {cnt} 个")

    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(description="所有账号并发采集 AVA coal cart")
    parser.add_argument("--ava", type=int, default=None, help="AVA lvl_id（不指定则自动检测）")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数（默认10）")
    args = parser.parse_args()

    asyncio.run(main_loop(args.ava, args.interval))


if __name__ == "__main__":
    main()
