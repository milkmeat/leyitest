# WestGame AI 团战系统 — 使用说明

## 1. 环境准备

### 1.1 安装依赖

```bash
cd autogame
pip install -r requirements.txt
```

主要依赖：`pydantic`, `aiohttp`, `openai`（兼容接口）, `numpy`, `scikit-learn`

### 1.2 Python 版本

Python 3.11+

---

## 2. 项目配置

### 2.1 LLM 模型配置

**文件位置**: `config/llm_secret.yaml`（已 gitignore，不会提交）

```yaml
active_profile: "zhipu"  # 切换模型只需改这一行

profiles:
  zhipu:
    model: "GLM-4.5-Air"
    base_url: "https://api.z.ai/api/coding/paas/v4"
    api_key: "你的API密钥"

  ollama:
    model: "qwen3.5:4b"
    base_url: "http://10.10.16.41:11434/v1"
    api_key: "sk-ollama"

  openai:
    model: "gpt-4o"
    base_url: "https://api.openai.com/v1"
    api_key: "sk-xxx"

  deepseek:
    model: "deepseek-chat"
    base_url: "https://api.deepseek.com/v1"
    api_key: "sk-xxx"
```

**切换模型**: 修改 `active_profile` 字段即可。所有 profile 使用 OpenAI 兼容接口格式。

### 2.2 L2 / L1 / L0 层级概念

系统采用递归分层指挥体系：

| 层级 | 角色 | 说明 |
|------|------|------|
| **L2** | 军团指挥官 | 1 个 LLM，负责全局战略决策。输入全局态势摘要，输出给每个小队的战略指令（如"去攻击某建筑"、"增援某据点"） |
| **L1** | 小队队长 | 4 个 LLM 并行，每个管理 1 个小队（5 人）。将 L2 的战略指令翻译为具体行动（哪个账号做什么） |
| **L0** | 执行层 | 纯 Python 代码，将 L1 的行动指令翻译为游戏 HTTP API 调用，并做合法性校验 |

**决策流**: L2 看全局 → 下发战略 → L1 看局部 → 生成行动 → L0 校验并执行

### 2.3 账号与小队配置

**账号列表**: `config/accounts.yaml`

- 我方联盟 (TestSquad2026, aid=20000118): 20 个活跃账号 (acc_01 ~ acc_20)
- 敌方联盟 (PhoenixRise2026, aid=20000119): 20 个活跃账号 (enemy_01 ~ enemy_20)
- 另有 21 个预备账号可用

**小队划分**: `config/squads.yaml`

我方 4 个小队，每队 5 人：
- Squad 1 (Alpha): UID 20010643-20010647
- Squad 2 (Bravo): UID 20010648-20010652
- Squad 3 (Charlie): UID 20010653-20010657
- Squad 4 (Delta): UID 20010658-20010662

敌方同样 4 个小队 × 5 人。

### 2.4 环境配置

**文件位置**: `config/env_config.yaml`

```yaml
current_env: test  # 可选: test / mock

environments:
  test:
    name: 测试环境
    url: https://leyi-offline-game-alb.leyinetwork.com/p10-test-lc-proxy
  mock:
    name: 本地Mock
    url: http://localhost:18888/mock
```

---

## 3. 创建 AVA 战场（Claude Skill）

在 Claude Code 中可以直接用自然语言触发 `create_ava` skill：

### 3.1 创建战场

对 Claude 说：
> "创建一个 ava 战场，id=40002，持续 2 小时"

等价于执行：
```bash
python src/main.py uid_ava_create 40002 duration=2
```

### 3.2 全员加入战场

对 Claude 说：
> "把所有账号加入战场 40002"

等价于执行：
```bash
python src/main.py uid_ava_join_all 40002
```

### 3.3 单个账号加入

```bash
# Step 1: 加入名单（camp_id: 1=我方, 2=敌方）
python src/main.py uid_ava_add 40002 20010643 1
# Step 2: 进入战场
python src/main.py uid_ava_enter 40002 20010643
```

### 3.4 创建新账号并更新配置

如果需要新增测试账号：
1. 通过 GM 后台创建账号，获得新 UID
2. 编辑 `config/accounts.yaml`，在对应联盟的 `active` 列表中添加新账号
3. 编辑 `config/squads.yaml`，将新账号分配到某个小队

---

## 4. L2 策略：修改与新增

### 4.1 策略文件位置

```
src/ai/prompts/l2_ava/
├── default.txt    # 均衡策略（根据积分态势动态攻防）
├── attack.txt     # 纯进攻策略（全力抢建筑，不防守）
└── defend.txt     # 防守策略（优先巩固已有建筑）
```

### 4.2 策略文件结构

每个策略文件是一个完整的 L2 System Prompt，包含：
- **角色定义**: 告诉 LLM 它是军团指挥官
- **AVA 规则**: 战场特殊机制（集结、建筑、得分）
- **战略原则**: 决策优先级和约束
- **动态策略**: 根据积分领先/落后的不同行为
- **建筑速查表**: 各建筑分值和开放时间
- **输出格式**: 严格 YAML 格式要求

### 4.3 新增策略

1. 在 `src/ai/prompts/l2_ava/` 下创建新文件，如 `rush.txt`
2. 参考 `default.txt` 的结构编写 prompt
3. 使用时通过 `--l2-prompt rush` 指定

**关键注意事项**:
- 输出格式必须保持 YAML `orders:` 结构不变（L1 依赖解析）
- 必须为每个小队生成指令（不可遗漏）
- 可以自由修改"战略原则"和"动态策略"部分来改变 AI 行为

### 4.4 调试策略

单次执行 L2 决策（不启动完整循环）：
```bash
python src/main.py l2_decide --ava 40001 --l2-prompt default
```

查看 L1 小队视图：
```bash
python src/main.py l1_view 1
```

---

## 5. 对战模拟测试 (ava_simulate.sh)

### 5.1 基本用法

```bash
./ava_simulate.sh --v1 default --v2 attack --rounds 3 --duration 30
```

**参数说明**:

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--v1` | default | 第一个 L2 策略版本名（对应 `l2_ava/` 下的文件名，不含 .txt） |
| `--v2` | attack | 第二个 L2 策略版本名 |
| `--rounds` | 1 | 对战轮数。每轮包含 2 场（交换阵营位置），消除位置偏差 |
| `--duration` | 60 | 每场对战时长（分钟） |
| `--csv` | ava_results.csv | 结果输出 CSV 文件路径 |

### 5.2 运行流程

每场对战自动执行：
1. 探测空闲战场 ID (40001-40100)
2. 创建新战场
3. 全员退出旧战场 → 全员加入新战场
4. 补给资源（宝石 + 士兵）
5. 记录起始状态
6. 启动双方 AI 主循环（后台并行）
7. 启动观察者循环（30 秒轮询记录积分变化）
8. 等待对战结束，记录最终积分和兵力损失

### 5.3 输出

- **终端**: 实时显示每场比分和胜负
- **CSV 文件**: 详细事件记录（积分变化、建筑易手、领先切换等）
- **日志目录**: `logs/` 下保存每场的详细日志

### 5.4 示例

```bash
# 均衡 vs 进攻，3 轮（6 场），每场 30 分钟
./ava_simulate.sh --v1 default --v2 attack --rounds 3 --duration 30

# 防守 vs 进攻，1 轮快速测试
./ava_simulate.sh --v1 defend --v2 attack --rounds 1 --duration 15

# 自定义策略对比
./ava_simulate.sh --v1 rush --v2 default --rounds 2 --duration 45
```

---

## 6. 可视化与等级分 (visualize_ava.py)

### 6.1 用途

将 `ava_simulate.sh` 产出的 CSV 数据转换为可视化 HTML 报告，包含：
- **Elo 等级分排名**: 基于对战胜负计算各策略的 Elo Rating（初始 1500，K=32）
- **对战矩阵**: 策略间的胜-负-平记录
- **积分走势图**: 每场对战的双方积分随时间变化曲线（Chart.js 折线图）
- **比赛摘要**: 领先切换次数、Factory 易手次数、胜方领先时间占比

### 6.2 使用方法

```bash
# 确保 ava_results.csv 存在（由 ava_simulate.sh 生成）
python visualize_ava.py
```

**输入**: `ava_results.csv`（当前目录）
**输出**: `ava_report.html`（当前目录，浏览器打开即可查看）

### 6.3 Elo 等级分说明

- 初始分: 1500
- K 因子: 32
- 每场对战按时间顺序更新双方 Elo
- 多轮对战后，Elo 分数越高的策略越强
- 对战矩阵显示任意两个策略间的直接胜负记录 (W-L-D)

### 6.4 积分走势图

- X 轴: 时间（分钟），线性均匀刻度
- Y 轴: 积分
- ★ 标记: Factory 易手事件
- 蓝线: 策略 A，红线: 策略 B

---

## 7. 常用命令速查

```bash
# ── 启动 AI 主循环 ──
python src/main.py run --ava 40001 --l2-prompt default

# ── 调试单次决策 ──
python src/main.py l2_decide --ava 40001 --l2-prompt attack
python src/main.py l1_decide 1 --ava 40001

# ── 查看状态 ──
python src/main.py get_ava_score 20010643 40001
python src/main.py get_player_info 20010643

# ── 战场管理 ──
python src/main.py uid_ava_create 40002 duration=2
python src/main.py uid_ava_join_all 40002

# ── A/B 对战测试 ──
./ava_simulate.sh --v1 default --v2 attack --rounds 2 --duration 30

# ── 生成可视化报告 ──
python visualize_ava.py
# 然后浏览器打开 ava_report.html
```

---

## 8. 注意事项

1. **llm_secret.yaml 不要提交**: 该文件包含 API 密钥，已在 .gitignore 中。首次使用需手动创建
2. **测试环境限制**: AVA 命令必须使用已加入战场的 UID，否则会报错
3. **战场 ID 范围**: 40001-40100，simulate 脚本会自动探测空闲 ID
4. **日志查看**: 每轮决策日志在 `logs/` 目录下，JSON 格式
5. **LLM 超时**: 默认 30 秒超时，如果模型响应慢可在 `config/` 中调整
6. **Windows 用户**: `ava_simulate.sh` 需要在 Git Bash 或 WSL 中运行
