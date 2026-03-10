"""WestGame AI 全自动化团战系统 — 入口

用法:
  python src/main.py get_player_pos <uid>          连接test服务器
  python src/main.py --mock get_player_pos <uid>   连接本地mock服务器
"""

import asyncio
import os
import sys

# 确保项目根目录在 sys.path 中，支持 python src/main.py 和 python -m src.main 两种方式
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


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


COMMANDS = {
    "get_player_pos": (cmd_get_player_pos, "<uid>", "查询玩家坐标"),
}


def main():
    args = sys.argv[1:]

    # 解析 --mock 参数
    env = None
    if "--mock" in args:
        env = "mock"
        args.remove("--mock")

    if len(args) < 1 or args[0] not in COMMANDS:
        print("用法:")
        for name, (_, a, desc) in COMMANDS.items():
            print(f"  python src/main.py [--mock] {name} {a}  — {desc}")
        sys.exit(1)

    cmd_name = args[0]
    func, _, _ = COMMANDS[cmd_name]
    asyncio.run(func(*args[1:], env=env))


if __name__ == "__main__":
    main()
