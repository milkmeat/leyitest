# Prompt Record

- Date: 2026-03-24 15:30
- Branch: master
- Commit: feat: LLM 输出格式 JSON → YAML，节省 30-40% tokens

---

### 1. L1 LLM 输出格式改为 YAML

在l1 llm的思考中，让他返回yaml格式的数据而非Json格式，以节省输出token，加快反馈速度

> **Insight**
> - **YAML vs JSON Token 差异**: JSON 需要大量 `"` 引号、`,` 逗号、`[]` 括号；YAML 靠缩进，省略这些符号
> - **估算节省**: 对于 L1 的 10-20 条指令，YAML 可节省约 30-40% output tokens
> - **解析兼容性**: PyYAML 已在项目中（用于配置文件），可直接复用

**Files:** `src/ai/prompts/l1_system.txt`, `src/ai/llm_client.py`, `src/ai/l1_leader.py`

### 2. AVA/AVA_Test prompt 也改为 YAML

l1 system ava 和ava_test这两个prompt也改一下

**Files:** `src/ai/prompts/l1_system_ava.txt`, `src/ai/prompts/l1_system_ava_test.txt`

### 3. L2 也改为 YAML

L2也改

**Files:** `src/ai/prompts/l2_system.txt`, `src/ai/l2_commander.py`

### 4. 对比 ava 与 ava_test prompt 差异

对比一下l1 ava/ava_test两个prompt，内容上有何异同

> **Insight**
> **潜在问题**：`ava_test` 的 `building_id` 格式要求（完整 unique_id）与 `ava` 不一致。如果实际服务器需要完整格式，`ava` 可能会产生无效指令。

### 5. 同步 building_id 格式到 ava

> **Q:** 是否需要将 `ava_test` 的 building_id 格式要求同步到 `ava`？

yes

**Files:** `src/ai/prompts/l1_system_ava.txt`
