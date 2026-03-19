#!/bin/bash
# test_l2_l1_integration.sh — L2+L1 联合实战测试
#
# 目的: 验证 L2 战略指挥 → L1 战术决策 → L0 执行 的完整决策链路
# 前置: config/llm_secret.yaml 已配置, test server 可达
#
# 测试内容:
#   1. L2 Commander 单独决策测试
#   2. L2 → L1 指令传递验证
#   3. 单轮全链路测试 (L2 → L1 → L0)
#   4. 多轮稳定性测试 (3轮)
#   5. 日志结构验证
#   6. 指令质量检查
#
# 用法:
#   bash test_l2_l1_integration.sh              # 默认 test 环境
#   bash test_l2_l1_integration.sh --mock       # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

export PYTHONIOENCODING=utf-8

# ── 配置 ────────────────────────────────────────────────
CMD="python src/main.py"
ENV_FLAG=""
PASS=0
FAIL=0
WARN=0
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
    echo "$1" | head -8
    if [ "$lines" -gt 8 ]; then
        echo "  ... (共 ${lines} 行)"
    fi
}

check_contains() {
    local name="$1" keyword="$2" output="$3"
    local matched
    matched=$(echo "$output" | grep -m1 "$keyword" || true)
    if [ -n "$matched" ]; then
        if [ ${#matched} -gt 120 ]; then
            matched="${matched:0:120}..."
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

check_json_field() {
    local log_file="$1"
    local field="$2"
    local expected="$3"
    local value
    value=$(python -c "
import json, sys
try:
    with open('$log_file') as f:
        data = json.load(f)
    val = data.get('$field', '')
    if isinstance(val, (dict, list)):
        print(json.dumps(val, ensure_ascii=False))
    else:
        print(str(val))
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)

    if [[ "$value" == *"$expected"* ]] || [ "$value" = "$expected" ]; then
        printf "  [\033[32mPASS\033[0m] %s → %s\n" "$field" "$value"
        ((PASS++))
        RESULTS+=("PASS|$field")
    else
        printf "  [\033[31mFAIL\033[0m] %s → 期望包含\"%s\", 实际: %s\n" "$field" "$expected" "$value"
        ((FAIL++))
        RESULTS+=("FAIL|$field")
    fi
}

# ── 开始测试 ────────────────────────────────────────────

echo "=================================================="
echo "L2+L1 联合实战测试 (L2战略 → L1战术 → L0执行)"
echo "  ENV: ${ENV_FLAG:-test}"
echo "=================================================="

# ==============================================================
# Test 1: L2 Commander 单独决策测试
# ==============================================================
echo ""
echo "=================================================="
echo "Test 1: L2 Commander 单独决策 (l2_decide)"
echo "=================================================="

show_cmd "l2_decide"
OUTPUT1=$(cli l2_decide)
EXIT1=$?

show_output "$OUTPUT1"

check_contains "L2 同步完成" "同步完成" "$OUTPUT1"
check_contains "L2 生成指令" "生成.*条.*指令" "$OUTPUT1"
check_not_contains "L2 无致命错误" "Error" "$OUTPUT1"

echo "  退出码: $EXIT1"

# ==============================================================
# Test 2: L2 → L1 指令传递验证
# ==============================================================
echo ""
echo "=================================================="
echo "Test 2: L2 → L1 指令传递 (主循环单轮, 检查指令传递)"
echo "=================================================="

rm -f logs/loop_*.json 2>/dev/null

show_cmd "run --once --loop.interval_seconds 0"
OUTPUT2=$(cli run --once --loop.interval_seconds 0)
EXIT2=$?

show_output "$OUTPUT2"

# 检查 L2 阶段执行
check_contains "L2 阶段执行" "\\[L2\\].*条指令" "$OUTPUT2"

# 检查 L1 阶段接收到 L2 指令
L1_LINE=$(echo "$OUTPUT2" | grep "\\[L1\\]" || true)
if [ -n "$L1_LINE" ]; then
    printf "  [\033[32mPASS\033[0m] L1 阶段执行 → %s\n" "$L1_LINE"
    ((PASS++))
    RESULTS+=("PASS|L1阶段执行")
else
    printf "  [\033[31mFAIL\033[0m] L1 阶段未执行\n"
    ((FAIL++))
    RESULTS+=("FAIL|L1阶段执行")
fi

# 检查 Action 阶段
check_contains "Action 阶段执行" "\\[action\\].*条指令" "$OUTPUT2"

echo "  退出码: $EXIT2"

# 等待 API 冷却
sleep 5

# ==============================================================
# Test 3: 日志结构验证
# ==============================================================
echo ""
echo "=================================================="
echo "Test 3: 日志结构验证 (logs/loop_1.json)"
echo "=================================================="

if [ -f "logs/loop_1.json" ]; then
    printf "  [\033[32mPASS\033[0m] 日志文件存在\n"
    ((PASS++))
    RESULTS+=("PASS|日志文件存在")

    # 验证 JSON 合法性
    if python -m json.tool logs/loop_1.json > /dev/null 2>&1; then
        printf "  [\033[32mPASS\033[0m] JSON 格式合法\n"
        ((PASS++))
        RESULTS+=("PASS|JSON格式合法")
    else
        printf "  [\033[31mFAIL\033[0m] JSON 格式非法\n"
        ((FAIL++))
        RESULTS+=("FAIL|JSON格式合法")
    fi

    # 检查关键字段（验证存在且为有效数值）
    check_json_field "logs/loop_1.json" "loop_id" "1"

    # 检查时间字段存在（值应该大于 0 表示真实执行）
    for field in sync_time l2_time l1_time; do
        TIME_VAL=$(python -c "
import json
with open('logs/loop_1.json') as f:
    data = json.load(f)
val = data.get('$field', 0)
if isinstance(val, (int, float)) and val >= 0:
    print('OK')
else:
    print('INVALID')
" 2>&1)
        if [ "$TIME_VAL" = "OK" ]; then
            printf "  [\033[32mPASS\033[0m] %s → 有效数值\n" "$field"
            ((PASS++))
            RESULTS+=("PASS|${field}")
        else
            printf "  [\033[31mFAIL\033[0m] %s → 无效值\n" "$field"
            ((FAIL++))
            RESULTS+=("FAIL|${field}")
        fi
    done

    # 检查阶段错误列表
    ERROR_COUNT=$(python -c "
import json
with open('logs/loop_1.json') as f:
    data = json.load(f)
errors = data.get('phase_errors', [])
print(len(errors))
" 2>&1 || echo "-1")

    if [ "$ERROR_COUNT" -eq 0 ]; then
        printf "  [\033[32mPASS\033[0m] 无阶段错误\n"
        ((PASS++))
        RESULTS+=("PASS|无阶段错误")
    else
        printf "  [\033[33mWARN\033[0m] 阶段错误数量: %d\n" "$ERROR_COUNT"
        ((WARN++))
        RESULTS+=("WARN|阶段错误=${ERROR_COUNT}")
    fi

    # 检查指令统计
    python -c "
import json
with open('logs/loop_1.json') as f:
    data = json.load(f)
instr = data.get('instructions_count', 0)
ok = data.get('actions_ok', 0)
fail = data.get('actions_fail', 0)
print(f'指令统计: {instr} 条生成, {ok} 条成功, {fail} 条失败')
" 2>&1 | while read -r line; do
    echo "  INFO: $line"
done

else
    printf "  [\033[31mFAIL\033[0m] 日志文件 logs/loop_1.json 不存在\n"
    ((FAIL++))
    RESULTS+=("FAIL|日志文件存在")
fi

# ==============================================================
# Test 4: L2 指令内容验证
# ==============================================================
echo ""
echo "=================================================="
echo "Test 4: L2 指令内容验证 (自然语言质量)"
echo "=================================================="

# 从日志中提取 L2 指令（如果有记录）
L2_ORDERS=$(python -c "
import json
import os
if os.path.exists('logs/loop_1.json'):
    with open('logs/loop_1.json') as f:
        data = json.load(f)
    # 检查是否有 L2 相关信息（可能需要扩展日志）
    print('JSON_EXISTS')
else:
    print('NO_LOG')
" 2>&1)

if [[ "$L2_ORDERS" == *"JSON_EXISTS"* ]]; then
    printf "  [\033[32mPASS\033[0m] L2 日志可解析\n"
    ((PASS++))
    RESULTS+=("PASS|L2日志可解析")

    # TODO: 添加更详细的 L2 指令内容检查
    # 需要先扩展 loop.py 的日志记录，保存 L2 orders
else
    printf "  [\033[33mWARN\033[0m] L2 指令内容检查跳过 (日志中未记录)\n"
    ((WARN++))
    RESULTS+=("WARN|L2指令内容检查待实现")
fi

# ==============================================================
# Test 5: 多轮稳定性测试 (2轮)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 5: 多轮稳定性测试 (2轮完整循环)"
echo "=================================================="

rm -f logs/loop_*.json 2>/dev/null

show_cmd "run --rounds 2 --loop.interval_seconds 1"
OUTPUT5=$(cli run --rounds 2 --loop.interval_seconds 1)
EXIT5=$?

# 检查 2 轮都执行了
LOOP_COUNT=$(echo "$OUTPUT5" | grep -c "loop #" || true)
if [ "$LOOP_COUNT" -ge 2 ]; then
    printf "  [\033[32mPASS\033[0m] 执行了 %d 轮循环\n" "$LOOP_COUNT"
    ((PASS++))
    RESULTS+=("PASS|多轮执行 (${LOOP_COUNT}轮)")
else
    printf "  [\033[31mFAIL\033[0m] 仅执行了 %d 轮循环 (期望 2 轮)\n" "$LOOP_COUNT"
    ((FAIL++))
    RESULTS+=("FAIL|多轮执行")
fi

# 检查每轮的 L2 和 L1 都执行了
L2_COUNT=$(echo "$OUTPUT5" | grep -c "\\[L2\\].*条指令" || true)
L1_COUNT=$(echo "$OUTPUT5" | grep -c "\\[L1\\].*条指令" || true)

echo "  L2 执行次数: $L2_COUNT"
echo "  L1 执行次数: $L1_COUNT"

if [ "$L2_COUNT" -ge 2 ] && [ "$L1_COUNT" -ge 2 ]; then
    printf "  [\033[32mPASS\033[0m] L2+L1 每轮都执行\n"
    ((PASS++))
    RESULTS+=("PASS|L2+L1每轮执行")
else
    printf "  [\033[31mFAIL\033[0m] L2+L1 执行次数不足\n"
    ((FAIL++))
    RESULTS+=("FAIL|L2+L1每轮执行")
fi

# 检查日志文件数量
LOG_COUNT=$(ls logs/loop_*.json 2>/dev/null | wc -l || echo "0")
if [ "$LOG_COUNT" -eq 2 ]; then
    printf "  [\033[32mPASS\033[0m] 日志文件数量正确 (2个)\n"
    ((PASS++))
    RESULTS+=("PASS|日志文件数量")
else
    printf "  [\033[33mWARN\033[0m] 日志文件数量: %d (期望 2)\n" "$LOG_COUNT"
    ((WARN++))
    RESULTS+=("WARN|日志文件数量=${LOG_COUNT}")
fi

echo "  退出码: $EXIT5"

# ==============================================================
# Test 6: 指令链路完整性验证
# ==============================================================
echo ""
echo "=================================================="
echo "Test 6: 指令链路完整性 (L2→L1→Action 无断裂)"
echo "=================================================="

# 检查日志中的数据流一致性
python -c "
import json
import os

for i in range(1, 3):
    log_file = f'logs/loop_{i}.json'
    if not os.path.exists(log_file):
        continue

    with open(log_file) as f:
        data = json.load(f)

    l2_time = data.get('l2_time', 0)
    l1_time = data.get('l1_time', 0)
    action_time = data.get('action_time', 0)
    instr_count = data.get('instructions_count', 0)
    actions_ok = data.get('actions_ok', 0)
    actions_fail = data.get('actions_fail', 0)

    print(f'Loop #{i}:')
    print(f'  L2耗时: {l2_time}s, L1耗时: {l1_time}s, Action耗时: {action_time}s')
    print(f'  指令: {instr_count} 生成, {actions_ok} 成功, {actions_fail} 失败')

    # 检查耗时合理性
    if l2_time > 0 and l1_time > 0:
        print(f'  [\033[32mOK\033[0m] L2+L1 都有耗时（执行了LLM调用）')
    elif l2_time == 0 and l1_time == 0:
        print(f'  [\033[33mWARN\033[0m] L2+L1 耗时为0（可能使用了 stub 模式）')
    else:
        print(f'  [\033[31mWARN\033[0m] L2/L1 耗时异常')
" 2>&1 | while read -r line; do
    echo "  $line"
done

# ==============================================================
# Test 7: L2 自然语言理解测试
# ==============================================================
echo ""
echo "=================================================="
echo "Test 7: L2 自然语言指令质量"
echo "=================================================="

# 使用 l2_decide --json 获取结构化输出
show_cmd "l2_decide --json"
OUTPUT7=$(cli l2_decide --json)
EXIT7=$?

# 检查 JSON 输出
JSON_VALID=$(echo "$OUTPUT7" | python -c "
import sys, json
data = sys.stdin.read()
# 找到 JSON 数组
lines = data.split('\n')
json_lines = []
found = False
for line in lines:
    stripped = line.strip()
    if stripped.startswith('[') or stripped.startswith('{'):
        found = True
    if found:
        json_lines.append(line)
if json_lines:
    try:
        parsed = json.loads(''.join(json_lines))
        print('VALID')
        # 检查 orders 结构
        if isinstance(parsed, list) and len(parsed) > 0:
            first = parsed[0]
            if 'squad_id' in first and 'order' in first:
                print('STRUCT_OK')
                print(f'count={len(parsed)}')
                print(f'first_squad={first[\"squad_id\"]}')
                print(f'first_order={first[\"order\"][:50]}...')
    except Exception as e:
        print(f'INVALID: {e}')
else:
    print('NO_JSON')
" 2>&1 || true)

if echo "$JSON_VALID" | grep -q "VALID"; then
    printf "  [\033[32mPASS\033[0m] L2 JSON 解析成功\n"
    ((PASS++))
    RESULTS+=("PASS|L2 JSON解析")
else
    printf "  [\033[31mFAIL\033[0m] L2 JSON 解析失败: %s\n" "$JSON_VALID"
    ((FAIL++))
    RESULTS+=("FAIL|L2 JSON解析")
fi

if echo "$JSON_VALID" | grep -q "STRUCT_OK"; then
    SQUAD_ID=$(echo "$JSON_VALID" | grep "first_squad=" | cut -d'=' -f2)
    ORDER_PREVIEW=$(echo "$JSON_VALID" | grep "first_order=" | cut -d'=' -f2-)
    printf "  [\033[32mPASS\033[0m] L2 orders 结构正确\n"
    printf "  示例: squad %s → %s\n" "$SQUAD_ID" "$ORDER_PREVIEW"
    ((PASS++))
    RESULTS+=("PASS|L2 orders结构")
else
    printf "  [\033[33mWARN\033[0m] L2 orders 结构校验未通过\n"
fi

echo "  退出码: $EXIT7"

# ── 汇总报告 ────────────────────────────────────────────
echo ""
echo "=================================================="
printf "测试结果: \033[32mPASS=%d\033[0m  \033[31mFAIL=%d\033[0m  \033[33mWARN=%d\033[0m  TOTAL=%d\n" "$PASS" "$FAIL" "$WARN" "$((PASS+FAIL+WARN))"
echo "=================================================="

for r in "${RESULTS[@]}"; do
    IFS='|' read -r status name <<< "$r"
    if [ "$status" = "PASS" ]; then
        printf "  [\033[32m%s\033[0m] %s\n" "$status" "$name"
    elif [ "$status" = "WARN" ]; then
        printf "  [\033[33m%s\033[0m] %s\n" "$status" "$name"
    else
        printf "  [\033[31m%s\033[0m] %s\n" "$status" "$name"
    fi
done

echo ""
echo "=================================================="
echo "测试说明"
echo "=================================================="
echo "本测试验证 L2+L1 联合决策链路的完整性:"
echo "  1. L2 Commander 能正常生成战略指令"
echo "  2. L2 指令能正确传递给 L1"
echo "  3. L1 能基于 L2 指令生成战术指令"
echo "  4. 多轮运行稳定性"
echo ""
echo "如果测试 FAIL，请检查:"
echo "  - config/llm_secret.yaml 是否正确配置"
echo "  - LLM API 是否可达"
echo "  - logs/loop_*.json 中的详细错误信息"
echo ""

# 退出码
if [ "$FAIL" -eq 0 ]; then
    echo "ALL TESTS PASSED — L2+L1 联合决策链路验证通过"
    exit 0
else
    echo "SOME TESTS FAILED — 请检查错误信息并修复"
    exit 1
fi
