## 目标
在cli上面添加uid_helper功能，使用系统管理指令来进行测试环境中的账号准备工作

## 任务
- cli 提供以下命令
- 使用copy_player将test环境指定的源账号数据复制到指定uid(可以是新增也可以是已有的，会被覆盖)。完成之后在test环境读取对应目标uid验证成功(兵力与源账号一致)
- 在test环境创建联盟
- squads.yaml 修改一下，允许管理多个联盟的账号和小队。L2启动时管理默认联盟，也可以管理参数所指定的联盟（这样我可以开两个L2进程，执行ai之间的团战测试）
- 将指定账号(uid)加入指定联盟(aid)，完成后get_al_members验证成功。同步更新squads.yaml中的联盟信息。该账号修改昵称(change_name)为 <Alpha><001>_<uid>


## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 所有新完成的命令字，都要在mock server上测试通过

## 验收标准
我手动执行uid helper指令并在test环境上验证

## 进度

### 工作项 1: squads.yaml 多联盟结构 + Schema 更新 ✅
- `config/squads.yaml` 从扁平 `squads:` 改为 `alliances.ours/enemy` 分组
- `schemas.py` 新增 `AllianceSquadGroup`，重构 `SquadsConfig` 使用 `alliances` dict + `PrivateAttr`
- `.squads` 属性向后兼容，现有引用代码零改动
- `AppConfig` 校验器遍历所有联盟，`all_known_uids()` 合并 accounts+enemies
- 30 个测试全部通过

### 工作项 2: 配置加载器支持联盟选择 ✅
- `loader.py` 的 `load_squads()` 兼容新旧两种 YAML 格式
- `load_all()` 新增 `alliance` 参数，加载后调用 `set_active()`

### 工作项 3: CLI uid_helper 命令 ✅
- `uid_copy <src_uid> <tar_uid>` — 复制+验证兵力
- `uid_create_al <name> <nick>` — 创建联盟
- `uid_join_al <aid> <uid1> [uid2...]` — 加入+改名+验证成员
- `uid_members <aid>` — 查看联盟成员
- `uid_setup <alliance_key> <src_uid> <tar_uid...>` — 一站式 copy+join+rename

### 工作项 4: Mock Server 验证 ✅
- `handle_al_create` 和 `handle_al_request_join` 已在 mock_server/app.py 中实现
- `handle_op_copy_player`, `handle_player_name_change`, `handle_get_self_al_member` 已有
- 配置加载验证通过，测试通过

## CLI 用法

```bash
# 复制账号
python src/main.py [--mock] uid_copy <src_uid> <tar_uid>

# 创建联盟
python src/main.py [--mock] uid_create_al <name> <nick>

# 加入联盟 + 自动改名
python src/main.py [--mock] uid_join_al <aid> <uid1> [uid2...]

# 查看联盟成员
python src/main.py [--mock] uid_members <aid>

# 一站式准备 (copy + join + rename)
python src/main.py [--mock] uid_setup <alliance_key> <src_uid> <tar_uid1> [tar_uid2...]
```
