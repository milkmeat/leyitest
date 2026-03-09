# 后台接口协议

## 1.0 v0.41

### 1.0.1 军队

#### 训练军队

>  **cmd**

  `troop_train`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                                                |
|:----------|:---------|:----------------------------------------------------|
| troop_id  | int      | 训练的军队id                                        |
| troop_num | int      | 训练的军队数量                                      |
| resource  | object   | 立即完成时需要传, 其它时候可以留空，用户持有的资源数 |
| type      | int      | 0：normal 1：instant                                  |

---
#### 晋升军队

>  **cmd**

`troop_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name        | val_type | desc                                                |
|:----------------|:---------|:----------------------------------------------------|
| troop_id        | int      | 训练的军队id                                        |
| target_troop_id | int      | 晋升到的军队id                                      |
| troop_num       | int      | 训练的军队数量                                      |
| resource        | object   | 立即完成时需要传, 其它时候可以留空，用户持有的资源数 |
| type            | int      | 0：normal 1：instant                                  |

---
#### 采集训练/晋升完的军队

>  **cmd**

`get_train_troop`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| troop_id | int      | 采集的军队id |

---

[comment]: <> "### 1.0.2 建筑"

[comment]: <> "#### 升级建筑"

[comment]: <> ">  **cmd**"

[comment]: <> "`building_upgrade`"

[comment]: <> "> **main_push**:"

[comment]: <> "`player`"

[comment]: <> ">  **param**:"

[comment]: <> "| key_name         | val_type | desc                                                |"

[comment]: <> "|:-----------------|:---------|:----------------------------------------------------|"

[comment]: <> "| pos              | int      | 建筑位置                                            |"

[comment]: <> "| id               | int      | 建筑id                                              |"

[comment]: <> "| resource         | int      | 立即完成时需要传, 其它时候可以留空，用户持有的资源数 |"

[comment]: <> "| type             | int      | 0：nornal 1：instant                                  |"

[comment]: <> "| client_action_id | long     | 客户端预生成的action_id\|                           |"

[comment]: <> "| level            | int      | 目标等级                                            |"

## 1.1 v0.42

### 1.1.1 军队

#### 治疗军队

>  **cmd**

  `troop_heal`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc                                                |
|:---------|:---------|:----------------------------------------------------|
| troop    | obj      | 治疗的军队,kv结构                                   |
| resource | object   | 立即完成时需要传, 其它时候可以留空，用户持有的资源数 |
| type     | int      | 0：normal 1：instant                                  |

---
#### 收取治疗完成的军队

>  **cmd**

`get_heal_done_troop`

> **main_push**:

`player`

>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|

---
### 1.1.2  资源

#### 采集资源

>  **cmd**

`collect_resource`

> **main_push**:

`player`

>  **param**:

| key_name      | val_type | desc                 |
|:--------------|:---------|:---------------------|
| building_id  | int      | 后台建筑id |

---

#### 批量采集资源

>  **cmd**

`batch_collect_resource`

> **main_push**:

`player`

>  **param**:

| key_name      | val_type | desc                 |
|:--------------|:---------|:---------------------|
| building_id_list  | array      | [int]后台建筑id列表 |

---
### 1.1.3  研究

#### 科技升级

>  **cmd**

`research_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name    | val_type | desc                                             |
|:------------|:---------|:-------------------------------------------------|
| research_id | int      | 科技id                                           |
| level       | int      | 目标科技等级                                     |
| resource    | object   | 消耗的资源数, 立即完成时需要传, 其它时候可以留空 |
| type        | int      | 0：normal 1：instant                               |
---

#### 获取研究完成的科技

>  **cmd**

`get_research_done`

> **main_push**:

`player`

>  **param**:

|key_name|val_type|desc|
| research_id | int      | 要领取的研究id |

---
### 1.1.4  建筑

#### 领取主城升级奖励

>  **cmd**

`get_castle_upgrade_reward`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc                           |
|:----------|:---------|:-------------------------------|
| castle_lv | int      | 要领取的主城升级奖励对应的等级 |

---
### 1.1.5  英雄

#### 开宝箱

>  **cmd**

`open_hero_chest`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc                      |
|:-----------|:---------|:--------------------------|
| chest_type | int      | 宝箱类型                  |
| open_type  | int      | 开启类型，0: 免费, 1: 道具 |
| num        | int      | 宝箱类型                  |

---
#### 解锁英雄

>  **cmd**

`hero_unlock`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc             |
|:----------|:---------|:-----------------|
| hero_id   | int      |                  |
| piece_num | int      | 雕像数量用于校验 |

---
#### 升星
>  **cmd**

`hero_star_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| hero_id    | int      |               |
| piece_list | array    | piece_id 列表 |

---
#### 升阶
>  **cmd**

`hero_stage_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| hero_id    | int      |               |
| piece_list | array    | piece_id 列表 |

---
#### 升级技能
>  **cmd**

`hero_skill_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc             |
|:----------|:---------|:-----------------|
| hero_id   | int      |       英雄id      |
| skill_id | int       | 指定的技能id |
| target_lv | int      | 传入客户端的下一级即可 |
---

#### 预设天赋技能升级

>  **cmd**

`hero_talent_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc     |
|:-----------|:---------|:---------|
| hero_id    | int      |          |
| index      | int      | 天赋预设 |
| point_cost | int      | 校验点数 |
| talent_id  | int      | 指定天赋 |

---

#### 重置预设天赋

>  **cmd**

`hero_talent_reset`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc                               |
|:----------|:---------|:-----------------------------------|
| hero_id   | int      |                                    |
| index     | int      | 天赋预设                           |
| cost_type | int      | 消耗类型: 0 道具，1宝石             |
| item_id   | int      | 道具                               |
| gem_cost  | int      | 当消耗宝石时，需要传入，用于校验数据 |

---

#### 使用预设

>  **cmd**

`hero_talent_use`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc                               |
|:----------|:---------|:-----------------------------------|
| hero_id   | int      |                                    |
| index     | int      | 天赋预设                           |
| cost_type | int      | 消耗类型: 0 道具，1宝石             |
| item_id   | int      | 道具                               |
| gem_cost  | int      | 当消耗宝石时，需要传入，用于校验数据 |

---


#### 修改预设名称

>  **cmd**

`hero_talent_name_change`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc     |
|:---------|:---------|:---------|
| hero_id  | int      |          |
| index    | int      | 天赋预设 |
| name     | string   | 预设名称 |

---


#### 通用雕像转化

>  **cmd**

`hero_universal_piece_transform`

> **main_push**:

`player`

>  **param**:

| key_name    | val_type | desc            |
|:------------|:---------|:----------------|
| piece_id    | int      | 通用雕像 id     |
| to_peice_id | int      | 需要转化成得 id |
| num         | int      | 数量            |

---


### 1.1.6  任务

#### 领取主线任务奖励

>  **cmd**

`claim_main_quest`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| claim_id | int      | 任务ID |

---
#### 领取支线任务奖励

>  **cmd**

`claim_side_quest`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| claim_id | int      | 任务ID |

---
#### 领取日常任务奖励

>  **cmd**

`claim_daily_quest`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| claim_id | int      | 任务ID |

---
#### 领取日常任务活跃度奖励

>  **cmd**

`claim_daily_quest_active_reward`

> **main_push**:

`player`

>  **param**:

| key_name    | val_type | desc       |
|-------------|----------|------------|
| claim_stage | int      | 活跃度阶段 |

---
#### 领取新手七天任务奖励

>  **cmd**

`claim_new_player_quest`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| claim_id | int      | 任务ID |

---
#### 领取新手七天任务最终奖励

>  **cmd**

`claim_new_player_final_reward`

> **main_push**:

`player`

>  **param**:

无

---

#### 领取特殊任务奖励

>  **cmd**

`claim_special_quest`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc |
| -------- | -------- | ---- |
|          |          |      |




---

## 1.2 v0.43

### 1.2.1 商店

#### 普通商店购买

>  **cmd**

  `normal_store_item_buy`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| id       | int      | 购买物品id   |
| num      | int      | 购买物品数量 |

---

## 1.3 v0.44

### 1.3.1 联盟帮助

#### 请求联盟帮助

>  **cmd**

  `al_help_apply`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                    |
|:----------|:---------|:------------------------|
| action_id | int      | 请求联盟帮助的action id |

---

#### 帮助联盟内全部可以帮助的action

>  **cmd**

  `al_help_all`

> **main_push**:

  `alliance`

>  **param**:

| key_name     | val_type | desc           |
| :----------- | :------- | :------------- |
| is_auto_help | int      | 是否是自动帮助 |

---
#### 客户端主动拉取可帮助的action列表

>  **cmd**

  `al_help_list_get`

> **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| 无       | 无       | 无   |

---

### 1.3.2 联盟礼物

#### 客户端主动拉取联盟礼物列表

>  **cmd**

  `get_al_gift_list`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
| :--------- | :------- | :----------- |
| al_gift_lv | int      | 联盟礼物等级 |

---

#### 开启单个联盟礼物

>  **cmd**

  `open_al_gift`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc                 |
|:-----------|:---------|:---------------------|
| al_gift_id | int      | 要开启的联盟礼物的id |
| type       | int      | 0：normal 1:iap       |
| 无         | 无       | 无                   |

---

#### 领取全部联盟礼物

>  **cmd**

  `open_al_gift_all`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| 无       | 无       | 无   |

---

#### 清除过期/已领取的联盟礼物

>  **cmd**

  `clear_al_gift`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| 无       | 无       | 无   |

---

#### 获取可开启的大宝箱

>  **cmd**

  `get_al_great_chest`

> **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| 无       | 无       | 无   |

---

#### 开启全部大宝箱

>  **cmd**

  `open_al_great_chest`

> **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| 无       | 无       | 无   |

---

### 1.3.3 联盟管理

#### 创建联盟

>  **cmd**

  `al_create`

>  **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc                       |
|:---------|:---------|:---------------------------|
| name     | string   | 联盟名称                   |
| nick     | string   | 联盟简称                   |
| desc     | string   | 联盟描述                   |
| lang     | int      | 联盟语言                   |
| policy   | int      | 加入策略(Normal=0;Auto=1;) |
| avatar   | int      | 旗帜                       |

---

#### 检查联盟名称

>  **cmd**

  `ds_create_alliance_check`

>  **main_push**:

  `global_svr`

>  **param**:

| key_name | val_type | desc                       |
|:---------|:---------|:---------------------------|
| name     | string   | 联盟名称                   |
| type     | int64    | 类型（1：名称 2：简称）     |
return_code：37304（存在）
---

#### 申请加入联盟

>  **cmd**

  `al_request_join`

>  **main_push**:

  `alliance`

>  **param**:

| key_name   | val_type | desc     |
|------------|----------|----------|
| target_aid | int      | 目标联盟 |

---

#### 撤销联盟申请

>  **cmd**

  `al_request_cancel`

>  **main_push**:

  `alliance`

>  **param**:

| key_name   | val_type | desc     |
|------------|----------|----------|
| target_aid | int      | 目标联盟 |

---

#### 同意加入联盟

>  **cmd**

  `al_request_allow`

>  **main_push**:

  `alliance`

>  **param**:

| key_name    | val_type | desc                  |
|-------------|----------|-----------------------|
| request_uid | int      | 请求加入联盟的用户uid |

---

#### 拒绝加入联盟

>  **cmd**

  `al_request_reject`

>  **main_push**:

  `alliance`

>  **param**:

| key_name    | val_type | desc                  |
|-------------|----------|-----------------------|
| request_uid | int      | 请求加入联盟的用户uid |

---

#### 退出联盟

>  **cmd**

  `al_leave`

>  **main_push**:

  `alliance`

>  **param**:

无

---

---

#### 更改联盟旗帜

>  **cmd**

  `al_avatar_change`

>  **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc                    |
|----------|----------|-------------------------|
| avatar   | string   | 旗帜id 注意是string类型 |

---

---

#### 更改联盟名字

>  **cmd**

  `al_name_change`

>  **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc         |
|----------|----------|--------------|
| name     | string   | 新的联盟名字 |

---

---

#### 更改联盟缩写

>  **cmd**

  `al_nick_change`

>  **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc         |
|----------|----------|--------------|
| nick     | string   | 新的联盟缩写 |

---



### 1.3.4 联盟科技

#### 获取联盟科技信息
>  **cmd**

  `al_research_info_get`

>  **main_push**:

  `svr_al_research_list`
  `svr_al_research_extra`

>  **param**:

无


#### 设置推荐联盟科技
>  **cmd**

  `set_recommend_al_research_id`

>  **main_push**:

  `svr_al_research_extra`

>  **param**:

| key_name    | val_type | desc |
|-------------|----------|------|
| research_id | int      |      |


#### 升级联盟科技
>  **cmd**

  `al_research_upgrade`

>  **main_push**:

  `svr_al_research_extra`

>  **param**:

| key_name    | val_type | desc |
|-------------|----------|------|
| research_id | int      |      |


#### 取消升级联盟科技
>  **cmd**

  `al_research_upgrade_cancel`

>  **main_push**:

  `svr_al_research_extra`

>  **param**:

| key_name    | val_type | desc |
|-------------|----------|------|
| research_id | int      |      |


#### 捐赠联盟科技
只能一次一次捐献，存在多倍暴击可能

>  **cmd**

  `donate_al_research`

>  **main_push**:

  `svr_al_research_donate_result`

>  **param**:

| key_name    | val_type | desc                                       |
|-------------|----------|--------------------------------------------|
| research_id | int      |                                            |
| donate_type | int      | 捐助类型, 0资源，1钻石                      |
| gem_num     | int      | 如果使用的是钻石，需要传入此值，传入用于校验 |


### 1.3.4 联盟技能

#### 捐献联盟技能
>  **cmd**

  `donate_al_skill`

>  **main_push**:


>  **param**:

| key_name    | val_type | desc                                       |
|-------------|----------|--------------------------------------------|
| al_skill_id | int      | 联盟技能id                                 |
| donate_type | int      | 捐助类型, 0资源，1钻石                      |
| gem_num     | int      | 如果使用的是钻石，需要传入此值，传入用于校验 |

#### 使用联盟技能
>  **cmd**

  `al_skill_open`

>  **main_push**:


>  **param**:

| key_name    | val_type | desc       |
|-------------|----------|------------|
| al_skill_id | int      | 联盟技能id |

---

### 1.3.5 联盟头衔

#### 联盟头衔更改

>  **cmd**

  `al_change_title`

> **main_push**:

  `alliance`

>  **param**:

| key_name   | val_type | desc     |
|:-----------|:---------|:---------|
| title_id   | int      | 头衔id   |
| target_uid | int      | 被赋予人 |

---

### 1.3.6 联盟商店

#### 联盟商店补货

>  **cmd**

  `al_replenish`

> **main_push**:

  `alliance`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| item_id  | int      | 物品id |
| item_num | int      | 数量   |

---

#### 联盟商店购买

>  **cmd**

  `al_shop_buy`

> **main_push**:

  `alliance`
  `player`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| item_id  | int      | 物品id |
| item_num | int      | 数量   |

---

#### 联盟回收

>  **cmd**

  `al_recycle`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| item_id  | int      | 物品id |
| item_num | int      | 数量   |

---


#### 获取联盟商店信息

>  **cmd**

  `al_shop_get`

> **main_push**:

  `player`

>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|

---

### 1.3.7 道具使用

#### 普通道具使用

>  **cmd**

  `use_common_item`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| item_id   | int      | 物品id                 |
| item_num  | int      | 数量                   |
| cost_type | int      | 使用方式(0:道具1:宝石) |

---

#### 批量道具使用

>  **cmd**

  `batch_use_common_item`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| item_list | array    | [[物品id,物品数量]]     |
---

#### 时间减少型道具使用

>  **cmd**

  `use_speeduptime_item`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                    |
|:----------|:---------|:------------------------|
| item_id   | int      | 物品id                  |
| item_num  | int      | 数量                    |
| cost_type | int      | 使用方式(0:道具1:宝石)  |
| target_id | int      | 使用目标队列(action id) |

---

#### 时间型增益道具使用

>  **cmd**

  `use_timebuff_item`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| item_id   | int      | 物品id                 |
| cost_type | int      | 使用方式(0:道具1:宝石) |

---

#### 开启随机奖励宝箱

>  **cmd**

  `open_random_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| chest_id  | int      | 宝箱id   |
| chest_num | int      | 宝箱数量 |

---

#### 开启自选奖励宝箱

>  **cmd**

  `open_select_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| chest_id   | int      | 宝箱id       |
| chest_num  | int      | 宝箱数量     |
| select_idx | int      | 目标奖励下标 |

---

#### 开启运营随机奖励宝箱

>  **cmd**

  `open_dc_random_chest`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| chest_id  | int      | 宝箱id   |
| chest_num | int      | 宝箱数量 |

---

#### 开启固定奖励宝箱

>  **cmd**

  `open_fixd_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| chest_id  | int      | 宝箱id   |
| chest_num | int      | 宝箱数量 |

---

#### 开启主城等级宝箱

>  **cmd**

  `open_castle_level_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| chest_id  | int      | 宝箱id   |
| chest_num | int      | 宝箱数量 |

---
#### 开启自选主城等级宝箱

>  **cmd**

  `open_select_castle_level_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| chest_id  | int      | 宝箱id   |
| chest_num | int      | 宝箱数量 |
| select_idx | int      | 目标奖励下标 |

---

## 1.4 v0.12

### 1.4.1 地块

#### 解锁大地块

>  **cmd**

  `unlock_block`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| block_id   | int      | 大地块id     |
| is_payment | int      | 是否付费解锁 |

---
### 1.4.2 科技

#### 科技升级

>  **cmd**

  `technology_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name      | val_type | desc     |
|:--------------|:---------|:---------|
| technology_id | int      | 科技id   |
| level         | int      | 目标等级 |

---

## 1.5 v0.13

### 1.5.1 资源

#### 采集资源

>  **cmd**

  `collect_resource`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc                                    |
|:------------|:---------|:----------------------------------------|
| building_id | int      | 采集哪个资源建筑的资源，此参数为建筑的id |

---

#### 采集所有资源   v0.17

>  **cmd**

  `collect_resource_all`

> **main_push**:

  `player`

>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|

---

### 1.5.2 建筑

#### 建造建筑

>  **cmd**

  `construct_building`

> **main_push**:

  `player`

>  **param**:

| key_name      | val_type | desc     |
|:--------------|:---------|:---------|
| building_type | int      | 建筑类型 |
| lv            | int      | 建筑等级 |
| pos           | int      | 建筑坐标 |
---

#### 合成建筑(单个合成和批量合成都用这个)

>  **cmd**

  `merge_building`

> **main_push**:

  `player`

>  **param**:

| key_name               | val_type | desc                 |
|:-----------------------|:---------|:---------------------|
| merge_building_id_list | array    | 用于合成的建筑的id列表 |
| target_building_list   | array    | 合成的目标建筑的列表\[{"lv":int32,"pos":int64\}]|
| building_type          | int      | 建筑类型(小时日志用)   |

---
#### 移动建筑/将领（后台认为这只是一组建筑/将领位置的移动）

>  **cmd**

  `move_entity`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type | desc                                                                                                           |
|:-----------------|:---------|:---------------------------------------------------------------------------------------------------------------|
| move_entity_list | object   | 移动的建筑及被让位的建筑列表 {"building":[{"id":int64, "pos":int32}], "commander":[{"id":int64, "pos":int32}]} |

---


---

#### 拆除建筑

>  **cmd**

  `remove_building`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc           |
|:------------|:---------|:---------------|
| building_id | int      | 要拆除的建筑id |

---


### 1.5.3 将领

#### 训练将领

>  **cmd**

  `train_commander`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc                   |
|:------------|:---------|:-----------------------|
| building_id | int      | 用于训练将领的将领营id |
| lv          | int      | 训练的将领等级         |
| pos         | int      | 训练的将领占据的位置   |

---

#### 取消训练将领

>  **cmd**

  `cancle_train_commander`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                   |
|:-------------|:---------|:-----------------------|
| building_id  | int      | 用于训练将领的将领营id |
| commander_id | int      | 取消的将领id           |

---

#### 加速训练将领

>  **cmd**

  `speedup_train_commander`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc                   |
|:------------|:---------|:-----------------------|
| building_id | int      | 用于训练将领的将领营id |
| item_id     | int      | 用于加速的道具id       |
| is_cost_gem | int      | 是否购买此道具         |
|is_all |int |是否加速全部:0: 加速正在训练的队列, 1: 加速全部队列||
|num |int |加速道具数量|
|items |object |全部加速需要, 示例如下|

items
```
{
  "1(svr_commander_id)": 1(cost_time),
  ...
}
```

---

#### 移动建筑/将领（后台认为这只是一组建筑/将领位置的移动）

>  **cmd**

  `move_entity`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type | desc                                                                                                           |
|:-----------------|:---------|:---------------------------------------------------------------------------------------------------------------|
| move_entity_list | object   | 移动的建筑及被让位的建筑列表 {"building":[{"id":int64, "pos":int32}], "commander":[{"id":int64, "pos":int32}]} |

---

#### 合成将领

>  **cmd**

  `merge_commander`

> **main_push**:

  `player`

>  **param**:

| key_name                | val_type | desc                                                                   |
|:------------------------|:---------|:-----------------------------------------------------------------------|
| merge_commander_id_list | array    | 用于合成的将领的id列表                                                 |
| targer_commander_list   | array    | 目标将领列表[{"type":int32(目标将领类型),"pos":int32(目标将领的坐标)}] |


#### 一键合成将领

>  **cmd**

  `merge_all_commander`

> **main_push**:

  `player`

>  **param**:

| key_name                | val_type | desc                                                                   |
|:------------------------|:---------|:-----------------------------------------------------------------------|
| merge_commander_id_list | array    | 用于合成的将领的id列表                                                 |
| targer_commander_list   | array    | 目标将领列表[{"type":int32(目标将领类型),"pos":int32(目标将领的坐标)}] |

---

#### 删除将领

>  **cmd**

  `remove_commander`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc         |
|:-------------|:---------|:-------------|
| commander_id | int      | 删除的将领id |

#### 批量删除将领

>  **cmd**

  `remove_multi_commander`

> **main_push**:

  `player`

>  **param**:

| key_name       | val_type | desc             |
|:---------------|:---------|:-----------------|
| normal_commander_list | array    | 删除的训练将领id列表:  [1,1,1...]|

---

#### 解锁将领管理所卡槽

>  **cmd**

  `unlock_commander_slot`

> **main_push**:


>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|
无

---

#### 领取将领

>  **cmd**

  `claim_commander`

> **main_push**:


>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|
|is_all|int|0: 领取单个，1 建筑内的全部
|svr_commander_id|int|将领id，领取单个时传入

---


### 1.5.4 token

#### 开始制造token

>  **cmd**

  `product_token`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc           |
|:---------|:---------|:---------------|
| item_id  | int      | 生产的道具id   |
| item_num | int      | 生产的道具数量 |

---

#### 取消token制造

>  **cmd**

  `cancel_product_token`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc                |
|:---------|:---------|:--------------------|
| token_id | int      | 取消制造的token的id |
---

#### 加速单个token制造

>  **cmd**

  `speed_up_token`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc                |
|:------------|:---------|:--------------------|
| token_id    | int      | 加速制造的token的id |
| item_id     | int      | 用于加速的道具id    |
| item_num    | int      | 使用的道具数量      |
| is_cost_gem | int      | 是否购买此道具      |
---

#### 加速全部token制造

>  **cmd**

  `speed_up_all_token`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc             |
|:------------|:---------|:-----------------|
| item_id     | int      | 用于加速的道具id |
| item_num    | int      | 使用的道具数量   |
| is_cost_gem | int      | 是否购买此道具   |
| items       | object   | 示例如下         |

items
```
{
  "1(int64 svr_token_id)": 1(cost_time),
  ...
}
```
---

#### 领取已完成的token

>  **cmd**

  `get_token`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc              |
|:---------|:---------|:------------------|
| token_id | int      | 要领取的token的id |

---

#### 领取已完成的全部token

>  **cmd**

  `get_all_token`

> **main_push**:

  `player`

>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|

---

## 1.6 v0.14

### 1.6.1 兵营

#### 生产兵

>  **cmd**

  `soldier_train`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| building_svr_id | long     | 生产对应的兵营的svr_id |
| pos             | int      | 生产中的兵在城内的位置 |
| soldier_id      | int      | 要训练的兵的id         |

---
#### 治疗兵

>  **cmd**

  `soldier_heal`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                                |
|:----------------|:---------|:------------------------------------|
| building_svr_id | long     | 生产对应的兵营的svr_id              |
| soldier_list    | object   | 治疗列表, key: soldier_id, val: num |

---
#### 晋升兵

>  **cmd**

  `soldier_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| soldier_id      | int      | 要晋升的兵的id         |
| soldier_num     | int      | 要晋升的兵的数量       |
| building_svr_id | long     | 生产对应的兵营的svr_id |
| pos             | int      | 生产中的兵在城内的位置 |
| target_id       | int      | 目标士兵id             |

---
#### 遣散兵

>  **cmd**

  `soldier_dismiss`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc             |
|:------------|:---------|:-----------------|
| soldier_id  | int      | 要遣散的兵的id   |
| soldier_num | int      | 要遣散的兵的数量 |

---
#### 取消训练

>  **cmd**

  `soldier_train_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                 |
|:-------------|:---------|:---------------------|
| train_svr_id | long     | 训练队列对应的svr_id |

---
#### 加速训练

>  **cmd**

  `speed_up_train_soldier`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                                   |
|:----------------|:---------|:---------------------------------------|
| building_svr_id | long     | 要加速的队列所在兵营的svr_id           |
| item_id         | int      | 加速道具id                             |
| item_num        | int      | 加速道具使用数量                       |
| is_cost_gem     | int      | 0: 消耗道具, 1: 消耗宝石               |
| is_all          | int      | 0: 加速正在训练的队列, 1: 加速全部队列 |
| items           | object   | 非全部加速, 示例如下                   |
| train_svr_id    | int      | 训练队列svr_id                         |

items
```
{
  "1(int64 svr_commander_id)": 1(cost_time),
  ...
}
```

---
#### 取消治疗

>  **cmd**

  `soldier_heal_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                             |
|:----------------|:---------|:---------------------------------|
| building_svr_id | long     | 要取消的治疗队列所在兵营的svr_id |

---
#### 刷新预生产队列训练时间

>  **extra_info**

需要在进入训练队列界面/全局加速界面时调用来刷新svr_soldier_train_time_info

>  **cmd**

  `refresh_soldier_train_time`

> **main_push**:

  `player`

>  **param**:

|key_name|val_type|desc|
|:----|:----|:----|

---


## 1.6 v0.15

### 1.6.1 副本

#### 发起进攻城内副本

>  **cmd**

  `attack_city_raid`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc                 |
|:-----------|:---------|:---------------------|
| block_id   | int      | 城内副本所属的地块id |
| troop_info | obj      | 如下                 |

troop_info格式:
```json
{
    "pos":{
        "dir": 1, // 朝向 1-8 
        "commander":{
            "槽位":[commander_id],
        },
        "soldier":{
            "type":num
        },
        "hero": { // 0.61
            "main": 1,
            "vice": 1
        }
    }
}
```
---

#### 发起进攻远征副本

>  **cmd**

  `attack_expedition_raid`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc   |
|:-----------|:---------|:-------|
| hurdle     | int      | 副本id |
| troop_info | obj      | 如下   |

troop_info格式:
```json
{
    "pos":{
        "dir": 1, // 朝向 1-8 
        "commander":{
            "槽位":[commander_id],
        },
        "soldier":{
            "type":num
        },
        "hero": { // 0.61
            "main": 1,
            "vice": 1
        }
    }
}
```
---

#### 领取战斗结束奖励
>  **cmd**

  `commit_raid`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| raid_id  | int      | 副本id |
---

#### 退出副本
>  **cmd**

  `exit_raid`

> **main_push**:

  `raid_server`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| raid_id  | int      | 副本id |
---

#### 清除副本
>  **cmd**

  `clear_raid`

> **main_push**:

  `raid_server`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| raid_id  | int      | 副本id |
---

### 1.6.2 战略中心

#### 副本资源收集

>  **cmd**

  `collect_expedition_bonus_production`

> **main_push**:

  `player`

>  **param**:

无

---

## 1.7 v0.18

### 1.7.1 添加士兵治疗

>  **cmd**

`soldier_treatment_add`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc     |
|:----------------|:---------|:---------|
| svr_building_id | int      | 建筑id   |
| soldier_id      | int      | 士兵id   |
| num             | int      | 士兵数量 |
| pos             | int      | 地图位置 |

### 1.7.2 取消士兵治疗

>  **cmd**

`soldier_treatment_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| svr_id   | int      | svr_id |

---

## 1.8 v0.21

#### 领取占领区域的奖励

>  **cmd**

  `get_area_reward`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc       |
|:------------|:---------|:-----------|
| svr_id_list | array    | 奖励id列表 |

---

#### 通用/半通用token使用

>  **cmd**

  `convert_common_token`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                 |
|-----------------|----------|----------------------|
| common_item_id  | int      | 通用/半通用token的id |
| common_item_num | int      | 数量                 |
| target_item_id  | int      | 兑换成专属token的id  |

---

#### 挂机道具使用

>  **cmd**

  `use_offline_item`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type | desc     |
|------------------|----------|----------|
| offline_item_id  | int      | 挂机的id |
| offline_item_num | int      | 数量     |

---

#### 领取训练士兵

>  **cmd**

  `claim_train_soldier`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc           |
|--------------|----------|----------------|
| train_svr_id | int      | 训练队列svr_id |

---

#### 领取治疗完成的士兵

>  **cmd**

`claim_treatment_soldier`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| svr_id   | int      | svr_id |

---

#### 批量领取士兵(训练/晋升/治疗)

>  **cmd**

  `batch_claim_soldiers`

> **main_push**:

  `player`

>  **param**:

| key_name           | val_type | des                  |
| ------------------ | -------- | -------------------- |
| train_svr_id_list  | array    | 兵营的训练svr_id列表 |
| treat_svr_id_list  | array    | 医院的治疗svr_id列表 |
| revive_svr_id_list | array    | 教堂的复活svr_id列表 |
| reward_svr_id_list | array    | 赠送士兵svr_id列表   |

---

#### 预领取挂机资源(计算资源产量)

>  **cmd**

  `pre_collect_expedition_production`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---

## 1.9 v0.61

### 1.9.1 装备

#### 穿装备

>  **cmd**

  `put_on_equip`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | des                                                                      |
|--------------|----------|--------------------------------------------------------------------------|
| svr_equip_id | int      | 后台给的装备唯一id                                                       |
| svr_hero_id  | int      | 后台给的英雄唯一id                                                       |
| slot         | int      | 装备槽位(1-武器,2-头盔,3-上装,4-手套,<br/>5-下装,6-鞋子,7-饰品1,8-饰品2) |

---

#### 脱装备

>  **cmd**

  `put_off_equip`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | des                                                                          |
|-------------|----------|------------------------------------------------------------------------------|
| svr_hero_id | int      | 后台给的英雄唯一id                                                           |
| slot        | int      | 装备槽位槽位(1-武器,2-头盔,3-上装,4-手套,<br/>5-下装,6-鞋子,7-饰品1,8-饰品2) |

---

#### 装备打造

>  **cmd**

  `compose_equip`

> **main_push**:

  `player`

>  **param**:

| key_name      | val_type | des                |                                                                            |
|---------------|----------|--------------------|----------------------------------------------------------------------------|
| equip_id      | int      | 数值配置的装备类型 |                                                                            |
| drawing_list  | array    | 图纸列表           | [{type: 1, // 1 图纸, 2 碎片, 3 宝箱 ,id: 1,   // 对应的 id, num  //数量}] |
| material_list | array    | 材料列表           | [{type: 1, // 1 图纸, 2 碎片, 3 宝箱 ,id: 1,   // 对应的 id, num  //数量}] |

---

#### 装备升级

>  **cmd**

  `equip_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name      | val_type | des                |                                                                            |
|---------------|----------|--------------------|----------------------------------------------------------------------------|
| equip_id      | int      | 装备的后台ID		|                                                                            |
| type      	| int      | 升级类型			| 1为升星,2为升级品质                                                        |
| tar_lv        | int      | 目标等级			| 升星时为目标星级(1,2,3)，升阶时为目标品质(0,1,2,3,4)                       |
| material_list | array    | 材料列表           | [{type: 1, //装备材料/宝箱 ,id: 1,   // 对应的 id, num  //数量}] |

---

#### 装备分解

>  **cmd**

  `decompose_equip`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | des                |
|--------------|----------|--------------------|
| svr_equip_id | int      | 后台给的装备唯一id |

---

#### 图纸合成

>  **cmd**

  `compose_equip_drawing`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type | des            |
|------------------|----------|----------------|
| equip_drawing_id | int      | 数值装备图纸id |

---

#### 材料合成

>  **cmd**

  `compose_equip_material`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des            |
|-------------------|----------|----------------|
| target_id | int      | 目标装备材料id |
| source_id | int      | 目标装备材料id |
| num       | int      | 数量           |

---

#### 材料分解

>  **cmd**

  `decompose_equip_material`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des            |
|-------------------|----------|----------------|
| target_id | int      | 目标装备材料id |
| source_id | int      | 目标装备材料id |
| num       | int      | 数量           |

---

#### 选择装备天赋

>  **cmd**

  `select_equip_talent`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | des                |
|--------------|----------|--------------------|
| svr_equip_id | int      | 后台给的装备唯一id |
| talent       | int      | 天赋               |

---

#### 材料生产

>  **cmd**

  `equip_material_produce`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | des     |
|-----------------|----------|---------|
| svr_building_id | int      | 建筑id  |
| item_id         | int      | 物品id  |
| item_num        | int      | 物品num |

---

#### 取消生产

>  **cmd**

  `equip_material_produce_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des    |
|----------|----------|--------|
| svr_id   | int      | 队列id |

---

#### 生产领取

>  **cmd**

  `equip_material_produce_claim`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des    |
|----------|----------|--------|
| svr_id   | int      | 队列id |

---

#### 领取所有

>  **cmd**

  `equip_material_produce_claim_all`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | des    |
|-----------------|----------|--------|
| svr_building_id | int      | 建筑id |

---
#### 获取地图缩略信息

>  **cmd**

  `get_map_brief_obj`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
|----------|----------|------|
| sid      | int      | 服id |
| extra_aid      | int      | 额外获取某个联盟的成员brief数据 |
---

#### 获取地图信息

>  **cmd**

  `game_svr_map_get`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des     |
|----------|----------|---------|
| sid      | int      | 服id    |
| bid_list | array    | bid列表 |

---

#### 派遣斥候

>  **cmd**

  `dispatch_scout`

> **main_push**:

  `ds_player`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| scout_queue_id | int      | 斥候id                                                                    |
| tar_pos        | int64    | 目的地坐标                                                                |
| tar_type       | int64    | 斥候行动类型 0:空闲 1:撤回 2:山洞 3:迷雾 4:侦查军队 5:侦查城市 6:侦查资源 14:前往雷达|

| tar_limit		    | array 	| 如果tar_type是迷雾的话，该字段应该存在并且表示 想要探索地图块的左上与右下坐标 |

| tar_info		    | object 	|{"type":int32, "id":int64} |

| need_camp	| int32 	|是否驻扎 0: 不驻扎  1:驻扎 |



#### 村庄探索

>  **cmd**

  `scout_village`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des      |
|----------|----------|----------|
| tar_pos  | int      | 村庄坐标 |

---


#### 拉取探访过的村庄/洞穴和全部迷雾信息

>  **cmd**

  `get_player_visit`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---



#### 使用清除迷雾道具

>  **cmd**

  `use_clear_fog_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name  | val_type | des              |
|-----------|----------|------------------|
| item_id   | int      | 迷雾道具id       |
| tar_limit | array    | 左上右下点的坐标 |

---

#### 派遣城市内的兵

>  **cmd**

  `dispatch_troop`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| march_type  | int      | 行军类型(1:驻扎 2:攻击 3:攻击资源地 4: 采集资源地 12:采集符文)                                 |
| target_type | int      | 目标类型(2.城市 45.野蛮人, 101:军队 6:~~采集地(废弃)~~,50地脉 103:标识空地 28:符文, 29:宝箱|
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                                               |
| march_info  | object   | 行军携带的军队信息 {"soldier":{"1":100},"hero":{vice":[]},"carry_lord":0(不携带)/1(携带),"leader":0(填兵队列)/1(主队列)},"effect_skill":{"$(hero_id)": {"$(slot_id)":skill_id}},"equip_preset":${preset_id} |

> **攻击资源地**

{
	"march_type":3,
	"target_type":6,
	"target_info":{
		"id":"1_1000",
    "key": 1,
		"pos":"17500350000"
	},
	"march_info":{
		"soldier":{
			"2":200,
		},
		"commander":{
			"1":[1, 2, ] // 将领的 svr_id
		},
		"hero":{
		  main:10,
		  vice:8
		},
		"sweep_count" : 1, // 扫荡次数,没有则不填这个字段
    "equip_preset" : int, // 装备预设id,没有则不填这个字段
	},

}
---

#### 派遣城市外的兵

>  **cmd**

  `change_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                         |
|-------------|----------|-----------------------------------------------------------------------------|
| march_type  | int      | 行军类型(1:驻扎 2:攻击 3:攻击资源地 4: 采集资源地, 5:回城 12:采集符文)      |
| target_type | int      | 目标类型(2.城市 45.野蛮人, 101:军队 6:采集地 103:标识空地 28:符文)          |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                            |
| march_info  | object   | 行军信息 {"ids":[unique_id(string)], "over_defend":true},默认不驻扎，直接回城 |

> **攻击资源地**

{
	"march_type":3,
	"target_type":6,
	"target_info":{
		"id":"1_1000",
		"pos":"17500350000"
	},
	"march_info":{
		"id":["101_1000", "102_1000"]
	}

}
---

#### 原地驻扎

>  **cmd**

  `troop_defend`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des        |
|----------|----------|------------|
| pos      | int      | 驻扎的位置 |
| id       | string   | 军队id     |

---



#### op清迷雾

>  **cmd**

  `op_clear_fog`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | des      |
|-----------|----------|----------|
| tar_limit | array    | 范围坐标 |

---

#### 无效道具兑换

>  **cmd**

  `exchange_invalid_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| type     | int      | global type |
| id       | int      | id          |
| num      | int      | 数量        |

---


## 1.10 v0.63


### 1.10.1

#### 打开Vip宝箱(登陆，每日)
>  **cmd**

  `vip_open_chest`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                |
|------------|----------|------------------------------------|
| chest_id   | int      | 登陆宝箱传0, 每日vip宝箱传 vip等级 |
| chest_type | int      | 0: 登陆宝箱，1: 每日宝箱            |

---

### 1.10.2

#### 英雄归来活动兑换奖励

>  **cmd**

`hero_back_shop_exchange`

> **main_push**:

`player`

>  **param**:

| key_name    | val_type | desc     |
|-------------|----------|----------|
| reward_type | int      | 奖励type |
| reward_id   | int      | 奖励id   |
| reward_num  | int      | 奖励数量 |

---

#### 远征商店兑换物品
>  **cmd**

  `expedition_shop_buy`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                   |
|-------------|----------|---------------------------------------|
| version | int      | 远征商店的当前版本   |
| type | int      | 所购买物品所属的槽位类型（0：固定，1：不固定，2：特权） |
| index | int | 所购买物品的槽位id |
| num | int | 购买数量 |

---

#### 远征商店刷新随机奖励
>  **cmd**

  `refresh_expedition_shop`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---


### 1.10.3 保护罩

#### 使用免费保护罩

>  **cmd**

`use_free_peace_time`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |

---

#### 使用时间型增益道具

>  **cmd**

`use_time_buff_item`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc                  |
|-----------|----------|-----------------------|
| cost_type | int      | 0:消耗道具;1:消耗宝石 |
| item_id   | int      | 道具id                |

---

#### 时代突破领取任务奖励
>  **cmd**

  `collect_age_upgrade_quest`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                |
| -------- | -------- | ------------------ |
| quest_id | int      | 时代突破任务对应id |

---

#### 地图搜索
>  **cmd**

  `search_obj`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type	| des            	|
| -------- | -------- | ------------------ |
| tar_type 	        | int 		  | 搜索类型，和map_obj类型一致。野蛮人:45,资源地6 |
| tar_inside_type 	| int 		  | 内置类型。如果是资源地，则为资源类型 |
| tar_lv           	| int 		  | 目标等级 |
| tar_full          | int       | 是否搜索满的资源地 0-不是 1-是，默认传0|

---

## 1.11 v0.64


### 1.11.1 城墙
#### 城墙设置主副将
>  **cmd**

  `city_wall_set_hero`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des           |
|----------|----------|---------------|
| pos      | int      | 1, 主将，2副将 |
| hero_id  | int      | 将领 id       |

---
#### 城墙灭火

>  **cmd**

  `city_wall_clear_fire`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| 无       |          |      |

---
#### 城墙修复

>  **cmd**

  `city_wall_repaire`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| gem      | int      | 消耗宝石数量     |

---


#### 获取game_server上所有的玩家数据

>  **cmd**

  `game_server_login_get`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des |
|----------|----------|-----|
|    all      |int          |1:全量数据     |

---

#### 获取game_server上的路径信息

>  **cmd**

  `game_map_path_get`

> **main_push**:

  `game_server``

>  **param**:

| key_name  | val_type | des                        |
|-----------|----------|----------------------------|
| start_pos | string   | 起始点                     |
| end_pos   | string   | 目标点                     |
| type      | int      | 类型(和实体的类型保持一致) |

---

### 1.11.2 个人信息

#### 获取他人信息
>  **cmd**

  `player_info_get`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | des       |
|----------|----------|-----------|
| uid      | int      | 对方的uid |

#### 根据玩家名称获取玩家信息
>  **cmd**

  `get_uid_by_name`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | des      |
|----------|----------|----------|
| name     | string   | 玩家名称 |

---

### 1.11.3 行动力

#### 购买行动力
>  **cmd**

  `action_energy_buy_use`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | des                     |
|----------|----------|-------------------------|
| gem_cost | int      | 需要的宝石数量，用于校验 |

---

#### 使用免费行动力
>  **cmd**

  `action_energy_free_use`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| 无       |          |      |

---

#### 实体路径获取
>  **cmd**

  `unity_path_get`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des           |
|-------------|----------|---------------|
| type        | int      | 军队，还是斥候 |
| march_info  | object   | 行军信息      |
| target_info | object   | 目标信息      |

+ 派遣城内兵去资源地
{
	
	type:101,
	march_info:{},
	target_info:{
		"unique_id":"6_234222"
	}
}

+ 派遣城外兵去资源地
{
	type:101,
	march_info:{
		"unique_id":"101_234234234"
	},
	target_info:{
		"unique_id":"6_234222",
	}
}

+ 派遣城内兵去驻扎
{
	type:101,
	march_info:{
	},
	target_info:{
		"pos":"120100000"
	}
}

+ 派遣斥候探索迷雾
{
	type:102,
	march_info:{
	},
	target_info:{
		"pos":"120100000",
	}
}

---

## 1.12 v0.65


### 1.12.1 移城

#### 定点移城

>  **cmd**

  `fixed_move_city`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                            |
|----------|----------|--------------------------------|
| tar_pos  | int      | 坐标信息（后台坐标）             |
| use_gem  | int      | 是否使用金币购买道具           |
| item_id  | int      | 道具id(根据道具id确定移城类型) |

---

#### 随机移城

>  **cmd**

  `random_move_city`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|  item_id  |   int   | 道具id |

---

#### 被动移城动画播放完毕

>  **cmd**

  `passive_move_city_confirm`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---

## 1.13 v0.68


### 1.13.1 资源运输

#### 派遣运输部队

>  **cmd**

  `dispatch_transport`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des                |
|--------------|----------|--------------------|
| resource     | object   | 运输的资源(KV结构) |
| tax_resource | object   | 税收的资源(KV结构) |
| tax_rate     | int      | 派遣运输时的税率   |
| target_uid   | int      | 目标玩家UID        |
| target_pos   | int64    | 目标玩家pos        |

---

#### 召回运输队列

>  **cmd**

  `transport_recall`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des |
|----------|----------|-----|
| src_type | int      |     |
| src_id   | int      |     |

---

#### 召回运输队列_0623

>  **cmd**

  `transport_recall_new`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des |
|----------|----------|-----|
| unique_id | string      |  type_id   |
---

### 1.13.2 联盟礼物

#### iap礼物匿名设置

>  **cmd**

  `set_iap_anonymous`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| switch   | int      | 0:关闭匿名 1:开启匿名 |


## 1.13.3 落日峡谷


#### 拉取目标军队预设信息(用户，机器人的客户端自己读取配置)

>  **cmd**

  `sunsetcanyon_target_troop_get`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des           |
|------------|----------|---------------|
| target_uid | uid      | 目标用户的 id |

#### 发起战斗

>  **cmd**

  `sunsetcanyon_start`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des                                 |
|--------------|----------|-------------------------------------|
| session      | int      | 赛季                                |
| target_type  | int      | 1: 玩家，2: 机器人                   |
| target_id    | int      | 玩家的时候传 uid, 机器人传机器人id  |
| skip_battle_process  | int      | 1: 跳过战斗  0: 不跳过              |
| source_troop | obj      | 自己的军队配置                      |
| target_troop | obj      | 目标的军队配置，用于校验军队是否改变 |

```json {
    session: 1,
    target_type: 1,   // 1: 玩家，2: 机器人
    target_id: 1,     // 玩家的时候传 uid, 机器人传机器人id
    skip_battle: 0,
    source_troop: {   // 自己的军队配置
        "1": {  // 槽位
            main_hero: 1,
            vice_hero: 1,
            commander: {
              "1": 1,     // id->num
            },
            soldier: { 
              "1": 1      // id->num
            },
        }
    }, 
    target_troop: {   // 目标的军队配置，用于校验军队是否改变
        "1": { // 槽位
            main_hero: {
                id: 1,
                level: 1,
                quality: 1,
                awoken: 1,
            },
            vice_hero: {
                id: 1,
                level: 1,
                quality: 1,
                awoken: 1,
            },
            commander: {
                "1": 1,     // id->num
            },
            soldier: { 
                "1": 1      // id->num
            },
        }
    },
}
```

#### 拉取落日峡谷记录

>  **cmd**

  `sunsetcanyon_record_get`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |


#### 0.73 拉取他人一条落日峡谷记录

>  **cmd**

  `sunsetcanyon_record_target_get`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type	| des            	|
|----------------|-------|-------------|
| target_uid        | int       | 目标用户id         |
| svr_id            | int       | 记录id             |

#### 军队预设设置

>  **cmd**

  `sunsetcanyon_defensive_set`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des      |
|----------|----------|----------|
| troop    | obj      | 预设军队 |

```json
troop: {       // 军队配置
    "1": {     // 槽位
        main_hero: 1,
        vice_hero: 1,
        commander: {
            "1": 1,     // id->num
        },
        soldier: { 
            "1": 1      // id->num
        },
    }
}
```

#### 拉取战役basic信息, 进入战役界面时拉取, 主要用于红点逻辑(如有)

>  **cmd**

  `get_campaign_basic`

> **main_push**:

  `pvp_svr`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |


#### 拉取日落峡谷详细信息, 进入日落峡谷页面时拉取

>  **cmd**

  `get_arena_info`

> **main_push**:

  `pvp_svr`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| is_all   |  int32   | 0/1 是否返回svr_arena_rank_info表 |


#### 拉取日落峡谷历史排行榜

>  **cmd**

  `get_arena_history_rank`

> **main_push**:

  `pvp_svr`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |


#### 拉取日落峡谷匹配结果

>  **cmd**

  `get_arena_match_result`

> **main_push**:

  `pvp_svr`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |


### 1.13.4 增援

#### 派遣军队增援


>  **cmd**

  `dispatch_troop`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| march_type  | int      | 行军类型(11：增援)                                                                              |
| target_type | int      | 目标类型(2.城市)                                                                               |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                                               |
| march_info  | object   | 行军携带的军队信息 {"soldier":{"1":100},"commander":{"1":{"3":1}},"hero":{"main":10,"vice":8}} |

---

#### 派遣城市外的兵去支援

>  **cmd**

  `change_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                         |
|-------------|----------|-----------------------------------------------------------------------------|
| march_type  | int      | 行军类型(11：增援)                                                           |
| target_type | int      | 目标类型(2.城市)                                                            |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                            |
| march_info  | object   | 行军信息 {"id":[unique_id(string)], "over_defend":true},默认不驻扎，直接回城 |

---

#### 根据uid拉取对方的city_obj

>  **cmd**

  `get_city_info_by_uid`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | des     |
|------------|----------|---------|
| target_uid | int      | 目标uid |


### 1.13.5 联盟排行榜


>  **cmd**

  `al_member_rank_get`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

### 1.13.6 集结

#### 获取玩家的预警列表

>  **cmd**

  `get_warning_list`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |


#### 获取单个预警详情

>  **cmd**

  `get_warning_detail`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | des          |
|-----------|----------|--------------|
| unique_id | string   | 预警的唯一id |


#### 创建集结

>  **cmd**

  `create_rally_war`

> **main_push**:

  `game_server`

>  **param**:

| key_name        | val_type | des                    |
|-----------------|----------|------------------------|
| march_type      | int32    | 行军类型(rally_attack) |
| target_type     | int32    | 目标类型               |
| target_info     | object   | 目标信息               |
| march_info      | object   | 与派兵保持一致         |
| prepare_time    | int32    | 准备时长(单位:s)       |
| recommand_troop | array    | 推荐兵种类型           |
| timestamp 	  | int64    | 用于发送联盟邀请(us)   |

> **集结城寨**

{
	"march_type":13,
	"target_type":13,
	"target_info":{
		"id":"13_324242",
	},
	"prepare_time":300,
	"recommand_troop":[1,2,3,4],
	"march_info":{
		"soldier":{
			"2":200,
		},
		"commander":{
			"1":[1, 2, ] // 将领的 svr_id
		},
		"hero":{
      main:10,
      vice:8
    }
	}
}

#### 召回集结

>  **cmd**

  `recall_reinforce`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | des          |
|-----------|----------|--------------|
| unique_id | string   | 召回的集结Id |


#### 遣返集结

>  **cmd**

  `repatriate_rally_reinforce`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | des          |
|-----------|----------|--------------|
| unique_id | string   | 集结id       |
| target_id | string   | 需要遣返的id |


#### 修改集结推荐兵种

>  **cmd**

  `change_rally_recommand_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name        | val_type | des          |
|-----------------|----------|--------------|
| unique_id       | string   | 集结id       |
| recommand_troop | array    | 推荐兵种类型 |

#### 解散集结

>  **cmd**

  `rally_dismiss`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | des    |
|-----------|----------|--------|
| unique_id | string   | 集结id |

## 1.14 v0.69

### 1.14.1 联盟第三期


#### 玩家领取联盟资源地产出资源

>  **cmd**

  `collect_al_resource`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des |
|----------|----------|-----|
|          |          |     |

-------------------------

#### 派遣军队去建造联盟建筑

>  **cmd**

  `construct_al_building`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name    | val_type | des                                                                                         |
|-------------|----------|---------------------------------------------------------------------------------------------|
| march_type  | int32    | 12建造并前往                                                                                |
| target_type | int32    | 9联盟要塞,10联盟旗子,                                                                       |
| target_info | obj      | {"key":int32（数值id）,"pos":int64(建造坐标),"insert_id":如果是联盟要塞，需要内置id}           |
| march_info  | obj      | 如果是调度已有的军队，使用change_troop命令字的参数，如果是新建一支队列，使用dispatch_troop参数 |

---

#### 拆除联盟建筑·
>  **cmd**

  `remove_al_building`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des                        |
|----------|----------|----------------------------|
| al_nick  | string   | 拆除者（当前玩家）的联盟简称 |
| uname    | string   | 玩家名字                   |
| avatar   | int32    | 玩家头像                   |
| src_type | int32    | obj类型                    |
| src_id   | int64    | obj id                     |
---

#### 主动拉取自己的联盟建筑列表
>  **cmd**

  `get_al_building_list`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---

#### 主动拉取某个联盟建筑的增援队列
>  **cmd**

  `get_al_building_reinforce_list`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des     |
|----------|----------|---------|
| src_type | int32    | obj类型 |
| src_id   | int64    | obj id  |
---


#### 主动使某个燃烧的联盟建筑进入恢复状态
>  **cmd**

  `recovery_al_building`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des     |
|----------|----------|---------|
| src_type | int32    | obj类型 |
| src_id   | int64    | obj id  |
---

#### 更换驻防军队
>  **cmd**

  `change_al_building_main_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name        | val_type | des          |
|-----------------|----------|--------------|
| src_unique_id   | string   | 建筑id       |
| troop_unique_id | string   | 换到哪只军队 |
---



### 1.14.2 VIP 商店

#### VIP商店购买

>  **cmd**

  `vip_shop_buy`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des                                  |
| ------------ | -------- | ------------------------------------ |
| goods_id     | int32    | 购买的商品id                         |
| buy_num      | int32    | 购买的数量                           |
| select_index | int32    | 购买可选商品时，选择的下标 (从0开始) |
---

### 1.14.3 神秘商店

#### 神秘商店刷新
>  **cmd**

  `mystery_shop_refresh`

> **main_push**:

  `ds_player`

>  **param**:

| key_name  | val_type | des           |
|-----------|----------|---------------|
| cost_type | int32    | 0, 免费，1宝石 |
---


#### 神秘商店购买
>  **cmd**

  `mystery_shop_buy`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des          |
|----------|----------|--------------|
| goods_id | int32    | 购买的商品id |
---


### 1.14.4 Token生产机优化

#### token生产
>  **cmd**

  `token_produce`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des    |
|-----------------|----------|--------|
| svr_building_id | int      | 建筑id |
| item_id         | int      | 物品id |
| item_num        | int      | 数量   |

#### 取消生产
>  **cmd**

  `token_produce_cancel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des    |
|-----------------|----------|--------|
| svr_building_id | int      | 建筑id |
| svr_id          | int      | 生产id |

#### 领取
>  **cmd**

  `token_produce_cliam`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des    |
|-----------------|----------|--------|
| svr_building_id | int      | 建筑id |
| svr_id          | int      | 生产id |

#### 领取所有
>  **cmd**

  `token_produce_cliam_all`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des    |
|-----------------|----------|--------|
| svr_building_id | int      | 建筑id |

#### 加速
>  **cmd**

  `token_produce_speedup`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des           |
|-----------------|----------|---------------|
| svr_building_id | int      | 建筑id        |
| svr_id          | int      | 生产id        |
| item_id         | int      | 加速道具id    |
| item_num        | int      | 加速道具数量  |
| is_cost_gem     | int      | 0 道具 1 宝石 |





#### 加速所有
>  **cmd**

  `token_produce_speedup_all`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des           |
|-----------------|----------|---------------|
| svr_building_id | int      | 建筑id        |
| item_id         | int      | 加速道具id    |
| item_num        | int      | 加速道具数量  |
| is_cost_gem     | int      | 0 道具 1 宝石 |
---

### 1.14.5 充值(补单)/每日特惠

#### 普通充值/vip尊享宝箱
>  **cmd**

  `gem_recharge`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| recharge_type | int      | 充值类型(0: 普通宝石, 1: vip尊享宝箱, 2: 季卡型活动解锁挡位, 3: 成长基金 4:token礼包, 5: 季卡活动(battle pass)解锁挡位) , 10: 不作校验，补代金券 18：储值礼包 |
| recharge_info | object   | 和recharge_type对应的相关内容, type不同, 内容不同, 可以多传, 不能少传  |
| purchase_info | object   | 充值校验相关内容, 根据平台不同, 传的参数不同, 可以多传, 不能少传       |

+ recharge_info
```json
//通用参数
{
    "gems": int, // 购买礼包价格的基础宝石数
    "store_type": int, // 商店类型
    "store_id": int,
    "pid": int,
    "money":string,		//	ISO 4217定义的由三个字母的货币代码
    "amount":string,	// 该币种的支付金额
    "extra": {
        //参照运营协议增加参数
    },
    "discount_coupon_id": int, // 限定折扣券道具id
    "common_discount_coupon_id": int, //通用折扣券道具id
    "common_discount_coupon_expire": int, //通用折扣券过期时间
}

//折扣券
{
  "coupon" :{ //折扣券，如果使用折扣券传，不使用就不传
      "item_id": int,
      "item_num" :int
  }
}

// 神秘商店购买iap
{
  "mystery_shop" :{ 
    "pid":
  }
}

//vip宝箱
{
  "vip_level": int //vip等级  vip尊享宝箱
}

//季卡型活动解锁挡位
{
  "event_id": string, //活动解锁挡位
  "stage_idx":int //档位下标
}

//token
{
  "refresh_time":int //buy_time > refresh_time : buy_time ; else: refresh_time 
}

//季卡活动(battle pass)解锁挡位 v1.1.6
{
  "event_id": string, //活动id
  "elite_unlock_index": int //礼包索引id, 来自活动
}

//自选宝箱
"event_recharge": { // IAP活动充值的额外参数
	"iap_customize": {
		"chest_id": int    // 所购买的宝箱ID
		"chest_chose"：[int]   // 玩家选取的每个格子的奖励序列
		"version": int     // 奖励版本号
	}
}
```


+ purchase_info
```json
ios
{
    "trans_id": string, // 与apple交易的id
    "receipt": string, // ios凭证
    "package_status": int, //1代表审核状态 0代表普通状态
}

android
{
    "purchase_token": string, // android凭证
    "package_name": string, // android包名
}

通用参数, 必传
{
    "item_id": string, // 购买的iap对应的名字, 例: 50gems3
}

```
---

#### 补单
>  **cmd**

  `operate_gem_recharge`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| recharge_type | int      | 参照充值参数|
| recharge_info | object   | 参照充值参数，添加需要补单的uid参数 |
| purchase_info | object   | 参照充值参数|

+ recharge_info
```json
{
    "gems": int, // 购买礼包价格的基础宝石数
    "store_type": int, // 商店类型
    "store_id": int,
    "pid": int,
    "money":string,		//	ISO 4217定义的由三个字母的货币代码
    "amount":string,	// 该币种的支付金额
    "extra": {
        "commander_id": int // 统帅id，购买每日特惠的统帅礼包时使用
        //参照运营协议增加参数
    },
    "vip_level": int, //vip等级  vip尊享宝箱
    "need_operate_gem_recharge_uid": int, //需要补单的uid,
}
```

+ purchase_info
```json
ios
{
    "trans_id": string, // 与apple交易的id
    "receipt": string, // ios凭证
    "package_status": int, //1代表审核状态 0代表普通状态
}

android
{
    "purchase_token": string, // android凭证
    "package_name": string, // android包名
}

通用参数, 必传
{
    "item_id": string, // 购买的iap对应的名字, 例: 50gems3
}

```
注：为了解决uid不同进行补单的行为，补单没有svr_iap_promote的反包

---

#### 每日特惠
>  **cmd**

  `get_free_chest`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                   |
|---------------|----------|---------------------------------------|
| recharge_type | int      | 0: 普通                               |
| recharge_info | object   | 宝箱相关信息                          |
| purchase_info | object   | 充值校验相关内容, 只传该字段，内容为空 |

+ recharge_info
```json
{
    "store_type": int, // 商店类型
    "store_id": int,
    "pid": int,
    "extra": {
        "commander_id": int // 统帅id，购买每日特惠的统帅礼包时使用
        //参照运营协议增加参数
    }
}
```
---

## 1.15 v0.70

### 1.15.1 促销商城

#### 商城
>  **cmd**

  `get_iap_promote_data`

> **main_push**:

  `op_svr`

>  **param**:

| key_name          | val_type	| des            	|
|----------------|-------|-------------|
| extra     | object       | 运营需求额外信息 |

+ extra //具体运营定
```json
{
        "svr_ctime": int, // 服务器切服时间
        "user_ctime": int, // 玩家创号时间
        "castle_lv": int, // 主城等级
        "trigger_id": [int...]  // 触发场景id
}
```

注：EServiceType = EN_SERVICE_TYPE__CLIENT__OP_SVR_REQ // 2019

---

### 1.15.2 公告栏

#### 公告栏摘要
>  **cmd**

  `get_op_conf`

> **main_push**:

  `op_svr`


>  **param**:

无

> 反包
+ svr_bulletin_board_abs

```json
[{"mark":int, "timestamp":int},...]
```

+ svr_prohibit_image // 封禁的自定义头像
```json
[string, ...]
```


#### 公告栏详情
>  **cmd**

  `get_bulletin_board_info`

> **main_push**:

  `op_svr`

>  **param**:

| key_name          | val_type	| des            	|
|-----------|----------|----------|
| timestamp     | object       | 需要的公告时间戳 |

+ timestamp 
```json
[int,...] 
```

> 反包
+ svr_bulletin_board_info

```json
[
  {
            "mark": int,
            "timestamp": int,
            "ui": int,
            "localization": {//lang=0
                "title": string,
                "desc": string
            }
  },
  ...
]
```

注：EServiceType = EN_SERVICE_TYPE__CLIENT__OP_SVR_REQ // 2019

---

### 1.15.3 洛哈的试炼  v0.70

#### 使用白骨项链(白骨项链就是宝箱chest)
>  **cmd**

  `open_random_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | des      |
|-----------|----------|----------|
| chest_id  | int      | 宝箱id   |
| chest_num | int      | 宝箱数量 |

---

#### 使用洛哈的长弓或圆盾
>  **cmd**

  `use_item_create_obj`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| item_id  | int      | 长弓或者圆盾的item_id |

---

### 1.15.4 回天改命  v0.70

#### 设置scene_id
>  **cmd**

  `set_scene_id_list`

> **main_push**:

  `player`

>  **param**:

| key_name      | val_type | des                    |
|---------------|----------|------------------------|
| scene_id_list | array    | 需要设置的scene_id列表 |
| set_type      | int      | 0清空,1设置            |

---

### 1.15.5 坐标收藏  v0.70

#### 添加收藏

>  **cmd**

  `bookmark_add`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| sid      | int      | 服务器id              |
| pos_id   | int      | 位置  y * 1000000 + x |
| name     | string   | 名称                  |
| classify | int      | 收藏分类              |
| wild_type | int     | 野地类型              |

---

#### 更新收藏

>  **cmd**

  `bookmark_updt`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| sid      | int      | 服务器id              |
| pos_id   | int      | 位置  y * 1000000 + x |
| name     | string   | 名称                  |
| classify | int      | 收藏分类              |

---

#### 更新收藏

>  **cmd**

  `bookmark_del`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| sid      | int      | 服务器id              |
| pos_id   | int      | 位置  y * 1000000 + x |

---


### 1.15.6 聊天服务  v0.70

#### 拉取所有信息

> **cmd**

`chat_get`
    
> **main_push**

`chat_index_mgr`

> **param**

无

> **output**

    svr_friend_list
    svr_stranger_list
    svr_friend_invite_list
    svr_group_invite_list
    svr_group_list
    svr_channel_list

#### 拉取群组列表
> **cmd**

`chat_group_list_get`

> **main_push**

`chat_index_mgr`

> **param**

无

> **output**

    svr_group_list 

#### 创建群
> **cmd**

`chat_group_create`

> **main_push**

`chat_index_mgr`

> **param**

| key_name   | val_type     | des        |
|------------|--------------|------------|
| uid_list   | `array<int>` |            |
| group_name | string       | group name |


> **output**

    svr_group_list_inc
    svr_group_member_status

#### 邀请好友进群
> **cmd**

`chat_group_invite`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type     | des      |
|----------|--------------|----------|
| group_id | int          | group id |
| uid_list | `array<int>` |          |

> **output**

    svr_group_member_list
    svr_group_member_status

#### 群组踢人
> **cmd**

`chat_group_kick`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type     | des      |
|----------|--------------|----------|
| group_id | int          | group id |
| uid_list | `array<int>` |          |

> **output**

    svr_chat_single_channel
    svr_chat_single_channel_inc

#### 退群
> **cmd**

`chat_group_leave`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des      |
|----------|----------|----------|
| group_id | int      | group id |

> **output**

    svr_group_list_inc
    svr_group_member_status

#### 修改群名
> **cmd**

`chat_group_change_name`

> **main_push**

`chat_index_mgr`

> **param**

| key_name   | val_type | des        |
|------------|----------|------------|
| group_id   | int      | group id   |
| group_name | string   | group name |

> **output**

    svr_group_list_inc
    svr_group_invite_list_inc

#### 解散群
> **cmd**

`chat_group_dissolution`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des      |
|----------|----------|----------|
| group_id | int      | group id |

> **output**

    svr_group_list_inc
    svr_group_invite_list_inc

#### 获取成员列表
> **cmd**

`chat_group_member_get`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des      |
|----------|----------|----------|
| group_id | int      | group id |

> **output**

    svr_group_member_list

#### 拉取好友列表
> **cmd**

`chat_friend_list_get`

> **main_push**

`chat_index_mgr`

> **param**


> **output**

    svr_friend_list

#### 发送好友申请
> **cmd**

`chat_friend_invite`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des      |
|----------|----------|----------|
| uid      | int      | uid      |
| msg      | string   | 验证消息 |
| anti_harass_uid     | int      | 发送对象uid防骚扰检测，无检测需要就填0     |


> **output**

    svr_friend_list_inc
    svr_friend_invite_list_inc

#### 同意好友申请

> **cmd**

`chat_friend_allow`

> **main_push**

`chat_index_mgr`

> **param**

| key_name  | val_type | des       |
|-----------|----------|-----------|
| invite_id | int      | invite_id |

> **output**

    svr_friend_list_inc
    svr_friend_invite_list_inc

#### 拒绝好友申请

> **cmd**

`chat_friend_reject`

> **main_push**

`chat_index_mgr`

> **param**

| key_name  | val_type | des       |
|-----------|----------|-----------|
| invite_id | int      | invite_id |

> **output**

    svr_friend_list_inc
    svr_friend_invite_list_inc

#### 拉取好友邀请列表
> **cmd**

`chat_friend_invite_get`

> **main_push**

`chat_index_mgr`

> **param**


> **output**

    svr_friend_invite_list
    svr_group_invite_list  

####  删除好友
> **cmd**

`chat_friend_delete`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des |
|----------|----------|-----|
| uid      | int      | uid |

> **output**

    svr_friend_list_inc
    svr_friend_invite_list_inc

#### 修改备注
> **cmd**

`chat_friend_change_alias`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des    |
|----------|----------|--------|
| uid      | int      |        |
| alias    | string   | 备注名 |


> **output**

    svr_friend_list_inc
    svr_friend_invite_list_inc

#### 获取会话列表
> **cmd**

`chat_channel_list_get`

> **main_push**

`chat_index_mgr`

> **param**


> **output**

    svr_channel_list   

#### 拉取指定频道聊天内容
> **cmd**

`chat_channel_page_get`

> **main_push**

`chat_index_mgr`

> **param**


| key_name     | val_type | des            |
|--------------|----------|----------------|
| channel_id   | string   |                |
| timestamps   | string      | 为0时，表示首页 |
| msg_del_time | string      |                |
| pg_size      | int      |                |


> **output**

    svr_chat_single_channel
    svr_chat_single_channel_inc

> **notic**

    如果是拉取翻页，key1传当前数据中最旧的消息    

#### 拉取指定频道聊天内容
> **cmd**

`chat_channel_range_get`

> **main_push**

`chat_index_mgr`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| channel_id     | string   | channel_id |
| new_timestamps | string      |            |
| old_timestamps | string      |            |
| msg_del_time   | string      |            |
| pg_size        | int      |            |



> **output**

    svr_chat_single_channel
    svr_chat_single_channel_inc

> **notic**

    key1 >= key2 >= key3
    如果是拉取公共频道首页，key1,key2,key3都传0
    如果是拉取私有频道首页，key1传channel信息中最新的timestamp
    如果是拉取丢失信息，拉取的范围为 [key2,key1]中最新的，最多pg_size条

#### 发送一条消息
> **cmd**

`chat_message_send`

> **main_push**

`chat_index_mgr`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| channel_id            | string   | channel_id                              |
| timestamps            | string   | 微秒时间戳                              |
| msg_type              | int      |                                         |
| content               | string   | 若msg_type == report，格式为客户端自定义 |
| user_info             | string   | 用于反包 见proto中的ChatMsgItem         |
| is_whisper            | int      | 0: 不是，1:是                            |
| whisper_receiver_name | string   |                                         |
| content_info          | string   | 对于玩家发出的content做的额外数据记录，纯客户端使用 |
| anti_harass_uid       | int      | 发送对象uid防骚扰检测，无检测需要就填0     |


> **output**

    svr_chat_single_channel
    svr_chat_single_channel_inc

#### 翻译一条消息
> **cmd**

`chat_message_translate`

> **main_push**

`chat_index_mgr`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| channel_id     | string   |            |
| timestamps     | string   | 微秒时间戳 |
| msg_seq        | int      |            |
| target_lang_id | int      |            |

> **output**

    svr_chat_single_channel
    svr_chat_single_channel_inc

#### 更新最新已读msg seq
> **cmd**

`chat_channel_read`

> **main_push**

`chat_index_mgr`

> **param**

| key_name   | val_type | des        |
|------------|----------|------------|
| channel_id | int      | channel_id |
| timestamps | string   | 微秒时间戳 |
| msg_seq    | int      |            |

> **output**

    无

#### 修改特别关注状态
> **cmd**

`chat_channel_sp_note`

> **main_push**

`chat_index_mgr`

> **param**

| key_name   | val_type | des               |
|------------|----------|-------------------|
| channel_id | int      |                   |
| sp_node    | int      | //0 不关注，1 关注 |


> **output**

    svr_friend_list
    svr_group_list

#### 修改是否接收推送
> **cmd**

`chat_channel_noti_switch`

> **main_push**

`chat_index_mgr`

> **param**

| key_name     | val_type | des                      |
|--------------|----------|--------------------------|
| channel_id   | string   |                          |
| notic_switch | int      | //0:关闭推送  1:开启推送 |


> **output**

    svr_friend_list
    svr_group_list

#### 发起陌生人聊天
> **cmd**

`chat_create_stranger_channel`

> **main_push**

`chat_index_mgr`

> **param**

| key_name | val_type | des |
|----------|----------|-----|
| uid      | int      |     |


#### 删除陌生人聊天
> **cmd**

`chat_delete_stranger_channel`

> **main_push**

`chat_index_mgr`

> **param**

| key_name   | val_type | des |
|------------|----------|-----|
| channel_id | int      |     |

#### 同意加入群聊

> **cmd**

`chat_group_allow`

> **main_push**

`chat_index_mgr`

> **param**

| key_name  | val_type | des |
|-----------|----------|-----|
| invite_id | int      |     |

#### 拒绝加入群聊
> **cmd**

`chat_group_reject`

> **main_push**

`chat_index_mgr`

> **param**

| key_name  | val_type | des |
|-----------|----------|-----|
| invite_id | int      |     |

#### 拉取群组邀请列表 

> **cmd**

`chat_group_invite_get`

> **main_push**

`chat_index_mgr`

> **param**


> **output**

    svr_group_invite_list  

#### 全部拒绝邀请

> **cmd**

`chat_invite_reject_all`
    
> **main_push**

`chat_index_mgr`

> **param**

| key_name     | val_type | des |
|--------------|----------|-----|
| channel_type | int      |     |


#### 删除聊天

> **cmd**

`chat_channel_delete`
    
> **main_push**

`chat_index_mgr`

> **param**

| key_name   | val_type | des |
|------------|----------|-----|
| channel_id | string   |     |

### 1.15.8 关卡  v0.70

#### 派遣城市内的兵

>  **cmd**

  `dispatch_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| march_type  | int      | 参考联盟建筑 |
| target_type | int      | 14关卡       |
| target_info | object   | 参考联盟建筑 |
| march_info  | object   | 参考联盟建筑 |

---

#### 派遣城市外的兵

>  **cmd**

  `change_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| march_type  | int      | 参考联盟建筑 |
| target_type | int      | 14关卡       |
| target_info | object   | 参考联盟建筑 |
| march_info  | object   | 参考联盟建筑 |

#### 创建集结

>  **cmd**

  `create_rally_war`

> **main_push**:

  `game_server`

>  **param**:

| key_name        | val_type | des                    |
|-----------------|----------|------------------------|
| march_type      | int32    | 行军类型(rally_attack) |
| target_type     | int32    | 目标类型(14关卡)       |
| target_info     | object   | 目标信息               |
| march_info      | object   | 与派兵保持一致         |
| prepare_time    | int32    | 准备时长(单位:s)       |
| recommand_troop | array    | 推荐兵种类型           |

---

#### 开放关卡

>  **cmd**

  `op_open_barrier`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| level  | int      | 关卡等级 |
| open_time  | int      | 开放时间 |

---

#### 更换头像框

>  **cmd**

  `change_head_frame`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| id          | int      | 头像框id     |

---

#### 使用装扮道具

>  **cmd**

  `use_dress_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| item_id     | int      | 道具id     |
| type        | int      | 类型：1：主城皮肤，2：铭牌 3:头像框 4:行军队列 5队长 8迁城特效|

---

#### 装扮（头像框，主城皮肤，铭牌）

>  **cmd**

  `change_dress`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| id          | int      | 皮肤或铭牌id  |
| type        | int      | 类型：1：主城皮肤，2：铭牌 3:头像框 4:行军队列 5队长 8迁城特效|

---

#### 新手目标充值活动领奖

>  **cmd**

  `claim_multiple_target_recharge_event_goal`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des          |
|-------------|----------|--------------|
| index       | int      | 需要领奖的goal_index  |

---


### 1.15.9 城防兵  v0.70

#### 生产兵

>  **cmd**

  `city_soldier_train`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| building_svr_id | long     | 对应的城墙svr_id       |
| pos             | int      | 生产中的兵在城内的位置 |
| city_soldier_id | int      | 要训练的兵的id         |

---

#### 治疗兵

>  **cmd**

  `city_soldier_treatment`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc              |
|:----------------|:---------|:------------------|
| building_svr_id | long     | 对应的城墙svr_id  |
| city_soldier_id | object   | 士兵id            |
| num             | int      | 士兵id            |
| pos             | int      | 地图位置          |
| treatment_type  | int      | 0:重伤兵 1:濒死兵 |

---
#### 晋升兵

>  **cmd**

  `city_soldier_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type | desc                   |
|:-----------------|:---------|:-----------------------|
| city_soldier_id  | int      | 要晋升的兵的id         |
| city_soldier_num | int      | 要晋升的兵的数量       |
| building_svr_id  | long     | 生产对应的城墙svr_id   |
| pos              | int      | 生产中的兵在城内的位置 |
| target_id        | int      | 目标士兵id             |

---
#### 遣散兵

>  **cmd**

  `city_soldier_dismiss`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type | desc             |
|:-----------------|:---------|:-----------------|
| city_soldier_id  | int      | 要遣散的兵的id   |
| city_soldier_num | int      | 要遣散的兵的数量 |

---
#### 取消训练

>  **cmd**

  `city_soldier_train_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                 |
|:-------------|:---------|:---------------------|
| building_svr_id | long     | 对应的建筑           |
| train_svr_id    | long     | 训练队列对应的svr_id |

---
#### 加速训练

>  **cmd**

  `speed_up_train_city_soldier`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                                         |
|:----------------|:---------|:---------------------------------------------|
| building_svr_id | long     | 生产对应的城墙svr_id                         |
| item_id         | int      | 加速道具id                                   |
| item_num        | int      | 加速道具使用数量                             |
| is_cost_gem     | int      | 0: 消耗道具, 1: 消耗宝石                     |
| is_all          | int      | 0: 加速正在训练的队列, 1: 加速全部队列       |
| items           | object   | 非全部加速, 示例如下.客户端计算时间，用于校验 |

items
```
{
  "1(int64 svr_id)": 1(cost_time),
  ...
}
```

---
#### 取消治疗

>  **cmd**

  `city_soldier_treatment_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                 |
|:----------------|:---------|:---------------------|
| building_svr_id | long     | 生产对应的城墙svr_id |
| treat_svr_id    | long     | |

---

#### 批量领取士兵(训练/晋升/治疗)

>  **cmd**

  `batch_claim_city_soldiers`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| train_svr_id_list | array    | 训练队列svr_id列表 |
| treat_svr_id_list | array    | 治疗队列svr_id列表 |

---

### 1.16.1 城市补给站  v0.73

#### 领取每日奖励

>  **cmd**

  `earn_iap_daily_rewards`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| store_type        | int      |  |
| store_id          | int      |  |
| pid               | int      |  |

>  **output**:

svr_iap_daily_rewards

---


#### 领取所有每日奖励

>  **cmd**

  `earn_iap_daily_rewards_array`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| store_type        | int      |  |
| store_id          | int      |  |
| pid               | array    |  |

>  **output**:

svr_iap_daily_rewards

---

#### 校验道具是否充足

>  **cmd**

  `check_enough_item`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| item_id           | int      |  |
| item_num          | int      |  |

---

#### 领取建筑士兵

>  **cmd**

  `claim_building_soldiers`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| soldier_type     | int      |0：治疗；1：训练，晋升 |
| svr_building_id   | int      |建筑svr_id          |

---

#### 单个或按建筑领取将领

>  **cmd**

  `claim_building_commander`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| svr_building_id   | int      |建筑svr_id          |

---

#### 领取地块奖励

>  **cmd**

  `claim_area_reward`

> **main_push**:

  `player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| area_id           | int      |  |

---
### 1.16.2 联盟矿  v0.73

#### 激活联盟矿

>  **cmd**

  `active_al_collect`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| tar_type        | int      |  |
| tar_id          | int      |  |

---

#### 取消激活联盟矿

>  **cmd**

  `active_al_collect_cancel`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| tar_type          | int      |                    |
| tar_id            | int      |                    |

---

### 1.16.3 王国相关  v0.73

#### 拉取王国信息

>  **cmd**

  `get_kindom_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---

#### 设置税率

>  **cmd**

  `set_tax_rate`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| rate              | int      |                    |

---

#### 任命头衔

>  **cmd**

  `claim_user_kindom_titile`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| target_uid        | int      | 目标玩家 |
| kingdom_title        | int   |  王国头衔，0为取消头衔|
---

#### 拉取广播

>  **cmd**

  `msg_get_new`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|                   |           |                   |
---

#### 添加轮盘槽位内的文案

>  **cmd**

  `set_quick_speech`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|doc_list             |object       |文案id              |
---

#### 轮盘消息数据推送

>  **cmd**

  `push_quick_speech`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|doc_id             |int64     |文案id              |
|unique_id          |string     |对象id              |
|block_id           |int64     |位置id              |
|map_type           |int32     |所处地图类型 0-大地图   1-ava战场   2-pvp战场         |
|raid_id            |int64     |所处地图id  sid        ava战场id   pvp战场id           |
---

#### 领取成长基金奖励
>  **cmd**

  `claim_castle_lv_up_iap_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|claim_idx          |int       |领取的奖励的下标,从1开始    |
---

#### 添加统帅
>  **cmd**

  `add_hero_leader`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|slot          |int       |槽位id    |
|hero_id       |int       |英雄id   |
---

#### 删除统帅
>  **cmd**

  `delete_hero_leader`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|slot          |int       |槽位id    |
---

#### 展示统帅细节
>  **cmd**

  `show_hero_leader`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|show_flag          |int       |0:隐藏英雄详情 1:隐藏天赋信息 2:公开英雄详情|
---

#### 检查能否联盟邀请
>  **cmd**

  `check_al_invited`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|target_uid         |int        | |
|aid                |int        | |
---

#### 发送联盟邀请
>  **cmd**

  `send_al_invited`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|target_uid         |int        | |
|aid                |int        | |
|doc                |string     | |
---

#### 拒绝联盟邀请
>  **cmd**

  `refuse_al_invited`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|aid                |int        | |
---

#### 接受联盟邀请
>  **cmd**

  `accept_al_invited`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|aid                |int        | |
---

#### 结束争分夺秒活动
>  **cmd**

  `hurry_up_end_immediate`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|event_id           |string    | 活动id |
---

#### 开始争分夺秒活动
>  **cmd**

  `hurry_up_event_challenge_begin`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|event_id           |string    | 活动id |
---

#### 发起联盟帮助
>  **cmd**

  `al_help_apply_by_building`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|sclass           |int    | action类型 |
|building_svr_id           |int    | 建筑svr_id |
---

### 1.16.4 跨服移城相关  v0.74

#### 拉取服务器信息

>  **cmd**

  `svr_info_get`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|target_sid         |int       | 目标服的id         |

> **返包**:
  `svr_info`
---

#### 获取全部王国的信息

>  **cmd**

  `svr_get`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |
> **返包**:
  `svr_list`
---

#### 发起跨服移城

>  **cmd**

  `svr_move_city_prepare`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|target_sid         |int       | 目标服的id         |
|target_province_id |int       | 目标省的id         |
|item_id            |int       | 道具id             |
---

#### 清除跨服移城标志

>  **cmd**

  `clear_svr_move_city_flag`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |




---

#### 查看其他王国的地图

>  **cmd**

  `other_game_svr_map_get`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|target_sid         |int       | 目标省的id         |
|bid_list           |array     | 道具id             |

---

##  1.17 优化

### 1.17.1 书签功能优化  v0.75

#### 添加/更新联盟书签(添加和更新用一个cmd)

>  **cmd**

  `al_bookmark_add`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| sid      | int      | 服务器id              |
| pos_id   | int      | 位置                  |
| name     | string   | 名称                  |
| classify | int      | 标记分类              |
| wild_type | int     | 野地类型              |
| wild_key | int      | 野地key            |
| notice_time| int    | 通知时间，秒级时间戳，默认传0 |

> **返包**:
  `svr_al_bookmark_list`
---

#### 删除联盟书签

>  **cmd**

  `al_bookmark_del`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| classify | int      | 标记分类               |

> **返包**:
  `svr_al_bookmark_list`
---

#### 获取联盟书签

>  **cmd**

  `al_bookmark_get`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
|       |       |                |
> **返包**:
  `svr_al_bookmark_list`
---

### 1.17.2 序列化优化  v0.75

#### 使用iap概率宝箱道具

>  **cmd**

  `use_iap_chest_item`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| item_id      | int      | 道具id              |
| item_num   | int      | 宝箱数量                  |
---

### 1.17.3 关卡  v0.76

#### 获取关卡信息

>  **cmd**

  `op_game_svr_all_barrier`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| choice      | int      | 0：获取未被占领的关卡，1获取被占领的关卡，2获取全部关卡             |
---

### 客户端标记

#### 添加标记记录

>  **cmd**

  `client_record_add`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| record   | string   |                       |
---

#### 删除标记记录

>  **cmd**

  `client_record_delete`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| record   | string   |                       |
---


### 0.76

#### 捐献联盟科技

>  **cmd**

  `donate_al_research_batch`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | des                  |
|--------------|----------|----------------------|
| donate_type  | int      | 捐献类型，0资源，1宝石 |
| gem_num      | int      |                      |
| research_id  | int      |                      |
| donate_times | int      | 捐献次数             |
---

#### 捐献联盟技能

>  **cmd**

  `donate_al_skill_batch`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | des                  |
|--------------|----------|----------------------|
| donate_type  | int      | 捐献类型，0资源，1宝石 |
| gem_num      | int      |                      |
| skill_id     | int      |                      |
| donate_times | int      | 捐献次数             |

### 0.75

#### 开启单个联盟礼物

>  **cmd**

  `open_al_gift_new`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc                 |
|:-----------|:---------|:---------------------|
| al_gift_id | int      | 要开启的联盟礼物的id |
| type       | int      | 0：normal 1:iap      |
| al_gift_lv | int      | 联盟礼物等级         |
| 无         | 无       | 无                   |

---

#### 领取全部联盟礼物

>  **cmd**

  `open_al_gift_all_new`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| al_gift_lv | int      | 联盟礼物等级   |
| type       | int      | 1-普通 2-iap礼物   |

---

#### 升级token_item

>  **cmd**

  `upgrade_token_item`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
|:---------|:---------|:-----|
| source_id | int     | 升级前item_id|
| source_num| int     | 升级前item数量|
| target_id | int     | 升级后itemid|
---

---

#### 加速训练将领（添加）

>  **cmd**

  `speedup_train_commander_v2`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc                   |
|:------------|:---------|:-----------------------|
| building_id | int      | 用于训练将领的将领营id |
| item_id     | int      | 用于加速的道具id       |
| is_cost_gem | int      | 是否购买此道具         |
|is_all |int |是否加速全部:0: 加速正在训练的队列, 1: 加速全部队列||
|num |int |加速道具数量|
|items |object |全部加速需要, 示例如下|
|instant |int |0:原本的加速方式，1:消耗宝石一键完成|
| total_time      |int       |总的加速时间                                  |

items
```
{
  "1(svr_commander_id)": 1(cost_time),
  ...
}
```
---
#### 加速训练士兵

>  **cmd**

  `speed_up_train_soldier_v2`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                                   |
|:----------------|:---------|:---------------------------------------|
| building_svr_id | long     | 要加速的队列所在兵营的svr_id           |
| item_id         | int      | 加速道具id                             |
| item_num        | int      | 加速道具使用数量                       |
| is_cost_gem     | int      | 0: 消耗道具, 1: 消耗宝石               |
| is_all          | int      | 0: 加速正在训练的队列, 1: 加速全部队列 |
| items           | object   | 非全部加速, 示例如下                   |
|instant          |int       |0:原本的加速方式，1:消耗宝石一键完成    |
| total_time      |int       |总的加速时间                                  |
| train_svr_id    | int      | 训练队列svr_id                         |
items
```
{
  "1(int64 svr_commander_id)": 1(cost_time),
  ...
}
```
---
#### 加速训练城防兵

>  **cmd**

  `speed_up_train_city_soldier_v2`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                                         |
|:----------------|:---------|:---------------------------------------------|
| building_svr_id | long     | 生产对应的城墙svr_id                         |
| item_id         | int      | 加速道具id                                   |
| item_num        | int      | 加速道具使用数量                             |
| is_cost_gem     | int      | 0: 消耗道具, 1: 消耗宝石                     |
| is_all          | int      | 0: 加速正在训练的队列, 1: 加速全部队列       |
| items           | object   | 非全部加速, 示例如下.客户端计算时间，用于校验 |
| instant         |int       |0:原本的加速方式，1:消耗宝石一键完成          |
| total_time      |int       |总的加速时间                                  |

items
```
{
  "1(int64 svr_id)": 1(cost_time),
  ...
}
```

---
#### 添加奖励到奖励收集箱

>  **cmd**

  `op_add_reward_to_collect_box`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc |
|:----------------|:---------|:-----|
| type            | int      |      |
| id              | int      |      |
| num             | int      |      |

---
#### 领取奖励收集箱的奖励

>  **cmd**

  `claim_reward_collect_box`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
| -------- | -------- | ---- |
|          |          |      |



#### 检查省容量

>  **cmd**

  `province_num_check`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | desc |
| :---------- | :------- | :--- |
| province_id | int      | 省id |

---



#### 获取省用户导入详情

>  **cmd**

  `get_user_import_detail`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
|          |          |      |

---

#### 通关特殊副本

>  **cmd**

  `finish_special_raid`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| raid_type|  int     |  关卡类型 1:城内副本 2:远征副本    |
| hurdle   |  int     |  关卡id    |

---

#### 单次训练多队列

>  **cmd**

  `soldier_train_by_array`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| train_param |array | 要训练的项目，每个项目信息如下 |

```json
"train_param":[
    {
        "svr_building_id":num,	// 此项训练所在的兵营建筑svr_id
        "soldier_id":num,		// 要训练的士兵id
        "soldier_num":num,		// 要训练的士兵数量
        "pos":-2,				// 士兵不占据城内位置, 现无用
    }
]
```

-----

### 0.80

---

#### 联盟研究宝石资源混合捐献

>  **cmd**

  `donate_al_research_batch_mix`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc                                         |
|----------|----------|----------------------------------------------|
| research_id | int      | 技能id                                       |
| gem_num  | int      | 消耗的宝石数量                               |
| donate   | array    | 捐献列表 [0,1,1,1,0...] 捐献类型，0资源，1宝石 |

---

---

#### 联盟技能宝石资源混合捐献

>  **cmd**

  `donate_al_skill_batch_mix`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc                                         |
|----------|----------|----------------------------------------------|
| skill_id | int      | 技能id                                       |
| gem_num  | int      | 消耗的宝石数量                               |
| donate   | array    | 捐献列表 [0,1,1,1,0...] 捐献类型，0资源，1宝石 |

---
#### 单次晋升多队列

>  **cmd**

  `soldier_upgrade_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| upgrade_param   | array    | [{"svr_building_id":1,"pos":1,"soldier_id":1,"soldier_num":1,"target_id":1}] |
---
#### 单次治疗多队列

>  **cmd**

  `soldier_treatment_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| treat_param   | array    | [{"svr_building_id":1,"pos":1,"soldier_id":1,"soldier_num":1}] |
---

#### 记录探索时间

>  **cmd**

  `scout_record_time`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
| -------- | -------- | ---- |
|          |          |      |




---

#### 拉取记录的探索时间

>  **cmd**

  `get_scout_record_time`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
| -------- | -------- | ---- |
|          |          |      |

---
#### 单次治疗多城防队列

>  **cmd**

  `city_soldier_treatment_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| data   | array    | [{"svr_building_id":1,"pos":1,"city_soldier_num":1,"city_soldier_id":1}] |
---
#### 单次训练城防多队列

>  **cmd**

  `city_soldier_train_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| train_param   | array    | [{"svr_building_id":1,"pos":1,"city_soldier_id":1}] |
---
#### 单次晋升城防多队列

>  **cmd**

  `city_soldier_upgrade_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| data   | array    | [{"svr_building_id":1,"pos":1,"city_soldier_id":1,"city_soldier_num":1,"target_id":1}] |
---
#### 单次训练将领多队列

>  **cmd**

  `train_commander_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| train_param   | array    | [{"svr_building_id":1,"pos":1,"lv":1}] |
---
#### 单次生产token多队列

>  **cmd**

  `token_produce_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                   |
|:----------------|:---------|:-----------------------|
| produce_param   | array    | [{"svr_building_id":1,"item_id":1,"item_num":1}] |
---

#### 连续建造建筑 (参数可以参考 1.5.2中的construct_building)

>  **cmd**

  `construct_building_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name      | val_type | desc     |
|:--------------|:---------|:---------|
| building_list | array    | 参数说明\[{"building_type":int,"lv":int,"pos":int\}]|

---


#### 开启token宝箱

>  **cmd**

  `open_token_chest`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc                                         |
|----------|----------|----------------------------------------------|
| castle_lv      | int      | 开启时的主城等级                       |
| id             | int      | 箱子id                                 |
| reward_index   | int      | 奖励下标                               |

---

#### 批量取消士兵治疗(参数可以参考soldier_treatment_cancel)

>  **cmd**

`soldier_treatment_cancel_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| cancel_list   | object      | \{"building_svr_id":\[svr_id_1, svr_id_2\]\} |

---

#### 批量取消城防兵治疗(参数可以参考city_soldier_treatment_cancel)

>  **cmd**

  `city_soldier_treatment_cancel_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name        | val_type | desc                 |
|:----------------|:---------|:---------------------|
| cancel_list | object     | \{"building_svr_id":\[treat_svr_id_1, treat_svr_id_2\]\} |

---

#### 批量取消城防兵训练或晋升(参数可以参考city_soldier_train_cancel)

>  **cmd**

  `city_soldier_train_cancel_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                 |
|:-------------|:---------|:---------------------|
| cancel_list    | object     | \{"building_svr_id":\[train_svr_id_1, train_svr_id_2\]\} |

---

#### 批量取消训练或晋升

>  **cmd**

  `soldier_train_cancel_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                 |
|:-------------|:---------|:---------------------|
| train_svr_id_list    | array     | [1,2,3] |
| svr_building_id    | int     | "svr_building_id":1 |

---

#### 批量取消将领训练

>  **cmd**

  `cancel_train_commander_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                 |
|:-------------|:---------|:---------------------|
| train_svr_id_list    | array     | [1,2,3] |
| svr_building_id    | int     | "svr_building_id":1 |

---

#### 批量取消token生产

>  **cmd**

  `token_produce_cancel_by_array`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc                 |
|:-------------|:---------|:---------------------|
| produce_svr_id_list    | array     | [1,2,3] |
| svr_building_id    | int     | "svr_building_id":1 |

---

#### 开启并添加资源自选奖励宝箱

>  **cmd**

  `add_resource_select_reward_chest`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| chest_id   | int      | 宝箱id       |
| chest_num  | int      | 宝箱数量     |
| select_idx | int      | 目标奖励下标 |

---

#### 更换个人旗帜

>  **cmd**

  `player_flag_change`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| flag_id   | int      | 旗帜id       |

---

#### 将领宝箱开箱

>  **cmd**

  `open_commander_chest`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| level      | int      | 宝箱阶级       |
| num        | int      | 开箱次数       |
| pos_list   | array    | 对应pos       |

---

#### 帝国蓝图快速挂机

>  **cmd**

  `empire_blueprint_quick_produce`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| is_cost_gem |int      | 是否消耗宝石（0：否，1：是） |

---
---
# ME2

## 0.10

### 建筑

#### 建造建筑

>  **cmd**

  `construct_building_new`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_type | int      | 建筑类型 |
| pos           | int      | 建筑坐标 |
| lv           | int      | 建筑等级 |
| instant           | int      | 1立即完成，0普通完成 |
| instant_gem           | int      | 立即完成所需宝石数量 |

---

#### 升级建筑

>  **cmd**

  `building_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_svr_id | int      | 建筑唯一id |
| lv           | int      | 目标等级 |
| instant           | int      | 1立即完成，0普通完成 |
| instant_gem           | int      | 立即完成所需宝石数量 |

---
#### 取消升级建筑

>  **cmd**

  `building_upgrade_cancel`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_svr_id | int      | 建筑唯一id |

---
#### 建筑加速

>  **cmd**

  `building_speed_up`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_svr_id | int      | 建筑唯一id |
| speed_up_type           | int      | 1消耗宝石，2消耗道具 |
| item_id           | int      | 道具id |
| item_num           | int      | 道具数量 |
| cost_gem           | int      | 消耗宝石时,所需宝石数量 |

---

#### 建筑第二队列道具兑换

>  **cmd**

  `exchange_invalid_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| type     | int      | global type |
| id       | int      | id          |
| num      | int      | 数量        |

---

#### 收集所有单种类资源地的资源
>  **cmd**

  `collect_resource_by_building_type`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| building_type     | int      | 建筑类型 |

---

#### 选择紧急治疗队列
>  **cmd**

  `select_emergency_treatment`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| svr_builingd_id     | int      |  |
| svr_list     | array      | [1,1,1,1,....] |

---

#### 加速紧急治疗队列
>  **cmd**

  `speed_up_emergency_treatment`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| svr_builingd_id     | int      |  |
| item_id         | int      | 加速道具id                                   |
| item_num        | int      | 加速道具使用数量                             |
| is_cost_gem     | int      | 0: 消耗道具, 1: 消耗宝石                     |
| items           | object   | 非全部加速, 示例如下.客户端计算时间，用于校验  |
| instant         |int       |0:原本的加速方式，1:消耗宝石一键完成           |
| total_time      |int       |总的加速时间                                 |

---

---

#### 拉取某个省的头衔信息
>  **cmd**

  `get_title_info_by_province_id`

> **main_push**:

  `game_serever`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| province_id     | int      | 省id |

---

#### 任命某个省的头衔
>  **cmd**

  `appoint_title_by_province_id`

> **main_push**:

  `game_serever`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| province_id     | int      | 省id |
| target_uid     | int      | 被任命的玩家uid |
| title     | int      | 被任命的头衔,0为取消头衔 |

---

#### 更换盟主
>  **cmd**

  `al_chancellor_change`

> **main_push**:

  `game_serever`

>  **param**:

| key_name | val_type | des         |
|----------|----------|-------------|
| target_uid     | int      | 目标玩家uid |

---

#### 派遣城市外的部队去采集

>  **cmd**

  `change_collect_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                          |
| ----------- | -------- | ------------------------------------------------------------ |
| march_type  | int      | 行军类型(4: 采集资源地, 5:回城)                              |
| target_type | int      | 目标类型(50:地脉)                                            |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}             |
| march_info  | object   | 行军信息 {"ids":[unique_id(string)], "over_defend":true},默认不驻扎，直接回城 |

#### 派遣城市内的部队去采集

>  **cmd**

  `dispatch_collect_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                          |
| ----------- | -------- | ------------------------------------------------------------ |
| march_type  | int      | 行军类型(4: 采集资源地, 5:回城)                              |
| target_type | int      | 目标类型(50:地脉)                                            |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}             |
| march_info  | object   | 行军携带的军队信息 {"soldier":{"1":100},"commander":{"1":{"3":1}},"hero":{"main":10,"vice":8}} |



#### 攻击地脉

>  **cmd**

  `dispatch_troop`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                          |
| ----------- | -------- | ------------------------------------------------------------ |
| march_type  | int      | 行军类型(3:攻击资源地)                                       |
| target_type | int      | 目标类型(50:地脉)                                            |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}             |
| march_info  | object   | 行军携带的军队信息 {"soldier":{"1":100},"commander":{"1":{"3":1}},"hero":{"main":10,"vice":8}} |





#### 攻击地脉

>  **cmd**

  `change_troop`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                          |
| ----------- | -------- | ------------------------------------------------------------ |
| march_type  | int      | 行军类型(3:攻击资源地)                                       |
| target_type | int      | 目标类型(50:地脉)                                            |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}             |
| march_info  | object   | 行军信息 {"id":[unique_id(string)], "over_defend":true},默认不驻扎，直接回城 |

---

#### 代金卷充值
>  **cmd**

  `gem_recharge_by_voucher`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| recharge_type | int      | 参照充值参数 |
| recharge_info | object   | 参照充值参数 |
| purchase_info | object   | 参照充值参数 |
| item_id       | int      | 代金卷道具id |

---

#### 治疗加速
>  **cmd**

  `speed_up_treatment`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des                                |
|-----------------|----------|------------------------------------|
| svr_building_id | int      | 要加速的队列所在医院的svr_id |
| instant         | int      | 是否是一键完成 0: 否 1 是          |
| total_time      | int      | 一键完成时需要的时间               |
| is_all          | int      | 0: 单队列， 1: 全部队列             |
| cost_type       | int      | 消耗类型: 0 道具，1宝石             |
| item_id         | int      | 道具id                             |
| item_num        | int      | 道具数量                           |
| gem_num         | int      | 当消耗宝石时，需要传入，用于校验数据 |
| items         | object      | 非全部加速, 示例如下.客户端计算时间，用于校验 |

---

#### 士兵复活


>  **cmd**

  `soldier_revive_immediately`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des                                       |
|--------------|----------|-------------------------------------------|
| revive_type  | int      | 1. 立即复活, 2. 普通复活                  |
| cost_type    | int      | 消耗类型: 0 道具，1宝石                    |
| item_id      | int      | 道具id                                    |
| item_num     | int      | 道具数量                                  |
| gem_num      | int      | 当消耗宝石时，需要传入，用于校验数据        |
| soldier_list | object   | { "1": 1, ....}  key： 士兵类型， val： 数量 |

---

#### 士兵取消复活队列

>  **cmd**

  `soldier_revive_cancel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                    |
|----------|----------|------------------------|
| list     | array    | [1, 2, ...] 队列id列表  |

---

#### 治疗加速
>  **cmd**

  `speed_up_city_soldier_treatment`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des                                |
|-----------------|----------|------------------------------------|
| svr_building_id | int      |                                    |
| instant         | int      | 是否是一键完成 0: 否 1 是          |
| total_time      | int      | 一键完成时需要的时间               |
| is_all          | int      | 0: 单队列， 1: 全部队列             |
| is_cost_gem       | int      | 消耗类型: 0 道具，1宝石             |
| item_id         | int      | 道具id                             |
| item_num        | int      | 道具数量                           |
| items         | object      | 非全部加速, 示例如下.客户端计算时间，用于校验 |

---

## 0.80

### 建筑

#### 免费加速

>  **cmd**

  `building_free_speed_up`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_svr_id | int      | 建筑唯一id |

---

#### 天赋设置

> **cmd**

  `hero_talent_upgrade_set`

> **main_push**:

  `player`

> **param**:

| key_name | val_type | desc   |
|:---------|:---------|:-------|
| hero_id  | int      | 英雄id |
| index    | int      | 预设页 |
| list     | obj    |  {"4001": 1, ...}   key:天赋id, val: 目标等级 |

## 1.20

#### 派遣城市内的兵

>  **cmd**

  `dispatch_troop`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| march_type  | int      | 行军类型(3:攻击地脉(攻打地脉中的npc) 16:攻击地脉中的守军 )                                 |
| target_type | int      | 目标类型(50地脉)|
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                                               |
| march_info  | object   | 行军携带的军队信息 {"soldier":{"1":100},"commander":{"1":{"3":1}},"hero":{"main":10,"vice":8}} |

---

#### 派遣城市外的兵

>  **cmd**

  `change_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                         |
|-------------|----------|-----------------------------------------------------------------------------|
| march_type  | int      | 行军类型(3:攻击地脉(攻打地脉中的npc) 16:攻击地脉中的守军 )      |
| target_type | int      | 目标类型(50地脉)          |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                            |
| march_info  | object   | 行军信息 {"id":[unique_id(string)], "over_defend":true},默认不驻扎，直接回城 |

---

#### 派遣城市内的兵

>  **cmd**

  `dispatch_troop`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                         |
|-------------|----------|-----------------------------------------------------------------------------|
| march_type  | int      | 行军类型(3:攻击地脉(攻打地脉中的npc) 16:攻击地脉中的守军 )      |
| target_type | int      | 目标类型(50地脉)          |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                            |
| march_info  | object   | 行军信息 {"id":[unique_id(string)], "over_defend":true},默认不驻扎，直接回城 |

---

# 派遣斥候

>  **cmd**

  `dispatch_scout`

> **main_push**:

  `ds_player`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| scout_queue_id | int      | 斥候id                                                                    |
| tar_pos        | int64    | 目的地坐标                                                                |
| tar_type       | int64    | 斥候行动类型 13：侦查地脉守军 |
| tar_limit		    | array 	| 如果tar_type是迷雾的话，该字段应该存在并且表示 想要探索地图块的左上与右下坐标 |
| tar_info		    | object 	|{"type":int32, "id":int64} |
| need_camp	| int32 	|是否驻扎 0: 不驻扎  1:驻扎 |

---

# 清除某个省全部迷雾

>  **cmd**

  `op_clear_province_fog`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| province_id | int      | 省id                                                                    |
| num        | int64    | 盟友视野的迷雾块数                                                                |
| force       | int64    | 跳过校验清除迷雾 |
---

# 根据unique id拉取某个obj的信息，返包同搜索功能

>  **cmd**

  `get_obj_by_unique_id`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| unique_id | string      |                                                                     |


#### 根据场景id拉取iap信息（批量拉取神秘商店iap礼包信息）

>  **cmd**

`get_special_promote_by_scene_list`

> **main_push**:

`player`

>  **param**:

|  key_name  | val_type |         desc        |
|------------|----------|---------------------|
| scene_id   | array    |     pid_list        |
| extra      | object    |     {"svr_ctime":int, "user_ctime":int, "castle_lv":int, "trigger_id": [int], "has_second_building_queue":int}        |


#### 领取新手任务进度奖励

>  **cmd**

`claim_new_player_quest_progress`

> **main_push**:

`ds_player`

>  **param**:

|  key_name  | val_type |         desc        |
|------------|----------|---------------------|
| claim_stage| int      |     完成任务数量    |
| claim_type | int      | 1:普通 2:vip 3:都要 |



# 开启联盟陷阱

>  **cmd**

  `set_boss_trap_start`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| level | int      | 等级                                                                   |
| diff        | int64    | 难度                                                                |
| time       | int64    | time:0 手动模式 否则自动模式 |
| trap_idx   | int32     | 第几个陷阱 | 

# 获取联盟陷阱排行信息

>  **cmd**

  `get_boss_trap_rank`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |

### 1.2.2

#### 使用王国技能
>  **cmd**

  `use_kingdom_skill`

> **main_push**:

  `game_server`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| skill_id | int      | 王国技能id  |

---



#### 激活恶魔入侵活动

>  **cmd**

  `active_demon_exorcist`

> **main_push**:

  `game_server`

>  **param**:

| key_name      | val_type | des        |
| ------------- | -------- | ---------- |
| event_id      | string   | 活动id     |
| difficulty_lv | int      | 等级(难度) |

---

#### 预约激活恶魔入侵活动

>  **cmd**

  `order_demon_exorcist`

> **main_push**:

  `game_server`

>  **param**:

| key_name      | val_type | des        |
| ------------- | -------- | ---------- |
| event_id      | string   | 活动id     |
| difficulty_lv | int      | 等级(难度) |
| time          | int64    | 预约时间   |

---


#### 获取自己联盟成员

>  **cmd**

  `get_self_al_member`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---


#### 获取其他联盟成员

>  **cmd**

  `get_other_al_member`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name      | val_type | des          |
| ------------- | -------- | ----------   |
|     aid       |   int64  | 目标联盟的aid |

---

### 体系版本

#### 攻打消灭情报

>  **cmd**

  `attack_barbarian_intel`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| march_type  | int      | 行军类型(2:攻击)                                 |
| target_type | int      | 目标类型(x:消灭情报 y:营救情报 z:探索情报)         |
| target_info | object   | {"id":string unique_id, "pos":string 目标的位置}                                               |
| march_info  | object   | 行军携带的军队信息 {"soldier":{"1":100},"commander":{"1":{"3":1}},"hero":{"main":10,"vice":8}} |


#### 对探索情报进行探索

>  **cmd**

  `explore_intel`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| unique_id  | string      |        情报id                         |

#### 开始情报探索

>  **cmd**

  `explore_intel_begin`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| unique_id  | string      |        情报id                         |

#### 完成情报探索

>  **cmd**

  `explore_intel_finish`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| unique_id  | string      |        情报id                         |

#### 派遣斥候前往营救情报

>  **cmd**

  `dispatch_scout`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| scout_queue_id | int      | 斥候id                                                                    |
| tar_pos        | int64    | 目的地坐标                                                                |
| tar_type       | int64    | 斥候行动类型 14:营救情报 |
| tar_limit		    | array 	| 如果tar_type是迷雾的话，该字段应该存在并且表示 想要探索地图块的左上与右下坐标 |
| tar_info		    | object 	|{"type":int32, "id":int64} |
| need_camp	| int32 	|是否驻扎 0: 不驻扎  1:驻扎 |

#### 领取情报奖励

>  **cmd**

  `claim_intel_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| intel_type     | int      | 情报类型      0:征伐 1:收集 2:普通                                        |
| svr_intel_id   | int64    | 后台情报id                                                                |


#### 领取固定惊喜奖励

>  **cmd**

  `claim_radar_regular_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

#### 刷新某类型情报

>  **cmd**

  `op_refresh_intel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| intel_type     | int      | 情报类型      0:征伐 1:收集 2:普通                                        |

#### 提升实力等级

>  **cmd**

  `radar_strength_level_up`

> **main_push**:

  `ds_player`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| target_lv     | int      | 目标等级                                        |





####  堡垒活动-获取堡垒的信息
>  **cmd**

  `get_fort_event_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| event_id       | string   | 活动唯一标识符                                                  |

> **desc**:
	打开活动界面、元素之域 向后台请求
	返包 svr_fort_event_info 、svr_fort_season_info 、svr_fort_al_info


####  堡垒活动-获取堡垒活动的排名信息
>  **cmd**

  `get_fort_rank_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| event_id       | string   | 活动唯一标识符                                                  |
> **desc**:
	返包 svr_fort_rank_info

####  堡垒活动-获取堡垒活动的配置
>  **cmd**

  `get_fort_project_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |
> **desc**:
	仅当客户当没有数据或者event_id、版本号发生变化，需要向后台发送请求
	返包 svr_fort_proj_info 、svr_fort_event_info 、svr_fort_season_info 、svr_fort_al_info

####  堡垒活动-报名投票
>  **cmd**

  `set_fort_sign`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| event_id       | string   | 活动唯一标识符                                                  |
| id             | int64    | 堡垒id                                                          |
| sign_time      | array    | 报名时间                                                        |

#### 获取跨省移城消耗道具数量

>  **cmd**

  `get_move_city_cost`

> **main_push**:

  `game_server`

>  **param**:

| key_name       | val_type | des                                                                       |
|----------------|----------|---------------------------------------------------------------------------|
| tar_pos     | int      | 坐标信息（后台坐标）                                        |

#### 定点移城

>  **cmd**

  `fixed_move_city`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                            |
|----------|----------|--------------------------------|
| tar_pos  | int      | 坐标信息（后台坐标）             |
| use_gem  | int      | 是否使用金币购买道具           |
| item_id  | int      | 道具id(根据道具id确定移城类型) |
| item_num  | int      | 道具数量                      |


### 探索

#### 探索区域

>  **cmd**

  `explore_area`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| area_id  | int      | 区域id                                 |
| troop_info | object      | 副本信息         |

```json
{
    "troop_info":{
        "pos":{
            "soldier":{
                "id":num
            },
            "hero":{
                "vice":[]
            },
            "dir":num,
			"default_pos":num,(默认位置)
           "carry_lord":0(不携带)/1(携带)
        }
    },
    "area_id":num
}
```



#### 退出探索

>  **cmd**

  `explore_exit`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| area_id  | int      | 区域id                                 |


#### 军队特殊移动

>  **cmd**

  `raid_change_troop_special`

> **main_push**:

  `raid_server`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| march_type  | int      | 行军类型(1:救援)                                |
| march_id  | string      | 操作的unique_id                                |


#### 副本移除障碍物

>  **cmd**

  `raid_obstacle_remove`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |


#### 副本救援

>  **cmd**

  `raid_finish_rescue_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |


#### 副本rpg副本

>  **cmd**

  `raid_finish_rpg_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| hero_list  | array      | 攻打rpg副本英雄列表                                |



#### 副本心跳

>  **cmd**

  `raid_heart_beat`

> **main_push**:

  `raid_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |


#### 探索宝箱领取

>  **cmd**

  `explore_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| area_id  | int      | 区域id                                 |


#### 区域收复

>  **cmd**

  `recover_area`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| area_id  | int      | 区域id                                 |


#### 副本内移动军队

>  **cmd**

  `change_raid_troop_target`

> **main_push**:

  `raid_server`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| march_id  | string      | 军队的unique_id                             |
| march_time  | int      | 区域id                                 |
| target_id  | string      | 目标的unique_id                                 |
| target_pos  | int      | 目标位置                                 |
| target_type  | int      | 目标类型                                |


#### 副本战胜野蛮人

>  **cmd**

  `finish_barbarion_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| hero_list  | array      | 攻打rpg副本英雄列表                                |


#### 副本战胜野蛮人

>  **cmd**

  `claim_obstacle_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |


#### 探索远征(重置进入)

>  **cmd**

  `explore_expedition`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| chapter | int      | 关卡                                |
| troop_info  | obj      | 军队信息(参考explore_area)                        |

#### 探索远征

>  **cmd**

  `explore_exist_expedition`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |
#### 退出远征

>  **cmd**

  `exit_expedition`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                     |
| -------- | -------- | ----------------------- |
| is_fail  | int      | 是否是战败时退出(1：是) |


#### 远征进入下一张地图

>  **cmd**

  `enter_expedition_next_map`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
|born_pos |string| 下一张地图的出生点|

#### 重新挑战本张地图

>  **cmd**

  `enter_expedition_cur_map`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |
#### 远征祝福选择

>  **cmd**

  `choose_expedition_blessing`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| blessing_id | int      | 选择的祝福id                              |


#### 开启远征宝箱

>  **cmd**

  `open_expedition_treasure`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |


#### 远征rpg副本完成

>  **cmd**

  `expedition_finish_rpg_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| hero_list  | array      | 英雄列表                                |

#### 远征救援副本完成

>  **cmd**

  `expedition_finish_rescue_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |

#### 远征治疗建筑完成

> **cmd**

`expedition_finish_treat`

> **main_push**:

  `ds_player`

> **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| building_id | int      | 建筑id |

#### 远征高级障碍物修复

> **cmd**

`expedition_repair_building`

> **main_push**:

  `ds_player`

> **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| building_id | int      | 建筑id |

#### 远征领取副本通关奖励

> **cmd**

`award_expedition_reward`

> **main_push**:

  `ds_player`

> **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |
#### 士兵立即训练

>  **cmd**

  `soldier_train_immediately`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                            |
|----------|----------|--------------------------------|
| gem_num          | int | 客户端计算的所需宝石数      |
| soldier_list     | int | 训练信息       {"soldier_id":1,"soldier_num":100}             |
| svr_building_id  | int | 建筑id|                     |
| train_type       | int | 可选参数，旧版本客户端没有此参数，新版客户端此参数为1，表示立即完成不计算资源|

#### 士兵立即训练

>  **cmd**

  `soldier_upgrade_immediately`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                            |
|----------|----------|--------------------------------|
| gem_num          | int | 客户端计算的所需宝石数      |
| soldier_list     | int | 训练信息                    |
| svr_building_id  | int | 建筑id|                     |
| train_type       | int | 可选参数，旧版本客户端没有此参数，新版客户端此参数为1，表示立即完成不计算资源|

#### 改建资源建筑

>  **cmd**

  `building_change`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc                 |
| :-------------- | :------- | :------------------- |
| building_svr_id | int      | 建筑唯一id           |
| building_type   | int      | 目标资源建筑         |
| instant         | int      | 1立即完成，0普通完成 |
| instant_gem     | int      | 立即完成所需宝石数量 |

---

#### 取消改建资源建筑

>  **cmd**

  `building_change_cancel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| building_svr_id | int      | 建筑唯一id |

#### rpg远征副本完成

>  **cmd**

  `rpg_expedition_finish`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc          |
| :--------- | :------- | :------------ |
| menu_id    | int      | rpg远征章节id |
| chapter_id | int      | rpg远征关卡id |
| hero_list  | array    | 英雄列表      |

#### 移除资源或战争建筑

>  **cmd**

  `building_remove`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc                 |
| :-------------- | :------- | :------------------- |
| building_svr_id | int      | 建筑唯一id           |
| instant         | int      | 1立即完成，0普通完成 |
| instant_gem     | int      | 立即完成所需宝石数量 |

---

#### 取消移除建筑

>  **cmd**

  `building_remove_cancel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| building_svr_id | int      | 建筑唯一id |

---

#### 使用加速道具

>  **cmd**

  `use_troop_speed_up_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| unique_id | string    | 目标的unique_id |
| item_id | int      | 道具id |
| item_num | int      | 道具数量 |
| cost_type | int      | 使用方式(0:道具1:宝石) |


---

#### 使用召回道具

>  **cmd**

  `use_troop_return_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| unique_id | string    | 目标的unique_id |
| item_id | int      | 道具id |
| item_num | int      | 道具数量 |
| cost_type | int      | 使用方式(0:道具1:宝石) |

---

#### 判断目标坐标是否可以到达

>  **cmd**

  `can_pos_arrive`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| tar_pos | int      | 坐标信息（后台坐标）             |
| size    | int      | 直径            |

---

#### 宝石镶嵌

>  **cmd**

  `crystal_mount`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| crystal_id | int      | 宝石id             |
| equip_id    | int      | 装备id            |
| index    | int      | 索引            |

---


#### 宝石拆除

>  **cmd**

  `crystal_unmount`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| equip_id | int      | 装备id             |
| index    | int      | 索引            |
| item_id    | int      | 0:直接删除宝石,其它拆除使用的物品id            |
| use_gem    | int      | 0:不使用金钱 1:使用金钱            |
---

#### 宝石合成

>  **cmd**

  `crystal_compose`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| crystal_id | int      | 宝石id             |
| num    | int      | 数量            |
---

#### 宝石分解

>  **cmd**

  `crystal_decompose`

> **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | desc       |
| :-------------- | :------- | :--------- |
| crystal_id | int      | 宝石id             |
| num    | int      | 数量            |
---


#### 远征副本领取每日奖励

>  **cmd**

  `claim_expedition_daily_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |
#### 遣返防守队列

>  **cmd**

  `alliance_troop_return`

> **main_push**:

  `game_server`

>  **param**:

| key_name    | val_type | des                                                                         |
|-------------|----------|-----------------------------------------------------------------------------|
| id          | string   | 队长队列unique_id      |
| src_unique_id| string   | 圣地或者联盟建筑id      |

#### 英雄一键升级使用物品

>  **cmd**

  `hero_item_use_by_array`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| hero_id     | int      | 英雄id |
| item_array  | array    | 使用的物品数组 |
| token_array  | array    | 使用的token数组 |


```Json
"item_array":[
	{
		"id":id,    // 物品id
		"num":num   // 物品数量
	},
	...
]
```

#### 进入远征

>  **cmd**

  `enter_new_expedition`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des         |
| ---------- | -------- | ----------- |
| hero_list  | array    | 英雄id_list |
| chapter_id | int      | 关卡id      |
| menu_id    | int      | 章节id      |

#### 新远征完成rpg战斗组件

>  **cmd**

  `finish_new_expedition_rpg_assembly`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                         |
| ----------- | -------- | ------------------------------------------- |
| hero_infos  | array    | 英雄信息([[int,int,int],...])               |
| assembly_id | int      | 组件id                                      |
| cur_index   | int      | 可选参数，当前在关卡内的第几层，不传默认为0 |

```json
{
    hero_infos:[[int(id),int(life),int(energy)]],
    assembly_id:int
}
```



#### 新远征完成商店组件

>  **cmd**

  `finish_new_expedition_shop_assembly`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                         |
| ----------- | -------- | ------------------------------------------- |
| assembly_id | int      | 组件id                                      |
| cur_index   | int      | 可选参数，当前在关卡内的第几层，不传默认为0 |

#### 新远征完成获得道具组件

>  **cmd**

  `finish_new_expedition_item_assembly`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                |
| ---------- | -------- | ---------------------------------- |
| assembly_id | int | 组件id |
| cur_index | int | 可选参数，当前在关卡内的第几层，不传默认为0 |

#### 新远征完成回血组件

>  **cmd**

  `finish_new_expedition_treat_assembly`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                |
| ---------- | -------- | ---------------------------------- |
| hero_list | array    | 英雄id_list |
| assembly_id | int      | 组件id |
| cur_index | int | 可选参数，当前在关卡内的第几层，不传默认为0 |

#### 新远征商店购买商品

>  **cmd**

  `new_expedition_shop_buy`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                |
| ---------- | -------- | ---------------------------------- |
| goods_id | int      | 商品id |
| goods_num | int      | 购买数量 |
#### 远征退出远征

>  **cmd**

  `exit_new_expedition`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                |
| ---------- | -------- | ---------------------------------- |
| reason | int    | 原因(0：通关,1：挑战失败,2：主动放弃) |

#### 开始雷达远征RPG情报

>  **cmd**

  `expedition_intel_begin`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| unique_id   | string   | 情报实体唯一id |

#### 雷达远征RPG情报完成

>  **cmd**

  `expedition_intel_finish`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| unique_id   | string   | 情报实体唯一id |
| is_win   	  | int      | 0:输了 1:赢了  |
| is_abandoned| int      | 0:没放弃 1:放弃了 |


#### 城内采集开始

>  **cmd**

  `city_collect_start`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| svr_building_id    | int   | 后台资源地id/建筑id |
| is_guide    | int   | 是否为指引，1为指引，0为非指引 |

#### 城内采集领取

>  **cmd**

  `city_collect_receive`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| svr_building_id    | int   | 后台资源地id/建筑id |


#### 城内采集取消

>  **cmd**

  `city_collect_cancel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des    |
| ----------- | -------- | ------ |
| svr_building_id    | int   | 后台资源地id/建筑id |


#### 城内新采集开始

>  **cmd**

  `city_collect_start_new`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name             | val_type | des                |
| -------------------- | -------- | ------------------ |
| svr_building_id_list | array    | 资源地后台id的数组 |

#### 获取城内临时自动采集的报告

>  **cmd**

  `get_city_collect_report`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

#### 领取章节奖励

>  **cmd**

  `claim_chapter_end`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| chapter_id | int | 章节id|



#### Token商店购买物品

>  **cmd**

  `token_shop_buy`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                  |
| ---------- | -------- | ------------------------------------ |
| type       | int      | 0-固定槽位，1-非固定槽位，2-特权槽位 |
| index      | int      | 槽位id                               |
| version    | int      | 商店版本                             |
| token_type | int      | token类型                            |
| num        | int      | 购买数量                            |

#### Token商店刷新

>  **cmd**

  `token_shop_refresh`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des       |
| ---------- | -------- | --------- |
| version    | int      | 商店版本  |
| token_type | int      | token类型 |


#### 获取监狱信息

>  **cmd**

  `get_prison_info`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name             | val_type | des                |
| -------------------- | -------- | ------------------ |
| uid                  | int64    |  想要查看的uid      |


#### 结束练兵并领取

>  **cmd**

  `end_train_soldier`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name             | val_type | des                |
| -------------------- | -------- | ------------------ |
| building_svr_id      | int64    |  要加速的队列所在兵营的svr_id            |
| instant              | int64    |  是否立即完成      |
| is_all               | int64    |  加速正在训练的队列:0|加速全部队列:1     |
| is_cost_gem          | int64    |  消耗道具:0|消耗宝石:1                   |
| item_id              | int64    |  加速道具id        |
| item_num             | int64    |  加速道具使用数量  |
| items                | object   |  非全部加速        |
| total_time           | int64    |  总时间            |
| train_svr_id         | int64    |  训练队列svr_id    |



---

#### 领取生产的token

>  **cmd**

  `claim_token`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des      |
| ----------  | -------- | -------- |
| building_id | int      | token生产建筑后台id |



#### 熔炉开始生成装备材料

>  **cmd**

  `furnace_produce`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name        | val_type | des                |
| --------------- | -------- | ------------------ |
| material_id     | int      | 生成的装备材料id   |



#### 取消所有的装备材料生成

>  **cmd**

  `furnace_produce_cancel`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |



#### 领取所有生成完的装备材料

>  **cmd**

  `furnace_produce_claim`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |



#### 熔炉升级/修复/第一次打开

>  **cmd**

  `furnace_upgrade`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

#### 设置锻造材料状态

>  **cmd**

  `set_material_state`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des      |
| -------- | -------- | -------- |
| type     | int      | 材料type |

#### 激活锻造材料

>  **cmd**

  `material_activated`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des      |
| -------- | -------- | -------- |
| type     | int      | 材料type |

#### 通用道具兑换

>  **cmd**

  `hero_skillupgrade_item_transform`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name |    val_type          | des      |
| -------- |      --------         | -------- |
| hero_id           | int      | 英雄id |
| cost_item_id      | int      | 消耗item_id |
| exchange_count     | int     | 兑换数量 |

#### 新搜索对象

>  **cmd**

  `search_obj_new`

>  **main_push**:

  `game_server`

>  **param**:

| key_name |    val_type          | des      |
| -------- |      --------         | -------- |
| type     | int      | 类型 |
| level    | int      | 等级 |
| extra_value  | array[int]     | 自定义参数,搜索野蛮人时,第一个参数为野蛮人时代 |

#### 新英雄升级技能

>  **cmd**

`hero_skill_upgrade_new`

> **main_push**:

`player`

>  **param**:

| key_name  | val_type | desc                   |
| :-------- | :------- | :--------------------- |
| hero_id   | int      | 英雄id                 |
| skill_id  | int      | 指定的技能id           |
| target_lv | int      | 传入客户端的下一级即可 |



#### 星器抽取

>  **cmd**

  `treasure_lottery`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                                                |
| -------- | -------- | -------------------------------------------------- |
| id       | int      | 抽取的奖池id（6：普通奖池抽取，7-9：限时奖池抽取） |
| num      | int      | 抽取次数                                           |
| gem_num  | int      | 花费的宝石数量                                     |
| type     | int      | 抽取类型（1：免费次数抽取，2：道具或宝石抽取）     |

#### 碎片合成星器

>  **cmd**

  `treasure_piece_compound`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                |
| ----------- | -------- | ------------------ |
| treasure_id | int      | 要合成的星器id     |
| cost_list   | array    | 花费的星器碎片列表 |

> **val_like**:

```json
"cost_list":[[217, 16, 30]]		// [type, id, num], 碎片的type为217
```

#### 穿戴星器

>  **cmd**

  `put_on_treasure`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des              |
| ----------- | -------- | ---------------- |
| treasure_id | int      | 要穿戴的星器id   |
| slot_id     | int      | 要穿戴上的槽位id |

#### 卸下星器

>  **cmd**

  `put_off_treasure`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des            |
| ----------- | -------- | -------------- |
| treasure_id | int      | 要卸下的星器id |
| slot_id     | int      | 要卸下的槽位id |

#### 星器升星

>  **cmd**

  `treasure_star_upgrade`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                          |
| ----------- | -------- | -------------------------------------------- |
| treasure_id | int      | 要升级的星器id                               |
| target_lv   | int      | 升级到的目标星级                             |
| cost_list   | array    | 要花费的升星材料列表（格式同”碎片合成星器“） |

#### 星器升级

>  **cmd**

  `treasure_lv_upgrade`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                          |
| ----------- | -------- | -------------------------------------------- |
| treasure_id | int      | 要升级的星器id                               |
| target_star | int      | 升级到的目标等级                             |
| cost_list   | array    | 要花费的升级材料列表（格式同”碎片合成星器“） |

#### 重置星器

>  **cmd**

  `treasure_reset`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des            |
| ----------- | -------- | -------------- |
| treasure_id | int      | 要重置的星器id |


#### 宝物升级token合成

>  **cmd**

  `treasure_token_transform`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                  |
| ----------- | -------- | -------------------- |
| target_list | array    | 要合成的目标材料列表 |
| cost_list   | array    | 所要花费的材料列表   |

> **val_like**:

```json
"target_list":[[0, 5260, 80]],		// [type, id, num], 材料为道具, type为0
"cost_list":[[0, 5330, 320]]		// [type, id, num]
```





#### 训练英雄

>  **cmd**

  `train_hero`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name |    val_type          | des      |
| -------- |      --------         | -------- |
| hero_id     | int      | 英雄id |
| slot        | int      | 训练队列槽位 |

#### 切换是否自动突破

>  **cmd**

  `switch_hero_auto_break`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name |    val_type          | des      |
| -------- |      --------         | -------- |
| slot        | int      | 训练队列槽位 |







## kvk版本

### 恢复期

#### 向联盟固定成员发起帮助请求

>  **cmd**

  `kvk_al_help_apply_to_player`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| target_uid | int      | 目标玩家      |
| chat_param  | object   | 聊天的参数    |

```
`chat_message_send`

> **main_push**

`chat_index_mgr`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| channel_id            | string   | channel_id                              |
| timestamps            | string   | 微秒时间戳                              |
| msg_type              | int      |                                         |
| content               | string   | 若msg_type == report，格式为客户端自定义 |
| user_info             | string   | 用于反包 见proto中的ChatMsgItem         |
| is_whisper            | int      | 0: 不是，1:是                            |
| whisper_receiver_name | string   |      

```

---

#### 向全联盟发起帮助请求

>  **cmd**

  `kvk_al_help_apply_to_alliance`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| chat_param | object   | 聊天的参数    |
| event_id | string  | 恢复期活动event_id|

```
`chat_message_send`

> **main_push**

`chat_index_mgr`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| channel_id            | string   | channel_id                              |
| timestamps            | string   | 微秒时间戳                              |
| msg_type              | int      |                                         |
| content               | string   | 若msg_type == report，格式为客户端自定义 |
| user_info             | string   | 用于反包 见proto中的ChatMsgItem         |
| is_whisper            | int      | 0: 不是，1:是                            |
| whisper_receiver_name | string   |      

```

---

#### 领取恢复活动任务奖励

>  **cmd**

  `kvk_claim_recover_task`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:------------- |
| task_id    | int      | 任务id 暂定1，2|
| event_id    | string  | 活动的id       |

---

#### 立即复活死兵

>  **cmd**

  `kvk_revive_soldier`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| event_id   | string   |活动的id       |

---

#### 获取联盟全量的援助信息,拉取返包 svr_kvk_al_help_list的

>  **cmd**

  `kvk_al_help_list_get`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|     |       ||

---

#### 获取个人的援助信息,拉取返包 svr_kvk_person_help_info

>  **cmd**

  `kvk_other_player_help_info_get`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|target_uid  | int      | 目标玩家的uid |
|event_id  | string     | 恢复期的活动event_id |

---

#### 帮助联盟成员增加比例

>  **cmd**

  `kvk_help_al_member`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name   | val_type | desc                |
|:-----------|:---------|:--------------------|
|target_uid  | int      | 目标玩家的uid        |
|num         | int      | 帮助券的数量1次or5次  |
|event_id    | string   | 活动的id             |

---

#### 用宝石购买提升复活比例

>  **cmd**

  `kvk_buy_revive_ratio`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|gem_num     | int      | 花费的宝石数量 |
|event_id    | string   | 活动的event_id |

---


#### kvk通知杀敌阶段开始

>  **cmd**

  `kvk_notify_kill_stage_begin`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|attack_sid  | int      | 侵略方sid |
|defend_sid  | int      | 防守方sid |
|fight_stage_btime_ms  | int      | kvk争夺开始时间 |
|fight_stage_etime_ms  | int      | kvk争夺终止时间 |
|kill_stage_etime_ms   | int      | kvk杀敌阶段终止时间 |
|buff_list   | array [[buff_id, buff_num, etime]]    | 杀敌期施加全服的buff |
|extra_info  | object      | 额外信息 |
|event_id  | string      | 活动id |

```text
extra_info:
{
  "holy_fight_stage_btime_ms": 圣地争夺开始时间
  "holy_fight_stage_etime_ms": 圣地争夺结束时间
  "occupy_info_disappear_etime_ms": 占领历史消失时间
  "capacity":医院容量
}
```
---

#### kvk跨服移城

>  **cmd**

  `kvk_svr_move_city`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|event_id  | string      | 活动id |
|tar_sid  | int      | 目标sid |
|tar_pos  | int      | 目标坐标 |
|item_id  | int      | 道具id |
|item_num  | int      | 道具数量 |
|use_gem  | int      | 是否使用宝石(1-使用宝石) |

---

#### 清除跨服移城被动移城标记

>  **cmd**

  `clear_kvk_passive_move_city_flag`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|num         | int      |              |

---

#### 新使用王国技能

>  **cmd**

  `use_kingdom_skill_new`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|sid         | int      |              |
|skill_id    | int      |              |

---

#### 获取kvk信息

>  **cmd**

  `get_kvk_info`

> **main_push**:

  `game_server`

>  **param**:


---

#### 获取多个服的王国头衔信息

>  **cmd**

  `get_multi_title_abs_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|sid_list    | array      |              |

---

#### 领取预下载奖励

>  **cmd**

  `get_client_pre_download_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|reward_id    | int      |              |

---

#### 拉取征伐野蛮人排行榜数据

>  **cmd**

  `get_gs_rank_data`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
---

#### 邮件翻译
> **cmd**

	`mail_translate`

> **main_push**

	`ds_compute`

> **param**:
| key_name |    val_type          | des      |
| -------- |      --------         | -------- |
| mail_id        | int      | 邮件id |
| data     | object | 要翻译的内容 |
| to_lang  | int | 要翻译的语言 |

'''
// key 翻译邮件的key，用于返包
// value 需要翻译的内容
{
	"key":value
}
'''
---

#### 清理跳级弹窗数据

>  **cmd**

  `clear_jump_lv_flag`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
---

#### 获取服务器相关数据

>  **cmd**

  `get_svr_info_list`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| svr_list        | array      | 服务器列表 |
---

#### 获取服务器王座占领数据

>  **cmd**

  `get_svr_info_list_by_sid`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| sid_list        | array      | 服务器列表 |


---

#### 装备预设重命名

>  **cmd**

  `player_equip_preset_change_name`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des              |
| ----------- | -------- | ---------------- |
| preset_id   | int      | 预设id           |
| preset_name | string   | 要更改的预设名字 |

#### 装备预设应用到领主身上

>  **cmd**

  `player_equip_preset_apply`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name  | val_type | des    |
| --------- | -------- | ------ |
| preset_id | int      | 预设id |

#### 装备预设方案内容的更改

>  **cmd**

  `player_equip_preset_update`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name  | val_type | des                                          |
| --------- | -------- | -------------------------------------------- |
| preset_id | int      | 预设id                                       |
| put_type  | int      | 要更新的类型（0：脱、1：穿）                 |
| slot_id   | int      | 要更新的槽位id                               |
| is_equip  | int      | 是否是要更新装备（0：更新宝物、1：更新装备） |
| id        | int      | 装备id、或宝物id                             |

#### 装备预设清空

>  **cmd**

  `player_equip_preset_reset`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name  | val_type | des    |
| --------- | -------- | ------ |
| preset_id | int      | 预设id |


#### 使用碎片永久解锁皮肤

>  **cmd**

  `dress_piece_compound`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des      |
| ---------- | -------- | -------- |
| skin_type  | int      | 皮肤type |
| skin_id    | int      | 皮肤id   |
| piece_type | int      | 碎片type |
| piece_id   | int      | 碎片id   |
| num        | int      | 碎片数量 |

#### 皮肤升星

>  **cmd**

  `dress_star_upgrade`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des      |
| ------------ | -------- | -------- |
| skin_type    | int      | 皮肤type |
| skin_id      | int      | 皮肤id   |
| piece_type   | int      | 碎片type |
| piece_id     | int      | 碎片id   |
| piece_num    | int      | 碎片数量 |
| upgrade_time | int      | 强化次数 |

#### 皮肤碎片兑换

>  **cmd**

  `dress_piece_transfer`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des            |
| ---------- | -------- | -------------- |
| cost_id    | int      | 消耗的碎片id   |
| cost_num   | int      | 消耗的碎片数量 |
| target_id  | int      | 目标碎片id     |
| target_num | int      | 目标碎片数量   |
| piece_type | int      | 碎片type       |

#### 军队预设重命名

>  **cmd**

  `player_troop_preset_change_name`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des              |
| ----------- | -------- | ---------------- |
| preset_id   | int      | 预设id           |
| preset_name | string   | 要更改的预设名字 |

#### 军队预设方案内容的更改

>  **cmd**

  `player_troop_preset_update`

>  **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des              |
| ------------ | -------- | ---------------- |
| preset_id    | int      | 预设id           |
| hero_array   | array    | 要设置的英雄列表 |
| soldier_list | object   | 要设置的士兵信息 |
| has_lord     | int   | 0没有领主 1有领主 |
| hero_list    | array    | 英雄列表 |
| version      | int      | 客户端传，默认0  |
| equip_preset | int      | 可选使用装备预设id，默认-999表示不使用预设  |

> **val_like**:

```json
"hero_array":[32, 20]					// 英雄id
"soldier_list":{"1":5000,"201":2000}	// 士兵id，对应的比例, 万分制(5000即为50%)
```

#### svs进入战场

>  **cmd**

  `svs_svr_move_city_enter`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|event_id  | string      | 活动id |
|tar_sid  | int      | 目标sid （战场id）|
|tar_pos  | int      | 目标坐标 |
|item_id  | int      | 道具id |
|item_num  | int      | 道具数量 |
|use_gem  | int      | 是否使用宝石(1-使用宝石) |

---

#### svs主动退出战场

>  **cmd**

  `svs_svr_move_city_back`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|

---

#### svs清理被踢出战场标记

>  **cmd**

  `clear_svs_passive_move_city_flag`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|

---

#### svs获取战场内各服人数及王座占领服

>  **cmd**

  `get_svs_info_by_battlefield_id`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|battle_field_id  | int | 战场id|
|   list     |   array  | 传对应战场的信息  [{"event_id":"string","event_type":int}]   
| rank_type_list  |   array  |[ {"rank_type":int // 排行榜类别 0-服务器总榜 1-总个人积分榜 2-服务器积分榜 3-王城占领榜 4-卫城占领榜 5-骁勇榜
                                    // 个人排行榜  1-总个人积分榜 3-王城占领榜 4-卫城占领榜 5-骁勇榜
                                    // sid排行榜    0-服务器总榜 2-服务器积分榜
								"show_size":int //获取排行榜的数据量，-1表示返回全量排行榜  } ]
---

#### svs兑换币

>  **cmd**

  `svs_exchange_reward`

> **main_push**:

  `event_proxy`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|event_id  | string      |商店event_id             |
|svs_event_id  | string  |铁王座event_id             |
|index     | int         |             |
|num       | int         |             |
---


#### 添加轮盘槽位内的文案 铁王座战场

>  **cmd**

  `svs_push_quick_speech`

> **main_push**:

  `game_server_10000`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|unique_id          |string       |文案id              |
|doc_id             |int(正数)       |文案id              |
|block_id           |int64     |位置id              |
---

#### svs添加/更新联盟书签

>  **cmd**

  `svs_al_bookmark_add`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| sid      | int      | 服务器id              |
| pos_id   | int      | 位置                  |
| name     | string   | 名称                  |
| classify | int      | 标记分类              |
| svs_etime | int      | svs争夺期结束时间              |
---

### 1.15.5 坐标收藏  v0.70

#### svs添加收藏

>  **cmd**

  `svs_bookmark_add`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | des                   |
|----------|----------|-----------------------|
| sid      | int      | 服务器id              |
| pos_id   | int      | 位置  y * 1000000 + x |
| name     | string   | 名称                  |
| classify | int      | 收藏分类              |
| svs_etime | int      | svs争夺期结束时间              |

---

#### svs拉取王国信息（国王uid  ksid）

>  **cmd**

  `svs_get_kingdom_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des                   |
battle_id     int        目标战场id

---

#### 领取成长基金奖励
>  **cmd**

  `claim_new_castle_lv_up_iap_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|claim_idx          |int       |领取的奖励的下标,从1开始    |



#### 使用个人头衔解锁道具

>  **cmd**

  `use_personal_title_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des                  |
| -------- | -------- | -------------------- |
| item_id  | int      | 激活个人头衔的道具id |
| item_num | int      | 使用道具的数量       |

#### 设置展示头衔

>  **cmd**

  `set_personal_title_displayed`

> **main_push**:

  `ds_player`

>  **param**:

| key_name  | val_type | des                            |
| --------- | -------- | ------------------------------ |
| title_id  | int      | 要设置的个人头衔id             |
| operation | int      | 操作类型，0取消展示、1设置展示 |











----

# **新增命令在此处以上增加**

---



# mg的cmd整理

## 士兵相关

#### 正在使用的命令

```json
cmd = {
    // 训练
    "soldier_train_by_array":"训练开始",
    "speed_up_train_soldier_v2":"训练加速",
    "end_train_soldier":"训练加速到立即完成并领取",
    "soldier_train_cancel_by_array":"训练取消",
    "soldier_train_immediately":"训练立即完成",

	// 治疗
    "soldier_treat":"治疗开始, 或治疗立即完成",
    "speed_up_treatment":"治疗加速",
    "soldier_treatment_cancel":"治疗取消",

	// 复活
    "soldier_revive":"复活开始",
    "soldier_revive_cancel":"复活取消",
    "soldier_revive_free":"复活立即完成并领取",


    "batch_claim_soldiers":"领取完成的士兵(包括训练，治疗, 复活)",

    "soldier_dismiss":"解散士兵",

}
// 2022.12.15更新
```

#### 士兵治疗或治疗立即完成

>  **cmd**

  `soldier_treat`

>  **param**:

| key_name        | val_type | desc                                                         |
| :-------------- | :------- | :----------------------------------------------------------- |
| svr_building_id | int      | 此项治疗所在的兵营建筑svr_id                                 |
| treat_type      | int      | 治疗类型，2是普通治疗，1花费宝石(用于治疗且补足资源)，3花费宝石(仅用于治疗) |
| gem_num         | int      | 所花费的宝石数                                               |
| soldier_list    | object   | 要治疗的士兵列表                                             |

> **val_like**:

```json
"soldier_list":{
    "$(soldier_id)"{
        "num":num,		// 要治疗的士兵数量
        "pos":-2,
    },
}
```



#### 士兵普通复活

>  **cmd**

  `soldier_revive`

>  **param**:

| key_name     | val_type | desc                                       |
| :----------- | :------- | :----------------------------------------- |
| revive_type  | int      | 复活类型，2是普通复活                      |
| cost_type    | int      | 非普通复活时，0花费道具，1花费宝石，现无用 |
| gem_num      | int      | 所花费的宝石数                             |
| item_id      | int      | 所花费的道具id                             |
| soldier_list | object   | 要治疗的士兵列表                           |

> **val_like**:

```json
"soldier_list":{
    "$(soldier_id)"{
        "num":num,		// 要复活的士兵数量
        "pos":-2,
    },
}
```



#### 士兵瞬间复活

>  **cmd**

  `soldier_revive_free`

>  **param**:

| key_name     | val_type | desc                                       |
| :----------- | :------- | :----------------------------------------- |
| cost_type    | int      | 非普通复活时，0花费道具，1花费宝石，现无用 |
| item_id      | int      | 所花费的道具id                             |
| item_num     | int      | 所花费的道具数量                           |
| soldier_list | object   | 要治疗的士兵列表                           |

> **val_like**:

```json
"soldier_list":{
    "$(soldier_id)"{
        "num":num,		// 要复活的士兵数量
        "pos":-2,
    },
}
```

------



## 道具相关

#### 正在使用的命令

```json
{

    //////////// 道具购买和兑换
    "normal_store_item_buy":"普通商店购买道具",
    "battle_score_shop_buy":"战功商店购买",
    "expedition_shop_buy":"远征商店, 用远征币购买道具",
    "token_shop_buy":"远征商店, 用token购买道具",
    "al_shop_buy":"联盟商店购买",



    ///////////// 道具使用
    // 普通道具, 如:
    // 资源栏目下的道具
    // 增益栏目下的训练容量增加道具
    // 其他栏目下的指挥官经验道具、建筑升级的token道具
    "use_common_item":"使用道具、或购买道具并使用",
    "batch_use_common_item":"批量使用道具",

    // 增益类道具
    "use_time_buff_item":"使用增益类道具",

    ////// 独立cmd的道具
    // 加速道具, 只能在各自的计时界面使用
    "building_speed_up":"建筑加速, 使用道具或钻石",
    "use_speeduptime_item":"研究加速, 使用道具或钻石",
    "speed_up_train_soldier_v2":"士兵训练加速",
    "speed_up_treatment":"士兵治疗加速",

    // 移城道具
    "random_move_city_new":"随机移城",
    "fixed_move_city_new":"每日免费移城、定点移城(花费道具或钻石)",

    // 英雄经验道具
    "hero_item_use":"英雄经验道具单个使用",
    "hero_item_use_by_array":"英雄经验道具批量使用, 用于一键升级",

    // 指挥官体力道具
    "action_energy_item_use":"指挥官行动力道具使用",

    // 洛哈道具
    "use_item_create_obj":"使用洛哈道具",

    // 宝箱道具
    "open_random_reward_chest":"开启随机宝箱道具",
    "open_select_reward_chest":"使用自选宝箱",
    "open_fixd_reward_chest":"开启固定宝箱奖励",

    // 英雄专属技能升级道具兑换
    "hero_skillupgrade_item_transform":"使用英雄通用技能道具, 兑换专属英雄技能道具",

    // 免费复活材料道具兑换
    "soldier_revive_free_item_charge":"使用道具再造电芯, 兑换立即复活材料"
}
// 2022.12.16更新
```



#### 战功商店购买

>  **cmd**

  `battle_score_shop_buy`

>  **param**:

| key_name | val_type | desc               |
| :------- | :------- | :----------------- |
| id       | int      | 所购买道具的槽位id |
| num       | int      | 购买数量          |


#### 随机移城

>  **cmd**

  `random_move_city_new`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
|          |          |      |



#### 定点移城

>  **cmd**

  `fixed_move_city_new`

>  **param**:

| key_name | val_type | desc                       |
| :------- | :------- | :------------------------- |
| use_gem  | int      | 使用宝石，1使用，0使用道具 |
| item_id  | int      | 道具id                     |
| tar_pos  | int      | 目标地坐标                 |



#### 英雄经验道具单个使用

>  **cmd**

  `hero_item_use`

>  **param**:

| key_name | val_type | desc     |
| :------- | :------- | :------- |
| hero_id  | int      | 英雄id   |
| item_id  | int      | 道具id   |
| item_num | int      | 道具数量 |



#### 指挥官体力道具使用

>  **cmd**

  `action_energy_item_use`

>  **param**:

| key_name | val_type | desc     |
| :------- | :------- | :------- |
| item_id  | int      | 道具id   |
| item_num | int      | 道具数量 |



#### 兑换立即复活材料

>  **cmd**

  `soldier_revive_free_item_charge`

>  **param**:

| key_name  | val_type | desc             |
| :-------- | :------- | :--------------- |
| cost_type | int      | 花费类型，1-道具 |
| item_id   | int      | 道具id           |
| item_num  | int      | 道具数量         |

---

#### 领取成长基金奖励
>  **cmd**

  `claim_new_castle_lv_up_iap_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|claim_idx          |int       |领取的奖励的下标,从1开始    |


### 1.4.3 总统邮件
>  **cmd**

  `president_mail_send_by_id`

> **main_push**:

  `mail_proxy`

>  **param**:

| key_name      | val_type | des                          |
|---------------|----------|------------------------------|
| sid           | int      | 玩家要发送邮件给哪个服       |
| sender        | object   | 发送人的信息                 |
| mail          | object   | 邮件信息                     |
| receiver      | object   | 邮件的接收者                 |

```json
{
	"sid": int,	// 接收邮件的服，与receiver的sid_list的服相同
	"sender":
	{
		"suid": int,
		"sender": string,      //发送人的名字
		"alnick": string,
		"player_avatar": int,   // 头像
		"head_frame_id": int   // 头像框
		"al_avatar": int       // 联盟旗帜
	},

	"mail":
	{
		"target_info": //接收人的展示信息
		{
			"names": [ string ], // 用户名称
			"alliance_nicknames": [ string ],  // 联盟名称
			"tuid": int,
			"player_avatar": int,   // 头像
			"head_frame_id": int   // 头像框
		},
		"title": string,
		"ctype": int  //参考邮件内容协议
		"content": string,
		"is_reply": int             // 0:false, 1:true
	},

	"receiver":
	{
		uid_list: [int], // 接收的用户列表，为空
		aid_list: [int], // 接收的联盟列表，为空
		sid_list: [int] // 接收的服列表，只能有一个服，与param的sid相等
	}
}
```
> **output**
  svr_mail_abs_inc

#### 确认继承
>  **cmd**

  `real_inherit`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|


#### 获取继承信息（被继承的uid，头像等..以及如果有继任人的话，也返继承人信息）
>  **cmd**

  `get_inherit_info`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| tar_uid           | int64    |  被继承的uid       |



#### 新号继承老号
>  **cmd**

  `new_account_inherit`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
| inherit           | int      | 老号uid |





## mg2接口协议


#### rpg建筑

>  **cmd**

  `raid_finish_rpg_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| hero_list  | array      | 攻打rpg副本英雄列表                                |
| building_id  | int      | 建筑id                                |
| area_id | int | 探索区域id |


#### 救援建筑

>  **cmd**

  `finish_rescue_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| area_id | int | 探索区域id |


#### 雷达障碍物

>  **cmd**

  `obstacle_remove`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| extra_buildings| array  | 额外需要删除的建筑，目前仅对主城生效，[svr_building_id] |
| area_id | int | 探索区域id |


#### 采集障碍物

>  **cmd**

  `city_collect_start_new`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| svr_building_id_list | array    | 资源地后台id的数组 |
| area_id | int | 探索区域id |



#### slg障碍物

>  **cmd**

  `finish_slg_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| building_id  | int      | 建筑id                                |
| wounded_soldier | array | 进医院的伤病 [[id, num]]|
| hero_list | array | 英雄列表[hero_id] |
| area_id | int | 探索区域id |

#### 收复区域

>  **cmd**

  `recover_area`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| area_id | int | 探索区域id |
| connect_building | object     | {"svr_id":["id1","di2"],"svr_id2":["id3","id4“,"id5"]} svr_id : string  涉及的后台建筑id   id1/2/3/4/5 : string(客户端要求string)  该建筑会连接的后台建筑id|



#### 放置建筑

>  **cmd**

  `place_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    |     val_type    | des                                                                                            |
|-------------|-----------------|------------------------------------------------------------------------------------------------|
| connect_building | array     |  连接的建筑后台id   （客户端要求string) 
| building_type | int      | 建筑类型 |
| pos           | int      | 建筑坐标 

#### 连接建筑

>  **cmd**

  `connect_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    |     val_type    | des                                                                                            |
|-------------|-----------------|------------------------------------------------------------------------------------------------|
| connect_building | object     | {"svr_id":["id1","di2"],"svr_id2":["id3","id4“,"id5"]} svr_id : string  涉及的后台建筑id   id1/2/3/4/5 : string(客户端要求string)  该建筑会连接的后台建筑id|

#### 建造建筑

>  **cmd**

  `construct_building`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    |     val_type    | des                                                                                            |
|-------------|-----------------|------------------------------------------------------------------------------------------------|
| building_id | int      | 后台建筑id| |
| lv           | int      | 建筑等级 |
| instant           | int      | 1立即完成，0普通完成 |
| instant_gem           | int      | 立即完成所需宝石数量 |

#### 移动建筑  （原本已有，加个连接建筑的参数）

>  **cmd**

  `move_entity`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    |     val_type    | des                                                                                            |
|-------------|-----------------|------------------------------------------------------------------------------------------------|
| move_entity_list | object   | 移动的建筑及被让位的建筑列表 {"building":[{"id":int64, "pos":int32}], "commander":[{"id":int64, "pos":int32}]} |
| connect_building | object     | {"svr_id":["id1","di2"],"svr_id2":["id3",”id4","id5"]} svr_id : string  涉及的后台建筑id   id1/2/3/4/5 : string(客户端要求string) 该建筑会连接的后台建筑id|
| special_building_id | array      | 这一次移动中  这一块失效建筑区的特殊建筑svr_id 或  这一块生效建筑区中的特殊建筑svr_id   string(客户端要求string)


#### 升级家具

>  **cmd**

  `furniture_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_id | int     | 建筑id  |
| upgrade_items | object      | 家具升级信息  |

+ upgrade_items
```json
//通用参数
{
  "type":lv // 家具type->家具目标等级
}
```


#### 派遣平民去采集

>  **cmd**

  `resource_worker_start`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| svr_building_id | int     | 建筑id  |
| num | int      | 平民数量  |



#### 取消挖矿工人工作

>  **cmd**

  `resource_worker_stop`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| svr_building_id | int     | 建筑id  |
| num | int      | 平民数量  |


#### 领取事件奖励

>  **cmd**

  `claim_cycle_event_reward`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| type | int     | 事件类型【0风暴威胁】  |



#### 自动领取事件奖励

>  **cmd**

  `claim_cycle_event_reward_auto`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| type | int     | 事件类型【0研究引入 1大水威胁】  |


#### 领取章节任务奖励

>  **cmd**

`claim_chapter_quest_list`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| claim_id | array    | [int] 任务ID |


#### 领取建筑问题气泡奖励

>  **cmd**

`claim_building_quest`

> **main_push**:

`player`

>  **param**:

| key_name    | val_type | desc       |
|-------------|----------|------------|
| building_id | int      | 建筑类型ID |
| claim_id    | int      | 任务ID     |


#### 领取移民建筑问题气泡奖励

>  **cmd**

`claim_migration_quest`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| claim_id | int      | 任务ID |


#### 从入夜进入白昼

>  **cmd**

`night_to_day`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| id       | int      | 夜晚ID |

#### 展示氛围背景图

>  **cmd**

`show_atmospheric`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| id       | int      | 氛围ID |

#### 领取指引奖励

>  **cmd**

`claim_guide_reward`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| id       | int      | 指引id |

#### 进入探索

>  **cmd**

`explore_area_new`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|
| area_id  | int      | 区域id                                 |


#### 领取保险箱进度奖励

>  **cmd**

`safe_box_claim_progress_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | des                                                                                            |
|-------------|----------|------------------------------------------------------------------------------------------------|


#### 建造建筑

>  **cmd**

  `construct_building_new`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| building_type | int      | 建筑类型 |
| pos           | int      | 建筑坐标 |
| lv           | int      | 建筑等级 |
| instant           | int      | 1立即完成，0普通完成 |
| instant_gem           | int      | 立即完成所需宝石数量 |
| connect_building | array     |  连接的建筑后台id   （客户端要求string) |


#### 英雄升级

>  **cmd**

`async_hero_lv_up`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc       |
| :------- | :------- | :--- |
| id       | int      | 英雄id     |
| exp      | int      | 消耗经验   |
| coin     | int      | 消耗突破币 |
| lv_before| int      | 原等级     |
| lv_after | int      | 目标等级   |


# 通关rpg远征关卡

>  **cmd**

  `clear_rpg_dungeon`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| stage_id | int      | 关卡id             |
| lineup   | array    | 战斗前的阵容信息   |

# 通关rpg远征关卡失败

>  **cmd**

  `clear_rpg_dungeon_failed`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| stage_id | int      | 关卡id             |
| lineup   | array    | 战斗前的阵容信息   |
```json
lineup:[$hero_id, ...]
```

# 领取rpg远征挂机奖励

>  **cmd**

  `collect_hang_up_reward`

> **main_push**:

  `player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
|          |          |      |


#### 修理建筑

>  **cmd**

  `repair_building`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc           |
|:------------|:---------|:---------------|
| building_id | int      | 被修理的建筑id |
|extra_buildings| array | 额外删除的建筑id [svr_building_id]|

#### 消除六边形宝石

>  **cmd**

  `clear_grid`

> **main_push**:

  `player`

>  **param**:

| key_name    | val_type | desc           |
|:------------|:---------|:---------------|
|pos_list| array | 待删除的pos列表 |


#### 清除弹窗

>  **cmd**

  `clear_tip_window`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| ids | array      | 弹窗id数组[int,...] |


#### 解锁第二建造队列

>  **cmd**

  `unlock_second_building_queue`

> **main_push**:

  `player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
| type       | int64      | 0:免费   1:收费 |
| cost_gem   | int64      | 消耗的宝石  免费填0 |


#### 领主水晶 消耗水晶token来升级水晶

>  **cmd**

  `player_crystal_upgrade`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type         | desc         |
|:-----------------|:-----------------|:-------------|
| equip_slot_id    | int64            | 装备槽位id   |
| crystal_slot_id  | int64            | 水晶槽位id   |

#### 领主水晶 消耗水晶token来合成水晶

>  **cmd**

  `player_crystal_compose`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type         | desc         |
|:-----------------|:-----------------|:-------------|
| crystal_id       | int64            | 水晶id       |

#### 领主水晶 镶嵌水晶

>  **cmd**

  `player_crystal_mount`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type         | desc         |
|:-----------------|:-----------------|:-------------|
| crystal_id       | int64            | 水晶id       |
| equip_slot_id    | int64            | 装备槽位id   |
| crystal_slot_id  | int64            | 水晶槽位id   |

#### 领主水晶 卸下水晶

>  **cmd**

  `player_crystal_unmount`

> **main_push**:

  `player`

>  **param**:

| key_name         | val_type         | desc         |
|:-----------------|:-----------------|:-------------|
| equip_slot_id    | int64            | 装备槽位id   |
| crystal_slot_id  | int64            | 水晶槽位id   |


#### 客户端数据透传后台上报

>  **cmd**

  `center_data_up`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc         |
|:-----------  |:---------|:-------------|
| main_type    | int64    | main_type    |
| action_type  | int64    | action_type  |
| key          | int64    | key          |
| value        | int64    | value        |
| info         | object   | 详细信息      |

> **val_like**:

```json
  [main_type, action_type, "key_value", info]
  上传token{
    main_type: 1,
    action_type: 7,
    key:  0
    value: 建筑id
    info:{
      svr_id: 建筑id
      type: 建筑类型
    }
  }
```

#### 竞技场rpg战斗校验

>  **cmd**

  `check_rpg_pvp_battle`

> **main_push**:

  `player`

>  **param**:

| key_name     | val_type | desc         |
|:-----------  |:---------|:-------------|
| rpg_battle_id| int64    | 战斗id       |
| output       | object   | 输出        |

#### 获取炮塔王座战争记录

>  **cmd**

  `get_land_building_battle_record`

> **main_push**:

  `game_server`

>  **param**:

| key_name     | val_type | desc         |
|:-----------  |:---------|:-------------|
| unique_id    | string    | 建筑unique_id       |



#### kvk被动移城动画播放完毕

>  **cmd**

  `kvk_passive_move_city_confirm`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---


#### kvk赋予头衔

>  **cmd**

  `claim_user_kingdom_title_new`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| kingdom_title  | int  |      |
|target_uid  | int|目标uid |
| sid      |int   | 目标sid
---


#### 建筑一键加速 v1.1.1

>  **cmd**

  `auto_building_speed_up`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type     | desc                   |
|:------------------|:-------------|:-----------------------|
| building_svr_id   | int          | 建筑唯一id              |
| cost_list         | array        | 消耗道具列表            |
| is_cost_gem       | int          | 0:使用道具 1:使用宝石   |
| cost_gem          | int          | 使用宝石数量            |

> **val_like**:

```json
"cost_list":[[0, 3526, 320]]		// [type, id, num] 道具type为0
```

#### 练兵一键加速 v1.1.1

>  **cmd**

  `auto_speed_up_train_soldier`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type     | desc                   |
|:------------------|:-------------|:-----------------------|
| building_svr_id   | int          | 要加速的队列所在兵营的svr_id    |
| train_svr_id      | int          | 训练队列svr_id               |
| cost_list         | array        | 消耗道具列表             |
| is_cost_gem       | int          | 0:使用道具 1:使用宝石   |
| cost_gem          | int          | 使用宝石数量            |
| is_claim          | int          | 是否立即领取士兵 0:否 1 是 |

> **val_like**:

```json
"cost_list":[[0, 3526, 320]]		// [type, id, num] 道具type为0
```

#### 治疗一键加速 v1.1.1

>  **cmd**

  `auto_speed_up_treatment`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type     | desc                   |
|:------------------|:-------------|:-----------------------|
| building_svr_id   | int          | 要加速的队列所在医院的svr_id |
| cost_list         | array        | 消耗道具列表            |
| is_cost_gem       | int          | 0:使用道具 1:使用宝石   |
| cost_gem          | int          | 使用宝石数量            |

> **val_like**:

```json
"cost_list":[[0, 3526, 320]]		// [type, id, num] 道具type为0
```

#### 研究一键加速 v1.1.1

>  **cmd**

  `auto_speed_up_research`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type     | desc                   |
|:------------------|:-------------|:-----------------------|
| target_id         | int          | 使用目标队列(action id) |
| cost_list         | array        |  消耗道具列表           |
| is_cost_gem       | int          | 0:使用道具 1:使用宝石   |
| cost_gem          | int          | 使用宝石数量            |

> **val_like**:

```json
"cost_list":[[0, 3526, 320]]		// [type, id, num] 道具type为0
```

#### 一键补充资源 v1.1.1

>  **cmd**

  `auto_use_resource_item`

> **main_push**:

  `ds_player`

>  **param**:

| key_name               | val_type     | desc                   |
|:------------------     |:-------------|:-----------------------|
| chest_cost_list        | array        | 自选宝箱                |
| item_cost_list         | array        | 消耗的通用道具          |

> **val_like**:

```json
"chest_cost_list":[[0, 3526, 320, 1]]		// [[type, chest_id, chest_num, select_idx]]
"item_cost_list":[[0,0,1]] // [[type, item_id, item_num]]
```


### 获取问卷

>  **cmd**

  `get_questionnaire_info`

> **main_push**:

  `op_svr`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |

> 反包
+ svr_questionnaire_info

```json
[
    {
        "begin_time": int
        "close_time": int // -1代表永久
        "event_id":string $begin_time_$close_time // 唯一id，即使填了多个，也只生效第一个
        "doc_id": title
        "reward":[ // 奖励列表
            {
                "a":[TINT32, TINT32, TINT32] // type, id, num
            }
        ],
        "url": string // url 
    }
]
```

#### 战令活动：宝石解锁档位

>  **cmd**

  `op_event_exchange_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc                     |
| :--------- | :------- | :----------------------- |
| list       | array    | 活动数据                  |
| extra      | object   | 请求信息                  |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "extra": {
      "gear":int  //解锁档位
  }
```
---

### 训练营训练英雄和下阵英雄

>  **cmd**

  `set_training_hero`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| slot_id     | int      | 槽位id   |
| hero_id     | int      | 英雄id 0表示下阵 |

---

### 训练营消除槽位冷却

>  **cmd**

  `clear_training_cd`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| slot_id     | int      | 槽位id   |

---

#### 英雄重置

>  **cmd**

`hero_reset`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| hero_id   | int      | 英雄id |

---

#### 消除英雄重置冷却

>  **cmd**

`clear_hero_reset_cd`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| hero_id   | int      | 英雄id |

---

#### 成就系统 领奖

>  **cmd**

`claim_achievement_reward`

> **main_push**:

`ds_player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| id       | int      | 成就id |

---

#### 成就系统 进度奖励

>  **cmd**

`claim_achievement_category_reward`

> **main_push**:

`ds_player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| category | int      | 类别id 0:成就总树 >=1:其他成就树|
| id       | int      | 进度id |
---

#### 成就系统 设置成就墙

>  **cmd**

`set_achievement_show`

> **main_push**:

`ds_player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| id_list  | array    | 成就id |

---

#### 成就系统 获取全服成就完成率

>  **cmd**

`get_achievement_rate`

> **main_push**:

`rank_event_svr`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|

> 反包
```
svr_achievement_rate
{
    "finish_list": [
        [int, int]  // [成就id, 完成人数]
    ],
    "svr_player_num": int
}
```

---

#### 成就系统 任务 活动结算时达到第X名

>  **cmd**

`op_event_final_rank`

> **main_push**:

`ds_player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| event_type | int    | 活动类别 66-个人对决 71-矿区|
| rank     | int      | 活动排名  |

---

#### 称号系统 装备或卸下

>  **cmd**

`set_self_title`

> **main_push**:

`ds_player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| id       | int      | 称号id 0:卸下|
---

#### 获取排行榜信息

>  **cmd**

`rank`

> **main_push**:

`rank_player`

>  **param**:

| key_name | val_type | desc   |
|----------|----------|--------|
| key0     | int      | 排行榜类别 |
| rank_type| int      | 排行榜范围（0-单服 1-临服 2-全服） |
---



### 教堂死兵普通复活

>  **cmd**

  `soldier_revive`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des                                          |
| ------------ | -------- | -------------------------------------------- |
| revive_type  | int      | 1. 立即普通复活                              |
| cost_type    | int      | 消耗类型: 0 道具，1宝石                      |
| item_id      | int      | 道具id (忠诚军牌)                            |
| item_num     | int      | 道具数量                                     |
| gem_num      | int      | 当消耗宝石时，需要传入，用于校验数据         |
| soldier_list | object   | { "1": 1, ....}  key： 士兵类型， val： 数量 |

---

### 教堂死兵立即复活

>  **cmd**

  `soldier_revive_free`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | desc                     |
| :----------- | :------- | :----------------------- |
| cost_type    | int      | -1无花费                 |
| item_id      | int      | 0                        |
| item_num     | int      | 0                        |
| soldier_list | object   | {}即可，默认全部立即复活 |

---

### 解散待治疗的伤兵

>  **cmd**

  `soldier_dismiss_wounded`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| soldier_id  | int      | 伤兵id   |
| soldier_num | int      | 伤兵数量 |

---

### 解散待复活的死兵

>  **cmd**

  `soldier_dismiss_dead`

> **main_push**:

  `ds_player`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| soldier_id  | int      | 死兵id   |
| soldier_num | int      | 死兵数量 |

---

### 发起联盟投票

>  **cmd**

  `al_vote_initiate`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| topic  | string      | 投票主题   |
| options | array      |选项列表 |
| is_multi  | int      | 0-不可多选   1-可以多选|
| need_top  | int      | 0-不置顶   1-置顶|
| duration  | int      | 持续时长，单位：秒|
```
options
[string]    // 按序号顺序的选项文案
```
---

### 置顶联盟投票

>  **cmd**

  `al_vote_top`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| vote_id     | int      | 投票id   |
| cancel_top  | int      | 0-置顶  1-取消置顶   |

---

### 联盟成员进行联盟投票(修改投票也使用此接口)

>  **cmd**

  `al_vote_chose`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| vote_id     | int      | 投票id   |
| option_id   | array    | 选项id列表，第几个选项就传几，从1开始   |

---

### 终止联盟投票

>  **cmd**

  `al_vote_stop`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| vote_id     | int      | 投票id   |

---

### 删除联盟投票记录

>  **cmd**

  `al_vote_del_record`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name    | val_type | desc     |
| :---------- | :------- | :------- |
| vote_id     | int      | 投票id   |

---
#### 添加轮盘槽位内的表情包

>  **cmd**

  `set_quick_emo`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|emo_list            |object   |{"$(slot_id)":emo_id}, slot_id从1开始|              |
---

#### 轮盘消息数据推送

>  **cmd**

  `push_quick_emo`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name          | val_type | des                |
|-------------------|----------|--------------------|
|emo_id             |int64     |文案id              |
|unique_id          |string    |对象id              |
|block_id           |int64     |位置id              |
|map_type           |int32     |所处地图类型 0-大地图   1-ava战场   2-pvp战场         |
|raid_id            |int64     |所处地图id  sid        ava战场id   pvp战场id           |
---

#### 翻译一个投票信息
> **cmd**

`al_vote_translate`

> **main_push**

`ds_alliance`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| vote_id        | int      |            |
| target_lang_id | int      |            |
---

#### 联盟投票通知接口
> **cmd**

`al_vote_inform`

> **main_push**

`ds_alliance`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| vote_id        | int      |            |
| uid_list       | array    | 玩家列表    |
| msg_info       | string   | 聊天通知内容    |
| user_info      | string   | 与chat_message_send一致    |
| time      | int   | 客户端时间us    |

---

#### 领主装备打造

>  **cmd**

  `player_compose_equip`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                |                                                                            |
|---------------|----------|--------------------|----------------------------------------------------------------------------|
| equip_id      | int      | 数值配置的装备类型 |                                                                            |
| material_list | array    | 材料列表           | [{type: 1, // 1 图纸, 2 碎片, 3 宝箱 ,id: 1,   // 对应的 id, num  //数量}] |
| slot          | int      | 装备槽位           |

---

#### 领取英雄故事奖励

>  **cmd**

  `hero_get_story_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                |                                                                            |
|---------------|----------|--------------------|----------------------------------------------------------------------------|
| hero_id       | int      | 领取奖励的英雄id     |
| star          | int      | 领取奖励的英雄星级   |                                                                             |

---

#### 防骚扰设置

>  **cmd**

  `player_anti_harass_set`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                |                                                                            |
|---------------|----------|--------------------|----------------------------------------------------------------------------|
| castle_lv_list| array    | 主城等级要求列表 数组下标[0-私聊 1-邮件 2-好友]      |                                                 |

---

#### 消耗道具发送信息（玩家发送世界广播）

>  **cmd**

  `cost_item_chat_message_send`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                |                                                                            |
|---------------|----------|--------------------|----------------------------------------------------------------------------|
| item_id       | int      | 消耗道具id      |                                                                            |
| item_num      | int      | 消耗道具数量    |
| cost_type     | int      | 使用方式(0:道具1:宝石) |
| chat_param    | object   | 聊天信息所需参数   |

```
chat_param的内容
| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| channel_id            | string   | channel_id                              |
| timestamps            | string   | 微秒时间戳                              |
| msg_type              | int      |                                         |
| content               | string   | 若msg_type == report，格式为客户端自定义 |
| user_info             | string   | 用于反包 见proto中的ChatMsgItem         |
| is_whisper            | int      | 0: 不是，1:是                            |
| whisper_receiver_name | string   |                                         |
| content_info          | string   |                                         |
```

---

### 自定义头像 获取要上传的头像的id

>  **cmd**

  `get_custom_avatar_id`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                        |
|---------------|----------|----------------------------|
| image_md5     | string   | 要上传的图片的md5值        |
| image_size    | int      | 要上传的图片的二进制大小   |
| image_suffix  | string   | 要上传的图片的后缀         |

---

### 自定义头像 上传成功后使用自定义头像

>  **cmd**

  `apply_custom_avatar`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                |
|---------------|----------|--------------------|


---

### 自定义头像 op接口 下架

>  **cmd**

  `op_remove_custom_avatar`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                      |
|---------------|----------|--------------------------|
| custom_avatar | string   | 该玩家要下架的头像id     |

---


### 自定义头像 举报头像

>  **cmd**

  `report_player_avatar`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name      | val_type | des                |
|---------------|----------|--------------------|
| report_key    | long     |  举报人uid         |
| reported_key  | long     |  被举报人uid       |
| report_reason | string   |  举报理由          |
| custom_avatar | string   |  头像id            |
| extra_info    | object   |  额外信息          |
```
extra_info
{
  "reported_name": string //被举报人名称
}
```

---
#### 工头升阶
>  **cmd**

`foreman_stage_upgrade`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id         | int      |  工头id       |

---
#### 上阵工头
>  **cmd**

`set_foreman`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id         | int      |  工头id       |
| building_id| int      |  建筑id       |
| slot_id    | int      |  槽位id       |

---
#### 抽取招募工头
>  **cmd**

`foreman_summon`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| item_id    | int      |  道具id      |
| num        | int      |  数量[1或10]       |
| type       | int      |  召唤类型[4工头普通召唤]       |

---

#### 合成解锁工头
>  **cmd**

`compose_foreman`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id    | int      |  工头id       |

---

#### 领取城外工头
>  **cmd**

`claim_wait_foreman`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id    | int      |  工头id       |

---

#### 玩家私发邮件
>  **cmd**

`mail_send_by_id_private`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| mail       | int      |  邮件内容       |
| receiver   | int      |  发送人信息       |
| sender     | int      |  目标信息       |
| reward_list| int      |  奖励       |
| anti_harass_uid     | int      | 发送对象uid防骚扰检测，无检测需要就填0     |


---

#### 运营创建全服个人BOSS接口
>  **cmd**

`create_server_personal_boss`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| event_id   | string   |  活动ID       |
| begin_time | int      |  活动开始时间  |
| close_time | int      |  活动结束时间  |
| personal_boss_key | int      |  怪物key  |


---

#### 获取后台个人boss数据接口
>  **cmd**

`get_server_personal_boss_data`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| event_id   | string   |  活动ID       |

---

#### 新手七日 领取bp奖励
>  **cmd**

`claim_new_player_quest_bp_reward`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc                            |
|:-----------|:---------|:--------------------------------|
| id         | int      | 奖励下标,从1开始 -1表示领取所有 |

---

#### 英雄装备 提升英雄装备专精等级
>  **cmd**

`hero_equip_sp_lv_up`

> **main_push**:

`player`

>  **param**:

| key_name         | val_type | desc                      |
|:-----------------|:---------|:--------------------------|
| equip_svr_id     | int      | 装备id                    |
| cost_equip_list  | array    | 需要消耗的金色装备id列表  |
| cost_list  | object    | 需要消耗的道具列表  |
```
cost_list
{
  "id": num //道具id和数量
}
```

---

#### 竞技场优化 刷新竞技场匹配对手
>  **cmd**

`refresh_arena_match_result`

> **main_push**:

`player`

>  **param**:

| key_name         | val_type | desc                      |
|:-----------------|:---------|:--------------------------|
| cost_gem         | int      | 花费X宝石                 |

> 反包
+ svr_arena_match_result
+ svr_arena_user_data
{
    "score": int,
    "real_time_rank": int
    "refresh_times": int,	// 今日已经刷新的次数
    "next_refresh_time": long,,	// 下次重置刷新的时间点
}
---

#### 恢复领主

>  **cmd**

  `treat_lord`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|

---

#### 勇士战令活动领取任务分数

>  **cmd**

  `op_get_event_score`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| list      | array      | 活动信息 |
| event_extra_info      | object      | 活动数据 |



```json
{
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":
  {
    "fight_token":{
        "task_type": int,                 // 任务类型： 0-每日任务；1-目标任务
        "index"：int                      // 领取的任务在数组中的下标（从 0 开始）； -1 表示一键领取；
    }
  }
}

```
---


#### 新洛哈 领取goal奖励

>  **cmd**

  `claim_new_joy_event_goal`

> **main_push**:

  `player`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| event_id  | string   | 活动id                 |
| index     | int      | 固定=1                 |

#### 一键执行

>  **cmd**

  `execute_radars`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|

---

#### 前往帮助盟友任务

>  **cmd**

  `dispatch_help_radar`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| task_id      | int      | 任务id |

---

#### 派出雷达队列执行雷达任务

>  **cmd**

  `dispatch_common_radar_queue`

> **main_push**:

  `game_server`

>  **param**:

| key_name  | val_type | desc                   |
|:----------|:---------|:-----------------------|
| task_id      | int      | 任务id |

---

#### 雷达联盟挖掘分享锁地形请求
> **cmd**

`radar_al_collect_lock_wild`

> **main_push**

`chat_index_mgr`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| unique_id             | string   | 地形唯一ID                              |

---

#### 一键领取每日任务
> **cmd**

`claim_all_daily_quests`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| ids             | array   | 任务ids                              |
```json
{
  "ids":["task_id"],
}
```
---

#### 隐秘指挥所（派遣任务） 派遣英雄队列
> **cmd**

`dispatch_hero`

> **main_push**

`game_server`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| task_seq              | int      | 后台id                     |
| hero_list             | array    | 英雄列表                   |

---

#### 隐秘指挥所（派遣任务） 批量派遣英雄队列
> **cmd**

`batch_dispatch_hero`

> **main_push**

`game_server`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| req_list              | list     | 请求派遣列表                |

req_list:[
  task_seq: int
  hero_list:[int]
]

---

#### 隐秘指挥所（派遣任务） 获取任务信息
> **cmd**

`get_dispatch_task_info`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|

---

#### 隐秘指挥所（派遣任务） 领取任务奖励
> **cmd**

`claim_dispatch_task_reward`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| task_seq              | int      | 后台任务id                 |
| unique_id             | string   | 建筑unique_id                 |

---

#### 隐秘指挥所（派遣任务） 批量领取任务奖励
> **cmd**

`batch_claim_dispatch_task_reward`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| req_list              | list     | 请求领取列表                 |

req_list:[
  task_seq:int,
  unique_id:string
]
---

#### 隐秘指挥所（派遣任务） 生成任务对应建筑
> **cmd**

`search_dispatch_task_building`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| task_seq              | int      | 后台内部id                 |

---

#### 隐秘指挥所（派遣任务） 掠夺
> **cmd**

`rob_dispatch_task`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| task_seq              | int      | 后台内部id                 |
| target_uid            | int      | 目标玩家的uid              |

---


#### 隐秘指挥所（派遣任务） 帮助
> **cmd**

`help_dispatch_task`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| task_seq              | int      | 后台内部id                 |
| target_uid            | int      | 目标玩家的uid              |

---

#### 隐秘指挥所（派遣任务） 发送表情
> **cmd**

`send_dispatch_task_emoji`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| emoji                 | int      | 表情id                     |
| report_id             | int      | 后台内部报告id             |
| target_uid            | int      | 目标玩家的uid              |

---

#### 隐秘指挥所 获取历史任务报告
> **cmd**

`get_history_task_report`

> **main_push**

`ds_player`

> **param**

---

#### 隐秘指挥所 增加任务可见性
> **cmd**

`add_dispatch_task_visibility`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| task_seq              | int      | 后台内部id                 |
| target_uid            | int      | 目标玩家的uid              |

---

#### 隐秘指挥所（派遣任务） 超级刷新
> **cmd**

`refresh_dispatch_task_super`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                        |
|-----------------------|----------|----------------------------|
| gems                  | int      | 宝石数量                   |
| item_num              | int      | 道具数量                   |
| quality              | int      | 品质                   |

---



#### 加入黑名单
> **cmd**

`blackuser_add`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|avatar_id              | int      |          头像                     |
|name                   | string   |          名称                     |
|uid                    | int      |          uid                      |
|custom_avatar          | string   |         自定义头像                 |
|head_frame             | int      |         头像框                     |

---

#### 交换水晶
> **cmd**

`player_crystal_exchange`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|crystal_slot_id_1        | int   |          水晶槽位id1                     |
|crystal_slot_id_2        | int   |          水晶槽位id1                     |
|equip_slot_id_1          | int   |          装备槽位1                     |
|equip_slot_id_2          | int   |         装备槽位2               |

---

#### 领取建筑投放的工头
> **cmd**

`claim_building_foreman`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|building_type          | string      |             数值建筑type           |


---

#### 领取建筑礼物
> **cmd**

`click_building_gift`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|id_list          | array      |             建筑id列表           |

---

#### 佣兵荣耀更换求助boss
> **cmd**

`mercenary_glory_change_help`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|unique_id              | string   |         求助的boss id           |
|user_info              | string   |         用户信息 聊天展示         |
---

#### 干扰陷阱捐献
> **cmd**

`boss_trap_donate`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|num                    | int   |         捐献数量         |
| trap_idx   | int32     | 第几个陷阱 | 
---

#### 自己收藏发车记录
> **cmd**

`car_record_collect`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|rid                    | int      |         记录id                    |
|keep                   | int      |         0取消收藏 1收藏           |
---

#### 货车刷新
> **cmd**

`refresh_truck`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|qid                    | int   |         队列id         |

---

#### 货车发车
> **cmd**

`start_truck`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|qid                    | int   |         队列id         |
|march_info             | array   |         阵容信息         |

```json
{
  "march_info":[{
    "troops":{"id":num},
    "heros":[id]
  }],
}
```
---

#### 领取货车奖励
> **cmd**

`claim_truck_reward`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|qid                    | int   |         队列id         |

---

#### 获取货车详情数据
> **cmd**

`get_truck_detail`

> **main_push**

`ds_compute`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|unique_id              | string   |        unique_id         |
|sid                    | int   |         sid         |

---
#### 道具召唤火车
> **cmd**

`summon_train`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|

---
#### 刷新奖励
> **cmd**

`refresh_train`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|train_id               | int   |         火车id         |
|train_key              | int   |         火车数值表train里的id         |


---
#### 任命车头
> **cmd**

`appoint_captain`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|train_id               | int      |         火车id         |
|target_uid             | int      |         target_uid         |

---
#### 车头改队列英雄阵容
> **cmd**

`change_train_hero_queue`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|train_id               | int      |         火车id          |
|queue_id               | int      |         队列id,三条队列的id，从1开始         |
|queue_data             | int      |         队列数据         |

```queue_data
{
  {
    "heros":[
      int   // hero id列表
    ],
    "soldier":{id:num}
  }
}
```
---

#### 排队
> **cmd**

`get_on_train`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|train_id               | int      |         火车id         |
|carriage_id            | int      |         车箱id 从1开始         |

---
#### 获取火车详情数据
> **cmd**

`get_train_detail`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|unique_id              | string      |         unique_id              |
|sid                    | int      |         sid                       |

---
#### 搜索
> **cmd**

`search_car`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|cur_objs               | array    |     当前结果                      |
|refresh                | int      |     是否刷新 0不刷新 1刷新        |
|ignore                 | int      |     忽略本服 0不忽略 1忽略        |

```json
{
  [{
    "sid":int,
    "obj_id":""
  }],
}
```
---
#### 通缉玩家
> **cmd**

`wanted_player`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|target_uid                    | int   |         uid         |

---
#### 掠夺
> **cmd**

`rob_car`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|unique_id              | string   |         掠夺         |
|march_info             | array   |         阵容信息         |
|sid                    | int     |         对面的sid        |

```json
{
  "march_info":[{
    "troops":{"id":num},
    "heros":[id]
  }],
}
```
---

#### 货车和火车获取其他玩家的发车记录
> **cmd**

`get_car_record`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|target_uid             | int      | 目标玩家uid                       |
|rid                    | int      |         记录id                    |
---

#### 荣耀远征战斗
> **cmd**

`travel_fighting`

> **main_push**

`ds_compute`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|id                     | int      |          战场id                   |
|lv                     | int      |         等级                      |
|hurdle_id              | int      |         关卡id                    |
|hero_id                | int      |         勇士战令英雄id             |
|march_info             | array   |         阵容信息         |

```json
{
  "hurdle_id": -1, // 快速战斗填-1
  "march_info":[{
    "troops":{"id":num},
    "heros":[id]
  }],
}
```

---

#### 荣耀远征选择难度
> **cmd**

`select_honor_dungeon`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                               |
|-----------------------|----------|-----------------------------------|
|id                     | int      |          战场id                   |
|lv                     | int      |          等级                     |

---

#### 联盟对决跨服移城

>  **cmd**

  `alliance_duel_svr_move_city`

> **main_push**:

  `game_server`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|event_id  | string      | 活动id |
|tar_sid  | int      | 目标sid |
|tar_pos  | int      | 目标坐标 |

---
#### 获取联盟对决移城位置

>  **cmd**

  `alliance_duel_get_alliance_pos`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
|----------|----------|------|
| target_sid      | int      | 服id |
| target_aid      | int      | 联盟id |

---

#### 设置驻防英雄

>  **cmd**

  `city_wall_set_heros`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|heros   | object   | 驻防队列英雄列表     |

```json
{
  "heros": {
    "id":{ // 队列id
      "${slot}": int, 
      ...
    }
  }
}
```
---

#### 使用龙魂

>  **cmd**

  `use_dragon_soul`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|id          | int      | 龙魂id     |

---

#### 设置龙魂自动存储玩法

>  **cmd**

  `set_dragon_soul_mode`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|switch      | int      | 开关（0-关 1-开）     |

---

#### 变更建筑功能玩法

>  **cmd**

  `change_building_mode`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|building_svr_id | int      | 后台建筑id    |
|building_type   | int      | 转换目标建筑类型    |
|cost_gems   | int      | 消耗宝石数量    |


---

#### 获取单人攻打城市战斗报告详情

>  **cmd**

  `get_city_battle_report`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|id          | string   | 报告id     |

---
#### 清楚淤泥

>  **cmd**

  `clear_muck`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|pos_list          | array   | 淤泥位置列表     |
---

#### 设置英雄表演

>  **cmd**

  `set_hero_perform`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|id_list     | array    | 英雄id 列表    |

---

#### 一键布局，删除建筑

>  **cmd**

  `auto_layout`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|move_entity_list  | object    | 移动的建筑{"type":[{"id":xxxx,"pos":xxx}，{"id":xxx,"pos":xxx,}]}    |
|extra_buildings  | array    | 删除的建筑[id,id2]    |
---

#### 出发风暴任务

>  **cmd**

  `show_cycle_event`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|type  | int    | id    |

#### 获取联盟推荐

>  **cmd**

  `al_recommend_get`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|al_join_t   | int    | 加入联盟时间    |
|pay_num     | int    | 付费值    |
|castle_lv   | int    | 主城等级    |
|force       | int    | 战力    |
|need_limit  | int    | 是否需要限制    |
|ab_test     | int    | abtest版本号    |


#### 洪水来袭

>  **cmd**

  `flood_coming`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|

#### lvl治疗一键加速 v1.1.1

>  **cmd**

  `lvl_auto_speed_up_treatment`

> **main_push**:

  `ds_player`

>  **param**:

| key_name          | val_type     | desc                   |
|:------------------|:-------------|:-----------------------|
| queue_type        | int          | 队列类型 0士兵 1陷阱    |
| cost_list         | array        | 消耗道具列表            |
| is_cost_gem       | int          | 0:使用道具 1:使用宝石   |
| cost_gem          | int          | 使用宝石数量            |

> **val_like**:

```json
"cost_list":[[0, 3526, 320]]		// [type, id, num] 道具type为0
```

---
#### 上阵\下阵工人
>  **cmd**

`set_worker`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id         | int      |  工人id       |
| building_id| int      |  建筑id（下阵填0）|
| furniture_id| int      |  家具id（下阵填0）|

---

#### 设置主城状态
>  **cmd**

`set_temperature_info`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| state       | object   |  主城状态       |



```json
"state":{
  "ignites":int,  // 0不开点燃 1开启点燃,
  "power":int,  // 0不开大功率 1开启大功率
}
```

---
#### 设置工人作息表开始时间（CG过后发送）
>  **cmd**

`set_p3_worker_init_time`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| timestamp  | int      |  CG跑完的时间戳|
---

#### 民意信箱 选择选项
>  **cmd**

`worker_help_choice`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc              |
|:-----------|:---------|:------------------|
| mail_id    | int      |  邮件id           |
| choice     | int      |  1:选项1 2:选项2  |
| type     | int      |  1:好评 2:差评 3:中庸  |

---

#### 民意信箱 领取奖励
>  **cmd**

`worker_help_reward`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc              |
|:-----------|:---------|:------------------|
| mail_id    | int      |  邮件id           |


---
#### 选择菜品
>  **cmd**

`select_dishes`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id       | int   |  菜品id       |

---

#### 选择菜品
>  **cmd**

`claim_p3_worker`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| type       | int   |  0:首次到来，1:普通领取 |
| choose     | int   |  对应首次到来的选项 |

---

#### 清理区域迷雾
>  **cmd**

`clear_area_fog`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id         | int      |  迷雾id       |


---
#### 邮件领取并删除
>  **cmd**

`mail_reward_collect_delete`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| class      | int      |  邮件类别     |
| id_list    | array    |  邮件id列表   |

#### 竞技场战斗开始(临时流程)
>  **cmd**

`arena_battle_without_reward`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| info      | object      |  与arena_battle的数据一致     |

#### 竞技场战斗结束(临时流程)
>  **cmd**

`arena_battle_with_reward`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| info      | object      |  与arena_battle的数据一致     |
|battle_input|object      | 战斗输入 |
|battle_output|object      | 战斗输出 |


#### 设置自动狩猎信息
>  **cmd**

`set_auto_hunting`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| info      | object      |  自动狩猎数据     |


```json
"info":{
  "lv":int,  // 自动狩猎野怪等级,
  "wound_limit":int,  // 伤兵限制
  "use_item":  // 自动使用体力道具限制信息
  {
    "6444":10
  }
}
```

#### 发起自动狩猎队列
>  **cmd**

`dispatch_auto_hunting`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id      | int      |  队列id     |
|march_info|object  | 行军携带的军队信息 {"soldier":{"1":100},"heros":{"1":42},"carry_lord":1,"queue_id":6001} |
|is_auto |int  | 0玩家主动 1客户端自动 |



#### 停止自动狩猎队列
>  **cmd**

`stop_auto_hunting`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id_list    | array    |  队列id列表   |


#### 连接建筑
>  **cmd**

`connect_building`

> **main_push**:

`ds_player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| svr_id    | int    |  建筑id   |

---

#### 联盟商店购买

>  **cmd**

  `buy_al_shops`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | des                                  |
| ------------ | -------- | ------------------------------------ |
| id           | int32    | 商店id                               |
| goods_id     | int32    | 购买的商品id                          |
| buy_num      | int32    | 购买的数量                            |
---

#### 刷新联盟商店

>  **cmd**

  `refresh_al_shops`

> **main_push**:

  `ds_player`

>  **param**:


---

#### 雷达地图搜索
>  **cmd**

  `search_obj_radar`

> **main_push**:

  `game_server`

>  **param**:

| key_name          | val_type  | des                |
| ------------------| ----------| -------------------|
| task_id           | int       | 雷达任务数值id     |

---
#### 获取联盟捐献排行榜

>  **cmd**

  `get_al_donate_rank`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name   | val_type | desc         |
|:-----------|:---------|:-------------|
|id          | int   | 报告id     |

---

#### 自动集结 设置自动集结信息

>  **cmd**

  `set_auto_rally`

> **main_push**:

  `game_server`

>  **param**:

| key_name     | val_type | desc         |
|:-------------|:---------|:-------------|
|preset_troop  | object   | 编队信息     |
|target_type   | array    | 目标类型     |
|rally_mode    | int      | 0：预设编队 1：全兵加入     |
|online_switch | int      | 开关 0关闭 1开启 |
|preset_hero   | int      | 预设编队时，派遣的英雄id 其余时刻传0 |

---

#### 自动集结 设置预设

>  **cmd**

  `auto_rally_preset`

> **main_push**:

  `game_server`

>  **param**:

| key_name     | val_type | desc         |
|:-------------|:---------|:-------------|
|preset_troop  | object   | 编队信息     |
|preset_hero   | int      | 预设编队时，派遣的英雄id 其余时刻传0 |

---

#### 自动集结 停止生效功能 不改动开关

>  **cmd**

  `cancel_auto_rally`

> **main_push**:

  `ds_player`

>  **param**:

| key_name     | val_type | desc         |
|:-------------|:---------|:-------------|
|  |    |      |

---



#### 宝石购买

>  **cmd**

  `gem_purchase`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | desc     |
| :------------ | :------- | :------- |
| purchase_info | object   | 购买信息 |
| recharge_info | array    | 充值信息 |
| recharge_type | int      | 充值类型 |

### 1.1 保护罩

#### 使用充能保护罩

>  **cmd**

`use_recharge_peace_time`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |
|item_id  | int   | 使用的充能道具itemid     |

---
#### 律令

>  **cmd**

`active_sleep`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |
|id  | int   | 0入睡 2建造 3研究 4药到 5紧急 6高效 7节日 8资源     |
|data| object| {"res_type":int}资源类型     |
---

#### 翻译一个联盟标记信息
> **cmd**

`al_bookmark_translate`

> **main_push**

`ds_alliance`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| svr_id         | int      | 标记唯一标识 |
| target_lang_id | int      | 语种id      |
---

#### 修改建筑生产材料
> **cmd**

`change_produce_resource`

> **main_push**

`ds_alliance`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| building_id         | int      | 后台建筑id |
| res_id | int      | 资源类型      |
---

=======

### evip相关

#### 领取evip宝箱

>  **cmd**

  `evip_open_chest`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                                |
|------------|----------|------------------------------------|
| chest_id   | int      | 登陆宝箱：0, 等级专属宝箱：evip等级      |
| chest_type | int      | 0: 登陆宝箱，1: 等级专属宝箱            |

#### evip兑换商店购买

>  **cmd**

  `evip_shop_buy`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| id       | int      | 购买的兑换券id   |
| num      | int      | 购买的兑换券数量 |

=======

#### 普通装备重铸

>  **cmd**

  `reset_hero_equip`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| id       | int      | 后台装备id   |
=======

#### 装备专精等级重铸

>  **cmd**

  `reset_sp_hero_equip`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| id       | int      | 后台装备id  |
=======
---

#### 发起宣战
> **cmd**

`alliance_claim_war_holyland`

> **main_push**

`ds_alliance`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| unique_id      | string   | 建筑的地图id |
---

=======

#### 主城等级排行榜获取

>  **cmd**

  `get_castle_rank`

> **main_push**:

  `ds_compute`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| num       | int      | topX  |
| lv       | int      | 等级  |
=======

#### 获取iap排期预览

>  **cmd**

  `get_iap_schedule_preview`

> **main_push**:

  `op_svr`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| preview_time       | int   | 希望预览的时刻，时间戳格式，取输入日期 UTC的点  |
| pay_group_lv       | int   | 付费群体等级，约定：-1表示所有付费等级  |
| pack_group         | int   | 礼包分组，默认为0  |
| castle_lv          | int   | 主城等级  |
| sid          | int   | sid  |
=======

#### 装备展示切换

>  **cmd**

  `set_show_equip`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| show       | int   | 0不展示 1展示  |
=======

#### 获取餐桌用餐记录

>  **cmd**

  `get_dinner_meal_record`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| src_type       | int   | type  |
| src_id       | int   | id  |
| aid       | int   | aid  |
=======

#### 修改宴会预约开启时间

>  **cmd**

  `set_dinner_schedule_btime`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| list       | array    | 活动数据    |
| event_extra_info | object   | 请求信息 |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":{
      "dinner_party":{
          "type":1, //0-直接开启  1-预约开启
          "begin_time":int64, //预约开启的时间
      }
  }
```

=======

#### 立即开启宴会

>  **cmd**

  `start_dinner`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| list       | array    | 活动数据                  |
| event_extra_info | object   | 请求信息                  |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":{
      "dinner_party":{
          "type":0, //0-直接开启  1-预约开启
          "begin_time":int64, //预约开启的时间
      }
  }
```


=======

#### 获取附近餐桌/获取最新iap餐桌

>  **cmd**

  `get_near_dinner_table`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| type | int   | 0获取附近餐桌 1获取最新iap餐桌  |


=======

#### 建造宴会建筑

>  **cmd**

  `create_dinner_building`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| key_name   | val_type | desc                     |
| :--------- | :------- | :----------------------- |
| list       | array    | 活动数据                  |
| event_extra_info      | object   | 请求信息       |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":{
      "party_postion": int // 宴会位置信息
  }
```
=======

#### 拆除宴会建筑

>  **cmd**

  `remove_dinner_building`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| unique_id | string   | unique_id  |

=======


#### 派遣用餐

>  **cmd**

  `dispatch_table`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| tar_type | int   | tar_type  |
| tar_id | int   | tar_id  |

=======

---

#### 一键领取每日任务和奖励
> **cmd**

`claim_all_daily_quests_and_reward`

> **main_push**

`ds_player`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| ids                   | array   | 任务ids                                  |
| claim_stage_list      | array   | 领取的活跃度阶段宝箱列表                   |
```json
{
  "ids":["task_id"],
  "claim_stage_list":[int],    // 内容参考claim_daily_quest_active_reward的claim_stage即可，注意领取列表要计算待领取的任务活跃度
}
```
#### 升阶到指定阶级
>  **cmd**

`hero_stage_up_to_tar`

> **main_push**:

`player`

>  **param**:

| key_name   | val_type | desc          |
|:-----------|:---------|:--------------|
| id    | int      | 目标英雄id    |
| stage | int    | 目标阶级 |

---

#### 开启英雄招募宝箱

>  **cmd**

  `open_hero_summon_score_chest`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
|          |          |      |

---

#### 联盟总动员宝石立即刷新任务

>  **cmd**

  `refresh_event_task_instant`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| event_id | string  | event_id |
| task_key | int  | 任务位置 |
| cost_gem | int  | 消耗宝石 |


---

#### 冻土活动领取奖励

>  **cmd**

  `claim_frozen_event_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| goal_index | int  | 任务位置 |
| goal_type | int  | 0-阶段奖励 1-勋章奖励 |
| list | array  | list |

---

#### 一键领取联盟礼物

>  **cmd**

  `open_al_gift_all_new`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| al_gift_lv | int  | 联盟礼物等级 |
| type | int  | 1-普通 2-iap |


---

#### 领取多个联盟礼物

>  **cmd**

  `open_al_gifts`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| ids | array  | 礼物id列表 |
| al_gift_lv | int  | 联盟礼物等级 |
| type | int  | 1-普通 2-iap |

---

#### 转让群主身份 直发聊天服务器

>  **cmd**

  `chat_group_change_owner`

> **main_push**:

  `chat_index_mgr`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| group_id   | string  | 群聊id |
| uid        | int     | 目标玩家id |
---

#### 联盟简介翻译

>  **cmd**

  `al_desc_translate`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| target_lang | int  | 目标语言 |
| aid | int  | 目标联盟id |

#### 其他联盟简介翻译

>  **cmd**

  `other_al_desc_translate`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| target_lang | int  | 目标语言 |
| aid | int  | 目标联盟id |

#### 领取干扰陷阱生涯goal

>  **cmd**

  `claim_boss_trap_user_life_goal_reward`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| pid      | int  | 目标pid |
| target   | int  | 目标分数 |

#### 隐秘任务查看浮层

>  **cmd**

  `watch_dispatch_task`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| target_uid      | int  | 目标uid |
| task_seq      | int  | 后台任务seq |
| src_type      | int  | 固定160 隐秘建筑type |
| src_id   | int  | 实体id |

#### 跨服竞技场每日宝箱领取

>  **cmd**

  `multi_arena_target_reward_claim`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |

#### 地心探险攻打关卡请求

>  **cmd**

  `earth_core_fighting`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| id       | int      | 关卡id |
| queue_data | array  | 玩家队列信息 |

```json
{
  "queue_data":[
    {
      "heros":[int]
    }
  ]
}
```

#### 地心探险正常兵的快照保存

>  **cmd**

  `earth_core_fight_soldiers_set`

> **main_push**:

  `ds_player`

>  **param**:

| key_name       | val_type | desc                             |
| :------------- | :------- | :------------------------------- |
| client_soldier | object   | 玩家正常状态的兵                 |
| type           | int      | 全局场景下：1, 正常挑战保存; 2, 快速挑战保存 |

```json
{
    "soldier_id":num,
}
```

#### 地心探险快速挑战

>  **cmd**

  `earth_core_challenge_quick`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | desc             |
| :--------- | :------- | :--------------- |
| start_id   | int      | 开始的关卡id     |
| queue_data | array    | 玩家最强队列信息 |

```json
{
  "queue_data":[
    {
      "heros":[int]
    }
  ]
}
```

#### 地心探险扫荡

>  **cmd**

  `earth_core_challenge_sweep`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc   |
| :------- | :------- | :----- |
| scene_id | int      | 场景id |

#### 地心探险一键领取goal奖励

>  **cmd**

  `earth_core_claim_goal_all`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
|          |          |      |

#### 添加联盟公告

>  **cmd**

  `al_notice_add`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| notice_content  | string  | 公告内容  |

#### 更改联盟公告

>  **cmd**

  `al_notice_update`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| notice_content  | string  | 公告内容  |
| notice_id  | int  | 公告id  |

#### 获取联盟公告

>  **cmd**

  `al_notice_get`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |

#### 删除联盟公告

>  **cmd**

  `al_notice_delete`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc |
| :------- | :------- | :--- |
| notice_id  | int  | 公告id  |
---
#### 修改宴会预约开启时间

>  **cmd**

  `set_dinner_schedule_btime_new`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| list       | array    | 活动数据    |
| event_extra_info | object   | 请求信息 |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":{
      "dinner_party":{
          "type":1, //0-直接开启  1-预约开启
          "begin_time":int64, //预约开启的时间
      }
  }
```

=======

#### 立即开启宴会

>  **cmd**

  `start_dinner_new`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| list       | array    | 活动数据                  |
| event_extra_info | object   | 请求信息                  |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":{
      "dinner_party":{
          "type":0, //0-直接开启  1-预约开启
          "begin_time":int64, //预约开启的时间
      }
  }
```


=======

#### 获取附近餐桌/获取最新iap餐桌

>  **cmd**

  `get_near_dinner_table_new`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| type | int   | 0获取附近餐桌 1获取最新iap餐桌  |


=======

#### 建造宴会建筑

>  **cmd**

  `create_dinner_building_new`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| key_name   | val_type | desc                     |
| :--------- | :------- | :----------------------- |
| list       | array    | 活动数据                  |
| event_extra_info      | object   | 请求信息       |

```
  "list":[
      {
          "event_id": string,
          "event_type": int
      }
  ],
  "event_extra_info":{
      "party_postion": int // 宴会位置信息
  }
```
=======

#### 拆除宴会建筑

>  **cmd**

  `remove_dinner_building_new`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| unique_id | string   | unique_id  |

---
=======

#### 领取社区活动奖励

>  **cmd**

  `claim_event_portal_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|

---
=======

#### 拉取全部联盟报告

>  **cmd**

  `get_all_al_report`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|

---
=======

#### 拉取联盟隐秘任务

>  **cmd**

  `get_al_dispatch_task`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|

---

---
=======

#### 开食材宝箱

>  **cmd**

  `open_food_chest`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name  | val_type | desc     |
|:----------|:---------|:---------|
| extra | object      | 宝箱数据 |

```
  "extra":{
      "event_type": int, // 活动类型 126-做菜活动 136-装饰圣诞树
      "chest_id": int  // 宝箱id
      "chest_num": int // 宝箱数量
  }
```




---

#### 英雄招募

>  **cmd**

  `hero_summon`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |
| item_id  | int      | 招募道具id                     |
| num      | int      | 招募数量                       |
| type     | int      | 招募类型(0高级招募，6普通招募) |
| cost_type | int      | 花费类型(0花费道具，1花费宝石(优先扣宝石，剩下的花宝石)) |

---

#### 领取首充奖励

>  **cmd**

  `claim_first_recharge_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |
| type  | int      | 0首充奖励 1次日奖励                 |
---

#### 发送集结邀请聊天横幅

>  **cmd**

  `send_invite_rally`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |
| uid_list  | array      | 邀请uid列表                 |
| unique_id  | string      | 集结unique_id                 |
| type  | int      | 类型,透传回去给客户端的【区分战场还是大地图等】|
| etime  | int      | 集结结束时间|

#### 拉取下期排期奖励信息

>  **cmd**

  `get_fort_proj_reward_info`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |

#### 联盟分配堡垒奖励

>  **cmd**

  `alloc_fort_reward`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |
| id  | int      | 堡垒id                 |
| index  | int      | 奖励类型【1击败奖励  2占领奖励】      |
| uids  | array      | 分配数据 |

```
  "uids":[
    {
      "uid":$uid,
      "count":分配数量
    }
  ]
```

---

#### 联盟成员主动代替盟主

>  **cmd**

  `al_replace_chancellor`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc         |
| :------- | :------- | :----------- |
| cost_gem | int      | 花费的宝石数 |

---



#### 设置联盟堡垒报名展示待办项

>  **cmd**

  `set_fort_sign_info_show_todo`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |
| id  | int      | 堡垒id      |
| show_todo  | int      | 0不展示 1展示 |


---



#### 获取堡垒争夺奖励分配记录

>  **cmd**

  `get_fort_reward_alloc`

> **main_push**:

  `ds_alliance`

>  **param**:

| key_name | val_type | desc                           |
| :------- | :------- | :----------------------------- |

---

#### 联盟群发信息接口

> **cmd**

`al_group_chat_message_send`

> **main_push**

`ds_alliance`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| uid_list       | array    | 玩家列表    |
| msg_info       | string   | 聊天通知内容    |
| user_info      | string   | 与chat_message_send一致    |
| time      | int   | 客户端时间戳us    |

---
#### 拉取联盟报告

> **cmd**

`get_al_record_page`

> **main_push**

`al_record_svr`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| tab_type       | int      | 1 战斗 2 活动 3 恶魔 4 成员 5 消息 |
| pre_svr_id     | int      | 传0就是最新的，或者就是拉这个svr_id之前的num数量    |
| num            | int      | 请求拉取的数量    								  |

---
#### 设置驻守英雄能否出城开关

> **cmd**

`set_city_wall_defend_flag`

> **main_push**

`ds_player`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| flag       | int      | 0 关闭 1 开启   							  |

---

#### 竞技场挑战券购买

> **cmd**

`arena_items_buy`

> **main_push**

`ds_player`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| item_id       | int      | 道具id   							  |
| item_num       | int      | 购买数量  							  |

---

#### 设置重伤龙行军特效可见状态

> **cmd**

`set_show_dragon_effect`

> **main_push**

`ds_player`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| show       | int      | 1不展示 0展示   							  |


---

#### 银行储蓄

> **cmd**

`bank_saving`

> **main_push**

`ds_player`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| slot       | int      | 储蓄罐槽位   							  |
| num       | int      | 宝石数量   							  |


---

#### 取出银行储蓄

> **cmd**

`take_out_bank_saving`

> **main_push**

`ds_player`

> **param**

| key_name       | val_type | des        |
|----------------|----------|------------|
| slot       | int      | 储蓄罐槽位   							  |

#### 点券充值 v1.7.6
>  **cmd**

  `gem_recharge_by_pay_point_coupon`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| recharge_type | int      | 参照充值参数 |
| recharge_info | object   | 参照充值参数 |
| purchase_info | object   | 参照充值参数 |
| point_coupon_id | int    | 点券id       |
| point_coupon_num| int    | 点券数量    |

---

#### 第三方支付获取链接 v1.7.6
>  **cmd**

  `appcharge_gem_recharge`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| recharge_type | int      | 参照充值参数 |
| recharge_info | object   | 参照充值参数 |
| purchase_info | object   | 参照充值参数 |
| deep_link 	| string   | 链接         |

---

#### 第三方支付实际支付回调 v1.7.6
>  **cmd**

  `appcharge_gem_recharge_response`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| meta_data | object      | 参照充值参数 |
| purchase_id | string   | 支付id |

```
{
  "purchase_info":{},
  "recharge_info":{},
  "user_info":{}
}
```
---


#### 升级宠物天赋 v1.7.6
>  **cmd**

  `pet_talent_upgrade`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| id            | int      | 宠物id   |
| talent_id     | int      | 天赋id |
| level         | int      | 目标等级  |
| cost_list     | array    | 消耗资源 [[type, id, num]] |
| type          | int      | 类型 0 1（立即完成）    |
| instant_gem   | int      | 立即完成的宝石数    |
| queue_id      | int      | 队列id 1或2   |

---

#### 领取天赋完成升级 v1.7.6
>  **cmd**

  `pet_talent_claim`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| id            | int      | 宠物id   |
| talent_id     | int      | 天赋id |

---

#### 加速升级宠物天赋 v1.7.6
>  **cmd**

  `pet_talent_speedup`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| action_id     | int      | 天赋action id |
| is_cost_gem   | int      | 是否使用宝石 0用道具 1用宝石加速 2立即完成 |
| cost_gem      | int      | 使用宝石数量   |
| cost_list     | array    | 消耗道具列表[[type, id, num]]    |

---

#### 取消升级宠物天赋 v1.7.6
>  **cmd**

  `pet_talent_cancel`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| action_id     | int      | 天赋action id |

---

#### 宠物进化 v1.7.6
>  **cmd**

  `pet_stage_upgrade`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| id            | int      | 宠物id |
| stage         | int      | 阶段 |

---

#### 使用宠物技能 v1.7.6
>  **cmd**

  `use_pet_skill`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| id            | int      | 宠物id |
| skill_id      | int      | 技能id |

---

#### 宠物勋章升级 v1.7.6
>  **cmd**

  `pet_medal_upgrade`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| id            | int      | 宠物id |

---

#### 兑换物品 v1.7.6
>  **cmd**

  `sub_exchange_reward`

> **main_push**:

  `ds_player`

>  **param**:

| key_name      | val_type | des                                                                   |
|---------------|----------|-----------------------------------------------------------------------|
| type          | int      |   消耗的内容type|
| id            | int      |   消耗的内容id|
| index         | int      |   兑换的物品下标 从1开始|
| num           | int      |   兑换次数|

---

#### 购买并使用实验品 v1.7.6

>  **cmd**

  `buy_and_use_sample`

> **main_push**:

  `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| pid        | int      | pid                     |
| good_index | int      | 宝物索引                |
| cost_list  | array    | 购买消耗(type, id, num) |

---

#### 使用立即完成道具 v1.7.6

>  **cmd**

 `use_instantly_finish_item`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| item_id  | int    | 立即完成道具id |

---
---
#### 自动分配工人设置

>  **cmd**

  `auto_set_worker_set`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | desc         |
|:---------|:---------|:-------------|
| switch  | int      | 功能开关(0:关 1:开) |
| set_flag  | int    | 本次登录是否生效(0:关 1:开) |

#### 解锁雷达
>  **cmd**

  `unlock_radar`

> **main_push**:

  `ds_player`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |

---
#### 发送一条消息
> **cmd**

`chat_message_send_noti`

> **main_push**

`chat_index_mgr`

> **param**

| key_name              | val_type | des                                     |
|-----------------------|----------|-----------------------------------------|
| channel_id            | string   | channel_id                              |
| timestamps            | string   | 微秒时间戳                              |
| msg_type              | int      |                                         |
| content               | string   | 若msg_type == report，格式为客户端自定义 |
| user_info             | string   | 用于反包 见proto中的ChatMsgItem         |
| is_whisper            | int      | 0: 不是，1:是                            |
| whisper_receiver_name | string   |                                         |
| content_info          | string   | 对于玩家发出的content做的额外数据记录，纯客户端使用 |
| anti_harass_uid       | int      | 发送对象uid防骚扰检测，无检测需要就填0     |
| anti_harass_type      | int      | 发送对象type防骚扰检测，无检测需要就填0     |
| not_translate         | int      | 是否不需要翻译     |
| notification_info     | object   | 推送     |
```json
目前只在联盟集结邀请时使用
客户端参数和chat_message_send一致，只是后台内部多走一步推送
```

---
### 佣兵荣耀预约开启

> **cmd**

`mercenary_glory_start_alliance_challenge_schedule`

> **main_push**:

  `game_server`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
| list | array | 运营协议      |
| extra | object | 运营协议      |

```json
// 以运营协议为准 以下为参考
{
  "list":[
    {
      "event_id":string,
      "event_type"int //  佣兵荣耀联盟服 - 70
    }
  ],
  "extra":
  {
    "al_begin_time": int64, //  开启时间
    "level": int //选择的等级
  }
}
```
--- 

#### 编辑装备预设 v1.9.1

>  **cmd**

 `update_equip_preset`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| id  | int    | 预设id |
| slot  | int    | 修改的槽位 |
| pid  | int    | buff方案id |

---

#### 编辑水晶预设 v1.9.1

>  **cmd**

 `update_crystal_preset`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| id    | int    | 预设id |
| slot  | int       | 修改的装备槽位 |
| cry_slot  | int    | 水晶槽位 |
| cry_id  | int    | 水晶id 0表示卸下|


---

#### 替换水晶预设 v1.9.1

>  **cmd**

 `exchange_crystal_preset`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| id    | int    | 预设id |
| slot  | int       | 装备槽位 |
| cry_slot  | int    | 水晶槽位 |
| slot_1  | int       | 水晶原来所在装备槽位 |
| cry_slot_1  | int    | 水晶原来槽位 |


---
#### 修改装备和水晶预设名称 v1.9.1

>  **cmd**

 `rename_equip_crystal_preset`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| id  | int    | 预设id |
| name  | string    | 预设名称 |


---

#### 使用装备和水晶预设 v1.9.1

>  **cmd**

 `use_equip_crystal_preset`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| id  | int    | 预设id |

---

#### 更换buff方案 v1.9.1

>  **cmd**

 `change_equip_buff_pid`

> **main_push**:

 `ds_player`

>  **param**:

| key_name   | val_type | des                     |
| ---------- | -------- | ----------------------- |
| slot_id  | int    | 槽位id |
| pid  | int    | 方案id |

---

#### 拉取恶魔入侵的可支援的联盟主城信息
>  **cmd**

  `get_demon_exorcist_city_list`

> **main_push**:

  `svr_demon_exorcist_city`

>  **param**:

| key_name | val_type | des  |
| -------- | -------- | ---- |
|          |          |      |



---

#### 获取排行榜的某个榜单信息

>  **cmd**

`rank_other`

> **main_push**:

`rank_player`

>  **param**:

| key_name  | val_type | desc                               |
| --------- | -------- | ---------------------------------- |
| key0      | int      | 排行榜类别                         |
| rank_type | int      | 排行榜范围（0-单服 1-临服 2-全服） |
| key1      | int      | 此类排行榜的榜单id                 |

---

#### web商店充值

>  **cmd**

`op_web_iap_recharge`

> **main_push**:

`rank_player`

>  **param**:

| key_name  | val_type | desc                               |
| --------- | -------- | ---------------------------------- |
| trans_id              | string      | 支付唯一凭证,平台组保证全平台唯一       |
| paid_virtual_good_sku | string      | 购买的付费内容sku                     |
| price                 | int         | 原价,美分                            |
| promo_code            | string      | 促销码,不使用促销码时传空              |
| external_id           | string      | 外部id,不使用促销码时传空              |

---


#### 联盟争霸赛报名

>  **cmd**

`alliance_struggle_sign_up`

> **main_push**:

`rank_player`

>  **param**:
| key_name  | val_type | desc                               |
| --------- | -------- | ---------------------------------- |
| carry_lord   |  int      |                                  |
| extra        | object    |                                  |
| heros        | object    |                                  |
| list         | array     |                                  |
| troop_info   | object    |                                  |
| equip_preset | object    |    装备预设id,没有则不填这个字段    |

---

#### 设置开启转换安全资源

>  **cmd**

`set_produce_resource`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |
|flag  | int   | 0关闭 1开启 |
---

#### 设置付费sdk上报状态

>  **cmd**

`recharge_sdk_report`

> **main_push**:

`player`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |
|status  | int   | 1:开始上报 2:上报完成 |
---

#### 设置web商店订单的上报状态

>  **cmd**

`web_recharge_report`

> **main_push**:

`common_record_svr`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |
|trans_id  | string   | 订单id |
|status  | int   | 1:开始上报 2:上报完成 |
---

#### 拉取web商店订单的上报状态

>  **cmd**

`web_recharge_get`

> **main_push**:

`common_record_svr`

>  **param**:

| key_name | val_type | desc |
|----------|----------|------|
|          |          |      |
---