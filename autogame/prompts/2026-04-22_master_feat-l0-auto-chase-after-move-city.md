# Prompt Record

- Date: 2026-04-22 11:00
- Branch: master
- Commit: feat: L0 移城后自动追击，消除降级浪费的 loop 周期（66→1）

---

### 1. 分析 investigate_action_downgrade_to_move_city

@todo\investigate_action_downgrade_to_move_city.md , 根据当前 logs/ 目录下的最新结果重新分析，制定计划

> **Plan**
> ## 修改计划
> ### Fix 1: L0 移城后自动追击（核心，消除浪费的 loop 周期）
> **文件**: `src/executor/l0_executor.py` — `execute_batch()` 方法
> **位置**: 第 497 行（移城失败重试之后）与第 498 行（`results.append`）之间
> **逻辑**:
> - 移城成功且 original_attack_instr 存在时:
>   1. 更新 _accounts[uid].city_pos 为移城目标坐标
>   2. 对 original_attack_instr 重新执行 _preprocess_lvl_attack_building
>   3. 如果预处理结果不是 MOVE_CITY 且未被跳过 → 执行攻击/驻防
>   4. 用追击结果替换移城结果（保持 instructions/results 1:1 对应）
>
> ### Fix 2: L1 prompt 增加距离决策引导
> 告知 L1 "L0 自动处理远距离移城"，而非教 L1 自己发两条指令
>
> ### Fix 3: error=-161 文档注释
> svr_city_wall push 中的 error=-161 是城墙状态重置通知，无需处理
>
> 设计考量：让 L0 自动追击而非教 L1 发两条指令。原因：(1) Fix 1 已在 L0 层解决效率问题；(2) LLM 生成两条有序指令容易出错；(3) 让 L1 专注于"选什么目标"而非"怎么到达"。

> **Insight**
> 核心设计决策：让 L0 自动追击而非教 L1 发两条指令。原因有三：
> 1. 可靠性：L0 是确定性代码，LLM 生成有序指令对容易出错（坐标不一致、顺序颠倒）
> 2. 关注点分离：L1 负责"打什么"，L0 负责"怎么到达"——移城是执行层的实现细节
> 3. 向后兼容：即使 L1 不改变行为，Fix 1 也能独立生效
>
> "移城后追击"模式的核心价值：MOVE_CITY 是瞬移操作（服务器端即时完成），所以在同一个 HTTP 请求周期内就能紧接着发送攻击指令。之前浪费 60s 等下一轮完全没必要。
>
> result 替换而非追加的设计：_build_l0_log 用 zip(instructions, results) 做 1:1 配对。追击成功后用攻击结果替换移城结果，让日志看起来就像一次正常的攻击——"实现细节不泄漏到上层"。

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system_ava.txt`, `todo/investigate_action_downgrade_to_move_city.md`
