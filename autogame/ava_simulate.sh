#!/bin/bash
# ava_simulate.sh — AVA 战场模拟对战脚本
#
# 用法: ./ava_simulate.sh <ava_id> [duration_minutes]
#   ava_id:           战场 ID (如 29999)
#   duration_minutes: 对战时长，默认 60 分钟
#
# 流程: 创建战场 → 全员加入 → 补给资源 → 记录起始积分
#       → 双方并发对战 → 等待 → 记录终止积分 → 全员退出 → 打印得分

set -uo pipefail
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8

# ── 参数 ────────────────────────────────────────────────
if [ $# -lt 1 ]; then
    echo "Usage: $0 <ava_id> [duration_minutes]"
    echo "  ava_id:           战场 ID (如 29999)"
    echo "  duration_minutes: 对战时长，默认 60 分钟"
    exit 1
fi

AVA_ID=$1
DURATION_MINUTES=${2:-60}
DURATION_SECONDS=$((DURATION_MINUTES * 60))

# ── 配置 ────────────────────────────────────────────────
CMD="python src/main.py"
SCORE_UID=20010643  # 用于查询积分的代表 UID

OUR_UIDS=(
    20010643 20010644 20010645 20010646 20010647
    20010648 20010649 20010650 20010651 20010652
    20010653 20010654 20010655 20010656 20010657
    20010658 20010659 20010660 20010661 20010662
)
ENEMY_UIDS=(
    20010668 20010669 20010670 20010671 20010672
    20010673 20010674 20010675 20010676 20010677
    20010678 20010679 20010680 20010681 20010682
    20010683 20010684 20010685 20010686 20010687
)
ALL_UIDS=("${OUR_UIDS[@]}" "${ENEMY_UIDS[@]}")

SOLDIER_IDS=(4 104 204)  # cavalry, infantry, archer

# ── 辅助函数 ────────────────────────────────────────────

cli() {
    echo "  > $CMD $*"
    $CMD "$@" 2>&1
}

# 从 get_ava_score 输出中提取指定 camp 的分数
# 用法: parse_camp_score "$output" 1   → 返回 Camp 1 的分数
parse_camp_score() {
    local output="$1" camp="$2"
    local score
    score=$(echo "$output" | sed -n "s/^Camp ${camp}.*score=\([0-9,]*\).*/\1/p" | tr -d ',')
    echo "${score:-0}"
}

# 后台进程管理
PID1=""
PID2=""

cleanup() {
    if [ -n "$PID1" ] || [ -n "$PID2" ]; then
        echo ""
        echo "Stopping battle processes..."
        [ -n "$PID1" ] && kill "$PID1" 2>/dev/null
        [ -n "$PID2" ] && kill "$PID2" 2>/dev/null
        wait "$PID1" 2>/dev/null
        wait "$PID2" 2>/dev/null
        PID1=""
        PID2=""
    fi
}

trap cleanup EXIT INT TERM

# ── 开始 ────────────────────────────────────────────────

echo "======================================================"
echo "  AVA Battlefield Simulation"
echo "  ava_id=$AVA_ID  duration=${DURATION_MINUTES}min"
echo "======================================================"
echo ""

# Step 1: 创建战场
echo "Step 1: Create AVA battlefield..."
cli uid_ava_create "$AVA_ID" "duration=2" || true
echo ""

# Step 2: 全员退出（清理旧状态）
echo "Step 2: Leave all accounts from battlefield..."
cli uid_ava_leave_all "$AVA_ID"
echo ""

# Step 3: 全员加入
echo "Step 3: Join all accounts to battlefield..."
cli uid_ava_join_all "$AVA_ID"
echo ""

# Step 4: 补给资源
echo "Step 4: Adding resources to all ${#ALL_UIDS[@]} accounts..."
for uid in "${ALL_UIDS[@]}"; do
    cli add_gem "$uid" 10000000 > /dev/null
    for sid in "${SOLDIER_IDS[@]}"; do
        cli add_soldiers "$uid" "$sid" 1000000 > /dev/null
    done
    echo "  [OK] uid=$uid"
done
echo ""

# Step 5: 记录起始积分
echo "Step 5: Recording starting scores..."
SCORE_START_OUTPUT=$(cli get_ava_score "$SCORE_UID" "$AVA_ID")
echo "$SCORE_START_OUTPUT"
CAMP1_START=$(parse_camp_score "$SCORE_START_OUTPUT" 1)
CAMP2_START=$(parse_camp_score "$SCORE_START_OUTPUT" 2)
echo ""
echo "  Starting scores: Camp1=$CAMP1_START  Camp2=$CAMP2_START"
echo ""

# Step 6: 启动双方对战
echo "Step 6: Starting battle (${DURATION_MINUTES} minutes)..."
echo "  > $CMD --team 1 run --ava $AVA_ID &"
$CMD --team 1 run --ava "$AVA_ID" &
PID1=$!

echo "  > $CMD --team 2 run --ava $AVA_ID &"
$CMD --team 2 run --ava "$AVA_ID" &
PID2=$!

echo "  Team1 PID=$PID1  Team2 PID=$PID2"
echo ""

# Step 7: 等待对战时长
echo "Step 7: Waiting ${DURATION_MINUTES} minutes..."
sleep "$DURATION_SECONDS"

# Step 8: 停止对战
echo ""
echo "Step 8: Time's up, stopping battle..."
cleanup
echo ""

# Step 9: 记录终止积分
echo "Step 9: Recording ending scores..."
SCORE_END_OUTPUT=$(cli get_ava_score "$SCORE_UID" "$AVA_ID")
echo "$SCORE_END_OUTPUT"
CAMP1_END=$(parse_camp_score "$SCORE_END_OUTPUT" 1)
CAMP2_END=$(parse_camp_score "$SCORE_END_OUTPUT" 2)
echo ""

# Step 10: 全员退出
echo "Step 10: Leave all accounts from battlefield..."
cli uid_ava_leave_all "$AVA_ID"
echo ""

# Step 11: 打印结果
CAMP1_DIFF=$((CAMP1_END - CAMP1_START))
CAMP2_DIFF=$((CAMP2_END - CAMP2_START))

echo "======================================================"
echo "  AVA Simulation Results (${DURATION_MINUTES} minutes)"
echo "======================================================"
echo "  Camp 1: $CAMP1_START -> $CAMP1_END  (delta: $CAMP1_DIFF)"
echo "  Camp 2: $CAMP2_START -> $CAMP2_END  (delta: $CAMP2_DIFF)"
echo "======================================================"
