# Prompt Record

- Date: 2026-03-13 10:35
- Branch: master
- Commit: complete rally test on test server: add rally_dismiss, fix grep encoding, reduce soldiers to 500

---

### 1. Continue todo remaining items

rally发起和响应协议已经调试通过了，现在继续完成todo里面的剩余部分

**Files:** `todo/test_l0_rally_attack.md`

### 2. Provide recall_reinforce and rally_dismiss protocol

更新一下协议，recall_reinforce只是撤回本人的增援军队，rally_dismiss是解散整个rally

```
03-13 10:02:38.620 W/Unity   ( 4623): [MdNetParam ToUrl]:recall_reinforce:1127:230.9424
03-13 10:02:38.620 W/Unity   ( 4623): {"param":{"unique_id":"101_1773366750527673_1"}}

03-13 10:00:45.085 W/Unity   ( 4623): [MdNetParam ToUrl]:rally_dismiss:1097:117.4064
03-13 10:00:45.085 W/Unity   ( 4623): {"param":{"unique_id":"107_1773366750527668_1"}}
```

> **Insight**
> 1. `rally_dismiss` 用 `107_xxx_1`（rally 对象 ID），由队长操作解散整个集结
> 2. `recall_reinforce` 用 `101_xxx_1`（部队对象 ID），由队员操作撤回自己的增援部队
> 3. 之前测试中 `recall_reinforce` 传 `107_xxx_1` 返回 30104 正是因为类型错误

**Files:** `src/config/cmd_config.yaml`, `src/executor/game_api.py`, `src/main.py`

### 3. Cancel rallies and reduce to 500 soldiers

所有刚才创建的集结都过期了。继续测试todo

### 4. One change at a time, 500 soldiers should fix 30001

先别改rally坐标，每次只测试一个变更。刚才返回30001很有可能是集结队列士兵数满了。改成500应该能通过。
现在取消集结再重新测试

**Files:** `test_rally.sh`

### 5. Test result: ALL TESTS PASSED

> **Insight**
> 1. 完整 rally 流程 end-to-end 验证通过：移城 → 侦察 → 发起集结 → 4人加入 → 等待5分钟 → 战斗结算 → 士兵减少
> 2. 战斗结算数据：A方每人损失225兵(500中损失45%)，B方损失125兵。5v1集结攻击中攻方每人损失相同，符合集结机制
> 3. 之前30001的原因确认：5000士兵超出集结队列限制，改为500后全部通过

**Files:** `todo/test_l0_rally_attack.md`
