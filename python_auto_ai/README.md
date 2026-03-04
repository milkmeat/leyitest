# 游戏HTTP请求驱动测试框架

一个基于 Python 的游戏测试自动化框架，支持通过 HTTP 请求驱动游戏操作，适用于游戏服务端接口的自动化测试。

## 项目结构

```
python_auto_ai/
├── config/                  # 配置文件目录
│   ├── env_config.yaml     # 环境配置（dev/test/prod）
│   └── cmd_config.yaml     # 命令配置
├── core/                    # 核心模块
│   ├── config_loader.py    # 配置加载器
│   ├── game_client.py      # 游戏HTTP客户端
│   └── request_builder.py  # 请求URL构建器
├── actions/                 # 操作模块
│   └── game_actions.py     # 游戏操作聚合类（链式调用）
├── main.py                  # 使用示例
├── FunctionTest.py          # 功能测试
└── requirements.txt         # 依赖文件
```

## 安装

```bash
pip install -r requirements.txt
```

## 依赖

- Python 3.7+
- requests >= 2.28.0
- pyyaml >= 6.0

## 快速开始

### 方式一：使用 GameClient 直接发送

```python
from core.game_client import GameClient

# 定义请求头
header = {
    "did": "self-system",
    "sid": 1,
    "uid": 20010366,
    "aid": 0,
    "ksid": 1,
    "ava_id": 0,
    "castle_lv": 25,
    "battle_type": 0,
    "battle_id": 0,
    "chat_scene": ",kingdom_1",
    "invoker_name": "test_debug"
}

# 初始化客户端（使用test环境）
client = GameClient(env="test")

# 发送命令
response = client.send_cmd("add_gem", header, {"gem_num": 116666})

# 检查响应
if response.is_success:
    print("操作成功")
else:
    print(f"操作失败: {response.err_msg}")
```

### 方式二：使用 GameActions 链式调用

```python
from actions.game_actions import GameActions

# 初始化
actions = GameActions(env="test")

# 链式添加多个操作
actions.add_gem(header, 116666) \
       .add_soldiers(header, soldier_id=204, soldier_num=100000) \
       .add_resource(header)

# 预览待执行的URL
for url in actions.preview():
    print(url)

# 执行所有操作
responses = actions.execute()
```

### 方式三：立即执行单个操作

```python
from actions.game_actions import GameActions

actions = GameActions(env="test")

# 立即执行移城（不走链式调用）
response = actions.move_city_now(header, x=192, y=189)
```

## 支持的操作

| 命令 | 方法 | 说明 |
|------|------|------|
| add_gem | `add_gem(header, gem_num)` | 添加宝石 |
| move_city | `move_city(header, x, y)` | 移城到指定坐标 |
| add_soldiers | `add_soldiers(header, soldier_id, soldier_num)` | 添加士兵 |
| attack_city | `attack_city(header, target_uid, target_x, target_y, ...)` | 攻打玩家主城 |
| add_resource | `add_resource(header, op_type)` | 添加资源 |
| scout_player | `scout_player(header, target_uid, target_x, target_y)` | 侦查玩家 |
| custom_cmd | `custom_cmd(cmd_name, header, param)` | 自定义命令 |

## 环境切换

```python
# 初始化时指定环境
client = GameClient(env="dev")

# 运行时切换环境
client.switch_env("prod")

# 使用GameActions切换环境
actions = GameActions(env="test")
actions.switch_env("dev")
```

## 配置文件

### env_config.yaml

配置不同环境的服务器地址：

```yaml
current_env: test

environments:
  dev:
    name: 开发环境
    url: http://dev-server.example.com/api
  test:
    name: 测试环境
    url: http://test-server.example.com/api
  prod:
    name: 生产环境
    url: http://prod-server.example.com/api
```

### cmd_config.yaml

配置可用的命令及默认参数：

```yaml
commands:
  add_gem:
    cmd: add_gem
    default_param:
      gem_num: 116666
  move_city:
    cmd: move_city
    default_param:
      use_gem: 1
      item_id: 1
```

## GameResponse 响应对象

`GameClient.send_cmd()` 返回 `GameResponse` 对象，提供以下属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `is_success` | bool | 请求是否成功（ret_code == 0） |
| `ret_code` | int | 业务返回码 |
| `err_msg` | str | 错误信息 |
| `status_code` | int | HTTP状态码 |
| `json_data` | dict | 完整JSON响应 |
| `res_header` | dict | 响应头 |
| `res_data` | list | 响应数据 |

## 运行示例

```bash
python main.py
```

## 许可证

MIT License
