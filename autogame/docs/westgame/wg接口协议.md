interface.func

# westgame 接口文档


## 1.前言

### 1.1.协议说明

> 协议适用范围：游戏开发的客户端、后台、运营等的交互协议。
leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func

### 1.2.特殊说明

  * **出现以下bug的接口，必须修复**



>   * 会导致服务挂的  
> 
>   * 不按协议字段说明传且不报错的，如要求传[{“a”:[int,int,int}]}]，传了[{“a”:[int,int}]}]
> 


### 1.3.请求协议

#### 规范

> **_a.所有参数必须小写_**  
>  **_b.所有参数必须有意义(含各命令字的参数)_**  
>  **_c.禁止同名参数_**  
>  **_d.命令字参数格式：k_xxx_**

#### 公共参数

> 说明：以下参数为很老旧的版本，需要更新最新的情况更新一下

字段 | 含义 | 类型  
---|---|---  
ip | 隐含参数，用户ip（后台获取） | string  
md5str | 隐含参数，由加密库生成，用于自动校验 | string  
lrct | Last req cost time,上次请求的客户端耗时 | string  
sn | 客户端请求序列号 | string  
time | 客户端请求时间 | string  
vs | 游戏版本号 | string  
sv | System version系统版本号 | string  
dt | Device type设备类型 | string  
idfa | Idfa | string  
pid | 产品id | string  
did | 设备id | string  
sid | 服务器id——战区id，初始登录且未知服务器时，填写-1 | string  
uid | 用户的全局id | string  
gid | 用户的gamecenter帐号 | string  
cidx | 用户当前城市id序号 | string  
cid | 用户当前城市id | string  
aid | 用户联盟id | string  
pg | 用户分页请求页码，默认为1 | string  
pp | 用户分页请求时每页的结果数目 | string  
mid | 用户请求时本地最新的邮件id | string  
rid | 用户请求时本地最新的report id | string  
lang | 用户语言 | string  
npc | 是否为NPC，0代表为用户，1代表NPC | string  
sbox | 是否属于测试环境充值，0为真实环境，1为测试环境 | string  
command | 用户请求命令字 | string  
k_xxx | 请求的各个参数 | string  
  
#### 请求举例

> a.加密请求：  
>  http://test.com/hu?version=2.7&request=xxxxxxxxxxxxxxxxxxxxxxxxxxx

> b.非加密请求：  
>  http://test.com/hu?version=2.7&request=version=2.7&request=time=0&version=2.7&did=11D4B57D-F9BC-4E79-BDC7-17F42A75C1FB&pid=730354031&lg=1&uid=0&idfa=11D4B57D-F9BC-4E79-BDC7-17F42A75C1FB&sid=-1&cid=0&aid=0&pp=0&pg=0&lang=0&mid=0&rid=0&os_version=iPhone6_iPhone_OS_8.1.2&gid=G:1095039743&command=login_get

### 1.4.响应协议

> 规范：主要使用pb协议，少量使用json协议

* * *

## 2.login_center 接口协议

> service_type：2005

* * *

### 2.1.登录

* * *

#### 登录-init

  * **命令字** **_init_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | rid | – | – | – | –  
key1 | email | – | – | – | –  
key2 | password | – | – | – | –  
key3 | th_id | – | – | – | –  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=init

  * **改动历史**

版本号 | 说明  
---|---  
1.0 | 初始化  
  
* * *

#### 登录-update

  * **命令字** **_update_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=update

  * **改动历史**

版本号 | 说明  
---|---  
1.0 | 初始化  
  
* * *

#### 登录-login

  * **命令字** **_login_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | email | – | – | – | –  
key1 | password | – | – | – | –  
key2 | th_id | – | – | – | –  
key3 | login_platform | – | – | – | –  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=login

  * **说明**

  * 此接口在5.7之前为account_svr的接口，此版本之后修改为login_center的

  * 旧service_type：34079

  * 新service_type：2005

  * **改动历史**


版本号 | 说明  
---|---  
5.7 | 初始化  
  
* * *

#### 登录-校验是否可创新号

  * **命令字** **_check_did_can_register_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=check_did_can_register

  * **说明**

  * 客户端上点击【创建新用户】时先校验，校验通过之后才回到loading条

  * **改动历史**


版本号 | 说明  
---|---  
5.7 | 初始化  
  
* * *

## 3.rank 接口协议

> service_type：34038

* * *

### 3.1.排行榜

* * *

#### 排行榜-拉取排行榜

  * **命令字** **_rank_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | rank_type | int32 | 1 | 1 |   
key1 | keyword 搜索用 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rank&key0=1&key1=1

  * **备注**



> 返回rank.json

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

### 3.2.联盟推荐

* * *

#### 联盟推荐-拉取联盟列表–走rank接口

  * **命令字** **_al_list_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | policy | int32 | 0 | 1 | (0:需要批准,1:自动加入,2:全部)  
key1 | key_word | string | dsfds | 1 | (要搜索的名字)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_list_get&key0=0&key1=dsfds

  * **备注**



> 返回alliancelist_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 联盟推荐-获取联盟推荐列表–走rank接口

  * **命令字** **_al_recommend_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_join_time | string | 15641561 | 1 | svr_player里面的al_join_t  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_recommend_get&key0=15641561

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

## 4.account_svr 接口协议

> service_type：34079

* * *

### 4.1.账号

* * *

#### 账号-检查账号状态

  * **命令字** **_check_account_status_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=check_account_status

  * **反包**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb1-1){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb1-2)    "msg":"xxxx",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb1-3)    "status":int, //账号状态
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb1-4)    "uid_binding_by_did":string, //当前设备绑定的uid
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb1-5)}

  * **改动历史**



* * *

## 5.op_svr 接口协议

> service_type：2019

* * *

### 5.1.从运营74节点拉活动

* * *

#### 从运营74节点拉活动-向运营74节点发起拉取活动具体信息

  * **命令字** **_get_event_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_info | json | xxxx | 1 | 具体支持的event type见下表  
key1 | 活动type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_event_info&key0=xxxx&key1=1

  * 支持的event type

event_type | 活动名称  
---|---  
127 | 成长阶梯活动  
128 | 幸运采购活动  
  
  * 改动历史

版本号 | 说明  
---|---  
v3.0 | 初始化  
v5.2 | 新增支持 成长阶梯&幸运礼包  
  
* * *

### 5.2.拉取活动数据

* * *

#### 拉取活动数据-通过event id拉取无活动服务detail

  * **命令字** **_get_no_svr_event_detail_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int32 | 18 | 1 | 具体支持的event type见下表  
key1 | event_id | string | xxx | 1 | 不同活动的event id格式不同  
key2 | event_info | json | 具体看协议 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_no_svr_event_detail_info&key0=18&key1=xxx&key2=具体看协议

  * 支持的event type

event_type | 活动名称  
---|---  
18 | 刹马镇  
48 | 多日活动  
49 | 主城等级冲刺活动  
52 | 新手充值活动  
53 | 多日充值活动  
64 | 领土法则  
65 | 洛哈  
68 | 预告页  
69 | 做蛋糕  
71 | 失落之地-活动主页  
85 | 暗影-主页  
88 | 活动医院  
90 | kvk-活动主页  
121 | 联盟送礼活动  
  
  * 改动历史

版本号 | 说明  
---|---  
v5.1 | 初始化  
v5.3 | 回流活动  
  
* * *

#### 拉取活动数据-通过pid拉取无活动服务detail

  * **命令字** **_get_no_svr_event_detail_info_by_pid_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int32 | 18 | 1 | 具体支持的event type见下表  
key1 | 活动的pid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_no_svr_event_detail_info_by_pid&key0=18&key1=1

  * 支持的event type

event_type | 活动名称  
---|---  
76 | 新手充值返利  
77 | 充值返利  
88 | 活动医院  
  
  * 改动历史

版本号 | 说明  
---|---  
v5.1 | 初始化  
  
* * *

#### 拉取活动数据-拉取 战时数据区域

  * **命令字** **_get_circus_battle_statistics_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战场类型 | int | 1 | 1 | 战场类型  
key1 | 组合id | int | 1 | 1 | 组合id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_circus_battle_statistics&key0=1&key1=1

  * **战场类型备注**

type | 备注  
---|---  
1 | GVE-战场类型  
  
  * **组合id备注**

id | 备注  
---|---  
battle_sid | GVE的战场sid  
  
  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

### 5.3.拉取缩略图数据

* * *

#### 拉取缩略图数据-通过sid拉取缩略图反包数据

  * **命令字** **_get_map_thumbnail_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 18 | 1 | 具体支持的sid见下表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_map_thumbnail_info&key0=18

  * 支持的sid

sid | 战场sid  
---|---  
  
  * 改动历史

版本号 | 说明  
---|---  
v1.8 | 拉取缩略图数据  
  
* * *

#### 拉取缩略图数据-通过sid拉取kvk战况实时数据

  * **命令字** **_get_kvk_score_board_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 18 | 1 | 具体支持的sid见下表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kvk_score_board&key0=18

  * 支持的sid

sid | 战场sid  
---|---  
  
  * 改动历史

版本号 | 说明  
---|---  
v1.6 | 拉取kvk战况数据  
  
* * *

#### 拉取缩略图数据-通过sid拉取缩略图小地图反包数据

  * **命令字** **_get_map_thumbnail_small_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 18 | 1 | 具体支持的sid见下表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_map_thumbnail_small_info&key0=18

  * 支持的sid

sid | 战场sid  
---|---  
  
  * 改动历史

版本号 | 说明  
---|---  
v5.9.1 | 拉取缩略图小地图数据  
  
* * *

#### 拉取缩略图数据-拉新kvk计分板

  * **命令字** **_get_new_kvk_score_board_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 18 | 1 | 具体支持的sid见下表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_new_kvk_score_board&key0=18

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 拉取缩略图数据-拉计分板通用化接口

  * **命令字** **_get_score_board_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 18 | 1 | 具体支持的sid见下表  
key1 | event_type | int32 | 142 | 1 | event_type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_score_board&key0=18&key1=142

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

### 5.4.新兑换商店

* * *

#### 新兑换商店-新兑换商店-拉取详情

  * **命令字** **_get_new_exchange_shop_detail_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | shop_big_type | int32 | 1 | 1 | 商店大类型  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_new_exchange_shop_detail_info&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

#### 新兑换商店-新兑换商店-标记兑换提醒

  * **命令字** **_new_exchange_shop_remind_setup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | shop_big_type | int32 | 1 | 1 | 商店大类型  
key1 | shop_id | string | 1 | 1 | 商店id  
key2 | flag | int32 | 1 | 1 | 是否需要提醒,0-否,1-是  
key3 | castle_lv | int32 | 1 | 1 | 玩家当前主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_exchange_shop_remind_setup&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

### 5.5.活动相关

* * *

#### 活动相关-选择自订礼包

  * **命令字** **_select_customize_iap_reward_promote_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | select info | {“event_type”:int64,“event_id”:str,“chest_id”:int64,“chose_idx”:[int64]} | {“event_type”:123,“event_id”:123——16789893268,“chest_id”:22,“chose_idx”:[-1]} | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=select_customize_iap_reward_promote&key0={“event_type”:123,“event_id”:123——16789893268,“chest_id”:22,“chose_idx”:[-1]}

  * **改动历史**

版本号 | 说明  
---|---  
op | 新增接口  
  
* * *

### 5.6.移服活动

* * *

#### 移服活动-移服活动-拉取详情

  * **命令字** **_get_self_immigration_event_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_immigration_event_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-拉取其他服务器的活动列表

  * **命令字** **_get_other_server_immigration_event_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | sid_list | string | 1,2,3,4 | 1 | sid列表,逗号分隔,-1代表此活动下的所有sid  
key2 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_other_server_immigration_event_info&key0=1&key1=1,2,3,4&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-拉取自己服务器的迁入名单

  * **命令字** **_get_self_server_immigration_player_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_server_immigration_player_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-拉取自己服务器的邀请名单

  * **命令字** **_get_self_server_immigration_invite_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_server_immigration_invite_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-拉取玩家自己的邀请名单

  * **命令字** **_get_self_player_immigration_invite_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_player_immigration_invite_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-拉取本服的邀请记录

  * **命令字** **_get_self_immigration_invite_log_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_immigration_invite_log_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-拉取自己服务器的申请名单

  * **命令字** **_get_self_server_immigration_request_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | castle_lv | int64 | 1 | 1 | 玩家的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_server_immigration_request_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 5.7.通用拉活动

* * *

#### 通用拉活动-整体活动信息获取

  * **命令字** **_all_event_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_info | json | 具体看协议 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=all_event_get&key0=具体看协议

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 通用拉活动-某类活动历史信息获取

  * **命令字** **_event_history_info_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int32 | 123 | 1 | 走运营proxy的活动  
key1 | event_info | json | 具体看协议 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=event_history_info_get&key0=123&key1=具体看协议

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 通用拉活动-获取主题活动历史信息

  * **命令字** **_theme_event_history_info_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_info | json | 具体看协议 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=theme_event_history_info_get&key0=具体看协议

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 通用拉活动-获取联盟主题活动历史

  * **命令字** **_al_theme_event_history_info_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_info | json | 具体看协议 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_theme_event_history_info_get&key0=具体看协议

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

### 5.8.通用透传请求

* * *

#### 通用透传请求-通用透传请求

  * **命令字** **_new_op_transparent_transmission_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_cmd | string | get_event_data | 1 | 具体见备注  
key1 | param | json | {} | 1 | 具体见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_transparent_transmission&key0=get_event_data&key1={}

  * 备注



> 除了basic表，其余都走这个通用透传

  * 举例



> 例：如要拉info，运营协议为
    
    
    "cmd":"get_event_data",
    请求包协议
    {
        "header": {
            "sid": int64,
            "uid": int64,
            "aid": int64,
            "ksid": int64,
        },
        "request": {
            "cmd": "get_event_data",
            "param":{
                "list":[
                    {
                        "event_id": string,
                        "event_type": int
                    }
                ],
                "extra":
                {
                    "name": string,
                    "lang": int,
                    "castle_lv": int,
                    "al_name": string,
                    "al_nick": string,
                    "ctime": long
                }
            }
        }
    }

> 则客户端拼的请求：
    
    
    key0=get_event_data
    key1=
    {
        "list":[
            {
                "event_id": string,
                "event_type": int
            }
        ],
        "extra":
        {
            "name": string,
            "lang": int,
            "castle_lv": int,
            "al_name": string,
            "al_nick": string,
            "ctime": long
        }
    }

> 具体透传内容详见支持活动的【客户端协议】

  * 改动历史

版本号 | 说明  
---|---  
v5.0 | 擂台赛版本初设计  
v5.6 | 新增支持 水晶岛活动  
  
* * *

## 6.副本 接口协议

> service_type：2003

* * *

### 6.1.GVG-初始化战场

* * *

#### GVG-初始化战场-开启新副本

  * **命令字** **_op_open_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_type | int | 3 | 1 | 见备注  
key1 | fuben_sid | int | 3 | 1 |   
key2 | fuben_info | json | {} | 1 | 见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_open_fuben&key0=3&key1=3&key2={}

  * **fuben_type**

fuben_type | 活动  
---|---  
3 | GVG  
  
  * **fuben_info**


    
    
    {
        "event_id": string,
        "contestants":    //参赛双方
        [                 //下标+1 = 阵营id
            [             // 该阵营下所有uid
                [
                    long, // uid
                    long, // ksid
                    [
                        // 具体内容由运营开发决定, 后台在结算时透传回去
                    ]
                ],
                ...
            ]
        ],
        "battle_info":     //战场属性
        {
            "time_info":   //时间属性
            [
                long,      //0U 副本开始时间（已错峰之后的） - 匹配完成
                long,      //1U 副本结束时间
                long,      //2U 副本关闭时间
                [          //3U 各争夺期时间, 实际只有一轮争夺期
                    [      //idx+1 = 第N轮争夺期
                        long,      //0U 本轮争夺期开始时间
                        long,      //1U 本轮争夺期结束时间
                        long,      //2U 本轮争夺期准备期时长 = 确认时长 + 原准备期时长
                        long,      //3U 本轮争夺期第一阶段时长
                        long,      //4U 本轮争夺期第二阶段时长
                    ]
                ]
            ],
            "player_info":  //玩家属性
            {
                "castle_lv": long,              //参与主城等级要求
                "energy_a":                     //特殊体力, 没有该功能则各字段默认给0
                [
                    long,                       //0U  上限
                    long,                       //1U  金币恢复-单次消耗恢复量
                    long,                       //2U  金币恢复-每阶段可使用次数
                    [long,long],                //3U  金币恢复-单次消耗，第idx+1次消耗long金币
                    long,                       //4U  token恢复-单次消耗恢复量
                    long,                       //5U  token恢复-单阶段可使用次数
                    [{"a":[long,long,long]}],   //6U  token恢复-单次消耗
                    long,                       //7U  自然恢复周期x
                    long,                       //8U  自然恢复值y，每x秒自然恢复y
                    {"long": long},             //9U  进攻时使用能量，单次使用量， {"wild_class": num}
                    {"long": long},             //10U 增援时使用能量，单次使用量， {"wild_class": num}
                ],
                "move_city":                    //移城相关
                [
                    long,                       //0U 免费移城-初始次数
                    long,                       //1U 免费移城-自然恢复周期x
                    long,                       //2U 免费移城-自然恢复值y，每x秒自然恢复y
                    long,                       //3U 金币移城-每阶段可使用次数, 没有该功能则给0
                    [long,long],                //4U 金币移城-单次使用消耗，第idx+1次消耗long金币, 没有该功能则给0
                    long,                       //5U token移城-每阶段可使用次数, 没有该功能则给0
                    [{"a":[long,long,long]}],   //6U token移城-单次消耗, 没有该功能则给0
                    long,                       //7U 随机移城-每阶段可使用次数, 没有该功能则给0
                ],
                "stop_fire":                    //阻止燃烧, 没有该功能则各字段默认给0
                [
                    long,                       //1U 金币阻止-每阶段可使用次数，-1为无限次
                    long,                       //2U 金币阻止-单次使用消耗
                    long,                       //3U 帮助阻止-每阶段可被帮助次数
                ],
                "army":
                [                               //下标 = 阶段idx
                    long,                       //本idx+1阶段的兵数量
                    long,
                    long,
                    long,
                    long
                ],
                "hosptal":
                [
                    long,                       //0U  医院容量
                    long,                       //1U  忠诚点-自然恢复周期x
                    long,                       //2U  忠诚点-自然恢复量y，每x秒自然恢复y
                    long,                       //3U  金币治疗-每阶段可使用次数 
                    [long,long],                //4U  金币治疗-每次使用消耗，第idx+1次消耗long金币
                    long,                       //5U  金币治疗-每次使用恢复量
                    long,                       //6U  token治疗-每阶段可使用次数, 没有该功能则给0
                    [{"a":[long,long,long]}],   //7U  token治疗-单次消耗, 没有该功能则给0
                    long,                       //8U  token治疗-每次使用恢复量, 没有该功能则给0
                    long,                       //9U  help治疗-每阶段可被帮助次数
                    long,                       //10U help治疗-每次被援助恢复量
                    long,                       //11U help治疗-单次求助可被帮助次数
                ]
            },
            "battle":
            [
                long,                           //战斗时，进入交战池队列数量上限
            ],
            "score_info":
            {
                "building":
                {
                    "long":                     //建筑wild class
                    [
                        long,                   //加分值y，每秒加y分
                    ]
                },
            },
            "buff_info":
            {
                "global_buff":    //战场buff
                [
                    {"long":long}                   //{"buff_id":buff_num}
                ]
            },
            "gvg_confront_info":
            {
                "airdrop":
                {
                    "score":
                    [
                        long,                       //0U 总分
                        long,                       //1U 采集总时长
                    ],
                    "refresh": // 每一次刷地配置
                    [
                        [
                            long,                   //0U 相对时间, 单位秒. 活动开始这么多秒后开始这一轮刷地
                            long,                   //1U 刷地类型, -1代表随机选择类型, 其他有效type见数值协议 gvg_confront_airdrop
                            long,                   //2U 刷地数量
                            long                    //3U 刷地范围
                        ]
                    ]
                },
                "missle":
                [
                    long,                           //0U 导弹开炮间隔
                    long,                           //1U 导弹伤害Y, 万分制
                ],
                "target_score": long,               //达到目标分后, 提前结束战场
                "rob_score":
                [
                    long,                           //0U 到X分时才可被抢
                    long,                           //1U 被抢的比例Y, 万分制
                ]
            }
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
v7.0.5 | 新增副本-巅峰赛-阵营战  
v7.0.8 | 新增副本-GVG  
  
* * *

### 6.2.副本通用接口

* * *

#### 副本通用接口-通用副本操作-user-xx操作

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb5-1)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb5-2)//通用接口，具体用法见具体操作

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 副本通用接口-通用副本操作-非user-xx操作

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb6-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb6-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb6-3)//通用接口，具体用法见具体操作

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 副本通用接口-通用副本op操作-user json -内部使用

  * **命令字** **_op_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**




> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.3.副本通用接口-buff相关

* * *

#### 副本通用接口-buff相关-副本通用接口-buff相关

  * **命令字** **_fuben_operate_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_buff&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-4)//--------------设置治安官装备----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-7)    "command":"set_sheriff_equip",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-11)        "equip_list":       //每次都要把7件装备传过来
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-12)        {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-13)            "int":long,     //"slot":data_id  "装备槽位"：后台数据id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-14)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-15)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-16)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-17)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-18)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-19)//--------------设置治安官技能----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-20)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-21){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-22)    "command":"set_sheriff_skill",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-23)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-24)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-25)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-26)        "skills":           //只修改传过来的type，不会处理未传的type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-27)        {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-28)            "int":          //skill type，//同大地图，0：sheriff 1：monster 2：grade
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-29)            {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-30)                "int":int,  //"id":lv
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-31)            }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-32)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-33)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-34)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-35)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-36)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-37)//--------------设置治安官装备+技能----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-38)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-39){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-40)    "command":"set_sheriff_equip_skill",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-41)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-42)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-43)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-44)        "equip_list":       //每次都要把7件装备传过来
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-45)        {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-46)            "int":long,     //"slot":data_id  "装备槽位"：后台数据id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-47)        },
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-48)        "skills":           //三个type都要有
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-49)        {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-50)            "int":          //skill type，//同大地图，0：sheriff 1：monster 2：grade
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-51)            {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-52)                "int":int,  //"id":lv
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-53)            }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-54)        },
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-55)        "horse_harness_list":
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-56)        {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-57)            "int": long,    //"slot":horse_harness_id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-58)        },
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-59)        "dragon_plan": long, // 7.2.7 临时处理，传入预设ID
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-60)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-61)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-62)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-63)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-64)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-65)//--------------设置治安官装备+技能----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-66)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-67){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-68)    "command":"use_sheriff_plan",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-69)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-70)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-71)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-72)        "plan_id":int,      //预设id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-73)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-74)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-75)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-76)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-77)//--------------设置march槽位信息----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-78)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-79){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-80)    "command":"set_march_slot",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-81)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-82)        "type":long,             //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-83)        "sid":long,              //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-84)        "slot_type":int,         //槽位type，见pb协议：fuben_march_slot_type_readme
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-85)        "slot_id":int,           //槽位id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-86)        "hero_list":[int,int],   //使用的英雄列表，最多5个
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-87)        "army_info":
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-88)        {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-89)            "category":{"int":int}, //slot_type = 1时有效，{"troop_category":rate}  万分比
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-90)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-91)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-92)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-93)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-94)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-95)//--------------切换副本内马具预设----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-96)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-97){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-98)    "command":"use_horse_preset",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-99)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-100)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-101)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-102)        "preset_id":int,    //预设id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-103)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-104)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb8-105)//---------------------------------------

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
v7.2.3 | 新增马具预设&战场内buff相关  
  
* * *

#### 副本通用接口-buff相关-副本通用接口-buff道具相关

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-1)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-4)//--------------购买并使用buff道具----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-7)    "command":"buy_and_use_buff_item",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-9)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-10)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-11)        "buff_id":long,      //buff_id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-12)        "item_id":long,      //道具id, 如无则给0
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-13)        "item_idx": long,    //购买的下标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-14)        "cost_type": long,   //1-免费,2-消耗宝石
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-15)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-16)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-17)//response
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-18)fuben_player_item_buff
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb9-19)//---------------------------------------

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
v7.2.3 | 新增处理buff道具相关  
  
* * *

#### 副本通用接口-buff相关-副本通用接口-设置目标buff

  * **命令字** **_op_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-4)//--------------设置战场内buff----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-7)    "command":"op_set_target_buff",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-11)        "target_type":int,  //目标类型, 1：aid
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-12)        "target_id": int64, //目标id  
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-13)        "buffs":
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-14)        [
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-15)            [long, long] // buff_id, buff_num
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-16)        ]
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-17)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-18)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb10-19)//---------------------------------------

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

### 6.4.副本通用接口-march相关

* * *

#### 副本通用接口-march相关-通用副本操作-user-march相关

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-1)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-2)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-3)//--------------发起action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-4)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-5){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-6)    "command":"create_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-7)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-8)        "type":long,               //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-9)        "sid":long,                //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-10)        "action_type":long,        //action类型
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-11)        "wild_class":long,         //目标地形类型
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-12)        "cost_time":long,          //action耗时
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-13)        "target_pos":long,         //action目标坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-14)        "set_type":long,           //设置march的方式  1：常规  2：预设槽位
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-15)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-16)        "extra_info":{             //不同action额外信息，根据需要传
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-17)            //见extra_info说明
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-18)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-19)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-20)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-21)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-22)//extra_info说明
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-23)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-24)//march type = scout
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-25)//传空{}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-26)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-27)//march type = attack、reinforce
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-28)//----------------------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-29)//set_type = 1时
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-30){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-31)    "troop":{"id":long}, //出兵信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-32)    "is_sheriff":long,     //是否带治安官
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-33)    "hero":[int], //带英雄
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-34)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-35)//----------------------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-36)//使用槽位的方式
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-37)//set_type = 2时，要传以下字段
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-38){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-39)    "march_slot_id": int,  //使用的march槽位
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-40)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-41)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-42)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-43)//march type = rally
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-44)//----------------------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-45)//set_type = 1时
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-46){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-47)    "prepare_time":long, // 准备时间    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-48)    "troop":{"id":long}, //出兵信息    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-49)    "is_sheriff":long,     //是否带治安官    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-50)    "hero":[int], //带英雄    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-51)    "troop_recommend": string // 推荐出兵
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-52)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-53)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-54)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-55)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-56)//march type = rally_reinforce
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-57)//----------------------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-58)//set_type = 1时
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-59){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-60)    "target_action_id":string, //目标action_id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-61)    "troop":{"id":long}, //出兵信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-62)    "is_sheriff":long,     //是否带治安官
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-63)    "hero":[int], //带英雄
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-64)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-65)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-66)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-67)//****************************************************
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-68)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-69)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-70)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-71)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-72)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-73)fuben_march_action_list_inc
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-74)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-75)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-76)//--------------加速自己的action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-77)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-78){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-79)    "command":"speedup_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-80)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-81)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-82)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-83)        "id":string,         //action id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-84)        "speedup_type":long, //加速类型 1万分比 2时间s
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-85)        "num":long,          //加速数值
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-86)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-87)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-88)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-89)fuben_march_action_list_inc
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-90)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-91)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-92)//--------------召回自己的action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-93)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-94){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-95)    "command":"recall_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-96)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-97)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-98)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-99)        "id":string,         //action id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-100)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-101)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-102)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-103)fuben_march_action_list_inc
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-104)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-105)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-106)//--------------遣返一条action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-107)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-108){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-109)    "command":"repatriate_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-110)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-111)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-112)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-113)        "pos":long,          //遣返点坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-114)        "wild_class":long,   //遣返点地形类型
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-115)        "id":string,         //action id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-116)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-117)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-118)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-119)//根据场景定制
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-120)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-121)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-122)//--------------解散action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-123)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-124){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-125)    "command":"dismiss_all_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-126)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-127)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-128)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-129)        "pos":long,          //解散点坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-130)        "wild_class":long,   //解散点地形类型
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-131)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-132)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-133)//rsp 
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-134)//根据场景定制
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb11-135)//---------------------------------------

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.5.副本通用接口-其它

* * *

#### 副本通用接口-其它-通用副本操作-非user-其它

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-4)//--------------其他玩家详情----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-7)    "command":"get_other_player_info",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-9)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-10)        "sid":long,//副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-11)        "uid":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-14)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-15)fuben_other_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb12-16)//---------------------------------------

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.6.副本通用接口-后台内部使用

* * *

#### 副本通用接口-后台内部使用-通用副本op操作-非user json -内部使用

  * **命令字** **_op_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-3)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-4)//创建副本
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-5){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-6)    "command":"init_fuben",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-7)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-8)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-9)        "sid":long, //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-10)        "status": long, //1准备期 2进行期 3结束期
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-11)        "begin_time":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-12)        "end_time":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-13)        "close_time":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-14)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-15)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-16)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-17)//修改副本状态
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-18){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-19)    "command":"op_set_fuben_info",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-20)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-21)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-22)        "sid":long, //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-23)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-24)        //参数都可选
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-25)        "status": long, //1准备期 2进行期 3结束期
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-26)        "begin_time":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-27)        "end_time":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-28)        "close_time":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-29)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-30)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb13-31)

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.7.副本通用接口-地图

* * *

#### 副本通用接口-地图-通用副本操作-非user-地图

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-4)//--------------拉大地图------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-7)    "command":"fuben_map_get",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-9)        "type":long,  //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-10)        "sid":long,   //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-11)        "id_list":[], //bid list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-14)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-15)fuben_map_bid_list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-16)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-17)fuben_map_march_action
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-18)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-19)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-20)//---------------建筑详情----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-21)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-22){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-23)    "command":"get_map_building_detail",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-24)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-25)        "type":long,  //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-26)        "sid":long,   //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-27)        "pos":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-28)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-29)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-30)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-31)fuben_map_building_detail
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-32)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-33)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-34)//--------------拉小地图------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-35)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-36){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-37)    "command":"fuben_minimap_get",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-38)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-39)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-40)        "sid":long,  //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-41)        "camp_id" : long,  //副本玩家阵营id 用于返回玩家小队主城数据 0或不传表示返回所有阵营
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-42)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-43)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-44)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-45)fuben_minimap
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-46)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-47)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-48)//--------------拉大缩略图------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-49)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-50){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-51)    "command":"fuben_thumbnail_get",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-52)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-53)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-54)        "sid":long,  //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-55)        "camp_id" : long,  //副本玩家阵营id 用于返回玩家小队主城数据 0或不传表示返回所有阵营
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-56)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-57)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-58)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-59)fuben_thumbnail
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-60)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-61)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-62)//--------------地图emoji-按指定march发送------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-63)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-64){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-65)    "command":"send_map_emoji_march",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-66)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-67)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-68)        "sid":long,  //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-69)        "emoji_id":int,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-70)        "march_id":string
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-71)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-72)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-73)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-74)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-75)//--------------地图emoji-按指定pos发送------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-76)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-77){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-78)    "command":"send_map_emoji_pos",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-79)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-80)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-81)        "sid":long,  //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-82)        "emoji_id":int,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-83)        "pos":int
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-84)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-85)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-86)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-87)//--------------地图搜索------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-88)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-89){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-90)    "command":"fuben_map_search",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-91)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-92)        "center_pos":long, //搜索中心位置
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-93)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-94)        "sid":long,  //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-95)        "wild_class":int,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-96)        "level":int
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-97)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-98)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-99)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-100)//--------------进入观战------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-101)//request v7.2.3
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-102){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-103)    "command":"fuben_enter_watch",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-104)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-105)        "type":long,  //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-106)        "sid":long,   //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-107)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-108)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-109)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-110)//--------------观战者拉大地图------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-111)//request v7.2.3
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-112){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-113)    "command":"fuben_map_watch_get",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-114)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-115)        "type":long,  //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-116)        "sid":long,   //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-117)        "id_list":[], //镜像bid list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-118)        //镜像bid转换规则: bid + MAX_X / 10 * 1000
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-119)        //即原bid加上地图最大X坐标转换的一个bid x值,确保独立于原bid，作为镜像bid进行推送
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-120)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-121)        //额外说明：此请求同时是观战者心跳请求,需要客户端在地图内时定时(如30s)请求维持观战,但是作为心跳时,bid list为空即可
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-122)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-123)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-124)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-125)fuben_map_bid_list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-126)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb14-127)fuben_map_march_action

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.8.副本通用接口-移城相关

* * *

#### 副本通用接口-移城相关-通用副本操作-user-移城

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-1)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-2)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-3)//---------------移城demo----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-4)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-5){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-6)    "command":"move_city_demo",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-7)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-8)        "type":long,   //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-9)        "sid":long,    //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-10)        "spos":long, 
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-11)        "tpos":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-14)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-15)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-16)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-17)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-18)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-19)//---------------定点移城----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-20)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-21){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-22)    "command":"move_city_prepare",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-23)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-24)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-25)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-26)        "spos":long,         //主城原坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-27)        "tpos":long,         //想移的坐标, 随机移城传-1
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-28)        "cost_type":long,    //消耗类型  1：免费 2：消耗金币 3：消耗token
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-29)        "move_type":long,    //移城类型  1：常规
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-30)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-31)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-32)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-33)fuben_move_city_prepare_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-34)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-35)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-36)//---------------定点移城----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-37)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-38){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-39)    "command":"move_city",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-40)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-41)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-42)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-43)        "spos":long,         //主城原坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-44)        "tpos":long,         //想移的坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-45)        "cost_type":long,    //消耗类型  1：免费 2：消耗金币 3：消耗token
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-46)        "move_type":long,    //移城类型  1：常规
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-47)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-48)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-49)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-50)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-51)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-52)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-53)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-54)//---------------随机移城----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-55)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-56){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-57)    "command":"move_city_random",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-58)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-59)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-60)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-61)        "province":long,     //想移的省，-1表示没想法
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-62)        "zone":long,         //想移的圈，-1表示没想法
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-63)        "cost_type":long,    //消耗类型  1：免费 2：消耗金币 3：消耗token
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-64)        "move_type":long,    //移城类型  1：常规
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-65)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-66)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-67)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-68)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-69)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-70)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb15-71)

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.9.副本通用接口-进入副本

* * *

#### 副本通用接口-进入副本-进入副本

  * **命令字** **_enter_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | fuben_type | int | 1 | 1 | 副本类型  
key2 | fuben_id | int | 1 | 1 | 副本id(sid)  
key3 | camp_id | int | 1 | 1 | 阵营id,在后台记录中的阵营id不一致时会报错  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=enter_fuben&key0=1&key1=1&key2=1&key3=1

  * **fuben_type**

fuben type | 活动  
---|---  
1 | 火车大劫案  
2 | 阵营战  
3 | GVG  
4 | 黄金圣杯  
  
  * **备注**



> 反包:user json,fuben_info、 fuben_player、 fuben_camp

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
v7.0.5 | 新增key3  
v7.0.8 | 新增副本类型3  
v7.2.3 | 新增副本类型4  
  
* * *

#### 副本通用接口-进入副本-被拉入副本

  * **命令字** **_auto_enter_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | fuben_type | int | 1 | 1 | 副本类型  
key2 | fuben_id | int | 1 | 1 | 副本id(sid)  
key3 | camp_id | int | 1 | 1 | 阵营id,在后台记录中的阵营id不一致时会报错  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auto_enter_fuben&key0=1&key1=1&key2=1&key3=1

  * **fuben_type**

fuben type | 活动  
---|---  
1 | 火车大劫案  
2 | 阵营战  
3 | GVG  
  
  * **备注**



> 反包:user json,fuben_info、 fuben_player、 fuben_camp

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.8 | 新增接口  
  
* * *

### 6.10.巅峰赛-阵营战-初始化战场

* * *

#### 巅峰赛-阵营战-初始化战场-开启新副本

  * **命令字** **_op_open_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_type | int | 3 | 1 | 此活动为1  
key1 | fuben_sid | int | 3 | 1 |   
key2 | fuben_info | json | {} | 1 | 见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_open_fuben&key0=3&key1=3&key2={}

  * **fuben_type**

fuben_type | 活动  
---|---  
2 | 阵营战  
  
  * **fuben_info**


    
    
    {
        "event_id": string,
        "contestants":    //参赛双方
        [                 //下标+1 = 阵营id
            [             // 该阵营下所有uid
                long, long, long
            ]
        ],
        "battle_info":     //战场属性
        {
            "time_info":   //时间属性
            [
                long,      //0U 副本开始时间（已错峰之后的）
                long,      //1U 副本结束时间
                long,      //2U 活动关闭时间
                [          //3U 每轮争夺期的时间, 注: 这里各轮争夺期之间的时间不一定衔接, 但一定不可重叠, 不处于各个阶段中的时间属于休战期
                    [      //idx+1 = 第N轮争夺期
                        long,      //0U 本轮争夺期开始时间
                        long,      //1U 本轮争夺期结束时间
                        long,      //2U 本轮争夺期准备期时长
                        long,      //3U 本轮争夺期第一阶段时长
                        long,      //4U 本轮争夺期第二阶段时长
                        long,      //5U 本轮争夺期第三阶段时长
                    ]
                ]
            ],
            "player_info":  //玩家属性
            {
                "castle_lv": long,              //参与主城等级要求
                "energy_a":                     //特殊体力
                [
                    long,                       //0U  上限
                    long,                       //1U  金币恢复-单次消耗恢复量
                    long,                       //2U  金币恢复-每阶段可使用次数
                    [long,long],                //3U  金币恢复-单次消耗，第idx+1次消耗long金币
                    long,                       //4U  token恢复-单次消耗恢复量
                    long,                       //5U  token恢复-单阶段可使用次数
                    [{"a":[long,long,long]}],   //6U  token恢复-单次消耗
                    long,                       //7U  自然恢复周期x
                    long,                       //8U  自然恢复值y，每x秒自然恢复y
                    {"long": long},             //9U  进攻时使用能量，单次使用量， {"wild_class": num}
                    {"long": long},             //10U 增援时使用能量，单次使用量， {"wild_class": num}
                ],
                "move_city":                    //移城相关
                [
                    long,                       //0U 免费移城-初始次数
                    long,                       //1U 免费移城-自然恢复周期x
                    long,                       //2U 免费移城-自然恢复值y，每x秒自然恢复y
                    long,                       //3U 金币移城-每阶段可使用次数
                    [long,long],                //4U 金币移城-单次使用消耗，第idx+1次消耗long金币
                    long,                       //5U token移城-每阶段可使用次数
                    [{"a":[long,long,long]}],   //6U token移城-单次消耗
                    long,                       //7U 随机移城-每阶段可使用次数
                ],
                "stop_fire":                    //阻止燃烧
                [
                    long,                       //1U 金币阻止-每阶段可使用次数，-1为无限次
                    long,                       //2U 金币阻止-单次使用消耗
                    long,                       //3U 帮助阻止-每阶段可被帮助次数
                ],
                "army":
                [                               //下标 = 阶段idx
                    long,                       //本idx+1阶段的兵数量
                    long,
                    long,
                    long,
                    long
                ],
                "hosptal":
                [
                    long,                       //0U  医院容量
                    long,                       //1U  忠诚点-自然恢复周期x
                    long,                       //2U  忠诚点-自然恢复量y，每x秒自然恢复y
                    long,                       //3U  金币治疗-每阶段可使用次数 
                    [long,long],                //4U  金币治疗-每次使用消耗，第idx+1次消耗long金币
                    long,                       //5U  金币治疗-每次使用恢复量
                    long,                       //6U  token治疗-每阶段可使用次数 
                    [{"a":[long,long,long]}],   //7U  token治疗-单次消耗
                    long,                       //8U  token治疗-每次使用恢复量
                    long,                       //9U  help治疗-每阶段可被帮助次数
                    long,                       //10U help治疗-每次被援助恢复量
                    long,                       //11U help治疗-单次求助可被帮助次数
                ]
            },
            "battle":
            [
                long,                           //战斗时，进入交战池队列数量上限
            ],
            "building_info":  //建筑开放
            {
                "long": // wild_class
                [
                    long, // 0u 加个人分周期x
                    long, // 1u 加阵营分周期x
                    long, // 2u 加个人分值y，占领后每x秒加y分
                    long, // 3u 加阵营分值z，占领后每x秒加z分
                ]
            },
            "mine_info": // 积分矿信息
            {
                "long":  // wild_class
                {
                    "long": // wild_type
                    [       // lv -1
                        [
                            long, // 最大刷出范围
                            long, // 刷出数量
                            long, // 积分上限
                            long, // 加分周期x
                            long, // 加积分值y, 每个周期加y分
                        ]
                    ]
                }
            },
            "buff_info":
            {
                "random_buff":
                [
                    {
                        "rate": long,
                        "info":
                        {
                            "long": // building_id
                            [
                                {
                                    "camp_ids": [ long, long ],
                                    "buffs": // 据点中的buff列表
                                    [
                                        [
                                            long, // buff_id
                                            long, // buff_num
                                        ]
                                    ]
                                }
                            ]
                        }
                    }
                ],
                "central_rebel_buff":
                [
                    long,      // 占领x个炮塔后生效
                    [
                        [
                                long, // buff_id
                                long, // buff_num
                        ]
                    ]
                ],
                "global_buff":    //战场buff
                [
                    {"long":long}                   //{"buff_id":buff_num}
                ],
            }
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
v7.0.5 | 新增副本-巅峰赛-阵营战  
  
* * *

### 6.11.巅峰赛-阵营战-战场相关

* * *

#### 巅峰赛-阵营战-战场相关-巅峰赛-阵营战-帮助相关-非user

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-1)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-2)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-3)//--------------发起帮助信息----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-4)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-5){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-6)    "command":"post_camp_help",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-7)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-8)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-9)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-10)        "help_type":long,   //帮助type 1：灭火援助 2：重伤兵援助
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-11)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-12)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-13)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-14)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-15)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-16)//--------------帮助盟友----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-17)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-18){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-19)    "command":"do_camp_help",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-20)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-21)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-22)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-23)        "help_type":long,   //帮助type 1：灭火援助 2：重伤兵援助
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-24)        "help_uids":[long]  //要帮助的uid list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-25)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb17-26)}

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 巅峰赛-阵营战-战场相关-巅峰赛-阵营战-op接口-非user

  * **命令字** **_op_faction_war_update_camp_assistance_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_id | int32 | 123456 | 1 | 副本id  
key1 | camp_id | int32 | 123456 | 1 | 阵营id  
key2 | buff_list | json | [] | 1 | buff列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_faction_war_update_camp_assistance_buff&key0=123456&key1=123456&key2=[]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-1)//buff_list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-2)[
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-3)    [
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-4)        long,       //buff_id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-5)        long,       //buff_num
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-6)    ]
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb18-7)]

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.12.火车大劫案-主城相关

* * *

#### 火车大劫案-主城相关-火车大劫案-主城相关-user

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-1)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-2)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-3)//---------------城防值-金币恢复城防值----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-4)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-5){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-6)    "command":"add_blood",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-7)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-8)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-9)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-10)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-11)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-12)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-13)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-14)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-15)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-16)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-17)//---------------城防值-金币灭火----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-18)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-19){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-20)    "command":"stop_fire",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-21)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-22)        "type":long,   //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-23)        "sid":long,    //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-24)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-25)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-26)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-27)fuben_map
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-28)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-29)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-30)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-31)//--------------活动医院-金币/道具治疗----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-32)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-33){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-34)    "command":"army_heal",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-35)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-36)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-37)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-38)        "cost_type":long,   //消耗类型 1：免费（此处无） 2：消耗金币 3：消耗token
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-39)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-40)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-41)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-42)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-43)//--------------特殊体力-金币/道具恢复----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-44)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-45){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-46)    "command":"add_energy",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-47)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-48)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-49)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-50)        "cost_type":long,   //消耗类型 1：免费（此处无） 2：消耗金币 3：消耗token
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-51)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-52)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb19-53)//---------------------------------------

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 火车大劫案-主城相关-火车大劫案-主城相关-非user

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-4)//--------------活动医院-使用忠诚点治疗----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-7)    "command":"army_heal_by_loyalty",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-11)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-12)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-13)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-14)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-15)//--------------march槽位-交换顺序----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-16)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-17){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-18)    "command":"swap_march_slot_priority",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-19)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-20)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-21)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-22)        "ids":[long,long]   //要交换优先级的两个id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-23)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-24)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-25)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-26)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-27)//--------------march槽位-设置顺序----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-28)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-29){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-30)    "command":"set_march_slot_priority",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-31)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-32)        "type":long,           //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-33)        "sid":long,            //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-34)        "ids":[long,long,long] //所有id的排序
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-35)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-36)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-37)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-38)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb20-39)//---------------------------------------

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.13.火车大劫案-初始化战场

* * *

#### 火车大劫案-初始化战场-开启新副本

  * **命令字** **_op_open_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_type | int | 3 | 1 | 此活动为1  
key1 | fuben_sid | int | 3 | 1 |   
key2 | fuben_info | json | {} | 1 | 见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_open_fuben&key0=3&key1=3&key2={}

  * **fuben_type**

fuben_type | 活动  
---|---  
1 | 火车大劫案  
  
  * **fuben_info**


    
    
    {
        "event_id": string,
        "contestants":    //参赛双方
        [                 //下标+1 = 阵营id
            [
                int,      //0U aid
                int,      //1U ksid
                int,      //2U al_flag
                str,      //3U al_nick
                str,      //4U al_name
            ]
        ],
        "battle_info":     //战场属性
        {
            "time_info":   //时间属性
            [
                long,      //0U 副本开始时间（已错峰之后的）
                long,      //1U 副本结束时间
                long,      //2U 活动关闭时间
                [          //3U 每个阶段的时间
                    [      //idx+1 = 阶段
                        long,      //0U 本阶段开始时间
                        long,      //1U 本阶段结束时间
                        long,      //2U 本阶段准备期时长
                        long,      //3U 本阶段争夺期时长
                        long,      //4U 本阶段非争夺期时长（修火车期）
                    ]
    
                ]
    
            ],
            "player_info":  //玩家属性
            {
                "castle_lv": long,              //参与主城等级要求
                "energy_a":                     //特殊体力
                [
                    long,                       //0U  上限
                    long,                       //1U  金币恢复-单次消耗恢复量
                    long,                       //2U  金币恢复-每阶段可使用次数
                    [long,long],                //3U  金币恢复-单次消耗，第idx+1次消耗long金币
                    long,                       //4U  token恢复-单次消耗恢复量
                    long,                       //5U  token恢复-单阶段可使用次数
                    [{"a":[long,long,long]}],   //6U  token恢复-单次消耗
                    long,                       //7U  自然恢复周期x
                    long,                       //8U  自然恢复值y，每x秒自然恢复y
                    {"long": long},             //9U  进攻时使用能量，单次使用量， {"wild_class": num}
                    {"long": long},             //10U 增援时使用能量，单次使用量， {"wild_class": num}
                ],
                "move_city":                    //移城相关
                [
                    long,                       //0U 免费移城-初始次数
                    long,                       //1U 免费移城-自然恢复周期x
                    long,                       //2U 免费移城-自然恢复值y，每x秒自然恢复y
                    long,                       //3U 金币移城-每阶段可使用次数
                    [long,long],                //4U 金币移城-单次使用消耗，第idx+1次消耗long金币
                    long,                       //5U token移城-每阶段可使用次数
                    [{"a":[long,long,long]}],   //6U token移城-单次消耗
                    long,                       //7U 随机移城-每阶段可使用次数
                ],
                "stop_fire":                    //阻止燃烧
                [
                    long,                       //1U 金币阻止-每阶段可使用次数，-1为无限次
                    long,                       //2U 金币阻止-单次使用消耗
                    long,                       //3U 帮助阻止-每阶段可被帮助次数
                ],
                "army":
                [                               //下标 = 阶段idx
                    long,                       //本idx+1阶段的兵数量
                    long,
                    long,
                    long,
                    long
                ],
                "hosptal":
                [
                    long,                       //0U  医院容量
                    long,                       //1U  忠诚点-自然恢复周期x
                    long,                       //2U  忠诚点-自然恢复量y，每x秒自然恢复y
                    long,                       //3U  金币治疗-每阶段可使用次数 
                    [long,long],                //4U  金币治疗-每次使用消耗，第idx+1次消耗long金币
                    long,                       //5U  金币治疗-每次使用恢复量
                    long,                       //6U  token治疗-每阶段可使用次数 
                    [{"a":[long,long,long]}],   //7U  token治疗-单次消耗
                    long,                       //8U  token治疗-每次使用恢复量
                    long,                       //9U  help治疗-每阶段可被帮助次数
                    long,                       //10U help治疗-每次被援助恢复量
                    long,                       //11U help治疗-单次求助可被帮助次数
                ]
            },
            "buff":                             //战场buff
            [
                {"long":long}                   //{"buff_id":buff_num}
            ],
            "battle":
            [
                long,                           //战斗时，进入交战池队列数量上限
            ],
            "score_info":
            {
                "building":
                {
                    "occupy":                       //完全修复状态下的持续加分
                    {
                        "long":                     //建筑wild class
                        [
                            long,                   //加分周期x
                            long,                   //加分值y，每x秒加y分
                        ]
                    }
                }
            },
            "building_info":  //特殊建筑开放
            {
                "mirror":     //镜像建筑开放列表
                [
                    int,      //building id
                    int
                ],
                "treasure_a": //藏宝图a开放列表
                [
                    int,      //building id
                    int
                ]
            }
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.14.火车大劫案-委托march

* * *

#### 火车大劫案-委托march-火车大劫案-主城相关-user

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb22-1)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb22-2)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb22-3)//暂无

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 火车大劫案-委托march-火车大劫案-主城相关-非user

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-4)//--------------委托队列-委托march槽位----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-7)    "command":"set_entrusted_march_slot",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-11)        "slot_id":int,      //march slot id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-14)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-15)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-16)//--------------委托队列-取消委托march槽位----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-17)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-18){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-19)    "command":"cancel_entrusted_march_slot",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-20)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-21)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-22)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-23)        "slot_id":int,      //march slot id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-24)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-25)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-26)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-27)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-28)//--------------委托队列-查看委托march_slot&march列表----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-29)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-30){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-31)    "command":"query_entrusted_info",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-32)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-33)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-34)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-35)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-36)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-37)//--------------委托队列-发起委托action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-38)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-39){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-40)    "command":"create_entrusted_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-41)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-42)        "entrusted_uid": long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-43)        //其他同create_march_action
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-44)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-45)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-46)//--------------委托队列-召回委托action----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-47)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-48){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-49)    "command":"recall_entrusted_march_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-50)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-51)        "entrusted_uid": long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-52)        //同recall_march_action
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-53)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-54)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb23-55)//---------------------------------------

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.15.火车大劫案-阵营相关

* * *

#### 火车大劫案-阵营相关-火车大劫案-城防耐久相关-user

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb24-1)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb24-2)

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 火车大劫案-阵营相关-火车大劫案-城防耐久相关-非user

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-4)//--------------发起帮助信息----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-7)    "command":"post_al_help",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-11)        "help_type":long,   //帮助type 1：灭火援助 2：重伤兵援助
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-14)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-15)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-16)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-17)//--------------帮助盟友----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-18)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-19){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-20)    "command":"do_al_help",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-21)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-22)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-23)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-24)        "help_type":long,   //帮助type 1：灭火援助 2：重伤兵援助
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-25)        "help_uids":[long]  //要帮助的uid list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-26)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-27)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-28)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-29)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-30)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-31)//--------------编辑联盟法令----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-32)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-33){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-34)    "command":"edit_camp_decree",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-35)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-36)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-37)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-38)        "content":string,   //联盟法令
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-39)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-40)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-41)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-42)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-43)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-44)//--------------编辑联盟宣言----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-45)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-46){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-47)    "command":"edit_camp_declaration",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-48)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-49)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-50)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-51)        "content":string,   //联盟法令
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-52)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-53)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-54)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-55)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-56)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-57)//--------------联盟邀请----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-58)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-59){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-60)    "command":"tr_al_invite",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-61)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-62)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-63)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-64)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-65)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-66)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-67)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-68)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-69)//--------------阵营相关标记-添加标记----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-70)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-71){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-72)    "command":"camp_map_marker_add",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-73)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-74)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-75)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-76)        "id":long,           //副本id * 10000000 + pos
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-77)        "pos":int,           //坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-78)        "flag":int,          //标记图标 
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-79)        "described":string,  //描述
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-80)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-81)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-82)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-83)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-84)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-85)//--------------阵营相关标记-修改标记----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-86)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-87){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-88)    "command":"camp_map_marker_change",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-89)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-90)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-91)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-92)        "id":long,           //副本id * 10000000 + pos
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-93)        "pos":int,           //坐标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-94)        "flag":int,          //标记图标 
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-95)        "described":string,  //描述
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-96)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-97)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-98)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-99)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-100)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-101)//--------------阵营相关标记-删除标记----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-102)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-103){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-104)    "command":"camp_map_marker_del",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-105)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-106)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-107)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-108)        "ids":[long, long]  //副本id * 10000000 + pos
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-109)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-110)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-111)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb25-112)//---------------------------------------

> 反包:special

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 6.16.黄金圣碑-主城相关

* * *

#### 黄金圣碑-主城相关-黄金圣碑-主城相关-治疗伤兵

  * **命令字** **_fuben_operate_buff_behavior_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[],如果消耗了金砖需要传入  
key2 | operate_type | [TINT32] | 1 | 1 | 1为治疗  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_buff_behavior&key0={xxx}&key1=[{“a”:[1,0,1000]}]&key2=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-1)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-2)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-3)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-4)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-5)//----------------治疗军队--------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-6)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-7){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-8)    "command":"fuben_heal_troop",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-9)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-10)        "type": long,             //副本type              
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-11)        "sid":long,               //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-12)        "heal_type":long,        //0:action完成 1 立即完成
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-13)        "real_cost":long,      //0:heal_type为0时为cost time, heal_type为1时为gem cost
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-14)        "heal_troop": {        // id -> num 治疗的士兵
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-15)            "id":num
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-16)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-17)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-18)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb26-19)//---------------------------------------

> 反包:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑-主城相关-黄金圣碑-主城相关-离开战场

  * **命令字** **_leave_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | fuben_type | int | 1 | 1 | 副本类型  
key2 | fuben_id | int | 1 | 1 | 副本id(sid)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=leave_fuben&key0=1&key1=1&key2=1

  * **fuben_type**

fuben type | 活动  
---|---  
1 | 火车大劫案  
2 | 阵营战  
3 | GVG  
4 | 黄金圣碑  
  
  * **备注**



> 反包:user json,fuben_info、 fuben_player、 fuben_camp 只有提前离开战场的时候才发此请求

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑-主城相关-黄金圣碑-主城相关-治疗队列相关

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-1)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-4)//--------------活动医院-立即完成当前治疗队列----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-7)    "command":"instant_complete_heal_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-11)        "gem_cost":long,    //消耗的宝石
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-14)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-15)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-16)//--------------加速完成----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-17)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-18){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-19)    "command":"speedup_heal_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-20)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-21)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-22)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-23)        "speedup_type":long, //加速类型 1万分比 2时间s
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-24)        "num":long,          //加速数值
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-25)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-26)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-27)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-28)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-29)//--------------取消当前治疗队列----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-30)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-31){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-32)    "command":"cancel_heal_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-33)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-34)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-35)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-36)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-37)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-38)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-39)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-40)//--------------活动医院-领取治疗完成士兵----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-41)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-42){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-43)    "command":"collect_heal_troop",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-44)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-45)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-46)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-47)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-48)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-49)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-50)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb27-51)

> 反包:user json,fuben_info、 fuben_player、 fuben_camp

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑-主城相关-黄金圣碑-主城&rally相关-非user类

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-1)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-4)//----------------拉取主城信息--------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-7)    "command":"get_map_city_detail",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-9)        "type": long,             //副本type              
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-10)        "sid":long,               //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-11)        "pos":long,               //副本pos
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-12)        "target_uid":long,        //目標UID
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-13)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-14)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-15)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-16)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-17)//--------------拉取此玩家抓捕的所有治安官----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-18)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-19){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-20)    "command":"get_map_city_prison",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-21)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-22)        "type": long,             //副本type              
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-23)        "sid":long,               //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-24)        "pos":long,               //副本pos
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-25)        "target_uid":long,        //目標UID
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-26)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-27)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-28)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-29)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-30)//----------------拉取rally信息--------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-31)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-32){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-33)    "command":"get_rally_detail_info",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-34)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-35)        "type": long,             //副本type              
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-36)        "sid":long,               //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-37)        "action_id":long,        //actionID
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-38)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-39)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-40)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-41)//----------------解散rally--------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-42)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-43){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-44)    "command":"dismiss_rally_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-45)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-46)        "type": long,             //副本type              
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-47)        "sid":long,               //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-48)        "action_id":long,        //actionID
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-49)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-50)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb28-51)

> 反包:user json,fuben_info、 fuben_player、 fuben_camp

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑-主城相关-黄金圣碑-治安官相关-user类

  * **命令字** **_fuben_operate_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_player&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-1)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-4)//--------------处决治安官----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-7)    "command":"fuben_dragon_kill",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-9)        "type":long,        //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-10)        "sid":long,         //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-11)        "target_uid":long,  //被处决者uid
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-12)        "cost_list":[{"a":[type,id,num]}]
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-13)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-14)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-15)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-16)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-17)fuben_church_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-18)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-19)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-20)//--------------治安官自杀----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-21)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-22){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-23)    "command":"fuben_dragon_suicide",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-24)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-25)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-26)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-27)        "cost_list":[{"a":[type,id,num]}]
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-28)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-29)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-30)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-31)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-32)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-33)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-34)//--------------治安官复活----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-35)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-36){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-37)    "command":"fuben_dragon_revive",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-38)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-39)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-40)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-41)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-42)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-43)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-44)fuben_player
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb29-45)//---------------------------------------

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑-主城相关-黄金圣碑-治安官相关-非user类

  * **命令字** **_fuben_operate_special_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_special&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-1)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-4)//----------------拉取主城信息--------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-7)    "command":"fuben_dragon_release",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-9)        "type": long,             //副本type              
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-10)        "sid":long,               //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-11)        "target_uid":long,        //(一键释放传-1)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-12)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-13)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb30-14)//---------------------------------------

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑-主城相关-黄金圣碑-主城相关-一键加速治疗队列

  * **命令字** **_fuben_one_click_acceleration_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
key1 | cost_list | [{“a”:[type,id,num]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式可传[]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_one_click_acceleration&key0={xxx}&key1=[{“a”:[1,0,1000]}]

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-1)//user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-4)//--------------加速完成----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-7)    "command":"speedup_heal_action",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-9)        "type":long,         //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-10)        "sid":long,          //副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-11)        "speedup_type":long, //加速类型 1万分比 2时间s
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-12)        "num":long,          //加速数值
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-13)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-14)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb31-15)

> 反包:user json,fuben_info、 fuben_player、 fuben_camp

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 6.17.黄金圣碑-初始化战场

* * *

#### 黄金圣碑-初始化战场-开启新副本

  * **命令字** **_op_open_fuben_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_type | int | 3 | 1 | 见备注  
key1 | fuben_sid | int | 3 | 1 |   
key2 | fuben_info | json | {} | 1 | 见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_open_fuben&key0=3&key1=3&key2={}

  * **fuben_type**

fuben_type | 活动  
---|---  
4 | 黄金圣碑  
  
  * **fuben_info**


    
    
    {
        "event_id": string,
        "castle_lv": long,              //参与主城等级要求
        "occupy_rank_num": long, //占领时长榜上榜名次
        "contestants":  //参赛双方
        [               //下标+1 = 阵营id
            [
                int,      //0U aid
                int,      //1U ksid
                int,      //2U al_flag
                str,      //3U al_nick
                str,      //4U al_name
                //说明:uid_list 参战人员uid列表需要等运营结算后，后台主动去拉取名单
            ]
        ],
        "battle_time":   //时间属性
        [
            long,      //0U 副本开始时间（已错峰之后的）
            long,      //1U 副本结束时间
            long,      //2U 活动关闭时间
            long,      //3U 黑土地开放时间
            [          //4U 各争夺期时间
                [      //idx+1 = 第N轮争夺期
                    long,      //0U 本轮争夺期开始时间
                    long,      //1U 本轮争夺期结束时间
                ]
            ],
            long,      //5U 战场结束期开始时间
            long,      //6U 副本开启期开始前x秒的横幅
            long,      //7U 参战委派期结束时间
        ],
        "battle_info":     //战场属性
        {
            // 见project/V7.2.3/协议/活动相关协议/活动/黄金圣碑/配置协议/map.txt
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
v7.2.3 | 新增副本-黄金圣碑  
  
* * *

### 6.18.黄金圣碑-水晶技能

* * *

#### 黄金圣碑-水晶技能-黄金圣碑-水晶技能

  * **命令字** **_fuben_operate_alliance_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fuben_info | json | {xxx} | 1 | 副本信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fuben_operate_alliance&key0={xxx}

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-1)//非user json
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-2)//fuben_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-3)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-4)//--------------使用水晶技能----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-5)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-6){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-7)    "command":"active_crystal_skill",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-8)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-9)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-10)        "sid":long,//副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-11)        "skill_id":long,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-12)        "cost_num":long, // 消耗的水晶数量
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-13)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-14)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-15)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-16)fuben_gm_crystal_skill
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-17)//---------------------------------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-18)
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-19)//--------------拉取水晶技能历史----------------
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-20)//request
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-21){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-22)    "command":"get_crystal_skill_active_history",
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-23)    "param":{
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-24)        "type":long, //副本type
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-25)        "sid":long,//副本id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-26)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-27)}
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-28)//rsp
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-29)fuben_gm_crystal_skill_history
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb33-30)//---------------------------------------

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

## 7.hu_tcp 接口协议

> service_type：2003

* * *

### 7.1.IAP

* * *

#### IAP-购买宝石

  * **命令字** **_gem_recharge_**

  * **补单命令字** **_operate_gem_recharge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
is_sand_box | 是否是沙盒账号 | 0-不是,1-是 | 1 | 0 | 后台自动生成-是否是沙盒账号  
hide_bonus | 是否购买失败 | 0-不是,1-是 | 1 | 0 | 后台自动生成-是否购买失败  
key0 | 原价对应宝石数 | TINT64 | 18000 | 1 |   
key1 | 客户端购买序号 | TINT64 | 100 | 1 |   
key2 | 充值类型 | TUINT32 | 1 | 1 | 见充值类型备注  
key3 | 交易id | string | abc | 1 |   
key4 | 运营促销id | TUINT32 | 1 | 1 |   
key5 | 具体促销方案id | TUINT32 | 1 | 1 |   
key6 | 商店类型 | TUINT32 | 1 | 1 | 见商店类型备注  
key7 | iap类型 | TUINT32 | 1 | 1 | 见iap类型备注  
key8 | 消耗物品 | type,id,num:type,id,num(string) | 1,160,1:1,161,1 | 1 | 传空表示没有  
key9 | 活动信息 | string | xxxxxx | 1 | 见key9备注  
key10 | 折扣价对应宝石数 | TINT64 | 9000 | 1 | 没有折扣传原价  
key11 | 批量购买礼包数量 | TUINT32 | 1 | 1 | 旧客户端不传 新客户端默认传1  
key15 | 是否是免费购买 | 0-不是,1-是 | 1 | 0 | 后台自动生成-是否是免费购买  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_recharge&is_sand_box=1&hide_bonus=1&key0=18000&key1=100&key2=1&key3=abc&key4=1&key5=1&key6=1&key7=1&key8=1,160,1:1,161,1&key9=xxxxxx&key10=9000&key11=1&key15=1

  * **充值流程**



> 本流程为markdowm版，web上可能看不出来
    
    
    sequenceDiagram
    
    loop 扣款
    app ->> platform: 发起充值
    platform ->> app: 扣款成功，返回订单
    end
    
    loop 充值-后台部分
    app ->> hu: gem_recharge请求
    
    loop 重复订单校验
    hu ->> aws_proxy: 拉取transaction
    aws_proxy ->> hu: 反包
    hu ->> hu: 重复订单校验
    end
    
    loop 真实充值校验
    hu ->> purchase_check: 普通充值req
    purchase_check ->> platform: req
    platform ->> purchase_check: rsp
    purchase_check ->> hu: rsp
    end
    
    loop 获取iap内容
    hu ->> iap_proxy: req
    iap_proxy ->> hu: rsp
    end
    
    loop 记录订单
    hu ->> aws_proxy: 写transaction
    aws_proxy ->> hu: 反包
    end
    
    hu ->> hu: 加奖励
    hu ->> app: 反包
    
    end
    
    app ->> platform: 消耗订单
    
    

  * **充值类型备注**

id | 备注  
---|---  
0 | 客户端购买  
1 | 运营模拟购买  
2 | 使用代金券  
3 | 补单代金券  
4 | 使用点券  
  
  * **商店类型备注**

id | 备注  
---|---  
0 | normal  
1 | evip  
2 | business ship  
3 | 场景iap  
4 | 周/月卡  
5 | evip尊享商城  
6 | 解锁成长基金  
7 | 回流礼包  
8 | 主题季卡  
9 | 自定礼包  
10 | 每日特惠  
11 | 免费礼包  
12 | 储值礼包  
13 | 普通商城高性价比  
14 | evip商城高性价比  
  
  * **iap类型备注**

key6 | 备注  
---|---  
4 | 周/月卡id  
6 | 多开成长基金event id  
  
  * **key9备注**



> 若传string，则为 “xxxxx”  
>  若传json，则为{“event_type”: int,“event_info”:{xxx}}

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
v5.2 | 改成新的一套接口  
  
* * *

#### IAP-新充值接口-通用参数说明

  * **命令字** **_gem_recharge_common_**

  * **补单命令字** **_operage_gem_recharge_common_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
transaction | 交易订单号 | string | 230001563409208 | store=ios | ios时同key3  
receipt | 交易令牌 | string | xxx | store=ios/amazon | amazon时同key3  
purchase_token | 交易令牌 | string | xxx | store=google/google_kr | android时同key3  
amazon_uid | 亚马逊商店账号uid | string | xxx | store=amazon |   
package_name | 安装包包名 | string | leyi.westgame | store=google/google_kr |   
order_id | 交易订单号 | string | GPA.3351-0898-8408-22006 | store=google/google_kr |   
item_id | 商店价位 | string | 10gems3 | 1 |   
user_id | 真实充值uid | TINT64 | 101100 | 1 |   
in_check | 是否在审核 | TINT32 | 1 | 1 | 审核期间无视白名单  
discount | 折扣券 | [[int,int]] | [[1,1]] | 使用时传 | [[id,num]]  
coupon | 代金券 | [[int,int]] | [[1,1]] | 使用时传 | [[id,num]]  
tickets | 点券 | [[int,int]] | [[1,1]] | 使用时传 | [[id,num]]  
key0 | 原价对应宝石数 | TINT64 | 18000 | 1 |   
key1 | 客户端购买序号 | TINT64 | 100 | 1 |   
key2 | 充值类型 | TUINT32 | 1 | 1 | 见充值类型备注  
key3 | 交易id | string | abc | 1 |   
key4 | 运营促销id | TINT64 | 1 | 1 | 必须是大于0的值  
key5 | 具体促销方案id | TINT64 | 1 | 1 |   
key6 | 实际对应宝石数 | TINT64 | 9000 | 1 | 折扣情况  
key7 | 商店类型 | string | type_1 | 1 | 见商店类型备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_recharge_common&transaction=230001563409208&receipt=xxx&purchase_token=xxx&amazon_uid=xxx&package_name=leyi.westgame&order_id=GPA.3351-0898-8408-22006&item_id=10gems3&user_id=101100&in_check=1&discount=[[1,1]]&coupon=[[1,1]]&tickets=[[1,1]]&key0=18000&key1=100&key2=1&key3=abc&key4=1&key5=1&key6=9000&key7=type_1

  * **充值类型备注**

id | 备注  
---|---  
0 | 客户端购买  
1 | 运营模拟购买  
2 | 使用代金券  
3 | 补单代金券  
4 | 使用点券  
  
  * **充值流程**



> 本流程为markdowm版，web上可能看不出来
    
    
    sequenceDiagram
    
    loop 扣款
    app ->> platform: 发起充值
    platform ->> app: 扣款成功，返回订单
    end
    
    loop 充值-后台部分
    app ->> hu: gem_recharge请求
    
    loop 重复订单校验
    hu ->> aws_proxy: 拉取transaction
    aws_proxy ->> hu: 反包
    hu ->> hu: 重复订单校验
    end
    
    loop 真实充值校验
    hu ->> purchase_check: 普通充值req
    purchase_check ->> platform: req
    platform ->> purchase_check: rsp
    purchase_check ->> hu: rsp
    end
    
    loop 获取iap内容
    hu ->> iap_proxy: req
    iap_proxy ->> hu: rsp
    end
    
    loop 记录订单
    hu ->> aws_proxy: 写transaction
    aws_proxy ->> hu: 反包
    end
    
    hu ->> hu: 加奖励
    hu ->> app: 反包
    
    end
    
    app ->> platform: 消耗订单
    
    

  * **改动历史**

版本号 | 说明  
---|---  
v5.2 | 新增说明  
  
* * *

#### IAP-新充值接口-普通购买（未启用）

  * **命令字** **_gem_recharge_normal_**

  * **补单命令字** **_operage_gem_recharge_normal_**

  * **使用场景**




> 原商店类型：0，1，2，3，5

  * **备注**



>   * 5.2版本仅设计此接口，不实际接入使用  
> 
>   * 此处只列特殊key（从key8开始），通用key见【新充值接口-通用参数说明】
> 


  * **参数**

参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key8 | 原business_ship_idx | int32 | 1 | 1 | 商船idx+1  
key9 | 原business_ship_etime | int64 | 1679287509 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_recharge_normal&key8=1&key9=1679287509

  * **支持的商店类型**

id | 备注  
---|---  
type_0 | normal  
type_1 | evip  
type_2 | business ship  
type_3 | 场景iap  
type_5 | evip尊享商城  
  
  * **改动历史**

版本号 | 说明  
---|---  
v5.2 | 新增接口  
  
* * *

#### IAP-新充值接口-周月卡（未启用）

  * **命令字** **_gem_recharge_card_**

  * **补单命令字** **_operage_gem_recharge_card_**

  * **使用场景**




> 原商店类型：4

  * **备注**



>   * 5.2版本仅设计此接口，不实际接入使用  
> 
>   * 此处只列特殊key（从key8开始），通用key见【新充值接口-通用参数说明】
> 


  * **参数**

参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key8 | 周/月卡id | TUINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_recharge_card&key8=1

  * **支持的商店类型**

id | 备注  
---|---  
type_4 | 周/月卡  
  
  * **改动历史**

版本号 | 说明  
---|---  
v5.2 | 新增接口  
  
* * *

#### IAP-新充值接口-活动（已启用，仅接入新增活动）

  * **命令字** **_gem_recharge_event_**

  * **补单命令字** **_operate_gem_recharge_event_**

  * **使用场景**




> 原商店类型：6，7，8，9，10，11

  * **备注**



>   * 5.2版本仅设计此接口，并应用于新增活动，原商店类型本版本不接入  
> 
>   * 此处只列特殊key（从key8开始），通用key见【新充值接口-通用参数说明】
> 


  * **参数**

参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key8 | 活动信息 | {“event_type”: int,“event_id”: string,“event_info”:{透传参照运营协议gem_recharge_event中说明的event,具体详见114-event_proxy_new协议.txt或咨询运营}} | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_recharge_event&key8=1

  * **支持的商店类型**

id | 备注  
---|---  
type_6 | 解锁成长基金  
type_7 | 回流礼包  
type_8 | 主题季卡  
type_9 | 自定礼包  
type_10 | 每日特惠  
type_11 | 免费礼包  
type_15 | 活动商城:给运营74节点发送购买请求  
type_16 | 解锁分服季卡  
type_17 | 纯宝石商店  
type_18 | 活动商城:给运营114节点发送购买请求  
type_19 | 解锁分服季卡-优化  
  
  * **改动历史**

版本号 | 说明  
---|---  
v5.2 | 新增接口  
  
* * *

#### IAP-获取iap信息//(原有, 现修改参数)

  * **命令字** **_getdata_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key1 | id1,id2,id3,id4… | string | 1,2,3 | 1 | knight id v1.9后放弃使用  
key2 | iap_promote_info | string |  | 1 | svr_iap_promote_info中的数据  
create_time | create_time | int64 | 151515 | 1 |   
castle_lv | castle_lv | int32 | 1 | 1 |   
has_card | left_collect_count>0?1:0 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=getdata&key1=1,2,3&key2=&create_time=151515&castle_lv=1&has_card=1

  * **备注**



> left_collect_count来源于svr_iap_card  
>  has_card=用户当前是否有月卡没领完，0:没有未领取的月卡奖励1:有未领取的月卡奖励

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### IAP-收集iap卡奖励

  * **命令字** **_iap_card_reward_collect_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=iap_card_reward_collect

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.41 | 新增接口  
  
* * *

#### IAP-获取特定促销方案

  * **命令字** **_get_special_promote_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | product_id | int64 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_special_promote&key0=111

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.41 | 新增接口  
  
* * *

#### IAP-获取特定场景促销方案

  * **命令字** **_get_scene_promote_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | info | int64 | 1 | 1 | iap promote info  
key1 | line_id | string | 2434dsf | 1 | 虚拟iap_ida  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_scene_promote&key0=1&key1=2434dsf

  * **备注**



> iap周卡/月卡，收集iap卡奖励

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.41 | 新增接口  
  
* * *

#### IAP-拉取指定商城iap

  * **命令字** **_get_shop_promote_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key1 | cowboy list | string | 1:2:3 | 1 |   
key2 | iap_store | int64 | 1 | 1 | 1:evip  
key3 | iap_class | int64 | 1 | 1 |   
key4 | iap_promote_info | string |  | 1 | svr_iap_promote_info中的数据  
create_time | create_time | int64 | 151515 | 1 |   
castle_lv | castle_lv | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_shop_promote&key1=1:2:3&key2=1&key3=1&key4=&create_time=151515&castle_lv=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

#### IAP-触发场景iap

  * **命令字** **_get_trigger_promote_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | line_id | int64 | 1 | 1 | 虚拟iap_ida  
key1 | iap_promote_info | string |  | 1 | user json中的svr_iap_promote_info  
key2 | active_type | int64 | 1 | 1 | 1: 里程碑 2: 回天改命  
key3 | active_detail | int64 | 1 | 1 | key2  
key4 | trigger_time | int64 | 1 | 1 | 触发时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_trigger_promote&key0=1&key1=&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.6 | 新增接口  
  
* * *

#### IAP-获取iap名称

  * **命令字** **_get_iap_names_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_iap_names

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

#### IAP-查询iap订单信息

  * **命令字** **_op_get_purchase_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
is_subscription | 是否是查询订阅 | int64 | 1 | 0 | 订阅传1，非订阅传0 默认为非订阅0  
platform | 平台 | string | ios | 1 | ios、android、amazon  
transaction | 订单id | string | xxx | 1 | ios传transaction，android传purchase_token  
package_name | 包名 | string | leyi.westgame | 0 | 默认为leyi.westgame  
item_id | item_id | string | xxx | 1 | 非订阅可以不传，订阅传递xxxdays  
amazon_uid | amazon_uid | string | xxx | 0 | 查询amazon订单，必传，其他平台可以不传  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_get_purchase_info&is_subscription=1&platform=ios&transaction=xxx&package_name=leyi.westgame&item_id=xxx&amazon_uid=xxx

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

#### IAP-appcharge获取充值url

  * **命令字** **_gem_recharge_appcharge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
item_id | 商店product id | str | 100gems | 1 | appcharge  
priceCurrencyCode | 货币代码 | int | 1 | 1 | 当前仅支持USD  
priceAmountMicros | 货币价格,单位分 | int | 1 | 1 | 4.99  
deep_link | deeplink链接 | str | 1 | 1 |   
key0 | project id | 礼包促销方案pid | 499 | 1 |   
key1 | 客户端计算的实际价格 | 价格*100,如4.99则为499 | 499 | 1 | 客户端计算的包含appcharge折扣  
key2 | iap store | int | 1 | 1 | iap商店类型  
key3 | iap class | int | 1 | 1 | iap充值类型  
key4 | 消耗物品 | type,id,num:type,id,num(string) | 1 | 1 | 空表示没有  
key5 | buy num | int | 1 | 1 | 购买数量,默认1  
key6 | event_info | 见key6备注 | 1 | 1 | event info,同gem_recharge_event的key8 和 gem_rechage的key9  
key10 | 客户端透传参数 | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_recharge_appcharge&item_id=100gems&priceCurrencyCode=1&priceAmountMicros=1&deep_link=1&key0=499&key1=499&key2=1&key3=1&key4=1&key5=1&key6=1&key10=1

  * **充值类型备注**

id | 备注  
---|---  
0 | 客户端购买  
1 | 运营模拟购买  
2 | 使用代金券  
3 | 补单代金券  
4 | 使用点券  
  
  * **商店类型备注** >gem_recharge保持一致

id | 备注  
---|---  
0 | normal  
1 | evip  
2 | business ship  
3 | 场景iap  
4 | 周/月卡k’k  
5 | evip尊享商城  
6 | 解锁成长基金  
7 | 回流礼包  
8 | 主题季卡  
9 | 自定礼包  
10 | 每日特惠  
11 | 免费礼包  
12 | 储值礼包  
13 | 普通商城高性价比  
14 | evip商城高性价比  
  
  * **iap类型备注**

key6 | 备注  
---|---  
4 | 周/月卡id  
6 | 多开成长基金event id  
  
  * **key6备注**



> 若传string，则为 “xxxxx”  
>  若传json，则为{“event_type”: int,“event_info”:{xxx}}

  * **反包**



> svr_iap_appcharge_pay_url

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
v7.2.0 | 新增参数key6  
  
* * *

#### IAP-appcharge充值成功后处理接口(平台使用)

  * **命令字** **_op_gem_recharge_after_appcharge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
purchase_id | 订单id | str | 1 |  |   
key0 | 透传请求时候的meta_data字段 | son字符串 | 1 |  |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gem_recharge_after_appcharge&purchase_id=1&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### IAP-iap免费宝箱领奖

  * **命令字** **_claim_iap_free_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | pid | int | 1 |  |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_iap_free_chest&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.2.action通用

* * *

#### action通用-宝石加速

  * **命令字** **_gem_speed_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 123 | 1 |   
key1 | gem cost | int64 | 123 | 1 |   
key2 | second_class | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_speed_up&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### action通用-免费加速

  * **命令字** **_free_speed_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 123 | 1 |   
key1 | second_class | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=free_speed_up&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### action通用-取消action

  * **命令字** **_action_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | xxx123xxx | 1 |   
key1 | second_class | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=action_cancel&key0=xxx123xxx&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### action通用-拉取action警告信息

  * **命令字** **_get_warning_detail_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | xxx123xxx | 1 |   
key1 | action sec_class | int | 2 | 1 | action的sec_class  
key2 | tar_sid | int64 | 1 | 1 | action目标服务器  
key3 | tar_pos | int64 | 250600 | 1 | action目标地块  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_warning_detail_info&key0=xxx123xxx&key1=2&key2=1&key3=250600

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

### 7.3.ava联赛

* * *

#### ava联赛-报名

  * **命令字** **_ava_league_sign_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “123” | 1 | 联赛报名活动 event id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_sign_up&key0=“123”

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-取消报名

  * **命令字** **_ava_league_sign_up_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “123” | 1 | 联赛报名活动 event id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_sign_up_cancel&key0=“123”

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-添加参战人员

  * **命令字** **_ava_league_add_competition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 123 | 1 |   
key1 | type | int32 | 123 | 1 | 0:出站 1:替补  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_add_competition&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-删除参战人员

  * **命令字** **_ava_league_del_competition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 123 | 1 |   
key1 | type | int32 | 123 | 1 | 0:出站 1:替补  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_del_competition&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-修改参战人员 替补/出战

  * **命令字** **_ava_league_operate_competition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 123 | 1 |   
key1 | type | int32 | 123 | 1 | 0:出站 1:替补  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_operate_competition&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-报名出战

  * **命令字** **_ava_league_sign_up_competition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 123 | 1 | 0:出站 1:替补  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_sign_up_competition&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-撤销出战

  * **命令字** **_ava_league_sign_up_competition_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 123 | 1 | 0:出站 1:替补  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_sign_up_competition_cancel&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-领取结算弹窗奖励

  * **命令字** **_ava_league_result_reward_claim_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id_str | string | “123” | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_league_result_reward_claim&key0=“123”

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### ava联赛-联赛战况信息

  * **命令字** **_get_ava_league_war_situation_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “123” | 1 |   
key1 | sid | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_ava_league_war_situation&key0=“123”&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

### 7.4.evip

* * *

#### evip-领取evip宝箱

  * **命令字** **_claim_evip_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 领取的宝箱类型,1-每日免费宝箱，2-特权等级宝箱,3-节日礼物  
key1 | lv | int32 | 1 | 1 | 宝箱的特权等级  
key2 | festival_type | int32 | 1 | 1 | 节日礼物类型  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_evip_reward&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
v7.2.6 | 新增参数key2  
  
* * *

#### evip-购买evip商品

  * **命令字** **_evip_shop_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1212_34 | 1 |   
key1 | goods_id | string | 1 | 1 | 要购买的商品id  
key2 | num | int64 | 12 | 1 | 购买数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=evip_shop_buy&key0=1212_34&key1=1&key2=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

#### evip-获取evip商店活动数据

  * **命令字** **_get_evip_shop_data_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 414515_12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_evip_shop_data&key0=414515_12

  * **备注**



> svr_evip_shop_data

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

#### evip-拉取evip信息

  * **命令字** **_get_evip_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | login_days | int64 | 1 | 1 |   
key1 | login_days_update_time | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_evip_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

#### evip-增加evip点数（op接口）

  * **命令字** **_op_add_evip_point_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | score | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_evip_point&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

#### evip-激活evip

  * **命令字** **_active_evip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=active_evip

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

#### evip-激活evip（运营使用）

  * **命令字** **_op_active_evip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_active_evip

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

### 7.5.globalres

* * *

#### globalres-通用出售，可用于皮肤item、碎片的出售

  * **命令字** **_global_res_sell_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type,id,num:type,id,num | string | 1,1,1:1,2,1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=global_res_sell&key0=1,1,1:1,2,1

  * **备注**



> rsp:user json  
>  key0=用:分割出售的对象,用,分割对象type,id,num

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### globalres-通用合成

  * **命令字** **_global_res_compose_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type,id,num | string | 1,2,1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=global_res_compose&key0=1,2,1

  * **备注**



> key0=要合成的物品 type,id,num之间用”,”隔开拼成字符串

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### globalres-宝石月卡半价折扣券，检查是否存在

  * **命令字** **_globalres_check_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type,id,num:type,id,num | string | 1,1,1:1,2,1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=globalres_check&key0=1,1,1:1,2,1

  * **备注**



> key0=字符串列表, 用:分割不同物品,用,分割对象type,id,num

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

#### globalres-兜底金币购买

  * **命令字** **_guaranteed_global_gem_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | global_type | int | 1 | 1 |   
key1 | global_id | int | 1 | 1 |   
key2 | buy_num | int | 1 | 1 | 购买的份数  
key3 | cost_gem | int | 1 | 1 | 花费金币数  
key4 | auto_use | int | 1 | 1 | 是否获取后自动使用  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=guaranteed_global_gem_buy&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### globalres-批量购买并使用

  * **命令字** **_common_item_buy_and_use_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | buy_type | int | 1 | 1 | 0 普通购买 1 金币兜底购买  
key1 | global_type | int | 1 | 1 | 仅支持道具  
key2 | global_id | int | 1 | 1 | id  
key3 | buy_num | int | 1 | 1 | 购买的数量/兜底购买则是份数  
key4 | cost_gem | int | 1 | 1 | 花费金币数  
key5 | traget id | int | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=common_item_buy_and_use_batch&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.7 | 新增接口  
  
* * *

### 7.6.hunt小队系统

* * *

#### hunt小队系统-获取自己队伍的详细信息

  * **命令字** **_get_self_hunt_team_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_hunt_team_info&key0=1

  * **备注**



> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-获取其他队伍的详细信息

  * **命令字** **_get_other_hunt_team_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 队伍 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_other_hunt_team_info&key0=1&key1=1

  * **备注**



> 反包:svr_other_hunt_team

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-获取队伍列表&筛选列表

  * **命令字** **_get_hunt_team_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | join_type | int64 | 1 | 1 | 入队类型,-1为全部  
key2 | timezone | int64 | 1 | 1 | 时区,-1为全部  
key3 | nick | str | 1 | 1 | 简称,空为不搜索简称  
key4 | page_idx | int64 | 1 | 1 | 请求的页数,从0开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_hunt_team_list&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> 反包:svr_hunt_team_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-获取最近组队玩家列表

  * **命令字** **_get_hunt_recently_team_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_hunt_recently_team_player&key0=1

  * **备注**



> 反包:svr_hunt_recently_team_player

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-创建队伍

  * **命令字** **_create_hunt_team_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | nick | str | 1 | 1 | 活动 id  
key2 | name | str | 1 | 1 | 活动 id  
key3 | join_type | int64 | 1 | 1 | 活动 id  
key4 | timezone_id | int64 | 1 | 1 | 活动 id  
key5 | icon | int64 | 1 | 1 | 活动 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=create_hunt_team&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1

  * **备注**



> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-加入队伍

  * **命令字** **_join_hunt_team_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | req_join_type | int64 | 1 | 1 | 1申请加入,2随机加入  
key2 | team_id | int64 | 1 | 1 | 队伍id，申请加入时传  
key3 | zone_id | int64 | 1 | 1 | 时区id，随机加入时传  
key4 | join_scene | int64 | 1 | 1 | 加入场景 1:快速加入  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=join_hunt_team&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



若用户未选择时区id，key3传0即可

> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-退出/解散队伍

  * **命令字** **_leave_hunt_team_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 队伍id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=leave_hunt_team&key0=1&key1=1

  * **备注**



> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-设置队伍信息

  * **命令字** **_set_hunt_team_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 队伍id  
key2 | team_info | json | 1 | 1 | 要修改的信息,见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_hunt_team_info&key0=1&key1=1&key2=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-1)//team_info,请求时只给出需要修改的信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-2){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-3)    "icon":int, //图标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-4)    "nick":str, //简称
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-5)    "name":str, //名字
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-6)    "timezone_id":int, //时区
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-7)    "join_type":int, //入队方式
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb36-8)}

> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-处理队伍加入申请

  * **命令字** **_handle_hunt_team_req_join_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 自己队伍id  
key2 | uid | int64 | 1 | 1 | 玩家id  
key3 | type | int64 | 1 | 1 | 处理方式：1同意,2拒绝  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=handle_hunt_team_req_join&key0=1&key1=1&key2=1&key3=1

  * **备注**



> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-邀请玩家加入队伍

  * **命令字** **_invite_player_join_hunt_team_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 自己队伍id  
key2 | uid_list | str | 1,2,3 | 1 | 逗号分隔玩家id列表,全部邀请时传多个  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=invite_player_join_hunt_team&key0=1&key1=1&key2=1,2,3

  * **备注**

  * **改动历史**


版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-踢出队伍

  * **命令字** **_kick_hunt_team_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 自己队伍id  
key2 | uid | int64 | 1 | 1 | 玩家id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=kick_hunt_team&key0=1&key1=1&key2=1

  * **备注** > 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**


版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-处理队伍邀请

  * **命令字** **_handle_hunt_team_invite_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 队伍id  
key2 | uid | int64 | 1 | 1 | 发出邀请的玩家id  
key3 | type | int64 | 1 | 1 | 处理方式：1同意,2拒绝  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=handle_hunt_team_invite&key0=1&key1=1&key2=1&key3=1

  * **备注** > 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**


版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-获取指定时区的所有队伍信息(运营匹配用)

  * **命令字** **_op_get_all_hunt_team_by_timezone_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | timezone_id | int64 | 1 | 1 | 时区id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_get_all_hunt_team_by_timezone&key0=1&key1=1

  * **备注** > 反包:svr_hunt_timezone_team_list

  * **改动历史**


版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-同步队伍匹配结果(运营匹配用)

  * **命令字** **_op_sync_hunt_team_match_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | timezone_id | int64 | 1 | 1 | 时区id  
key2 | result | json | 1 | 1 | 匹配结果信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_sync_hunt_team_match_result&key0=1&key1=1&key2=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-1)//匹配结果信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-2){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-3)    "id": //队伍id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-4)    {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-5)        "begin_time":long, //战斗开始时间
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-6)        "end_time":long, //战斗结束时间
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-7)        "prepare_time":long, //战斗准备时间
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-8)        "stage_time1":long, //阶段1时间
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-9)        "stage_time2":long, //阶段2时间
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-10)        "stage_time3":long, //阶段3时间
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-11)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb37-12)}

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-重设队伍时区(队伍匹配失败或战斗结束失效后重新报名)

  * **命令字** **_reset_hunt_team_timezone_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 队伍id  
key2 | team_info | json | 1 | 1 | 要修改的信息,见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_hunt_team_timezone&key0=1&key1=1&key2=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-1)//team_info,请求时只给出需要修改的信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-2){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-3)    "icon":int, //图标
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-4)    "nick":str, //简称
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-5)    "name":str, //名字
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-6)    "timezone_id":int, //时区
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-7)    "join_type":int, //入队方式
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb38-8)}

> 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-一键忽略入队申请

  * **命令字** **_ignore_all_team_req_join_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | team_id | int64 | 1 | 1 | 队伍id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ignore_all_team_req_join&key0=1&key1=1

  * **备注** > 反包:svr_self_hunt_team、svr_hunt_req_join_list

  * **改动历史**


版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-获取符合条件的小队信息

  * **命令字** **_get_other_hunt_team_info_by_condition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
key1 | type | int64 | 1 | 1 | 类型1：表示从指定时区向后循环检索合适加入的小队  
key2 | timezone_id | int64 | 1 | 1 | 时区id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_other_hunt_team_info_by_condition&key0=1&key1=1&key2=1

  * **备注**



> 反包:svr_other_hunt_team

  * **改动历史**

版本号 | 说明  
---|---  
v5.6.0 | 新增接口  
  
* * *

#### hunt小队系统-获取队伍信息预览

  * **命令字** **_get_hunt_team_info_overview_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 活动 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_hunt_team_info_overview&key0=1

  * **备注**



> 反包:svr_hunt_team_overview

  * **改动历史**

版本号 | 说明  
---|---  
v5.9.1 | 新增接口  
  
* * *

### 7.7.kvk

* * *

#### kvk-拉取kvk计分榜

  * **命令字** **_get_kvk_score_board_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_info | string |  | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kvk_score_board&key0=

  * **改动历史**

版本号 | 说明  
---|---  
v2.0 | 新增接口  
  
* * *

#### kvk-发送kvk活动结果

  * **命令字** **_send_kvk_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 | target sid  
key1 | result | int64 | 1 | 1 |   
key2 | info | string | {“sid”:{“points”:1}} | 1 | 所有参赛svr都要  
key3 | victory_reward | string | {“wild_id”: int, .. } | 1 | 同svr_kvk_event_list中victory_reward字段  
key4 | version | int64 | 1 | 1 | 1s  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=send_kvk_result&key0=1&key1=1&key2={“sid”:{“points”:1}}&key3={“wild_id”: int, .. }&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.9.3 | 新增接口  
  
* * *

#### kvk-kvk活动赠送分

  * **命令字** **_send_kvk_score_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int32 | 1 | 1 |   
key1 | score | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=send_kvk_score&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.9.3 | 新增接口  
  
* * *

#### kvk-kvk战况

  * **命令字** **_get_kvk_war_situation_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kvk_war_situation&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.9.3 | 新增接口  
  
* * *

#### kvk-原kvk预告期战场争夺数据

  * **命令字** **_op_kvk_prepare_fighting_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int | 1 | 1 | sid  
key1 | battle_info | json_str | 3 | 1 | 战场信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_kvk_prepare_fighting_reward&key0=1&key1=3

  * **battle info**


    
    
    {
        "battle_info":
        {
            "map_conf": //战场配置
            {
                "building":    //建筑得分速率
                {
                    "${wild_class}": // 根据event_id拿到pid
                                      // 从kvk_event_project.json 取出pid中calc_score=>kingdom_building_score_list_new
                                      // 取到score_type=116, score_id_map    : 0(王座) 转为 wild_class=8/ 1(要塞) 转为 wild_class=12
                                      // 后台自行处理对应做一下转化 building id来自game_kingdom_building
                    [
                        long,   //服务器得分速率(x/min)
                    ]
                }
            }
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.9 | 新增接口  
  
* * *

### 7.8.quest及活跃任务

* * *

#### quest及活跃任务-日常任务和联盟任务——开始

  * **命令字** **_quest_start_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest type | int64 | 1 | 1 | 1:daily quest, 2:alliance quest  
key1 | quest idx | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=quest_start&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### quest及活跃任务-日常任务和联盟任务——领取奖励

  * **命令字** **_quest_reward_collect_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest type | int64 | 1 | 1 | 1: daily quest, 2: alliance quest  
key1 | quest idx | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=quest_reward_collect&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### quest及活跃任务-强制刷新任务（使用宝石或者物品）

  * **命令字** **_refresh_time_quest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 1: daily quest, 2: alliance quest  
key1 | gem cost | int64 | 1 | 1 | 消耗宝石数量,下同  
key2 | item id | int32 | 1 | 1 | 使用物品时，key1为0  
key3 | type | int32 | 1 | 1 | 0代表使用物品 1代表使用loy  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=refresh_time_quest&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### quest及活跃任务-收集top quest(不包括升降任务)

  * **命令字** **_quest_claim_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=quest_claim&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### quest及活跃任务-标记清除标记

  * **命令字** **_task_clear_flag_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=task_clear_flag

  * **备注**



> 清除掉task的is_new 和 is_going标记

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.33 | 新增接口  
  
* * *

#### quest及活跃任务-特殊操作

  * **命令字** **_task_operate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | operate_type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=task_operate&key0=1

  * **备注**



> 用于上报特殊操作,比如查看世界地图,type:1–查看世界地图;2 –查看新邮件;3—查看新report;4—查看联盟帮助;5—发送联盟chat

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.33 | 新增接口  
  
* * *

#### quest及活跃任务-设置指定questid完成

  * **命令字** **_set_quest_finished_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_quest_finished&key0=1

  * **备注**



> 仅能对无对应taskid的quest指定完成

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

### 7.9.vip

* * *

#### vip-解锁vip阶段

  * **命令字** **_unlock_vip_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
key1 | gem_cost | int64 | 1 | 1 |   
key2 | type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=unlock_vip_stage&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.52 | 新增接口  
  
* * *

#### vip-解锁vip下一阶段

  * **命令字** **_unlock_vip_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
key1 | gem_cost | int64 | 1 | 1 |   
key2 | cost_type | int32 | 1 | 1 | 1—消耗金币，2—消耗道具  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=unlock_vip_stage&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.52 | 新增接口  
  
* * *

### 7.10.web商店

* * *

#### web商店-web登陆

  * **命令字** **_op_web_login_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | is login | int32 | 1 | 1 | 登陆请求带1, 非登陆的验证请求带0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_web_login_get&uid=1&key0=1&key1=1

  * 命令字反包格式 – http请求反包协议


    
    
        "svr_web_player_info":
        {
            "uid": string,
            "name": string,      // 玩家名
            "avatarRss": string, // 完整的头像资源路径
            "ksid": string,
            "attributes": //用户属性,针对部分商品,用来筛选该用户是否可以购买;可以随意添加,但必须跟web商品配置的key相同
            [
                {
                    "key": string, //比如主城等级, castle_lv...
                    "val": string
                }
            ]
        }

  * **改动历史**

版本号 | 说明  
---|---  
v5.7.0 | 新增接口  
v5.7.0 | 添加key1  
v5.9.1 | key0改成只有uid,后台会做兼容  
  
* * *

#### web商店-web充值

  * **命令字** **_op_web_iap_recharge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | trans_id | string | 1 | 1 | 支付唯一凭证,平台组保证全平台唯一  
key2 | paid_virtual_good_sku | string | 1 | 1 | 购买的付费内容sku  
key3 | price | int | 499 | 1 | 原价,美分  
key4 | real_paid | int | 499 | 1 | 实际支付金额,美分  
key5 | promo_code | string | abc | 1 | 促销码,不使用促销码时传空  
key6 | external_id | string | abc | 1 | 外部id,不使用促销码时传空  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_web_iap_recharge&uid=1&key0=1&key1=1&key2=1&key3=499&key4=499&key5=abc&key6=abc

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v5.7.0 | 新增接口  
v5.9.1 | key0改成只有uid,后台会做兼容  
v6.1 | 添加key5、key6  
  
* * *

#### web商店-web领取免费奖励

  * **命令字** **_op_web_claim_free_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | free_bundle_sku | string | 1 | 1 | 领取的免费捆绑包sku  
key2 | free_virtual_good_sku_list | string | 1,2,3 | 1 | 捆绑包下免费内容sku, 以逗号隔开  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_web_claim_free_reward&uid=1&key0=1&key1=1&key2=1,2,3

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v5.7.0 | 新增接口  
v5.9.1 | key0改成只有uid,后台会做兼容  
  
* * *

#### web商店-web使用优惠券(码)

  * **命令字** **_op_web_active_coupon_code_**
  * **参数**

参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | coupon_virtual_good_sku_list | string | 1 | 1 | 兑换的优惠券sku列表,以逗号隔开  
key2 | coupon_code | string | abc | 1 | 优惠券(码)  
key3 | external_id | string | abc | 1 | 外部id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_web_active_coupon_code&uid=1&key0=1&key1=1&key2=abc&key3=abc

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### web商店-web自动扣包

  * **命令字** **_op_web_iap_refund_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | trans_id | string | 1 | 1 | 支付唯一凭证,平台组保证全平台唯一  
key2 | reason_code | int32 | 1 | 1 | 退款理由  
key10 | purchase_time | int64 | 123 | 0 | 后台补充日志, 充值时间  
key11 | sku | string | xx-123 | 0 | 后台补充日志, 购买的sku  
key12 | is_succ | int32 | 1 | 0 | 后台补充日志, 该次扣包是否需要扣包  
key13 | price | int64 | 1 | 0 | 后台补充日志, 价格  
key14 | paid | int64 | 1 | 0 | 后台补充日志, 实际付费金额  
key15 | platform | string | abc | 0 | 后台补充日志, 订单平台来源  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_web_iap_refund&uid=1&key0=1&key1=1&key2=1&key10=123&key11=xx-123&key12=1&key13=1&key14=1&key15=abc

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v5.7.0 | 新增接口  
v5.9.1 | key0改成只有uid,后台会做兼容  
v7.0.3 | 新增参数key15  
  
* * *

#### web商店-web手动扣包

  * **命令字** **_op_web_iap_refund_manual_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 填uid  
key1 | trans_id | string | 1 | 1 | 支付唯一凭证  
key2 | reason_code | int32 | 1 | 1 | 退款理由, 填0  
key10 | purchase_time | int64 | 123 | 0 | 后台补充日志, 充值时间  
key11 | sku | string | xx-123 | 0 | 后台补充日志, 购买的sku  
key12 | is_succ | int32 | 1 | 0 | 后台补充日志, 该次扣包是否需要扣包  
key13 | price | int64 | 1 | 0 | 后台补充日志, 价格  
key14 | paid | int64 | 1 | 0 | 后台补充日志, 实际付费金额  
key15 | platform | string | abc | 0 | 后台补充日志, 订单平台来源  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_web_iap_refund_manual&uid=1&key0=1&key1=1&key2=1&key10=123&key11=xx-123&key12=1&key13=1&key14=1&key15=abc

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v5.7.0 | 新增接口  
v7.0.3 | 新增参数key15  
  
* * *

#### web商店-appcharge登陆

  * **命令字** **_op_appcharge_login_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | is login | int32 | 1 | 1 | 登陆请求带1, 非登陆的验证请求带0  
key2 | is bind | int32 | 1 | 0 | 存在且为1时代表是社区机器人绑定的那一条  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_appcharge_login_get&uid=1&key0=1&key1=1&key2=1

  * 命令字反包格式 – http请求反包协议


    
    
        "svr_web_player_info":
        {
            "uid": string,
            "name": string,      // 玩家名
            "avatarRss": string, // 完整的头像资源路径
            "ksid": string,
            "attributes": //用户属性,针对部分商品,用来筛选该用户是否可以购买;可以随意添加,但必须跟web商品配置的key相同
            [
                {
                    "key": string, //比如主城等级, castle_lv...
                    "val": string
                }
            ]
        }

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
v7.1.1 | 新增key2  
  
* * *

#### web商店-appcharge充值

  * **命令字** **_op_appcharge_iap_recharge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | trans_id | string | 1 | 1 | 支付唯一凭证,平台组保证全平台唯一  
key2 | paid_virtual_good_sku | string | 1 | 1 | 购买的付费内容sku  
key3 | price | int | 499 | 1 | 原价,美分  
key4 | real_paid | int | 499 | 1 | 实际支付金额,美分  
key5 | promo_code | string | abc | 1 | 促销码,不使用促销码时传空  
key6 | external_id | string | abc | 1 | 外部id,不使用促销码时传空  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_appcharge_iap_recharge&uid=1&key0=1&key1=1&key2=1&key3=499&key4=499&key5=abc&key6=abc

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

#### web商店-appcharge领取免费奖励

  * **命令字** **_op_appcharge_claim_free_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | free_bundle_sku | string | 1 | 1 | 领取的免费捆绑包sku  
key2 | free_virtual_good_sku_list | string | 1,2,3 | 1 | 捆绑包下免费内容sku, 以逗号隔开  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_appcharge_claim_free_reward&uid=1&key0=1&key1=1&key2=1,2,3

  * 命令字反包格式 – 空

  * **改动历史**


版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

#### web商店-官网门户登陆

  * **命令字** **_op_offical_web_login_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | id | string | 1 | 1 | 由uid构成  
key1 | request_type | int32 | 1 | 1 | 1.login 2.validate  
key2 | access_token | string | abc | 1 | request_type为1时, 该字段为空  
key3 | login type | int32 | 1 | 0 | 1->uid登陆,2->token登陆,3->非登陆验证  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_offical_web_login_get&uid=1&key0=1&key1=1&key2=abc&key3=1

  * 命令字反包格式 – http请求反包协议


    
    
        "svr_offical_web_player_info":
        {
            "accessToken" : string, // 玩家的唯一身份标识, 随机字符串, login时返回, 且每次登录需要改变, 用于validate md5sum(uid+登陆时间+随机数)
            "name" : stirng, //用户名
            "image" : string, //用户头像链接
            "email" : string, //为空, 暂定不传
            "attributes" : [  //门户网站上展示的属性
                {
                    "key" : string,                 // 属性唯一标识符
                    "value" : string,               // 属性展示文本
                    "label" : string,               // 人类可读的属性标签
                    "icon" : string,                // 属性图标链接
                }
            ],
            "currencies" : [  //门户网站上展示的货币
                {
                    "key" : string,                 // 货币唯一标识符
                    "value" : int,                  // 向用户显示的数字
                    "label" : string,               // 人类可读的标签
                    "icon" : string,                // 货币图标链接
                }
            ],
            "xsollaAttributes" : [  //xsolla上记录的属性, 用于实现针对不同属性的商品展示
                {
                    "key" : string,                 // 属性唯一标识符
                    "value" : string,       // 属性值
                }
            ]
        }

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
v7.2.2 | 新增key3  
  
* * *

#### web商店-拉取appcharge第三方支付入口开关

  * **命令字** **_op_get_iap_appcharge_flag_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
region_code | 地区码 | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_get_iap_appcharge_flag&region_code=1

  * 命令字反包格式 – http请求反包协议


    
    
        "svr_iap_appcharge_flag":
        {
            "open": int, // 0 关闭 1 开放
        }

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

#### web商店-拉取官网登陆token

  * **命令字** **_get_offical_login_token_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_offical_login_token&uid=1

  * 命令字反包格式


    
    
        svr_offical_login_token

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.11.个人称号

* * *

#### 个人称号-使用个人称号

  * **命令字** **_player_title_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | title_id | int64 | 1 | 1 | 称号 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=player_title_put_on&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4.0 | 新增接口  
  
* * *

#### 个人称号-op接口添加个人称号

  * **命令字** **_op_add_player_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | title_id | int64 | 1 | 1 | 称号 id  
key1 | time | int64 | 1 | 1 | 称号 到期时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_player_title&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4.0 | 新增接口  
  
* * *

#### 个人称号-op接口移除个人称号

  * **命令字** **_op_remove_player_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | title_id | int64 | 1 | 1 | 称号 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_remove_player_title&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4.0 | 新增接口  
  
* * *

#### 个人称号-op接口设置个人称号过期时间

  * **命令字** **_op_set_player_title_expired_time_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | title_id | int64 | 1 | 1 | 称号 id  
key1 | time | int64 | 1 | 1 | 称号 到期时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_player_title_expired_time&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4.0 | 新增接口  
  
* * *

### 7.12.主城等级冲刺任务

* * *

#### 主城等级冲刺任务-领取奖励

  * **命令字** **_claim_castle_lv_event_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 15_34 | 1 |   
key1 | castle_lv | int64 | 1 | 1 | 任务对应的主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_castle_lv_event_reward&key0=15_34&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

### 7.13.书签

* * *

#### 书签-添加书签

  * **命令字** **_bookmark_add_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | marked pos | int32 | 1 | 1 |   
key1 | nickname | string | sdfg | 1 |   
key2 | mark type | int8 | 1 | 1 | 三种type，单选  
key3 | sid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=bookmark_add&key0=1&key1=sdfg&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.19 | 新增接口  
  
* * *

#### 书签-更新书签

  * **命令字** **_bookmark_updt_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | pos list | string | 2500600,1520168 | 1 | (以,分隔)  
key1 | nickname list | string | wer,werr | 1 | (以,分隔)  
key2 | type list | string | 1,23,6 | 1 | (以,分隔)  
key3 | sid list | string | ,1,2,3 | 1 | (以,分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=bookmark_updt&key0=2500600,1520168&key1=wer,werr&key2=1,23,6&key3=,1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.19 | 新增接口  
  
* * *

#### 书签-删除书签

  * **命令字** **_bookmark_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | pos list | string | 2500600,1520168 | 1 | (以,分隔)  
key1 | sid list | string | ,1,2,3 | 1 | (以,分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=bookmark_del&key0=2500600,1520168&key1=,1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.19 | 新增接口  
  
* * *

#### 书签-增加/删除/更新联盟标记

  * **命令字** **_al_bookmark_update_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | marked pos | int64 | 1500600 | 1 |   
key1 | nickname | string | sdfdf | 1 |   
key2 | sid | int32 | 1 | 1 |   
key3 | flag id | int64 | 1 | 1 |   
key4 | operate type | int64 | 1 | 1 | 0 :add 1:del 2: update  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_bookmark_update&key0=1500600&key1=sdfdf&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.8 | 新增接口  
  
* * *

### 7.14.任务

* * *

#### 任务-日常/联盟任务开始

  * **命令字** **_quest_start_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest_type | int64 | 123 | 1 | 1-日常任务 2-联盟任务 6-vip任务  
key1 | quest_idx | int64 | 1230123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=quest_start&key0=123&key1=1230123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### 任务-自动完成领取任务奖励

  * **命令字** **_quest_reward_collect_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest_type | int64 | 123 | 1 | 1-日常任务 2-联盟任务 6-vip任务  
key1 | quest_idx | int64 | 1230123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=quest_reward_collect&key0=123&key1=1230123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### 任务-批量自动完成一键领取任务奖励

  * **命令字** **_batch_quest_reward_collect_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest_type | int64 | 123 | 1 | 1-日常任务 2-联盟任务 6-vip任务  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=batch_quest_reward_collect&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

### 7.15.传世之器

* * *

#### 传世之器-传世之器合成

  * **命令字** **_heirloom_compose_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 123 | 1 | 数值id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_compose&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器升级

  * **命令字** **_heirloom_levelup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 123 | 1 | 数值id  
key1 | target_level | int32 | 6 | 1 | 目标等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_levelup&key0=123&key1=6

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器摆放&卸下&替换

  * **命令字** **_heirloom_setup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot | int32 | 1 | 1 | 数值配置的槽位id  
key1 | op_type | int32 | 123 | 1 | 1->卸下, 2->摆放, 3->替换  
key2 | new_id | int32 | 123 | 1 | 数值id, 要摆放上去的传世之器id, 卸下时传-1  
key3 | old_id | int32 | 123 | 1 | 数值id, 原来已摆放上去的传世之器id, 原来没有摆放时传-1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_setup&key0=1&key1=123&key2=123&key3=123

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器阵容设置

  * **命令字** **_heirloom_lineup_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | lineup_info | string | 1:1001,2:1002 | 1 | 以逗号分隔,表示每个槽位摆放的id,然后以冒号分隔,分别代表槽位及id。未摆放的槽位不放在参数里  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_lineup_change&key0=1:1001,2:1002

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器预设设置

  * **命令字** **_heirloom_preset_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
key1 | slot | int32 | 1 | 1 | 数值配置的槽位id  
key2 | op_type | int32 | 123 | 1 | 1->卸下, 2->摆放, 3->替换  
key3 | new_id | int32 | 123 | 1 | 数值id, 要摆放上去的传世之器id, 卸下时传-1  
key4 | old_id | int32 | 123 | 1 | 数值id, 原来已摆放上去的传世之器id, 原来没有摆放时传-1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_change&key0=1&key1=1&key2=123&key3=123&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器预设改名

  * **命令字** **_heirloom_preset_set_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
key1 | new_name | string | preset_1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_set_name&key0=1&key1=preset_1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器预设应用

  * **命令字** **_heirloom_preset_apply_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_apply&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器预设重置

  * **命令字** **_heirloom_preset_reset_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_reset&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-op设置传世之器等级

  * **命令字** **_op_set_heirloom_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id_list | string | 1 | 1001,1002 | id列表,逗号分隔.-1代表本服开放的所有  
key1 | level | int32 | 1 | 1 | 等级,小于等于0为删除  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_heirloom&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-op设置传世之器碎片

  * **命令字** **_op_set_heirloom_pieces_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id_list | string | 1 | 1001,1002 | id列表,逗号分隔.-1代表本服开放的所有  
key1 | num | int32 | 1 | 1 | 数量,小于等于0为删除  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_heirloom_pieces&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增接口  
  
* * *

#### 传世之器-传世之器组摆放&卸下&替换

  * **命令字** **_heirloom_setup_group_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type | int32 | 123 | 1 | 1->卸下, 2->摆放, 3->替换  
key1 | group_id | int32 | 1 | 1 | 数值配置的符文id  
key2 | slot_id | int32 | 1 | 1 | 数值配置的槽位id  
key3 | new_id | int32 | 123 | 1 | 数值id, 要摆放上去的传世之器id, 卸下时传-1  
key4 | old_id | int32 | 123 | 1 | 数值id, 原来已摆放上去的传世之器id, 原来没有摆放时传-1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_setup_group&key0=123&key1=1&key2=1&key3=123&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 传世之器-传世之器组预设设置

  * **命令字** **_heirloom_preset_change_group_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
key1 | op_type | int32 | 123 | 1 | 1->卸下, 2->摆放, 3->替换  
key2 | group_id | int32 | 1 | 1 | 数值配置的符文id  
key3 | slot_id | int32 | 1 | 1 | 数值配置的槽位id  
key4 | new_id | int32 | 123 | 1 | 数值id, 要摆放上去的传世之器id, 卸下时传-1  
key5 | old_id | int32 | 123 | 1 | 数值id, 原来已摆放上去的传世之器id, 原来没有摆放时传-1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_change_group&key0=1&key1=123&key2=1&key3=1&key4=123&key5=123

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 传世之器-传世之器组预设改名

  * **命令字** **_heirloom_preset_set_name_group_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
key1 | new_name | string | preset_1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_set_name_group&key0=1&key1=preset_1

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 传世之器-传世之器组预设应用

  * **命令字** **_heirloom_preset_apply_group_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_apply_group&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 传世之器-传世之器组预设重置

  * **命令字** **_heirloom_preset_reset_group_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 预设下标, 从1开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_preset_reset_group&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 传世之器-传世之器训练

  * **命令字** **_heirloom_train_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | TINT64 | 1021 | 1 | 1  
key1 | cur_lv | TINT64 | 1 | 1 | 当前的等级-后台会校验  
key2 | target_lv | TINT64 | 1 | 1 | 目标的等级-此处一定是cur_lv+1  
key3 | 培养消耗 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_train&key0=1021&key1=1&key2=1&key3=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 传世之器-传世之器通用碎片兑换

  * **命令字** **_heirloom_universal_pieces_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 万能传世之器碎片id | TINT64 | 121 | 1 |   
key1 | 万能传世之器碎片数量 | TINT64 | 21 | 1 |   
key2 | 目标传世之器碎片id | TINT64 | 122 | 1 |   
key3 | 目标传世之器碎片数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_universal_pieces_exchange&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v6.9 | 新增接口  
  
* * *

#### 传世之器-传世之器改装解锁

  * **命令字** **_heirloom_modification_unlock_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 123 | 1 | 传世之器的id  
key1 | 解锁所需资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key2 | star | int32 | 123 | 1 | 要解锁的改装阶段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_modification_unlock&key0=123&key1=[{“a”:[1,0,1000]}]&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 传世之器-传世之器改装提升

  * **命令字** **_heirloom_modification_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 123 | 1 | 传世之器的id  
key1 | 解锁所需资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key2 | target_star | int32 | 123 | 1 | 目标改装阶段  
key3 | target_stage | int32 | 123 | 1 | 目标改装等级  
key4 | target_level | int32 | 123 | 1 | 目标改装进度  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_modification_upgrade&key0=123&key1=[{“a”:[1,0,1000]}]&key2=123&key3=123&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 传世之器-传世之器改装图纸碎片转化

  * **命令字** **_heirloom_modification_piece_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 通用改装图纸碎片id | TINT64 | 121 | 1 |   
key1 | 通用改装图纸碎片数量 | TINT64 | 21 | 1 |   
key2 | 目标专属改装图纸碎片id | TINT64 | 122 | 1 |   
key3 | 目标专属改装图纸碎片数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_modification_piece_exchange&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 传世之器-传世之器万能碎片转化为改装图纸碎片

  * **命令字** **_heirloom_modification_piece_exchange_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 万能传世之器碎片id | TINT64 | 121 | 1 |   
key1 | 万能传世之器碎片数量 | TINT64 | 21 | 1 |   
key2 | 目标专属改装图纸碎片id | TINT64 | 122 | 1 |   
key3 | 目标专属改装图纸碎片数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=heirloom_modification_piece_exchange_new&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

### 7.16.佣兵荣耀

* * *

#### 佣兵荣耀-求助

  * **命令字** **_mercenary_glory_personal_monster_request_help_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | abcd | 1 | 活动id  
key1 | event_type | int32 | 123 | 1 | 活动类型  
key2 | target_pos | int32 | 1000200 | 1 | 目标地块  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mercenary_glory_personal_monster_request_help&key0=abcd&key1=123&key2=1000200

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-帮助盟友rally个人怪

  * **命令字** **_mercenary_glory_personal_monster_help_rally_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | cost_time | int32 | 30 | 1 |   
Key1 | target_pos | int32 | 1310072 | 1 |   
Key2 | troop_list | string | “1:4000:233:4000” | 1 | :分隔,位数代表兵种ID  
Key3 | is_sheriff_join | bool | 1 | 1 |   
Key4 | hero_list | string | “1,3,3,5” | 1 | ,分隔  
Key5 | building_type | int32 | 1 | 1 |   
Key6 | prepare_time | int32 | 20 | 1 |   
Key7 | quick_send | int32 | 1 | 0 | 含义为是否在满员时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mercenary_glory_personal_monster_help_rally&Key0=30&Key1=1310072&Key2=“1:4000:233:4000”&Key3=1&Key4=“1,3,3,5”&Key5=1&Key6=20&Key7=1&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-检查卡片是否有效

  * **命令字** **_mercenary_glory_check_monster_valid_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | target_pos | int32 | 1000200 | 1 | 目标位置  
Key1 | target_type | int32 | 123 | 1 | 目标类型  
Key2 | target_ctime | int64 | 150000000 | 1 | 目标地块的创建时间  
Key3 | req_time | int64 | 150000000 | 1 | 求助发起时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mercenary_glory_check_monster_valid&Key0=1000200&Key1=123&Key2=150000000&Key3=150000000

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-拉取盟友挑战进度

  * **命令字** **_get_mercenary_glory_al_progress_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | aid | int64 | 12345678 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_mercenary_glory_al_progress&Key0=abcd&Key1=12345678

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-刷个人怪

  * **命令字** **_op_mercenary_glory_summon_personal_monster_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | abcd | 1 | 活动id  
key1 | event_type | int32 | 123 | 1 | 活动类型  
key2 | event_pid | string | abcd | 1 | 活动pid  
key3 | event_etime | int64 | 150000000 | 活动关闭时间戳 |   
key4 | difficult | int32 | 123 | 1 | 玩家所选难度  
key5 | target_lv | int32 | 123 | 1 | 要刷的怪物等级  
key6 | help_times | int32 | 123 | 1 | 剩余的求助机会  
key7 | num_pid | string | abcd | 1 | 数值pid  
key8 | reward | json格式的string | [{“a”:[int,int,int]}] | 1 | 奖励展示  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_summon_personal_monster&key0=abcd&key1=123&key2=abcd&key3=150000000&key4=123&key5=123&key6=123&key7=abcd&key8=[{“a”:[int,int,int]}]

  * 命令字反包格式


    
    
        "svr_mercenary_glory_summon_result":
        {
            "wild_type": int,
            "pos": int,
            "sid": int,
            "expire_time": int64,
            "max_hp": int64, // 个人怪会是0
            "ctime": int64,
        }

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-刷联盟怪

  * **命令字** **_op_mercenary_glory_summon_alliance_monster_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | abcd | 1 | 活动id  
key1 | event_type | int32 | 123 | 1 | 活动类型  
key2 | event_pid | string | abcd | 1 | 活动pid  
key3 | event_etime | int64 | 150000000 | 活动关闭时间戳 |   
key4 | target_lv | int32 | 123 | 1 | 要刷的怪物等级  
key5 | aid | int64 | 123 | 1 | 怪所属的联盟  
key6 | pos_when_click | int32 | 1230789 | 1 | 点击预约时玩家主城所在位置  
key7 | num_pid | string | abcd | 1 | 数值pid  
key8 | reward | json格式的string | [{“a”:[int,int,int]}] | 1 | 奖励展示  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_summon_alliance_monster&key0=abcd&key1=123&key2=abcd&key3=150000000&key4=123&key5=123&key6=1230789&key7=abcd&key8=[{“a”:[int,int,int]}]

  * 命令字反包格式


    
    
        "svr_mercenary_glory_summon_result":
        {
            "wild_type": int,
            "pos": int,
            "sid": int,
            "expire_time": int64,
            "max_hp": int64, // 个人怪会是0
            "ctime": int64,
        }

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-更新玩家剩余求助机会

  * **命令字** **_op_mercenary_glory_refresh_help_times_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | abcd | 1 | 活动id  
key1 | event_type | int32 | 123 | 1 | 活动类型  
key2 | event_pid | string | abcd | 1 | 活动pid  
key3 | target_pos | int32 | 1000200 | 1 | 目标位置  
key4 | help_times | int32 | 123 | 1 | 剩余的求助机会  
key5 | updt_seq | int64 | 12345678 | 1 | 更新的seq,后台只保留值更大的那一次请求的数据  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_refresh_help_times&key0=abcd&key1=123&key2=abcd&key3=1000200&key4=123&key5=12345678

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-更新挑战进度-击杀&求助

  * **命令字** **_op_mercenary_glory_update_personal_progress_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | aid | int64 | 12345678 | 1 |   
Key2 | uid | int64 | 12345678 | 1 |   
Key3 | diff | int32 | 1234 | 1 | 难度  
Key4 | lv | int32 | 1234 | 1 | 等级  
Key5 | help | int32 | 1234 | 1 | 是否发起求助  
Key6 | pos | int32 | 1230789 | 1 | 地块位置  
Key7 | type | int32 | 1234 | 1 | 地块类型  
Key8 | ctime | int64 | 12345678 | 1 | 地块ctime  
Key9 | etime | int64 | 12345678 | 1 | 地块etime  
Key10 | event_etime | int64 | 150000000 | 活动关闭时间戳 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_update_personal_progress&Key0=abcd&Key1=12345678&Key2=12345678&Key3=1234&Key4=1234&Key5=1234&Key6=1230789&Key7=1234&Key8=12345678&Key9=12345678&Key10=150000000

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-发送联盟怪击杀奖abs

  * **命令字** **_op_mercenary_glory_send_al_monster_kill_reward_abs_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | sid | int64 | 12345678 | 1 |   
Key2 | aid | int64 | 12345678 | 1 |   
Key3 | pos | int32 | 1234 | 1 | 地块位置  
Key4 | lv | int32 | 1234 | 1 | 地块等级  
Key5 | wild_type | int32 | 1234 | 1 | 地块类型  
Key6 | lost_hp | int64 | 12345678 | 1 | 总掉血  
Key7 | max_hp | int64 | 12345678 | 1 | 总血量  
Key8 | participate_num | int32 | 1234 | 1 | 参与人数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_send_al_monster_kill_reward_abs&Key0=abcd&Key1=12345678&Key2=12345678&Key3=1234&Key4=1234&Key5=1234&Key6=12345678&Key7=12345678&Key8=1234

  * 命令字反包格式


    
    
        "svr_mercenary_glory_send_al_monster_kill_reward_abs":
        {
            "mail_id": int64,
        }

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
v6.8 | 已废弃  
  
* * *

#### 佣兵荣耀-发送联盟怪击杀奖-个人

  * **命令字** **_op_mercenary_glory_send_al_monster_kill_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | mail_id | int64 | 12345678 | 1 |   
key2 | reward | json格式的string | [{“a”:[int,int,int]}] | 1 | 给该玩家的奖励  
Key3 | wild_type | int32 | 1234 | 1 | 联盟怪地块类型  
Key4 | wild_level | int32 | 1234 | 1 | 联盟怪等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_send_al_monster_kill_reward&Key0=abcd&Key1=12345678&key2=[{“a”:[int,int,int]}]&Key3=1234&Key4=1234

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-发送联盟怪预约召唤邮件

  * **命令字** **_op_mercenary_glory_send_al_monster_appointment_mail_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | event_type | int32 | 123 | 1 |   
Key2 | appoint_time | int64 | 150000000 | 预约时间戳 |   
Key3 | aid | int64 | 12345678 | 1 |   
Key4 | target_lv | int32 | 123 | 1 | 要刷的怪物等级  
Key5 | num_pid | string | abcd | 1 | 数值pid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_send_al_monster_appointment_mail&Key0=abcd&Key1=123&Key2=150000000&Key3=12345678&Key4=123&Key5=abcd

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
v6.8 | 已废弃  
  
* * *

#### 佣兵荣耀-发送联盟怪击杀失败邮件

  * **命令字** **_op_mercenary_glory_send_al_monster_expire_mail_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | sid | int64 | 12345678 | 1 |   
Key2 | aid | int64 | 12345678 | 1 |   
Key3 | pos | int32 | 1234 | 1 | 地块位置  
Key4 | lv | int32 | 1234 | 1 | 地块等级  
Key5 | wild_type | int32 | 1234 | 1 | 地块类型  
Key6 | lost_hp | int64 | 12345678 | 1 | 总掉血  
Key7 | max_hp | int64 | 12345678 | 1 | 总血量  
Key8 | disappear_time | int64 | 12345678 | 1 | 地块消失时间  
Key9 | last_time | int64 | 12345678 | 1 | 地块存在时长  
Key10 | uid_list | string | 1234:1235:1236 | 1 | 参与人列表,冒号分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_send_al_monster_expire_mail&Key0=abcd&Key1=12345678&Key2=12345678&Key3=1234&Key4=1234&Key5=1234&Key6=12345678&Key7=12345678&Key8=12345678&Key9=12345678&Key10=1234:1235:1236

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 佣兵荣耀-发送联盟怪击杀奖

  * **命令字** **_op_mercenary_glory_send_kill_alliance_m_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | abcd | 1 | 活动id  
Key1 | sid | int64 | 12345678 | 1 |   
Key2 | aid | int64 | 12345678 | 1 |   
Key3 | pos | int32 | 1234 | 1 | 地块位置  
Key4 | lv | int32 | 1234 | 1 | 地块等级  
Key5 | wild_type | int32 | 1234 | 1 | 地块类型  
Key6 | lost_hp | int64 | 12345678 | 1 | 总掉血  
Key7 | max_hp | int64 | 12345678 | 1 | 总血量  
Key8 | user_list | json格式的string | {“uid”:damage} | 1 | 参与人列表  
Key9 | reward | json格式的string | [{“a”:[int,int,int]}] | 1 | 奖励  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mercenary_glory_send_kill_alliance_m_reward&Key0=abcd&Key1=12345678&Key2=12345678&Key3=1234&Key4=1234&Key5=1234&Key6=12345678&Key7=12345678&Key8={“uid”:damage}&Key9=[{“a”:[int,int,int]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

### 7.17.充值活动

* * *

#### 充值活动-领取目标奖励

  * **命令字** **_claim_novice_recharge_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | score | int64 | 1231 | 1 | 目标分数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_novice_recharge_reward&key0=1231

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

#### 充值活动-发送活动完成弹窗

  * **命令字** **_op_send_event_goals_achieved_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 111 | 1 |   
Key1 | event_type | int64 | 1 | 1 |   
Key2 | event_id | string | 1212_121 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_send_event_goals_achieved&key0=111&Key1=1&Key2=1212_121

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

### 7.18.兑换商城

* * *

#### 兑换商城-兑换商城列表

  * **命令字** **_exchangeshop_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=exchangeshop_list

  * **备注**



> rsp_type: exchamgeshop_json rsp_table: exchangeshop_list

  * **改动历史**

版本号 | 说明  
---|---  
v2.4.1 | 新增接口  
  
* * *

#### 兑换商城-兑换商城购买

  * **命令字** **_exchangeshop_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | shop_id | string | 1 | 1 | 商店id  
key1 | goods_id | string | 1 | 1 | 商品id  
key2 | amount | int32 | 1 | 1 | 购买数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=exchangeshop_buy&key0=1&key1=1&key2=1

  * **备注**



> rsp_type: user_json

  * **改动历史**

版本号 | 说明  
---|---  
v2.4.1 | 新增接口  
  
* * *

### 7.19.兑换商店

* * *

#### 兑换商店-兑换商店购买

  * **命令字** **_store_buy_item_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | store_id | int32 | 1 | 1 |   
key1 | slot_id | int32 | 1 | 1 |   
key2 | buy_type | int32 | 1 | 1 | 0-固定商品 1-随机商品  
key3 | buy_num | int32 | 1 | 1 |   
key4 | cost_type | int32 | 1 | 1 |   
key5 | cost_id | int32 | 1 | 1 |   
key6 | cost_num | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=store_buy_item&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1&key6=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 兑换商店-刷新兑换商店

  * **命令字** **_refresh_store_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | store_id | int32 | 1 | 1 |   
key1 | item_id | int32 | 1 | 1 |   
key2 | item_num | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=refresh_store&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

### 7.20.其他

* * *

#### 其他-客户端事件上报

  * **命令字** **_client_event_report_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=client_event_report&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 其他-举报玩家不当言论

  * **命令字** **_report_improper_msg_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 1 | 1 | 被举报玩家的uid  
key1 | uname | string | xdfsf | 1 | 被举报玩家的名字  
key2 | avatar_id | int64 | 1 | 1 | avatar_id  
key3 | type | int32 | 1 | 1 | 举报类型 1:垃圾信息 2:不当行为 3:骚扰 4:违反准则  
key4 | content | string | dfgdfg | 1 | 举报内容  
key5 | extra_info | string | dfdgf | 1 | westgame v2.7 客户端自行定义  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_improper_msg&key0=1&key1=xdfsf&key2=1&key3=1&key4=dfgdfg&key5=dfdgf

  * **改动历史** s |版本号|说明| |–|–| |v2.2.2|新增接口|



* * *

#### 其他-运营log(直接返回,无cmd执行)

  * **命令字** **_operate_log_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | (后台不用客户端使用) | string | ert | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_log&key0=ert

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.100 | 新增接口  
  
* * *

#### 其他-获取指定坐标附近空地，npc进攻者

  * **命令字** **_get_npc_attacker_pos_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_npc_attacker_pos

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 其他-获取指定坐标附近空地，hive

  * **命令字** **_get_hive_empty_pos_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_hive_empty_pos

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 其他-购买折扣商品

  * **命令字** **_item_buy_discount_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | gem_cost | int64 | 1 | 1 | 折扣后的总价  
key1 | item_id | int32 | 1 | 1 | 返包中给的条目id  
key2 | buy_num | int32 | 1 | 1 | 购买条目数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_buy_discount&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.5.2 | 新增接口  
  
* * *

#### 其他-使用无action buff道具(不需要结算的buff, 目前仅用于第二队列, 旧buff保持原接口不变)

  * **命令字** **_use_no_action_buff_item_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
key1 | gem_cost | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=use_no_action_buff_item&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 其他-获取联盟自己rank

  * **命令字** **_get_self_alliance_rank_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_self_alliance_rank

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 其他-召唤活动rally怪

  * **命令字** **_summon_wild_army_rally_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
key1 | wild_id | int32 | 1 | 1 |   
key2 | wild_lv | int32 | 1 | 1 |   
key3 | city_pos | int64 | 1250157 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=summon_wild_army_rally&key0=1&key1=1&key2=1&key3=1250157

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

#### 其他-征战成就领取task奖励

  * **命令字** **_lost_achievement_event_claim_task_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 154_165 | 1 | str  
key1 | task_id | int64 | 1 | 1 | int  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lost_achievement_event_claim_task_reward&key0=154_165&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.8 | 新增接口  
  
* * *

#### 其他-拉取资源

  * **命令字** **_lost_al_building_occupy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | int64 | 657 | 1 |   
key1 | target pos | int64 | 2500600 | 1 |   
key3 | troop list | string | 0:1:0:2 | 1 | (以:分割)  
key4 | general | int32 | 1 | 1 | 是否带将领  
key5 | occupy num | int64 | 111 | 1 | 客户端计算的采集量，后台并没有用到  
key6 | card list | string | 1,2,3 | 1 | 骑士列表，传卡牌后台id(,分割)  
key7 | stage | int32 | 1 | 1 | 时代  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lost_al_building_occupy&key0=657&key1=2500600&key3=0:1:0:2&key4=1&key5=111&key6=1,2,3&key7=1

  * **备注**



> rsp type: user json

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 其他-切换仓库保护开关

  * **命令字** **_change_warehouse_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | switch | int64 | 1 | 1 | 0：开 1：关  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_warehouse_switch&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.5 | 新增接口  
  
* * *

#### 其他-客户端弹窗上报手机号绑定弹窗

  * **命令字** **_candlestick_window_show_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=candlestick_window_show

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 其他-设置未成年验证信息

  * **命令字** **_set_age_verify_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | age_data | int64 | 1 | 1 | 1：未成年 2：成年 3:未成年(平台数据) 4:成年(平台数据)  
key1 | install_id | str | 1 | 1 | 1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_age_verify_info&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.21.军团战

* * *

#### 军团战-解散军团

  * **命令字** **_disband_al_legion_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | Lid | int32 | legion id | 1 | legion id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=disband_al_legion&key0=legion id

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-操作团长

  * **命令字** **_al_legion_commander_manage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion id | int32 | 123 | 1 |   
key1 | type | int32 | 1 | 1 | 操作, 1: 任命, 2: 卸任  
key2 | commander uid | int64 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_commander_manage&key0=123&key1=1&key2=12

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-管理军团成员

  * **命令字** **_al_legion_member_manage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion id | int32 | 123 | 1 |   
key1 | type | int32 | 1 | 1 | 操作, 1: 出战, 2: 撤销  
key2 | member uid | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_member_manage&key0=123&key1=1&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-军团改名

  * **命令字** **_al_legion_change_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion id | int32 | 123 | 1 |   
key1 | name | string | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_change_name&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-军团战报名

  * **命令字** **_enroll_al_legion_to_event_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion id | int32 | 123 | 1 |   
key1 | event_id | int32 | 123 | 1 | //(forecast time)  
key2 | dwScheduleId | int32 | 123 | 1 | 排期id, 取自活动  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=enroll_al_legion_to_event&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-军团战领奖

  * **命令字** **_confirm_al_legion_war_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=confirm_al_legion_war_result

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-op设置匹配失败 //客户端不会调用

  * **命令字** **_op_set_al_legion_war_match_fail_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 234 | 1 |   
key1 | legion id | int32 | 123 | 1 |   
key2 | event_id | int64 | 123 | 1 |   
key3 | strReward | string | [1,2,3] | 1 | 奖励, 通用奖励json格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_al_legion_war_match_fail&key0=234&key1=123&key2=123&key3=[1,2,3]

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-op设置匹配成功

  * **命令字** **_op_set_al_legion_war_match_succ //客户端不会调用_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 234 | 1 |   
key1 | legion id | int32 | 123 | 1 |   
key2 | event_id | int64 | 123 | 1 |   
key3 | linfo | string | {“1//(int,aid)”:{“sid”:int, “al_nick”:str, “legion_name”:str, “legion_id”:int}, 2//(int,aid)”:{…}} | 1 | 双方军团信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_al_legion_war_match_succ //客户端不会调用&key0=234&key1=123&key2=123&key3={“1//(int,aid)”:{“sid”:int, “al_nick”:str, “legion_name”:str, “legion_id”:int}, 2//(int,aid)”:{…}}

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-op设置军团战战果 //客户端不会调用

  * **命令字** **_op_set_al_legion_war_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 234 | 1 |   
key1 | legion id | int32 | 123 | 1 |   
key2 | event_id | int64 | 123 | 1 |   
key3 | result | string | 123 | 1 | 战果, json格式, 和xml里面的内容对应…  
key4 | reward | string | 123 | 1 | 奖励, 通用奖励json格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_al_legion_war_result&key0=234&key1=123&key2=123&key3=123&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-op自动填充军团成员 //客户端不会调用

  * **命令字** **_op_set_auto_fill_legion_member_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_auto_fill_legion_member&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-拉取军团战战况

  * **命令字** **_get_legion_war_situation_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_legion_war_situation&key0=0

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-拉取军团战战场城市信息

  * **命令字** **_get_legion_city_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 0 | 1 |   
key1 | pos | int32 | 1230123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_legion_city_info&key0=0&key1=1230123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-op生成军团战战场初始化action //客户端不用

  * **命令字** **_op_gen_al_legion_battlefiled_action_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
sid | 战场id | int32 | 123 | 1 |   
key0 | 战场开启时间 | int64 | 123 | 1 |   
key1 | 战场关闭时间 | int64 | 123 | 1 |   
key2 | 红方aid | int32 | 123 | 1 |   
key3 | 红方军团id | int32 | 123 | 1 |   
key4 | 蓝方aid | int32 | 123 | 1 |   
key5 | 蓝方军团id | int32 | 123 | 1 |   
key6 | 红方军团troop force | int64 | 123 | 1 |   
key7 | 蓝方军团troop force | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_al_legion_battlefiled_action&sid=123&key0=123&key1=123&key2=123&key3=123&key4=123&key5=123&key6=123&key7=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战-一键委派旧军团成员

  * **命令字** **_al_legion_quick_assign_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion id | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_quick_assign&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 军团战-拉取联盟新军团战操作记录

  * **命令字** **_get_al_legion_op_record_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_al_legion_op_record_list&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 军团战-玩家旧军团请战操作

  * **命令字** **_al_legion_ask_fight_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | old legion id | int32 | 123 | 1 | key2为1时传0  
key1 | new legion id | int32 | 123 | 1 | 发出请战操作目标军团id  
key2 | type | int32 | 1 | 1 | 操作, 1-发出请战, 2-取消请战 3-修改请战  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_ask_fight&key0=123&key1=123&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 军团战-玩家旧军团不参与操作

  * **命令字** **_al_legion_no_fight_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | no fight legion id | int32 | 123 | 1 | 操作目标军团id  
key1 | type | int32 | 1 | 1 | 操作, 1-申请不参与, 2-取消不参与  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_no_fight&key0=123&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.22.军团战march

* * *

#### 军团战march-attack

  * **命令字** **_legion_city_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | int32 | 123 | 1 |   
key1 | target pos | int32 | 123 | 1 |   
key2 | troop list | string | 1:2:3 | 1 | :分隔  
key3 | if general join | bool | 0 | 1 |   
key4 | card_list | string | 1,2,3 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_attack&key0=123&key1=123&key2=1:2:3&key3=0&key4=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-rally_war

  * **命令字** **_legion_city_rally_war_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123 | 1 | 1:2:3  
key4 | if general join | bool | 0 | 1 |   
key5 | card_list | string | 1,2,3 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_rally_war&key0=123&key1=123&key2=123&key3=123&key4=0&key5=1,2,3&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-reinforce //支援普通队列

  * **命令字** **_legion_city_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_left | 当前可用槽位 | TINT64 | 20 | 1 | 1  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 1230123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_reinforce&rf_troop_num=900000&rf_slot_left=20&key0=123&key1=1230123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-dispatch //支援指挥官队列

  * **命令字** **_legion_city_dispatch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_left | 当前可用槽位 | TINT64 | 20 | 1 | 1  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_dispatch&rf_troop_num=900000&rf_slot_left=20&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-abandon

  * **命令字** **_legion_city_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_abandon&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-dismiss all

  * **命令字** **_legion_city_dismiss_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_dismiss_all&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-recall reinforce

  * **命令字** **_legion_city_recall_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_recall_reinforce&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-legion_city_reinforce_speedup

  * **命令字** **_legion_city_reinforce_speedup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | uint32 | 123 | 1 | (key2>0 时, 优先消耗宝石)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_reinforce_speedup&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-遣散

  * **命令字** **_legion_city_repatriate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | action id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_city_repatriate&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-拉取所有被完全占领的战场城市

  * **命令字** **_get_all_full_occupied_legion_city_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_all_full_occupied_legion_city&key0=123

  * **备注**



> rsp_type : throne json 进入军团战地图时主动拉一次 收到svr_all_full_occupied_legion_city_list_flag时主动拉一次

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-土匪boss相关战争attack

  * **命令字** **_legion_boss_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 0 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_boss_attack&key0=123&key1=123&key2=123&key3=0&key4=123

  * **备注**



> rsp_type: user_json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 军团战march-土匪城市相关战争attack

  * **命令字** **_legion_bandit_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=legion_bandit_attack&key0=123&key1=123&key2=123&key3=1&key4=123

  * **备注**



> rsp_type: user_json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

### 7.23.军队

* * *

#### 军队-训练军队

  * **命令字** **_troop_train_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop id | int32 | 1 | 1 |   
key1 | num | int32 | 111 | 1 | 训练数量  
key2 | cost time | int64 | 111 | 1 | 花费的时间  
key3 | exp | int32 | 11 | 1 | 获得的经验  
key5 | gem num | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=troop_train&key0=1&key1=111&key2=111&key3=11&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-治疗受伤军队

  * **命令字** **_troop_heal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop id | int64 | 1 | 1 |   
key1 | num | int64 | 111 | 1 | 治疗的数量  
key2 | cost time | int64 | 11 | 1 | 花费的时间  
key3 | exp | int64 | 11 | 1 | 获得的经验  
key5 | gem num | int64 | 11 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=troop_heal&key0=1&key1=111&key2=11&key3=11&key5=11

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-放弃受伤军队

  * **命令字** **_hospital_troop_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop id | int32 | 1 | 1 |   
kye1 | num | int64 | 111 | 1 | （要放弃的数量）  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=hospital_troop_abandon&key0=1&kye1=111

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-解散军队

  * **命令字** **_troop_dismiss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop_id | int8 | 1 | 1 |   
kye1 | num | int64 | 111 | 1 | （要解散的数量）  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=troop_dismiss&key0=1&kye1=111

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-取消训练troop

  * **命令字** **_troop_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=troop_cancel&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-取消治疗军队

  * **命令字** **_hos_cancel_troop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 11 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=hos_cancel_troop&key0=11

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-发起复活队列

  * **命令字** **_revive_troop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | revive_type | int32 | 1 | 1 | 复活类型 0普通，1立即  
key1 | revive_troop_detail | string | 1:0:2 | 1 | ”0:0:…”，参考march_action中的军队详情  
key2 | item_id | int32 | 1 | 1 | 复活道具id  
key3 | item_num | int32 | 1 | 1 | 复活道具数量  
key4 | cost_time | int64 | 1 | 1 | 复活耗时  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=revive_troop&key0=1&key1=1:0:2&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 军队-取消复活队列

  * **命令字** **_revive_troop_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | revive_action_index | int64 | 1 | 1 | 复活队列索引  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=revive_troop_cancel&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-解散伤亡军队

  * **命令字** **_dismiss_dead_troop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop_id | int64 | 1 | 1 | 部队id  
key1 | troop_num | int64 | 1 | 1 | 部队数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dismiss_dead_troop&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.6 | 新增接口  
  
* * *

#### 军队-同时代同兵种提升

  * **命令字** **_troop_promote_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop id | int32 | 1 | 1 | 提升兵种id  
key1 | troop num | int32 | 1 | 1 | 提升兵种数量  
key2 | cost time | int64 | 1 | 1 | 花费时间  
key3 | gem num | int64 | 1 | 1 | 花费宝石 立即完成传 不然传0  
key4 | target troop id | int32 | 1 | 1 | 原兵种id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=troop_promote_level&key0=1&key1=1&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.9 | 新增接口  
  
* * *

#### 军队-兵种晋升2.0

  * **命令字** **_troop_promote_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop id | int32 | 1 | 1 |   
key1 | troop num | int32 | 1 | 1 |   
key2 | target troop id | int32 | 1 | 1 |   
key3 | target troop num | int32 | 1 | 1 |   
key4 | time_cost | int64 | 1 | 1 |   
key5 | gem_num | int64 | 1 | 1 | 需要立即完成则传宝石数量, 否则传0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=troop_promote&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.7.8 | 新增接口  
  
* * *

#### 军队-重伤医院治疗

  * **命令字** **_serious_troop_heal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop_detail | json | {“1”:10} | 1 | {“id”:num}  
key1 | cost_time | int64 | 1 | 1 | 耗时  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=serious_troop_heal&key0={“1”:10}&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.5 | 新增接口  
  
* * *

#### 军队-解散重伤军队

  * **命令字** **_dismiss_serious_troop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop_id | int64 | 1 | 1 | 部队id  
key1 | troop_num | int64 | 1 | 1 | 部队数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dismiss_serious_troop&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.5 | 新增接口  
  
* * *

#### 军队-加速重伤军队治疗/补充治疗点

  * **命令字** **_speedup_serious_troop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int64 | 1 | 1 | 使用的道具id  
key1 | item num | int64 | 1 | 1 | 使用的道具数量  
key2 | action id | int64 | 1 | 1 | 治疗队列action id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=speedup_serious_troop&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.5 | 新增接口  
  
* * *

#### 军队-取消重伤医院治疗

  * **命令字** **_serious_troop_heal_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=serious_troop_heal_cancel&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.5 | 新增接口  
  
* * *

#### 军队-募兵

  * **命令字** **_revive_immediate_by_loyalty_point_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | troop_detail | json | {“1”:10} | 1 | {“id”:num}  
key1 | cost_loyalty | int64 | 1 | 1 | 忠诚点  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=revive_immediate_by_loyalty_point&key0={“1”:10}&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.5 | 新增接口  
  
* * *

### 7.24.军队预设

* * *

#### 军队预设-预设改名

  * **命令字** **_set_army_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | plan_name | string | dsrfds | 1 | 预设名  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_army_plan_name&key0=1&key1=dsrfds

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

#### 军队预设-修改预设

  * **命令字** **_set_army_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | cowboy_list | string | 1,2,3 | 1 | cowboy_id1,cowboy_id2…  
key2 | troop_list | string | 1:2:3 | 1 | troop_rate1:troop_rate2…rate为整数,分母默认10000  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_army_plan&key0=1&key1=1,2,3&key2=1:2:3

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

#### 军队预设-重置预设

  * **命令字** **_reset_army_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_army_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8.0 | 新增接口  
  
* * *

### 7.25.决斗

* * *

#### 决斗-切换模式

  * **命令字** **_shoot_mode_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mode | int32 | 1 | 1 | 需要切换的mode，跟现在mode相同时将不做处理  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shoot_mode_switch&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 决斗-射击(击杀对手或者切换模式时，客户端必须给后台发请求，并等待后台处理成功)

  * **命令字** **_shoot_cowboy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | curr_seq | int64 | 1 | 1 | 当前决斗的序号，从svr_shooting_gallary获得  
key1 | new_process | int32 | 111 | 1 | 对方当前的血量  
key2 | new_shoot_count | int32 | 11 | 1 | 发请求时已射击次数，可以理解为当前奖励已领取个数  
key3 | shoot_time | int64 | 1111 | 1 | 射击的时间，要保证跟后台时间一致  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shoot_cowboy&key0=1&key1=111&key2=11&key3=1111

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 决斗-领取福袋

  * **命令字** **_collect_shoot_lucky_bag_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=collect_shoot_lucky_bag

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

### 7.26.刹马镇

* * *

#### 刹马镇-//开启刹马镇活动

  * **命令字** **_start_shama_battlefield_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | int64 | 123 | 1 |   
key1 | 小队id | int64 | 123 | 1 |   
key2 | 难度 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=start_shama_battlefield&key0=123&key1=123&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇-创建小队

  * **命令字** **_al_shama_team_create_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | difficulty | int32 | 1 | 1 |   
key1 | event_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_shama_team_create&key0=1&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇-解散小队

  * **命令字** **_al_shama_team_disband_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | team_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_shama_team_disband&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇-踢出成员

  * **命令字** **_kick_al_team_member_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | team_id | int64 | 123 | 1 |   
key1 | uid | int64 | 123 | 1 | 被踢者的uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=kick_al_team_member&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇-加入小队

  * **命令字** **_al_shama_team_join_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | team_id | int64 | xxxxxx | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_shama_team_join&key0=xxxxxx

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇-退出小队

  * **命令字** **_al_shama_team_leave_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_shama_team_leave

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇-战场结算 //客户端不会调用

  * **命令字** **_op_set_shama_battle_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 123 | 1 |   
key1 | team_id | int64 | 123 | 1 |   
key2 | result | string | xxxxxx | 1 | string{“result”: int, “difficulty”: int, “last_hit_hp”: int, “occupier_name”:string, “pass_time”: long}  
key3 | reward | string | xxxxxx | 1 | 通用reward json  
key10 | result | 0,1 | 1 | 0 | 后台自用-输赢结果  
key11 | difficulty | 22 | 1 | 0 | 后台自用-难度  
key12 | leader_uid | uid | 1 | 0 | 后台自用-leader_uid  
key13 | exit_uid_list | uid,uid | 1 | 0 | 后台自用-退出的uid列表  
key14 | join_uid_list | uid,uid | 1 | 0 | 后台自用-加入的uid列表  
key15 | no_join_uid_list | uid,uid | 1 | 0 | 后台自用-未加入的uid列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_shama_battle_result&key0=123&key1=123&key2=xxxxxx&key3=xxxxxx&key10=1&key11=1&key12=1&key13=1&key14=1&key15=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

### 7.27.刹马镇map

* * *

#### 刹马镇map-拉取全量地图数据

  * **命令字** **_map_get_shama_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_get_shama&key0=123

  * **备注**



> rsp_type: map

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

### 7.28.刹马镇march

* * *

#### 刹马镇march-attack

  * **命令字** **_shama_tower_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_attack&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-rally_war

  * **命令字** **_shama_tower_rally_war_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123:123 | 1 |   
key4 | if general join | uint32 | 123 | 1 |   
key5 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_rally_war&key0=123&key1=123&key2=123&key3=123:123&key4=123&key5=123&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-reinforce //支援普通队列

  * **命令字** **_shama_tower_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_num | 当前已用槽位 | TINT64 | 20 | 1 | 1  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 1230123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_reinforce&rf_troop_num=900000&rf_slot_num=20&key0=123&key1=1230123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-dispatch //支援指挥官队列

  * **命令字** **_shama_tower_dispatch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_num | 当前已用槽位 | TINT64 | 20 | 1 | 1  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_dispatch&rf_troop_num=900000&rf_slot_num=20&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-dismiss all

  * **命令字** **_shama_tower_dismiss_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_dismiss_all&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-recall reinforce

  * **命令字** **_shama_tower_recall_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_recall_reinforce&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-speedup

  * **命令字** **_shama_tower_reinforce_speedup //(仅用于防守方)_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | string | 123 | 1 | (key2>0 时, 优先消耗宝石)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_reinforce_speedup //(仅用于防守方)&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 刹马镇march-//遣散

  * **命令字** **_shama_tower_repatriate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | action id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=shama_tower_repatriate&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

### 7.29.副官

* * *

#### 副官-副官招募

  * **命令字** **_deputy_recruit_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官id | TINT64 | 1021 | 1 |   
key1 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_recruit&key0=1021&key1=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官升职

  * **命令字** **_deputy_upgrade_star_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官id | TINT64 | 1021 | 1 |   
key1 | 目标职级 | TINT64 | 2 | 1 |   
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_upgrade_star&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官升阶

  * **命令字** **_deputy_upgrade_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官id | TINT64 | 1021 | 1 |   
key1 | 目标阶级 | TINT64 | 2 | 1 |   
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_upgrade_stage&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-通用碎片兑换

  * **命令字** **_deputy_universal_piece_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 万能副官碎片id | TINT64 | 121 | 1 |   
key1 | 万能副官碎片数量 | TINT64 | 21 | 1 |   
key2 | 目标副官碎片id | TINT64 | 122 | 1 |   
key3 | 目标副官碎片数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_universal_piece_exchange&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官额外buff培养

  * **命令字** **_deputy_develop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官id | TINT64 | 1021 | 1 |   
key1 | 培养方式 | TINT64 | type | 0-低级培养,1-高级培养 |   
key2 | 培养消耗 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key3 | 是否是重新培养 | TINT64 | re_develop | 0-正常,1-重新培养 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_develop&key0=1021&key1=type&key2=[{“a”:[1,0,1000]}]&key3=re_develop

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官额外buff培养确认

  * **命令字** **_deputy_develop_confirm_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官id | TINT64 | 1021 | 1 |   
key1 | 保留培养还是放弃 | TINT64 | type | 0-保留,1-放弃 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_develop_confirm&key0=1021&key1=type

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官任命&替换

  * **命令字** **_deputy_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 任命槽位 | TINT64 | 2 | 1 |   
key1 | 副官id | TINT64 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_put_on&key0=2&key1=1021

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官替换

  * **命令字** **_deputy_replace_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官id | TINT64 | 1021 | 1 |   
key1 | 被替换副官id | TINT64 | 1022 | 1 |   
key2 | 任命槽位 | TINT64 | 2 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_replace&key0=1021&key1=1022&key2=2

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官卸任

  * **命令字** **_deputy_put_off_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备槽位 | TINT64 | 2 | 1 |   
key1 | 副官id | TINT64 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=deputy_put_off&key0=2&key1=1021

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-副官阵容设置

  * **命令字** **_set_deputy_slot_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 副官阵容列表 | string | 将所有deputy_id用,隔开，槽位对应为1,2,3,4,5 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_deputy_slot&key0=将所有deputy_id用,隔开，槽位对应为1,2,3,4,5

  * 改动历史

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-槽位职位技能使用

  * **命令字** **_slot_skill_active_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 要使用技能的槽位 | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=slot_skill_active&key0=1

  * 改动历史

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 副官-领取副官日志奖励

  * **命令字** **_claim_deputy_log_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 日志id | TINT64 | 1 | 1 |   
key1 | 日志等级 | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_deputy_log_reward&key0=1&key1=1

  * 改动历史

版本号 | 说明  
---|---  
v7.2.7 | 新增接口  
  
* * *

### 7.30.勋章

* * *

#### 勋章-勋章装配

  * **命令字** **_medal_new_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装配槽位 | int32 | 1 | 1 |   
key1 | 勋章id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_new_put_on&key0=1&key1=1

  * 改动历史

版本号 | 说明  
---|---  
v4.0 | 新增接口  
  
* * *

#### 勋章-勋章卸下

  * **命令字** **_medal_new_put_off_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装配槽位 | int32 | 1 | 1 |   
key1 | 勋章id | int32 | 1 | 1 |   
key2 | 替换消耗 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_new_put_off&key0=1&key1=1&key2=[{“a”:[1,0,1000]}]

  * 改动历史

版本号 | 说明  
---|---  
v4.0 | 新增接口  
  
* * *

#### 勋章-勋章替换

  * **命令字** **_medal_new_replace_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 要替换的槽位 | int32 | 1 | 1 |   
key1 | 被替换的勋章id | int32 | 1 | 1 |   
key2 | 要替换的勋章id | int32 | 1 | 1 |   
key3 | 替换消耗 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_new_replace&key0=1&key1=1&key2=1&key3=[{“a”:[1,0,1000]}]

  * 改动历史

版本号 | 说明  
---|---  
v4.0 | 新增接口  
  
* * *

#### 勋章-勋章升级

  * **命令字** **_medal_new_upgrade_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 勋章id | int32 | 1 | 1 |   
key1 | 目标等级 | int32 | 1 | 1 |   
key2 | 勋章碎片id | int32 | 1 | 1 |   
key3 | 勋章碎片数量 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_new_upgrade_level&key0=1&key1=1&key2=1&key3=1

  * 改动历史

版本号 | 说明  
---|---  
v4.0 | 新增接口  
  
* * *

#### 勋章-勋章升品

  * **命令字** **_medal_new_upgrade_quality_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 勋章id | int32 | 1 | 1 |   
key1 | 目标品质等级 | int32 | 1 | 1 |   
key2 | 消耗宝石数量 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_new_upgrade_quality&key0=1&key1=1&key2=[{“a”:[1,0,1000]}]

  * 改动历史

版本号 | 说明  
---|---  
v4.0 | 新增接口  
  
* * *

#### 勋章-词条重铸

  * **命令字** **_medal_new_affix_recast_quality_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 勋章id | int32 | 1 | 1 |   
key1 | 要重铸勋章id词 | int32 | 1 | 1 |   
key2 | 勋章碎片id | int32 | 1 | 1 |   
key3 | 勋章碎片数量 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_new_affix_recast_quality&key0=1&key1=1&key2=1&key3=1

  * 改动历史

版本号 | 说明  
---|---  
v4.0 | 新增接口  
  
* * *

#### 勋章-提升勋章等级

  * **命令字** **_medal_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int64 | 1 | 1 | 勋章id  
key1 | target_level | int64 | 1 | 1 | 目标等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=medal_upgrade&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

### 7.31.勋章预设

* * *

#### 勋章预设-勋章预设改名

  * **命令字** **_set_medal_new_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | plan_name | string | dsrfds | 1 | 预设名  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_medal_new_plan_name&key0=1&key1=dsrfds

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 勋章预设-修改勋章预设

  * **命令字** **_set_medal_new_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | medal_new_id | int32 | 1 | 1 |   
key2 | dwPos | int32 | 1 | 1 |   
key3 | dwType | int32 | 1 | 1 | 1-装备 2-卸下  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_medal_new_plan&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 勋章预设-重置勋章预设

  * **命令字** **_reset_medal_new_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_medal_new_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 勋章预设-使用勋章预设

  * **命令字** **_change_medal_new_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | 替换消耗 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_medal_new_plan&key0=1&key1=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

### 7.32.博客

* * *

#### 博客-领取博客奖励

  * **命令字** **_claim_bulletin_board_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | bulletin_board id | int | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_bulletin_board_reward&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

### 7.33.周年庆活动

* * *

#### 周年庆活动-制作蛋糕活动领奖

  * **命令字** **_anniversary_cake_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 15415_51 | 1 | 活动id  
key1 | level | int64 | 1 | 1 | 奖励等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=anniversary_cake_claim_reward&key0=15415_51&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

#### 周年庆活动-制作蛋糕活动意见领取奖励

  * **命令字** **_anniversary_cake_claim_reward_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 15415_51 | 1 | 活动id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=anniversary_cake_claim_reward_all&key0=15415_51

  * **改动历史**

版本号 | 说明  
---|---  
v6.7.0 | 新增接口  
  
* * *

#### 周年庆活动-增加蛋糕经验

  * **命令字** **_anniversary_cake_add_exp_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 12152_12 | 1 | 活动id  
key1 | type,id,num | string | 1,2,3 | 1 |   
key2 | exp | int64 | 1 | 1 | 本次增加的经验  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=anniversary_cake_add_exp&key0=12152_12&key1=1,2,3&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

#### 周年庆活动-解锁蛋糕档次奖励

  * **命令字** **_anniversary_cake_unlock_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 121_121 | 1 | 活动id  
key1 | type | int64 | 1 | 1 | 0:免费解锁 1: 宝石解锁  
key2 | num | int64 | 1 | 1 | 宝石数,宝石解锁时才需要  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=anniversary_cake_unlock_reward&key0=121_121&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

### 7.34.周月卡

* * *

#### 周月卡-月/周卡发奖

  * **命令字** **_op_mail_send_all_card_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mail_send_all_card_reward

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

### 7.35.回流活动

* * *

#### 回流活动-回流活动创建新账号

  * **命令字** **_backflow_create_new_account_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 1 | 1 | int  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=backflow_create_new_account&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.3.0 | 新增接口  
  
* * *

#### 回流活动-回流活动账号继承

  * **命令字** **_backflow_inherit_account_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int32 | 1 | 1 | int关联老号的uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=backflow_inherit_account&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.3.0 | 新增接口  
  
* * *

#### 回流活动-回流活动设置邮箱绑定标记

  * **命令字** **_backflow_set_mail_bind_flag_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int32 | 1 | 1 | int关联老号的uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=backflow_set_mail_bind_flag&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.3.0 | 新增接口  
  
* * *

### 7.36.土匪来袭

* * *

#### 土匪来袭-盟主开启土匪来袭活动

  * **命令字** **_start_bandit_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | difficulty | int32 | 1 | 1 |   
key1 | event_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=start_bandit_attack&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v5.4 | 新增参数key1  
  
* * *

### 7.37.土匪来袭march

* * *

#### 土匪来袭march-rally war土匪聚集地

  * **命令字** **_rally_attack_bandit_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123:123 | 1 |   
key4 | preparetime | uint32 | 123 | 1 |   
key5 | if general join | uint32 | 123 | 1 |   
key6 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_attack_bandit&key0=123&key1=123&key2=123&key3=123:123&key4=123&key5=123&key6=123&Key10=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.0 | 新增接口  
  
* * *

#### 土匪来袭march-支援土匪聚集地 rally war

  * **命令字** **_rally_reinforce_bandit_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123:123 | 1 |   
key4 | if general join | uint32 | 123 | 1 |   
key5 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_reinforce_bandit&key0=123&key1=123&key2=123&key3=123:123&key4=123&key5=123

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.0 | 新增接口  
  
* * *

### 7.38.城市守卫preset

* * *

#### 城市守卫preset-设置城防预设名称

  * **命令字** **_set_guard_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dwplanid | int32 | 123 | 1 |   
key1 | sznewname | string | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_guard_plan_name&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城市守卫preset-编辑城防预设

  * **命令字** **_set_guard_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dwplanid | int32 | 12 | 1 |   
key1 | cowboy_list | string | 1,2,3 | 1 | string, 格式：cowboy_id1,cowboy_id2…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_guard_plan&key0=12&key1=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城市守卫preset-使用城防预设

  * **命令字** **_change_guard_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dwplanid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_guard_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城市守卫preset-重置城防预设

  * **命令字** **_reset_guard_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dwplanid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_guard_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

### 7.39.城防

* * *

#### 城防-训练fort

  * **命令字** **_fort_train_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fort id | uint32 | 123 | 1 |   
key1 | fort num trained | uint32 | 123 | 1 |   
key2 | cost time | int64 | 123 | 1 |   
key3 | exp | int32 | 123 | 1 |   
key4 | need resource | int32 | 123 | 0 | 后台默认为1  
key5 | gem num | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fort_train&key0=123&key1=123&key2=123&key3=123&key4=123&key5=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城防-取消训练fort

  * **命令字** **_fort_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fort_cancel&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城防-解散城防

  * **命令字** **_fort_dismiss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fort id | uint8 | 1 | 1 |   
kye1 | num | uint32 | 23 | 1 | （要解散的数量）  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fort_dismiss&key0=1&kye1=23

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城防-放弃死亡的城防

  * **命令字** **_dead_fort_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fort id | int64 | 123 | 1 |   
kye1 | num | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dead_fort_abandon&key0=123&kye1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城防-治疗死亡的城防

  * **命令字** **_dead_fort_heal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | fort id | uint32 | 12 | 1 |   
key1 | num | uint32 | 12 | 1 |   
key2 | cost time | int64 | 123 | 1 |   
key3 | exp | uint32 | 12 | 1 |   
key4 | need resource | int32 | 1 | 0 | 后台默认为1  
key5 | gem num | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dead_fort_heal&key0=12&key1=12&key2=123&key3=12&key4=1&key5=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城防-取消正在治疗的城防

  * **命令字** **_fort_heal_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=fort_heal_cancel&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 城防-复活战损保护返回的兵损

  * **命令字** **_lost_troop_heal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lost_troop_heal

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

### 7.40.多日任务

* * *

#### 多日任务-领取任务奖励：

  * **命令字** **_continuous_activities_task_claim_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | task_id | string | 111 | 1 |   
key1 | event_id | string | 112 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=continuous_activities_task_claim&key0=111&key1=112

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 多日任务-领取宝箱

  * **命令字** **_continuous_activities_chest_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | num | int32 | 1 | 1 |   
key1 | event_id | string | 11 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=continuous_activities_chest_open&key0=1&key1=11

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

### 7.41.失落之地

* * *

#### 失落之地-拉取失落之地缩略图信息（固定建筑、关卡、盟友主城）

  * **命令字** **_get_lost_map_thumbnail_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_lost_map_thumbnail_info&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-失落之地建造联盟要塞/联盟旗帜/联盟资源中心

  * **命令字** **_lost_al_building_put_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | cost_time | int32 | 1 | 1 |   
Key1 | target_pos | int32 | 2550625 | 1 |   
Key2 | troop_list（’:’分隔） | string | 101:10212:1521 | 1 |   
Key3 | is_dragon_join | int32 | 1 | 1 |   
Key4 | cowboy_list（’,’分隔） | string | 101,102,103 | 1 |   
Key5 | building_id | int32 | 1 | 1 |   
Key6 | cost_al_resource(type1:id1:num1,type2:id2:num2…) | string | 1:1,100,1:2:200 | 1 |   
Key7 | stage | int32 | 1 | 1 | 时代,资源中心用 wg v3.8  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lost_al_building_put_up&Key0=1&Key1=2550625&Key2=101:10212:1521&Key3=1&Key4=101,102,103&Key5=1&Key6=1:1,100,1:2:200&Key7=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-失落之地修复联盟要塞/联盟旗帜

  * **命令字** **_lost_al_building_repair_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | pos | int32 | 2550625 | 1 |   
Key1 | building_id | int32 | 1 | 1 |   
Key2 | cost_type | int32 | 1 | 1 | 0:金块，1:联盟忠诚点(废弃)，2:联盟玛瑙矿  
Key3 | cost_num | int32 | 100 | 1 |   
Key4 | sid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lost_al_building_repair&Key0=2550625&Key1=1&Key2=1&Key3=100&Key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-失落之地拆除联盟要塞/联盟旗帜

  * **命令字** **_lost_al_building_remove_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | pos | int32 | 2550625 | 1 |   
Key1 | building_id | int32 | 1 | 1 |   
Key2 | sid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lost_al_building_remove&Key0=2550625&Key1=1&Key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-失落之地获取联盟占领建筑

  * **命令字** **_get_lost_building_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | aid | int64 | 1021 | 1 |   
Key1 | sid | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_lost_building_info&Key0=1021&Key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-失落之地获取联盟仓库数据

  * **命令字** **_get_lost_storehouse_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | aid | int64 | 10252 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_lost_storehouse_info&Key0=10252

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-拉取失落之地缩略图（联盟建筑）

  * **命令字** **_get_lost_al_building_thumbnail_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | aid | int64 | 1022 | 1 |   
Key1 | json | string | [121,122,123] | 1 | bid例如[xxxxx,xxxxx,xxxxx]  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_lost_al_building_thumbnail&Key0=1022&Key1=[121,122,123]

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-领取编年史任务奖励

  * **命令字** **_claim_chronicle_task_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | event_id | string | 102121_424412 | 1 |   
Key1 | task_id | string | 1121 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_chronicle_task_reward&Key0=102121_424412&Key1=1121

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 失落之地-卸任所有指挥官身份

  * **命令字** **_unassign_all_lost_building_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=unassign_all_lost_building

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

### 7.42.失落之地map

* * *

#### 失落之地map-拉取失落之地地块数据

  * **命令字** **_map_get_lost_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | sid | TINT32 | 1 | 1 |   
Key0 | str_bid | string | “12,123,123” | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_get_lost&Key0=1&Key0=“12,123,123”

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

### 7.43.套装

* * *

#### 套装-套装培养

  * **命令字** **_develop_suit_special_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | suit_id | int32 | 123 | 1 |   
key1 | 消耗 | string | [1,2,3] | 1 | [type,id,num]  
key2 | exp | int64 | 123 | 1 | 获得经验，包括暴击，后台不校验  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=develop_suit_special_buff&key0=123&key1=[1,2,3]&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v5.3 | 新增接口  
  
* * *

### 7.44.季卡

* * *

#### 季卡-领取奖励

  * **命令字** **_battle_pass_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 |   
key1 | level | int32 | 1 | 1 | type  
key2 | bp type | int32 | 0 | 1 |   
key4 | new_stage | int32 | 1 | 1 |   
key5 | event_id | string | 127_xxxx | 0 | 不传默认为0  
key6 | event_type | int64 | 1 | 1 | 活动类型  
key7 | extra | string | 1 | 1 | 扩展字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=battle_pass_claim_reward&key0=1&key1=1&key2=0&key4=1&key5=127_xxxx&key6=1&key7=1

  * **备注**



> key0 = 奖励类型 -1：领取全部等级奖励；0：基础等级奖励；1：精英等级奖励；2：月度资源宝箱奖励；3：每日经验奖励 4: 领取某个等级的奖励 key1 = level type = 0 || 1 || 4 时有效 key2 = 季卡类型 0:bp1 1:bp3 2:重构后bp1 4.bp5 5.bp6-登录型 6.bp7-对bp5的优化 7.bp8-大富翁bp key3 = 时代是运营配置值, 固需客户端透传字段, 以保持前后台一致 key4 = 时代 key5 = event_id key6 = event_type key7 = extra 客户端额外信息
    
    
    {
        "event_type": int      // V4.5  活动购买的活动type，非活动购买时填0
        "event_id": str      // V4.5  活动购买的活动string
        "event_info": {     // V4.5 活动购买信息
            // 不同活动的购买信息不同
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
v6.4.0 | 新增字段  
v7.1.4 | 新增季卡类型 大富翁bp  
  
* * *

#### 季卡-通用加分接口-走special流程

  * **命令字** **_op_score_type_add_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int64 | 1 | 1 | 活动类型  
key1 | event_id | string | 127_xxxx | 0 | 不传默认为0  
key2 | add_type | int64 | 1 | 1 | 1-uid 2-aid 3-sid  
key3 | target | int64 | 1 | 1 | 按照key2进行数据拉取  
key4 | extra | string | 1 | 1 | 加分字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_score_type_add_batch&key0=1&key1=127_xxxx&key2=1&key3=1&key4=1

  * **备注**



> key0 = 活动类型 目前只支持分服季卡 key1 = 活动id 有精准要求就传 无则传0 key2 = 加分目标类型 目前只支持uid key3 = 加分目标id key4 = 加分信息-以通用得分项为标准设计
    
    
    {
        "type_list" : [[type,id,lv,num]] // [[100008,道具id,-1,exp]]
    }

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

### 7.45.宝物

* * *

#### 宝物-使用宝物

  * **命令字** **_treasure_use_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int64 | 123456 | 1 | 后台id  
key1 | action_id | int64 | 123456 | 1 |   
key10 | num_id | int64 | 1 | 1 | 宝物数值id  
key11 | action_second_class | int64 | 1 | 1 | 要加速的action_second_class  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=treasure_use&key0=123456&key1=123456&key10=1&key11=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 宝物-宝物购买

  * **命令字** **_treasure_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | idx | int32 | 123456 | 1 |   
key1 | seq | int64 | 123456 | 1 | 轮次  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=treasure_buy&key0=123456&key1=123456

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 宝物-寻宝

  * **命令字** **_treasure_hunt_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=treasure_hunt

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 宝物-宠物宝物购买

  * **命令字** **_animal_treasure_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | idx | int32 | 123456 | 1 |   
key1 | seq | int64 | 123456 | 1 | 轮次  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=animal_treasure_buy&key0=123456&key1=123456

  * **改动历史**

版本号 | 说明  
---|---  
v5.7 | 新增接口  
  
* * *

#### 宝物-宠物寻宝

  * **命令字** **_animal_treasure_hunt_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=animal_treasure_hunt

  * **改动历史**

版本号 | 说明  
---|---  
v5.7 | 新增接口  
  
* * *

### 7.46.宠物

* * *

#### 宠物-宠物放生

  * **命令字** **_set_animal_status_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 宠物id | int32 | 1 | 1 |   
key1 | 状态0-正常 1-放生 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_animal_status&key0=1&key1=1

  * 改动历史

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

#### 宠物-宠物天赋升级

  * **命令字** **_upgrade_military_animal_talent_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 升级类型 | int32 | 1 | 1 |   
key1 | 天赋id | int32 | 1 | 1 |   
key2 | 目标等级 | int32 | 1 | 1 |   
key3 | 消耗 | int32 | 1 | 1 |   
key4 | 宠物id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=upgrade_military_animal_talent&key0=1&key1=1&key2=1&key3=1&key4=1

  * 改动历史

版本号 | 说明  
---|---  
v4.5 | 新增接口  
  
* * *

#### 宠物-宠物潜能升级

  * **命令字** **_upgrade_military_animal_potential_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 升级类型 | int32 | 1 | 1 |   
key1 | 潜能天赋id | int32 | 1 | 1 |   
key2 | 目标等级 | int32 | 1 | 1 |   
key3 | 消耗 | int32 | 1 | 1 |   
key4 | 宠物id | int32 | 1 | 1 |   
key5 | 潜能树id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=upgrade_military_animal_potential&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1

  * 改动历史

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.47.广告

* * *

#### 广告-领取每次播放广告奖励

  * **命令字** **_claim_ad_stage_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | stage | int32 | 1 | 1 |   
key1 | ad_type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_ad_stage_reward&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.0.1 | 新增接口  
  
* * *

#### 广告-领取累计播放广告奖励

  * **命令字** **_claim_ad_cumulative_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_ad_cumulative_reward

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.0.1 | 新增接口  
  
* * *

### 7.48.建筑

* * *

#### 建筑-建筑升级

  * **命令字** **_building_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 操作类型 | int8 | 1 | 1 | 0: normal, 1: instant(材料足够,消耗材料), 2: buy(材料不足,不消耗材料)  
key1 | pos | int32 | 102 | 1 |   
key2 | building type | int8 | 1 | 1 |   
key3 | target level | int64 | 1 | 1 |   
key4 | gem cost or cost time | int64 | 11 | 1 | key0为0时为cost time, key0为1或2时为gem cost  
key5 | exp | int32 | 1 | 1 |   
key6 | 是否直接req help | int64 | 1 | 1 |   
key7 | client_action_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=building_upgrade&key0=1&key1=102&key2=1&key3=1&key4=11&key5=1&key6=1&key7=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.4 | 新增接口  
  
* * *

#### 建筑-拆除建筑

  * **命令字** **_building_remove_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int8 | 0 | 1 | 0: normal, 1: instant, 2: buy_and_use  
key1 | pos | int32 | 151 | 1 |   
key2 | cost time | int64 | 544 | 1 |   
key3 | price | int64 | 1211 | 1 |   
key10 | building id | int64 | 1 | 1 |   
key11 | building lv | int64 | 11 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=building_remove&key0=0&key1=151&key2=544&key3=1211&key10=1&key11=11

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.4 | 新增接口  
  
* * *

#### 建筑-主城建筑位置编辑

  * **命令字** **_building_exchange_pos_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 | 移动建筑item id  
key1 | gem_cost | int64 | 1 | 1 | 移动建筑的宝石消耗 > 0则优先消耗宝石  
key2 | source pos | int32 | 122 | 1 | 移动建筑的位置  
key3 | target pos | int32 | 1223 | 1 | 建筑目标位置  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=building_exchange_pos&key0=1&key1=1&key2=122&key3=1223

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 建筑-切换建筑时代

  * **命令字** **_change_building_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | pos | int64 | 144 | 1 |   
key1 | stage | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_building_stage&key0=144&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.4 | 新增接口  
  
* * *

### 7.49.开关

* * *

#### 开关-拉指定服的开关信息

  * **命令字** **_get_other_function_schedule_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid_list | string | 1,2,3,4 | 1 | sid列表,逗号分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_other_function_schedule&key0=1,2,3,4

  * 命令字反包 - svr_other_function_schedule
  * **改动历史**

版本号 | 说明  
---|---  
v5.7 | 新增接口  
  
* * *

#### 开关-设置跟随玩家uid的通用开关

  * **命令字** **_set_player_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 1 | 1 | 开关类型  
key1 | value | int32 | 1 | 1 | 开关值  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_player_switch&key0=1&key1=1

  * 命令字反包 - svr_player_switch

  * **改动历史**

  * **备注**




> id详见https://alidocs.dingtalk.com/i/nodes/m9bN7RYPWdlyPGMXfgolmzdPWZd1wyK0?utm_scene=team_space

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

### 7.50.怪物聚集地march

* * *

#### 怪物聚集地march-怪物聚集地 rally war

  * **命令字** **_rally_attack_lair_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | int64 | 123 | 1 |   
key1 | pos | int64 | 1230123 | 1 |   
key3 | troop list | string | 1:2:4 | 1 | (以:分隔)  
key4 | prepare time | uint32 | 12 | 1 |   
key5 | is hero not join | int32 | 1 | 1 |   
key6 | card_list | string | 1,2,3 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
Key7 | quick_send | int32 | 1 | 0 | 含义为是否在满员时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
key11 | wild_class | uint32 | 1 | 1 | 目标地块class  
key12 | wild_type | uint32 | 1 | 1 | 目标地块type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_attack_lair&key0=123&key1=1230123&key3=1:2:4&key4=12&key5=1&key6=1,2,3&Key7=1&Key10=1&key11=1&key12=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
v7.0.2 | 修改接口  
  
* * *

#### 怪物聚集地march-支援怪物聚集地 rally war

  * **命令字** **_rally_reinforce_lair_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | int64 | 1213 | 1 |   
key1 | pos | int64 | 123 | 1 |   
key3 | troop list | int32 | 1:2:3 | 1 | (以:分隔)  
key4 | rally war action id | int64 | 123 | 1 |   
key6 | card_list | string | 1,2,3 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_reinforce_lair&key0=1213&key1=123&key3=1:2:3&key4=123&key6=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

### 7.51.悬赏

* * *

#### 悬赏-领取阶段目标奖励

  * **命令字** **_gem_bounty_claim_total_stage_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | stage_id | int32 | 1 | 1 | 星星目标的阶段数(1-3)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_bounty_claim_total_stage_reward&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 悬赏-领取任务完成奖励

  * **命令字** **_gem_bounty_claim_task_stage_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | task_id | int32 | 1 | 1 | 任务目标的id  
key1 | stage_id | int32 | 1 | 1 | 任务目标的阶段数(0-2按服务器下发的数据转发即可)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gem_bounty_claim_task_stage_reward&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

### 7.52.惊魂马戏团

* * *

#### 惊魂马戏团-匹配成功

  * **命令字** **_op_circus_battle_match_succ_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 见下面的备注 | 1 |   
key1 | 匹配用户信息 | json | 见下面的备注 | 1 |   
key2 | 活动难度 | int | 1 | 1 |   
key3 | 匹配完成时间 | long | 1234556 | 1 |   
key4 | route key | long | 1 | 1 | 运营服务路由使用的key  
key5 | 战场相关信息 | json | 见下面的备注 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_circus_battle_match_succ&key0=见下面的备注&key1=见下面的备注&key2=1&key3=1234556&key4=1&key5=见下面的备注

  * **匹配信息**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-1){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-2)    "long":    //uid
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-3)    {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-4)        "left_times":long,  //当日剩余参赛次数（已-1），用于战场结算弹窗反包
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-5)        "tid":long,         //team id，如无则为0
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-6)        "avatar":long,      //玩家头像
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-7)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb50-8)}

  * **战场相关信息**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb51-1){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb51-2)    "buff":[ //战场buff
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb51-3)        [id,num],//buf id num
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb51-4)        ...
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb51-5)    ],
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb51-6)}

  * **备注**



> 直连hu_tcp，反包表名svr_circus_battle_open_result

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 惊魂马戏团-拉取 战场状态

  * **命令字** **_get_circus_battle_status_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战场sid | int | 1 | 1 | 战场sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_circus_battle_status&key0=1

  * **改动历史** > 反包表名svr_circus_battle_status

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

### 7.53.成长任务

* * *

#### 成长任务-领取任务奖励

  * **命令字** **_claim_growth_quest_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | task_id | int64 | 1 | 1 | 任务id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_growth_quest_reward&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

#### 成长任务-领取活跃度奖励

  * **命令字** **_claim_growth_quest_liveness_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | liveness | int64 | 1 | 1 | 活跃度  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_growth_quest_liveness_reward&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

### 7.54.战场move

* * *

#### 战场move-进入战场准备 //enter_battle_map_preprocess

  * **命令字** **_enter_battle_map_preprocess_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | battle_id | int64 | 123 | 1 |   
key3 | item_id | int64 | 123 | 0 |   
key4 | cost | int64 | 123 | 0 |   
key5 | type | int64 | 1 | 0 | 0-消耗道具 1-消耗金币  
key7 | extra | string | 1 | 1 | 扩展字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=enter_battle_map_preprocess&key0=123&key1=123&key3=123&key4=123&key5=1&key7=1

  * **备注**



> key0 = 战场类型 key1 = 战场id key2 = xxx key3 = 消耗的道具id key4 = 喜好 key7 = extra 客户端额外信息
    
    
    {
        "event_type": int, // V7.1.1 进入战场类型
        "event_id": str, //V7.1.1 进入战场活动id
    }

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 战场move-进入战场 //可替换掉enter_ava_battle_map

  * **命令字** **_enter_battle_map_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | battle_id | int64 | 123 | 1 |   
key2 | move_city_pos | int64 | 1230123 | 0 | v5.6 水晶岛活动进入战场时该值传0  
key3 | item_id | int64 | 123 | 0 |   
key4 | gem_cost | int64 | 123 | 0 |   
key5 | type | int64 | 1 | 0 | 0-消耗道具 1-消耗金币  
key6 | province | int64 | 123 | 0 | 所选省,水晶岛活动战场必传. v5.6优化需求 废弃  
key7 | extra | string | 1 | 1 | 扩展字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=enter_battle_map&key0=123&key1=123&key2=1230123&key3=123&key4=123&key5=1&key6=123&key7=1

  * **battle_type**

battle_type | 活动 | 说明  
---|---|---  
0 | ava | –  
1 | 旧军团战 | –  
2 | 刹马镇 | –  
3 | ava淘汰联赛 | –  
4 | 失落之地 | –  
5 | 新军团战 | –  
6 | 擂台赛 | 需要key2，key3，key4，key5  
7 | 水晶岛 | 需要传key6,v5.6优化需求之后不需要再传  
8 | GVE | –  
9 | 新AVA | 传key0 key1  
  
  * **备注**



> key7 = extra 客户端额外信息
    
    
    {
        "event_type": int, // V7.1.1 进入战场类型
        "event_id": str, // V7.1.1 进入战场活动id
    }

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
v5.6 | 新增参数区域(key6)  
v5.6 | key6废弃  
v6.2 | 新ava  
  
* * *

#### 战场move-退出战场 //可替换掉leave_ava_battle_map

  * **命令字** **_leave_battle_map_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | int64 | 123 | 1 |   
key3 | type | uint32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=leave_battle_map&key0=123&key1=123&key2=123&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 战场move-op退出战场 //客户端不会用到

  * **命令字** **_op_leave_battle_map_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | int64 | 123 | 1 |   
key3 | type | uint32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_leave_battle_map&key0=123&key1=123&key2=123&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 战场move-战场内移城准备

  * **命令字** **_move_city_battle_prepare //修改原有命令字, 增加key3类型/增加key7_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | uint32 | 123 | 1 |   
key1 | gem_cost | int64 | 123 | 1 |   
key2 | old city pos | uint32 | 1230123 | 1 |   
key3 | type | uint32 | 1 | 1 | 移城类型, emovecitytype:: en_move_city_type__al_legion_move_city  
key4 | tar_sid | uint32 | 123 | 1 |   
key5 | type | uint32 | 1 | 1 |   
key7 | tar pos | uint32 | 1230123 | 1 | 目标坐标, 目前仅军团战移城使用  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=move_city_battle_prepare //修改原有命令字, 增加key3类型/增加key7&key0=123&key1=123&key2=1230123&key3=1&key4=123&key5=1&key7=1230123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 战场move-战场内移城

  * **命令字** **_move_city_battle //修改原有命令字, 增加key3类型_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | uint32 | 123 | 1 |   
key1 | gem_cost | int64 | 123 | 1 |   
key2 | old city pos | uint32 | 1230123 | 1 |   
key3 | int | uint32 | 1 | 1 | 移城类型, emovecitytype:: en_move_city_type__al_legion_move_city  
key4 | target_sid | uint32 | 123 | 1 | 移入/移出战场 使用  
key5 | target_pos | uint32 | 1230123 | 1 | 定点移城用  
key6 | province_idx | uint32 | 1 | 1 | 随机移城用  
key7 | cost_type | uint32 | 1 | 1 | 消耗类型 0 item。1 gem.，2 不消耗  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=move_city_battle //修改原有命令字, 增加key3类型&key0=123&key1=123&key2=1230123&key3=1&key4=123&key5=1230123&key6=1&key7=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.55.战场医院

* * *

#### 战场医院-治疗战场医院军队

  * **命令字** **_recovery_battlefield_army_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 123 | 1 | 0: troop 1: fort  
key1 | id | int32 | 123 | 1 | id  
key2 | num | int64 | 123 | 1 | num  
key3 | cost_time | int32 | 123 | 1 | 治疗消耗时间, 立即完成, 此值传0  
key4 | cost_gem | int32 | 123 | 1 | 立即完成消耗宝石数, 非立即完成, 此值传0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=recovery_battlefield_army&key0=123&key1=123&key2=123&key3=123&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 战场医院-取消治疗战场医院军队

  * **命令字** **_cancel_recovery_battlefield_army_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 123 | 1 | 对应的action id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cancel_recovery_battlefield_army&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

### 7.56.战报

* * *

#### 战报-拉取report总列表

  * **命令字** **_report_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_get

  * 备注



> 用公共参数pg传需要的页过来  
>  返回“svr_report_total_list”

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 战报-拉取report二级列表

  * **命令字** **_report_detail_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | report_type | TINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_detail_get&Key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 战报-标记已读

  * **命令字** **_report_read_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | Key0 = op type:report id,op type:report id | 自定格式 | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_read&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 战报-删除report

  * **命令字** **_report_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | Key0 = op type:report id,op type:report id | 自定格式 | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_del&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 战报-获取聊天中的report

  * **命令字** **_op_report_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | report id | TINT64 | 5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_report_get&key0=5204441

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 战报-获取联盟report

  * **命令字** **_al_report_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int8 | 1 | 1 | (0-all,1-out,2-in)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_report_get&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.38 | 新增接口  
  
* * *

#### 战报-发送通用report

  * **命令字** **_op_send_common_universal_report_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int64 | 1 | 1 |   
key1 | result | int64 | 1 | 1 |   
key2 | action_id | int64 | 1 | 1 |   
key3 | report_time | int64 | 1 | 0 | 不传则为请求处理时间  
key4 | content | string | 1 | 1 |   
key5 | from | string | 1 | 1 |   
key6 | to | string | 1 | 1 |   
key7 | uid_list | string | 1 | 1 | array,用逗号分割  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_send_common_universal_report&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1&key6=1&key7=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 战报-拉取report收藏总列表

  * **命令字** **_report_star_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_star_get

  * 备注



> 用公共参数pg传需要的页过来  
>  返回“svr_report_star_total_list”

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 战报-拉取report收藏二级列表

  * **命令字** **_report_star_detail_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | report_type | TINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_star_detail_get&Key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 战报-收藏report

  * **命令字** **_report_star_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type:report_id,op_type:report_id | 自定格式 | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_star&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 战报-report取消收藏

  * **命令字** **_report_unstar_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type:mail_id,op_type:mail_id | string | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=report_unstar&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 战报-获取收藏的report

  * **命令字** **_op_report_star_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | report id | TINT64 | 5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_report_star_get&key0=5204441

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

### 7.57.战马

* * *

#### 战马-战马马具合成

  * **命令字** **_horse_harness_recruit_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战马id | TINT64 | 1021 | 1 |   
key1 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_recruit&key0=1021&key1=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-马具升品

  * **命令字** **_horse_harness_upgrade_star_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战马id | TINT64 | 1021 | 1 |   
key1 | 目标品级 | TINT64 | 2 | 1 |   
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_upgrade_star&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-马具升阶

  * **命令字** **_horse_harness_upgrade_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战马id | TINT64 | 1021 | 1 |   
key1 | 目标阶级 | TINT64 | 2 | 1 |   
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_upgrade_stage&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-马具升级

  * **命令字** **_horse_harness_upgrade_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战马id | TINT64 | 1021 | 1 |   
key1 | 目标等级 | TINT64 | 2 | 1 |   
key2 | 所需token资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_upgrade_level&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-马具技能升级

  * **命令字** **_horse_harness_upgrade_skill_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战马id | TINT64 | 1021 | 1 |   
key1 | 目标等级 | TINT64 | 2 | 1 |   
key2 | 所需token资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_upgrade_skill_level&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-战马马具通用碎片兑换

  * **命令字** **_horse_harness_universal_piece_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 万能战马马具碎片id | TINT64 | 121 | 1 |   
key1 | 万能战马马具碎片数量 | TINT64 | 21 | 1 |   
key2 | 目标战马马具碎片id | TINT64 | 122 | 1 |   
key3 | 目标战马马具碎片数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_universal_piece_exchange&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-战马马具通用技能输兑换

  * **命令字** **_horse_harness_universal_book_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 万能战马马具技能书id | TINT64 | 121 | 1 |   
key1 | 万能战马马具技能书数量 | TINT64 | 21 | 1 |   
key2 | 目标战马马具技能书id | TINT64 | 122 | 1 |   
key3 | 目标战马马具技能书数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_universal_book_exchange&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-马具装配

  * **命令字** **_horse_harness_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 任命槽位 | TINT64 | 2 | 1 |   
key1 | id | TINT64 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_put_on&key0=2&key1=1021

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 战马-设置战马马具展示槽位

  * **命令字** **_horse_harness_set_slot_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | str_horse_harness_id | string | 1,2,3 | 1 | 将所有horse_harness_id用,隔开，槽位对应为1,2,3,4,5  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_harness_set_slot&key0=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-战马派遣任务开始

  * **命令字** **_horse_task_start_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | TINT64 | 1 | 1 | 战马任务槽位id  
key1 | task_id | TINT64 | 12 | 1 | 战马任务id  
key2 | horse_id | TINT64 | 1021 | 1 | 治安官皮肤id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_task_start&key0=1&key1=12&key2=1021

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-战马派遣任务完成奖励领取

  * **命令字** **_horse_task_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | TINT64 | 1 | 1 | 战马任务槽位id  
key1 | task_id | TINT64 | 12 | 1 | 战马任务id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_task_claim_reward&key0=1&key1=12

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-联盟宝藏分享

  * **命令字** **_al_treasure_share_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | treasure_id | TINT64 | xxx | 1 | 要分享的联盟宝藏  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_treasure_share&key0=xxx

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-联盟宝藏领取

  * **命令字** **_al_treasure_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | TINT64 | xxx | 1 | 要领取目标uid的联盟宝藏  
key1 | treasure_id | TINT64 | xxx | 1 | 要领取的联盟宝藏id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_treasure_claim_reward&key0=xxx&key1=xxx

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-拉联盟宝藏的列表

  * **命令字** **_get_al_treasure_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | TINT64 | xxx | 1 | 目标联盟id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_al_treasure_reward_list&key0=xxx

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-拉联盟宝藏的详情记录

  * **命令字** **_get_al_treasure_reward_record_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | TINT64 | xxx | 1 | 目标联盟id  
key1 | uid | TINT64 | xxx | 1 | 目标联盟id  
key2 | treasure_id | TINT64 | xxx | 1 | 要分享的联盟宝藏  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_al_treasure_reward_record&key0=xxx&key1=xxx&key2=xxx

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 战马-战马派遣任务一键派遣

  * **命令字** **_horse_task_batch_start_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | [[slot_id,task_id,horse_id]] | string | 1 | 1 | 战马派遣任务一键派遣id_list  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_task_batch_start&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

#### 战马-战马派遣任务一键奖励领取

  * **命令字** **_horse_task_batch_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | [[slot_id,task_id]] | string | 1 | 1 | 领取战马任务奖励槽位id_list  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=horse_task_batch_claim_reward&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

#### 战马-联盟宝藏一键领取

  * **命令字** **_al_treasure_batch_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | [[uid,treasure_id]] | string | 1 | 1 | 联盟宝藏领取id_list  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_treasure_batch_claim_reward&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

### 7.58.战马预设

* * *

#### 战马预设-预设改名

  * **命令字** **_set_horse_harness_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | plan_name | string | dsrfds | 1 | 预设名  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_horse_harness_plan_name&key0=1&key1=dsrfds

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

#### 战马预设-修改预设

  * **命令字** **_set_horse_harness_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | horse_harness_id | int32 | 1 | 1 |   
key2 | dwPos | int32 | 1 | 1 |   
key3 | dwType | int32 | 1 | 1 | 1-装备 2-卸下  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_horse_harness_plan&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

#### 战马预设-重置预设

  * **命令字** **_reset_horse_harness_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_horse_harness_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

#### 战马预设-使用预设

  * **命令字** **_change_horse_harness_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_horse_harness_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

### 7.59.手机号绑定

* * *

#### 手机号绑定-绑定

  * **命令字** **_bind_candlestick_id_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | csid | string | abc123 | 1 | 客户端完成绑定了sdk后获取到的csid,不可为空  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=bind_candlestick_id&key0=abc123

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

#### 手机号绑定-op换绑

  * **命令字** **_op_rebind_candlestick_id_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | csid | string | abc123 | 1 | 重新绑定的csid,解绑时传空,不为空时csid不存在会报错  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_rebind_candlestick_id&key0=abc123

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

### 7.60.拍卖

* * *

#### 拍卖-缴纳入场费

  * **命令字** **_auction_pay_admission_fee_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | auction_id | int64 | 1 | 1 |   
key1 | price | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auction_pay_admission_fee&key0=1&key1=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 拍卖-出价

  * **命令字** **_auction_set_price_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | auction_id | int64 | 1 | 1 |   
key1 | goods_id | string | 1 | 1 |   
key2 | price | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auction_set_price&key0=1&key1=1&key2=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 拍卖-设置自动竞价

  * **命令字** **_auction_set_expect_price_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | auction_id | int64 | 1 | 1 |   
key1 | goods_id | string | 1 | 1 |   
key2 | price | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auction_set_expect_price&key0=1&key1=1&key2=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 拍卖-拍卖金取回

  * **命令字** **_auction_get_expect_price_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwauctionid | int64 | 1 | 1 |   
key1 | strgoodsid | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auction_get_expect_price&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.0 | 新增接口  
  
* * *

### 7.61.指引

* * *

#### 指引-新手教学

  * **命令字** **_guide_finish_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | int32 | 2 | 1 | 2 :科技 3：训练4:召唤&强化  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=guide_finish_stage&key0=2

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.2 | 新增接口  
  
* * *

#### 指引-反派入侵

  * **命令字** **_inverse_invasion_finish_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=inverse_invasion_finish

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 指引-新手指引

  * **命令字** **_new_hand_guide_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | building_id | int32 | 1 | 1 |   
key1 | building_pos | int32 | 1122 | 1 |   
key2 | building_lv | int32 | 1 | 1 |   
key3 | troop_id | int32 | 1 | 1 |   
key4 | troop_num | int32 | 1 | 1 |   
key5 | train_cost_time | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_hand_guide&key0=1&key1=1122&key2=1&key3=1&key4=1&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.2 | 新增接口  
  
* * *

### 7.62.推送

* * *

#### 推送-推送token更新：

  * **命令字** **_apns_token_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | token | string | 5453 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=apns_token&key0=5453

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.42 | 新增接口  
  
* * *

#### 推送-推送开关更新：

  * **命令字** **_apns_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type: | int32 | 1 | 1 | 根据产品给出的类型进行定义  
key1 | switch | int32 | 1 | 1 | 0表示关，1表示仅text开，2表示text和sound全开  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=apns_switch&key0=1&key1=1

  * **备注**



> ret_response：详见svr_login表的输出

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.42 | 新增接口  
  
* * *

### 7.63.新ava

* * *

#### 新ava-新ava免费加速

  * **命令字** **_new_ava_free_speed_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | long | 3 | 1 |   
key1 | item id | int | 1 | 1 | 只是用来取加速比例，不实际消耗  
key2 | rally_war_id | int64 | 123456 | 1 | 如果是团战增援队列,则需要传对应的团战id,否则传0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_ava_free_speed_up&key0=3&key1=1&key2=123456

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

#### 新ava-采集散落积分矿

  * **命令字** **_new_ava_scattered_crystal_occupy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | long | 3 | 1 |   
key1 | target pos | int | 1310072 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_ava_scattered_crystal_occupy&key0=3&key1=1310072

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

#### 新ava-开启战场

  * **命令字** **_op_open_new_ava_battlefield_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_sid | int | 3 | 1 |   
key1 | battle_info | json | {} | 1 | 见备注  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_open_new_ava_battlefield&key0=3&key1={}

  * **battle info**


    
    
    {
        "contestants":    //参赛双方
        {
            "int":     //side， 0：红 1：蓝
            [
                int,   //aid
                int,   //ksid
                int,   //al_flag
                str,   //al_nick
                str,   //al_name
                int,   //军团，1：主军团 2：副军团
                [
                    long,     //成员uid list
                ]
            ]
        },
        "battle_info":     //战场属性
        {
            "time_info":   //时间属性
            [
                long,   //战场准备期时间戳
                long,   //阶段一开始时间戳
                long,   //阶段二开始时间戳
                long,   //阶段三开始时间戳
                long    //战场结算时间戳
            ]
            "building_info":   //建筑详情
            {
                "score_building":    //占领积建筑
                {
                    "int":       //wild class
                    [
                        long,    //首占个人积分
                        long,    //首占军团积分
                        long,    //持续占领个人积分速率 x/min
                        long,    //持续占领军团积分速率 x/min，x要求被60整除
                        long,    //建筑破罩时间戳
                    ]
                },
                "warehouse":     //资源仓库
                {
                    "refresh":   //刷新配置
                    [
                        [
                            long,   //刷新时间戳
                            int,    //刷出数量
                        ]
                    ],
                    "info":      //资源仓库属性
                    [
                        long,    //积分总量
                        long,    //拉取速度  x/s
                    ]
    
                },
                "score_mine": { // 积分矿（占领积分掉落实体）
                    "num": [int, int], // 掉落的积分矿数量 [数量下限，数量上限] v6.6 废除 不用传
                    "min_score": int // 每个矿的最小积分值
                    "score_mine_conf": // v6.6 新增
                    [
                        {
                            "score_num": [int, int],  //被扣除的积分总量
                            "num": [int, int], // 掉落的积分矿数量 [数量下限，数量上限]
                        }
                    ],
                },
                "legion_score_rate": int, //v6.6 军团积分扣除 X,万分制
            }
        }
    
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

### 7.64.新kvk

* * *

#### 新kvk-新kvk捐献

  * **命令字** **_new_kvk_donate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | str | 1 | 1 | 活动id  
key1 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_kvk_donate&key0=1&key1=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-拉取炮塔监控攻击队列信息

  * **命令字** **_get_building_monitor_attack_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 3 | 1 | 监控的建筑sid  
key1 | pos | long | 3 | 1 | 监控的建筑坐标,如王座坐标  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_building_monitor_attack_info&key0=3&key1=3

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-拉取炮塔监控支援队列信息

  * **命令字** **_get_building_monitor_reinforce_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 3 | 1 | 监控的建筑sid  
key1 | pos | long | 3 | 1 | 监控的建筑坐标,如王座坐标  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_building_monitor_reinforce_info&key0=3&key1=3

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-活动丰碑-复活兵

  * **命令字** **_event_monument_troop_revive_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | eventid | str | 3 | 1 | 医院活动id  
key1 | troop_list | json_str | [[id,num],[id,num],…] | 1 | 治疗兵列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=event_monument_troop_revive&key0=3&key1=[[id,num],[id,num],…]

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-活动丰碑-提升复活比例

  * **命令字** **_event_monument_troop_revive_percent_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | eventid | str | 3 | 1 | 医院活动id  
key1 | gem_num | long | 3 | 1 | 消耗宝石数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=event_monument_troop_revive_percent_up&key0=3&key1=3

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-联盟帮助other-请求援助

  * **命令字** **_al_help_other_request_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | long | 3 | 1 | 请求援助类型  
key1 | eventid | str | 3 | 1 | 医院活动id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_help_other_request&key0=3&key1=3
    
    
    请求援助类型：
    1、活动丰碑

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-联盟帮助other-援助X次

  * **命令字** **_al_help_other_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | str | 3 | 1 | 被帮助uid  
key1 | action_id | long | 1 | 1 | 被帮助action id  
key2 | cost | str | [[type,id,num],…] | 1 | 单次消耗道具  
key3 | num | long | 1 | 1 | 帮助次数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_help_other_new&key0=3&key1=1&key2=[[type,id,num],…]&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-获取其他人活动丰碑信息

  * **命令字** **_get_other_event_monument_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | eventid | str | 3 | 1 | 医院活动id  
key1 | uid | long | 1 | 1 | uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_other_event_monument&key0=3&key1=1

  * **反包**


    
    
    svr_other_event_monument

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-获取统治官礼包列表

  * **命令字** **_get_new_kvk_emperor_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 1 | 1 | sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_new_kvk_emperor_reward_list&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-获取统治官礼包详情

  * **命令字** **_get_new_kvk_emperor_reward_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 1 | 1 | sid  
key1 | gift_id | long | 1 | 1 | gift_id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_new_kvk_emperor_reward_history&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-统治官发礼包

  * **命令字** **_new_kvk_emperor_send_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | long | 1 | 1 | uid  
key1 | gift id | long | 1 | 1 | 礼包id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_kvk_emperor_send_reward&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-更新特殊统治官礼包信息

  * **命令字** **_op_new_kvk_set_king_gift_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | king_gift_info | json_str | 3 | 1 | 特殊统治官礼包信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_new_kvk_set_king_gift_info&key0=3

  * **king gift info**


    
    
    {
        "event_id":str, //活动id
        "close_time":long, //活动关闭时间
        "sid_list":[sid1,sid2,sid3],     //3个sid,顺序保持运营一致,下标代表红绿蓝
        "sheriff_gift_conf": //统治官礼包
        {
            "reward_conf": [
                {
                    "gift_lv": int //奖励级别 0:低级奖励配置 1:中级奖励配置 2:高级奖励配置
                    "gift_list": 
                    {
                        "gift_id" : //礼包id 要求本pid内是唯一的
                        {
                            "reward": [
                                {"a":[int,int,int]} //设计上这里只给配置箱子 便于展示处理
                            ],
                            "limit_num": int //发奖次数限制
                        },
                    },
                }
            ]
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-匹配成功通知

  * **命令字** **_op_new_kvk_match_succ_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_info | json_str | 3 | 1 | 匹配战场信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_new_kvk_match_succ&key0=3

  * **battle info**


    
    
    {
        "event_id":str, //活动id
        "event_type":long, //活动type
        "pid":long, //活动pid
        "skill_pid":long, //技能方案PID
        "prepare_castle_lv":long, //备战等级要求
        "fight_castle_lv":long, //对战等级要求
        "battle_info":    //参赛者
        {
            "sid_list":[sid1,sid2,sid3],     //3个sid,顺序保持运营一致,下标代表红绿蓝
            "fight_beg_time":long,       //对战期开始时间
            "fight_stage_time":            //每轮对战的时间
            [
                [        //第idx + 1轮的时间
                    long,  //本轮btime
                    long   //本轮etime
                ]
            ],
            "barrier_period":            //v6.9.1 孤星壁垒各轮时间配置 实际未使用 备战期结算时才正式使用
            [
                [        //第idx + 1轮的时间
                    long,  //本轮btime
                    long   //本轮etime
                ]
            ],
            "prepare_war_time":long,            //备战期开始时间
            "fight_end_time":long,    //对战期结束时间
            "fight_prepare_time":long,//对战准备期时间
            "end_time":long,//活动结束时间
            "duration_conf":    //单位秒
            [
                int,    //对战期结束后最长多久踢出战场
                int,    //警戒状态开启提示，密林之地警戒状态前X分钟
                int,    //警戒状态，建筑争夺期前X
                int,    //警戒状态，建筑争夺期前Y
                int,    //城内提醒横幅时间偏移（包括对战期即将开始、第x轮建筑争夺即将开始、第x轮建筑争夺即将结束、战场即将关闭），默认15分钟
                int,    //城外提醒横幅时间偏移（包括对战期即将开始、第x轮建筑争夺即将开始、第x轮建筑争夺即将结束、战场即将关闭），默认1分钟
                int,    //离线推送的推送时间，每轮建筑争夺期开启前x分钟
                int,    //对战期结束后x秒开始遣返
                int,    //孤星壁垒-某服务器连续占领达到Z时长则提前结束争夺并关闭建筑    v6.9.1 Z值＜Y值（barrier_battle_duration）＜X值（barrier_duration）
            ],
    
            "other_info":
            {
                "user_score_diff":int,       //主城攻防可得分的评分差，万分制 v6.9.1 废弃
                "free_move_city":int,   //免费跨服移城进出敌方服务器次数
                "buy_move_num":int,     //付费移城金砖购买次数
                "buff_list":   //对战期战场buff，对战期固定生效的buff（和平守卫和战争狂热、主战场中心密林行军加速）、v6.9.1 活动矿行军加速buff
                [
                    [int, int]  //[buff_id, buff_num]
                ]
            }
        },
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-备战期服务器rank通知

  * **命令字** **_op_new_kvk_prepare_fighting_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_info | json_str | 3 | 1 | 结算信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_new_kvk_prepare_fighting_reward&key0=3

  * **battle info**


    
    
    {
        "event_id":str, //活动id
        "event_type":long, //活动type
        "pid":long, //活动pid
        "skill_pid":long, //技能方案pid
        "rank":[ //下标为排名,支持3个sid排名(最后一名为主战场)
            {
                "sid":long, 
                "buff":[ //胜负buff,生效期为对战期
                    [id,num],//buf id num
                    ...
                ],
            }
        ],
        "battle_info":    //参赛双方
        {
            "sid_list":[sid1,sid2,sid3],  //支持3个sid,顺序保持运营一致,下标代表红绿蓝
            "fight_beg_time":long,       //对战期开始时间
            "fight_stage_time":            //每轮对战的时间
            [
                [        //第idx + 1轮的时间
                    long,  //本轮btime
                    long   //本轮etime
                ]
            ],
            "barrier_period":            //v6.9.1 孤星壁垒各轮时间配置
            [
                [        //第idx + 1轮的时间
                    long,  //本轮btime
                    long   //本轮etime
                ]
            ],
            "fight_end_time":long,    //对战期结束时间
            "fight_prepare_time":long,//对战准备期时间
            "end_time":long,//活动结束时间
            "map_conf": //战场配置
            {
                "mine":    //活动矿
                {
                    "${wild_id}":   //地形id
                    {
                        "reward":[{"a":[int,int,int]}],     //捐献token [[type,id,num]]，只支持一个
                        "refresh":                          //刷地信息
                        [
                            long,   //刷出数量
                            long,   //最大刷地半径
                        ],
                        "collect":                          //采集信息
                        [
                            long,   //捐献token采集速率，X秒
                            long,   //捐献token采集速率，Y个
                            long,   //占领每N秒，固定60
                            long,   //占领每M分
                        ],
                        "army_num":long,    // v6.9.1 活动矿出兵数量
                    }
    
                },
                "barrier":  // v6.9.1 孤星壁垒
                {
                    "refresh":                          //刷地信息
                    [
                        long,   //刷出数量，至少支持刷出20个
                        long,   //X，第X次及之后搜寻坐标时，开始处理主城&正在被采集的资源地
                        long,   //Y，最多进行搜索次数
                    ]
                },
                "turret":  // v6.9.1 不刷出炮塔时，无需配置炮塔坐标
                {
                    "${pos}": int,  // 炮塔坐标：炮塔id，例：  2500600：81
                }
                "building":    //建筑得分速率
                {
                    "${building_id}":   //建筑id，非wild_class
                    [
                        long,   //个人得分速率(x/min)
                        long,   //服务器得分速率(x/min)
                    ]
                },
                "boss": // v7.1 限时boss 后台
                {
                    "center_pos":int,   //中心位置，写死2500600
                    "range":int,        //刷出半径
                },
                "march_limit": // v7.2.2 队列限制
                {
                    "type": int,   //限制方式-配置开关 0-不启用 1-启用a方式 2-启用b方式
                    "plan_a" : long,  //a方式限制 每个玩家同时可派出的战争/增援队列到指定建筑的建筑总个数限制 x个建筑(首府/炮塔/孤星壁垒) (合法性校验 1~6)
                    "plan_b" : //b方式限制 
                    [
                        long, //每个玩家同时可派出的战争/增援队列到炮塔建筑个数限制 x个炮塔 (合法性校验 1~6)
                        long, //每个玩家同时可派出的战争/增援队列到炮塔建筑个数限制 y个孤星壁垒 (合法性校验 1~6)
                    ]
                },
                "open_battle_buff":int, //v7.2.7 是否开战争狂热buff，默认开，0-不开、1-开
            },
            "duration_conf":    //单位秒
            [
                int,    //对战期结束后最长多久踢出战场
                int,    //警戒状态开启提示，密林之地警戒状态前X分钟
                int,    //警戒状态，建筑争夺期前X
                int,    //警戒状态，建筑争夺期前Y
                int,    //城内提醒横幅时间偏移（包括对战期即将开始、第x轮建筑争夺即将开始、第x轮建筑争夺即将结束、战场即将关闭），默认15分钟
                int,    //城外提醒横幅时间偏移（包括对战期即将开始、第x轮建筑争夺即将开始、第x轮建筑争夺即将结束、战场即将关闭），默认1分钟
                int,    //离线推送的推送时间，每轮建筑争夺期开启前x分钟
                int,    //对战期结束后x秒开始遣返
                int,    //孤星壁垒-某服务器连续占领达到Z时长则提前结束争夺并关闭建筑    v6.9.1 Z值＜Y值（barrier_battle_duration）＜X值（barrier_duration）
            ],
    
            "other_info":
            {
                "user_score_diff":int,       //主城攻防可得分的评分差，万分制 v6.9.1 废弃
                "free_move_city":int,   //免费跨服移城进出敌方服务器次数
                "buy_move_num":int,     //付费移城金砖购买次数
                "buff_list":   //对战期战场buff，对战期固定生效的buff（和平守卫和战争狂热、主战场中心密林行军加速）、v6.9.1 活动矿行军加速buff
                [
                    [int, int]  //[buff_id, buff_num]
                ]
            }
        },
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-设置服务器buff

  * **命令字** **_op_set_kingdom_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 3 | 1 | sid  
key1 | sources | long | 1 | 1 | 来源  
key2 | battle_info | json_str | 3 | 1 | 结算信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_kingdom_buff&key0=3&key1=1&key2=3

  * **sources**

sources type | 备注  
---|---  
1 | 新svs备战期服务器rank buff  
2 | 新svs捐献  
其它数字 | 可能是方便自测加的任何来源  
  
  * **battle info**


    
    
    {
        "event_id":str, //活动id
        "buff": //buff id num,btim,etime
        [
            [id,num,beg_time,end_time], 
        ],
        "condition": //buff额外生效条件,可以没有,可以一项或多项
        {
            "castle_lv":long, //主城等级要求
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-计分板同步

  * **命令字** **_op_new_kvk_sync_score_board_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_info | json_str | 3 | 1 | 结算信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_new_kvk_sync_score_board&key0=3

  * **battle info**


    
    
    {
        "event_id":str, //活动id
        "score_board":
        {
            "sid":
            {
                "data" : 
                {
                    "team" : long, //sid阵营
                    "sid" : long, //sid数据
                    "points" : long,//得分
                    "update_time" : long,//得分更新时间
                    "is_main" : long,//是否是主战场
                }
            }
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-对战期服务器rank通知

  * **命令字** **_op_new_kvk_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_info | json_str | 3 | 1 | 结算信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_new_kvk_result&key0=3

  * **battle info**


    
    
    {
        "event_id":str, //活动id
        "event_type":int, 
        "event_pid":int,
        "rank":[
            {
                "type":long, //0-防守 1-进攻方
                "sid":long, 
                "aid":long, //统治官所属联盟 没有给0 
                "rank":log, //
                "score":log, //服务器分 没有给0
            }
        ],
        "is_draw" : 1 //0-不平局 1-平局
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-开启双方战场(后台内部调用)

  * **命令字** **_op_open_new_kvk_battle_procedure_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int | 3 | 1 | 主战场sid  
key1 | battle_info | json_str | 3 | 1 | 开启战场信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_open_new_kvk_battle_procedure&key0=3&key1=3

  * **battle info**


    
    
    {
        "event_id":str, //活动id
        "battle_info":    //参赛双方
        {
            "sid_list":[sid1,sid2,sid3],     //3个sid,顺序保持运营一致,下标代表红绿蓝
            "fight_beg_time":long,       //对战期开始时间
            "fight_stage_time":            //每轮对战的时间
            [
                [        //第idx + 1轮的时间
                    long,  //本轮btime
                    long   //本轮etime
                ]
            ],
            "barrier_period":            //v6.9.1 孤星壁垒各轮时间配置
            [
                [        //第idx + 1轮的时间
                    long,  //本轮btime
                    long   //本轮etime
                ]
            ],
            "fight_end_time":long,    //对战期结束时间
            "fight_prepare_time":long,//对战准备期时间
            "end_time":long,//活动结束时间
            "map_conf": //战场配置
            {
                "mine":    //活动矿
                {
                    "${wild_id}":   //地形id
                    {
                        "reward":[{"a":[int,int,int]}],     //捐献token [[type,id,num]]，只支持一个
                        "refresh":                          //刷地信息
                        [
                            long,   //刷出数量
                            long,   //最大刷地半径
                        ],
                        "collect":                          //采集信息
                        [
                            long,   //捐献token采集速率，X秒
                            long,   //捐献token采集速率，Y个
                            long,   //占领每N秒，固定60
                            long,   //占领每M分
                        ],
                        "army_num":long,    // v6.9.1 活动矿出兵数量
                    }
    
                },
                "barrier":  // v6.9.1 孤星壁垒
                {
                    "refresh":                          //刷地信息
                    [
                        long,   //刷出数量，至少支持刷出20个
                        long,   //X，第X次及之后搜寻坐标时，开始处理主城&正在被采集的资源地
                        long,   //Y，最多进行搜索次数
                    ]
                },
                "turret":  // v6.9.1 不刷出炮塔时，无需配置炮塔坐标
                {
                    "${pos}": int,  // 炮塔坐标：炮塔id，例：  2500600：81
                }
                "building":    //建筑得分速率
                {
                    "${building_id}":   //建筑id，非wild_class
                    [
                        long,   //个人得分速率(x/min)
                        long,   //服务器得分速率(x/min)
                    ]
                }
            },
            "duration_conf":    //单位秒
            [
                int,    //对战期结束后最长多久踢出战场
                int,    //警戒状态开启提示，密林之地警戒状态前X分钟
                int,    //警戒状态，建筑争夺期前X
                int,    //警戒状态，建筑争夺期前Y
                int,    //城内提醒横幅时间偏移（包括对战期即将开始、第x轮建筑争夺即将开始、第x轮建筑争夺即将结束、战场即将关闭），默认15分钟
                int,    //城外提醒横幅时间偏移（包括对战期即将开始、第x轮建筑争夺即将开始、第x轮建筑争夺即将结束、战场即将关闭），默认1分钟
                int,    //离线推送的推送时间，每轮建筑争夺期开启前x分钟
                int,    //对战期结束后x秒开始遣返
                int,    //孤星壁垒-某服务器连续占领达到Z时长则提前结束争夺并关闭建筑    v6.9.1 Z值＜Y值（barrier_battle_duration）＜X值（barrier_duration）
            ],
        },
    }

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 新kvk-新kvk备战期 刷boss

  * **命令字** **_op_gen_new_kvk_boss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 1 | 1 | sid  
key1 | center_pos | long | 1 | 1 | 2500600  
key2 | range | long | 1 | 1 | 刷boss在中心点范围  
key3 | end_time | long | 1 | 1 | boss消失时间  
key4 | event_id | string | 1 | 1 | boss活动even id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_new_kvk_boss&key0=1&key1=1&key2=1&key3=1&key4=1

> 运营在备战期开始时刻刷出

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

#### 新kvk-新kvk备战期 攻打限时boss

  * **命令字** **_new_kvk_boss_solo_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | target_pos | TINT32 | 3420022 | 1 |   
Key1 | march_time | TINT64 | 123 | 1 | 行军时间  
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_kvk_boss_solo_attack&Key0=3420022&Key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

### 7.65.新兑换商店

* * *

#### 新兑换商店-新兑换商店-兑换

  * **命令字** **_new_exchange_shop_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | shop_big_type | int32 | 1 | 1 | 商店大类型,1代表普通商店,2代表回收站  
key1 | shop_type | int32 | 1 | 1 | 商店类型,具体见新兑换商店协议  
key2 | shop_id | string | abc123 | 1 |   
key3 | good_id | int64 | 1 | 1 | 商品id,全局唯一  
key4 | buy_num | int64 | 1 | 1 | 购买次数  
key5 | cost | json | [{“a”:[0,1,1]}] | 1 | 购买消耗,需要合并相同项,传递1个商品的消耗  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_exchange_shop_buy&key0=1&key1=1&key2=abc123&key3=1&key4=1&key5=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

#### 新兑换商店-新兑换商店-解锁条件

  * **命令字** **_op_new_exchange_shop_update_event_rule_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 对应商店协议里面的【条件类型】type  
key1 | range | int32 | 1 | 1 | 对应商店协议里面的【生效范围】range  
key2 | range_value | int32 | 1 | 1 | 对应商店协议里面的【生效范围】range的值  
key3 | event_id | string | “11111” | 1 | 活动id  
key4 | event_type | int32 | 1 | 1 | 活动type  
key5 | event_pid | int32 | 1 | 1 | 此活动的pid  
key6 | value | int32 | 1 | 1 | 解锁的具体的value  
key7 | time | int64 | 1 | 1 | 解锁规则的时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_new_exchange_shop_update_event_rule&key0=1&key1=1&key2=1&key3=“11111”&key4=1&key5=1&key6=1&key7=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

### 7.66.新军团战

* * *

#### 新军团战-报名

  * **命令字** **_new_legion_sign_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 军团id(aid×10000+legion_idx×100+0) | int64 | 10002160100 | 1 |   
key1 | 新军团活动id | string | 127_168828939934_1_0 | 1 |   
key2 | 报名战斗id（对应排期配置） | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_legion_sign_up&key0=10002160100&key1=127_168828939934_1_0&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-取消报名

  * **命令字** **_new_legion_sign_up_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 军团id(aid×10000+legion_idx×100+0) | int64 | 10002160100 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_legion_sign_up_cancel&key0=10002160100

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-修改军团名称

  * **命令字** **_new_legion_change_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 军团id(aid×10000+legion_idx×100+0) | int64 | 10002160100 | 1 |   
key1 | 军团名字 | string | new_legion_name | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_legion_change_name&key0=10002160100&key1=new_legion_name

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-成员管理

  * **命令字** **_new_legion_member_manage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 军团id(aid×10000+legion_idx×100+0) | int64 | 10002160100 | 1 |   
key1 | 操作类型 1-参战 2-移除 | int32 | 1 | 1 |   
key2 | 目标成员uid | int64 | 1000216 | 1 |   
key3 | 报名活动id | string | 127_168828939934_1_0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_legion_member_manage&key0=10002160100&key1=1&key2=1000216&key3=127_168828939934_1_0

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-军团长管理

  * **命令字** **_new_legion_commander_manage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 军团id(aid×10000+legion_idx×100+0) | int64 | 10002160100 | 1 |   
key1 | 操作类型 1-参战 2-移除 | int32 | 1 | 1 |   
key2 | 目标军团长uid | int64 | 1000216 | 1 |   
key3 | 报名活动id | string | 127_168828939934_1_0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_legion_commander_manage&key0=10002160100&key1=1&key2=1000216&key3=127_168828939934_1_0

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-解散军团

  * **命令字** **_new_legion_disband_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 军团id(aid×10000+legion_idx×100+0) | int64 | 10002160100 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_legion_disband&key0=10002160100

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-拉战况

  * **命令字** **_get_legion_war_situation_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 155 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_legion_war_situation_new&key0=155

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-拉取所有被完全占领的战场城市

  * **命令字** **_get_all_full_occupied_legion_city_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 155 | 1 | 进入军团战地图时主动拉一次,收到svr_all_full_occupied_legion_city_list_new_flag时主动拉一次  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_all_full_occupied_legion_city_new&key0=155

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-领取军团胜负奖励

  * **命令字** **_confirm_al_legion_war_result_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
|  |  |  | 0 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=confirm_al_legion_war_result_new&=

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 新军团战-一键委派新军团成员

  * **命令字** **_new_al_legion_quick_assign_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion id | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_al_legion_quick_assign&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 新军团战-拉取新军团战玩家活动操作日志

  * **命令字** **_get_al_legion_new_op_record_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_al_legion_new_op_record_list&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 新军团战-玩家新军团请战操作

  * **命令字** **_al_legion_new_ask_fight_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | old legion key | int64 | 123 | 1 | key2为1时传0  
key1 | new legion key | int64 | 123 | 1 | 发出请战操作目标军团key  
key2 | type | int32 | 1 | 1 | 操作, 1-发出请战, 2-取消请战 3-修改请战  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_new_ask_fight&key0=123&key1=123&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 新军团战-玩家新军团不参与操作

  * **命令字** **_al_legion_new_no_fight_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | legion key | int64 | 123 | 1 | 操作目标军团key  
key1 | type | int32 | 1 | 1 | 操作, 1-申请不参与, 2-取消不参与  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_legion_new_no_fight&key0=123&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.67.新手充值返利活动

* * *

#### 新手充值返利活动-领取新手充值返利活动奖励

  * **命令字** **_claim_novice_recharge_rebate_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 任务id | TINT64 | 2 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_novice_recharge_rebate_reward&key0=2

  * **改动历史**

版本号 | 说明  
---|---  
v4.1.1 | 新增接口  
  
* * *

#### 新手充值返利活动-领取充值返利活动奖励

  * **命令字** **_claim_recharge_rebate_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168023798_1_0 | 1 |   
key1 | 任务id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_recharge_rebate_reward&key0=127_168023798_1_0&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.1.1 | 新增接口  
  
* * *

#### 新手充值返利活动-选择一个任务

  * **命令字** **_choice_recharge_rebate_task_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168023798_1_0 | 1 |   
key1 | 任务id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=choice_recharge_rebate_task&key0=127_168023798_1_0&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.1.1 | 新增接口  
  
* * *

#### 新手充值返利活动-取消选择任务

  * **命令字** **_unchoice_recharge_rebate_task_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168023798_1_0 | 1 |   
key1 | 任务id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=unchoice_recharge_rebate_task&key0=127_168023798_1_0&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.1.1 | 新增接口  
  
* * *

### 7.68.新折扣商店

* * *

#### 新折扣商店-新折扣商店-购买折扣商品

  * **命令字** **_item_buy_discount_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1xx_xxxx_xxx | 1 |   
key1 | good_id | int64 | 1 | 1 | 商品id,全局唯一  
key2 | buy_num | int64 | 1 | 1 | 购买次数  
key3 | cost | json | [0,1,1] | 1 | 购买消耗,需要合并相同项,传递1个商品的消耗  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_buy_discount_new&key0=1xx_xxxx_xxx&key1=1&key2=1&key3=[0,1,1]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 新折扣商店-新折扣商店-刷新神秘商店

  * **命令字** **_refresh_mystery_shop_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1xx_xxxx_xxx | 1 |   
key1 | cost | json | [0,1,1] | 1 | 刷新消耗,需要合并相同项,传递1个刷新所需要的的消耗,免费刷新num传0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=refresh_mystery_shop_new&key0=1xx_xxxx_xxx&key1=[0,1,1]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 优化新增接口  
  
* * *

### 7.69.新节日活动

* * *

#### 新节日活动-联盟宴会-建造宴会建筑

  * **命令字** **_al_banquet_building_put_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 |   
key2 | pos | int64 | 1 | 1 |   
key3 | wild_id | int64 | 1 | 1 | 宴会建筑数值id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_banquet_building_put_up&key0=1&key1=1&key2=1&key3=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

#### 新节日活动-联盟宴会-拆除宴会建筑

  * **命令字** **_al_banquet_building_remove_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 |   
key2 | pos | int64 | 1 | 1 |   
key3 | wild_id | int64 | 1 | 1 | 宴会建筑数值id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_banquet_building_remove&key0=1&key1=1&key2=1&key3=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

#### 新节日活动-联盟宴会-设置宴会开启时间(内部接口)

  * **命令字** **_op_al_banquet_building_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 |   
key2 | pos | int64 | 1 | 1 |   
key3 | aid | int64 | 1 | 1 |   
key4 | time | int64 | 1 | 1 | 宴会开启时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_al_banquet_building_open&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp:special json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

#### 新节日活动-联盟宴会-宴会加餐

  * **命令字** **_op_al_banquet_building_add_table_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 | 宴会建筑sid  
key2 | pos | int64 | 1 | 1 | 宴会建筑坐标  
key3 | aid | int64 | 1 | 1 |   
key4 | table_info | json | 1 | 1 | 加餐信息  
key5 | wild_id | int64 | 1 | 1 | 宴会建筑数值id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_al_banquet_building_add_table&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-1)//table_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-2){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-3)    "user_info":{ //加餐者信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-4)        "uid":int,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-5)        "uname": str, // 加餐者名称
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-6)        "avatar": int, // 头像
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-7)        "head_frame": int
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-8)    },
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-9)    "table_conf":{//餐桌信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-10)        "$table_id": { //id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-11)            "num":int, //数量
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-12)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-13)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb64-14)}

> rsp:special json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

#### 新节日活动-联盟宴会-发起用餐队列

  * **命令字** **_march_al_banquet_table_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost_time | str | 1 | 1 | time  
key1 | target_pos | int64 | 1 | 1 | 坐标  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=march_al_banquet_table&key0=1&key1=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

### 7.70.最强治安官

* * *

#### 最强治安官-领取活动个人goal奖

  * **命令字** **_claim_event_center_goal_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 12_342 | 1 | string  
key1 | goal_num | int64 | 1 | 1 | int 从0开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_event_center_goal_reward&key0=12_342&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

#### 最强治安官-领取活动联盟goal奖

  * **命令字** **_claim_event_center_alliance_goal_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 123_241 | 1 | string  
key1 | goal_num | int64 | 1 | 1 | int 从0开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_event_center_alliance_goal_reward&key0=123_241&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

#### 最强治安官-领取活动服务器goal奖

  * **命令字** **_claim_event_center_serv_goal_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 123_241 | 1 | string  
key1 | goal_num | int64 | 1 | 1 | int 从0开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_event_center_serv_goal_reward&key0=123_241&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

### 7.71.本地notic

* * *

#### 本地notic-添加一个客户端本地推送

  * **命令字** **_add_local_notic_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 推送对象类型 | long | 1 | 1 | 见备注说明  
key1 | 推送对象id | long | 1 | 1 |   
key2 | 推送文案id | long | 1 | 1 |   
key3 | 消息触发时间 | long | 12345 | 1 |   
key4 | 消息替换内容 | json array | [string,string] | 1 | 下标n替换STRINGn  
key5 | extra info | string | {} | 0 |   
key6 | 展示依赖 | json array | [[type,id,value]] | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=add_local_notic&key0=1&key1=1&key2=1&key3=12345&key4=[string,string]&key5={}&key6=[[type,id,value]]

  * **推送对象类型**

type | 说明  
---|---  
1 | user  
2 | alliance  
3 | sid  
  
  * **依赖条件说明**

type | id | value  
---|---|---  
1 | 此时固定为0 | 玩家最低主城等级  
2 | 活动event_type | 军团id  
3 | 活动event_type | 0  
4 | 活动event_type | 1  
  
  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

#### 本地notic-批量添加客户端本地推送

  * **命令字** **_add_local_noti_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 推送对象类型 | long | 1 | 1 | 见备注说明  
key1 | 推送对象id | json array | [long,long] | 1 |   
key2 | 推送文案id | long | 1 | 1 |   
key3 | 消息触发时间 | long | 12345 | 1 |   
key4 | 消息替换内容 | json array | [string,string] | 1 | 下标n替换STRINGn  
key5 | extra info | string | {} | 0 |   
key6 | 展示依赖 | json array | [[type,id,value]] | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=add_local_noti_batch&key0=1&key1=[long,long]&key2=1&key3=12345&key4=[string,string]&key5={}&key6=[[type,id,value]]

  * **推送对象类型**

type | 说明  
---|---  
1 | user  
2 | alliance  
3 | sid  
  
  * **依赖条件说明**

type | id | value  
---|---|---  
1 | 此时固定为0 | 玩家最低主城等级  
2 | 活动event_type | 军团id  
3 | 活动event_type | 0  
4 | 活动event_type | 1  
  
  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

### 7.72.模拟战斗

* * *

#### 模拟战斗-生成战斗节点

  * **命令字** **_op_gen_battle_node_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 12345678 | 1 | 车头uid  
key0 | info | json | {} | 1 | 战斗信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_battle_node&uid=12345678&key0={}

  * **备注**


    
    
    info格式
    {
        "sheriff": {
            "preset_id": int,
        },
        "hero_list": [
            long, long, long
        ],
        "troop_list": {
            "long": long  // 兵id->兵数量
        },
        "global_buff": {
            "long": long // buff id->buff num
        }
    }
    反包: svr_op_battle_node

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.1 | 新增接口  
  
* * *

#### 模拟战斗-生成npc战斗节点 - 仅供后台内部使用

  * **命令字** **_op_gen_npc_battle_node_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | info | json | {} | 1 | 战斗信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_npc_battle_node&key0={}

  * **备注**


    
    
    info格式
    {
        "troop":                    //npc兵数量和种类
        [
            [
                troopid,
                num
            ]
        ],
        "slgbuff":                  //npc兵战斗时的BUFF值
        [
            [
                buffid,
                num
            ]
        ],
        "hero":                     //npc队伍英雄
        [
            [
                id,
                star,
                lv
            ]
        ]
        "sheriff":                  //治安官
        [
            3001,                   //治安官头像id
            20                      //等级                    
        ],
        "extra":
        {
            "name": string,
            "alnick": string,
            "ksid": int,
            "uid": int,
            "avatar": int,
            "alname": string,
        },
        "global_buff": {
            "long": long // buff id->buff num
        }
    }
    反包: svr_op_battle_node

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.1 | 新增接口  
  
* * *

#### 模拟战斗-跟玩家战斗

  * **命令字** **_op_do_battle_with_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 12345678 | 1 | 攻击方车头uid  
key0 | attacker_info | json | {} | 1 | 攻击方信息  
key1 | defender_node | json | {} | 1 | 防守方battle_node  
key2 | combat_type | int | 123 | 1 | 战斗类型,2->多回合solo1打1  
key3 | battle_type | int | 123 | 1 | 战斗场景,31->火车大劫案solo  
key4 | wild_class | int | 123 | 1 | 地块类型,7.0.1马车pvp掠夺用副本内主城107  
key5 | report_type | int | 123 | 1 | 报告类型,7.0.1马车pvp掠夺用117  
key6 | report_json | json | {“xxx”:xxx} | 1 | 报告内容,根据report_type传不同内容  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_do_battle_with_player&uid=12345678&key0={}&key1={}&key2=123&key3=123&key4=123&key5=123&key6={“xxx”:xxx}

  * **备注**


    
    
    attacker_info格式
    {
        "sheriff": {
            "preset_id": int,
        },
        "hero_list": [
            long, long, long
        ],
        "troop_list": {
            "long": long  // 兵id->兵数量
        },
        "global_buff": {
            "long": long // buff id->buff num
        }
    }
    // report_type: 117 时
    // report_json
    {
        "carriage_info":
        {
            "left_time": int, // 剩余可被掠夺次数
            "quality": int,   // 马车品质
        },
        "reward":[[xxx]] // 奖励
    }
    反包: svr_op_battle_result

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.1 | 新增接口  
  
* * *

#### 模拟战斗-跟npc战斗

  * **命令字** **_op_do_battle_with_npc_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 12345678 | 1 | 攻击方车头uid  
key0 | attacker_info | json | {} | 1 | 攻击方信息  
key1 | defender_info | json | {} | 1 | 防守方信息,数值配置  
key2 | combat_type | int | 123 | 1 | 战斗类型,2->多回合solo1打1  
key3 | battle_type | int | 123 | 1 | 战斗场景,31->火车大劫案solo  
key4 | wild_class | int | 123 | 1 | 地块类型,7.0.1马车pvp掠夺用副本内主城107  
key5 | report_type | int | 123 | 1 | 报告类型,7.0.1马车pvp掠夺用117  
key6 | report_json | json | {“xxx”:xxx} | 1 | 报告内容,根据report_type传不同内容  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_do_battle_with_npc&uid=12345678&key0={}&key1={}&key2=123&key3=123&key4=123&key5=123&key6={“xxx”:xxx}

  * **备注**


    
    
    attacker_info格式
    {
        "sheriff": {
            "preset_id": int,
        },
        "hero_list": [
            long, long, long
        ],
        "troop_list": {
            "long": long  // 兵id->兵数量
        },
        "global_buff": {
            "long": long // buff id->buff num
        }
    }
    // report_type: 117 时
    // report_json
    {
        "carriage_info":
        {
            "left_time": int, // 剩余可被掠夺次数
            "quality": int,   // 马车品质
        },
        "reward":[[xxx]] // 奖励
    }
    反包: svr_op_battle_result

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.1 | 新增接口  
  
* * *

#### 模拟战斗-战斗

  * **命令字** **_op_do_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | attacker_node | json | {} | 1 | 攻击方battle_node  
key1 | defender_node | json | {} | 1 | 防守方battle_node  
key2 | combat_type | int | 123 | 1 | 战斗类型,2->多回合solo1打1  
key3 | battle_type | int | 123 | 1 | 战斗场景,31->火车大劫案solo  
key4 | wild_class | int | 123 | 1 | 地块类型,7.0.1马车pvp掠夺用副本内主城107  
key5 | report_type | int | 123 | 1 | 报告类型,7.0.1马车pvp掠夺用117  
key6 | report_json | json | {“xxx”:xxx} | 1 | 报告内容,根据report_type传不同内容  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_do_battle&key0={}&key1={}&key2=123&key3=123&key4=123&key5=123&key6={“xxx”:xxx}

  * **备注**


    
    
    // report_type: 117 时
    // report_json
    {
        "carriage_info":
        {
            "left_time": int, // 剩余可被掠夺次数
            "quality": int,   // 马车品质
        },
        "reward":[[xxx]] // 奖励
    }
    反包: svr_op_battle_result

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.1 | 新增接口  
  
* * *

#### 模拟战斗-火车-生成战斗节点

  * **命令字** **_op_gen_battle_node_for_train_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 12345678 | 1 | 车头uid  
key0 | info | json | [{}] | 1 | 战斗信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_battle_node_for_train&uid=12345678&key0=[{}]

  * **备注**


    
    
    info格式
    [
        {
            "sheriff": {
                "preset_id": int,
            },
            "hero_list": [
                long, long, long
            ],
            "troop_list": {
                "long": long  // 兵id->兵数量
            },
            "global_buff": {
                "long": long // buff id->buff num
            }
            "need_fill": int // 0 不用填充 1 要填充
            "serial_num": int // 序列号，从1开始，传多少返回多少
        }
    ]
    
    反包: svr_op_battle_node_multi

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 模拟战斗-多轮次战斗

  * **命令字** **_op_do_battle_multi_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | attacker_node | json | [] | 1 | 攻击方battle_node,注意是array  
key1 | defender_node | json | [] | 1 | 防守方battle_node,注意是array  
key2 | combat_type | int | 123 | 1 | 战斗类型,2->多回合solo1打1  
key3 | battle_type | int | 123 | 1 | 战斗场景,31->火车大劫案solo  
key4 | wild_class | int | 123 | 1 | 地块类型  
key5 | report_type | int | 123 | 1 | 报告类型  
key6 | report_json | json | {“xxx”:xxx} | 1 | 报告内容,根据report_type传不同内容  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_do_battle_multi&key0=[]&key1=[]&key2=123&key3=123&key4=123&key5=123&key6={“xxx”:xxx}

  * **备注**


    
    
    // report_type: 117 时
    // report_json
    {
        "carriage_info":
        {
            "left_time": int, // 剩余可被掠夺次数
            "quality": int,   // 品质
        },
        "reward":[[xxx]] // 奖励
    }
    反包: svr_op_battle_result

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.73.水晶岛活动

* * *

#### 水晶岛活动-同步匹配结果

  * **命令字** **_op_hunt_event_send_match_result_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | match_result | json | {“xxx”:111} | 1 | 具体协议待定  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_hunt_event_send_match_result_all&Key0={“xxx”:111}

  * match_result格式


    
    
    {
        "event_id": string,   
        "time_zone_id": long, //时区id
    
        "wild_refresh":
        {
            "mine":     //水晶矿刷新配置
            {
                "stage_1":    //阶段1
                [
                    [
                        long,    //wild_id
                        long,    //num
                        long,   //生成水晶矿的最大圈数
                    ]
                ],
                "stage_2":    //阶段2
                [
                    [
                        long,    //wild_id
                        long,    //num
                        long,   //生成水晶矿的最大圈数
                    ]
                ],
                "outbreak_1":    //爆发式-阶段1
                [
                    [
                        long,   //stage 1之后x秒
                        long,   //wild_id
                        long,   //num
                        long,   //生成水晶矿的最大圈数
                    ]
                ],
                "outbreak_2":    //爆发式-阶段2
                [
                    [
                        long,   //stage 1之后x秒
                        long,   //wild_id
                        long,   //num
                        long,   //生成水晶矿的最大圈数
                    ]
                ],
                "outbreak_f": long, // 爆发式刷新预告间隔, 连续2次爆发式刷新间隔低于该值的属于同一轮次
            },
            "crystal":    //散落水晶刷新配置
            {
                "statue":   //神像周边
                [
                    long,    //wild_id
                    long,    //刷新周期
                    long,    //补充至N个
                    long,    //最多找N圈，N<=5      
                ],
                "island":   //水晶岛周边
                [
                    long,    //wild_id
                    long,    //刷新周期
                    long,    //补充至N个
                    long,    //最多找N圈，N<=5     
                ],
                "mine":     //水晶矿
                [
                    long,    //wild_id
                    long,    //战胜NPC后，即刻在该地形周围随机刷出X个
                    long,    //最多找N圈，N<=5 
                ]
            }
        }
    
        "match_succ":
        [
            {
                "battle": long,   //战场sid
                "team":           //本场小队列表
                [
                    team_id,
                    team_id
                ],
                "time_zone":
                [
                    long,   //开打时间戳，理论上和阶段1相同
                    long,   //结束时间戳
                    long,   //准备期时间戳
                    long,   //阶段1
                    long,   //阶段2
                    long,   //阶段3准备时间
                    long,   //阶段3
                    long,   //结算完成时间
                ],
                "statue_open_choose": long, // 随机数, 用于判断先开放哪两个神像
            }
        ],
        "match_fail":
        {
            "team":
            {
                "a":  //因小队数量小于x，所有小队轮空
                [
                    team_id,
                    team_id
                ],
                "b":  //因小队成员数量不足导致轮空
                [
                    team_id,
                    team_id
                ]
            },
            "end_time":long     //匹配失败结果展示到此时间
        },
        "wild_list":
        {
            "${wild_id}":
            [
                long,   //小队积分总量
                long,   //小队积分获取分数Z，列：200
                long,   //小队积分获取速度Y，列：30s
            ]
        },
        "occupy_rate": long, // 水晶矿积分掠夺比例
    }
    
    

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

#### 水晶岛活动-神像结算-小队

  * **命令字** **_op_hunt_event_building_balance_team_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | balance_result | json | {“xxx”:111} | 1 | 具体协议待定  
Key1 | battle_sid | long | 1 | 1 | 战场sid  
Key2 | statue_pos | long | 1 | 1 | 神像位置  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_hunt_event_building_balance_team&Key0={“xxx”:111}&Key1=1&Key2=1
    
    
    {
        "statue_id": long,
        "event_id": long,
        "user_rank": [
            {
                "rank": int,
                "uid": long,
                "team_id": long,
                "score": long, // 所获积分
                "kill_num": long,
                "lost_num": long,
                "rating": long, // 评分
                "uname": string,
                "avatar": long
            }
        ],
        "team_rank": [
            {
                "rank": long,
                "team_id": long,
                "team_nick": string,
                "team_name": string,
                "team_avatar": int,
                "score": long, // 所获积分
                "rating": long, // 评分
                "reward_buff":
                [
                    [id,num]
                ]
            }
        ]
    }

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

#### 水晶岛活动-神像结算-个人

  * **命令字** **_op_hunt_event_building_balance_personal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | balance_result | json | {“xxx”:111} | 1 | 具体协议待定  
Key1 | battle_sid | long | 1 | 1 | 战场sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_hunt_event_building_balance_personal&Key0={“xxx”:111}&Key1=1
    
    
    {
        "statue_id": long,
        "event_id": long,
        "user_rank": [
            {
                "rank": int,
                "uid": long,
                "score": long, // 所获积分
                "kill_num": long,
                "lost_num": long,
                "rating": long, // 评分
                "uname": string,
                "team_id": long
                "avatar": long
            }
        ]
    }

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
v5.6 | 优化需求-废弃  
  
* * *

#### 水晶岛活动-战场结算

  * **命令字** **_op_hunt_event_battle_field_balance_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | balance_result | json | {“xxx”:111} | 1 | 具体协议待定  
Key1 | battle_sid | long | 1 | 1 | 战场sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_hunt_event_battle_field_balance&Key0={“xxx”:111}&Key1=1

  * balance_result格式


    
    
    {
        "event_id": string, // 活动id
        "battle_id": int,   // 战场id
        "team_rank":   //本场次所有小队的积分排名
        [
            [
                long,   //rank
                long,   //team_id
                long,   //score
            ]
        ],
        "user_rank":   //本场次所有玩家的积分排名
        {
            "score_rank":   //个人积分排行
            [
                [
                    long,  //rank
                    long,  //uid
                    long,  //team_id
                    long,  //score
                    long,  //contribution
                    [      //得分明细
                        long,    //神像个人伤害排行榜
                        long,    //占领水晶矿
                        long,    //掠夺水晶矿
                        long,    //采集水晶
                        long,    //水晶岛占领时长
                    ]
                ]
            ],
            "occupy_island":   //水晶岛占领时长排行
            [
                [
                    long,  //rank
                    long,  //uid
                    long,  //team_id
                    long   //score
                ]
            ],
            "occupy_mine":   //水晶矿得分
            [
                //同occupy_1
            ],
            "occupy_statue":   //四神像得分
            [
                //同occupy_1
            ]
        },
        "show":   //四个榜的展示顺序
        [
            long, //rank type
            long, //rank type
            long, //rank type
            long  //rank type
        ]
    
    }
    

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

#### 水晶岛活动-首次移入战场前选兵

  * **命令字** **_hunt_first_send_event_army_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | epoch | int | 1 | 1 |   
Key1 | battle_id | int | 170001 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=hunt_first_send_event_army&Key0=1&Key1=170001

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

#### 水晶岛活动-使用宝石购买活动兵

  * **命令字** **_hunt_buy_event_army_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | troop_id | int | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=hunt_buy_event_army&Key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

### 7.74.水晶岛活动march

* * *

#### 水晶岛活动march-采集散落水晶

  * **命令字** **_hunt_event_scattered_crystal_occupy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | cost time | TUINT32 | 3 | 1 |   
Key1 | target pos | TUINT32 | 1310072 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=hunt_event_scattered_crystal_occupy&Key0=3&Key1=1310072

  * **改动历史**

版本号 | 说明  
---|---  
v5.6 | 新增接口  
  
* * *

### 7.75.水晶相关

* * *

#### 水晶相关-合成-水晶

  * **命令字** **_compose_crystal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id | TUINT32 | 2 | 1 |   
key1 | IsComposeAll | TUINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=compose_crystal&key0=2&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.20 | 新增接口  
  
* * *

#### 水晶相关-镶嵌水晶-水晶

  * **命令字** **_crystal_insert_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | TUINT64 | 2 | 1 |   
key1 | crystal_id | TUINT32 | 1 | 1 |   
key2 | pos | TUINT32 | 1 | 1 |   
key10 | equit_type | TINT64 | 1 | 0 | 后台自动生成-表示镶嵌的数值装备ID  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=crystal_insert&key0=2&key1=1&key2=1&key10=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.20 | 新增接口  
  
* * *

#### 水晶相关-拆除水晶-水晶

  * **命令字** **_crystal_remove_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | TUINT64 | 2 | 1 |   
key1 | pos | TUINT32 | 1 | 1 | 装备的第几个槽位  
key2 | item_id | TUINT32 | 1 | 0 | 有偿拆除必传  
key3 | price_type | TUINT32 | 1 | 1 | 0宝石-1忠诚度  
key4 | price_num | TINT64 | 1 | 1 | 传入表示购买并使用  
key10 | crystal_id | TINT64 | 1 | 0 | 后台自动生成-表示移除的数值水晶ID  
key11 | equit_type | TINT64 | 1 | 0 | 后台自动生成-表示移除的数值装备ID  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=crystal_remove&key0=2&key1=1&key2=1&key3=1&key4=1&key10=1&key11=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.20 | 新增接口  
  
* * *

#### 水晶相关-分解水晶-水晶

  * **命令字** **_decompose_crystal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | material id | TINT32 | 2 | 1 |   
key1 | decompose all | TINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=decompose_crystal&key0=2&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.20 | 新增接口  
  
* * *

#### 水晶相关-设置水晶预设-水晶

  * **命令字** **_set_crystal_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan id | TINT32 | 2 | 1 |   
key1 | crystal id | string | “1” | 1 |   
key2 | pos | TINT32 | 1 | 0 |   
key3 | type | TINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_crystal_plan&key0=2&key1=“1”&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
3.0.0 | 新增接口  
  
* * *

### 7.76.治安官

* * *

#### 治安官-改变玩家名字

  * **命令字** **_player_name_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | name | string | lalalal | 1 |   
key1 | 宝石消耗 | int64 | 1 | 1 | 不消耗传0  
key2 | 道具id | int32 | 1 | 1 | 不消耗传-1  
key3 | 消耗类型 | int32 | 1 | 1 | 0：道具、1：宝石  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=player_name_change&key0=lalalal&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.29 | 新增接口  
  
* * *

#### 治安官-改变基地名字

  * **命令字** **_player_name_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | name | string | lalalal | 1 |   
key1 | 宝石消耗 | int64 | 1 | 1 | 不消耗传0  
key2 | 道具id | int32 | 1 | 1 | 不消耗传-1  
key3 | 消耗类型 | int32 | 1 | 1 | 0：道具、1：宝石  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=player_name_change&key0=lalalal&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.29 | 新增接口  
  
* * *

#### 治安官-改变玩家国王形象

  * **命令字** **_player_avatar_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | avatar id | int32 | 1 | 1 |   
key1 | 消耗类型 | int32 | 1 | 1 | 0：消耗道具、1：消耗宝石  
key2 | 宝石数量 | int64 | 1 | 1 |   
key3 | 道具id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=player_avatar_change&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.29 | 新增接口  
  
* * *

#### 治安官-改变玩家龙名字

  * **命令字** **_dragon_name_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | name | string | lalalla | 1 |   
key1 | 宝石数量 | int64 | 1 | 1 | 不消耗传0  
key2 | 道具id | int32 | 1 | 1 | 不消耗传-1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_name_change&key0=lalalla&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.36 | 新增接口  
  
* * *

#### 治安官-治安官专属技能加点

  * **命令字** **_dragon_grade_skill_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skill_info | string | 1:10,2:10 | 1 | id:lv,id:lv,id:lv  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_grade_skill_upgrade&key0=1:10,2:10

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

#### 治安官-治安官专属技能重置

  * **命令字** **_dragon_grade_skill_reset_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 消耗类型 | int32 | 1 | 1 | 0：消耗道具、1：消耗宝石  
key1 | 宝石数量 | int64 | 1 | 1 |   
key2 | 道具id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_grade_skill_reset&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

#### 治安官-升级龙技能

  * **命令字** **_dragon_skill_upgrade_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skill_list | string | 1:10,2:10 | 1 | id:lv,id:lv  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_skill_upgrade_new&key0=1:10,2:10

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.30 | 新增接口  
  
* * *

#### 治安官-重置龙技能点数

  * **命令字** **_dragon_skill_reset_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 消耗类型 | int32 | 1 | 1 | 0：消耗道具、1：消耗宝石  
key1 | 宝石数量 | int64 | 1 | 1 |   
key2 | 道具id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_skill_reset&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.30 | 新增接口  
  
* * *

#### 治安官-升级龙怪物技能

  * **命令字** **_dragon_monster_skill_upgrade_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skill_list | string | 1:10,2:10 | 1 | id:lv,id:lv  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_monster_skill_upgrade_new&key0=1:10,2:10

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.30 | 新增接口  
  
* * *

#### 治安官-重置龙怪物技能点数

  * **命令字** **_dragon_monster_skill_reset_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 消耗类型 | int32 | 1 | 1 | 0：消耗道具、1：消耗宝石  
key1 | 宝石数量 | int64 | 1 | 1 |   
key2 | 道具id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_monster_skill_reset&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.30 | 新增接口  
  
* * *

#### 治安官-治安官升级

  * **命令字** **_dragon_level_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dragon_level_up_quest_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_level_up&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.36 | 新增接口  
  
* * *

#### 治安官-拉取玩家信息

  * **命令字** **_player_info_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int32 | 1 | 1 |   
key1 | sid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=player_info_get&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.100 | 新增接口  
  
* * *

#### 治安官-获取自定义头像

  * **命令字** **_get_lord_image_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id or chest_id | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_lord_image&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 治安官-治安官阶级提升

  * **命令字** **_dragon_grade_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | quest_id | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_grade_up&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

### 7.77.治安官preset

* * *

#### 治安官preset-设计方案名字

  * **命令字** **_set_dragon_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 12 | 1 | (从1开始)  
key1 | plan_name | string | xxxxxx | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_dragon_plan_name&key0=12&key1=xxxxxx

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

#### 治安官preset-设置方案装备

  * **命令字** **_set_dragon_plan_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id(从1开始) | int32 | 1 | 1 |   
key1 | equip_id | int64 | 123 | 1 |   
key2 | equip_pos | int32 | 123 | 1 |   
key3 | type(0: 穿 1:脱) | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_dragon_plan_equip&key0=1&key1=123&key2=123&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

#### 治安官preset-设置方案技能

  * **命令字** **_set_dragon_plan_skill_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | (从1开始)  
key1 | skill_type | int64 | 1 | 1 | (0: dragon_skill 1: monster_skill 2: grade_skill)  
key2 | skill_list | string | 1:2,3:4 | 1 | (id:lv,id:lv)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_dragon_plan_skill&key0=1&key1=1&key2=1:2,3:4

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

#### 治安官preset-重置方案技能

  * **命令字** **_reset_dragon_plan_skill_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | (从1开始)  
key1 | skill_type | int32 | 1 | 1 | (0: hero_skill 1: monster_skill 2: grade_skill)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_dragon_plan_skill&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

#### 治安官preset-切换方案

  * **命令字** **_change_dragon_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 123 | 1 | (从1开始)  
key1 | gem cost | int64 | 123 | 1 |   
key2 | item id | int32 | 123 | 1 |   
key3 | cost type | int32 | 123 | 1 | 1-gem 2-item  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_dragon_plan&key0=123&key1=123&key2=123&key3=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

#### 治安官preset-重置治安官预设

  * **命令字** **_reset_dragon_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_dragon_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

### 7.78.治安官被抓

* * *

#### 治安官被抓-复活龙

  * **命令字** **_dragon_revive_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | gem cost | int64 | 0 | 1 | (消耗道具则传0)  
key1 | item id | int32 | 123 | 1 | (消耗宝石则传-1)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_revive&key0=0&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 治安官被抓-主动释放抓捕的龙

  * **命令字** **_dragon_release_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_release&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 治安官被抓-处决龙

  * **命令字** **_dragon_kill_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | gem cost | int64 | 0 | 1 | (消耗道具则传0)  
key2 | item id | int32 | 123 | 1 | (消耗宝石则传-1)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_kill&key0=123&key1=0&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 治安官被抓-地图上的监狱信息

  * **命令字** **_prison_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | map pos | int32 | 1230123 | 1 |   
key2 | target sid | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=prison_info&key0=123&key1=1230123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.1 | 新增接口  
  
* * *

#### 治安官被抓-龙自杀

  * **命令字** **_dragon_suicide_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | gem_cost | int64 | 123 | 1 | 免费自杀传0  
key1 | item_id | int32 | 123 | 1 |   
key2 | item_num | int32 | 123 | 1 | 免费自杀传0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_suicide&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 治安官被抓-大赦天下

  * **命令字** **_launch_amnesty_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=launch_amnesty&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.0 | 新增接口  
  
* * *

#### 治安官被抓-一键放龙

  * **命令字** **_release_all_dragon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid |  |  | 1000455 |  |   
uid |  |  | 1000455 |  |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=release_all_dragon&uid=1000455&uid=1000455

  * **改动历史**

版本号 | 说明  
---|---  
v4.8.1 | 新增接口  
  
* * *

#### 治安官被抓-拉龙处决历史

  * **命令字** **_get_dragon_kill_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_dragon_kill_history&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v6.9 | 新增接口  
  
* * *

### 7.79.活动医院

* * *

#### 活动医院-一键治疗所有军队-免费治疗

  * **命令字** **_event_hosptal_revive_all_army_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动医院的event id | string | 127_168828939934_1_0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=event_hosptal_revive_all_army&key0=127_168828939934_1_0

  * **改动历史**

版本号 | 说明  
---|---  
v4.4 | 新增接口  
v5.1 | 活动医院逻辑改动，修改部分代码  
  
* * *

### 7.80.活动发奖

* * *

#### 活动发奖-活动—增加奖励

  * **命令字** **_op_add_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 1 | 1 | 0:goal 1:rank  
key3 | goal_num or rank_num | int32 | 1 | 1 | depends on key2  
key4 | score | int64 | 1 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | Cowboy_QYR:Oko:Marrrr | 1 | first at one,use “:” to divide and available when key2=1  
key6 | rank svr_id in order list | string | 1:1:1 | 1 | first at one,use “:” to divide and available when key2=1, each to key4  
key7 | event_score in order list | string | 1:1:1 | 1 |   
key8 | {“e_t”://活动结束时间, “e_id”://活动id } | string | {“e_t”:1678881599,“e_id”:16788711001} | 1 |   
key9 | window_option | int32 | 1 | 1 | 弹窗设置（0：城内城外弹窗 1：只在城内弹窗）  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_reward_list&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=1&key3=1&key4=1&key5=Cowboy_QYR:Oko:Marrrr&key6=1:1:1&key7=1:1:1&key8={“e_t”:1678881599,“e_id”:16788711001}&key9=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.40 | 新增接口  
  
* * *

#### 活动发奖-活动—增加联盟礼物

  * **命令字** **_op_add_al_reward_list_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 1 | 1 | 0:goal 1:rank  
key5 | alid | int32 | 1001 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_al_reward_list_new&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=1&key5=1001

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.40 | 新增接口  
  
* * *

#### 活动发奖-主题活动—增加个人奖励

  * **命令字** **_op_add_theme_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 | 个人主题活动:999联盟主题活动: 1000 kvk活动后台定为1001  
key2 | reward_type | int32 | 1 | 1 | 0:goal 1:rank  
key3 | goal_num or rank_num | int32 | 1 | 1 | depends on key2  
key4 | score | int64 | 1 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | Cowboy_QYR:Oko:Marrrr | 1 |   
key6 | rank svr_id in order list | string | 1:2:3 | 1 |   
key7 | score_list | string | 1 | 1 |   
key8 | event_info | string | 1 | 1 |   
key9 | window_option | int32 | 1 | 1 | 弹窗设置（0：城内城外弹窗 1：只在城内弹窗）  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_theme_reward_list&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=1&key3=1&key4=1&key5=Cowboy_QYR:Oko:Marrrr&key6=1:2:3&key7=1&key8=1&key9=1

  * **备注**



> key8={“e_t”://活动结束时间, “e_id”://活动id, “kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.40 | 新增接口  
  
* * *

#### 活动发奖-主题活动—增加联盟奖励

  * **命令字** **_op_add_theme_al_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | 1 | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 取自数值reward.json协议  
key2 | reward_type | int32 | 1 | 1 | 0:goal 1:rank  
key5 | alid | int32 | 1 | 1 |   
key6 | rank alname in order list | string | Cowboy_QYR:Oko:Marrrr | 1 |   
key7 | rank svr_id in order list | string | 1:2:3 | 1 |   
key8 | score_list | string | 1:2 | 1 |   
key9 | event_info | string | 11221_215 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_theme_al_reward_list&key0=1&key2=1&key5=1&key6=Cowboy_QYR:Oko:Marrrr&key7=1:2:3&key8=1:2&key9=11221_215

  * 备注



> key9={“e_t”://活动结束时间, “e_id”://活动id, “kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.40 | 新增接口  
  
* * *

#### 活动发奖-联盟主题活动—增加联盟奖励

  * **命令字** **_op_add_alliance_theme_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key2 | reward_type | int32 | 0 | 1 | (0:goal 1:rank)  
key3 | goal_num or rank_num | int32 | 1 | 1 |   
key4 | score | int64 | 1 | 111 | 该活动的分数  
key5 | alid | int32 | 11 | 1 |   
key6 | rank alname in order list | string | Cowboy_QYR:Oko:Marrrr | 1 |   
key7 | rank svr_id in order list | string | 1:2:3 | 1 |   
key8 | score_list | string | 1:2:3 | 1 |   
key9 | event_info | string |  | 1 |   
key10 | window_option | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_alliance_theme_reward_list&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key2=0&key3=1&key4=1&key5=11&key6=Cowboy_QYR:Oko:Marrrr&key7=1:2:3&key8=1:2:3&key9=&key10=1

  * **备注**



> key9={“e_t”://活动结束时间, “e_id”://活动id, “kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.40 | 新增接口  
  
* * *

#### 活动发奖-充值活动个人充值累积&全服充值累积&首充发放奖励

  * **命令字** **_op_add_recharge_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward(奖励列表) | string | 1:2:3,4:5:6 | 1 |   
key1 | event_type | int32 | 1 | 1 | (首充/个人累积/全服累积)  
key2 | num | int32 | 1 | 1 | 达成的目标,个人累积时代表奖励level  
key3 | score(积分) | int64 | 1 | 1 |   
key4 | score_list | string | 1:2 | 1 |   
key5 | window_opt | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_recharge_reward&key0=1:2:3,4:5:6&key1=1&key2=1&key3=1&key4=1:2&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.40 | 新增接口  
  
* * *

#### 活动发奖-运营给玩家发奖-普通

  * **命令字** **_operate_add_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | 1:2:3,4:5:6 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_add_reward&key0=1:2:3,4:5:6

  * **备注**



> 推uidrefresh，发奖，没有其他操作，目前只有联盟日常活动任务发奖

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 活动发奖-运营给联盟发奖-发放联盟皮肤

  * **命令字** **_operate_add_al_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
aid | aid | int64 | 123456 | 1 | 联盟  
key0 | reward | string | [{“a”:[136,skin_id,90*86400]}] | 1 | 取自数值reward.json协议只能给联盟皮肤  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_add_al_reward&aid=123456&key0=[{“a”:[136,skin_id,90*86400]}]

  * **备注**



> 没有推送发奖，需配合邮件通知使用，目前只有ava联赛 联盟建筑皮肤奖励

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 活动发奖-运营给玩家发奖-邮件

  * **命令字** **_operate_event_add_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 0 | 1 | 0:goal 1:rank 2:联盟贡献度 3:个人主题活动的联盟目标  
key3 | goal_num or rank_num | int32 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key9 | window_option | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
key12 | 跳转方式 | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_reward&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=0&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key9=1&key12=0

  * **备注**



> 推uidrefresh，发奖，根据活动类型有其他弹窗&邮件之类的额外操作，例如充值活动发奖  
>  key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 活动发奖-运营给联盟发奖

  * **命令字** **_operate_event_add_al_gift_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 1 | 1 | 0:goal 1:rank 2:贡献度 3:个人主题活动的联盟目标  
key3 | goal_num or rank_num | int32 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key9 | window_option | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
key10 | alid | int64 | 111 | 1 | 发给的联盟id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_al_gift&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=1&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key9=1&key10=111

  * **备注**



> 推aidrefresh，发联盟礼物，例如联盟日常活动发联盟礼物  
>  key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 活动发奖-给联盟发奖（邮件）

  * **命令字** **_operate_event_add_al_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 0 | 1 | 0:goal 1:rank 2:贡献度 3:个人主题活动的联盟目标联盟礼物 4:个人主题活动的联盟目标普通奖励  
key3 | goal_num or rank_num | int64 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key9 | window_option | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
key10 | alid | int64 | 111 | 1 | 发给的联盟id  
key12 | extraInfo | string |  | 1 |   
key14 | 跳转方式 | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_al_reward&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=0&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key9=1&key10=111&key12=&key14=0

  * **备注**



> key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 活动发奖-(超级王座)给sid发奖

  * **命令字** **_operate_event_add_svr_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 0 | 1 | 0:goal 1:rank 2:贡献度 3:个人主题活动的联盟目标  
key3 | goal_num or rank_num | int64 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key10 | sid | int64 | 1 | 1 | 发给svr id  
key12 | 跳转方式 | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_svr_reward&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=0&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key10=1&key12=0

  * **备注**



> 活动调用  
>  key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 活动发奖-(超级王座)发奖 //活动调用，buff

  * **命令字** **_op_set_skvk_svr_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 1112_4154 | 1 |   
key1 | sid | int64 | 111 | 1 |   
key2 | type | int32 | 0 | 1 | 0:全国动员 1:战备竞赛 2:步兵攻击榜 3:远程兵攻击榜 4:骑兵攻击榜 5:银榜  
key3 | lv | int64 | 111 | 1 |   
key4 | is_op | int32 | 0 | 1 | 0：不可降级 1：可降级 活动固定传0  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_skvk_svr_buff&key0=1112_4154&key1=111&key2=0&key3=111&key4=0

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 活动发奖-(超级王座)发奖 //活动调用，批量buff

  * **命令字** **_op_sync_skvk_encourage_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 121_44545 | 1 |   
key1 | sid_list | string |  | 1 | {“sid”:rank,”sid”:rank}  
key2 | type | int32 | 2 | 1 | 2:步兵攻击榜 3:远程兵攻击榜 4:骑兵攻击榜 5:银榜  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_sync_skvk_encourage_buff&key0=121_44545&key1=&key2=2

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 活动发奖-运营给玩家发奖-支持docid

  * **命令字** **_operate_event_add_reward_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
common_event_reward | 发奖励时玩家是否判定玩家在奖励服 | int32 | 1 | 1 | 结合key8的sid_list使用  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 0 | 1 | 0:goal 1:rank 2:联盟贡献度 3:个人主题活动的联盟目标  
key3 | goal_num or rank_num | int32 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key9 | window_option | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
key10 | doc_id | int32 | 1 | 1 | 邮件id  
key12 | 跳转方式 | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_reward_new&common_event_reward=1&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=0&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key9=1&key10=1&key12=0

  * **备注**



> 推uidrefresh，发奖，根据活动类型有其他弹窗&邮件之类的额外操作，例如充值活动发奖  
>  key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}  
>  参数如果传了common_event_reward=1就会校验发奖时,玩家当前所属国籍在不在传过来的sid_list中不在就会报错不会发奖励，还有就是如果传rank_sid!=-1也会校验这个rank_sid是不是等于玩家所属国籍

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 补充接口  
  
* * *

#### 活动发奖-给联盟发奖-支持doc id

  * **命令字** **_operate_event_add_al_reward_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 0 | 1 | 0:goal 1:rank 2:贡献度 3:个人主题活动的联盟目标联盟礼物 4:个人主题活动的联盟目标普通奖励  
key3 | goal_num or rank_num | int64 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key9 | window_option | int32 | 1 | 1 | 0：城内城外弹窗 1：只在城内弹窗  
key10 | alid | int64 | 111 | 1 | 发给的联盟id  
key11 | ExceptUid | string | 11,22,33 | 1 | 被排除在外的uid  
key12 | extraInfo | string |  | 1 |   
key13 | doc_id | int32 | 1 | 1 | 邮件id  
key14 | 跳转方式 | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_al_reward_new&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=0&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key9=1&key10=111&key11=11,22,33&key12=&key13=1&key14=0

  * **备注**



> key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}  
>  会校验是否在联盟 玩家退出联盟 就收不到联盟奖励了

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 补充接口  
  
* * *

#### 活动发奖-给sid发奖-支持docid

  * **命令字** **_operate_event_add_svr_reward_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key1 | event_type | int32 | 1 | 1 |   
key2 | reward_type | int32 | 0 | 1 | 0:goal 1:rank 2:贡献度 3:个人主题活动的联盟目标  
key3 | goal_num or rank_num | int64 | 1 | 1 | depends on key2  
key4 | score | int64 | 12 | 1 | 玩家该活动的分数  
key5 | rank uname in order list | string | adsad:sdsd | 1 |   
key6 | rank svr_id in order list | string | 1:2 | 1 |   
key7 | event_score in order list | string | 1:2 | 1 |   
key8 | event_info | string |  | 1 |   
key10 | sid | int64 | 1 | 1 | 发给svr id  
key11 | doc_id | int32 | 1 | 1 | 邮件id  
key12 | 跳转方式 | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_event_add_svr_reward_new&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key1=1&key2=0&key3=1&key4=12&key5=adsad:sdsd&key6=1:2&key7=1:2&key8=&key10=1&key11=1&key12=0

  * **备注**



> 活动调用 key8={“e_t”://活动结束时间, “e_id”://活动id ,“kingdoms”: //是否跨服, “event_ui”:活动label ui id, “localization”://活动标题}

  * **改动历史**

版本号 | 说明  
---|---  
v6.2.0 | 新增接口  
  
* * *

#### 活动发奖-活动—通用追加奖励

  * **命令字** **_op_add_new_globalres_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_new_globalres&key0=[{“a”:[1,0,200]},{“a”:[0,12,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

### 7.81.活动相关

* * *

#### 活动相关-活动领goal奖励

  * **命令字** **_claim_event_center_goal_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168828939934_1_0 | 1 |   
key1 | goal num | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_event_center_goal_reward&key0=127_168828939934_1_0&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

#### 活动相关-付费领奖

  * **命令字** **_claim_statistics_event_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动type | int32 | 1 | 1 |   
key1 | 活动id | string | 127_168828939934_1_0 | 1 |   
key2 | task_id | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_statistics_event_reward&key0=1&key1=127_168828939934_1_0&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

#### 活动相关-领取积分型goal奖

  * **命令字** **_common_event_claim_goal_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动type | TINT64 | 127 | 1 |   
key1 | 活动id | string | 127_168828939934_1_0 | 1 |   
key2 | goal id | TINT64 | 1 | 1 |   
key3 | type | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=common_event_claim_goal&key0=127&key1=127_168828939934_1_0&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.6 | 新增接口  
  
* * *

#### 活动相关-道具转化

  * **命令字** **_item_transform_op_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168828939934_1_0 | 1 |   
key1 | 道具消耗 | [[int64,int64,int64],[int64,int64,int64]] | [[1,0,1]] | 1 |   
key2 | exp | TINT64 | 1 | 1 |   
key3 | 经验暴击倍数 | [[int32,int32],[int32,int32] …] | [[1,1],[2,2]] | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_transform_op&key0=127_168828939934_1_0&key1=[[1,0,1]]&key2=1&key3=[[1,1],[2,2]]

  * **改动历史**

版本号 | 说明  
---|---  
v4.8 | 新增接口  
  
* * *

#### 活动相关-领取宝箱

  * **命令字** **_item_transform_claim_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168828939934_1_0 | 1 |   
key1 | idx | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_transform_claim_chest&key0=127_168828939934_1_0&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.6 | 新增接口  
  
* * *

#### 活动相关-联盟付费赠礼活动

  * **命令字** **_item_transform_claim_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | string | 127_168828939934_1_0 | 1 |   
key1 | uid | TINT64 | 1036198 | 1 |   
key2 | 礼物id | TINT64 | 1 | 1 |   
key3 | 礼物数量 | TINT64 | 999 | 0 | 弃用，数量默认为1  
key4 | 赠送礼物文本内容 | string | 送礼了还不说声谢谢？ | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_transform_claim_chest&key0=127_168828939934_1_0&key1=1036198&key2=1&key3=999&key4=送礼了还不说声谢谢？

  * **改动历史**

版本号 | 说明  
---|---  
v4.8 | 新增接口  
  
* * *

#### 活动相关-活动赠送分

  * **命令字** **_send_event_score_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int32 | 1 | 1 |   
key1 | score | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=send_event_score&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.38 | 新增接口  
  
* * *

#### 活动相关-活动补分(运营补分专用)

  * **命令字** **_op_add_score_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | score_type | int32 | 1 | 1 |   
key1 | score_id_list | string | 1:2:3 | 1 | 以:分隔  
key2 | score_list | string | 1:445:221 | 1 | 以:分隔  
key3 | op_time | int64 | 145415 | 1 | 时间戳  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_score&key0=1&key1=1:2:3&key2=1:445:221&key3=145415

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.38 | 新增接口  
  
* * *

#### 活动相关-一键领取小镇任务奖励

  * **命令字** **_claim_all_finished_game_quest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_all_finished_game_quest

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 活动相关-治安官等级提升批量领奖

  * **命令字** **_dragon_level_up_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | from | int32 | 1 | 1 | 想要领取的治安官等级奖励的起始等级  
key1 | to | int32 | 5 | 1 | 想要领取的治安官等级奖励的截止等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_level_up_batch&key0=1&key1=5

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 活动相关-治安官天赋等级提升批量领奖

  * **命令字** **_dragon_grade_up_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | from | int32 | 1 | 1 | 想要领取的治安官天赋奖励的起始quest_id  
key1 | to | int32 | 5 | 1 | 想要领取的治安官天赋奖励的最后quest_id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_grade_up_batch&key0=1&key1=5

  * **改动历史**

版本号 | 说明  
---|---  
v6.1 | 新增接口  
  
* * *

#### 活动相关-带联盟校验的透传

  * **命令字** **_new_op_forwarding_al_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_cmd | string | get_event_data | 1 | 具体见备注  
key1 | param | json | {} | 1 | 具体见备注  
key2 | aid | int | 1 | 1 | 客户端本地数据所在aid，与后台数据不一致时报错  
key3 | check uid list | long,long | 1,1,1 | 1 | 需要校验这些uid是不是在本联盟，如果不需要就传空  
key4 | is manager | int | 1 | 1 | 是否要校验职位，0：不需要，1：需要  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_forwarding_al&key0=get_event_data&key1={}&key2=1&key3=1,1,1&key4=1

  * **备注**



> 和new_op_transparent_transmission一样的用法  
>  反包中没有数据，活动把数据推送给客户端

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

#### 活动相关-带消耗的透传

  * **命令字** **_new_op_forwarding_with_cost_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_cmd | string | get_event_data | 1 | 具体见备注  
key1 | param | json | {} | 1 | 具体见备注  
key2 | cost | [{“a”:[int,int,int]}] | [{“a”:[int,int,int]}] | 1 | 消耗列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_forwarding_with_cost&key0=get_event_data&key1={}&key2=[{“a”:[int,int,int]}]

  * **备注**



> 和new_op_transparent_transmission一样的用法  
>  反包中没有数据，活动把数据推送给客户端

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.1 | 新增接口  
  
* * *

### 7.82.活动领奖相关

* * *

#### 活动领奖相关-活动领奖

  * **命令字** **_new_op_claim_goal_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int64 | 1 | 1 | 活动类型  
key1 | event_id | string | 1 | 1 | 活动id  
key2 | extra | string | 1 | 1 | 扩展字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_claim_goal_reward&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.0.0 | 新增接口  
  
* * *

#### 活动领奖相关-带消耗的活动活动领奖

  * **命令字** **_new_op_claim_goal_reward_with_cost_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int64 | 1 | 1 | 活动类型  
key1 | event_id | string | 1 | 1 | 活动id  
key2 | extra | string | 1 | 1 | 扩展字段  
key3 | 所需消耗资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_claim_goal_reward_with_cost&key0=1&key1=1&key2=1&key3=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 活动领奖相关-活动领奖-透传客户端领奖cmd

  * **命令字** **_new_op_tt_claim_goal_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int64 | 1 | 1 | 活动类型  
key1 | event_id | string | 1 | 1 | 活动id  
key2 | extra | string | 1 | 1 | 扩展字段  
key3 | cmd | string | 1 | 1 | 扩展字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_tt_claim_goal_reward&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

#### 活动领奖相关-活动领奖-领取活动特殊奖励

  * **命令字** **_new_op_tt_claim_special_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int64 | 1 | 1 | 活动类型  
key1 | event_id | string | 1 | 1 | 活动id  
key2 | extra | string | 1 | 1 | 扩展字段  
key3 | cmd | string | 1 | 1 | 扩展字段  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_tt_claim_special_reward&key0=1&key1=1&key2=1&key3=1

> 特殊活动领奖: 目前用于领取战斗军备物资

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

### 7.83.消息相关

* * *

#### 消息相关-拉取消息

  * **命令字** **_msg_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | need_update | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=msg_get&key0=1

  * **备注**



> tips，广播等  
>  rsp_type: msg_json,收到 svr_msg_get_flag时主动发起此请求

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.100 | 新增接口  
  
* * *

#### 消息相关-发送tips

  * **命令字** **_op_add_tips_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int32 | 121 | 1 | 目标uid  
key1 | tips_type | int32 | 1 | 1 | battle_pass升级tips传128  
key2 | intkey0 | int64 | 1 | 1 | battle_pass升级传tips中显示的等级  
key3 | intkey1 | int64 | 1 | 1 |   
key4 | intkey2 | int64 | 1 | 1 |   
key5 | strkey0 | string | we | 1 |   
key6 | strkey1 | string | wwe | 1 |   
key7 | strkey2 | string | ew | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_tips&key0=121&key1=1&key2=1&key3=1&key4=1&key5=we&key6=wwe&key7=ew

  * **备注** > 对于接口传递来说, 给客户端反包(key2&key3&key4&key5&key6&key7)拼接都是一个字符串, 分隔符是&，接受的拼接格式是6个字段  
> 前3个字段(key2,key3,key4)是int, 没有就按0值传递, 后三个字段(key5,key6,key7)是string, 没有就按照空字符串传递

  * **改动历史**


版本号 | 说明  
---|---  
v1.6 | 新增接口  
  
* * *

### 7.84.满意度调研

* * *

#### 满意度调研-问卷提交

  * **命令字** **_submit_satisfaction_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key1 | is_mark | int32 | 1 | 1 | 是否标记玩家  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=submit_satisfaction&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

#### 满意度调研-领取问卷奖励

  * **命令字** **_claim_satisfaction_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_satisfaction

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

#### 满意度调研-领取问卷rating奖励

  * **命令字** **_collect_auto_rating_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=collect_auto_rating_reward

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.0 | 新增接口  
  
* * *

### 7.85.特殊资源

* * *

#### 特殊资源-运输特殊资源

  * **命令字** **_transport_sp_rss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 花费时间 | TUINT32 | 34 | 1 |   
key1 | 目标位置 | TUINT32 | 2500600 | 1 |   
key2 | 要运输的特殊资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key3 | 税 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=transport_sp_rss&key0=34&key1=2500600&key2=[{“a”:[1,0,1000]}]&key3=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v4.8.1 | 新增接口  
  
* * *

#### 特殊资源-领取特殊资源

  * **命令字** **_claim_sp_rss_from_building_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 特殊资源id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_sp_rss_from_building&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.8.1 | 新增接口  
  
* * *

#### 特殊资源-切换特殊资源生产

  * **命令字** **_swap_building_buff_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | buff_idx | TINT64 | 1 | 1 |   
key1 | 建筑id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=swap_building_buff&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.8.1 | 新增接口  
  
* * *

#### 特殊资源-联盟请求特殊资源

  * **命令字** **_al_assist_send_sp_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 帮助类型 | TINT64 | 1 | 1 |   
key1 | 特殊资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key2 | 主城位置 | TINT64 | 2500600 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_assist_send_sp&key0=1&key1=[{“a”:[1,0,1000]}]&key2=2500600

  * **改动历史**

版本号 | 说明  
---|---  
v4.8.1 | 新增接口  
  
* * *

### 7.86.猎熊行动

* * *

#### 猎熊行动-猎熊行动 联盟建筑开启陷阱

  * **命令字** **_bear_hunt_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
no_event | 0-正常 1-跳过 | TINT64 | TINT64 | 1 | 造假flag  
Key0 | event_type | TINT64 | TINT64 | 1 | 活动type  
Key1 | event_id | string | event_xxxxx | 1 | 活动id  
Key2 | target_pos | TINT64 | 2500600 | 1 | 目标位置  
Key3 | op_type | TINT64 | 1 | 1-开启 2-预约开启 3-修改开启时间 4-取消预约开启 | 开启方式  
key4 | jsn_param | string | 123 | 1 | {“open_time”:开启时间戳, “buff_idx”: -1随机模式, 其他为buff_idx}  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=bear_hunt_open&no_event=TINT64&Key0=TINT64&Key1=event_xxxxx&Key2=2500600&Key3=1&key4=123

> 流程: 1. 通过后台透传开启者数据给运营, 运营进行校验确认符合活动开启条件 2. 运营开发返给带给后台一些必要的活动数据反包 后台拿到后进行陷阱校验 3. 后台拉取到联盟建筑数据 符合开启条件后 进行陷阱数据设定 并同步给回运营开启成功请求 4. 客户端拿到错误码来判定是否开启成功 0-成功后造假数据 1-失败 原数据不变化

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 猎熊行动-猎熊行动 陷阱捐献

  * **命令字** **_bear_hunt_donate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
no_event | 0-正常 1-跳过 | TINT64 | TINT64 | 1 | 造假flag  
Key0 | event_type | TINT64 | TINT64 | 1 | 活动type  
Key1 | event_id | string | event_xxxxx | 1 | 活动id  
Key2 | target_pos | TINT64 | 2500600 | 1 | 目标位置  
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=bear_hunt_donate&no_event=TINT64&Key0=TINT64&Key1=event_xxxxx&Key2=2500600&key2=[{“a”:[1,0,1000]}]

> 流程: 1. 通过后台透传陷阱数据给运营, 运营进行校验是否符合捐献条件 并计算是否可以升级 2. 运营开发返给带给后台一些必要的活动数据反包 后台拿到后进行陷阱数据的处理变更 3. 对地块需要进行推包保证没有问题 4. 客户端拿到错误码来判定是否捐献成功 0-成功后造假数据 1-失败 原数据不变化

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 猎熊行动-团战陷阱

  * **命令字** **_map_building_rally_bear_hunt_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | udwCostTime | TUINT32 | 30 | 1 |   
Key1 | udwTargetPos | TUINT32 | 1310072 | 1 |   
Key2 | strTroopList | string | “1:4000:233:4000” | 1 | :分隔,位数代表兵种ID  
Key3 | isSheriffJoin | bool | 1 | 1 |   
Key4 | strHeroList | string | “1,3,3,5” | 1 | ,分隔  
Key5 | udwBuildingType | TUINT32 | 1 | 1 |   
Key6 | udwPrepareTime | TUINT32 | 20 | 1 |   
Key7 | udwQuickSend | TUINT32 | 1 | 0 | 是否在满员时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_rally_bear_hunt&Key0=30&Key1=1310072&Key2=“1:4000:233:4000”&Key3=1&Key4=“1,3,3,5”&Key5=1&Key6=20&Key7=1&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 猎熊行动-支援建筑

  * **命令字** **_map_building_reinforce_bear_hunt_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_num | 当前已用槽位 | TINT64 | 20 | 1 | 1  
Key0 | udwCostTime | TUINT32 | 30 | 1 |   
Key1 | udwTargetPos | TUINT32 | 1310071 | 1 |   
Key2 | strTroopList | string | “1:4000:222:4000” | 1 | :分隔,位数代表兵种ID  
Key3 | rally_war_id | TINT64 | 33 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_reinforce_bear_hunt&rf_troop_num=900000&rf_slot_num=20&Key0=30&Key1=1310071&Key2=“1:4000:222:4000”&Key3=33

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.87.王座

* * *

#### 王座-设置王座税收强度

  * **命令字** **_throne_tax_set_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | val | int32 | 123 | 1 | 税收强度  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_tax_set&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座-取王座信息

  * **命令字** **_get_throne_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | throne pos | int32 | 1230123 | 1 |   
key1 | sid | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_throne_info&key0=1230123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座-放弃王座

  * **命令字** **_throne_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_abandon

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座-设置王座公告

  * **命令字** **_change_kingdom_notice_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | notice | string | xxxxxx | 1 |   
key1 | mail | string | xxxxxx | 0 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_kingdom_notice&key0=xxxxxx&key1=xxxxxx

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座-使用国王技能

  * **命令字** **_use_kingdom_skill_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 1 | 1 |   
key1 | skill_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=use_kingdom_skill&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 王座-获取国王使用技能历史记录

  * **命令字** **_get_kingdom_use_skill_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kingdom_use_skill_history&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 王座-给服务器添加奖励-王座皮肤

  * **命令字** **_op_add_reward_throne_skin_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 1 | 1 | 服务器  
key1 | skin_id | int32 | 1 | 1 | 皮肤ID  
key2 | add_time | int64 | 1 | 1 | 皮肤有效持续时间 -1表示永久  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_add_reward_throne_skin&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.5 | 新增接口  
  
* * *

#### 王座-获取服务器皮肤列表

  * **命令字** **_get_svr_skin_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_svr_skin_list

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.5 | 新增接口  
  
* * *

### 7.88.王座march

* * *

#### 王座march-攻击王座

  * **命令字** **_throne_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | TINT32 | 123 | 1 |   
key1 | target pos | TINT32 | 1230123 | 1 |   
key2 | troop list | string | “123:123:123:123” | 1 | :分隔  
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | “1,2,3,4,5” | 1 | ，分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_attack&key0=123&key1=1230123&key2=“123:123:123:123”&key3=1&key4=“1,2,3,4,5”

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座march-rally_war throne

  * **命令字** **_throne_rally_war_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | TINT32 | 123 | 1 |   
key1 | prepare time | TINT32 | 123 | 1 |   
key2 | target pos | TINT32 | 1230123 | 1 |   
key3 | troop list | string | “1:332:322:234” | 1 | :分隔  
key4 | if general join | bool | 1 | 1 |   
key5 | card_list | string | “1,2,3,4,5” | 1 | ，分隔  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_rally_war&key0=123&key1=123&key2=1230123&key3=“1:332:322:234”&key4=1&key5=“1,2,3,4,5”&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座march-reinforce throne

  * **命令字** **_throne_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_num | 当前已用槽位 | TINT64 | 20 | 1 | 1  
key0 | cost time | TINT32 | 123 | 1 |   
key1 | pos | TINT32 | 1230123 | 1 |   
key2 | troop list | string | “123:123:123” | 1 | 以:分隔  
key3 | if general join | bool | 0 | 1 |   
key4 | card_list | string | “1,2,3,4,5” | 1 | 骑士列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_reinforce&rf_troop_num=900000&rf_slot_num=20&key0=123&key1=1230123&key2=“123:123:123”&key3=0&key4=“1,2,3,4,5”

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座march-throne_reinforce_speedup

  * **命令字** **_throne_reinforce_speedup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | TINT32 | 123 | 1 |   
key1 | pos | TINT32 | 1230567 | 1 |   
key2 | troop list | string | “33:112:22” | 1 | 以:分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_reinforce_speedup&key0=123&key1=1230567&key2=“33:112:22”

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座march-throne dismiss all

  * **命令字** **_throne_dismiss_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | TINT32 | 123 | 1 |   
key1 | pos | TINT32 | 123 | 1 |   
key2 | troop list | string | 1:2 | 1 | 以:分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_dismiss_all&key0=123&key1=123&key2=1:2

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 王座march-放弃王座

  * **命令字** **_throne_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | TINT32 | 123 | 1 |   
key1 | pos | TINT32 | 1230123 | 1 |   
key2 | troop list | string | 12:12 | 1 | 以:分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_abandon&key0=123&key1=1230123&key2=12:12

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.89.王座title

* * *

#### 王座title-任命称号

  * **命令字** **_throne_dub_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | uint32 | 123 | 1 |   
key1 | title id | int32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=throne_dub_title&key0=123&key1=12

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.90.登录

* * *

#### 登录-登录用户信息

  * **命令字** **_account_login_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_login

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.2 | 新增接口  
  
* * *

#### 登录-获取用户信息

  * **命令字** **_login_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=login_get

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.1 | 新增接口  
  
* * *

### 7.91.皮肤

* * *

#### 皮肤-碎片合成皮肤item

  * **命令字** **_city_skin_piece_merge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_id | int64 | 1 | 1 | 皮肤 id  
key1 | skin_piece_id | int64 | 1 | 1 | 皮肤碎片 id  
key2 | skin_piece_num | int64 | 1 | 1 | 皮肤碎片数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=city_skin_piece_merge&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-主城皮肤升星

  * **命令字** **_city_skin_star_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_id | int64 | 1 | 1 | 皮肤 id  
key1 | item_id | int64 | 1 | 1 | 升星 item id  
key1 | item_num | int64 | 1 | 1 | 升星 item 数量  
key2 | target_star_level | int64 | 1 | 1 | 目标星级  
key10 | is_succ | int64 | 1 | 1 | 0升级失败1-成功  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=city_skin_star_up&key0=1&key1=1&key1=1&key2=1&key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-主城皮肤穿戴

  * **命令字** **_city_skin_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_id | int64 | 1 | 1 | 皮肤 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=city_skin_put_on&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-主城皮肤碎片出售

  * **命令字** **_city_skin_piece_sell_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_piece_id_list | string | 1,2,3 | 1 | 皮肤碎片 id 列表 id1,id2,id3…  
key1 | skin_piece_num_list | string | 1,1,1 | 1 | 皮肤碎片数量列表 num1,num2,num3…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=city_skin_piece_sell&key0=1,2,3&key1=1,1,1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-主城皮肤item出售

  * **命令字** **_city_skin_item_sell_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_item_id | int64 | 1 | 1 | 皮肤 item id  
key1 | skin_item_num | int64 | 1 | 1 | 皮肤 item 数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=city_skin_item_sell&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-领主皮肤穿戴

  * **命令字** **_sheriff_skin_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_id | int64 | 1 | 1 | 皮肤 id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=sheriff_skin_put_on&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-皮肤碎片合成

  * **命令字** **_skin_piece_merge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_type | int32 | 1 | 1 |   
key1 | skin_id | int64 | 1 | 1 | 皮肤id  
key2 | skin piece id | int64 | 1 | 1 | 皮肤碎片id  
key3 | skin piece num | int64 | 1 | 1 | 皮肤碎片数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skin_piece_merge&key0=1&key1=1&key2=1&key3=1

  * **备注**



> rsp_type:user_json  
>  key0=1:主城皮肤 2:治安官皮肤 3:行军队列皮肤 4:采集队列皮肤 5:scout队列皮肤 6:头像框皮肤

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-皮肤升星

  * **命令字** **_skin_star_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_type | int64 | 1 | 1 |   
key1 | skin_id | int64 | 1 | 1 | 皮肤id  
key2 | item id (升星token) | int64 | 1 | 1 | 皮肤升星item id  
key3 | item num | int64 | 1 | 1 | 皮肤升星item数量  
key4 | target_star_level | int64 | 1 | 1 | 目标星级  
key10 | is_succ | int64 | 1 | 1 | 0升级失败1-成功  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skin_star_up&key0=1&key1=1&key2=1&key3=1&key4=1&key10=1

  * **备注**



> rsp_type:user_json  
>  key0=1:主城皮肤 2:治安官皮肤 3:行军队列皮肤 4:采集队列皮肤 5:scout队列皮肤 6:头像框皮肤

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-皮肤穿戴

  * **命令字** **_skin_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_type | int64 | 1 | 1 |   
key1 | skin id | int64 | 1 | 1 | 皮肤id  
key2 | gem_cost | int64 | 1 | 0 |   
key3 | item_id | int64 | 1 | 0 |   
key4 | item_num | int64 | 1 | 0 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skin_put_on&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp_type:user_json  
>  key0=1:主城皮肤 2:治安官皮肤 3:行军队列皮肤 4:采集队列皮肤 5:scout队列皮肤 6:头像框皮肤  
>  key2=宝石消耗,大于0则消耗宝石,否则消耗item，(v2.6头像框皮肤新增,仅存在消耗的情况下需要传此参数)  
>  key3=item消耗(v2.6头像框皮肤新增，仅存在消耗的情况下传此参数)  
>  key4=item数量(v2.6头像框皮肤新增，仅存在消耗的情况下传此参数)

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-领取皮肤收集奖励

  * **命令字** **_collect_permanent_skin_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_type | int64 | 1 | 1 |   
key1 | num | int64 | 1 | 1 | 数值配置的档位，与数值一一对应  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=collect_permanent_skin_reward&key0=1&key1=1

  * **备注**



> key0=1:主城皮肤 2:治安官皮肤 3:行军队列皮肤 4:采集队列皮肤 5:scout队列皮肤 6:头像框皮肤

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 皮肤-切换将领皮肤

  * **命令字** **_change_general_skin_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | card_type | int32 | 1 | 1 |   
key1 | item_id | int32 | 1 | 1 |   
key2 | gem_cost | int64 | 1 | 1 | 非0代表消耗宝石  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_general_skin&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.6.0 | 新增接口  
  
* * *

#### 皮肤-使用解锁用户头像道具

  * **命令字** **_unlock_user_avatar_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
key1 | avatar_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=unlock_user_avatar&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-使用解锁用户聊天框道具

  * **命令字** **_unlock_chatbubble_skin_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=unlock_chatbubble_skin&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-穿戴数值皮肤

  * **命令字** **_numerical_skin_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | numerical_skin_id | int32 | 1 | 1 |   
key1 | skin_type | int32 | 1 | 1 | 主城皮肤 or 治安官皮肤 or 行军队列皮肤  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=numerical_skin_put_on&key0=1&key1=1

  * **skin_type定义**

skin_type | 含义 | 备注  
---|---|---  
1 | 主城数值皮肤 |   
2 | 治安官数值皮肤 |   
3 | 行军队列数值皮肤 |   
  
  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-使用解锁表情包道具

  * **命令字** **_use_emoji_skin_item_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=use_emoji_skin_item&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-屏蔽表情包开关设置

  * **命令字** **_change_block_emoji_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | value | int32 | 1 | 1 | 0 为不屏蔽, 1 为屏蔽  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_block_emoji_switch&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-大地图表情包轮盘穿戴

  * **命令字** **_map_emoji_conf_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | emoji_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_emoji_conf_put_on&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-大地图表情包轮盘卸下

  * **命令字** **_map_emoji_conf_put_off_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | index | int32 | 1 | 1 | 要卸载的表情包的位置,下标从0开始  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_emoji_conf_put_off&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-地块发送大地图表情包

  * **命令字** **_pos_send_map_emoji_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | emoji_id | int32 | 1 | 1 |   
key1 | pos_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=pos_send_map_emoji&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-行军队列发送大地图表情包

  * **命令字** **_march_send_map_emoji_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | emoji_id | int32 | 1 | 1 |   
key1 | action_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=march_send_map_emoji&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 皮肤-使用皮肤特效道具

  * **命令字** **_use_skin_special_effects_item_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=use_skin_special_effects_item&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.2 | 新增接口  
  
* * *

#### 皮肤-皮肤特效状态设置

  * **命令字** **_set_skin_special_effects_status_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_special_effects_id | int32 | 1 | 1 |   
key1 | status | int32 | 1 | 0-未使用 1-使用 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_skin_special_effects_status&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.2 | 新增接口  
  
* * *

#### 皮肤-皮肤通用碎片兑换

  * **命令字** **_skin_universal_piece_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_type | int32 | 1 | 1 | 皮肤类型  
key1 | universal_piece_id | int32 | 1 | 1 | 通用碎片ID  
key2 | target_piece_id | int32 | 1 | 1 | 目标碎片ID  
key3 | num | int32 | 1 | 1 | 兑换数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skin_universal_piece_exchange&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

### 7.92.目标活动

* * *

#### 目标活动-领取统计活动奖励

  * **命令字** **_claim_statistics_event_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_type | int32 | 1 | 1 | int  
key1 | event_id | string | 121_23 | 1 | string  
key2 | task_id | string | 1 | 1 | int  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_statistics_event_reward&key0=1&key1=121_23&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

### 7.93.研究

* * *

#### 研究-科技升级

  * **命令字** **_research_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | upgrade type) | int64 | 1 | 1 |   
key1 | research type | int64 | 1 | 1 |   
key2 | target level | int64 | 1 | 1 |   
key3 | gem cost or cost time | int64 | 11 | 1 |   
key4 | exp | int64 | 111 | 1 |   
key5 | 是否直接req help | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=research_upgrade&key0=1&key1=1&key2=1&key3=11&key4=111&key5=1

  * **备注**



> key0=0: normal, 1: instant(材料足够,消耗材料), 2: buy(材料不足,不消耗材料

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.5 | 新增接口  
  
* * *

### 7.94.研究token生产

* * *

#### 研究token生产-领取研究token

  * **命令字** **_claim_dev_token_from_building_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dev token id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_dev_token_from_building&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

#### 研究token生产-切换研究token生产

  * **命令字** **_swap_building_buff_for_dev_token_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | buff_idx | TINT64 | 1 | 1 |   
key1 | 建筑id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=swap_building_buff_for_dev_token&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.2 | 新增接口  
  
* * *

### 7.95.社区bot

* * *

#### 社区bot-社区签到

  * **命令字** **_op_social_bot_checkin_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
uid | uid | int64 | 1 | 1 |   
key0 | time | int64 | 1 | 1 | 发出时间,单位秒  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_social_bot_checkin&uid=1&key0=1

  * 命令字反包格式 – 仅错误码

  * **改动历史**


版本号 | 说明  
---|---  
v7.1.1 | 新增接口  
  
* * *

### 7.96.神秘人商店

* * *

#### 神秘人商店-刷新商店

  * **命令字** **_mysterious_merchant_refresh_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | num | int32 | 1 | 1 | 已刷新次数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mysterious_merchant_refresh&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

#### 神秘人商店-购买商品

  * **命令字** **_mysterious_merchant_item_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int64 | 1 | 1 |   
key1 | id | string | 1 | 1 | 类别商品id  
key2 | type,id,num:type,id,num | string | 1,2,1:1,3,1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mysterious_merchant_item_buy&key0=1&key1=1&key2=1,2,1:1,3,1

  * **备注**



> key0=商品类别 0-时代1资源，1-时代2资源，2-加速，3-其他 与数值协议保持一致 key2=用:分割不同物品,用,分割对象type,id,num 传入消耗物品

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

#### 神秘人商店-累计在线5分钟

  * **命令字** **_mysterious_merchant_arrive_time_reduce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mysterious_merchant_arrive_time_reduce

  * **改动历史**

版本号 | 说明  
---|---  
v3.2.0 | 新增接口  
  
* * *

### 7.97.神秘礼物

* * *

#### 神秘礼物-收集神秘礼物

  * **命令字** **_mistery_gift_collect_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mistery_gift_collect

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

#### 神秘礼物-保护平民，其实是领取神秘礼物奖励

  * **命令字** **_protect_civilian_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=protect_civilian

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.8 | 新增接口  
  
* * *

### 7.98.离线补偿

* * *

#### 离线补偿-领取离线防守补偿奖励

  * **命令字** **_claim_offline_defence_compensation_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_offline_defence_compensation

  * **改动历史**

版本号 | 说明  
---|---  
v2.0 | 新增接口  
  
* * *

### 7.99.移服活动

* * *

#### 移服活动-移服活动-搜索玩家

  * **命令字** **_search_immigration_player_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | search_type | int32 | 1 | 1 | 搜索类型，1是uid，2是user_name  
key1 | search_key | string | 1 | 1 | 搜索内容,具体见移服活动协议  
key2 | event_id | string | “11111” | 1 | 活动id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=search_immigration_player_info&key0=1&key1=1&key2=“11111”

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-移服检查

  * **命令字** **_immigration_event_move_check_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | move_type | int32 | 1 | 1 | 移城type 1.特别邀请 2.高级邀请 3.普通邀请 9.自由移民  
key2 | old_city_pos | int32 | 1 | 1 | 当前主城位置  
key3 | target_sid | int32 | 1 | 1 | 目标sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_move_check&key0=“11111”&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-移服准备

  * **命令字** **_immigration_event_move_prepare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | move_type | int32 | 1 | 1 | 移城type 1.特别邀请 2.高级邀请 3.普通邀请 9.自由移民  
key2 | old_city_pos | int32 | 1 | 1 | 当前主城位置  
key3 | target_sid | int32 | 1 | 1 | 目标sid  
key4 | rss | string |  | 1 | [[type,id,num],[type,id,num]…]json格式传入要设置的资源，超过可携带上限的资源需设置为可携带上限  
key5 | item_id | int32 | 1 | 1 | 消耗token的id  
key6 | item_num | int32 | 1 | 1 | 消耗token的num  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_move_prepare&key0=“11111”&key1=1&key2=1&key3=1&key4=&key5=1&key6=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-移服

  * **命令字** **_immigration_event_move_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | move_type | int32 | 1 | 1 | 移城type 1.特别邀请 2.高级邀请 3.普通邀请 9.自由移民  
key2 | old_city_pos | int32 | 1 | 1 | 当前主城位置  
key3 | target_sid | int32 | 1 | 1 | 目标sid  
key4 | rss | string |  | 1 | [[type,id,num],[type,id,num]…]json格式传入要设置的资源，超过可携带上限的资源需设置为可携带上限  
key5 | item_id | int32 | 1 | 1 | 消耗token的id  
key6 | item_num | int32 | 1 | 1 | 消耗token的num  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_move&key0=“11111”&key1=1&key2=1&key3=1&key4=&key5=1&key6=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-邀请玩家

  * **命令字** **_immigration_event_invite_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | invite_type | int32 | 1 | 1 | 邀请type 1.特别邀请 2.高级邀请 3.普通邀请  
key2 | target_uid | int32 | 1 | 1 | 邀请的UID  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_invite_player&key0=“11111”&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-取消邀请

  * **命令字** **_immigration_event_cancel_invite_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | invite_type | int32 | 1 | 1 | 邀请ype 1.特别邀请 2.高级邀请 3.普通邀请  
key2 | target_uid | int32 | 1 | 1 | 邀请的UID  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_cancel_invite&key0=“11111”&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-拒绝邀请

  * **命令字** **_immigration_event_reject_invite_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | invite_type | int32 | 1 | 1 | 邀请ype 1.特别邀请 2.高级邀请 3.普通邀请  
key2 | source_sid | int32 | 1 | 1 | 邀请的sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_reject_invite&key0=“11111”&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-删除邀请

  * **命令字** **_immigration_event_delete_invite_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | invite_type | int32 | 1 | 1 | 邀请ype 1.特别邀请 2.高级邀请 3.普通邀请  
key2 | source_sid | int32 | 1 | 1 | 邀请的sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_delete_invite&key0=“11111”&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
v7.2.6 | 更新type  
  
* * *

#### 移服活动-移服活动-申请成为移民官

  * **命令字** **_apply_immigration_event_candidate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=apply_immigration_event_candidate&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-投票

  * **命令字** **_vote_immigration_event_candidates_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 | 活动的event_id  
key1 | uid_list | string | 1,2,3 | 1 | uid,uid,uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=vote_immigration_event_candidates&key0=1&key1=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v7.2 | 新增接口  
  
* * *

#### 移服活动-移服活动-请求申请

  * **命令字** **_immigration_event_request_invite_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | target_sid | int32 | 1 | 1 | 请求的sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_request_invite&key0=“11111”&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 移服活动-移服活动-撤回请求

  * **命令字** **_immigration_event_withdraw_request_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | target_sid | int32 | 1 | 1 | 请求的sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_withdraw_request&key0=“11111”&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 移服活动-移服活动-同意请求

  * **命令字** **_immigration_event_approve_request_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | target_uid | int32 | 1 | 1 | 请求的uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_approve_request&key0=“11111”&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 移服活动-移服活动-拒绝请求

  * **命令字** **_immigration_event_reject_request_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | “11111” | 1 | 活动id  
key1 | target_uid | int32 | 1 | 1 | 请求的uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=immigration_event_reject_request&key0=“11111”&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.100.竞猜

* * *

#### 竞猜-下注

  * **命令字** **_betting_normal_set_chips_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 主活动id | string | 121_167889986_0_1 | 1 |   
key1 | 活动id | string | 121_167889986_0_1 | 1 |   
key2 | 竞猜活动id | string | 121_167889986_0_1 | 1 |   
key3 | 竞猜押注方 | TINT64 | 2500600 | 1 | 0：左 1：右 2：平  
key4 | 下注筹码 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=betting_normal_set_chips&key0=121_167889986_0_1&key1=121_167889986_0_1&key2=121_167889986_0_1&key3=2500600&key4=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 竞猜-加注

  * **命令字** **_betting_normal_add_chips_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 主活动id | string | 121_167889986_0_1 | 1 |   
key1 | 活动id | string | 121_167889986_0_1 | 1 |   
key2 | 竞猜活动id | string | 121_167889986_0_1 | 1 |   
key3 | 竞猜押注方 | TINT64 | 2500600 | 1 | 0：左 1：右 2：平  
key4 | 下注筹码 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=betting_normal_add_chips&key0=121_167889986_0_1&key1=121_167889986_0_1&key2=121_167889986_0_1&key3=2500600&key4=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 竞猜-撤注

  * **命令字** **_betting_normal_cancel_chips_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 主活动id | string | 121_167889986_0_1 | 1 |   
key1 | 活动id | string | 121_167889986_0_1 | 1 |   
key2 | 竞猜活动id | string | 121_167889986_0_1 | 1 |   
key3 | 竞猜历史下注的id | string | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=betting_normal_cancel_chips&key0=121_167889986_0_1&key1=121_167889986_0_1&key2=121_167889986_0_1&key3=123

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

#### 竞猜-领取奖励

  * **命令字** **_betting_normal_claim_chips_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 主活动id | string | 121_167889986_0_1 | 1 |   
key1 | 活动id | string | 121_167889986_0_1 | 1 |   
key2 | 领取下注历史奖励 | (todo) | (todo) | 1 | 需查询确认  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=betting_normal_claim_chips&key0=121_167889986_0_1&key1=121_167889986_0_1&key2=(todo)

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
  
* * *

### 7.101.竞猜相关

* * *

#### 竞猜相关-普通竞猜-下注

  * **命令字** **_betting_normal_set_chips_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 竞猜主页的event id | string | aaaa | 1 |   
key1 | 普通竞猜活动的event id | string | bbbb | 1 |   
key2 | 单局普通竞猜event id | string | cccc | 1 |   
key3 | 竞猜对象 | int32 | 1 | 1 | 0：左 1：右 2：平  
key4 | 下注筹码 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=betting_normal_set_chips&key0=aaaa&key1=bbbb&key2=cccc&key3=1&key4=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v4.7 | 新增接口  
v5.0 | 随便写个历史测一下  
v5.2 | 随便写个历史测一下  
  
* * *

### 7.102.累计充值活动

* * *

#### 累计充值活动-累计充值活动领奖

  * **命令字** **_accumulate_recharge_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event id | string | 15415_51 | 1 | 活动id  
key1 | level,level | str | 1 | 1 | 要领取的奖励等级列表,逗号分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=accumulate_recharge_claim_reward&key0=15415_51&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.4.0 | 新增接口  
  
* * *

### 7.103.美女玩牌

* * *

#### 美女玩牌-启动猜牌

  * **命令字** **_start_play_card_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | diamond_cost | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=start_play_card&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 美女玩牌-玩家猜牌

  * **命令字** **_play_guess_card_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | card_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=play_guess_card&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 美女玩牌-一键玩牌

  * **命令字** **_auto_play_guess_card_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | diamond_cost | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auto_play_guess_card&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.104.联盟公告板

* * *

#### 联盟公告板-联盟信息墙添加消息

  * **命令字** **_al_wall_msg_add_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | content | string | sfdfsfd | 1 |   
key1 | top_flag | int | 1 | 1 | 不传或者传0代表不置顶,1代表置顶  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_wall_msg_add&key0=sfdfsfd&key1=1

  * **备注**



> 返回wall_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.43 | 新增接口  
v7.1 | 新增参数key1  
  
* * *

#### 联盟公告板-联盟信息墙添删除消息

  * **命令字** **_al_wall_msg_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | msg id | int64 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_wall_msg_del&key0=111

  * **备注**



> 返回wall_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.43 | 新增接口  
  
* * *

#### 联盟公告板-拉取联盟信息墙

  * **命令字** **_al_wall_msg_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_wall_msg_get

  * **备注**



> 返回wall_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.43 | 新增接口  
  
* * *

#### 联盟公告板-联盟comment——置顶+取消置顶

  * **命令字** **_c_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | msg_id | int64 | 111 | 1 |   
key1 | type: | int32 | 1 | 1 | 0 取消置顶，1设置置顶  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=c&key0=111&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.43 | 新增接口  
  
* * *

### 7.105.联盟功能

* * *

#### 联盟功能-退出联盟准备

  * **命令字** **_al_leave_prepare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
|  |  |  |  |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_leave_prepare&=

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.13 | 新增接口  
  
* * *

#### 联盟功能-退出联盟

  * **命令字** **_al_kick_prepare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 目标uid | TUINT32 | 1000455 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_kick_prepare&key0=1000455

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.13 | 新增接口  
  
* * *

#### 联盟功能-翻译联盟外交板

  * **命令字** **_al_diplomacy_comment_translate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 目标联盟id | TINT64 | 100012 | 1 |   
key1 | 外交板留言id | TINT64 | 1 | 1 |   
key2 | 目标语言id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_diplomacy_comment_translate&key0=100012&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.13 | 新增接口  
  
* * *

#### 联盟功能-翻译联盟公告

  * **命令字** **_al_wall_msg_translate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 公告id | TINT64 | 2 | 1 |   
key1 | 目标语言id | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_wall_msg_translate&key0=2&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.1 | 新增接口  
  
* * *

#### 联盟功能-创建联盟

  * **命令字** **_al_create_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_name | string | dfgd | 1 |   
key1 | al_desc | string | sdf | 1 |   
key2 | al_language | int32 | 1 | 1 |   
key3 | al_nick_name | string | sdfsd | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_create&key0=dfgd&key1=sdf&key2=1&key3=sdfsd

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-加入联盟

  * **命令字** **_al_join_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_join&key0=111

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-离开联盟

  * **命令字** **_al_leave_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 111 | 0 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_leave&key0=111

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-踢出联盟

  * **命令字** **_al_kick_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_kick&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.13 | 新增接口  
  
* * *

#### 联盟功能-获取联盟加入请求

  * **命令字** **_al_request_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_request_get

  * **备注**



> 返回playerlist_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-允许加入联盟

  * **命令字** **_al_allow_join_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid(以:隔开) | string | 1:12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_allow_join&key0=1:12

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-拒绝某人加入联盟

  * **命令字** **_al_reject_join_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid(以:隔开) | string | 1:12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_reject_join&key0=1:12

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-拉取成员列表

  * **命令字** **_al_member_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 1 | 1 |   
key0 | jump | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_member_get&key0=1&key0=1

  * **备注**



> 返回playerlist_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-改变联盟成员职位

  * **命令字** **_al_pos_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int32 | 111 | 1 |   
key1 | from_pos | int32 | 2500600 | 1 |   
key2 | target_pos | int32 | 2500600 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_pos_change&key0=111&key1=2500600&key2=2500600

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-改变联盟加入策略

  * **命令字** **_al_policy_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | policy | int32 | 0 | 1 | 0:需要批准,1:自动加入  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_policy_change&key0=0

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-改变联盟desc

  * **命令字** **_al_desc_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_desc | string | fsdfx | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_desc_change&key0=fsdfx

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-改变联盟notice

  * **命令字** **_al_notice_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_notice | string | dsgfg | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_notice_change&key0=dsgfg

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-翻译联盟notice

  * **命令字** **_al_notice_translate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 目标语言id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_notice_translate&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

#### 联盟功能-改变联盟语言

  * **命令字** **_al_lang_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_lang | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_lang_change&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-拉取别人的联盟信息

  * **命令字** **_al_info_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_info_get&key0=111

  * **备注**



> 返回allianceinfo_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-拉取别人的联盟信息(op)

  * **命令字** **_op_al_info_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int32 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_al_info_get&key0=111

  * **备注**



> 返回allianceinfo_json.h

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

#### 联盟功能-改变玩家alliance flag

  * **命令字** **_al_avatar_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | flag id | int32 | 1 | 1 |   
key1 | 消耗类型 | int32 | 1 | 1 | (0 消耗道具, 1消耗宝石)  
key2 | gem_num | int64 | 1 | 1 |   
key3 | item id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_avatar_change&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-改联盟简称

  * **命令字** **_al_nick_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_nick_name | string | dsfgdsdf | 1 |   
key1 | gem num | int64 | 1 | 1 |   
key2 | item_id | int32 | 1 | 1 |   
key3 | type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_nick_change&key0=dsfgdsdf&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-改联盟名字

  * **命令字** **_al_name_change_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | al_nick_name | string | dsfgdsdf | 1 |   
key1 | gem num | int64 | 1 | 1 |   
key2 | item_id | int32 | 1 | 1 |   
key3 | type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_name_change&key0=dsfgdsdf&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-设置联盟据点位置

  * **命令字** **_al_set_hive_pos_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | hive_svr | int32 | 1 | 1 |   
key1 | hive_pos | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_set_hive_pos&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-设置联盟hive

  * **命令字** **_set_hive_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_pos | int32 | 1 | 1 |   
key1 | target_svr | int32 | 1 | 1 |   
key2 | item_id | int32 | 1 | 1 | 必传  
key3 | gem_cost | int64 | 1 | 1 | 大于0表示消耗宝石  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_hive&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-联盟自动踢人开关

  * **命令字** **_auto_al_kick_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | switch | int32 | 1 | 1 | 0:close、1:open  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auto_al_kick_switch&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.12 | 新增接口  
  
* * *

#### 联盟功能-创建部门

  * **命令字** **_al_department_create_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | name | string | sdfgdsf | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_department_create&key0=sdfgdsf

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-解散部门

  * **命令字** **_al_department_dismiss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | department_id | int64 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_department_dismiss&key0=111

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-部门改名

  * **命令字** **_al_department_rename_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | department_id | int64 | 1 | 1 |   
key1 | new_name | string | sdfdsf | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_department_rename&key0=1&key1=sdfdsf

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-部门权限分配

  * **命令字** **_al_department_assign_privilege_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | department_id | int64 | 34 | 1 |   
key1 | new_privilege_list | string | sdgdf,dfg | 1 | privilege1,privilege2,privilege3…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_department_assign_privilege&key0=34&key1=sdgdf,dfg

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-部门成员增删

  * **命令字** **_al_department_member_modify_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | department_id | int64 | 1 | 1 |   
key1 | add_uid_list | string | 1,2,3 | 1 | uid1,uid2,uid3…  
key2 | del_uid_list | string | 1,2,3 | 1 | uid1,uid2,uid3…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_department_member_modify&key0=1&key1=1,2,3&key2=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-拉取所有部门

  * **命令字** **_al_all_department_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key1 | aid | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_all_department_get&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-外交留言板发言

  * **命令字** **_al_diplomacy_comment_add_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_aid | int64 | 1 | 1 |   
key1 | content | string | sdsgdf | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_diplomacy_comment_add&key0=1&key1=sdsgdf

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-外交留言板删除发言

  * **命令字** **_al_diplomacy_comment_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_aid | int64 | 1 | 1 |   
key1 | comment_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_diplomacy_comment_del&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-外交留言板发言获取

  * **命令字** **_al_diplomacy_comment_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_aid | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_diplomacy_comment_get&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-刷新推荐用户列表

  * **命令字** **_refresh_al_recommend_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=refresh_al_recommend_player

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-邀请联盟推荐用户

  * **命令字** **_invite_recommend_player_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid_list | string | 1,2,3 | 1 | uid3,uid2,uid1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=invite_recommend_player&key0=1,2,3

  * **备注**



> 所有邀请都用该命令字, 旧的邀请命令字废弃…

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-设置邀请/推荐开关

  * **命令字** **_set_recommend_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | switch | int64 | 1 | 1 | 0: 开 1: 关  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_recommend_switch&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7.0 | 新增接口  
  
* * *

#### 联盟功能-获取服务器force排名前X的联盟

  * **命令字** **_get_server_rank_alliance_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 | sid  
key1 | num | int64 | 1 | 1 | 数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_server_rank_alliance_list&key0=1&key1=1

  * **备注**


    
    
    反包格式
    [
        long, // aid
        long,
    ]
    
    反包: svr_cache_svr

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.106.联盟商店

* * *

#### 联盟商店-联盟item兑换

  * **命令字** **_al_item_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
key1 | item num | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_item_exchange&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.16 | 新增接口  
  
* * *

#### 联盟商店-购买联盟item

  * **命令字** **_al_item_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
key1 | item num | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_item_buy&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.16 | 新增接口  
  
* * *

#### 联盟商店-联盟item打星

  * **命令字** **_al_item_mark_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_item_mark&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.16 | 新增接口  
  
* * *

#### 联盟商店-取消联盟store item打星

  * **命令字** **_al_item_unmark_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_item_unmark&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.16 | 新增接口  
  
* * *

#### 联盟商店-删除联盟store item打星记录

  * **命令字** **_al_item_mark_clear_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_item_mark_clear&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
2.1.16 | 新增接口  
  
* * *

### 7.107.联盟外交

* * *

#### 联盟外交-设置联盟外交关系

  * **命令字** **_al_diplomacy_set_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 目标联盟id | int32 | 11 | 1 |   
key1 | 关系(见枚举) | int8 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_diplomacy_set&key0=11&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.18 | 新增接口  
  
* * *

#### 联盟外交-获取联盟外交关系

  * **命令字** **_al_diplomacy_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | diplomacy_type | int8 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_diplomacy_get&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.18 | 新增接口  
  
* * *

### 7.108.联盟外交公告板

* * *

#### 联盟外交公告板-联盟外交公告板添加黑名单成员

  * **命令字** **_al_comment_black_add_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 留言id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_comment_black_add&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.0 | 新增接口  
  
* * *

#### 联盟外交公告板-联盟外交公告板删除黑名单成员

  * **命令字** **_al_comment_black_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_comment_black_del&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.0 | 新增接口  
  
* * *

### 7.109.联盟帮助

* * *

#### 联盟帮助-帮助联盟其他人的action

  * **命令字** **_al_help_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_help&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.14 | 新增接口  
  
* * *

#### 联盟帮助-帮助联盟其他所有人的action

  * **命令字** **_al_help_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_help_all

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.14 | 新增接口  
  
* * *

#### 联盟帮助-联盟帮助(新)

  * **命令字** **_al_help_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid:action_id,uid:action_id… | string | 111:222,333:444 | 1 | 最多20条action  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_help_new&key0=111:222,333:444

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.14 | 新增接口  
  
* * *

### 7.110.联盟建筑

* * *

#### 联盟建筑-开始建造联盟建筑

  * **命令字** **_al_building_put_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | building id | int32 | 123 | 1 |   
key1 | pos | int32 | 1230123 | 1 |   
key0 | stage id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_put_up&key0=123&key1=1230123&key0=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-支援建造//(此action recall用普通 的action recall)

  * **命令字** **_al_building_put_up_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost_time | uint32 | 123 | 1 |   
key1 | target_pos | uint32 | 123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_put_up_reinforce&key0=123&key1=123&key2=123

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-拆除建筑

  * **命令字** **_al_building_remove_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | building id | int32 | 123 | 1 |   
key1 | pos | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_remove&key0=123&key1=123

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-移动建筑

  * **命令字** **_al_building_move_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | building id | int32 | 123 | 1 |   
key1 | new pos | int32 | 123 | 1 |   
key2 | old pos | int32 | 123 | 1 |   
key3 | item_id | int32 | 123 | 1 | 道具id，要有值  
key4 | item num | int32 | 123 | 1 |   
key5 | cost_gold | int32 | 123 | 1 | 消耗道具时此值填0，否则消耗金块  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_move&key0=123&key1=123&key2=123&key3=123&key4=123&key5=123

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-建筑失效

  * **命令字** **_op_al_building_invalid_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int64 | 123 | 1 |   
key1 | building id | uint32 | 123 | 1 |   
key2 | pos | int32 | 1230123 | 1 |   
key2 | hive size | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_al_building_invalid&key0=123&key1=123&key2=1230123&key2=123

  * **备注**



> rsp_type：special

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-建筑生效

  * **命令字** **_op_al_building_active_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | aid | int64 | 123 | 1 |   
key1 | building id | uint32 | 123 | 1 |   
key2 | pos | int32 | 1230123 | 1 |   
key2 | hive size | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_al_building_active&key0=123&key1=123&key2=1230123&key2=123

  * **备注**



> rsp_type：special

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-发起拉联盟资源地

  * **命令字** **_al_building_occupy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 1230123 | 1 |   
key3 | troop list | string | 123:123 | 1 | (以:分隔)  
key4 | general | bool | 0 | 1 | 是否带将领  
key5 | occupy_num | uint32 | 123 | 0 | 客户端计算的采集量, 后台并没有用到..  
key6 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
key7 | RssStage | int64 |  | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_occupy&key0=123&key1=1230123&key3=123:123&key4=0&key5=123&key6=123&key7=

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-存资源

  * **命令字** **_al_building_storage_rss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | send rss | string | 123 | 1 |   
key2 | building id | int32 | 123 | 1 |   
key3 | pos | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_storage_rss&key0=123&key1=123&key2=123&key3=123

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-取资源

  * **命令字** **_al_building_take_out_rss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | send rss | string | “123:211” | 1 |   
key2 | building id | int32 | 123 | 1 |   
key3 | pos | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_take_out_rss&key0=123&key1=“123:211”&key2=123&key3=123

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-查看al building情况

  * **命令字** **_get_al_building_detail_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_al_building_detail_info&key0=123&key1=123

  * **备注**



> rsp_type：al_buildng_info

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 联盟建筑-获取全服联盟堡垒信息

  * **命令字** **_get_all_al_fortress_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_all_al_fortress_info&key0=123

  * **备注**



> 反包:svr_all_al_fortress_info

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

### 7.111.联盟建筑march

* * *

#### 联盟建筑march-attack

  * **命令字** **_al_building_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_attack&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-rally_war

  * **命令字** **_al_building_rally_war_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123:123 | 1 |   
key4 | if general join | uint32 | 123 | 1 |   
key5 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_rally_war&key0=123&key1=123&key2=123&key3=123:123&key4=123&key5=123&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-reinforce //支援普通队列

  * **命令字** **_al_building_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 1230123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_reinforce&key0=123&key1=1230123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-dispatch

  * **命令字** **_al_building_dispatch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_dispatch&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-dismiss all

  * **命令字** **_al_building_dismiss_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_dismiss_all&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-recall reinforce

  * **命令字** **_al_building_recall_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_recall_reinforce&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-speed up

  * **命令字** **_al_building_reinforce_speedup (仅用于防守方)_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | string | 123 | 1 | (key2>0 时, 优先消耗宝石)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_reinforce_speedup (仅用于防守方)&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟建筑march-kick

  * **命令字** **_al_building_repatriate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | action id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_building_repatriate&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

### 7.112.联盟战

* * *

#### 联盟战-报名

  * **命令字** **_ava_battle_sign_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | int64 | 123 | 1 |   
key1 | zone_schedule_idx | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_sign_up&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战-选择参战人员

  * **命令字** **_ava_select_competition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid_list | string | 1,2,3 | 1 | uid,uid,uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_select_competition&key0=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战-退赛 //报名期间解散联盟，若有参赛，则要先发退赛请求

  * **命令字** **_ava_battle_sign_up_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | uint64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_sign_up_cancel&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战-拉取参赛人员列表

  * **命令字** **_get_ava_battle_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_ava_battle_info

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.113.联盟战march

* * *

#### 联盟战march-attack （ava资源地形occupy和attack都用这个命令字）

  * **命令字** **_ava_battle_building_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_attack&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-rally_war

  * **命令字** **_ava_battle_building_rally_war_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123:123 | 1 |   
key4 | if general join | uint32 | 1 | 1 |   
key5 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_rally_war&key0=123&key1=123&key2=123&key3=123:123&key4=1&key5=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-reinforce //支援普通队列

  * **命令字** **_ava_battle_building_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 1230123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_reinforce&key0=123&key1=1230123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-dispatch //支援指挥官队列

  * **命令字** **_ava_battle_building_dispatch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | troop list | string | 123 | 1 | (以:分隔)  
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_dispatch&key0=123&key1=123&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-abandon （ava资源地recall用这个命令字）

  * **命令字** **_ava_battle_building_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_abandon&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-dismiss all

  * **命令字** **_ava_battle_building_dismiss_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_dismiss_all&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-recall_reinforce

  * **命令字** **_ava_battle_building_recall_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_recall_reinforce&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-speed_up

  * **命令字** **_ava_battle_building_reinforce_speedup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action_id | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | uint32 | 123 | 1 | (key2>0 时, 优先消耗宝石)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_reinforce_speedup&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-遣散

  * **命令字** **_ava_battle_building_repatriate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | uint32 | 123 | 1 |   
key1 | pos | uint32 | 123 | 1 |   
key2 | action id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_building_repatriate&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-报名

  * **命令字** **_ava_battle_sign_up_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | int64 | 123 | 1 |   
key1 | zone_schedule_idx | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_sign_up&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-选择参战人员

  * **命令字** **_ava_select_competition_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid_list | string | 1,2,3 | 1 | uid,uid,uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_select_competition&key0=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战march-退赛 //报名期间解散联盟，若有参赛，则要先发退赛请求

  * **命令字** **_ava_battle_sign_up_cancel_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | uint64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=ava_battle_sign_up_cancel&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.114.联盟战move

* * *

#### 联盟战move-进入战场前置处理

  * **命令字** **_enter_ava_battle_map_preprocess_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | battle_id | int64 | 123 | 1 |   
key3 | item_id | int64 | 123 | 0 |   
key4 | cost | int64 | 123 | 0 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=enter_ava_battle_map_preprocess&key0=123&key1=123&key3=123&key4=123

  * **备注**



> 和移城准备一样需要等待, 取原协议中move_city_prepare_time作为等待时间, 不处理边界情况, 等待完直接调用进入请求进入战场

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战move-进入战场

  * **命令字** **_enter_ava_battle_map_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | battle_id | int64 | 123 | 1 |   
key2 | move_city_pos | int64 | 1230123 | 1 |   
key3 | item_id | int64 | 123 | 0 |   
key4 | gem_cost | int64 | 123 | 0 |   
key5 | type | int64 | 1 | 0 | 0-消耗道具 1-消耗金币  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=enter_ava_battle_map&key0=123&key1=123&key2=1230123&key3=123&key4=123&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战move-退出战场

  * **命令字** **_leave_ava_battle_map_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | battle_type | int64 | 123 | 1 |   
key1 | item_id | uint32 | 123 | 1 |   
key2 | gem_cost | int64 | 123 | 1 |   
key3 | type | uint32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=leave_ava_battle_map&key0=123&key1=123&key2=123&key3=1

  * **备注**



> 需要等待, 取新协议字段out_ava_battle_wait_time作为等待时间, 需要多次重试, 直到out_ava_battle_wait_time为0代表退出成功, 再进行后续操作; 需要有重试上限, 到达上限还未成功, 直接报错

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 联盟战move-踢出战场

  * **命令字** **_kick_out_ava_battle_map_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | kick_out_user_id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=kick_out_ava_battle_map&key0=123

  * **备注**



> 同退出战场…

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.115.联盟日常活动

* * *

#### 联盟日常活动-领取联盟日常活动任务

  * **命令字** **_receive_al_event_task_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | task_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=receive_al_event_task&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

#### 联盟日常活动-领取联盟日常活动任务奖励

  * **命令字** **_collect_al_event_task_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | task_id | int32 | 1 | 1 |   
key1 | event_type | int32 | 1 | 1 |   
key2 | event_id | int64 | 1122 | 1 |   
key3 | event_id | string | 2323_2323 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=collect_al_event_task_reward&key0=1&key1=1&key2=1122&key3=2323_2323

  * **改动历史**

版本号 | 说明  
---|---  
v1.4.0 | 新增接口  
  
* * *

### 7.116.联盟皮肤

* * *

#### 联盟皮肤-皮肤激活

  * **命令字** **_al_skin_active_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_skin_active&key0=1

  * **备注**



> user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.9 | 新增接口  
  
* * *

#### 联盟皮肤-皮肤穿戴

  * **命令字** **_al_skin_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | skin_id | int64 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_skin_put_on&key0=12

  * **备注**



> user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.9 | 新增接口  
  
* * *

### 7.117.联盟研究

* * *

#### 联盟研究-科技捐献

  * **命令字** **_al_research_donate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | research_id | int32 | 1 | 1 |   
key1 | research_lv | int32 | 1 | 1 |   
key2 | research_stage | int32 | 1 | 1 |   
key3 | donate_type | int32 | 1 | 1 | 0-资源捐献，1-金块捐献  
key4 | donate_num | int64 | 1 | 0 | 不传默认1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_research_donate&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟研究-科技升级

  * **命令字** **_al_research_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | research_id | int64 | 1 | 1 |   
key1 | target_lv | int64 | 1 | 1 | 目标等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_research_upgrade&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟研究-科技推荐

  * **命令字** **_al_research_recommand_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 0:add、1:del  
key1 | research_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_research_recommand&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟研究-科技捐献重置次数

  * **命令字** **_al_research_donate_reset_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost_gold | int32 | 1 | 1 | gold为0是消耗item，不为0时消耗金币  
key1 | item_id | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_research_donate_reset&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 联盟研究-联盟科技快速捐献

  * **命令字** **_al_research_donate_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | research_id | int32 | 1 | 1 |   
key1 | research_lv | int32 | 1 | 1 |   
key2 | research_stage | int32 | 1 | 1 |   
key3 | donate_type | int32 | 1 | 1 | 0-资源捐献，1-金块捐献  
key4 | donate_num | int64 | 1 | 0 | 不传默认1  
key5 | 重置次数所需消耗的重置道具 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_research_donate_batch&key0=1&key1=1&key2=1&key3=1&key4=1&key5=[{“a”:[1,0,1000]}]

  * **备注**



> rsp_type：user json 注意目前只支持资源捐献类型, 捐献数量不能大于剩余捐献数量+重置道具个数*单次重置量

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

### 7.118.联盟礼物

* * *

#### 联盟礼物-打开联盟礼物

  * **命令字** **_al_gift_open_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 礼物类型(1普通，2稀有)  
key1 | gift_id | int64 | 1 | 1 | 后台给的唯一id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_gift_open_new&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

#### 联盟礼物-批量打开联盟礼物

  * **命令字** **_al_gift_open_all_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 |   
key1 | gift_id:gift_id:gift_id… | string | 1:2:3 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_gift_open_all_new&key0=1&key1=1:2:3

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

#### 联盟礼物-清除联盟礼物

  * **命令字** **_al_gift_clear_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 礼物类型(1普通，2稀有)  
key1 | gift_id | int64 | 1 | 1 | 后台给的唯一id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_gift_clear_new&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

#### 联盟礼物-清除全部联盟礼物

  * **命令字** **_al_gift_clear_all_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int32 | 1 | 1 | 礼物类型(1普通，2稀有)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_gift_clear_all_new&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

#### 联盟礼物-设置联盟礼物匿名状态

  * **命令字** **_set_al_gift_nameless_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | is_nameless | int32 | 1 | 1 | 匿名状态1是 0否  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_al_gift_nameless&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

#### 联盟礼物-获取联盟礼物

  * **命令字** **_al_gift_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_gift_get

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.15 | 新增接口  
  
* * *

#### 联盟礼物-打开多个联盟礼物

  * **命令字** **_open_all_al_gift_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | id_list(联盟礼物id列表,用:分隔) | string | 1:2:3 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=open_all_al_gift&key0=1:2:3

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.15 | 新增接口  
  
* * *

#### 联盟礼物-赠送联盟礼物

  * **命令字** **_present_al_gift_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int64 | 1 | 1 | 目标玩家uid  
key1 | item_id | int32 | 1 | 1 |   
key2 | item_num | int32 | 1 | 1 |   
key3 | gem_cost | int64 | 1 | 1 | 消耗钻石总数  
key4 | greeting_msg | string | dffgdf | 1 | 招呼语  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=present_al_gift&key0=1&key1=1&key2=1&key3=1&key4=dffgdf

  * **改动历史**

版本号 | 说明  
---|---  
v3.5.1 | 新增接口  
  
* * *

### 7.119.联盟资源帮助

* * *

#### 联盟资源帮助-发送联盟assist

  * **命令字** **_al_assist_send_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | assist_type | int8 | 1 | 1 | (见枚举)  
key1 | resource | string | 1:2:3 | 1 | (以:隔开)  
key2 | cid | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_assist_send&key0=1&key1=1:2:3&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.17 | 新增接口  
  
* * *

#### 联盟资源帮助-获取联盟assist

  * **命令字** **_al_assist_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_assist_get

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.17 | 新增接口  
  
* * *

#### 联盟资源帮助-删除联盟assist

  * **命令字** **_al_assist_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | assist_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_assist_del&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.17 | 新增接口  
  
* * *

### 7.120.英雄

* * *

#### 英雄-获取/升星牛仔

  * **命令字** **_cowboy_star_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 牛仔id | TINT64 | 1021 | 1 |   
key1 | 目标星级 | TINT64 | 2 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_star_upgrade&key0=1021&key1=2

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
v2.0 | 作废，不可删除  
  
* * *

#### 英雄-设置骑士驻防

  * **命令字** **_set_city_defender_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 牛仔列表 | TINT64:TINT64:TINT64:TINT64:TINT64 | 1020:1021:1024:1023:1036 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_city_defender&key0=1020:1021:1024:1023:1036

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-牛仔改名

  * **命令字** **_cowboy_change_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 牛仔id | TINT64 | 34 | 1 |   
key1 | 牛仔名 | string | cowboy_new_name | 1 |   
key2 | 金币消耗 | TINT64 | 111 | 1 |   
key3 | 改名卡id | TINT32 | 12 | 1 |   
key4 | 类型 | TINT32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_change_name&key0=34&key1=cowboy_new_name&key2=111&key3=12&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-碎片换钱

  * **命令字** **_sell_cowboy_piece_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 碎片id | TINT64 | 34 | 1 |   
key1 | 数量 | TINT64 | 1 | 1 |   
key2 | 时代 | TINT64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=sell_cowboy_piece&key0=34&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-开启碎片宝箱

  * **命令字** **_open_cowboy_piece_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 宝箱类型 | TUINT32 | 34 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=open_cowboy_piece_chest&key0=34

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-领取羁绊奖励

  * **命令字** **_cowboy_claim_fetters_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 牛仔羁绊id | TINT64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_claim_fetters_reward&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v5.1 | 新增接口  
  
* * *

#### 英雄-熟练度等级提升

  * **命令字** **_cowboy_proficiency_lv_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 牛仔id | TINT64 | 34 | 1 |   
key1 | 目标等级 | TINT64 | 5 | 1 |   
key2 | 消耗材料 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_proficiency_lv_upgrade&key0=34&key1=5&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v5.1 | 新增接口  
  
* * *

#### 英雄-牛仔升阶/升星

  * **命令字** **_cowboy_star_stage_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_id | int64 | 1 | 1 |   
key1 | target_star_lv | int64 | 1 | 1 | 目标星级  
key2 | target_stage_lv | int64 | 1 | 1 | 目标阶级  
key3 | piece_id | int64 | 1 | 1 |   
key4 | piece_num | int64 | 1 | 1 | 消耗的碎片数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_star_stage_upgrade&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-牛仔技能升级

  * **命令字** **_cowboy_star_skill_upgrade_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_id | int64 | 1 | 1 |   
key1 | skill_star_lv | int64 | 1 | 1 | 技能星级  
key2 | target_skill_lv | int64 | 1 | 1 | 目标技能等级  
key3 | item_id | int64 | 1 | 1 | 技能书id  
key4 | book_num | int64 | 1 | 1 | 消耗的技能书数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_star_skill_upgrade&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-牛仔解锁

  * **命令字** **_cowboy_unlock_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_id | int64 | 1 | 1 |   
key1 | piece_id | int64 | 1 | 1 |   
key2 | piece_num | int64 | 1 | 1 | 消耗的碎片数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_unlock&key0=1&key1=1&key2=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-设置cowboy展示槽位

  * **命令字** **_set_cowboy_slot_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | str_cowboy_id | string | 1,2,3 | 1 | 将所有cowboyid用,隔开，槽位对应为1,2,3,4,5  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_cowboy_slot&key0=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-cowboy狂化

  * **命令字** **_set_cowboy_berserker_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_id | int64 | 1 | 1 |   
key1 | item_id | int64 | 1 | 1 |   
key2 | num | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_cowboy_berserker&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-牛仔万能碎片交换

  * **命令字** **_cowboy_universal_piece_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | universal_piece_id | int64 | 1 | 1 |   
key1 | cost num | int64 | 1 | 1 |   
key2 | exchange_piece_id | int64 | 1 | 1 |   
key3 | exchange_num | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_universal_piece_exchange&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

#### 英雄-开牛仔箱子

  * **命令字** **_open_cowboy_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | chest_type | int32 | 1 | 1 |   
key1 | open_type | int32 | 1 | 1 | 0->free, 1->cost_item, 2->cost_gem  
key2 | gem_cost | int32 | 1 | 1 | open_type为2时候有效，总消耗  
key3 | item_num | int32 | 1 | 0 | 开箱个数，如果不传默认为1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=open_cowboy_chest&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.3.0 | 新增接口  
  
* * *

#### 英雄-建立师徒关系-废弃

  * **命令字** **_establish_cowboy_mentorship_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mentorship_id | int32 | 1 | 1 | 关系id  
key1 | mentor_cowboy_id | int32 | 1 | 1 | 导师id  
key2 | mentee_cowboy_id | int32 | 1 | 1 | 学生id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=establish_cowboy_mentorship&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.9.1 | 新增接口  
  
* * *

#### 英雄-设置牛仔传承-废弃

  * **命令字** **_set_cowboy_relation_ship_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | int32 | 1 | 1 | 槽位id  
key1 | cowboy_id | int64 | 1 | 1 | 牛仔id 传-1代表把该位置的英雄下阵  
key2 | type | int32 | 1 | 1 | 1 传承方 2 接收传承方  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_cowboy_relation_ship&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.7 | 新增接口  
  
* * *

#### 英雄-解除牛仔传承-废弃

  * **命令字** **_cancel_cowboy_relation_ship_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | int32 | 1 | 1 | 槽位id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cancel_cowboy_relation_ship&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.7 | 新增接口  
  
* * *

#### 英雄-牛仔传承-（招募）

  * **命令字** **_cowboy_unlock_relation_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_id | int64 | 1 | 1 |   
key1 | 传承消耗碎片 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key2 | relation_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_unlock_relation&key0=1&key1=[{“a”:[1,0,1000]}]&key2=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 英雄-牛仔图鉴奖励领取

  * **命令字** **_cowboy_gallery_claim_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_rank | int64 | 1 | 1 | 领取军衔  
key1 | cowboy_star | int64 | 1 | 1 | 领取总星数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=cowboy_gallery_claim_reward&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.1 | 新增接口  
  
* * *

### 7.121.藏宝图

* * *

#### 藏宝图-藏宝图转化

  * **命令字** **_identify_monster_essence_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | int64 | 123456 | 1 | 位置id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=identify_monster_essence&key0=123456

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 藏宝图-藏宝图删除

  * **命令字** **_delete_monster_essence_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | int64 | 123456 | 1 | 位置id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=delete_monster_essence&key0=123456

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 藏宝图-藏宝图奖励领取

  * **命令字** **_collect_monster_essence_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | slot_id | int64 | 123456 | 1 | 位置id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=collect_monster_essence&key0=123456

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 藏宝图-设置藏宝图接受等级上限

  * **命令字** **_set_monster_essence_lv_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | level | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_monster_essence_lv&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 藏宝图-发起藏宝图帮助队列

  * **命令字** **_help_identify_monster_essence_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int32 | 1 | 1 |   
key1 | target_pos | int32 | 1 | 1 | 目标地块  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=help_identify_monster_essence&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.2 | 新增接口  
  
* * *

#### 藏宝图-获取藏宝图帮助历史

  * **命令字** **_get_monster_essence_helped_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int32 | 1 | 1 | 传自己的uid就可以  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_monster_essence_helped_history&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.2 | 新增接口  
  
* * *

### 7.122.装备

* * *

#### 装备-设置治安官预设装备

  * **命令字** **_set_dragon_plan_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 预设id | int32 | 1 | 1 | 预设编号  
key1 | 装备id | int64 | 1 | 1 |   
key2 | 装备槽位 | int32 | 1 | 1 |   
key3 | 类型 | int32 | 1 | 1 | 0：卸下、1：穿戴  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_dragon_plan_equip&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.8 | 新增接口  
  
* * *

#### 装备-合成灵魂装备

  * **命令字** **_compose_soul_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备类型 | int64 | 1 | 1 |   
key1 | 灵魂id | int64 | 1 | 1 |   
key2 | 碎片id | string | 1 | 1:2:3 | 以:分隔  
key3 | 耗时 | int64 | 1 | 100 |   
key4 | 消耗宝石 | int64 | 1 | 10 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=compose_soul_equip&key0=1&key1=1&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
  
* * *

#### 装备-分解灵魂装备

  * **命令字** **_decompose_soul_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备id | int64 | 1 | 1 |   
key10 | 装备上的水晶 | id,id,id | 1 | 0 | 后台自动生成-表示装备上的水晶  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=decompose_soul_equip&key0=1&key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
  
* * *

#### 装备-合成装备

  * **命令字** **_compose_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备后台id | int32 | 1 | 1 |   
key1 | 装备数值id | int32 | 1 | 1 |   
key2 | 耗时 | int64 | 1 | 1 |   
key3 | 消耗宝石 | int64 | 1 | 1 | 立马完成  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=compose_equip&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
v6.4 | 作废  
  
* * *

#### 装备-装备拆解

  * **命令字** **_equip_destroy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备id | int64 | 1 | 1 |   
key10 | 装备上的水晶 | id,id,id | 1 | 0 | 后台自动生成-表示装备上的水晶  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=equip_destroy&key0=1&key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
  
* * *

#### 装备-穿上装备

  * **命令字** **_put_on_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备id | int64 | 1 | 1 |   
key1 | 槽位 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=put_on_equip&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
  
* * *

#### 装备-脱下装备

  * **命令字** **_put_off_equip_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备id | int64 | 1 | 1 |   
key1 | 槽位 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=put_off_equip&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
  
* * *

#### 装备-增加装备格子

  * **命令字** **_add_equip_grid_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 数量 | int32 | 1 | 1 |   
key1 | 道具id | int32 | 1 | 1 | 必传  
key2 | 消耗类型 | int32 | 1 | 1 | 0宝石、1忠诚度  
key3 | 价格数量 | int64 | 1 | 1 | 传入表示购买并使用Item  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=add_equip_grid&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.20 | 新增接口  
  
* * *

#### 装备-装备强化

  * **命令字** **_set_equipment_berserker_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备id | int32 | 1 | 1 |   
key1 | 道具id | int32 | 1 | 1 | 必传  
key2 | 数量 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_equipment_berserker&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 装备-合成核心

  * **命令字** **_compose_soul_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 原始id | int32 | 123 | 1 |   
key1 | is all | int32 | 123 | 1 | 0表示单个 1表示全部  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=compose_soul&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.4 | 新增接口  
  
* * *

#### 装备-分解核心

  * **命令字** **_decompose_soul_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 原始id | int32 | 123 | 1 |   
key1 | is all | int32 | 123 | 1 | 0表示单个 1表示全部  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=decompose_soul&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.4 | 新增接口  
  
* * *

#### 装备-合成部件

  * **命令字** **_compose_fragment_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 原始id | int32 | 123 | 1 |   
key1 | is all | int32 | 123 | 1 | 0表示单个 1表示全部  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=compose_fragment&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.4 | 新增接口  
  
* * *

#### 装备-分解部件

  * **命令字** **_decompose_fragment_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 原始id | int32 | 123 | 1 |   
key1 | is all | int32 | 123 | 1 | 0表示单个 1表示全部  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=decompose_fragment&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.4 | 新增接口  
  
* * *

#### 装备-合成装备-新

  * **命令字** **_compose_equip_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备后台id | int32 | 1 | 1 |   
key1 | 装备数值id | int32 | 1 | 1 |   
key2 | 耗时 | int64 | 1 | 1 |   
key3 | 消耗宝石 | int64 | 1 | 1 | 立马完成  
key4 | 目标品质 | int32 | 1 | 10 |   
key5 | 目标品阶 | int32 | 1 | 10 | 0-无阶 1-p1 2-p2 3-p3  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=compose_equip_new&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

### 7.123.装备-精英装备

* * *

#### 装备-精英装备-精英装备-重铸

  * **命令字** **_elite_equipment_reforge_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_type | int32 | 1 | 1 | 目标装备类型  
key1 | buff_type | int32 | 1 | 1 | 重铸目标装备的BUFF类型  
key2 | cost_equip_id | int32 | 1 | 1 | 重铸消耗的装备id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_equipment_reforge&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英装备-升星

  * **命令字** **_elite_equipment_upgrade_star_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 目标装备ID  
key1 | target_star | int32 | 1 | 1 | 目标星级  
key2 | cost | json | [{“a”:[0,1,1]}] | 1 | 升星消耗,需要合并相同项  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_equipment_upgrade_star&key0=1&key1=1&key2=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英装备-升阶

  * **命令字** **_elite_equipment_upgrade_stage_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 目标装备ID  
key1 | target_stage | int32 | 1 | 1 | 目标阶级  
key2 | cost | json | [{“a”:[0,1,1]}] | 1 | 升阶消耗,需要合并相同项  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_equipment_upgrade_stage&key0=1&key1=1&key2=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英装备-升级

  * **命令字** **_elite_equipment_upgrade_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 目标装备ID  
key1 | target_level | int32 | 1 | 1 | 目标等级  
key2 | cost | json | [{“a”:[0,1,1]}] | 1 | 升级消耗,需要合并相同项  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_equipment_upgrade_level&key0=1&key1=1&key2=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英装备-切换BUFF

  * **命令字** **_elite_equipment_change_buff_type_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 目标装备ID  
key1 | target_buff_type | int32 | 1 | 1 | 目标buff type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_equipment_change_buff_type&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英水晶-解锁

  * **命令字** **_elite_crystal_unlock_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 精英装备ID  
key1 | crystal_id | int32 | 1 | 1 | 水晶ID  
key2 | target_buff_type | int32 | 1 | 1 | 目标buff type  
key3 | cost | json | [{“a”:[0,1,1]}] | 1 | 消耗,需要合并相同项  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_crystal_unlock&key0=1&key1=1&key2=1&key3=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英水晶-升级

  * **命令字** **_elite_crystal_upgrade_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 精英装备ID  
key1 | crystal_id | int32 | 1 | 1 | 水晶ID  
key2 | target_level | int32 | 1 | 1 | 目标等级  
key3 | cost | json | [{“a”:[0,1,1]}] | 1 | 消耗,需要合并相同项  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_crystal_upgrade_level&key0=1&key1=1&key2=1&key3=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英水晶-切换BUFF

  * **命令字** **_elite_crystal_change_buff_type_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | equip_id | int32 | 1 | 1 | 目标装备ID  
key1 | crystal_id | int32 | 1 | 1 | 水晶ID  
key2 | target_buff_type | int32 | 1 | 1 | 目标buff type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=elite_crystal_change_buff_type&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

#### 装备-精英装备-精英装备水晶-切换预设BUFF

  * **命令字** **_dragon_plan_change_buff_type_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dragon_plan_id | int32 | 1 | 1 | 预设ID  
key1 | change_list | json | {xxx} | 1 | 目标装备ID  
key2 | target_buff_type | int32 | 1 | 1 | 目标buff type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=dragon_plan_change_buff_type&key0=1&key1={xxx}&key2=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-1)//change_list
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-2){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-3)    "equip_id": // 装备id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-4)    {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-5)        "is_change": int, // 0 不设置自己 1 设置自己
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-6)        "crystal_list: [int] // 改动的水晶列表
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-7)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb77-8)}

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.124.装备preset

* * *

#### 装备preset-预设改名

  * **命令字** **_set_crystal_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | plan_name | string | xxxxxx | 1 | 预设名  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_crystal_plan_name&key0=1&key1=xxxxxx

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### 装备preset-设置预设

  * **命令字** **_set_crystal_paln_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 12 | 1 | 预设编号  
key1 | crystal_id | int32 | 12 | 1 | 水晶编号  
key2 | pos | int32 | 1 | 1 | 预设的第几个位置  
key3 | type | int32 | 1 | 1 | 0-卸下，1-装备  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_crystal_paln&key0=12&key1=12&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### 装备preset-切换预设

  * **命令字** **_change_crystal_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 12 | 1 | 预设编号  
key1 | equip_id | int64 | 123 | 1 | 装备编号  
key2 | item_list | string | 1:2:3 | 1 | 消耗物品列表，类型为string,格式为: item_id1:item_id2:item_id3:item_id4:0  
key3 | price_num | int64 | 123 | 1 | 消耗的货币数  
key4 | real_cost_item_list | json | [{“a”:[0,1,1]}] | 1 | 实际消耗的物品列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_crystal_plan&key0=12&key1=123&key2=1:2:3&key3=123&key4=[{“a”:[0,1,1]}]

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
v7.1.2 | 修改接口-key2 传入玩家实际消耗的item即可  
  
* * *

#### 装备preset-重置预设

  * **命令字** **_reset_crystal_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_crystal_plan&key0=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

### 7.125.西部军校

* * *

#### 西部军校-教官招募

  * **命令字** **_instructor_recruit_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 教官id | TUINT32 | 1021 | 1 |   
key1 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_recruit&key0=1021&key1=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官升星

  * **命令字** **_instructor_upgrade_star_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 教官id | TUINT32 | 1021 | 1 |   
key1 | 目标星级 | TUINT32 | 2 | 1 |   
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_upgrade_star&key0=1021&key1=2&key2=[{“a”:[1,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官天赋解锁

  * **命令字** **_instructor_talent_unlock_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 教官id | TUINT32 | 1021 | 1 |   
key1 | 天赋id | TUINT32 | 22 | 1 |   
key2 | 所需天赋点 | TUINT32 | 3 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_talent_unlock&key0=1021&key1=22&key2=3

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官天赋升级

  * **命令字** **_instructor_talent_upgrade_level_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 教官id | TUINT32 | 1021 | 1 |   
key1 | 天赋id | TINT64 | 22 | 1 |   
key2 | 所需碎片资源 | [{“a”:[int64,int64,int64]}] | [{“a”:[1,0,1000]}] | 1 | 通用reward格式  
key15 | instructor_talent_id | 1001 | 1 | 0 | 后台自动生成-升级的教官天赋id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_talent_upgrade_level&key0=1021&key1=22&key2=[{“a”:[1,0,1000]}]&key15=1

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-抽卡

  * **命令字** **_instructor_open_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 调令类型 | TUINT32 | 1 | 1 |   
key1 | 打开类型 | TUINT32 | 1 | 1 |   
key2 | 花费宝石数量 | TUINT32 | 100 | 1 |   
key3 | 印章id | TUINT32 | 1313 | 1 |   
key4 | 单次花费数据 | TUINT32 | 1 | 1 |   
key5 | 开箱子个数 | TUINT32 | 10 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_open_chest&key0=1&key1=1&key2=100&key3=1313&key4=1&key5=10

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-碎片兑换

  * **命令字** **_instructor_universal_piece_exchange_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 万能教官碎片id | TINT64 | 121 | 1 |   
key1 | 万能教官碎片数量 | TINT64 | 21 | 1 |   
key2 | 目标教官碎片id | TINT64 | 122 | 1 |   
key3 | 目标教官碎片数量 | TINT64 | 21 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_universal_piece_exchange&key0=121&key1=21&key2=122&key3=21

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-修改教官升级天赋区间

  * **命令字** **_instructor_talent_change_upgrade_range_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 教官id | TUINT32 | 1021 | 1 |   
key1 | 要改变右区间 | TUINT32 | 10 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_talent_change_upgrade_range&key0=1021&key1=10

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官任命

  * **命令字** **_instructor_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备槽位 | TUINT32 | 2 | 1 |   
key1 | 教官id | TUINT32 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_put_on&key0=2&key1=1021

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官卸任

  * **命令字** **_instructor_put_off_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备槽位 | TUINT32 | 2 | 1 |   
key1 | 教官id | TUINT32 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_put_off&key0=2&key1=1021

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官替换

  * **命令字** **_instructor_replace_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备槽位 | TUINT32 | 2 | 1 |   
key1 | 教官id | TUINT32 | 1021 | 1 |   
key2 | 目标教官id | TUINT32 | 1022 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_replace&key0=2&key1=1021&key2=1022

  * **改动历史**

版本号 | 说明  
---|---  
v4.2 | 新增接口  
  
* * *

#### 西部军校-教官组任命

  * **命令字** **_instructor_group_put_on_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 要装备组id | TUINT32 | 0 | 1 |   
key1 | 装备组pos | TUINT32 | 0 | 1 |   
key2 | 教官id | TUINT32 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_put_on&key0=0&key1=0&key2=1021

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校-教官组卸任

  * **命令字** **_instructor_group_put_off_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 要装备组id | TUINT32 | 0 | 1 |   
key1 | 装备组pos | TUINT32 | 0 | 1 |   
key2 | 教官id | TUINT32 | 1021 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_put_off&key0=0&key1=0&key2=1021

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校-教官组替换

  * **命令字** **_instructor_group_replace_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 要装备组id | TUINT32 | 0 | 1 |   
key1 | 装备组pos | TUINT32 | 0 | 1 |   
key2 | 教官id | TUINT32 | 1021 | 1 |   
key3 | 目标教官id | TUINT32 | 1022 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_replace&key0=0&key1=0&key2=1021&key3=1022

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校-教官组主阵容切换

  * **命令字** **_instructor_group_main_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 装备组id | TUINT32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_main_switch&key0=0

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校-设置教官展示槽位

  * **命令字** **_set_instructor_slot_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | str_instructor_id | string | 1,2,3 | 1 | 将所有instructorid用,隔开，槽位对应为1,2,3,4,5  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_instructor_slot&key0=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校-教官低级天赋一键解锁

  * **命令字** **_instructor_talent_lower_batch_unlock_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 教官id | TUINT32 | 1021 | 1 | 要求是满等级满军衔的教官  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_talent_lower_batch_unlock&key0=1021

  * **改动历史**

版本号 | 说明  
---|---  
v7.1 | 新增接口  
  
* * *

### 7.126.西部军校预设

* * *

#### 西部军校预设-预设改名

  * **命令字** **_set_instructor_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | plan_name | string | dsrfds | 1 | 预设名  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_instructor_plan_name&key0=1&key1=dsrfds

  * **改动历史**

版本号 | 说明  
---|---  
v5.3 | 新增接口  
  
* * *

#### 西部军校预设-修改预设

  * **命令字** **_set_instructor_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | instructor_id | int32 | 1 | 1 |   
key2 | dwPos | int32 | 1 | 1 |   
key3 | dwType | int32 | 1 | 1 | 1-装备 2-卸下  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_instructor_plan&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.3 | 新增接口  
  
* * *

#### 西部军校预设-重置预设

  * **命令字** **_reset_instructor_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=reset_instructor_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.3 | 新增接口  
  
* * *

#### 西部军校预设-使用预设

  * **命令字** **_change_instructor_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=change_instructor_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.3 | 新增接口  
  
* * *

#### 西部军校预设-组预设改名

  * **命令字** **_instructor_group_set_plan_name_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | plan_name | string | dsrfds | 1 | 预设名  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_set_plan_name&key0=1&key1=dsrfds

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校预设-组预设设置主教官

  * **命令字** **_instructor_group_set_plan_main_instructor_group_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | group_id | int32 | 1 | 1 | 预设组  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_set_plan_main_instructor_group&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校预设-修改组预设

  * **命令字** **_instructor_group_set_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
key1 | group_id | int32 | 1 | 1 | 预设组  
key2 | pos | int32 | 1 | 1 | 预设位置  
key3 | instructor_id | int32 | 1 | 1 |   
key4 | dwType | int32 | 1 | 1 | 1-装备 2-卸下  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_set_plan&key0=1&key1=1&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校预设-重置组预设

  * **命令字** **_instructor_group_reset_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_reset_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

#### 西部军校预设-使用组预设

  * **命令字** **_instructor_group_change_plan_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | plan_id | int32 | 1 | 1 | 预设编号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=instructor_group_change_plan&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.9 | 新增接口  
  
* * *

### 7.127.订阅

* * *

#### 订阅-发起订阅

  * **命令字** **_iap_subscription_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | gems | int64 | 100 | 1 | 运营要…后台不用也不知道有啥用…  
key1 | project_id | int64 | 1 | 1 |   
receipt | receipt | string | ios | 1 | ios  
transaction | transaction | string | ios | 1 | ios  
product_id | product_id | string | 121 | 1 | ios  
purchase_token | purchase_token | string | android | 1 | android  
package_name | package_name | string | android | 1 | android  
subscription_id | subscription_id | string | android | 1 | android  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=iap_subscription&key0=100&key1=1&receipt=ios&transaction=ios&product_id=121&purchase_token=android&package_name=android&subscription_id=android

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 订阅-获取订阅奖励

  * **命令字** **_get_subscription_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_subscription_reward

  * **备注**



> ps: 当前可领, 但是没有奖励的时候发起…

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 订阅-收集订阅奖励

  * **命令字** **_collect_subscription_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=collect_subscription_reward

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

#### 订阅-订阅补单

  * **命令字** **_op_iap_subscription_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
user_id | user_id | int64 | 111 | 1 |   
product_id | product_id | string | 121 | 1 | ios  
transaction | transaction | string | ios | 1 | ios  
receipt | receipt | string | ios | 1 | ios  
purchase_token | purchase_token | string | android | 1 | android  
package_name | package_name | string | android | 1 | android  
order_id | order_id | string | android | 1 | android  
subscription_id | subscription_id | string | android | 1 | android  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_iap_subscription_new&user_id=111&product_id=121&transaction=ios&receipt=ios&purchase_token=android&package_name=android&order_id=android&subscription_id=android

  * **改动历史**

版本号 | 说明  
---|---  
v1.2.1 | 新增接口  
  
* * *

### 7.128.资源

* * *

#### 资源-资源转化

  * **命令字** **_resource_transform_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | original_id | int64 | 1 | 1 |   
key1 | original_num | int64 | 1 | 1 |   
key2 | target_id | int64 | 1 | 1 |   
key3 | target_num | int64 | 1 | 1 |   
key4 | cost_time | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=resource_transform&key0=1&key1=1&key2=1&key3=1&key4=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.8 | 新增接口  
  
* * *

### 7.129.赠送礼物

* * *

#### 赠送礼物-赠送礼物

  * **命令字** **_give_gift_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | gift_id | string | 1 | 1 |   
key1 | content | string | dsfgs | 1 |   
key2 | uid_list | string | 1:2:3 | 1 | (:分隔)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=give_gift&key0=1&key1=dsfgs&key2=1:2:3

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.51 | 新增接口  
  
* * *

#### 赠送礼物-新赠礼

  * **命令字** **_send_gift_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_uid | int64 | 1 | 1 |   
key1 | target_form | int32 | 1 | 1 | 对方成分,0->盟友,1->聊天好友  
key2 | scene | int32 | 1 | 1 | 赠送的场景,0->寻常,1->活动中  
key3 | scene_detail | int32 | 1 | 1 | 场景细节, 寻常则传0, 活动中则传event_type  
key4 | gift_reward | json | [{“a”:[int,int,int]}] | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=send_gift_new&key0=1&key1=1&key2=1&key3=1&key4=[{“a”:[int,int,int]}]

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.2 | 新增接口  
  
* * *

### 7.130.超级王座

* * *

#### 超级王座-捐献资源

  * **命令字** **_skvk_mobilize_donate_rss_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | rsstype | int32 | 123 | 1 |   
key1 | ddwrssnum | int64 | 123 | 1 | 捐赠总资源数  
key2 | strclienteventid | string | 123 | 1 |   
key3 | ddwdonatenum | int64 | 123 | 1 | 捐赠次数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skvk_mobilize_donate_rss&key0=123&key1=123&key2=123&key3=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-购买次数

  * **命令字** **_skvk_mobilize_donate_buy_num_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwgemnum | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skvk_mobilize_donate_buy_num&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-领取奖励

  * **命令字** **_skvk_prepare_collect_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | seventid | string | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skvk_prepare_collect_reward&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-任命大帝 //活动调用

  * **命令字** **_op_appoint_emperor_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | streventid | string | 123 | 1 |   
key1 | ddwuid | int64 | 123 | 1 |   
key2 | dwoccupytime | int64 | 123 | 1 | 累计占领时长  
key3 | 0 |  | 0 | 1 | 活动固定传0  
key4 | strsidlist | string | 1,2,3 | 1 | 本场活动，帝王录参赛sid list,格式sid,sid,sid  
key5 | dwbalance_emperor | int64 | 1 | 1 | 0 表示不结算大帝称号， 1结算大帝称号  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_appoint_emperor&key0=123&key1=123&key2=123&key3=0&key4=1,2,3&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-捐赠

  * **命令字** **_skvk_encourage_donate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target sid | nt64 | 12 | 1 |   
key1 | type | int64 | 2 | 1 | 2:步兵攻击榜 3:远程兵攻击榜 4:骑兵攻击榜 5:银榜 (超级王座) 6:步兵攻击榜 7:远程兵攻击榜 8:骑兵攻击榜 9:银榜(铁王座)  
key2 | item id | int64 | 123 | 1 |   
key3 | num | int64 | 12 | 1 | 捐赠数量  
key4 | evnet_id | string | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skvk_encourage_donate&key0=12&key1=2&key2=123&key3=12&key4=123

  * **备注**



> rsp_type: user_json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-领取贡献奖励

  * **命令字** **_skvk_encourage_collect_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwType | int32 | 1 | 1 | 传入5为银榜，否则金榜  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skvk_encourage_collect_reward&key0=1

  * **备注**



> rsp_type: user_json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-大帝赏赐

  * **命令字** **_skvk_emperor_send_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | gift lv | int32 | 123 | 1 |   
key2 | aid | int32 | 123 | 1 |   
key3 | sid | int32 | 2 | 1 |   
key4 | uname | string | 123 | 1 |   
key5 | alname | string | 123 | 1 |   
key6 | alnick | string | 123 | 1 |   
key7 | avatar | int32 | 123 | 1 |   
key8 | force | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=skvk_emperor_send_reward&key0=123&key1=123&key2=123&key3=2&key4=123&key5=123&key6=123&key7=123&key8=123

  * **备注**



> rsp_type: user_json

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-拉取赏赐历史记录

  * **命令字** **_get_skvk_emperor_reward_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_skvk_emperor_reward_history

  * **备注**



> rsp_type: throne json svr_skvk_emperor_reward_record |key0|sid (超级王座传100，铁王座传王座sid)|stringuint32|123|1||

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-拉取大帝历史记录

  * **命令字** **_get_skvk_emperor_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 战场所在sid | stringuint32 | 123 | 1 | 超级王座是100，铁王座为对应sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_skvk_emperor_history&key0=123

  * **备注**



> rsp_type: throne json svr_skvk_emperor_history

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-活动准备 //活动调用

  * **命令字** **_op_skvk_prepare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | begin time | int64 | 123 | 1 | 王座争夺阶段开始时间  
key1 | end time | int64 | 123 | 1 | 王座争夺阶段结束时间  
key3 | forcast time | int64 | 123 | 1 | 王座争夺阶段预告时间  
key4 | strSidList | string | 100,100 | 1 | sid列表,分隔  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_skvk_prepare&key0=123&key1=123&key3=123&key4=100,100

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-拉取战况

  * **命令字** **_get_skvk_war_situation_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 123 | 1 |   
key1 | uid | int64 | 123 | 1 |   
key2 | sid | int64 | 123 | 1 | (传所在王座服sid，例如超级王座则为100)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_skvk_war_situation&key0=123&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座-设置超级王座公告板

  * **命令字** **_set_super_building_notice_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 12 | 1 |   
key1 | pos | int64 | 1230123 | 1 |   
key2 | notice | string | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=set_super_building_notice&key0=12&key1=1230123&key2=123

  * **备注**



> rsp_type:throne json svr_map_building_detail_info

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

### 7.131.超级王座map

* * *

#### 超级王座map-生成建筑 //后台使用

  * **命令字** **_op_gen_super_building_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | type | int64 | 1 | 1 | 0:add 1:del 2:fix  
key1 | sid | int64 | 123 | 1 |   
key2 | building id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_super_building&key0=1&key1=123&key2=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座map-设置和平期 //后台使用

  * **命令字** **_op_set_super_building_peace_time_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 123 | 1 |   
key1 | pos | int64 | 1230123 | 1 |   
key2 | type | int64 | 1 | 1 | 0:end time 1:time unix  
key3 | time | int64 | 12312321 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_super_building_peace_time&key0=123&key1=1230123&key2=1&key3=12312321

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

### 7.132.超级王座title

* * *

#### 超级王座title-赋予个人超级title

  * **命令字** **_super_throne_dub_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | uint32 | 123 | 1 |   
key1 | title id | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=super_throne_dub_title&key0=123&key1=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

#### 超级王座title-赋予服务器title

  * **命令字** **_super_throne_dub_kingdom_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target sid | uint32 | 123 | 1 |   
key1 | title id | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=super_throne_dub_kingdom_title&key0=123&key1=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v2.5 | 新增接口  
  
* * *

### 7.133.转盘活动

* * *

#### 转盘活动-选择大奖

  * **命令字** **_select_lucky_big_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动type | int32 | 1 | 1 |   
key1 | 活动id | int64 | 1 | 1 |   
key2 | 选择的大奖的index | int32 | 1 | 1 |   
key3 | 活动id | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=select_lucky_big_reward&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 转盘活动-抽奖

  * **命令字** **_luck_draw_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动type | int32 | 1 | 1 |   
key1 | 活动id | int64 | 1 | 1 |   
key2 | 抽奖次数 | int32 | 1 | 1 |   
key3 | 消耗 | json_string | 1 | [type,id,num] |   
key4 | 消耗宝石 | int64 | 1 | 10 |   
key5 | draw_type | int64 | 1 | 10 |   
key6 | 活动id | string | 1 | “xxxxx” |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=luck_draw&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1&key6=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 转盘活动-洗牌

  * **命令字** **_lucky_card_shuffle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 活动id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=lucky_card_shuffle&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 转盘活动-领取活动奖励

  * **命令字** **_iap_chest_collect_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 任务id | int32 | 1 | 1 |   
key1 | 活动type | int32 | 1 | 1 |   
key2 | 活动id | int64 | 1 | 1 |   
key3 | 活动id | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=iap_chest_collect_reward&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
v5.2 | 新增支持成长阶梯活动  
  
* * *

### 7.134.运营开发用

* * *

#### 运营开发用-新实时推送接口

  * **命令字** **_push_data_common_json_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | push_type | int | 1 | 1 |   
key1 | id_list | string | 123:465:234 | 1 | (:分隔)  
key2 | push_data | json_string | {} | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=push_data_common_json&key0=1&key1=123:465:234&key2={}

  * **推送类型说明**

push_type | 含义  
---|---  
1 | uid  
2 | sid  
3 | aid  
4 | sid+地块block_id  
5 | 页面场景  
6 | 聊天场景  
7 | 水晶岛小队  
8 | {副本id}_{阵营id}  
  
  * **push data**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb78-1){  //示例
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb78-2)    "svr_xxx":    //表名
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb78-3)    {
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb78-4)        //表数据
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb78-5)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb78-6)}

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 运营开发用-新发送系统消息接口

  * **命令字** **_op_send_sys_msg_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | channel_id | string | 1 | 1 |   
key1 | sys_msg | string | xxxx | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_send_sys_msg&key0=1&key1=xxxx

  * **频道id说明** |channel_id|含义| |–|–| |circusteam_gid_tid|马戏团频道id|

  * **sys_msg说明** |sys_msg|含义| |–|–| |type(43)#uid#uname#timeunix|创建小队| |type(44)#uid#uname#timeunix|加入小队| |type(45)#uid#uname#timeunix|离开小队|

  * **改动历史**


版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

### 7.135.远征副本

* * *

#### 远征副本-开始攻打远征副本

  * **命令字** **_expedition_enter_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | stage_id | int64 | 1 | 1 |   
key1 | team | string | 213dsf | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=expedition_enter&key0=1&key1=213dsf

  * **备注**



> key1={“t”:[{“c”:[1,2,3],”t”:{“1”:1,”2”:1},”g”:1},{“c”:[4,0,5,0,6],”t”:{“1”:1,”2”:1},”g”:0}]}  
>  派兵信息, c为牛仔，第一位为大帅，其余为副将，t为兵力，g为是否有治安官1为有，0为无

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

#### 远征副本-结束攻打副本

  * **命令字** **_expedition_finish_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | stage_id | int64 | 1 | 1 |   
key1 | star | int32 | 1 | 1 |   
key2 | battle_seed | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=expedition_finish&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

#### 远征副本-副本每日奖励

  * **命令字** **_claim_expedition_daily_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | stage_id_list | string | 1,2 | 1 | stage_id,stage_id  
key1 | claim_all | int32 | 0 | 1 | 0-领取指定关卡,1-全部领取,置1后,key0可以为空  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_expedition_daily_reward&key0=1,2&key1=0

  * **改动历史**

版本号 | 说明  
---|---  
v2.8.1 | 新增接口  
  
* * *

### 7.136.通用map

* * *

#### 通用map-地图搜索

  * **命令字** **_map_search_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | wild_class | uint32 | 1 | 1 | 野地类型, 见wild_res.txt  
key1 | wild_type | uint32 | 1 | 1 | 类型id, 见wild_res.txt  
key2 | level | int32 | 1 | 1 |   
key3 | city_pos | uint32 | 1230123 | 1 | city position  
key4 | pos_list | string | 1230123,1230123 | 1 | pos,pos,pos,pos  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_search&key0=1&key1=1&key2=1&key3=1230123&key4=1230123,1230123

  * **备注**



> 上一次搜索的pos列表,为空表示重新搜索,列表不为空, 后台将负责帮助客户端过滤不符合搜索条件的数据

  * **改动历史**

版本号 | 说明  
---|---  
v2.7 | 新增接口  
  
* * *

#### 通用map-拉取地形建筑信息

  * **命令字** **_get_map_building_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 |   
key1 | pos | int64 | 1230123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_map_building_info&key0=1&key1=1230123

  * **备注**



> rsp_type: throne json,rsp_table: svr_map_building_detail_info

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 通用map-获取王国建筑信息

  * **命令字** **_get_kingdom_building_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int32 | 123 | 1 |   
key1 | id | int32 | 123 | 1 | 数值id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kingdom_building_info&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.4 | 新增接口  
  
* * *

#### 通用map-军团战和ava获取地图

  * **命令字** **_map_get_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 |   
key1 | str_bid | string | 1,2,3 | 1 | bid之间用”,”分隔例如xxxxx,xxxxx,xxxxx  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_get_battle&key0=1&key1=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v2.9 | 新增接口  
  
* * *

### 7.137.通用march

* * *

#### 通用march-侦查

  * **命令字** **_march_scout_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | cost time | TUINT32 | 3 | 1 |   
Key1 | target pos | TUINT32 | 1310072 | 1 |   
Key2 | costgem | TINT32 | 0 | 1 |   
Key3 | resource | string | “4400:0:0:0:0:0:0:0:0:0” | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=march_scout&Key0=3&Key1=1310072&Key2=0&Key3=“4400:0:0:0:0:0:0:0:0:0”

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 通用march-召回

  * **命令字** **_action_recall_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | ActionId | TINT64 | 323423 | 1 |   
Key1 | ItemId | TINT32 | 1 | 1 | 不消耗就传-1  
Key2 | GemCost | TINT64 | 0 | 1 | 不消耗就传0  
Key3 | Type | TINT32 | 0 | 1 | type = 2为无消耗召回  
key10 | tpos | TINT64 | 1 | 0 | 后台自动生成-表示march的tpos  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=action_recall&Key0=323423&Key1=1&Key2=0&Key3=0&key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 通用march-遣返

  * **命令字** **_repatriate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | ActionId | TINT64 | 323423 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=repatriate&Key0=323423

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
  
* * *

#### 通用march-探索怪物巢穴

  * **命令字** **_explore_monster_lair_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | cowboy_list | string | 1025,2015,2021,1021 | 1 | ,分隔  
Key1 | target_pos | TINT32 | 3420022 | 1 |   
Key2 | march_time | TINT64 | 123 | 1 | 行军时间  
Key3 | explore_times | TINT64 | 25 | 1 | 探索次数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=explore_monster_lair&Key0=1025,2015,2021,1021&Key1=3420022&Key2=123&Key3=25

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 通用march-团战

  * **命令字** **_rally_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | udwCostTime | TUINT32 | 30 | 1 |   
Key1 | udwTargetPos | TUINT32 | 1310072 | 1 |   
Key3 | strTroopList | string | “1:4000:233:4000” | 1 | :分隔,位数代表兵种ID  
Key4 | udwPrepareTime | TUINT32 | 20 | 1 |   
Key5 | isSheriffJoin | bool | 1 | 1 |   
Key6 | strHeroList | string | “1,3,3,5” | 1 | ,分隔  
Key7 | udwQuickSend | TUINT32 | 1 | 0 | v6.2新增,新ava战场内rally主城,含义为是否在满人时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_attack&Key0=30&Key1=1310072&Key3=“1:4000:233:4000”&Key4=20&Key5=1&Key6=“1,3,3,5”&Key7=1&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.0 | 新增接口  
v6.2 | 新增key7  
  
* * *

#### 通用march-攻击建筑

  * **命令字** **_map_building_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | CostTime | TUINT32 | 30 | 1 |   
Key1 | TargetPos | TUINT32 | 1310071 | 1 |   
Key2 | strTroopList | string | “1:32:3:4” | 1 | :分隔,位数代表兵种ID  
Key3 | isSheriffJoin | bool | 1 | 1 |   
Key4 | HeroList | string | “1,2,3,4,5” | 1 | ，分隔  
Key5 | BuildingType | TUINT32 | 70 | 1 |   
Key6 | isPeaceMarch | TUINT32 | 1 | 1 | 标记是否需要开罩，默认为0，1代表期望这个march不会开罩  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_attack&Key0=30&Key1=1310071&Key2=“1:32:3:4”&Key3=1&Key4=“1,2,3,4,5”&Key5=70&Key6=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-团战建筑

  * **命令字** **_map_building_rally_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | udwCostTime | TUINT32 | 30 | 1 |   
Key1 | udwTargetPos | TUINT32 | 1310072 | 1 |   
Key2 | strTroopList | string | “1:4000:233:4000” | 1 | :分隔,位数代表兵种ID  
Key3 | isSheriffJoin | bool | 1 | 1 |   
Key4 | strHeroList | string | “1,3,3,5” | 1 | ,分隔  
Key5 | udwBuildingType | TUINT32 | 1 | 1 |   
Key6 | udwPrepareTime | TUINT32 | 20 | 1 |   
Key7 | udwQuickSend | TUINT32 | 1 | 0 | v5.8新增,惊魂马戏团必带该参数,含义为是否在满员时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_rally&Key0=30&Key1=1310072&Key2=“1:4000:233:4000”&Key3=1&Key4=“1,3,3,5”&Key5=1&Key6=20&Key7=1&Key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
v5.8 | 新增参数Key7  
  
* * *

#### 通用march-支援建筑

  * **命令字** **_map_building_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_num | 当前已用槽位 | TINT64 | 20 | 1 | 1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_reinforce&rf_troop_num=900000&rf_slot_num=20

|Key0|udwCostTime|TUINT32|30|1|| |Key1|udwTargetPos|TUINT32|1310071|1|| |Key2|strTroopList|string|“1:4000:222:4000”|1|:分隔,位数代表兵种ID| |Key3|udwBuildingType|TUINT32|33|1||

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-指挥官队列支援建筑

  * **命令字** **_map_building_assign_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
rf_troop_num | 当前已增援数量 | TINT64 | 900000 | 1 | 1  
rf_slot_num | 当前已用槽位 | TINT64 | 20 | 1 | 1  
Key0 | CostTime | TUINT32 | 20000 | 1 |   
Key1 | TargetPos | TINT32 | 560088 | 1 |   
Key2 | troopList | string | “123:123:123:123” | 1 | :分隔,位数代表兵种ID  
Key3 | SheriffJoin | bool | 1 | 1 |   
Key4 | HeroList | string | “1,2,3,4,5” | 1 | ,分隔  
Key5 | BuildingType | TUINT32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_assign&rf_troop_num=900000&rf_slot_num=20&Key0=20000&Key1=560088&Key2=“123:123:123:123”&Key3=1&Key4=“1,2,3,4,5”&Key5=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-遣返所有守军

  * **命令字** **_map_building_dismiss_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | sid | TINT32 | 12 | 1 |   
Key1 | pos | TINT32 | 1230123 | 1 |   
Key2 | BuildingType | TUINT32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_dismiss_all&Key0=12&Key1=1230123&Key2=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-遣返所有守军并放弃建筑

  * **命令字** **_map_building_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | sid | TINT32 | 12 | 1 |   
Key1 | pos | TINT32 | 1230123 | 1 |   
Key2 | BuildingType | TUINT32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_abandon&Key0=12&Key1=1230123&Key2=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-召回自己的一条支援

  * **命令字** **_map_building_recall_reinforce_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | TINT64 | 123123123 | 1 |   
key1 | udwBuildingType | TUINT32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_recall_reinforce&key0=123123123&key1=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-加速任意一条在路上的支援队列

  * **命令字** **_map_building_reinforce_speedup_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | action id | TINT64 | 123123132 | 1 |   
key1 | item id | TINT32 | 13 | 1 |   
key2 | gem_cost | TUINT32 | 0 | 1 |   
key3 | udwBuildingType | TUINT32 | 12 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_reinforce_speedup&key0=123123132&key1=13&key2=0&key3=12

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-踢回一条支援队列

  * **命令字** **_map_building_repatriate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | sid | TUINT32 | 111 | 1 |   
Key1 | pos | TUINT32 | 1110111 | 1 |   
Key2 | action_id | TINT64 | 1231231123 | 1 |   
Key3 | udwBuildingType | TUINT32 | 111 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_repatriate&Key0=111&Key1=1110111&Key2=1231231123&Key3=111

  * **改动历史**

版本号 | 说明  
---|---  
v3.6 | 新增接口  
  
* * *

#### 通用march-rally自动开uid记忆开关

  * **命令字** **_rally_quick_send_switch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | quick_send | TUINT32 | 1 | 1 | 0-不自动开 1-自动开  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_quick_send_switch&Key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 通用march-rally自动集结开启&更新配置

  * **命令字** **_al_auto_rally_reinforce_start_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | {“wild_class_list”:[1,2,3]} | json格式的string | 1 | 0 | v6.8新增增援者设置的团战自动接受集结野怪加入类型  
Key1 | {“troop_limit_set”:{“wild_class”:num}} | json格式的string | 1 | 0 | v6.9.1 新增增援者设置的团战自动接受集结野怪加入对于的兵种规模限制  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_auto_rally_reinforce_start&Key0=1&Key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 通用march-rally自动集结停止

  * **命令字** **_al_auto_rally_reinforce_stop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_auto_rally_reinforce_stop

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 通用march-rally自动集结编队设置军队-废弃

  * **命令字** **_al_auto_rally_reinforce_preset_troop_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | {“id”:num(万分比),} | json格式的string | 1 | 0 | v6.8新增增援者设置的团战自动接受集结军队预设数据  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_auto_rally_reinforce_preset_troop&Key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

#### 通用march-rally自动集结推荐兵种设置

  * **命令字** **_al_auto_rally_reinforce_recommand_set_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | ddwRallyWarId | action id | 1 | 0 | 团战id  
Key1 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.8新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_auto_rally_reinforce_recommand_set&Key0=1&Key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.8 | 新增接口  
  
* * *

### 7.138.通用move

* * *

#### 通用move-移城准备(只用发起一次,随后发起移城即可)

  * **命令字** **_move_city_prepare_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | uint32 | 123 | 1 |   
key1 | gem_cost | int64 | 123 | 1 |   
key2 | old city pos | uint32 | 1230123 | 1 |   
key3 | move_type | uint32 | 123 | 1 |   
key4 | tar_sid | uint32 | 123 | 1 |   
key5 | type | uint32 | 123 | 1 | 0:消耗道具 1:消耗金币 3:金币+道具混用  
key6 | dwProvince | uint32 | 123 | 1 |   
key7 | tar_pos | uint32 | 123 | 1 |   
key8 | item_num | uint32 | 123 | 1 | 总共使用道具数量  
key12 | item_num | uint32 | 123 | 1 | 金币购买并使用的道具数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=move_city_prepare_new&key0=123&key1=123&key2=1230123&key3=123&key4=123&key5=123&key6=123&key7=123&key8=123&key12=123

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 通用move-各种移城

  * **命令字** **_move_city_new_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | uint32 | 123 | 1 |   
key1 | gem_cost | int64 | 123 | 1 | ava中传需要消耗的金币总量  
key2 | old city pos | uint32 | 1230123 | 1 |   
key3 | move_type | uint32 | 1 | 1 | emovecitytype  
key4 | target_sid | uint32 | 1 | 1 | 跨服移城用  
key5 | target_pos | uint32 | 1230123 | 1 | 定点移城用  
key6 | province_idx | uint32 | 1 | 1 | 随机移城用  
key7 | type | uint32 | 1 | 1 | 0:消耗道具 1:消耗金币 3:金币+道具混用  
key8 | item_num | uint32 | 123 | 1 | 总共使用道具数量  
key10 | old_iron_sid/old_shadow_sid | TINT64 | 1 | 0 | 后台自动生成-表示旧霸主sid  
key11 | new_iron_sid/new_shadow_sid | TINT64 | 1 | 0 | 后台自动生成-表示新霸主sid  
key12 | item_num | uint32 | 123 | 1 | 金币购买并使用的道具数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=move_city_new&key0=123&key1=123&key2=1230123&key3=1&key4=1&key5=1230123&key6=1&key7=1&key8=123&key10=1&key11=1&key12=123

  * **move_type定义**



> 说明：和其它cmd共用这些枚举，19之前的是历史的，一定要在代码中确认是不是用这个接口….

move_type | 含义 | 备注  
---|---|---  
1 | 服内定点移城 |   
2 | 服内随机移城 |   
3 | kvk跨服移城 |   
4 | 新手移城 |   
11 | 军团战战场内移城 |   
12 | skvk跨服移城 |   
13 | 铁王座跨服移城 |   
14 | 失落之地战场内定点移城 |   
15 | 失落之地战场内随机移城 |   
16 | 暗影战场移城 |   
17 | 回流活动跨服移城 |   
18 | 新军团战战场内移城 |   
20 | 一定时长内的免费移城 |   
21 | 免费移城 |   
22 | 新AVA战场内定点移城 |   
23 | 新AVA战场内免费移城 |   
24 | 新kvk跨服付费移城 |   
25 | 新kvk跨服免费移城 |   
  
  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
v5.6.0 | 增加move_type  
  
* * *

#### 通用move-拉取指定svr指定rank type的rank

  * **命令字** **_get_rank_by_type_at_svr_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_sid | int64 |  | 1 |   
key1 | rank_type | int64 |  | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_rank_by_type_at_svr&key0=&key1=

  * **备注**



> rsp_type：rank json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 通用move-永久移城准备(只用发起一次,随后发起移城即可)

  * **命令字** **_move_city_immigrant_prepare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | uint32 | 123 | 1 |   
key2 | old city pos | uint32 | 123 | 1 |   
key3 | move_type | uint32 | 1 | 1 | 移城类型  
key4 | target_sid | uint32 | 123 | 1 |   
key6 | item_num | uint32 | 123 | 1 |   
key9 | rss | string |  | 1 | [[type,id,num],[type,id,num]…]json格式传入要设置的资源，超过可携带上限的资源需设置为可携带上限  
key10 | event_id | string | “123” | 1 | 回流移民使用，传入回流活动eventid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=move_city_immigrant_prepare&key0=123&key2=123&key3=1&key4=123&key6=123&key9=&key10=“123”

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 通用move-永久移城(继承自move_city_new的实现，对应key含义相同)

  * **命令字** **_move_city_immigrant_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_id | uint32 | 123 | 1 |   
key2 | old city pos | uint32 | 123 | 1 |   
key3 | move_type | uint32 | 6 | 1 | （6：移民 17：回流活动移民）  
key4 | target_sid | int32 | 123 | 1 |   
key5 | target_pos | int32 | 1230123 | 1 |   
key7 | type | int32 | 1 | 1 |   
key8 | item_num | int32 | 123 | 1 |   
key9 | rss | string | xxxxxx | 1 | [[type,id,num],[type,id,num]…]json格式传入要设置的资源，超过可携带上限的资源需设置为可携带上限  
key10 | event_id | string | xxxxxx | 1 | 回流移民使用，传入回流活动eventid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=move_city_immigrant&key0=123&key2=123&key3=6&key4=123&key5=1230123&key7=1&key8=123&key9=xxxxxx&key10=xxxxxx

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.2 | 新增接口  
  
* * *

#### 通用move-刷新玩家在推荐服务器的排名

  * **命令字** **_refresh_self_rank_in_recommend_svr_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
|  |  |  |  |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=refresh_self_rank_in_recommend_svr&=

  * **改动历史**

版本号 | 说明  
---|---  
v4.5 | 新增接口  
  
* * *

### 7.139.通用title

* * *

#### 通用title-赋予个人title

  * **命令字** **_common_dub_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | title id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=common_dub_title&key0=123&key1=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 通用title-赋予服务器title

  * **命令字** **_common_dub_kingdom_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target sid | int64 | 123 | 1 |   
key1 | title id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=common_dub_kingdom_title&key0=123&key1=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 通用title-获取其它svr的称号

  * **命令字** **_get_title_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target_svr | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_title_info&key0=123

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 通用title-获取所有称号(所有svr)

  * **命令字** **_get_all_title_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_all_title_info

  * **改动历史**

版本号 | 说明  
---|---  
v3.1 | 新增接口  
  
* * *

#### 通用title-战争活动中给个人赋予title

  * **命令字** **_battle_event_dub_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | title id | int64 | 123 | 1 |   
key2 | battle_sid | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=battle_event_dub_title&key0=123&key1=123&key2=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 通用title-战争活动中删除已颁发的个人title

  * **命令字** **_battle_event_remove_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | title id | int64 | 123 | 1 |   
key2 | battle_sid | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=battle_event_remove_title&key0=123&key1=123&key2=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 通用title-罢免个人title

  * **命令字** **_common_cancel_title_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | target uid | int64 | 123 | 1 |   
key1 | title id | int64 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=common_cancel_title&key0=123&key1=123

  * **备注**



> rsp_type: special

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.7 | 新增接口  
  
* * *

### 7.140.通用推送系列

* * *

#### 通用推送系列-推送延迟消息

  * **命令字** **_op_gen_common_msg_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwKeyType | 1=sid 2=aid 3=uid | 1= | 1 | 推送类型  
key1 | strJsnIdList | string | [1,2,3] | 1 | 目标对象列表  
key2 | strContent | string | {“svr_test”:{}} | 1 | 按需推送  
key3 | ddwExpireTime | int64 | 3600 | 1 | 按需设置  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_common_msg&key0=1=&key1=[1,2,3]&key2={“svr_test”:{}}&key3=3600

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

#### 通用推送系列-发广播

  * **命令字** **_op_send_broadcast_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | dwType | 广播id | 1 | 1 | 广播id-注意每次新增都需要找数值新增对应广播配置  
key1 | strReplace | string | x#xx#xx | 1 | 要替换的内容数据  
key2 | strParam | string |  | 1 | 按需推送  
key3 | strIdList | 1,2,3,4 | id_list | 1 | 按需设置  
key4 | dwType | 0=仅单个sid 1=支持aid_list 4=支持sid_list | 1 | 1 | 推送类型  
key5 | ddwExpireTime | 广播有效期 | 1 | 0 | 如果不传或者传-1，则使用默认过期时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_send_broadcast&key0=1&key1=x#xx#xx&key2=&key3=id_list&key4=1&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.7 | 新增接口  
  
* * *

### 7.141.通用特殊统治官礼包

* * *

#### 通用特殊统治官礼包-获取特殊统治官礼包列表

  * **命令字** **_get_kingdom_emperor_reward_list_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 1 | 1 | sid  
key1 | soure_id | int64 | 1 | 1 | 2-旧kvk,3-黄金圣碑  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kingdom_emperor_reward_list&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
v7.2.3 | source_id新增3-黄金圣碑  
  
* * *

#### 通用特殊统治官礼包-获取特殊统治官礼包详情

  * **命令字** **_get_kingdom_emperor_reward_history_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 1 | 1 | sid  
key1 | gift_id | int64 | 1 | 1 | gift_id,-1代表所有  
key2 | soure_id | int64 | 1 | 1 | 2-旧kvk,3-黄金圣碑  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_kingdom_emperor_reward_history&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
v7.2.3 | source_id新增3-黄金圣碑  
  
* * *

#### 通用特殊统治官礼包-特殊统治官发礼包

  * **命令字** **_kingdom_emperor_send_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | long | 1 | 1 | uid  
key1 | gift id | long | 1 | 1 | 礼包id  
key2 | soure_id | int64 | 1 | 1 | 2-旧kvk,3-黄金圣碑  
key3 | battle_sid | int64 | 1 | 1 | source_id为3时,需要给一个战场sid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=kingdom_emperor_send_reward&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

#### 通用特殊统治官礼包-更新特殊统治官礼包信息

  * **命令字** **_op_set_kingdom_emperor_gift_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | king_gift_info | json_str | 3 | 1 | 特殊统治官礼包信息  
key1 | soure_id | int64 | 1 | 1 | 2-旧kvk,3-黄金圣碑  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_kingdom_emperor_gift_info&key0=3&key1=1

  * **kingdom emperor gift info**


    
    
    {
        "event_id":str, //活动id
        "close_time":long, //活动关闭时间
        "sid_list":[sid1,sid2,sid3],     //3个sid,顺序保持运营一致,下标代表红绿蓝, 当source_id为3时, 将battle_sid拼在这里一并带过来
        "sheriff_gift_conf": //统治官礼包
        {
            "reward_conf": [ //如果是配置为没有礼包 此处空数组即可
                {
                    "gift_lv": int //奖励级别 0:低级奖励配置 1:中级奖励配置 2:高级奖励配置
                    "gift_list": 
                    {
                        "gift_id" : //礼包id 要求本pid内是唯一的
                        {
                            "reward": [
                                {"a":[int,int,int]} //设计上这里只给配置箱子 便于展示处理
                            ],
                            "limit_num": int //发奖次数限制
                        },
                    },
                }
            ]
        },
        "ceremony_official": //礼官礼包
        {
            "reward":[{"a":[int,int,int]}]
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
v7.2.3 | source_id新增3-黄金圣碑  
  
* * *

#### 通用特殊统治官礼包-设置特殊统治官权限

  * **命令字** **_op_set_kingdom_special_power_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | long | 1 | 1 | sid  
key1 | is_power | int64 | 1 | 1 | 1-设置 0-清除  
key2 | soure_id | int64 | 1 | 1 | 2-旧kvk  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_kingdom_special_power&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

#### 通用特殊统治官礼包-通用设置kingdom stat

  * **命令字** **_op_set_kingdom_stat_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid_list | json_str | [1,2,3] | 1 | sid_list  
key1 | soure_id | int64 | 1 | 1 | 2-旧kvk  
key2 | kingdom_stat | json_str | xxx | 1 | kingdom信息  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_set_kingdom_stat&key0=[1,2,3]&key1=1&key2=xxx

  * **kingdom stat info**


    
    
    {
        "event_id":str, //活动id
        "event_type":long, //活动type
        "pid":long, //活动pid
        "is_special_power":long, //是否是特殊统治官 0-不是 1-是
        "ceremony_official_id":long, //礼官id 用来控制统治官礼官礼包的发放权限 默认写20
    }

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

#### 通用特殊统治官礼包-领取礼官礼包

  * **命令字** **_kingdom_emperor_claim_ceremony_official_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | long | 1 | 1 | uid  
key1 | soure_id | int64 | 1 | 1 | 2-旧kvk  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=kingdom_emperor_claim_ceremony_official_reward&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.4 | 新增接口  
  
* * *

### 7.142.通用透传接口

* * *

#### 通用透传接口-带国王校验的透传接口

  * **命令字** **_new_op_forwarding_for_king_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | 哪个服的国王 | 1 | 1 | sid  
key1 | cmd | 透传cmd | 1 | 1 | sid  
key2 | param | 透传参数 | 1 | 1 | {xxxx}  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_forwarding_for_king&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.3 | 新增接口  
  
* * *

#### 通用透传接口-带force rank校验(实际是后台拼给运营)的透传接口

  * **命令字** **_new_op_forwarding_for_force_rank_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cmd | 透传cmd | 1 | 1 | sid  
key1 | param | 透传参数 | 1 | 1 | {xxxx}  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=new_op_forwarding_for_force_rank&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.5 | 新增接口  
  
* * *

### 7.143.道具箱子

* * *

#### 道具箱子-使用物品

  * **命令字** **_item_use_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
key1 | target id | int64 | 10086 | 1 |   
key2 | action_second_class | int32 | 15 | 1 |   
key3 | rallywar id | int64 | 12 | 1 | (大于0有效)  
key4 | rally side | int32 | 0 | 1 | (0 是进攻 1是防守)  
key5 | use_num | int32 | 1 | 0 | (不传是默认1个，传的值须大于0)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_use&key0=1&key1=10086&key2=15&key3=12&key4=0&key5=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.11 | 新增接口  
  
* * *

#### 道具箱子-购买物品

  * **命令字** **_item_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 0 | 1 |   
key1 | price | int64 | 1000 | 1 | (gem cost)  
key2 | price | int64 | 1000 | 1 | (loyalty price)  
key3 | buy_num | int32 | 1 | 0 | (不传是默认1个，传的值须大于0)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_buy&key0=0&key1=1000&key2=1000&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.11 | 新增接口  
  
* * *

#### 道具箱子-购买&使用物品

  * **命令字** **_item_buy_and_use_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
key1 | target id | int64 | 123456 | 1 |   
key2 | price | int64 | 123456789 | 1 | (gem cost)  
key3 | action_second_class | int32 | 1 | 1 |   
key4 | rallywar id | int64 | 1 | 1 | (大于0有效)  
key5 | rally side | int32 | 0 | 1 | (0 是进攻 1是防守)  
key6 | price | int64 | 123456789 | 1 | (gem cost)  
key8 | rally side | int32 | 1 | 1 | (备份key5，因为cblog用到key5会覆盖)  
key9 | buy_num | int32 | 1 | 0 | (不传是默认1个，传的值须大于0)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_buy_and_use&key0=1&key1=123456&key2=123456789&key3=1&key4=1&key5=0&key6=123456789&key8=1&key9=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.11 | 新增接口  
v6.3 | 新增购买数量参数  
  
* * *

#### 道具箱子-一键开启多个箱子

  * **命令字** **_chest_open_all_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | open_type | int32 | 0 | 1 | 0: use item 1: use gem  
key1 | chest_id | int32 | 1 | 1 |   
key2 | item_id | int32 | 1 | 1 |   
key2 | chest_num | int32 | 10 | 1 |   
key2 | gem_cost | int64 | 10 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=chest_open_all&key0=0&key1=1&key2=1&key2=10&key2=10

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.11 | 新增接口  
  
* * *

#### 道具箱子-使用多个道具

  * **备注**



> 只对增加资源类道具有效

  * **命令字** **_vip_common_item_use_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 | 道具id  
key1 | item num | int64 | 100 | 1 | 使用数量  
key2 | target id | int64 | 100 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=vip_common_item_use&key0=1&key1=100&key2=100

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.11 | 新增接口  
  
* * *

#### 道具箱子-多选一箱子

  * **命令字** **_chest_select_item_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 |   
key1 | select idx | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=chest_select_item&key0=1&key1=1

  * **备注**



> rsp_type：user json

  * **改动历史**

版本号 | 说明  
---|---  
v2.1 | 新增接口  
  
* * *

#### 道具箱子-多开多选一箱子

  * **命令字** **_vip_chest_select_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | chestid | int32 | 1 | 1 | 箱子id  
key1 | select_item_id | int32 | 1 | 1 | 选项  
key2 | num | int32 | 1 | 1 | 数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=vip_chest_select&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v3.0 | 新增接口  
  
* * *

#### 道具箱子-使用立刻完成道具

  * **命令字** **_use_immediately_complete_item_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item id | int32 | 1 | 1 | 仅传立刻完成道具  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=use_immediately_complete_item&key0=1

  * **改动历史**

版本号 | 说明  
---|---  
v5.7 | 新增接口  
  
* * *

#### 道具箱子-一键加速

  * **命令字** **_one_click_acceleration_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_list | string | {“16”:8} | 1 | [[item_type,item_id,item_num],[long,long,long]…]  
key1 | target_id | long | 42956205605282568 | 1 |   
key2 | sec_class | int | 161 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=one_click_acceleration&key0={“16”:8}&key1=42956205605282568&key2=161

  * **改动历史**

版本号 | 说明  
---|---  
v6.2 | 新增接口  
  
* * *

#### 道具箱子-组合式使用道具

  * **命令字** **_item_use_combination_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | item_list | json类格式物品 | [{“a”:[type,id,num]}] | 1 | 后台传什么就用会处理奖励聚合-暂支持教官道具加经验  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=item_use_combination&key0=[{“a”:[type,id,num]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 道具箱子-一键使用资源道具

  * **命令字** **_one_click_resource_item_use_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | use_list | string | {“1”:8} | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=one_click_resource_item_use&key0={“1”:8}

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 道具箱子-快捷使用资源宝箱

  * **命令字** **_vip_chest_select_and_use_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | chestid | int32 | 1 | 1 | 箱子id  
key1 | select_item_id | int32 | 1 | 1 | 选项  
key2 | num | int32 | 1 | 1 | 数量  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=vip_chest_select_and_use&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 道具箱子-批量开不同id的箱子(系统限制-不能超过10个不同id)

  * **命令字** **_batch_open_chest_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 要开的箱子 | [{“a”:[int64,int64,int64]}] | [{“a”:[0,0,1000]}] | 1 | 通用reward格式  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=batch_open_chest&key0=[{“a”:[0,0,1000]}]

  * **改动历史**

版本号 | 说明  
---|---  
v6.9 | 新增接口  
  
* * *

#### 道具箱子-使用自迭代箱子

  * **命令字** **_auto_iterate_chest_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 箱子id | int64 | 123 | 1 |   
key1 | 箱子数量 | int32 | 123 | 1 |   
key2 | 选择下标 | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auto_iterate_chest_open&key0=123&key1=123&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.8 | 新增接口  
  
* * *

#### 道具箱子-使用自迭代混合箱子

  * **命令字** **_auto_iterate_multiple_selected_chest_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 箱子id | int64 | 123 | 1 |   
key1 | 箱子数量 | int32 | 123 | 1 |   
key2 | 选择下标 | int32 | 1 | 1 | idx=(type*1000000000+id) 真实的奖励type和id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auto_iterate_multiple_selected_chest_open&key0=123&key1=123&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.7 | 新增接口  
  
* * *

#### 道具箱子-使用自迭代随机箱子

  * **命令字** **_auto_iterate_multiple_random_chest_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 箱子id | int64 | 123 | 1 |   
key1 | 箱子数量 | int32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=auto_iterate_multiple_random_chest_open&key0=123&key1=123

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.7 | 新增接口  
  
* * *

### 7.144.邮件

* * *

#### 邮件-标记已读

  * **命令字** **_mail_read_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type:mail_id,op_type:mail_id | 自定格式 | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_read&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-删除邮件

  * **命令字** **_mail_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type:mail_id,op_type:mail_id | 自定格式 | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_del&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-收藏邮件

  * **命令字** **_mail_star_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type:mail_id,op_type:mail_id | 自定格式 | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_star&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-邮件取消收藏

  * **命令字** **_mail_unstar_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | op_type:mail_id,op_type:mail_id | string | 0:5204441 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_unstar&key0=0:5204441

  * 备注



> op_type 0 表示操作单封, 1表示操作集合  
>  各封邮件间以, 分隔最多一次支持40组

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-收集奖励

  * **命令字** **_mail_reward_collect_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_id | int64 | 1234567 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_reward_collect&key0=1234567

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-发送邮件

  * **命令字** **_mail_send_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | send_type | int32 | 1 | 1 | 见EmailSendType 0表示玩家对玩家,1表示玩家对联盟  
key1 | names | string | Cowboy_QYR:Oko:Marrrr | 1 | 以:隔开  
key2 | title | string | lost event | 1 |   
key3 | content | string | lost event content | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_send&key0=1&key1=Cowboy_QYR:Oko:Marrrr&key2=lost event&key3=lost event content

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-发送运营邮件

  * **命令字** **_operate_mail_send_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | send_type | int32 | 2 | 1 | 见EmailSendType 0表示玩家对玩家,1表示玩家对联盟  
key1 | 目标id | int32 | 10086 | 1 |   
key2 | title | string | event title | 1 |   
key3 | 文案id | int32 | 1 | 1 | 没有传0  
key4 | content | string | event content | 1 |   
key5 | extra content | string | extra content | 1 | 活动奖励类邮件默认需要传end_time  
key6 | 展示分类 | int32 | 1000004 | 1 |   
key7 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key8 | 类型 | int32 | 0 | 1 | 0表示发给所有服、1表示发给单个服  
key9 | platform | string | Android | 1 | 为空发给全平台、IOS给IOS、Android给Android  
key10 | platform | string | 1.2 | 1 | version为空发给全版本、1.2 发给1.2版本  
key11 | url | string |  | 1 |   
key12 | 跳转方式 | int32 | 0 | 1 |   
key13 | model id | int64 | 1 | 1 | web工具邮件模板用 额外需要调用op_update_mail_model设定文案数据  
key14 | szShowReward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key15 | ExceptUid | string | 11,22,33 | 1 | 被排除在外的uid  
key16 | AlManager | string | 6,5,4 | 1 | 给联盟管理发邮件时 给哪些管理发邮件  
key17 | SendUid | string | 6,5,4 | 1 | 发联盟邮件给指定的的uid发邮件  
key18 | 是否可一键已读 | int | 1 | 1 | 0表示不可一键已读, 1表示可一键已读  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_mail_send&key0=2&key1=10086&key2=event title&key3=1&key4=event content&key5=extra content&key6=1000004&key7=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key8=0&key9=Android&key10=1.2&key11=&key12=0&key13=1&key14=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key15=11,22,33&key16=6,5,4&key17=6,5,4&key18=1

  * 备注 key5是json格式的string,如[“STRING0”,“STRING1”]



> Key0=send_type  
>  2:玩家  
>  3:联盟  
>  6:单服  
>  7:全服  
>  8:旧军团战  
>  9:新军团战  
>  10:一堆玩家，最多100个  
>  11:联盟，管理者

> Key1=目标id  
>  Key0等于2时表示玩家id 只支持一个  
>  Key0等于3时表示联盟id 只支持一个  
>  key0等于10时表示一堆uid，支持最多100个  
>  Key0等于11时表示联盟id 只支持一个

> Key6=邮件分类汇总senduid  
>  -1000000：表示 SYSTEM_NOTICE  
>  -1000001：表示 SYSTEM_EVENT 邮箱-活动邮箱-活动  
>  -1000002：表示 SYSTEM_ENCOURAGE  
>  -1000003：表示 SYSTEM_WAR  
>  -1000004：表示 SYSTEM_ACTIVITY  
>  -1000005：表示 SYSTEM_HOLIDAY  
>  -1000006：表示 SYSTEM_NEW_PLAYER_AL  
>  -1000007：表示 缺失  
>  -1000008：表示 SYSTEM_INVITE 邮箱-邀请  
>  -1000009：表示 SYSTEM_DIPLOMACY 邮箱-帮派  
>  -1000010：表示 SYSTEM_SUPPORT  
>  -1000011：表示 SYSTEM_MANAGE_AL 邮件-邮箱-帮派管理  
>  -1000012：表示 SYSTEM_AL_EVENT  
>  -1000013：表示 SYSTEM_KVK_EVENT 邮件-邮箱-旧svs  
>  -1000014：表示 SYSTEM_EVIP 邮件-邮箱-精英服务  
>  -1000015：表示 SYSTEM_IAP_CARD 邮件-邮箱-周月卡  
>  -1000016：表示 SYSTEM_STATE_MAIL 邮件-邮箱-州邮件  
>  -1000017：表示 SYSTEM_ITEM_DROP  
>  -1000018：表示 SYSTEM_LOST_EVENT 活动邮件-总督疆界  
>  -1000019：表示 SYSTEM_CUSTOM_IAP 邮件–邮箱-指定礼包  
>  -1000020：表示 SYSTEM_HUNT_EVENT hunt event  
>  -1000021：表示 SYSTEM_CIRCUS_EVENT circus event  
>  -1000022：表示 SYSTEM_NEW_AVA_EVENT new ava event  
>  -1000023：表示 SYSTEM_NEW_KVK_EVENT new kvk event  
>  -1000024：表示 SYSTEM_MERCENARY_GLORY 佣兵荣耀  
>  -1000025：表示 SYSTEM_TRAIN_ROBBERY 火车大劫案  
>  -1000026：表示 SYSTEM_NEW_AVA_LEAGUE 新ava联赛

> Key12=jmp_type  
>  0：不跳转  
>  1：跳转到FB: Go to Facebook  
>  2：跳转到其他外部链接: Check it Now  
>  3：跳转到IAP: Go to Gem Store  
>  4：跳转到活动: Go to Event  
>  5：跳转到帐号绑定: Go Bind Account  
>  6：跳转到游戏说明: How to Play  
>  7：跳转到博物馆: Go to MONUMENT  
>  8：跳转到编年史: Go LOST  
>  9：跳转到联盟坐标: Go to AL_BOOKMARK  
>  10：跳转到联盟建筑皮肤设置: Go AL_BUILDING_SKIN

> 以上所有key要经过URL编码

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-获取邮件二级列表

  * **命令字** **_mail_detail_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_display_type | int32 | 1 | 1 | 见EmailSendType 0表示玩家对玩家,1表示玩家对联盟  
key1 | sender_uid | int64 | 10086 | 1 | 玩家uid或者联盟aid  
key2 | receive_uid | int64 | 10010 | 1 |   
key3 | mail_id | int64 | 1012411 | 8 |   
key4 | support | int32 |  | 1 |   
key4 | support | int32 | ssxsx | 1 | 1  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_detail_get&key0=1&key1=10086&key2=10010&key3=1012411&key4=&key4=ssxsx

  * 备注



> 用公共参数传需要的页过来  
>  返回“svr_mail_detail_list”

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-获取邮件详情

  * **命令字** **_op_mail_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_id | int64 | 12345678 | 1 | 目标邮件id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mail_get&key0=12345678

  * 备注



> 返回“svr_op_mail_list”

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
v6.8 | 提供给客户端  
  
* * *

#### 邮件-获取邮件

  * **命令字** **_mail_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | support | int32 | 1 | 1 |   
key1 | box type | int32 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_get&key0=1&key1=1

  * 备注



> 用公共参数传需要的页过来  
>  返回“svr_mail_detail_list”

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-邮件翻译

  * **命令字** **_mail_translate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_id | int64 | 1 | 1 |   
key1 | target_lang_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_translate&key0=1&key1=1

  * **备注**



> rsp_type：mail_json (svr_op_mail_list)

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-批量领取邮件

  * **命令字** **_mail_reward_collect_batch_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | box_type | int64 | 1 | 1 |   
key1 | display_id | int64 | 1 | 1 |   
key10 | 邮件信息 | mail_id,mail_id | 1 | 0 | 后台自动生成-表示领取的邮件id列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_reward_collect_batch&key0=1&key1=1&key10=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.37 | 新增接口  
  
* * *

#### 邮件-发送州邮件

  * **命令字** **_send_state_mail_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 |   
key1 | content | string | dsgfdsgf | 1 | string  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=send_state_mail&key0=1&key1=dsgfdsgf

  * **改动历史**

版本号 | 说明  
---|---  
v3.4.1 | 新增接口  
  
* * *

#### 邮件-旧邮箱发送验证码

  * **命令字** **_account_change_mail_send_old_code_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_send_old_code

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-旧邮箱验证码确认

  * **命令字** **_account_change_mail_vertify_old_code_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | code | int64 | 165789 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_vertify_old_code&key0=165789

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-新邮箱发送验证码

  * **命令字** **_account_change_mail_send_new_code_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | new_mail | string | xxxxxxxxxxxx@leyinetwork.com | 1 |   
key1s | 是否跳过旧邮箱验证 | int64 | 1 | 1 | 1=是 0/其他=否  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_send_new_code&key0=xxxxxxxxxxxx@leyinetwork.com&key1s=1

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-新邮箱验证码确认

  * **命令字** **_account_change_mail_vertify_new_code_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | code | int64 | 165789 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_vertify_new_code&key0=165789

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-提交自证表单

  * **命令字** **_account_change_mail_submit_self_certification_form_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 表单数据 | json | {“ctime”:long,“total_pay”:[long,long]} | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_submit_self_certification_form&key0={“ctime”:long,“total_pay”:[long,long]}

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-玩家点击确认

  * **命令字** **_account_change_mail_comfirm_result_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_comfirm_result

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-玩家点击放弃

  * **命令字** **_account_change_mail_abandon_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=account_change_mail_abandon

  * **改动历史**

版本号 | 说明  
---|---  
v6.6 | 新增接口  
  
* * *

#### 邮件-给国王发送邮件专用接口

  * **命令字** **_operate_add_king_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
only_king | only_king | int32 | 1 | 1 | 1-只能给国王发 0-表示会给国王发，无国王给rank1发  
key0 | sid | int32 | 2 | 1 | 某个服务器sid  
key1 | king_uid | int32 | 10086 | 1 | 如果没有就会自己去查找  
key2 | title | string | event title | 1 |   
key3 | 文案id | int32 | 1 | 1 | 没有传0  
key4 | content | string | event content | 1 |   
key5 | extra content | string | extra content | 1 |   
key6 | 展示分类 | int32 | 1000004 | 1 |   
key7 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key8 | 默认传1 | int32 | 0 | 1 | 1  
key9 | platform | string | Android | 1 | 为空发给全平台、IOS给IOS、Android给Android  
key10 | platform | string | 1.2 | 1 | version为空发给全版本、1.2 发给1.2版本  
key11 | url | string |  | 1 |   
key12 | 跳转方式 | int32 | 0 | 1 |   
key13 | model id | int64 | 1 | 1 |   
key14 | szShowReward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key15 | ExceptUid | string | 传空 | 1 | 被排除在外的uid  
key16 | AlManager | string | 传空 | 1 | 给联盟管理发邮件时 给哪些管理发邮件  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_add_king_reward&only_king=1&key0=2&key1=10086&key2=event title&key3=1&key4=event content&key5=extra content&key6=1000004&key7=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key8=0&key9=Android&key10=1.2&key11=&key12=0&key13=1&key14=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key15=传空&key16=传空

  * 备注 key5是json格式的string,如[“STRING0”,“STRING1”]



> Key6=邮件分类汇总senduid  
>  -1000000：表示 SYSTEM_NOTICE  
>  -1000001：表示 SYSTEM_EVENT 邮箱-活动邮箱-活动  
>  -1000002：表示 SYSTEM_ENCOURAGE  
>  -1000003：表示 SYSTEM_WAR  
>  -1000004：表示 SYSTEM_ACTIVITY  
>  -1000005：表示 SYSTEM_HOLIDAY  
>  -1000006：表示 SYSTEM_NEW_PLAYER_AL  
>  -1000007：表示 缺失  
>  -1000008：表示 SYSTEM_INVITE 邮箱-邀请  
>  -1000009：表示 SYSTEM_DIPLOMACY 邮箱-帮派  
>  -1000010：表示 SYSTEM_SUPPORT  
>  -1000011：表示 SYSTEM_MANAGE_AL 邮件-邮箱-帮派管理  
>  -1000012：表示 SYSTEM_AL_EVENT  
>  -1000013：表示 SYSTEM_KVK_EVENT 邮件-邮箱-旧svs  
>  -1000014：表示 SYSTEM_EVIP 邮件-邮箱-精英服务  
>  -1000015：表示 SYSTEM_IAP_CARD 邮件-邮箱-周月卡  
>  -1000016：表示 SYSTEM_STATE_MAIL 邮件-邮箱-州邮件  
>  -1000017：表示 SYSTEM_ITEM_DROP  
>  -1000018：表示 SYSTEM_LOST_EVENT 活动邮件-总督疆界  
>  -1000019：表示 SYSTEM_CUSTOM_IAP 邮件–邮箱-指定礼包  
>  -1000020：表示 SYSTEM_HUNT_EVENT hunt event  
>  -1000021：表示 SYSTEM_CIRCUS_EVENT circus event  
>  -1000022：表示 SYSTEM_NEW_AVA_EVENT new ava event  
>  -1000023：表示 SYSTEM_NEW_KVK_EVENT new kvk event  
>  -1000024：表示 SYSTEM_MERCENARY_GLORY 佣兵荣耀  
>  -1000025：表示 SYSTEM_TRAIN_ROBBERY 火车大劫案  
>  -1000026：表示 SYSTEM_NEW_AVA_LEAGUE 新ava联赛

> Key12=jmp_type  
>  0：不跳转  
>  1：跳转到FB: Go to Facebook  
>  2：跳转到其他外部链接: Check it Now  
>  3：跳转到IAP: Go to Gem Store  
>  4：跳转到活动: Go to Event  
>  5：跳转到帐号绑定: Go Bind Account  
>  6：跳转到游戏说明: How to Play  
>  7：跳转到博物馆: Go to MONUMENT  
>  8：跳转到编年史: Go LOST  
>  9：跳转到联盟坐标: Go to AL_BOOKMARK  
>  10：跳转到联盟建筑皮肤设置: Go AL_BUILDING_SKIN

> 以上所有key要经过URL编码

  * **改动历史**

版本号 | 说明  
---|---  
v7.0.5 | 新增接口  
  
* * *

#### 邮件-获取收藏邮件

  * **命令字** **_mail_star_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_star_get

  * 备注



> 用公共参数传需要的页过来  
>  返回“svr_mail_star_total_list”

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 邮件-获取收藏邮件二级列表

  * **命令字** **_mail_star_detail_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_display_type | int32 | 1 | 1 |   
key1 | sender_uid | int64 | 10086 | 1 | 玩家uid或者联盟aid  
key2 | receive_uid | int64 | 10010 | 1 |   
key3 | mail_id | int64 | 1012411 | 8 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_star_detail_get&key0=1&key1=10086&key2=10010&key3=1012411

  * 备注



> 用公共参数传需要的页过来  
>  返回“svr_mail_star_detail_list”

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 邮件-获取收藏邮件详情

  * **命令字** **_op_mail_star_get_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_id | int64 | 12345678 | 1 | 目标邮件id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_mail_star_get&key0=12345678

  * 备注



> 返回“svr_op_mail_list”

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 邮件-收藏邮件翻译

  * **命令字** **_mail_star_translate_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | mail_id | int64 | 1 | 1 |   
key1 | target_lang_id | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=mail_star_translate&key0=1&key1=1

  * **备注**



> rsp_type：mail_json (svr_op_mail_list)

  * **改动历史**

版本号 | 说明  
---|---  
v7.1.2 | 新增接口  
  
* * *

#### 邮件-发送esc带end_time的web邮件

  * **命令字** **_operate_mail_send_with_end_time_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | send_type | int32 | 2 | 1 | 见EmailSendType 0表示玩家对玩家,1表示玩家对联盟  
key1 | 目标id | int32 | 10086 | 1 |   
key2 | title | string | event title | 1 |   
key3 | 文案id | int32 | 1 | 1 | 没有传0  
key4 | content | string | event content | 1 |   
key5 | extra content | string | extra content | 1 | 活动奖励类邮件默认需要传end_time  
key6 | 展示分类 | int32 | 1000004 | 1 |   
key7 | reward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key8 | 类型 | int32 | 0 | 1 | 0表示发给所有服、1表示发给单个服  
key9 | platform | string | Android | 1 | 为空发给全平台、IOS给IOS、Android给Android  
key10 | platform | string | 1.2 | 1 | version为空发给全版本、1.2 发给1.2版本  
key11 | url | string |  | 1 |   
key12 | 跳转方式 | int32 | 0 | 1 |   
key13 | model id | int64 | 1 | 1 | web工具邮件模板用 额外需要调用op_update_mail_model设定文案数据  
key14 | szShowReward | string | [{“a”:[1,0,200]},{“a”:[0,12,1]}] | 1 | 取自数值reward.json协议  
key15 | ExceptUid | string | 11,22,33 | 1 | 被排除在外的uid  
key16 | AlManager | string | 6,5,4 | 1 | 给联盟管理发邮件时 给哪些管理发邮件  
key17 | SendUid | string | 6,5,4 | 1 | 发联盟邮件给指定的的uid发邮件  
key18 | 是否可一键已读 | int | 1 | 1 | 0表示不可一键已读, 1表示可一键已读  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=operate_mail_send_with_end_time&key0=2&key1=10086&key2=event title&key3=1&key4=event content&key5=extra content&key6=1000004&key7=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key8=0&key9=Android&key10=1.2&key11=&key12=0&key13=1&key14=[{“a”:[1,0,200]},{“a”:[0,12,1]}]&key15=11,22,33&key16=6,5,4&key17=6,5,4&key18=1

  * 备注 key5是json格式的string,如[“STRING0”,“STRING1”]



> Key0=send_type  
>  2:玩家  
>  3:联盟  
>  6:单服  
>  7:全服  
>  8:旧军团战  
>  9:新军团战  
>  10:一堆玩家，最多100个  
>  11:联盟，管理者

> Key1=目标id  
>  Key0等于2时表示玩家id 只支持一个  
>  Key0等于3时表示联盟id 只支持一个  
>  key0等于10时表示一堆uid，支持最多100个  
>  Key0等于11时表示联盟id 只支持一个

> Key6=邮件分类汇总senduid  
>  -1000000：表示 SYSTEM_NOTICE  
>  -1000001：表示 SYSTEM_EVENT 邮箱-活动邮箱-活动  
>  -1000002：表示 SYSTEM_ENCOURAGE  
>  -1000003：表示 SYSTEM_WAR  
>  -1000004：表示 SYSTEM_ACTIVITY  
>  -1000005：表示 SYSTEM_HOLIDAY  
>  -1000006：表示 SYSTEM_NEW_PLAYER_AL  
>  -1000007：表示 缺失  
>  -1000008：表示 SYSTEM_INVITE 邮箱-邀请  
>  -1000009：表示 SYSTEM_DIPLOMACY 邮箱-帮派  
>  -1000010：表示 SYSTEM_SUPPORT  
>  -1000011：表示 SYSTEM_MANAGE_AL 邮件-邮箱-帮派管理  
>  -1000012：表示 SYSTEM_AL_EVENT  
>  -1000013：表示 SYSTEM_KVK_EVENT 邮件-邮箱-旧svs  
>  -1000014：表示 SYSTEM_EVIP 邮件-邮箱-精英服务  
>  -1000015：表示 SYSTEM_IAP_CARD 邮件-邮箱-周月卡  
>  -1000016：表示 SYSTEM_STATE_MAIL 邮件-邮箱-州邮件  
>  -1000017：表示 SYSTEM_ITEM_DROP  
>  -1000018：表示 SYSTEM_LOST_EVENT 活动邮件-总督疆界  
>  -1000019：表示 SYSTEM_CUSTOM_IAP 邮件–邮箱-指定礼包  
>  -1000020：表示 SYSTEM_HUNT_EVENT hunt event  
>  -1000021：表示 SYSTEM_CIRCUS_EVENT circus event  
>  -1000022：表示 SYSTEM_NEW_AVA_EVENT new ava event  
>  -1000023：表示 SYSTEM_NEW_KVK_EVENT new kvk event  
>  -1000024：表示 SYSTEM_MERCENARY_GLORY 佣兵荣耀  
>  -1000025：表示 SYSTEM_TRAIN_ROBBERY 火车大劫案  
>  -1000026：表示 SYSTEM_NEW_AVA_LEAGUE 新ava联赛

> Key12=jmp_type  
>  0：不跳转  
>  1：跳转到FB: Go to Facebook  
>  2：跳转到其他外部链接: Check it Now  
>  3：跳转到IAP: Go to Gem Store  
>  4：跳转到活动: Go to Event  
>  5：跳转到帐号绑定: Go Bind Account  
>  6：跳转到游戏说明: How to Play  
>  7：跳转到博物馆: Go to MONUMENT  
>  8：跳转到编年史: Go LOST  
>  9：跳转到联盟坐标: Go to AL_BOOKMARK  
>  10：跳转到联盟建筑皮肤设置: Go AL_BUILDING_SKIN

> 以上所有key要经过URL编码

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.2 | 新增接口  
  
* * *

### 7.145.野地march

* * *

#### 野地march-攻打野外军队

  * **命令字** **_wild_army_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
key5 | attack_time | uint32 | 123 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=wild_army_attack&key0=123&key1=123&key2=123&key3=1&key4=123&key5=123

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 野地march-能量恢复

  * **命令字** **_wild_army_energy_recover_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost_item | uint32 | 123 | 1 | 消耗的道具id  
key1 | cost_num | uint32 | 123 | 1 | 消耗的道具数量  
key2 | curr_recover_count | uint32 | 12 | 1 | 今日已恢复次数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=wild_army_energy_recover&key0=123&key1=123&key2=12

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 野地march-攻打个人野怪

  * **命令字** **_wild_army_solo_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target pos | uint32 | 123 | 1 |   
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
key5 | wild_class | uint32 | 1 | 1 | 目标地块class  
key6 | wild_type | uint32 | 1 | 1 | 目标地块type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=wild_army_solo_attack&key0=123&key1=123&key2=123&key3=1&key4=123&key5=1&key6=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
v7.0.2 | 更新接口  
  
* * *

#### 野地march-攻打新rally野怪

  * **命令字** **_rally_war_wild_army_rally_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | prepare time | uint32 | 123 | 1 |   
key2 | target pos | uint32 | 123 | 1 |   
key3 | troop list | string | 123:123 | 1 |   
key4 | preparetime | uint32 | 123 | 1 |   
key5 | if general join | uint32 | 123 | 1 |   
key6 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
Key7 | quick_send | int32 | 1 | 0 | 含义为是否在满员时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.8新增发起者设置的团战推荐参数  
key11 | wild_class | uint32 | 1 | 1 | 目标地块class  
key12 | wild_type | uint32 | 1 | 1 | 目标地块type  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_war_wild_army_rally&key0=123&key1=123&key2=123&key3=123:123&key4=123&key5=123&key6=123&Key7=1&Key10=1&key11=1&key12=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
v7.0.2 | 更新接口  
  
* * *

#### 野地march-支援rally新rally野怪 rally war

  * **命令字** **_rally_reinforce_wild_army_rally_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost time | uint32 | 123 | 1 |   
key1 | target_pos | uint32 | 123 | 1 |   
key3 | troop list(以:分隔) | string | 12,3,33 | 1 |   
key4 | rally war action id | int64 | 123 | 1 |   
key6 | car_list | string | 1,2,3 | 1 | 牛仔列表  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_reinforce_wild_army_rally&key0=123&key1=123&key3=12,3,33&key4=123&key6=1,2,3

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

#### 野地march-探索怪物巢穴

  * **命令字** **_explore_monster_lair_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cowboy_list | string | 1,2,3 | 1 | (,分隔)  
key1 | target_pos | uint32 | 1230123 | 1 | 怪物巢穴坐标  
key2 | march_time | uint32 | 123 | 1 | 行军时间  
key3 | explore_times | int32 | 1 | 1 | 探索次数, 由客户端计算传给后台, 后台会做能量校验..  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=explore_monster_lair&key0=1,2,3&key1=1230123&key2=123&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v1.7 | 新增接口  
  
* * *

### 7.146.销号

* * *

#### 销号-web销号准备

  * **命令字** **_web_start_delete_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | Seed | TINT64 | 8888 | 1 |   
key1 | ExpireTime | TINT64 | 170612863312 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=web_start_delete&key0=8888&key1=170612863312

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

#### 销号-web销号操作

  * **命令字** **_web_delete_account_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | Name | string | user_name | 1 |   
key1 | Seed | TINT64 | 8888 | 1 | 需和web_start_delete一致  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=web_delete_account&key0=user_name&key1=8888

  * **改动历史**

版本号 | 说明  
---|---  
v6.3 | 新增接口  
  
* * *

### 7.147.雷达活动

* * *

#### 雷达活动-领取雷达活动任务奖励

  * **命令字** **_claim_radar_reward_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | string | event | 148_xxxx | 1 | 雷达活动id  
key1 | string | task_id | xxxx | 1 | 雷达任务id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=claim_radar_reward&key0=148_xxxx&key1=xxxx

  * **改动历史**

版本号 | 说明  
---|---  
v6.4.0 | 新增接口  
  
* * *

#### 雷达活动-雷达营救地形派出队列进行攻打

  * **命令字** **_wild_rescue_solo_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | string | event | 148_xxxx | 1 | 雷达活动id  
key1 | string | task_id | xxxx | 1 | 雷达任务id  
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=wild_rescue_solo_attack&key0=148_xxxx&key1=xxxx&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v6.4.0 | 新增接口  
  
* * *

#### 雷达活动-雷达任务-击杀屠夫兄弟帮

  * **命令字** **_radar_wild_army_solo_attack_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | string | event | 148_xxxx | 1 | 雷达活动id  
key1 | string | task_id | xxxx | 1 | 雷达任务id  
key2 | troop list | uint32 | 123 | 1 |   
key3 | if general join | bool | 1 | 1 |   
key4 | card_list | string | 123 | 1 | (,分隔) //骑士列表, 传卡牌后台id…  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=radar_wild_army_solo_attack&key0=148_xxxx&key1=xxxx&key2=123&key3=1&key4=123

  * **改动历史**

版本号 | 说明  
---|---  
v6.4.0 | 新增接口  
  
* * *

#### 雷达活动-雷达攻打-土匪/野生动物

  * **命令字** **_radar_explore_monster_lair_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
Key0 | cowboy_list | string | 1025,2015,2021,1021 | 1 | ,分隔  
key1 | string | event | 148_xxxx | 1 | 雷达活动id  
key2 | string | task_id | xxxx | 1 | 雷达任务id  
Key3 | explore_times | TINT64 | 25 | 1 | 探索次数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=radar_explore_monster_lair&Key0=1025,2015,2021,1021&key1=148_xxxx&key2=xxxx&Key3=25

  * **改动历史**

版本号 | 说明  
---|---  
v6.4 | 新增接口  
  
* * *

### 7.148.非aid类rally

* * *

#### 非aid类rally-非aid团战建筑

  * **命令字** **_map_building_rally_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | udwCostTime | TUINT32 | 30 | 1 |   
key1 | udwTargetPos | TUINT32 | 1310072 | 1 |   
key2 | strTroopList | string | 1:4000:233:4000 | 1 | :分隔,位数代表兵种ID  
key3 | isSheriffJoin | bool | 1 | 1 |   
key4 | strHeroList | string | 1,3,3,5 | 1 | ,分隔  
key5 | udwBuildingType | TUINT32 | 1 | 1 |   
key6 | udwPrepareTime | TUINT32 | 20 | 1 |   
key7 | udwQuickSend | TUINT32 | 1 | 1 | 惊魂马戏团必带该参数,含义为是否在满员时立即派出,1代表是  
Key10 | {“category”:[int],“epoch”:[int],“tier”:[int]} | json格式的string | 1 | 0 | v6.6新增发起者设置的团战推荐参数  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=map_building_rally_battle&key0=30&key1=1310072&key2=1:4000:233:4000&key3=1&key4=1,3,3,5&key5=1&key6=20&key7=1&Key10=1

|lock_type|udwLockType|TUINT32|1|1|要锁的类型,含义如下| |lock_key|strLockKey|string|abc|1|要锁的目标id,不同type,id不同,如lock_type为0则传uid|
    
    
    lock_type:
        EN_LOCK_ID_TYPE__UID = 0,               // uid
        EN_LOCK_ID_TYPE__AID = 1,               // aid
        EN_LOCK_ID_TYPE__TASK_ID = 2,
        EN_LOCK_ID_TYPE__WILD = 3,              // pos
        EN_LOCK_ID_TYPE__THRONE = 4,            // sid
        EN_LOCK_ID_TYPE__ACTION_ID = 5,         // action id
        EN_LOCK_ID_TYPE__AVA_EVENT_ID = 6,
        EN_LOCK_ID_TYPE__DID = 7,
        EN_LOCK_ID_TYPE__HUNT_TEAM_ID = 8,      // 水晶岛team_id
    
    不同场景:
        GVE团战鳄鱼boss: lock_type=4, lock_key=战场sid

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 非aid类rally-非aid增援团战

  * **命令字** **_rally_reinforce_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | udwCostTime | TUINT32 | 30 | 1 |   
key1 | udwTargetPos | TUINT32 | 1310072 | 1 |   
key3 | strTroopList | string | 1:4000:233:4000 | 1 | :分隔,位数代表兵种ID  
key4 | ddwRallyWarId | TINT64 | 12345678 | 1 | 目标rally action id  
key6 | strCardList | string | 1,2,3 | 1 | ,分隔,牛仔列表  
lock_type | udwLockType | TUINT32 | 1 | 1 | 要锁的类型,含义如下  
lock_key | strLockKey | string | abc | 1 | 要锁的目标id,不同type,id不同,如lock_type为0则传uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_reinforce_battle&key0=30&key1=1310072&key3=1:4000:233:4000&key4=12345678&key6=1,2,3&lock_type=1&lock_key=abc
    
    
    不同场景:
        GVE团战鳄鱼boss: lock_type=4, lock_key=战场sid

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 非aid类rally-遣返非aid团战增援

  * **命令字** **_rally_reinforce_repatriate_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwRallyId | TINT64 | 1234567 | 1 | rally action id  
key1 | ddwReinforceId | TINT64 | 1234567 | 1 | 目标rally reinforce action id  
lock_type | udwLockType | TUINT32 | 1 | 1 | 要锁的类型,含义如下  
lock_key | strLockKey | string | abc | 1 | 要锁的目标id,不同type,id不同,如lock_type为0则传uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_reinforce_repatriate_battle&key0=1234567&key1=1234567&lock_type=1&lock_key=abc
    
    
    不同场景:
        GVE团战鳄鱼boss: lock_type=4, lock_key=战场sid

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 非aid类rally-取消非aid团战

  * **命令字** **_rally_dismiss_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwRallyId | TINT64 | 1234567 | 1 | rally action id  
key1 | ddwItemId | TINT64 | 123 | 1 | 道具id  
key2 | ddwGemCost | TINT64 | 123 | 1 | 不使用道具时,传需要消耗的宝石数量  
key3 | ddwType | TINT64 | 1 | 1 | 消耗类型,0消耗道具,1消耗宝石  
lock_type | udwLockType | TUINT32 | 1 | 1 | 要锁的类型,含义如下  
lock_key | strLockKey | string | abc | 1 | 要锁的目标id,不同type,id不同,如lock_type为0则传uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_dismiss_battle&key0=1234567&key1=123&key2=123&key3=1&lock_type=1&lock_key=abc
    
    
    不同场景:
        GVE团战鳄鱼boss: lock_type=4, lock_key=战场sid

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 非aid类rally-加速非aid团战

  * **命令字** **_rally_speedup_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwRallyId | TINT64 | 1234567 | 1 | rally action id  
key1 | ddwItemId | TINT64 | 123 | 1 | 道具id  
key2 | ddwGemCost | TINT64 | 123 | 1 | 不使用道具时,传需要消耗的宝石数量  
lock_type | udwLockType | TUINT32 | 1 | 1 | 要锁的类型,含义如下  
lock_key | strLockKey | string | abc | 1 | 要锁的目标id,不同type,id不同,如lock_type为0则传uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_speedup_battle&key0=1234567&key1=123&key2=123&lock_type=1&lock_key=abc
    
    
    不同场景:
        GVE团战鳄鱼boss: lock_type=4, lock_key=战场sid

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

#### 非aid类rally-加速非aid团战的增援队列

  * **命令字** **_rally_reinforce_speedup_battle_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | ddwReinforceId | TINT64 | 1234567 | 1 | 目标rally reinforce action id  
key1 | ddwRallyId | TINT64 | 1234567 | 1 | rally action id  
key2 | ddwItemId | TINT64 | 123 | 1 | 道具id  
key3 | ddwGemCost | TINT64 | 123 | 1 | 不使用道具时,传需要消耗的宝石数量  
lock_type | udwLockType | TUINT32 | 1 | 1 | 要锁的类型,含义如下  
lock_key | strLockKey | string | abc | 1 | 要锁的目标id,不同type,id不同,如lock_type为0则传uid  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=rally_reinforce_speedup_battle&key0=1234567&key1=1234567&key2=123&key3=123&lock_type=1&lock_key=abc
    
    
    不同场景:
        GVE团战鳄鱼boss: lock_type=4, lock_key=战场sid

  * **改动历史**

版本号 | 说明  
---|---  
v5.8 | 新增接口  
  
* * *

### 7.149.黄金圣碑-宴会活动

* * *

#### 黄金圣碑-宴会活动-宴会-生成宴会建筑

  * **命令字** **_op_gen_golden_stele_banquet_building_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 |   
key2 | type | int64 | 1 | 1 | 类型 (1:黄金圣碑-霸主宴会)  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_gen_golden_stele_banquet_building&key0=1&key1=1&key2=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 黄金圣碑-宴会活动-宴会-设置宴会开启时间

  * **命令字** **_golden_stele_banquet_building_open_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 |   
key2 | pos | int64 | 1 | 1 |   
key3 | type | int64 | 1 | 1 | 0 直接开启 1 预约开启  
key4 | time | int64 | 1 | 1 | 宴会开启时间  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=golden_stele_banquet_building_open&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**



> rsp:special json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 黄金圣碑-宴会活动-宴会-宴会加餐

  * **命令字** **_op_golden_stele_banquet_building_add_table_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | str | 1 | 1 | 宴会活动id  
key1 | sid | int64 | 1 | 1 | 宴会建筑sid  
key2 | pos | int64 | 1 | 1 | 宴会建筑坐标  
key3 | table_info | json | 1 | 1 | 加餐信息  
key4 | wild_id | int64 | 1 | 1 | 宴会建筑数值id  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_golden_stele_banquet_building_add_table&key0=1&key1=1&key2=1&key3=1&key4=1

  * **备注**


    
    
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-1)//table_info
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-2){
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-3)    "user_info":{ //加餐者信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-4)        "uid":int,
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-5)        "uname": str, // 加餐者名称
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-6)        "avatar": int, // 头像
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-7)        "head_frame": int
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-8)    },
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-9)    "table_conf":{//餐桌信息
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-10)        "$table_id": { //id
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-11)            "num":int, //数量
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-12)        }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-13)    }
    [](http://leyi_offline_gateway.leyinetwork.com:12131/interface/dev/func#cb87-14)}

> rsp:special json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 黄金圣碑-宴会活动-宴会-发起用餐队列

  * **命令字** **_march_golden_stele_banquet_table_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | cost_time | str | 1 | 1 | time  
key1 | target_pos | int64 | 1 | 1 | 坐标  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=march_golden_stele_banquet_table&key0=1&key1=1

  * **备注**



> rsp:user json

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.150.黄金圣碑霸主相关

* * *

#### 黄金圣碑霸主相关-黄金圣碑-给霸主颁发称号

  * **命令字** **_op_golden_stele_appoint_governor_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | source_id | int32 | 1 | 1 | 3:黄金圣碑霸主  
key1 | battle_sid | int32 | 1 | 1 | 战场的sid  
key2 | target_uid | int64 | 1 | 1 | 目标uid  
key3 | title_time | int32 | 1 | 1 | 称号结束时间  
key4 | title_id | int32 | 1 | 1 | 称号id,不为0时会直接使用这个id  
key5 | extra_info | json | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_golden_stele_appoint_governor&key0=1&key1=1&key2=1&key3=1&key4=1&key5=1
    
    
    extra_info格式如下:
    {
        "event_type":int
        "event_id":string, //活动id
        "end_time":long,//活动结束时间戳        -1代表永久有效
        "localization":
        {
            "int":    //lang+1
            {
                "title":"string",    //活动标题
            }
        },
        "division": long,
        "reward": [[long, long, long]],
        "sid_list": [1,2,3],
        "aid_list": [1,2,3]
    }

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑霸主相关-黄金圣碑-报名提醒消息

  * **命令字** **_op_golden_stele_send_sign_up_message_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | event_id | string | 1 | 1 |   
key1 | end_time | int64 | 1 | 1 | 报名期结束时间  
key2 | target_sid | int64 | 1 | 1 | 目标sid  
key3 | castle_lv | int64 | 1 | 1 | 主城等级  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_golden_stele_send_sign_up_message&key0=1&key1=1&key2=1&key3=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.3 | 新增接口  
  
* * *

#### 黄金圣碑霸主相关-黄金圣碑-翻译霸主宣言

  * **命令字** **_op_translate_emperor_declare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | translate_content | string | 1 | 1 | 要翻译的内容  
key1 | target_lang_id | int64 | 1 | 1 | 翻译的语言  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_translate_emperor_declare&key0=1&key1=1

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

#### 黄金圣碑霸主相关-黄金圣碑-发送霸主宣言

  * **命令字** **_op_golden_stele_public_emperor_declare_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | 原请求的json的str | string | 1 | 1 |   
key1 | 霸主宣言的内容 | string | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=op_golden_stele_public_emperor_declare&key0=1&key1=1
    
    
    原请求的json格式如下:
    {
        "op_header":
        {
            "golden_stele":
            {
                "battle_sid":int //战场
            }
        },
        "extra":
        {
            "golden_stele":
            {
                "content":string,   //参战宣言
                "utime":int, //发布宣言的时时间
                "lang":int, //v7.2.6 发布内容语言
            }
        }
    }

  * **改动历史**

版本号 | 说明  
---|---  
v7.2.6 | 新增接口  
  
* * *

### 7.151.黑名单

* * *

#### 黑名单-黑名单增加

  * **命令字** **_blackuser_add_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 121 | 1 |   
key1 | name | string | dsfds | 1 |   
key2 | avatar_id | int64 | 154 | 1 |   
key5 | extra_info | string | sdff | 1 | westgame v2.7 客户端自行定义  
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=blackuser_add&key0=121&key1=dsfds&key2=154&key5=sdff

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.34 | 新增接口  
  
* * *

#### 黑名单-黑名单删除

  * **命令字** **_blackuser_del_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | uid | int64 | 121 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=blackuser_del&key0=121

  * **改动历史**

版本号 | 说明  
---|---  
v2.1.34 | 新增接口  
  
* * *

### 7.152.黑市

* * *

#### 黑市-拉取黑市信息

  * **命令字** **_get_al_blackmarket_info_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | blackmarket_id | int32 | 0 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=get_al_blackmarket_info&key0=0

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 黑市-黑市兑换

  * **命令字** **_al_blackmarket_buy_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | goods idx | int64 | 1 | 1 |   
key1 | blackmarket_id | int64 | 1 | 1 |   
key2 | buy_num | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=al_blackmarket_buy&key0=1&key1=1&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口  
  
* * *

#### 黑市-召唤黑市

  * **命令字** **_gen_al_blackmarket_**

  * **参数**


参数名 | 含义 | 类型 | 示例 | 必传 | 备注  
---|---|---|---|---|---  
key0 | sid | int64 | 1 | 1 |   
key1 | pos | int64 | 2500600 | 1 |   
key2 | level | int64 | 1 | 1 |   
  
  * **url示例：**



> xxxxx&ksid=xxxx&sid=xxx&aid=xxx&uid=xxx&lang=xxx&in_check=0&checkac=0&op_en_flag=0&command=gen_al_blackmarket&key0=1&key1=2500600&key2=1

  * **改动历史**

版本号 | 说明  
---|---  
v2.5.1 | 新增接口
