# Prompt Record

- Date: 2026-05-21 10:25
- Branch: master
- Commit: feat: L2 AVA prompt 多版本管理（--l2-prompt 参数 + prompts 列表命令）

---

### 1

我需要测试L2 ava prompt的多个版本，
1. 添加L2 ava prompt的多版本管理功能
2. cli 添加命令允许列出有多少个版本（有一个是默认版本，未指定参数时用）
3. 在 "CLI --team 2 run --ava AVA_ID" 启动对战控制时，添加一个参数允许指定使用哪个prompt版本
4. 添加prompt只需要在对应目录下新建txt文件即可，cli能自动识别并根据参数选用

> **Insight**
> - 采用"子目录 + 文件名即版本名"模式，比命名约定（如 `l2_system_ava_v2.txt`）更清晰，扩展性更好
> - 保留旧文件 `l2_system_ava.txt` 作为 fallback，确保向后兼容——即使忘记迁移也不会崩溃
> - 复用已有的 `--l1-prompt` 参数模式，CLI 风格一致，学习成本为零

**Files:** `src/ai/prompts/l2_ava/default.txt`, `src/ai/l2_commander.py`, `src/controller/loop.py`, `src/main.py`
