# Prompt Record

- Date: 2026-03-18 12:00
- Branch: master
- Commit: feat: add uid_helper CLI commands and multi-alliance squads.yaml support

---

### 1. Implement uid_helper plan with multi-alliance support

Implement the following plan:

# uid_helper — 测试环境账号准备工具 + 多联盟支持

## Context

需要为 L2+L1 联合实战测试准备账号。当前 squads.yaml 只支持单联盟，用户需要：
1. CLI 工具批量准备账号（复制、建联盟、加入联盟、改名）
2. squads.yaml 支持多联盟，两个 L2 进程可分别管理不同联盟（AI vs AI 测试）

来源：`todo/uid_helper.md`

## 工作项分解

### 工作项 1: squads.yaml 多联盟结构 + Schema 更新

**`config/squads.yaml`** — 从扁平列表改为按联盟分组：

```yaml
alliances:
  ours:
    aid: 20000118
    name: "TestSquad2026"
    squads:
      - squad_id: 1
        name: "Alpha"
        leader_uid: 20010643
        member_uids: [20010643, 20010644, 20010645, 20010646, 20010647]
      # ... (保留现有 4 个小队)
  enemy:
    aid: 20000119
    name: "PhoenixRise2026"
    squads: []  # uid_helper join 后自动填充
```

**`src/config/schemas.py`** — 新增模型，保持向后兼容：

```python
class AllianceSquadGroup(BaseModel):
    """单联盟的小队配置"""
    aid: int
    name: str = ""
    squads: list[SquadEntry] = Field(default_factory=list)

class SquadsConfig(BaseModel):
    alliances: dict[str, AllianceSquadGroup]
    _active_key: str = "ours"  # 运行时选择

    @property
    def squads(self) -> list[SquadEntry]:
        """向后兼容：返回当前活跃联盟的小队列表"""
        return self.alliances[self._active_key].squads

    @property
    def active_alliance(self) -> AllianceSquadGroup:
        return self.alliances[self._active_key]

    def set_active(self, key: str):
        if key not in self.alliances:
            raise ValueError(f"未知联盟: {key}")
        self._active_key = key
```

**关键：** `.squads` 属性保持向后兼容，以下 8 处代码无需改动：
- `l2_commander.py:83`, `l1_leader.py:133`, `data_sync.py:78`, `l2_view.py:269`
- `main.py:563,569,640,646`

**`AppConfig` 校验器更新：** 改为检查所有联盟的 squad UID（不仅 ours）：
- `check_squad_uids_in_accounts` → 遍历所有 `alliances` 中的 squads
- 新增 `all_known_uids()` 方法合并 accounts + enemies + reserves

### 工作项 2: 配置加载器支持联盟选择

**`src/config/loader.py`**：
- `load_squads()` 适配新 YAML 结构
- `load_all()` 新增可选 `alliance: str = "ours"` 参数
- 加载后调用 `squads_config.set_active(alliance)`

### 工作项 3: CLI uid_helper 命令

在 `src/main.py` 新增 5 个命令（复用 `GameAPIClient.send_cmd()`）：

#### 3a. `uid_copy <src_uid> <tar_uid>`
- 调用 `send_cmd("copy_player", src_uid, src_uid=src_uid, src_sid=1, tar_uid=tar_uid, tar_sid=1)`
- 验证：`send_cmd("get_player_info", tar_uid)` 读取目标，比对兵力

#### 3b. `uid_create_al <name> <nick>`
- 需要一个 uid 作为创建者（用第一个 accounts uid）
- 调用 `send_cmd("create_alliance", uid, name=name, nick=nick)`
- 打印返回的 aid

#### 3c. `uid_join_al <aid> <uid1> [uid2...]`
- 对每个 uid：
  1. `send_cmd("join_alliance", uid, target_aid=aid)` — 加入联盟
  2. 根据 squads.yaml 中该 uid 所属小队，生成昵称 `{SquadName}{seq:03d}_{uid}`
  3. `send_cmd("change_name", uid, name=nickname)` — 改名
- 全部完成后：`send_cmd("get_al_members", uid, header_overrides={"aid": aid})` 验证

#### 3d. `uid_members <aid>`
- 调用 `send_cmd("get_al_members", any_uid, header_overrides={"aid": aid})`
- 打印成员列表

#### 3e. `uid_setup <alliance_key> <src_uid> <uid_list...>`
- 一站式：对每个 tar_uid 执行 copy_player + join_alliance + change_name
- 自动按 squads.yaml 中的配置分配小队和昵称
- 完成后打印验证摘要

### 工作项 4: Mock Server 验证

现有 mock handlers（`app.py`）已覆盖：
- `handle_op_copy_player` ✓
- `handle_player_name_change` ✓
- `handle_get_al_members` ✓

需新增/确认：
- `handle_al_create` — 返回 `{code: 0, data: {aid: 12345}}`
- `handle_al_request_join` — 返回 `{code: 0}`

所有新命令先在 `--mock` 环境测试通过。

## 文件变更清单

| 文件 | 操作 | 工作项 |
|------|------|--------|
| `src/config/schemas.py` | **修改** | 1: 新增 AllianceSquadGroup，重构 SquadsConfig，更新 AppConfig 校验 |
| `config/squads.yaml` | **重写** | 1: 按联盟分组结构 |
| `src/config/loader.py` | **修改** | 2: 适配新结构 + alliance 参数 |
| `src/main.py` | **修改** | 3: 新增 5 个 uid_helper CLI 命令 |
| `mock_server/app.py` | **修改** | 4: 补齐 al_create/al_request_join handlers |
| `todo/uid_helper.md` | **更新** | 进度记录 |
| `tests/test_l2_view.py` | **修改** | 1: fixture 适配新 SquadsConfig 结构 |
| `tests/test_l2_commander.py` | **修改** | 1: fixture 适配新 SquadsConfig 结构 |

## 实施顺序

1. schemas.py + squads.yaml 重构 → `pytest tests/` 确保回归通过
2. loader.py 适配 → 手动 `python src/main.py sync` 验证加载正常
3. mock_server handlers 补齐 → `--mock` 测试
4. CLI 命令逐个实现 → `--mock` 测试每个命令
5. 更新 todo/uid_helper.md 进度

## 验证方式

1. `pytest tests/ -v` — 回归测试全通过（schemas 变更不破坏现有功能）
2. `python src/main.py --mock uid_copy 20010643 20010700` — mock 环境复制账号
3. `python src/main.py --mock uid_create_al TestAI TSTA` — mock 创建联盟
4. `python src/main.py --mock uid_join_al 12345 20010643 20010644` — mock 加入+改名
5. `python src/main.py --mock uid_members 12345` — mock 查看成员

> **Insight**
> **SquadsConfig 重构的核心设计**：
> 1. 使用 `PrivateAttr` 而非普通 `_active_key` 来存储运行时状态，这是 Pydantic v2 中私有属性的正确方式
> 2. `.squads` 属性保持向后兼容，现有 8 处引用代码零改动
> 3. `AppConfig` 校验器需遍历所有联盟的 squad UID，而非仅活跃联盟
>
> **uid_helper 命令设计思路**：
> 1. 每个命令复用已有的 `GameAPIClient.send_cmd()` + `cmd_config.yaml` 中的命令字映射，零新增底层代码
> 2. `uid_setup` 是一站式命令，内部串联 copy + join + rename，适合批量准备账号
> 3. 昵称格式 `{SquadName}{seq:03d}_{uid}` 便于在游戏中快速识别小队归属
>
> **实现总结 — 关键设计决策**：
> 1. Pydantic `PrivateAttr` — `_active_key` 用 `PrivateAttr` 而非普通字段，使其不参与序列化/校验
> 2. 向后兼容策略 — `SquadsConfig.squads` 属性代理到活跃联盟的 squads 列表，8 处引用代码完全无需改动
> 3. 旧格式自动升级 — `load_squads()` 检测到旧的 `squads:` 扁平格式时自动包装为单联盟 "ours"

**Files:** `src/config/schemas.py`, `config/squads.yaml`, `src/config/loader.py`, `src/main.py`, `tests/test_l2_view.py`, `tests/test_l2_commander.py`, `todo/uid_helper.md`
