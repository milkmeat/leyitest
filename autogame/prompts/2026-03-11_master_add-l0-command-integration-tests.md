# Prompt Record

- Date: 2026-03-11 22:00
- Branch: master
- Commit: add L0 command integration tests with CLI text commands and mock server fixes

---

### 1. Complete the test_l0_commands.md task

你来完成test_l0_commands.md

> **Insight**
> 分析发现几个关键问题：
> 1. Mock Server 行为与真实服务器不一致: add_gem 在 mock 中是 SET，但任务说明是 ADD；add_soldiers 在 mock 中是 ADD，但应该是 SET
> 2. Mock 数据缺少测试 UID: mock_data.yaml 没有 uid=20010366
> 3. 测试策略: 使用 GameAPIClient 的 async 方法，对每个命令执行 "读-改-读-验" 四步流程

**Files:** `mock_server/app.py`, `mock_server/mock_data.yaml`, `tests/test_l0_commands.py`, `test_l0.sh`, `todo/test_l0_commands.md`

### 2. Choose to fix tests based on real server behavior

> **Q:** 测试发现 ADD/SET 行为与描述相反（add_gem 实测为 SET，add_soldiers 实测为 ADD），move_city 一直失败（ret_code=20009/21105），如何处理？

按实测行为修正测试

**Files:** `mock_server/app.py`, `tests/test_l0_commands.py`

### 3. Switch to CLI text commands instead of Python function calls

测试动作全部使用 "l0 MOVE_CITY 20010413 500 500" 这样的文本指令来触发，不要调python函数

> **Insight**
> CLI 文本指令测试 vs Python 函数调用的设计取舍：
> 1. CLI 方式更接近真实使用场景 — 测试的是完整链路（参数解析 → API 调用 → 响应解析），而不只是底层函数逻辑
> 2. L0 执行器路径 (l0 MOVE_CITY) 比直接 move_city 多了 UID 校验、指令反序列化等步骤，能覆盖更多代码路径
> 3. 为了让 bash 脚本简洁，新增了 get_gem/get_soldiers 输出纯数字的查询命令 — 这体现了"为可测试性设计接口"的原则

**Files:** `src/main.py`, `test_l0.sh`, `tests/test_l0_commands.py` (deleted)
