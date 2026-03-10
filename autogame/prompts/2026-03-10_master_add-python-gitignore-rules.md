# Prompt Record

- Date: 2026-03-10 00:00
- Branch: master
- Commit: add comprehensive Python gitignore rules to project and repo root

---

### 1

把关于python的gitignore项目加入项目根目录的文件下

> **Insight**
> - **`*.py[cod]`** 是一个字符类匹配，一次性覆盖 `.pyc`、`.pyo`、`.pyd` 三种编译产物，比逐个列出更简洁
> - **`*.egg-info/` 和 `dist/`** 是 `pip install -e .`（开发模式安装）和 `python -m build` 打包时产生的目录，在本项目后续如果做包分发时会用到
> - **`.pytest_cache/` 和 `.mypy_cache/`** 分别是 pytest 和 mypy 的缓存目录，项目使用 Pydantic v2 做数据校验，配合 mypy 类型检查时这些缓存会自动生成

**Files:** `autogame/.gitignore`

### 2

加入到../gitignore，这样所有的项目都可以生效

> **Insight**
> - **Git 的 `.gitignore` 是层级继承的**：父目录的 `.gitignore` 规则会自动应用到所有子目录（包括 `autogame/`、`SLGrobot/`、`python_auto_ai/` 等），无需每个子项目重复配置
> - **子目录的 `.gitignore` 可以覆盖父级规则**：如果某个子项目需要特殊处理（比如取消忽略某个 `.env` 文件），可以在子目录的 `.gitignore` 中用 `!.env` 来反转规则
> - **原有的 Java 规则保持不变**：`.class`、`.jar` 等规则继续对 Java 子项目生效，两套规则互不冲突

**Files:** `.gitignore`
