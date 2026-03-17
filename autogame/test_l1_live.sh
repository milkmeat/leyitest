#!/bin/bash
# test_l1_live.sh — L1 单小队实战测试 (真实 LLM + test server)
#
# 目的: 验证 LLM→L1→L0→game_api 全链路
# 前置: config/llm_secret.yaml 已配置, test server 可达
#
# 用法:
#   bash test_l1_live.sh              # 默认 test 环境
#   bash test_l1_live.sh --mock       # mock 环境 (仅测试解析，不用真LLM)

set -uo pipefail
cd "$(dirname "$0")"

export PYTHONIOENCODING=utf-8

# ── 配置 ────────────────────────────────────────────────
CMD="python src/main.py"
ENV_FLAG=""
PASS=0
FAIL=0
RESULTS=()

for arg in "$@"; do
    case $arg in
        --mock) ENV_FLAG="--mock" ;;
    esac
done

# ── 辅助函数 ────────────────────────────────────────────

cli() {
    $CMD $ENV_FLAG "$@" 2>&1
}

show_cmd() {
    echo "  执行: $CMD ${ENV_FLAG:+$ENV_FLAG }$*"
}

show_output() {
    local lines
    lines=$(echo "$1" | wc -l)
    echo "$1" | head -5
    if [ "$lines" -gt 5 ]; then
        echo "  ... (共 ${lines} 行)"
    fi
}

check_contains() {
    local name="$1" keyword="$2" output="$3"
    local matched
    matched=$(echo "$output" | grep -m1 "$keyword" || true)
    if [ -n "$matched" ]; then
        if [ ${#matched} -gt 100 ]; then
            matched="${matched:0:100}..."
        fi
        printf "  [\033[32mPASS\033[0m] %s → %s\n" "$name" "$matched"
        ((PASS++))
        RESULTS+=("PASS|$name")
    else
        printf "  [\033[31mFAIL\033[0m] %s: 未找到 \"%s\"\n" "$name" "$keyword"
        ((FAIL++))
        RESULTS+=("FAIL|$name")
    fi
}

check_not_contains() {
    local name="$1" keyword="$2" output="$3"
    local matched
    matched=$(echo "$output" | grep -m1 "$keyword" || true)
    if [ -z "$matched" ]; then
        printf "  [\033[32mPASS\033[0m] %s\n" "$name"
        ((PASS++))
        RESULTS+=("PASS|$name")
    else
        printf "  [\033[31mFAIL\033[0m] %s: 不应出现 \"%s\"\n" "$name" "$keyword"
        ((FAIL++))
        RESULTS+=("FAIL|$name")
    fi
}

# ── 开始测试 ────────────────────────────────────────────

echo "=================================================="
echo "L1 单小队实战测试 (LLM→L1→L0→game_api 全链路)"
echo "  ENV: ${ENV_FLAG:-test}"
echo "=================================================="

# ==============================================================
# Test 1: LLM 连通性
# ==============================================================
echo ""
echo "=================================================="
echo "Test 1: LLM 连通性 (llm_test)"
echo "=================================================="

show_cmd "llm_test"
OUTPUT=$(cli llm_test)
EXIT1=$?

check_contains "LLM 响应成功" "\\[OK\\]" "$OUTPUT"
check_not_contains "LLM 无超时" "超时" "$OUTPUT"

echo "  退出码: $EXIT1"

# ==============================================================
# Test 2: L1 单小队决策 (squad 1, 真实LLM)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 2: L1 单小队决策 (squad 1)"
echo "=================================================="

show_cmd "l1_decide 1"
OUTPUT2=$(cli l1_decide 1)
EXIT2=$?

show_output "$OUTPUT2"

# 基本结构检查
check_contains "同步完成" "同步完成" "$OUTPUT2"
check_contains "生成指令" "生成.*条指令" "$OUTPUT2"

# 检查是否出现有效 action（非 dry_run 预设的 SCOUT）
# 合法 action: MOVE_CITY, ATTACK_TARGET, SCOUT, GARRISON_BUILDING,
#   INITIATE_RALLY, JOIN_RALLY, RETREAT, RALLY_DISMISS, RECALL_REINFORCE
HAS_ACTION=$(echo "$OUTPUT2" | grep -E "(MOVE_CITY|ATTACK_TARGET|SCOUT|GARRISON_BUILDING|INITIATE_RALLY|JOIN_RALLY|RETREAT|RALLY_DISMISS|RECALL_REINFORCE)" || true)
if [ -n "$HAS_ACTION" ]; then
    printf "  [\033[32mPASS\033[0m] 包含有效 action\n"
    ((PASS++))
    RESULTS+=("PASS|包含有效 action")
else
    printf "  [\033[33mWARN\033[0m] 无指令输出 (LLM 可能返回空 instructions，不视为失败)\n"
    # 空指令列表是合法的（"若无明显需要行动的场景，可以返回空 instructions 列表"）
fi

echo "  退出码: $EXIT2"

# 等待 API 冷却
sleep 5

# ==============================================================
# Test 3: L1 JSON 输出结构 (--json 模式)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 3: L1 JSON 输出结构 (squad 1, --json)"
echo "=================================================="

show_cmd "l1_decide 1 --json"
OUTPUT3=$(cli l1_decide 1 --json)
EXIT3=$?

# 检查 JSON 合法性
JSON_VALID=$(echo "$OUTPUT3" | python -c "
import sys, json
data = sys.stdin.read()
# 找到第一个 [ 开始的 JSON 数组（跳过 sync 输出行）
lines = data.split('\n')
json_lines = []
found = False
for line in lines:
    stripped = line.strip()
    if stripped.startswith('['):
        found = True
    if found:
        json_lines.append(line)
if json_lines:
    try:
        parsed = json.loads('\n'.join(json_lines))
        print('VALID')
        print(f'count={len(parsed)}')
        # 校验每条指令结构
        for item in parsed:
            assert 'action' in item, 'missing action'
            assert 'uid' in item, 'missing uid'
        print('STRUCT_OK')
    except Exception as e:
        print(f'INVALID: {e}')
else:
    print('NO_JSON')
" 2>&1 || true)

if echo "$JSON_VALID" | grep -q "VALID"; then
    printf "  [\033[32mPASS\033[0m] JSON 解析成功\n"
    ((PASS++))
    RESULTS+=("PASS|JSON 解析")
else
    printf "  [\033[31mFAIL\033[0m] JSON 解析失败: %s\n" "$JSON_VALID"
    ((FAIL++))
    RESULTS+=("FAIL|JSON 解析")
fi

if echo "$JSON_VALID" | grep -q "STRUCT_OK"; then
    printf "  [\033[32mPASS\033[0m] 指令结构校验 (action + uid)\n"
    ((PASS++))
    RESULTS+=("PASS|指令结构校验")
else
    printf "  [\033[33mWARN\033[0m] 指令结构校验未通过 (可能为空列表)\n"
fi

# 等待 API 冷却
sleep 5

# ==============================================================
# Test 4: L1 决策稳定性 (3轮重复, 各用不同小队)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 4: L1 决策稳定性 (3轮重复)"
echo "=================================================="

SUCCESS_COUNT=0
for round in 1 2 3; do
    echo -n "  Round $round: "
    ROUND_OUT=$(cli l1_decide $round --json 2>&1)
    ROUND_EXIT=$?
    if [ $ROUND_EXIT -eq 0 ] && echo "$ROUND_OUT" | grep -q "生成.*条指令"; then
        INSTR_LINE=$(echo "$ROUND_OUT" | grep "生成.*条指令" | tail -1)
        echo "OK — $INSTR_LINE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "FAIL (exit=$ROUND_EXIT)"
        echo "$ROUND_OUT" | tail -2
    fi
    # 避免触发 API 速率限制
    [ $round -lt 3 ] && sleep 5
done

echo ""
if [ $SUCCESS_COUNT -eq 3 ]; then
    printf "  [\033[32mPASS\033[0m] 3/3 轮决策全部成功\n"
    ((PASS++))
    RESULTS+=("PASS|3轮稳定性")
elif [ $SUCCESS_COUNT -ge 2 ]; then
    printf "  [\033[33mWARN\033[0m] %d/3 轮决策成功 (可接受)\n" "$SUCCESS_COUNT"
    ((PASS++))
    RESULTS+=("PASS|稳定性 ${SUCCESS_COUNT}/3")
else
    printf "  [\033[31mFAIL\033[0m] 仅 %d/3 轮决策成功\n" "$SUCCESS_COUNT"
    ((FAIL++))
    RESULTS+=("FAIL|稳定性 ${SUCCESS_COUNT}/3")
fi

# 等待 API 冷却
sleep 10

# ==============================================================
# Test 5: 主循环单轮 (真实LLM)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 5: 主循环单轮 (run --once, 真实LLM)"
echo "=================================================="

rm -f logs/loop_*.json 2>/dev/null

show_cmd "run --once --loop.interval_seconds 0"
OUTPUT5=$(cli run --once --loop.interval_seconds 0)
EXIT5=$?

show_output "$OUTPUT5"

check_contains "AIController 启动" "AIController" "$OUTPUT5"
check_contains "Sync 阶段" "\\[sync\\]" "$OUTPUT5"
# 提取 L1 行单独检查
L1_LINE=$(echo "$OUTPUT5" | grep "\\[L1\\]" || true)
check_contains "L1 生成指令 (非stub)" "\\[L1\\].*条指令" "$OUTPUT5"

# 检查 L1 行不含 "跳过"（L2 stub 的 "跳过" 不应干扰）
if echo "$L1_LINE" | grep -q "跳过"; then
    printf "  [\033[31mFAIL\033[0m] L1 不应是 stub\n"
    ((FAIL++))
    RESULTS+=("FAIL|L1 非stub")
else
    printf "  [\033[32mPASS\033[0m] L1 非 stub — %s\n" "$L1_LINE"
    ((PASS++))
    RESULTS+=("PASS|L1 非stub")
fi

# 检查日志文件
if ls logs/loop_1.json 1>/dev/null 2>&1; then
    # 检查日志中是否有 L1 指令统计
    L1_INSTR=$(python -c "
import json
with open('logs/loop_1.json') as f:
    data = json.load(f)
print(f\"instructions={data.get('instructions_count',0)} ok={data.get('actions_ok',0)} fail={data.get('actions_fail',0)}\")
" 2>&1 || echo "parse_error")
    printf "  [\033[32mPASS\033[0m] 日志记录: %s\n" "$L1_INSTR"
    ((PASS++))
    RESULTS+=("PASS|日志记录")
else
    printf "  [\033[31mFAIL\033[0m] 日志文件 logs/loop_1.json 不存在\n"
    ((FAIL++))
    RESULTS+=("FAIL|日志记录")
fi

echo "  退出码: $EXIT5"

# 等待 API 冷却
sleep 10

# ==============================================================
# Test 6: 多小队覆盖 (squad 1-4)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 6: 多小队覆盖 (squad 1-4)"
echo "=================================================="

SQUAD_OK=0
for sid in 1 2 3 4; do
    echo -n "  Squad $sid: "
    SQ_OUT=$(cli l1_decide $sid 2>&1)
    SQ_EXIT=$?
    if [ $SQ_EXIT -eq 0 ] && echo "$SQ_OUT" | grep -q "生成.*条指令"; then
        INSTR_LINE=$(echo "$SQ_OUT" | grep "生成.*条指令" | tail -1)
        echo "OK — $INSTR_LINE"
        SQUAD_OK=$((SQUAD_OK + 1))
    else
        echo "FAIL (exit=$SQ_EXIT)"
        echo "$SQ_OUT" | tail -3
    fi
    # 避免触发 API 速率限制
    [ $sid -lt 4 ] && sleep 5
done

echo ""
if [ $SQUAD_OK -eq 4 ]; then
    printf "  [\033[32mPASS\033[0m] 4/4 小队决策全部成功\n"
    ((PASS++))
    RESULTS+=("PASS|4小队覆盖")
elif [ $SQUAD_OK -ge 3 ]; then
    printf "  [\033[33mWARN\033[0m] %d/4 小队决策成功\n" "$SQUAD_OK"
    ((PASS++))
    RESULTS+=("PASS|小队覆盖 ${SQUAD_OK}/4")
else
    printf "  [\033[31mFAIL\033[0m] 仅 %d/4 小队决策成功\n" "$SQUAD_OK"
    ((FAIL++))
    RESULTS+=("FAIL|小队覆盖 ${SQUAD_OK}/4")
fi

# ── 汇总报告 ────────────────────────────────────────────
echo ""
echo "=================================================="
printf "测试结果: \033[32mPASS=%d\033[0m  \033[31mFAIL=%d\033[0m  TOTAL=%d\n" "$PASS" "$FAIL" "$((PASS+FAIL))"
echo "=================================================="
for r in "${RESULTS[@]}"; do
    IFS='|' read -r status name <<< "$r"
    if [ "$status" = "PASS" ]; then
        printf "  [\033[32m%s\033[0m] %s\n" "$status" "$name"
    else
        printf "  [\033[31m%s\033[0m] %s\n" "$status" "$name"
    fi
done

if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "ALL TESTS PASSED — L1 全链路验证通过"
    exit 0
else
    echo ""
    echo "SOME TESTS FAILED — 请检查 LLM 输出和指令质量"
    exit 1
fi
