# Prompt Record

- Date: 2026-04-15 12:00
- Branch: master
- Commit: feat: 新增 ava_simulate.sh AVA 战场模拟对战脚本

---

### 1. 审阅 ava_simulate.md 补充项

看一下ava_simulate.md，有没有要补充的

> **Insight**
> ava_simulate.md 是一个 shell 脚本的需求文档，核心是串联已有 CLI 命令完成一场完整的 AVA 模拟对战。关键在于确保文档中的命令和参数与实际代码一致。

**Files:** `todo/ava_simulate.md`

### 2. 确认问题答案来源

阅读代码，你自己确认一下以上问题哪些可以从代码中找到答案

### 3. 确认时长控制方式

> **Q:** 1小时时长控制方式：脚本自己用 sleep+kill 还是给 run 命令加 --duration？

1. 脚本自己用sleep+kill来控制时长
2. 加上duration 参数,默认1小时
3. 什么是trap清理？
4. 每个兵种都加

**Files:** `todo/ava_simulate.md`

### 4. 确认兵种 ID

兵种只使用 4, 104, 204 这三种

**Files:** `todo/ava_simulate.md`

### 5. 确认战场检查方式

战场确认方式：：直接调用 `uid_ava_create`，已存在时根据返回错误码判断

**Files:** `todo/ava_simulate.md`

### 6. 制定实现计划

依照ava_simulate.md完成plan

> **Plan**
> 创建 `ava_simulate.sh`（项目根目录），沿用项目已有 shell 脚本风格。配置区硬编码 40 个 UID，辅助函数包含 cli()、parse_camp_score()、cleanup()。11 步执行流程：创建战场 → 全员退出 → 全员加入 → 补给资源(40 UID × 4 命令) → 记录起始积分 → 启动双方对战(后台) → sleep 等待 → kill 停止 → 记录终止积分 → 全员退出 → 打印得分差。关键：--team 是全局参数须放命令名之前，积分用 sed 解析去逗号，trap EXIT INT TERM 管理后台进程。

### 7. 运行 1 分钟快速验证

./ava_simulate.sh 29999 1

### 8. 运行 10 分钟测试

./ava_simulate.sh 29999 10
