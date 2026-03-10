"""WestGame AI 全自动化团战系统 — 入口

用法:
  python src/main.py get_player_pos <uid>   查询玩家坐标
"""

import os
import sys

# 确保项目根目录在 sys.path 中，支持 python src/main.py 和 python -m src.main 两种方式
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def cmd_get_player_pos(uid_str: str):
    from src.client import get_player_pos

    uid = int(uid_str)
    pos = get_player_pos(uid)
    if pos:
        print(f"({pos[0]},{pos[1]})")
    else:
        print(f"无法获取 uid={uid} 的坐标", file=sys.stderr)
        sys.exit(1)


COMMANDS = {
    "get_player_pos": (cmd_get_player_pos, "<uid>", "查询玩家坐标"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("用法:")
        for name, (_, args, desc) in COMMANDS.items():
            print(f"  python src/main.py {name} {args}  — {desc}")
        sys.exit(1)

    cmd_name = sys.argv[1]
    func, _, _ = COMMANDS[cmd_name]
    func(*sys.argv[2:])


if __name__ == "__main__":
    main()
