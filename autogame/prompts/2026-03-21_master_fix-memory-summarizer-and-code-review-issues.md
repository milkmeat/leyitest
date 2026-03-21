# Prompt Record

- Date: 2026-03-21 00:00
- Branch: master
- Commit: fix: 修复 memory 摘要功能失效 + loop.py 私有属性访问 + loader profile 警告

---

### 1. 审查昨天全天提交的 commit 记录

你检查一下昨天全天提交的commit记录中（包括prompts目录下面的会话记录），看看有没有完成得不够好的地方，包括代码质量、会话内容

> **Insight**
> 代码审查的核心价值在于发现"能运行但不正确"的代码。昨天6个commit中最典型的例子是 memory 模块的 `chat_json` + 纯文本 prompt 矛盾——代码不会报错（有 fallback），但核心功能静默失效，这类问题只有通过仔细审查才能发现。

### 2. 修复优先级 1 和 2 的问题

修复 1,2

> **Insight**
> 1. **接口契约一致性**：当调用方法名含 `_json` 时，prompt 也必须要求 JSON 输出——接口名和 prompt 指令的"契约"不一致是静默 bug 的常见来源，因为 fallback 机制会掩盖问题。
> 2. **封装的价值**：`_` 前缀在 Python 中是"请勿直接访问"的约定。`MemoryStore` 已提供了 `get_latest()` 公开方法，使用它不仅更安全，还能在未来自由修改内部数据结构。

**Files:** `src/ai/memory.py`, `src/controller/loop.py`, `src/config/loader.py`
