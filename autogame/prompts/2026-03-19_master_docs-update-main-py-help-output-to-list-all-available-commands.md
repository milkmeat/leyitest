# Prompt Record

- Date: 2026-03-19
- Branch: master
- Commit: docs: update main.py help output to list all available commands

---

### 1. 更新 main.py --help 帮助信息，列出所有可用命令

更新一下 python main.py --help 所打印的信息，列出所有可用命令

> **Insight**
> 1. **命令分组策略**：通过按功能分类（AI决策调试、查询、行动、uid_helper等）使大量命令更易于浏览
> 2. **双重文档维护**：同时更新了文件顶部 docstring 和 `main()` 函数中的 help 输出，确保一致性

**Files:** `src/main.py`
