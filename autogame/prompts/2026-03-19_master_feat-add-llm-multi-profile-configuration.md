# Prompt Record

- Date: 2026-03-19
- Branch: master
- Commit: feat: add LLM multi-profile configuration for quick model switching

---

### 1. 添加 LLM 多模型配置快速切换功能

修改一下 llm的配置模块，我想能方便地切换到本地 ollama 模型 做简单测试 （保存多个模型配置进行快速切换）

> **Insight**
> 设计方案：
> 1. 使用 `profiles` 结构存储多个模型配置
> 2. 用 `active_profile` 字段快速切换
> 3. 保持向后兼容，同时支持新的多配置模式

**Files:** `src/config/schemas.py`, `src/config/loader.py`, `config/llm_secret.yaml.example`, `config/llm_secret.yaml`
