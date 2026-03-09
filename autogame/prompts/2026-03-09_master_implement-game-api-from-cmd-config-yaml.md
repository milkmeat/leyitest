# Prompt Record

- Date: 2026-03-09 00:00
- Branch: master
- Commit: implement game_api.py with YAML-driven command definitions, move cmd_config.yaml to src/config/

---

### 1. Implement game_api.py based on game_actions.py, reading commands from cmd_config.yaml

docs/game_actions.py 是历史项目中的一个api客户端。其中每个函数对应一个命令字。
请在模仿game_actions接口的情况下，完成src/executor/game_api.py
需要改进的是：game_actions本应从cmd_config.yaml里面读取所有的命令字和参数信息的，它却把这些信息写死了。
在game_api.py里面，从cmd_config.yaml读取信息而不是硬编码
（把cmd_config.yaml移动到 src/config/下面）

**Files:** `src/executor/game_api.py`, `src/config/cmd_config.yaml`
