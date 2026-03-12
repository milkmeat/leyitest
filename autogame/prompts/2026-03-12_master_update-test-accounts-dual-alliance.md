# Prompt Record

- Date: 2026-03-12 20:30
- Branch: master
- Commit: update test accounts to new 40-player dual-alliance setup

---

### 1. Query alliance IDs for 40 test players

在test环境上看一下这批玩家的联盟aid,是不是分属两个联盟
20010643,20010644,20010645,20010646,20010647,20010648,20010649,20010650,20010651,20010652,20010653,20010654,20010655,20010656,20010657,20010658,20010659,20010660,20010661,20010662,
20010668,20010669,20010670,20010671,20010672,20010673,20010674,20010675,20010676,20010677,20010678,20010679,20010680,20010681,20010682,20010683,20010684,20010685,20010686,20010687

> **Insight**
> - 查询用的是 `get_player_info` 接口，只请求了 `svr_lord_info_new` 和 `svr_player` 两个模块，避免拉取不必要的士兵/英雄数据，减少传输量
> - 联盟ID (`aid`) 来自 `svr_lord_info_new` 模块中的 `lord_info.aid` 字段，联盟名则来自 `svr_player` 模块的 `al_name`

### 2. Save accounts to config files

把这批账号的信息保存到配置文件，以后就用这些来测试

> **Insight**
> - 把 `enemies` 单独作为一个 key 存放，而非混入 `accounts`，这样代码加载时可以清晰区分"我方控制"和"对手目标"，数据同步和 AI 决策模块各取所需
> - `alliances` 元信息集中存放 aid，避免在代码中硬编码联盟 ID，后续切换测试环境或联盟只改配置即可

**Files:** `config/accounts.yaml`, `config/squads.yaml`

### 3. Move old accounts to reserves

> **Q:** accounts.yaml 写入时用户中断，要求旧账号全部放到 reserves 作为备用

accounts.yaml里面的旧账号全都放到reserves,作为备用

**Files:** `config/accounts.yaml`

### 4. Update schemas to match new config structure

> **Q:** models/的py文件要跟着改吗

改一下

> **Insight**
> - Pydantic v2 默认行为是忽略未声明字段（不报错也不存储），所以现在程序能正常启动，只是拿不到 `enemies`/`alliances` 数据
> - `models/` 目录下的是运行时数据模型（从服务器 API 同步填充），而 `config/schemas.py` 是配置文件 schema（从 YAML 加载），两者职责不同，改配置结构只需动 schema
> - `all_uids()` 故意不包含 enemies，因为它在 `data_sync.py:222` 用于敌我判断："不在 all_uids 里的玩家 = 非我方"。如果把 enemies 也加进去，地图扫描时就会跳过已知对手，导致感知层看不到敌人
> - UID 唯一性校验现在覆盖三个列表（accounts + enemies + reserves），防止同一个号意外出现在多个角色中

**Files:** `src/config/schemas.py`
