# Prompt Record

- Date: 2026-03-14 12:59
- Branch: master
- Commit: auto-build march_info, same-cycle rally backfill, and remove LLM JSON mode for faster inference

---

### 1. Same-cycle rally_id extraction

队长生成的rally id可以在返回值中拿到，不需要等到下一次循环

**Files:** `src/executor/l0_executor.py`, `src/ai/prompts/l1_system.txt`

### 2. Remove JSON response mode to speed up LLM

返回不要使用json，是否可以加快响应？

**Files:** `src/ai/llm_client.py`

### 3. Investigate 30114 error source

什么指令返回 30114

### 4. Reference working test scripts for march_info

test_solo.sh和test_rally.sh里面有成功进攻的测试。参考其实现

**Files:** `src/executor/l0_executor.py`, `src/controller/loop.py`

### 5. Re-test rally flow

再测试一下
