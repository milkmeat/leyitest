# Prompt Record

- Date: 2026-03-10 00:00
- Branch: master
- Commit: refactor: extract coordinate encode/decode to shared utils module

---

### 1

计算坐标的逻辑是不是有很多重复代码，重构成函数复用  pos = x * 100_000_000 + y * 100

> **Insight**
> `mock_server/` 和 `src/` 是平级目录，`python mock_server/app.py` 运行时，Python 只把 `mock_server/` 加到 `sys.path`，找不到 `src` 包。解决方案：在 `mock_server/app.py` 中加入和 `main.py` 一样的项目根目录路径处理，或者把 `coords.py` 放在更中立的位置。最简单的方式是在 app.py 中手动添加项目根目录到 sys.path。

> **Insight**
> `坐标函数放在 game_api.py 中有个问题`：这个文件依赖 `aiohttp`，而 `client.py` 和 `mock_server/app.py` 是同步代码，不应依赖异步库。更好的做法是把坐标工具函数抽到一个轻量的公共模块（如 `src/utils/coords.py`），让三处都 import 它。

**Files:** `src/utils/__init__.py`, `src/utils/coords.py`, `src/executor/game_api.py`, `src/client.py`, `mock_server/app.py`
