# Prompt Record

- Date: 2026-03-09 20:30
- Branch: master
- Commit: scaffold project directory structure and CLAUDE.md based on requirements spec

---

### 1

根据需求说明书的内容，为本项目创建适当的代码目录及claude.md (使用python).  和上级与其他平级目录没关系，关注本目录就好

> **Insight**
> - 该项目采用**递归分层指挥体系**：L2（战略）→ L1×10（战术，并行）→ L0（执行，代码层），管理100账号×3部队=300个行动单元
> - 核心循环60秒一轮：Sync → L2 Strategy → L1 Tactics(并行) → Action → Sleep
> - 技术栈：Python + asyncio + requests/aiohttp，LLM 做决策，代码做执行和校验
>
> - **目录按架构层级组织**：`src/` 下的子目录直接映射需求文档中的四层架构——`ai/`(L2+L1决策)、`executor/`(L0执行)、`perception/`(数据感知)、`controller/`(主循环+CLI)、`models/`(数据模型)。这种"架构即目录"的方式让新开发者能快速定位代码
> - **Mock Server 独立于主系统**：`mock_server/` 与 `src/` 平级而非嵌套在内，因为它模拟的是外部依赖(游戏服务器)，未来接入真实服务器时只需切换 `game_api.py` 的 base_url，不影响主系统代码
> - **CLAUDE.md 作为 AI 协作的上下文锚点**：包含了架构概览、命令字映射表、关键游戏机制摘要和编码规范，确保后续用 Claude Code 开发时，AI 能快速理解项目全貌而无需每次重读 55KB 的完整需求文档

**Files:** `CLAUDE.md`, `requirements.txt`, `.gitignore`, `src/main.py`, `src/__init__.py`, `src/config/loader.py`, `src/config/schemas.py`, `src/models/account.py`, `src/models/building.py`, `src/models/enemy.py`, `src/models/rally.py`, `src/models/score.py`, `src/controller/loop.py`, `src/controller/admin_cli.py`, `src/ai/l2_commander.py`, `src/ai/l1_leader.py`, `src/ai/memory.py`, `src/ai/prompts/l2_system.txt`, `src/ai/prompts/l1_system.txt`, `src/executor/l0_executor.py`, `src/executor/game_api.py`, `src/perception/data_sync.py`, `src/perception/l1_view.py`, `src/perception/l2_view.py`, `mock_server/app.py`, `mock_server/world_state.py`, `mock_server/simulation.py`, `mock_server/battle.py`, `mock_server/enemy_ai.py`
