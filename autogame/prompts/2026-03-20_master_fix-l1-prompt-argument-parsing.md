# Prompt Record

- Date: 2026-03-20 23:00
- Branch: master
- Commit: fix: correct --l1-prompt argument parsing for space-separated format

- Fixed cmd_l1_decide to support both --l1-prompt=value and --l1-prompt value formats
- Fixed Building.obj_type attribute reference in memory.py (was using .type)
- Added debug logging to verify prompt template loading

This fixes the critical bug where LLM was generating main world commands
(ATTACK_TARGET) instead of AVA battlefield commands (LVL_ATTACK_BUILDING)
despite using --l1-prompt ava parameter.

Root cause: Argument parser only supported equals format but command was
called with space-separated format. LLM defaulted to standard l1_system.txt
prompt instead of l1_system_ava.txt.

After fix:
- L1Leader correctly loads l1_system_ava.txt (5216 chars)
- LLM generates proper AVA commands: LVL_ATTACK_BUILDING, LVL_MOVE_CITY, etc.
- Instructions include building_key and other AVA-specific fields

---

### 1. Fix grep encoding issues in prepare_alpha.sh

检查 prepare_alpha.sh，使用正确指令进入ava战场. grep中不要使用中文字符串，可能会有乱码

**Files:** `scripts/prepare_alpha.sh`

### 2. Convert log output to English

日志中有很多中文乱码，先把L1输出的内容和指令改成全英文

**Files:** `src/ai/l1_leader.py`, `src/perception/l1_view.py`

### 3. Investigate LLM prompt and output

我们输入给l1的prompt是什么？ 跑一次 l1_decide (with 正确的 rompt参数），看看他输出什么

> **Insight**
> The LLM was generating `ATTACK_TARGET` (main world command) instead of `LVL_ATTACK_BUILDING` (AVA command), indicating the wrong prompt was being loaded.

**Files:** `src/main.py`

### 4. Verify template name

--l1-prompt ava 这个模板名称是不是不对?

> **Insight**
> The template name was correct, but the argument parser only supported `--l1-prompt=value` format, not the space-separated `--l1-prompt ava` format that was being used.

### 5. Remove remaining Chinese output

把日志里面的中文输出都去掉

**Files:** `src/ai/l1_leader.py`, `src/controller/loop.py`

### 6. Show generated L0 instructions

llm生成的l0指令是什么

> **Insight**
> After the fix, LLM correctly generates AVA battlefield commands:
> - `action: LVL_ATTACK_BUILDING` (not ATTACK_TARGET)
> - `building_key: 27` (building type)
> - `building_id: "27_1_1"` (unique ID format)

**Files:** None (query only)

### 7. Commit changes

commit
