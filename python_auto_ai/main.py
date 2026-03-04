"""
游戏HTTP请求驱动测试框架使用示例
"""

from core.game_client import GameClient
from actions.game_actions import GameActions


def main():
    print("=" * 60)
    print("方式1: 使用GameClient直接发送")
    print("=" * 60)

    # 初始化客户端（使用test环境）
    client = GameClient(env="test")
    print(f"当前环境: {client.get_current_env_info()}")

    # 使用 build_header 构建请求头（sid, uid, aid 作为参数传入）
    header = client.build_header(uid=20010366, sid=1, aid=0)
    print(f"构建的header: {header}")

    # 构建URL预览（不发送请求）
    # url = client.build_url("add_gem", header, {"gem_num": 116666})
    # print(f"\n构建的URL预览:\n{url}")

    # 实际发送请求（取消注释以发送）
    # 测试移城命令，坐标 (192, 189)，tar_pos = 192 * 100000000 + 189 * 100 = 19200018900
    tar_pos = 192 * 100000000 + 189 * 100
    response = client.send_cmd("move_city", header, {"use_gem": 1, "item_id": 1, "tar_pos": tar_pos})
    print(f"响应内容: {response.text}")

    print("\n" + "=" * 60)
    # print("方式2: 使用GameActions聚合操作（链式调用）")
    # print("=" * 60)

    # 初始化GameActions
    # actions = GameActions(env="test")

    # 使用 build_header 构建请求头
    # header = actions.build_header(uid=20010366, sid=1, aid=0)

    # 链式添加操作
    # actions.add_gem(header, 116666).add_gold(header, 999999)

    # print(f"待执行操作数: {actions.pending_count}")

    # 预览所有URL
    # print("\n待执行的URL预览:")
    # for i, url in enumerate(actions.preview(), 1):
    #     print(f"\n[{i}] {url}")

    # 实际执行操作（取消注释以发送）
    # responses = actions.execute()
    # for i, resp in enumerate(responses, 1):
    #     print(f"[{i}] 状态: {resp.status_code}, 响应: {resp.text}")

    # print("\n" + "=" * 60)
    # print("方式3: 环境切换")
    # print("=" * 60)

    # 清空之前的操作
    # actions.clear()

    # 切换到开发环境
    # actions.switch_env("dev")

    # 添加新操作
    # actions.add_gem(header, 50000)

    # print("\n切换环境后的URL预览:")
    # for url in actions.preview():
    #     print(url)

    # 清空待执行操作
    # actions.clear()

    # print("\n" + "=" * 60)
    # print("方式4: 自定义命令")
    # print("=" * 60)

    # 使用自定义命令
    # actions.custom_cmd("add_gem", header, {"gem_num": 88888})
    # print(f"自定义命令URL: {actions.preview()[0]}")


if __name__ == "__main__":
    main()
