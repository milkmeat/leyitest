# Prompt Record

- Date: 2026-03-31
- Branch: master
- Commit: docs: CLAUDE.md 添加 error_msg.yaml 错误码表引用

---

### 1. Document error_msg.yaml reference in CLAUDE.md

在claude.md记录一下，test server所返回的错误代码，可以在error_msg.yaml中查询

> **Insight**
> `error_msg.yaml` 合并了两个数据源：客户端的 `doc_err_info`（1369条，有用户友好文本）和服务端的 `ETshpErrCode`（838条，枚举定义）。带 `[SVC]` 前缀的条目来自服务端，在客户端文档中没有对应文本。调试时如果看到错误码，直接按数字查这个文件即可。

**Files:** `CLAUDE.md`
