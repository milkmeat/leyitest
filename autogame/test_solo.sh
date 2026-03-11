#!/bin/bash
# test_solo.sh — Solo Attack 集成测试 (A 攻击 B)
#
# 所有测试动作通过 CLI 文本指令触发，如:
#   python src/main.py add_gem 20010366 77777
#   python src/main.py attack_player 20010366 20010373 500 500
#
# 用法:
#   ./test_solo.sh                    # 默认 test 环境
#   ./test_solo.sh --mock             # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

# ── 配置 ────────────────────────────────────────────────
UID_A=20010366
UID_B=20010373
CMD="python src/main.py"
ENV_FLAG=""
IS_MOCK=false
PASS=0
FAIL=0
SKIP=0
RESULTS=()
SOLDIER_ID=204   # 使用 archer 类型进行验证

# 解析参数
for arg in "$@"; do
    case $arg in
        --mock) ENV_FLAG="--mock"; IS_MOCK=true ;;
    esac
done

# ── 辅助函数 ────────────────────────────────────────────

# 执行 CLI 命令并返回 stdout（stderr 静默）
cli() {
    $CMD $ENV_FLAG "$@" 2>/dev/null
}

# 执行 CLI 命令并返回 stdout + stderr
cli_verbose() {
    $CMD $ENV_FLAG "$@" 2>&1
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

# 检查数值小于预期
check_less_than() {
    local name="$1" before="$2" after="$3"
    if [ "$after" -lt "$before" ]; then
        printf "  [\033[32mPASS\033[0m] %s: before=%s, after=%s (减少了 %d)\n" "$name" "$before" "$after" "$((before - after))"
        ((PASS++))
        RESULTS+=("PASS|$name|before=$before, after=$after, decreased=$((before - after))")
    else
        printf "  [\033[31mFAIL\033[0m] %s: before=%s, after=%s (未减少)\n" "$name" "$before" "$after"
        ((FAIL++))
        RESULTS+=("FAIL|$name|before=$before, after=$after (未减少)")
    fi
}

# 检查命令输出包含成功标志
check_success() {
    local name="$1" output="$2"
    local ret_code
    ret_code=$(echo "$output" | grep -oP 'ret_code=\K\d+' || echo "")
    if echo "$output" | grep -q "成功\|OK\|已出发\|侦察"; then
        printf "  [\033[32mPASS\033[0m] %s: 命令执行成功\n" "$name"
        ((PASS++))
        RESULTS+=("PASS|$name|命令执行成功")
    elif [ "$ret_code" = "0" ] || [ -z "$ret_code" ]; then
        printf "  [\033[32mPASS\033[0m] %s: ret_code=%s\n" "$name" "${ret_code:-ok}"
        ((PASS++))
        RESULTS+=("PASS|$name|ret_code=${ret_code:-ok}")
    else
        printf "  [\033[31mFAIL\033[0m] %s: %s\n" "$name" "$output"
        ((FAIL++))
        RESULTS+=("FAIL|$name|$output")
    fi
}

# 跳过测试（mock 环境不支持的功能）
skip_test() {
    local name="$1" reason="$2"
    printf "  [\033[33mSKIP\033[0m] %s: %s\n" "$name" "$reason"
    ((SKIP++))
    RESULTS+=("SKIP|$name|$reason")
}

# 生成随机数 [min, max]
rand_range() {
    local min=$1 max=$2
    echo $(( RANDOM % (max - min + 1) + min ))
}

# ── 开始测试 ────────────────────────────────────────────

echo "Solo Attack 集成测试 (A→B)"
echo "  A:   $UID_A"
echo "  B:   $UID_B"
echo "  ENV: ${ENV_FLAG:-test}"
echo ""

# ==============================================================
# Step 1: 给 A, B 都加上足够的宝石
# ==============================================================
echo "=================================================="
echo "Step 1: 添加宝石 (确保移城可用)"
echo "=================================================="

GEM_AMOUNT=200000
echo "  执行: add_gem $UID_A $GEM_AMOUNT"
cli add_gem $UID_A $GEM_AMOUNT > /dev/null
echo "  执行: add_gem $UID_B $GEM_AMOUNT"
cli add_gem $UID_B $GEM_AMOUNT > /dev/null

# 验证宝石设置成功
GEM_A=$(cli get_gem $UID_A)
GEM_B=$(cli get_gem $UID_B)
echo "  A 宝石: $GEM_A"
echo "  B 宝石: $GEM_B"
check "A 宝石设置" "$GEM_AMOUNT" "$GEM_A"
check "B 宝石设置" "$GEM_AMOUNT" "$GEM_B"

# ==============================================================
# Step 2: 给 A, B 添加随机数量士兵，记录初始数量
# ==============================================================
echo ""
echo "=================================================="
echo "Step 2: 添加随机士兵并记录初始数量"
echo "=================================================="

ADD_A=$(rand_range 1000 5000)
ADD_B=$(rand_range 1000 5000)

# 读取当前士兵数量
OLD_A=$(cli get_soldiers $UID_A $SOLDIER_ID)
OLD_B=$(cli get_soldiers $UID_B $SOLDIER_ID)
echo "  A 当前士兵(id=$SOLDIER_ID): $OLD_A"
echo "  B 当前士兵(id=$SOLDIER_ID): $OLD_B"

# 添加士兵 (ADD 行为)
echo "  执行: add_soldiers $UID_A $SOLDIER_ID $ADD_A"
cli add_soldiers $UID_A $SOLDIER_ID $ADD_A > /dev/null
echo "  执行: add_soldiers $UID_B $SOLDIER_ID $ADD_B"
cli add_soldiers $UID_B $SOLDIER_ID $ADD_B > /dev/null

# 验证士兵添加成功
NEW_A=$(cli get_soldiers $UID_A $SOLDIER_ID)
NEW_B=$(cli get_soldiers $UID_B $SOLDIER_ID)
EXPECTED_A=$((OLD_A + ADD_A))
EXPECTED_B=$((OLD_B + ADD_B))
echo "  A 士兵(添加后): $NEW_A (期望=$EXPECTED_A)"
echo "  B 士兵(添加后): $NEW_B (期望=$EXPECTED_B)"
check "A 士兵添加" "$EXPECTED_A" "$NEW_A"
check "B 士兵添加" "$EXPECTED_B" "$NEW_B"

# 记录攻击前的士兵数量
PRE_ATTACK_A=$NEW_A
PRE_ATTACK_B=$NEW_B

# ==============================================================
# Step 3: B 移城到随机位置
# ==============================================================
echo ""
echo "=================================================="
echo "Step 3: B 移城到随机位置"
echo "=================================================="

# 重试移城（目标坐标可能被占用）
B_MOVE_OK=false
B_TARGET_X=0
B_TARGET_Y=0
for attempt in 1 2 3 4 5; do
    B_TARGET_X=$(rand_range 100 700)
    B_TARGET_Y=$(rand_range 100 700)
    echo "  尝试 #$attempt: l0 MOVE_CITY $UID_B $B_TARGET_X $B_TARGET_Y"
    B_MOVE_OUTPUT=$(cli_verbose l0 MOVE_CITY $UID_B $B_TARGET_X $B_TARGET_Y)
    if echo "$B_MOVE_OUTPUT" | grep -q "\[OK\]"; then
        B_MOVE_OK=true
        echo "  成功!"
        break
    fi
    echo "  失败 (坐标可能被占用)，重试..."
done

if $B_MOVE_OK; then
    printf "  [\033[32mPASS\033[0m] B 移城命令执行成功\n"
    ((PASS++))
    RESULTS+=("PASS|B 移城命令执行|[OK] → ($B_TARGET_X,$B_TARGET_Y)")
else
    printf "  [\033[31mFAIL\033[0m] B 移城命令执行: 多次尝试均失败\n"
    ((FAIL++))
    RESULTS+=("FAIL|B 移城命令执行|多次尝试均失败")
fi

# 读取 B 的实际坐标（后续操作均使用实际坐标）
B_POS=$(cli get_player_pos $UID_B)
B_ACTUAL_X=$(echo "$B_POS" | grep -oP '^\(\K\d+')
B_ACTUAL_Y=$(echo "$B_POS" | grep -oP ',\K\d+(?=\))')
echo "  B 实际坐标: $B_POS"
check "B 移城坐标验证" "($B_TARGET_X,$B_TARGET_Y)" "$B_POS"

# ==============================================================
# Step 4: 打印 B 的位置，等待 1 分钟
# ==============================================================
echo ""
echo "=================================================="
echo "Step 4: 等待观察"
echo "=================================================="
echo "  B 当前位置: ($B_ACTUAL_X,$B_ACTUAL_Y)"
echo "  请在模拟器上确认 B 已移城到 ($B_ACTUAL_X,$B_ACTUAL_Y)"
if $IS_MOCK; then
    echo "  (Mock 模式: 跳过等待)"
else
    echo "  等待 60 秒..."
    sleep 60
fi

# ==============================================================
# Step 5: A 移城到 B 旁边
# ==============================================================
echo ""
echo "=================================================="
echo "Step 5: A 移城到 B 旁边"
echo "=================================================="

# 尝试多个偏移位置（主城有宽度，相邻格可能被占用）
OFFSETS=(3 -3 5 -5 7 -7 4 -4 6 -6)
A_MOVE_OK=false
A_TARGET_X=0
A_TARGET_Y=0

echo "  B 实际位置: ($B_ACTUAL_X,$B_ACTUAL_Y)"
for offset in "${OFFSETS[@]}"; do
    A_TARGET_X=$((B_ACTUAL_X + offset))
    A_TARGET_Y=$B_ACTUAL_Y
    echo "  尝试: l0 MOVE_CITY $UID_A $A_TARGET_X $A_TARGET_Y (偏移=$offset)"
    A_MOVE_OUTPUT=$(cli_verbose l0 MOVE_CITY $UID_A $A_TARGET_X $A_TARGET_Y)
    if echo "$A_MOVE_OUTPUT" | grep -q "\[OK\]"; then
        A_MOVE_OK=true
        echo "  成功!"
        break
    fi
    echo "  失败 (可能被占用)，尝试下一个偏移..."
done

if $A_MOVE_OK; then
    printf "  [\033[32mPASS\033[0m] A 移城命令执行成功\n"
    ((PASS++))
    RESULTS+=("PASS|A 移城命令执行|[OK] → ($A_TARGET_X,$A_TARGET_Y)")
else
    printf "  [\033[31mFAIL\033[0m] A 移城命令执行: 所有偏移位置均被占用\n"
    ((FAIL++))
    RESULTS+=("FAIL|A 移城命令执行|所有偏移位置均被占用")
fi

# 验证 A 的坐标
A_POS=$(cli get_player_pos $UID_A)
echo "  A 实际坐标: $A_POS"
check "A 移城坐标验证" "($A_TARGET_X,$A_TARGET_Y)" "$A_POS"

# ==============================================================
# Step 6: A 对 B 发起侦察 (fire and forget)
# ==============================================================
echo ""
echo "=================================================="
echo "Step 6: A 侦察 B"
echo "=================================================="

echo "  执行: scout_player $UID_A $UID_B $B_ACTUAL_X $B_ACTUAL_Y"
SCOUT_OUTPUT=$(cli_verbose scout_player $UID_A $UID_B $B_ACTUAL_X $B_ACTUAL_Y)
echo "  输出: $(echo "$SCOUT_OUTPUT" | head -3)"
check_success "A 侦察 B 命令执行" "$SCOUT_OUTPUT"

# ==============================================================
# Step 7: A 对 B 发起攻击
# ==============================================================
echo ""
echo "=================================================="
echo "Step 7: A 攻击 B"
echo "=================================================="

ATTACK_COUNT=5000
echo "  执行: attack_player $UID_A $UID_B $B_ACTUAL_X $B_ACTUAL_Y $SOLDIER_ID $ATTACK_COUNT"
ATTACK_OUTPUT=$(cli_verbose attack_player $UID_A $UID_B $B_ACTUAL_X $B_ACTUAL_Y $SOLDIER_ID $ATTACK_COUNT)
echo "  输出: $(echo "$ATTACK_OUTPUT" | head -3)"
check_success "A 攻击 B 命令执行" "$ATTACK_OUTPUT"

# ==============================================================
# Step 8: 等待 1 分钟 (战斗结算)
# ==============================================================
echo ""
echo "=================================================="
echo "Step 8: 等待战斗结算"
echo "=================================================="
if $IS_MOCK; then
    echo "  (Mock 模式: 跳过等待)"
else
    echo "  等待 60 秒让战斗完成..."
    sleep 60
fi

# ==============================================================
# Step 9: 验证 A, B 的士兵数量都减少了
# ==============================================================
echo ""
echo "=================================================="
echo "Step 9: 验证士兵数量变化"
echo "=================================================="

POST_A=$(cli get_soldiers $UID_A $SOLDIER_ID)
POST_B=$(cli get_soldiers $UID_B $SOLDIER_ID)
echo "  A 士兵(攻击前): $PRE_ATTACK_A → 攻击后: $POST_A"
echo "  B 士兵(攻击前): $PRE_ATTACK_B → 攻击后: $POST_B"

if $IS_MOCK; then
    skip_test "A 士兵减少验证" "Mock 环境无战斗结算"
    skip_test "B 士兵减少验证" "Mock 环境无战斗结算"
else
    check_less_than "A 士兵减少验证" "$PRE_ATTACK_A" "$POST_A"
    check_less_than "B 士兵减少验证" "$PRE_ATTACK_B" "$POST_B"
fi

# ── 汇总报告 ────────────────────────────────────────────
echo ""
echo "=================================================="
printf "测试结果: \033[32mPASS=%d\033[0m  \033[31mFAIL=%d\033[0m  \033[33mSKIP=%d\033[0m  TOTAL=%d\n" "$PASS" "$FAIL" "$SKIP" "$((PASS+FAIL+SKIP))"
echo "=================================================="
for r in "${RESULTS[@]}"; do
    IFS='|' read -r status name detail <<< "$r"
    if [ "$status" = "PASS" ]; then
        printf "  [\033[32m%s\033[0m] %s: %s\n" "$status" "$name" "$detail"
    elif [ "$status" = "SKIP" ]; then
        printf "  [\033[33m%s\033[0m] %s: %s\n" "$status" "$name" "$detail"
    else
        printf "  [\033[31m%s\033[0m] %s: %s\n" "$status" "$name" "$detail"
    fi
done

# 退出码
if [ "$FAIL" -eq 0 ]; then
    echo ""
    echo "ALL TESTS PASSED (${SKIP} skipped)"
    exit 0
else
    echo ""
    echo "SOME TESTS FAILED"
    exit 1
fi
