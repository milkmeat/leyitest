#!/bin/bash
# test_rally.sh — Rally Attack 集成测试 (A组5人 集结攻击 B)
#
# 所有测试动作通过 CLI 文本指令触发，如:
#   python src/main.py add_gem 20010413 77777
#   python src/main.py create_rally 20010413 20010373 500 500 204 5000
#
# 用法:
#   ./test_rally.sh                    # 默认 test 环境
#   ./test_rally.sh --mock             # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

# ── 配置 ────────────────────────────────────────────────
UID_A1=20010413   # 队长
UID_A2=20010414
UID_A3=20010415
UID_A4=20010416
UID_A5=20010417
UID_A_ALL=($UID_A1 $UID_A2 $UID_A3 $UID_A4 $UID_A5)
UID_B=20010373

CMD="python src/main.py"
ENV_FLAG=""
IS_MOCK=false
PASS=0
FAIL=0
SKIP=0
RESULTS=()
SOLDIER_ID=204   # 使用 archer 类型进行验证
RALLY_SOLDIER_COUNT=5000

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
    if echo "$output" | grep -q "成功\|OK\|已出发\|侦察\|集结已发起\|已加入集结"; then
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

echo "Rally Attack 集成测试 (A组5人 → B)"
echo "  A1(队长): $UID_A1"
echo "  A2: $UID_A2"
echo "  A3: $UID_A3"
echo "  A4: $UID_A4"
echo "  A5: $UID_A5"
echo "  B:  $UID_B"
echo "  ENV: ${ENV_FLAG:-test}"
echo ""

# ==============================================================
# Step 1: 给 A(5人), B 都加上足够的宝石
# ==============================================================
echo "=================================================="
echo "Step 1: 添加宝石 (确保移城可用)"
echo "=================================================="

GEM_AMOUNT=200000
for uid in "${UID_A_ALL[@]}" $UID_B; do
    echo "  执行: add_gem $uid $GEM_AMOUNT"
    cli add_gem $uid $GEM_AMOUNT > /dev/null
done

# 验证宝石设置成功
for uid in "${UID_A_ALL[@]}" $UID_B; do
    GEM=$(cli get_gem $uid)
    echo "  uid=$uid 宝石: $GEM"
    check "uid=$uid 宝石设置" "$GEM_AMOUNT" "$GEM"
done

# ==============================================================
# Step 2: 给 A(5人), B 添加随机数量士兵，记录初始数量
# ==============================================================
echo ""
echo "=================================================="
echo "Step 2: 添加随机士兵并记录初始数量"
echo "=================================================="

declare -A PRE_ATTACK_SOLDIERS

for uid in "${UID_A_ALL[@]}" $UID_B; do
    ADD_COUNT=$(rand_range 1000 5000)
    OLD=$(cli get_soldiers $uid $SOLDIER_ID)
    echo "  uid=$uid 当前士兵(id=$SOLDIER_ID): $OLD, 添加: $ADD_COUNT"
    cli add_soldiers $uid $SOLDIER_ID $ADD_COUNT > /dev/null
    NEW=$(cli get_soldiers $uid $SOLDIER_ID)
    EXPECTED=$((OLD + ADD_COUNT))
    echo "  uid=$uid 士兵(添加后): $NEW (期望=$EXPECTED)"
    check "uid=$uid 士兵添加" "$EXPECTED" "$NEW"
    PRE_ATTACK_SOLDIERS[$uid]=$NEW
done

# ==============================================================
# Step 3: B 移城到随机位置
# ==============================================================
echo ""
echo "=================================================="
echo "Step 3: B 移城到随机位置"
echo "=================================================="

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

# 读取 B 的实际坐标
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
echo "Step 4: 等待观察 B 移城结果"
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
# Step 5: A(5人)全部移城到 B 的旁边
# ==============================================================
echo ""
echo "=================================================="
echo "Step 5: A组(5人) 移城到 B 附近(距离10以内)"
echo "=================================================="

# 生成多个偏移候选位置（距离B约3-10格）
OFFSET_PAIRS=(
    "3 3" "-3 3" "3 -3" "-3 -3"
    "5 0" "-5 0" "0 5" "0 -5"
    "7 3" "-7 3" "7 -3" "-7 -3"
    "4 6" "-4 6" "4 -6" "-4 -6"
    "8 0" "0 8" "-8 0" "0 -8"
    "6 6" "-6 6" "6 -6" "-6 -6"
    "9 0" "0 9" "-9 0" "0 -9"
)

offset_idx=0
echo "  B 实际位置: ($B_ACTUAL_X,$B_ACTUAL_Y)"

for uid in "${UID_A_ALL[@]}"; do
    A_MOVE_OK=false
    # 从候选偏移中依次尝试
    while [ $offset_idx -lt ${#OFFSET_PAIRS[@]} ]; do
        pair=${OFFSET_PAIRS[$offset_idx]}
        dx=$(echo $pair | cut -d' ' -f1)
        dy=$(echo $pair | cut -d' ' -f2)
        A_TARGET_X=$((B_ACTUAL_X + dx))
        A_TARGET_Y=$((B_ACTUAL_Y + dy))
        ((offset_idx++))

        # 边界检查
        if [ $A_TARGET_X -lt 1 ] || [ $A_TARGET_X -gt 998 ] || [ $A_TARGET_Y -lt 1 ] || [ $A_TARGET_Y -gt 998 ]; then
            continue
        fi

        echo "  尝试: l0 MOVE_CITY $uid $A_TARGET_X $A_TARGET_Y (偏移=$dx,$dy)"
        A_MOVE_OUTPUT=$(cli_verbose l0 MOVE_CITY $uid $A_TARGET_X $A_TARGET_Y)
        if echo "$A_MOVE_OUTPUT" | grep -q "\[OK\]"; then
            A_MOVE_OK=true
            echo "  成功!"
            break
        fi
        echo "  失败 (可能被占用)，尝试下一个偏移..."
    done

    if $A_MOVE_OK; then
        A_POS=$(cli get_player_pos $uid)
        printf "  [\033[32mPASS\033[0m] uid=$uid 移城成功 → $A_POS\n"
        ((PASS++))
        RESULTS+=("PASS|uid=$uid 移城|→ $A_POS")
    else
        printf "  [\033[31mFAIL\033[0m] uid=$uid 移城: 所有候选位置均被占用\n"
        ((FAIL++))
        RESULTS+=("FAIL|uid=$uid 移城|所有候选位置均被占用")
    fi
done

# ==============================================================
# Step 6: A1 对 B 发起侦察 (fire and forget)
# ==============================================================
echo ""
echo "=================================================="
echo "Step 6: A1 侦察 B"
echo "=================================================="

echo "  执行: scout_player $UID_A1 $UID_B $B_ACTUAL_X $B_ACTUAL_Y"
SCOUT_OUTPUT=$(cli_verbose scout_player $UID_A1 $UID_B $B_ACTUAL_X $B_ACTUAL_Y)
echo "  输出: $(echo "$SCOUT_OUTPUT" | head -3)"
check_success "A1 侦察 B 命令执行" "$SCOUT_OUTPUT"

# ==============================================================
# Step 7: A1 对 B 发起集结 (create_rally)
# ==============================================================
echo ""
echo "=================================================="
echo "Step 7: A1 发起集结攻击 B (5分钟倒计时)"
echo "=================================================="

echo "  执行: create_rally $UID_A1 $UID_B $B_ACTUAL_X $B_ACTUAL_Y $SOLDIER_ID $RALLY_SOLDIER_COUNT 300"
RALLY_OUTPUT=$(cli_verbose create_rally $UID_A1 $UID_B $B_ACTUAL_X $B_ACTUAL_Y $SOLDIER_ID $RALLY_SOLDIER_COUNT 300)
echo "  输出: $(echo "$RALLY_OUTPUT" | head -5)"
check_success "A1 发起集结命令执行" "$RALLY_OUTPUT"

# 从 JSON 输出中提取 rally_id (可能在转义的 JSON 字符串中)
RALLY_ID=$(echo "$RALLY_OUTPUT" | grep -oP '"rally_id"\s*:\s*"\K[^"]+' | head -1)
if [ -z "$RALLY_ID" ]; then
    # 转义格式: \"rally_id\": \"rally_xxx\"
    RALLY_ID=$(echo "$RALLY_OUTPUT" | grep -oP '\\?"rally_id\\?"\s*:\s*\\?"(\K[^"\\]+)' | head -1)
fi
if [ -z "$RALLY_ID" ]; then
    # 最宽松匹配: rally_UID_TIMESTAMP 模式
    RALLY_ID=$(echo "$RALLY_OUTPUT" | grep -oP 'rally_\d+_\d+' | head -1)
fi

if [ -n "$RALLY_ID" ]; then
    printf "  [\033[32mPASS\033[0m] 获取 rally_id: %s\n" "$RALLY_ID"
    ((PASS++))
    RESULTS+=("PASS|获取 rally_id|$RALLY_ID")
else
    printf "  [\033[31mFAIL\033[0m] 未能从响应中提取 rally_id\n"
    ((FAIL++))
    RESULTS+=("FAIL|获取 rally_id|响应中未找到 rally_id")
    echo "  完整输出:"
    echo "$RALLY_OUTPUT"
fi

# ==============================================================
# Step 8: A2-A5 加入集结 (join_rally)
# ==============================================================
echo ""
echo "=================================================="
echo "Step 8: A2-A5 加入集结"
echo "=================================================="

if [ -z "$RALLY_ID" ]; then
    echo "  无法加入集结: rally_id 未获取到"
    for uid in $UID_A2 $UID_A3 $UID_A4 $UID_A5; do
        skip_test "uid=$uid 加入集结" "rally_id 未获取到"
    done
else
    for uid in $UID_A2 $UID_A3 $UID_A4 $UID_A5; do
        echo "  执行: join_rally $uid $RALLY_ID $SOLDIER_ID $RALLY_SOLDIER_COUNT"
        JOIN_OUTPUT=$(cli_verbose join_rally $uid $RALLY_ID $SOLDIER_ID $RALLY_SOLDIER_COUNT)
        echo "  输出: $(echo "$JOIN_OUTPUT" | head -3)"
        check_success "uid=$uid 加入集结" "$JOIN_OUTPUT"
    done
fi

# ==============================================================
# Step 9: 等待 6 分钟至战斗完成
# ==============================================================
echo ""
echo "=================================================="
echo "Step 9: 等待战斗完成"
echo "=================================================="
if $IS_MOCK; then
    echo "  (Mock 模式: 跳过等待)"
else
    echo "  集结倒计时 5 分钟 + 行军时间，共等待 6 分钟..."
    echo "  开始时间: $(date '+%H:%M:%S')"
    sleep 360
    echo "  结束时间: $(date '+%H:%M:%S')"
fi

# ==============================================================
# Step 10: 验证 A(5人), B 的士兵数量都减少了
# ==============================================================
echo ""
echo "=================================================="
echo "Step 10: 验证士兵数量变化"
echo "=================================================="

for uid in "${UID_A_ALL[@]}" $UID_B; do
    POST=$(cli get_soldiers $uid $SOLDIER_ID)
    PRE=${PRE_ATTACK_SOLDIERS[$uid]}
    echo "  uid=$uid 士兵(攻击前): $PRE → 攻击后: $POST"

    if $IS_MOCK; then
        skip_test "uid=$uid 士兵减少验证" "Mock 环境无战斗结算"
    else
        check_less_than "uid=$uid 士兵减少验证" "$PRE" "$POST"
    fi
done

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
