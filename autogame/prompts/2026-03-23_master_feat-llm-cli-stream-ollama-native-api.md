# Prompt Record

- Date: 2026-03-23 12:30
- Branch: master
- Commit: feat: --llm CLI 切换 + 流式输出 + Ollama 原生 API (think=false)

---

### 1. 添加 --llm CLI 参数

给 cli 加一个参数，允许选择用哪个llm (zhipu/ollama)

> **Insight**
> - 利用已有的 `LLMConfig.switch_profile()` 方法和 `llm_secret.yaml` 多 profile 配置，只需在 CLI 入口层加一个全局 `--llm` 参数即可
> - 设计为全局参数（和 `--mock`、`--verbose` 同级），这样所有子命令都自动生效
> - `_load_config()` helper 封装了 `load_all` + profile 切换，5 个 LLM 相关命令统一调用

**Files:** `src/main.py`

### 2. l1/l2_decide 打印完整 prompt

仅对 l1_decide和l2_decide命令，把所有的system/user prompt和response都打印出来

**Files:** `src/main.py`

### 3. 更新 help 输出

更新 --help 消息，给cli测试命令行的使用添加更详细的说明

能让 --help 直接打印doc string的内容吗？以减少重复冗余信息

**Files:** `src/main.py`

### 4. Ollama num_ctx 参数

在调用ollama的时候，多传入一个参数 num_ctx=16384

**Files:** `src/ai/llm_client.py`

### 5. 所有 LLM 统一流式输出

所有的llm包括zhipu也可以使用流式吗？都用流式吧

**Files:** `src/ai/llm_client.py`

### 6. 排查 Ollama 卡死问题

加上 2>&1后能在终端实时看到llm输出吗，"python src/main.py l1_decide 1 --mock-l2 "[小队 1 (Alpha)] 控制 建筑 pos:( 154, 170 )" --l1-prompt ava_test --ava 29999 --llm ollama 2>&1"

> **Insight**
> - 根因：qwen3.5 模型即使传了 `think=False`，在 Ollama 的 OpenAI 兼容端点 (`/v1/`) 中仍然在做 reasoning
> - OpenAI SDK 的 `delta` 对象不包含 `reasoning` 字段，但 `model_extra` 属性保留了额外字段
> - 之前"卡死"的真相：模型在 thinking 阶段 `delta.content` 全是空字符串，看起来像无响应

**Files:** `src/ai/llm_client.py`

### 7. Ollama think=false 传参方式

> **Q:** nothink或者think=false标签要怎么传给ollama

https://github.com/ollama/ollama/issues/14617 上述文档中指出："There is currently no way to set thinking mode via the Modelfile (#10961). If you are using the API, set "think":false." ，只是不能通过修改model file永久禁止thinking,但是可以通过API参数，每次抑制thinking

### 8. 改用 Ollama 原生 API

> **Q:** 方案1（对 Ollama 改用原生 API /api/chat）还是保持现状？

方案1. 确保zhipu的调用不会受影响

> **Insight**
> - Ollama 走原生 `/api/chat` + `think: false` + aiohttp 流式：无 thinking 开销，直接输出 content
> - Zhipu 继续走 OpenAI SDK `stream=True`：不受任何影响
> - 两条路径通过 `is_ollama` 标志自动切换，对上层完全透明

**Files:** `src/ai/llm_client.py`
