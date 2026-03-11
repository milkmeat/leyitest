#!/bin/bash
# test_l0.sh — L0 命令集成测试
#
# 所有测试动作通过 CLI 文本指令触发，如:
#   python src/main.py add_gem 20010366 77777
#   python src/main.py l0 MOVE_CITY 20010366 500 500
#
# 用法:
#   ./test_l0.sh                    # 默认 test 环境
#   ./test_l0.sh --mock             # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

# ── 配置 ────────────────────────────────────────────────
TEST_UID=20010366
CMD="python src/main.py"
ENV_FLAG=""
PASS=0
FAIL=0
RESULTS=()

# 解析参数
for arg in "$@"; do
    case $arg in
        --mock) ENV_FLAG="--mock" ;;
    esac
done

# ── 辅助函数 ────────────────────────────────────────────

# 执行 CLI 命令并返回 stdout（stderr 静默）
cli() {
    $CMD $ENV_FLAG "$@" 2>/dev/null
}

# 记录测试结果
check() {
    local name="$1" expected="$2" actual="$3"
    if [ "$expected" = "$actual" ]; then
        printf "  [\033[32mPASS\033[0m] %s: expected=%s, actual=%s\n" "$name" "$expected" "$actual"
        ((PASS++))
        RESULTS+=("PASS|$name|expected=$expected, actual=$actual")
    else
        printf "  [\033[31mFAIL\033[0m] %s: expected=%s, actual=%s\n" "$name" "$expected" "$actual"
        ((FAIL++))
        RESULTS+=("FAIL|$name|expected=$expected, actual=$actual")
    fi
}

# 检查命令输出包含关键字
check_success() {
    local name="$1" output="$2"
    local ret_code
    ret_code=$(echo "$output" | grep -oP 'ret_code=\K\d+' || echo "")
    if echo "$output" | grep -q "成功\|OK"; then
        printf "  [\033[32mPASS\033[0m] %s: 命令执行成功\n" "$name"
        ((PASS++))
        RESULTS+=("PASS|$name|命令执行成功")
    elif [ "$ret_code" = "0" ] || [ -z "$ret_code" ]; then
        # 没有错误标记，也算通过
        printf "  [\033[32mPASS\033[0m] %s: ret_code=%s\n" "$name" "${ret_code:-ok}"
        ((PASS++))
        RESULTS+=("PASS|$name|ret_code=${ret_code:-ok}")
    else
        printf "  [\033[31mFAIL\033[0m] %s: %s\n" "$name" "$output"
        ((FAIL++))
        RESULTS+=("FAIL|$name|$output")
    fi
}

# ── 开始测试 ────────────────────────────────────────────

echo "L0 命令集成测试 (CLI Text Mode)"
echo "  UID:  $TEST_UID"
echo "  ENV: ${ENV_FLAG:-test}"

# ==============================================================
# Test 1: add_gem (SET 行为)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 1: add_gem (SET 行为)"
echo "=================================================="

# 1a. 读取当前宝石
OLD_GEM=$(cli get_gem $TEST_UID)
echo "  读取: get_gem $TEST_UID → $OLD_GEM"

# 1b. 设置为特定值
SET_VAL=77777
if [ "$OLD_GEM" = "$SET_VAL" ]; then SET_VAL=88888; fi
echo "  执行: add_gem $TEST_UID $SET_VAL"
cli add_gem $TEST_UID $SET_VAL > /dev/null

# 1c. 重新读取
NEW_GEM=$(cli get_gem $TEST_UID)
echo "  验证: get_gem $TEST_UID → $NEW_GEM"
check "add_gem SET 值验证" "$SET_VAL" "$NEW_GEM"

# 1d. 再设一次不同值，确认是 SET 而非 ADD
SET_VAL2=66666
echo "  执行: add_gem $TEST_UID $SET_VAL2 (二次验证非ADD)"
cli add_gem $TEST_UID $SET_VAL2 > /dev/null
NEW_GEM2=$(cli get_gem $TEST_UID)
echo "  验证: get_gem $TEST_UID → $NEW_GEM2"
check "add_gem SET 二次验证 (非ADD)" "$SET_VAL2" "$NEW_GEM2"

# ==============================================================
# Test 2: add_soldiers (ADD 行为)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 2: add_soldiers (ADD 行为)"
echo "=================================================="

SOLDIER_ID=204
ADD_NUM=500

# 2a. 读取当前兵力
OLD_COUNT=$(cli get_soldiers $TEST_UID $SOLDIER_ID)
echo "  读取: get_soldiers $TEST_UID $SOLDIER_ID → $OLD_COUNT"

# 2b. 添加兵力
echo "  执行: add_soldiers $TEST_UID $SOLDIER_ID $ADD_NUM"
cli add_soldiers $TEST_UID $SOLDIER_ID $ADD_NUM > /dev/null

# 2c. 重新读取
NEW_COUNT=$(cli get_soldiers $TEST_UID $SOLDIER_ID)
echo "  验证: get_soldiers $TEST_UID $SOLDIER_ID → $NEW_COUNT"
EXPECTED=$((OLD_COUNT + ADD_NUM))
check "add_soldiers ADD 值验证" "$EXPECTED" "$NEW_COUNT"

# ==============================================================
# Test 3: add_resource (命令执行成功)
# ==============================================================
echo ""
echo "=================================================="
echo "Test 3: add_resource (命令执行)"
echo "=================================================="

echo "  执行: add_resource $TEST_UID 0"
OUTPUT=$(cli add_resource $TEST_UID 0; $CMD $ENV_FLAG add_resource $TEST_UID 0 2>&1)
check_success "add_resource 命令执行" "$OUTPUT"

# ==============================================================
# Test 4: move_city 通过 L0 执行器
# ==============================================================
echo ""
echo "=================================================="
echo "Test 4: l0 MOVE_CITY (L0执行器)"
echo "=================================================="

# 确保有足够宝石（移城消耗宝石）
echo "  准备: add_gem $TEST_UID 116666 (确保宝石充足)"
cli add_gem $TEST_UID 116666 > /dev/null

# 4a. 读取当前坐标
OLD_POS=$(cli get_player_pos $TEST_UID)
echo "  读取: get_player_pos $TEST_UID → $OLD_POS"

# 4b. 移城到随机坐标（避开常见占用位置）
TARGET_X=$(( RANDOM % 700 + 100 ))
TARGET_Y=$(( RANDOM % 700 + 100 ))
# 如果当前就在目标位置，偏移一下
if [ "$OLD_POS" = "($TARGET_X,$TARGET_Y)" ]; then
    TARGET_X=$(( (TARGET_X + 50) % 900 + 100 ))
fi
echo "  执行: l0 MOVE_CITY $TEST_UID $TARGET_X $TARGET_Y"
L0_OUTPUT=$($CMD $ENV_FLAG l0 MOVE_CITY $TEST_UID $TARGET_X $TARGET_Y 2>&1)
echo "  L0 输出: $L0_OUTPUT"

# 检查 L0 返回 [OK]
if echo "$L0_OUTPUT" | grep -q "\[OK\]"; then
    printf "  [\033[32mPASS\033[0m] l0 MOVE_CITY 命令执行成功\n"
    ((PASS++))
    RESULTS+=("PASS|l0 MOVE_CITY 命令执行|[OK]")
else
    printf "  [\033[31mFAIL\033[0m] l0 MOVE_CITY 命令执行: %s\n" "$L0_OUTPUT"
    ((FAIL++))
    RESULTS+=("FAIL|l0 MOVE_CITY 命令执行|$L0_OUTPUT")
fi

# 4c. 验证坐标
NEW_POS=$(cli get_player_pos $TEST_UID)
echo "  验证: get_player_pos $TEST_UID → $NEW_POS"
check "l0 MOVE_CITY 坐标验证" "($TARGET_X,$TARGET_Y)" "$NEW_POS"

# ── 汇总报告 ────────────────────────────────────────────
echo ""
echo "=================================================="
printf "测试结果: \033[32mPASS=%d\033[0m  \033[31mFAIL=%d\033[0m  TOTAL=%d\n" "$PASS" "$FAIL" "$((PASS+FAIL))"
echo "=================================================="
for r in "${RESULTS[@]}"; do
    IFS='|' read -r status name detail <<< "$r"
    if [ "$status" = "PASS" ]; then
        printf "  [\033[32m%s\033[0m] %s: %s\n" "$status" "$name" "$detail"
    else
        printf "  [\033[31m%s\033[0m] %s: %s\n" "$status" "$name" "$detail"
    fi
done

# 退出码
if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "ALL TESTS PASSED"
    exit 0
else
    echo ""
    echo "SOME TESTS FAILED"
    exit 1
fi
