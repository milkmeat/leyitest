## Prompt Record

- Date: 2026-06-15 16:18
- Branch: master
- Commit: refactor: L2 AVA prompt fallback 改读 l2_ava/default.txt 并删除冗余 l2_system_ava.txt

---

### 1

对比一下 @src\ai\prompts\l2_system_ava.txt 和 @src\ai\prompts\l2_ava\default.txt 内容一样吗

> **Insight**
> - **判断文件相等的可靠手段**：`diff` 看差异 + `md5sum` 看哈希。仅靠 `wc -l` 行数相同不能证明内容一致（同一行可能字符不同），而仅看 md5 又看不出"哪里不同"。两者结合既给结论又给证据。
> - **同 prompt 出现在两处**通常意味着系统正在做"按场景路由 prompt"的重构：`l2_system_ava.txt` 是历史扁平命名，`l2_ava/default.txt` 是按目录分组的新结构（`l2_ava/` 目录下可放 `default.txt`、`aggressive.txt`、`defensive.txt` 等多策略变体）。在这个项目里看到 `prompts/` 目录直接放 `l2_system.txt`、`l1_system.txt` 的扁平命名（见 CLAUDE.md 的目录结构），而 `l2_ava/` 子目录是新增的，说明 AVA 战场正在迁移到"主 prompt + 多策略变体"的目录化结构。
> - **两份相同文件存在的风险**：未来修改其中一份而忘了同步另一份，会导致行为漂移——取决于代码加载哪一个。建议确认调用方走哪条路径后，删掉旧的或让其中一个 import/链接到另一个，避免 drift。

### 2

检查一下

> **Insight**
> - **fallback 链的代价**：保留 `l2_system_ava.txt` 这条 fallback 看似"安全"，实际上当 `default.txt` 存在时它永远跑不到，但又不能直接删——因为代码里第 72 行 `_load_prompt("l2_system_ava.txt")` 还在引用它，删除会让 fallback 路径直接抛 `FileNotFoundError`，再降级到第 76 行的 `l2_system.txt`（非 AVA 通用 prompt，AVA 战场会走错策略）。这是典型的"渐进迁移留下的中间态"。
> - **真正的风险是 silent drift**：现在两份字节相同，所以无论走哪条路结果都对。一旦有人改了 `l2_system_ava.txt` 而忘了同步 `default.txt`（反之亦然），运行时跑的是后者，但所有 prompts/ 历史记录显示开发者一直在改前者——会出现"我明明改了 prompt 但行为没变"的诡异 bug。最近的 `2026-05-19` 和 `2026-05-14` 几次改动都还在写 `l2_system_ava.txt`，说明这个混淆已经在发生。
> - **干净的解法**有两条：(a) 删 `l2_system_ava.txt`，把 l2_commander.py:72 的 fallback 直接改成读 `l2_ava/default.txt`；(b) 把 `l2_system_ava.txt` 改成符号链接/同步脚本指向 `l2_ava/default.txt`。Windows 下 (a) 更省事。

### 3

> **Q:** 需要我把 `l2_system_ava.txt` 删掉并把 `l2_commander.py:72` 的 fallback 改成 `l2_ava/default.txt` 吗？这样就只剩一份"事实来源"，避免今后再出现同步遗漏。

好的

> **Insight**
> - **回归验证的正确姿势**：测试一开始就 fail 时，先 `git stash` 跑一遍**原始代码**——如果同样失败，说明是 pre-existing，不应该阻塞当前改动；如果原本通过，那才是回归。这一招把"我的改动导致测试坏了"和"测试本来就坏"区分开，避免被误导去修无关的 mock 问题。
> - **改动没有被现有单测覆盖**也是一个发现：`tests/test_l2_commander.py` 里完全没有 `ava` / `prompt_template` 的测试用例，意味着 AVA prompt 加载路径在改造前就处于零自动化测试覆盖。这也解释了为什么之前会留下 `l2_system_ava.txt` 和 `l2_ava/default.txt` 两份相同副本——光靠测试 CI 抓不到。如果想长期防止 drift，可以把刚才那段冒烟脚本固化到 `test_l2_commander.py` 里作为 `TestL2AvaPromptLoading` class。
> - **fallback 链的健康改造**：原代码用 `try/except FileNotFoundError` 包 `_load_prompt`，新代码改成显式 `os.path.isfile` 判断 + `default.txt` 路径。前者依赖异常控制流，后者更直接——而且既然主路径（`versioned_path`）也是用 `os.path.isfile` 判断的，fallback 分支保持同样的风格，代码更对称易读。

**Files:** `src/ai/l2_commander.py`, `src/ai/prompts/l2_system_ava.txt`

### 4

> **Q:** 下一步建议：要不要把冒烟测试沉淀进 `tests/test_l2_commander.py` 作为正式单测？不然今后再有人误改 `_L2_AVA_DIR` 路径或 fallback 顺序，CI 还是抓不到。

ok

> **Insight**
> - **测试与实现解耦的小技巧**：`test_named_version_loads_specific_file` 不写 `prompt_version="attack"`，而是 `non_default = [v for v in versions if v != "default"][0]` 动态挑一个。这样 `attack.txt` 哪天改名为 `aggressive.txt`，测试照样跑得通；如果未来真的只剩一个 `default.txt`，测试会优雅 `pytest.skip` 而不是 fail。**写守护型测试时，断言"行为契约"，不要锁死"具体内容"**——否则单测会变成阻碍重构的负担。
> - **断言日志内容是廉价但高价值的回归保护**：第 2 条用例里 `assert "fell back to l2_ava/default.txt" in caplog.text` 看起来微不足道，但它直接反映了我改造后日志字符串的具体形式。如果未来有人把 fallback 路径再改回去（比如改成 `l2_system.txt` 又重新创建 `l2_system_ava.txt`），这条断言会先一步炸出来。**日志即合约**——尤其是 fallback、降级、warning 这类"非主路径"的代码，单元行为往往就是日志输出。
> - **5 条测试只用了 0.63 秒**，因为它们不调 LLM、不构造 snapshot、只读 prompt 文件。在写"加载/配置/路径"类测试时，**不要拿正常路径的 fixture 顺手跑**——最小化构造能让单测便宜到几乎零成本，鼓励别人多写。这个项目的 `_make_snapshot`、`_mock_llm_client` 都不需要在这里出现，正是因为我们只测加载逻辑而不测 decide 流程。

**Files:** `tests/test_l2_commander.py`
