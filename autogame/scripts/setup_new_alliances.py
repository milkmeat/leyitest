"""一次性脚本：把新一批测试账号并入两个现成联盟并组队

背景: 旧测试账号 (20010643-20010662 / 20010668-20010687) 已失效，
更换为新一批 40 个连号账号。这批账号已分布在若干现成联盟中，
不再新建联盟，直接复用两个盟主账号所在的现成联盟:

  - 我方 ours : 盟主 20013796 所在联盟 aid=20000214，成员 20013796-20013815
  - 敌方 enemy: 盟主 20013816 所在联盟 aid=20000215，成员 20013816-20013835

流程（对测试服务器的写操作）:
  1. 盟主已在盟内，仅改名
  2. 其余成员逐个 join_alliance 到对应固定 aid，再改名
  3. 打印两个联盟真实名字 + 成员数，供回写配置 / 核对

用法:
  python scripts/setup_new_alliances.py            # 真正执行（加入现成联盟）
  python scripts/setup_new_alliances.py --dry-run  # 只打印计划，不发请求
  python scripts/setup_new_alliances.py --check    # 只查每个账号当前 aid
  python scripts/setup_new_alliances.py --members 20000214,20000215  # 查联盟成员
"""

import asyncio
import argparse
import os
import sys

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.executor.game_api import GameAPIClient

# --- 联盟与小队定义：复用现成联盟（aid 固定），每批第一个 uid 即盟主 ---
ALLIANCES = {
    "ours": {
        "aid": 20000214,          # 盟主 20013796 所在的现成联盟
        "squads": [
            ("Alpha",   [20013796, 20013797, 20013798, 20013799, 20013800]),
            ("Bravo",   [20013801, 20013802, 20013803, 20013804, 20013805]),
            ("Charlie", [20013806, 20013807, 20013808, 20013809, 20013810]),
            ("Delta",   [20013811, 20013812, 20013813, 20013814, 20013815]),
        ],
    },
    "enemy": {
        "aid": 20000215,          # 盟主 20013816 所在的现成联盟
        "squads": [
            ("Red-A", [20013816, 20013817, 20013818, 20013819, 20013820]),
            ("Red-B", [20013821, 20013822, 20013823, 20013824, 20013825]),
            ("Red-C", [20013826, 20013827, 20013828, 20013829, 20013830]),
            ("Red-D", [20013831, 20013832, 20013833, 20013834, 20013835]),
        ],
    },
}


def _member_plan(squads):
    """展开小队为 [(uid, nickname), ...]

    昵称规则: {小队名去掉非字母数字}{两位序号}，例如 Alpha01 / RedA03。
    注意: 服务器改名禁止下划线/连字符等特殊字符（错误码 20544），
    因此昵称只用字母数字。
    """
    plan = []
    for squad_name, uids in squads:
        safe = "".join(ch for ch in squad_name if ch.isalnum())  # Red-A -> RedA
        for idx, uid in enumerate(uids):
            plan.append((uid, f"{safe}{idx + 1:02d}"))
    return plan


async def join_existing_alliance(client, key, conf, dry_run):
    """把一批账号并入现成联盟并改名，返回 (aid, al_name, ok_count, fail_count)

    要点:
    - join_alliance 必须把 header.aid 覆盖为 0，否则 default_header 里的旧 aid
      会让服务器误判“已在联盟”而返回 20029。
    - 改名昵称只用字母数字（见 _member_plan）。
    """
    aid = conf["aid"]
    plan = _member_plan(conf["squads"])
    leader_uid, leader_nick = plan[0]

    # 读取联盟真实名字（从盟主玩家信息）
    al_name = ""
    if not dry_run:
        info = await client.get_player_info(leader_uid, modules=["svr_player", "svr_lord_info_new"])
        al_name = info.get("alliance_name", "")

    print(f"\n=== [{key}] 并入现成联盟 aid={aid} name='{al_name}' (盟主 {leader_uid}) ===")
    if dry_run:
        print(f"  [dry-run] 盟主 uid={leader_uid} 已在盟内, 改名 -> {leader_nick}")
        for uid, nickname in plan[1:]:
            print(f"  [dry-run] join(aid={aid}) + rename uid={uid} -> {nickname}")
        return aid, al_name, 0, 0

    ok = fail = 0

    # 1) 盟主：已在盟内，仅改名（header.aid 用其真实联盟）
    resp = await client.send_cmd("change_name", leader_uid, name=leader_nick,
                                 header_overrides={"aid": aid})
    if resp.get("res_header", {}).get("ret_code", -1) == 0:
        print(f"  uid={leader_uid} (盟主) 改名 -> {leader_nick}")
        ok += 1
    else:
        print(f"  [WARN] uid={leader_uid} 盟主改名失败", file=sys.stderr)
        fail += 1

    # 2) 其余成员加入 + 改名
    for uid, nickname in plan[1:]:
        # 加入时 header.aid=0（尚无联盟），避免 20029 误判
        resp = await client.send_cmd("join_alliance", uid, target_aid=aid,
                                     header_overrides={"aid": 0})
        if resp.get("res_header", {}).get("ret_code", -1) != 0:
            print(f"  [FAIL] uid={uid} 加入联盟 {aid} 失败", file=sys.stderr)
            fail += 1
            continue
        # 改名时 header.aid 用目标联盟
        resp = await client.send_cmd("change_name", uid, name=nickname,
                                     header_overrides={"aid": aid})
        if resp.get("res_header", {}).get("ret_code", -1) == 0:
            print(f"  uid={uid} 加入 {aid}, 改名 -> {nickname}")
        else:
            print(f"  uid={uid} 加入 {aid}, 改名失败", file=sys.stderr)
        ok += 1  # 加入成功即计入

    # 3) 验证成员数
    members = await client.get_alliance_members(leader_uid, aid)
    print(f"  联盟 {aid} 当前成员数: {len(members)}")
    return aid, al_name, ok, fail


async def main():
    parser = argparse.ArgumentParser(description="把两批账号并入两个现成联盟并组队")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不发请求")
    parser.add_argument("--check", action="store_true", help="只查询所有账号当前所在联盟 aid，不做任何修改")
    parser.add_argument("--members", default=None,
                        help="只查询指定联盟成员（逗号分隔 aid），用各联盟盟主当 viewer")
    parser.add_argument("--env", default=None, help="环境名（默认取 env_config.current_env）")
    args = parser.parse_args()

    all_uids = [uid for conf in ALLIANCES.values()
                for _, uids in conf["squads"] for uid in uids]
    # aid -> 该联盟首个 uid（盟主），用于查成员时的 viewer
    leader_by_aid = {conf["aid"]: conf["squads"][0][1][0] for conf in ALLIANCES.values()}

    client = GameAPIClient(env=args.env)
    results = {}
    try:
        # --check: 只读，打印每个账号当前所在联盟
        if args.check:
            print("查询所有账号当前所在联盟 aid (0=未入盟, None=查询失败):")
            for uid in all_uids:
                aid = await client.get_aid_by_uid(uid)
                print(f"  uid={uid}  aid={aid}")
            return

        # --members: 只读，打印指定联盟成员列表（viewer 用对应盟主，回退到首个 uid）
        if args.members:
            for aid_str in args.members.split(","):
                aid = int(aid_str.strip())
                viewer = leader_by_aid.get(aid, all_uids[0])
                members = await client.get_alliance_members(viewer, aid)
                print(f"联盟 {aid} 成员数: {len(members)} (viewer={viewer})")
                for m in members:
                    print(f"  uid={m.get('uid')} name={m.get('name','')}")
            return

        # 默认：把两批账号并入各自现成联盟
        for key in ("ours", "enemy"):
            aid, al_name, ok, fail = await join_existing_alliance(
                client, key, ALLIANCES[key], args.dry_run)
            results[key] = (aid, al_name, ok, fail)
    finally:
        await client.close()

    print("\n" + "=" * 56)
    print("完成。请将以下联盟信息回写配置文件:")
    for key in ("ours", "enemy"):
        if key in results:
            aid, al_name, ok, fail = results[key]
            print(f"  {key:6s}: aid={aid}  name='{al_name}'  (ok={ok} fail={fail})")
    print("=" * 56)


if __name__ == "__main__":
    asyncio.run(main())

