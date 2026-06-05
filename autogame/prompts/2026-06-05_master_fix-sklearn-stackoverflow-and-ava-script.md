# Prompt Record

- Date: 2026-06-05 10:40
- Branch: master
- Commit: fix: 用纯 Python DBSCAN 替换 sklearn 修复 run 启动栈溢出

  asyncio 事件循环线程内导入 sklearn (经 l2_view→l2_commander 链)
  触发 Windows 原生栈溢出，run 进程 exit 127 静默崩溃，导致 AVA
  模拟全程无 LLM 决策、无动作、积分零。

  - l2_view.py: 移除 numpy/sklearn 顶层导入，新增纯 Python _dbscan
    函数（行为与 sklearn 默认 DBSCAN 一致），改写 _cluster_enemies
    用纯 Python 算中心/bbox。test_l2_view.py 25 个测试全绿。
  - requirements.txt: 移除 numpy 和 scikit-learn（全项目无其它引用）。
  - ava_simulate.sh: 同步 SCORE_UID/OUR_UIDS/ENEMY_UIDS 到新批次
    20013796-20013835；run 进程 stdout/stderr 重定向到 logs/
    run_team*.log，避免崩溃被静默吞掉；新增 --matches-per-round
    开关支持单场快速测试。
  - .gitignore: 忽略 ava_results.csv 等 AVA 模拟运行产物。

---

### 1

用ava_simulate.sh怎么快速跑一场15分钟的测试

> **Insight**
> - 脚本里"一场"和"一轮"不是一回事：`--rounds 1` 实际跑 **2 场**（脚本第 311-319 行，每轮固定先 `Team1=V1/Team2=V2`，再交换成 `Team1=V2/Team2=V1`），目的是消除阵营位置偏差。所以 `--duration 15` 的总耗时是 ≈30 分钟对战 + 每场的建场/补给开销。
> - `--duration` 控制的是 `sleep` 时长（第 257 行），即 AI 实际对打多久；而建场命令固定写死 `duration=2`（第 196 行，战场本身的存活时长），两者无关，改 `--duration` 不会动战场寿命。
> - 每场开始会自动归档旧 `logs/` 目录、重置账号、补给资源（gem + 三兵种各 100 万），所以无需手动清理。

### 2

增加一个开关，设置一回合是一场还是两场

> **Insight**
> - **校验放在解析之后、使用之前**：`--matches-per-round` 的合法性检查（只能 1 或 2）放在参数解析循环结束、`TOTAL_MATCHES` 计算之前。这是 shell 脚本的惯例——先收集全部输入，再统一校验，避免在解析循环里写一堆分散的检查。
> - **消除"魔法数 2"**：原脚本三处硬编码了 `×2`/`÷2`/`%2`（`TOTAL_MATCHES`、汇总区的 round/match 还原）。这些都隐式假设"每轮 2 场"。引入开关时必须把它们全替换成 `MATCHES_PER_ROUND` 变量，否则单场模式下汇总区的 Round/Match 编号会算错（比如 5 场会显示成 Round3 Match1 而非 Round5 Match1）。这是加开关时最容易漏的地方。
> - **默认值保持向后兼容**：默认仍是 2，所有现有调用（包括没带这个参数的）行为完全不变，只有显式传 `1` 才进入快速单场模式。

**Files:** `ava_simulate.sh`

### 3

> **Q:** 在 15 分钟的模拟战斗中，你没看到 LLM 输出、账号没动作就结束了。是 LLM 调用出问题了吗？（用户附了脚本运行日志，显示 Score 0/0、Loss 0/0）

在15分钟的模拟战斗中，我没有看到llm的输出，账号也没有任何动作，就结束了。是否llm的调用出问题了。

（附上一段运行日志：补给完成、起始兵力 49198880、Score Camp1=0 Camp2=0、Loss T1=0 T2=0）

### 4

> **Q:** 根因已确认：asyncio 线程内 import sklearn 导致 Windows 原生栈溢出，run 进程静默崩溃 (exit 127)。另外 ava_simulate.sh 的 UID 还停留在旧账号。你希望我修复到什么程度？（选项：两个都修 / 只修 run 崩溃 / 只先验证根因）

什么地方需要用到sklearn，可以不import它吗？

### 5

4项都执行

### 6

commit

### 7

ava_results.csv 不需要提交，加入gitignore

**Files:** `src/perception/l2_view.py`, `requirements.txt`, `ava_simulate.sh`, `.gitignore`, `prompts/2026-06-05_master_fix-sklearn-stackoverflow-and-ava-script.md`
