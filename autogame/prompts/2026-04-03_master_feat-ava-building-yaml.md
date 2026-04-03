# Prompt Record

- Date: 2026-04-03
- Branch: master
- Commit: feat: 提取 AVA 战场建筑数据到 doc_lvl_building.yaml (含得分规则/效果/map_type映射)

---

### 1. 查看 Mercenary Camp 信息

看一下 mercenary camp 在document_english.json中的信息

> **Insight**
> 1. 佣兵营是 AVA 副本中的战略建筑：占领后可对敌方占领的建筑发起佣兵打击，削弱敌方攻防，是一种"非行军"的远程骚扰手段
> 2. 权限控制：只有驻防队长（Garrison Leader）能指派佣兵，AI 系统中需要识别谁是队长才能执行此操作
> 3. 建筑 ID 969 是关键字段，在地图数据同步（doc_tile）和命令字系统中都用这个 ID 标识佣兵营

### 2. 查看 doc_tile 全部信息

doc_tile里面有什么信息，除了建筑还有其他吗

> **Insight**
> 1. doc_tile 是地图渲染层：它定义了地图上每个格子"是什么"——从地形到建筑到野怪都涵盖
> 2. AVA 副本建筑集中在 ID 951~975 区间
> 3. ID 编号有规律：资源类 113xxx、野怪 101xxx、僵尸营地 362xxx

### 3. 提取 AVA 建筑数据到 YAML

把关于ava战场建筑的信息： doc_lvl_building, doc_lvl_building_info， 保存到同一个yaml文件

**Files:** `docs/p10/doc_lvl_building.yaml`

### 4. 补充建筑得分规则和效果

document_english里面有记录每个建筑的首占得分、持续占领得分、特殊效果吗？提取出来加入yaml

> **Insight**
> 1. document_english.json 只存文字描述，不存数值：首占得多少分等数值由服务器端配置表决定
> 2. 建筑效果具有联动性：先占 Boiler House 缩短占领时间 → 再占 Production Plant 更快 → 最后占 Steam Factory
> 3. Stable 是移城战术的关键：缩短免费迁城冷却，是 AI 系统中"移城无CD"策略的放大器

**Files:** `docs/p10/doc_lvl_building.yaml`

### 5. 补充 doc_map_wild 类型映射

有一个类型 10006 的建筑，好像没有出现在上面的yaml文档里面

> **Insight**
> 1. 三套 ID 体系的关联：doc_map_wild.map_type（sync 返回值）→ doc_tile.id（地图渲染）→ doc_lvl_building.id（建筑定义）
> 2. 10002 是"合并类型"：Boiler House 和 Arsenal 在 map_wild 中共用 type=10002（叫 Boost Building），服务器不区分具体是哪个加成建筑

**Files:** `docs/p10/doc_lvl_building.yaml`
