# 如何切换游戏

只需修改 `config.py` 中的 `ACTIVE_GAME`，其他配置自动生效。

## 步骤

打开 `config.py`，找到：

```python
ACTIVE_GAME = "frozenisland"
```

改为目标游戏 ID：

```python
ACTIVE_GAME = "westgame2"
```

`GAME_PACKAGE` 会自动从 `GAME_PACKAGES` 查表得到，无需手动改。

## 当前支持的游戏

| ACTIVE_GAME | GAME_PACKAGE | 游戏名称 |
|---|---|---|
| `frozenisland` | `leyi.frozenislandpro` | 冰封大陆 Pro |
| `westgame2` | `leyi.cowboyclash3` | 西部牛仔 3 |

## 添加新游戏

1. 在 `config.py` 的 `GAME_PACKAGES` 字典中添加一行映射
2. 在 `games/<新游戏ID>/` 下创建 `game.json`、`templates/` 等资源
3. 将 `ACTIVE_GAME` 改为新游戏 ID

## 自动关联的资源

切换 `ACTIVE_GAME` 后，以下路径自动跟随变化：

- 模板目录：`games/<ACTIVE_GAME>/templates/`
- 游戏配置：`games/<ACTIVE_GAME>/game.json`
- 游戏状态：`games/<ACTIVE_GAME>/game_state.json`
- 导航路径：`games/<ACTIVE_GAME>/navigation_paths.json`
- 任务队列：`games/<ACTIVE_GAME>/tasks.json`
- Android 包名：由 `GAME_PACKAGES[ACTIVE_GAME]` 决定
