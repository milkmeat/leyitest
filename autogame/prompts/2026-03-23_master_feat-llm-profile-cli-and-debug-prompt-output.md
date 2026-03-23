# Prompt Record

- Date: 2026-03-23 11:04
- Branch: master
- Commit: feat: --llm CLI profile 切换 + l1/l2_decide 打印完整 prompt + help 重构

---

### 1. 添加 --llm CLI 参数

给 cli 加一个参数，允许选择用哪个llm (zhipu/ollama)

> **Insight**
> - 利用已有的 `LLMConfig.switch_profile()` 方法和 `llm_secret.yaml` 多 profile 配置，只需在 CLI 入口层加一个全局 `--llm` 参数即可
> - 设计为全局参数（和 `--mock`、`--verbose` 同级），这样所有子命令都自动生效，无需每个命令单独加
> - `_load_config()` helper 封装了 `load_all` + profile 切换，5 个 LLM 相关命令统一调用

**Files:** `src/main.py`

### 2. l1/l2_decide 打印完整 prompt 和 response

仅对 l1_decide和l2_decide命令，把所有的system/user prompt和response都打印出来

**Files:** `src/main.py`

### 3. 更新 help 输出为 docstring + 补充说明

更新 --help 消息，给cli测试命令行的使用添加更详细的说明

能让 --help 直接打印doc string的内容吗？以减少重复冗余信息

**Files:** `src/main.py`
