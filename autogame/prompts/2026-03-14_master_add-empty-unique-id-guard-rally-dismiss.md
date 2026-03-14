# Prompt Record

- Date: 2026-03-14 13:02
- Branch: master
- Commit: add empty unique_id guard to rally_dismiss CLI command

---

### 1. Guard rally_dismiss against empty unique_id

给rally_dismiss加个检查，不让他发空的unique_id。如果为空打印一个错误信息，退出。

> **Insight**
> - 将 `unique_id` 的默认值设为 `""` 而非保持必填参数，这样即使 CLI 调用时漏传参数也不会抛 Python TypeError，而是给出友好的中文错误提示
> - `strip()` 额外处理了传入纯空白字符串的边界情况

**Files:** `src/main.py`
