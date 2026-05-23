#!/bin/bash
# ava_simulate.sh — AVA 战场 A/B 对战模拟脚本
#
# 用法: ./ava_simulate.sh [--v1 VERSION1] [--v2 VERSION2] [--rounds N] [--duration MINUTES] [--csv FILE]
#
#   --v1        第一个 L2 prompt 版本（默认: default）
#   --v2        第二个 L2 prompt 版本（默认: attack）
#   --rounds    对战轮数，每轮2场交换阵营（默认: 1）
#   --duration  每场对战时长，分钟（默认: 60）
#   --csv       结果 CSV 文件路径（默认: ava_results.csv）
#
# 每轮对战包含两场（交换 team1/team2 位置），消除阵营位置偏差。
# 每场开始前创建新战场并重置账号状态。

set -uo pipefail
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8

# ── 参数解析 ────────────────────────────────────────────
V1="default"
V2="attack"
ROUNDS=1
DURATION_MINUTES=60
CSV_FILE="ava_results.csv"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --v1) V1="$2"; shift 2 ;;
        --v2) V2="$2"; shift 2 ;;
        --rounds) ROUNDS="$2"; shift 2 ;;
        --duration) DURATION_MINUTES="$2"; shift 2 ;;
        --csv) CSV_FILE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

DURATION_SECONDS=$((DURATION_MINUTES * 60))
TOTAL_MATCHES=$((ROUNDS * 2))

# ── 配置 ────────────────────────────────────────────────
CMD="python src/main.py"
SCORE_UID=20010643

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
SOLDIER_IDS=(4 104 204)

# ── 结果存储数组 ────────────────────────────────────────
declare -a MATCH_V_TEAM1=()
declare -a MATCH_V_TEAM2=()
declare -a MATCH_SCORE_CAMP1=()
declare -a MATCH_SCORE_CAMP2=()
declare -a MATCH_LOSS_TEAM1=()
declare -a MATCH_LOSS_TEAM2=()

# ── 辅助函数 ────────────────────────────────────────────

cli() {
    echo "  > $CMD $*"
    $CMD "$@" 2>&1
}

find_free_ava_id() {
    local id
    for id in $(seq 40001 40100); do
        local output
        output=$($CMD lvl_get_battle_server_detail "$id" 2>&1)
        if echo "$output" | grep -q "\[OK\]"; then
            echo "  ava_id=$id 已存在，跳过" >&2
        else
            echo "$id"
            return 0
        fi
    done
    echo "ERROR: 40001-40100 全部被占用" >&2
    return 1
}

parse_camp_score() {
    local output="$1" camp="$2"
    local score
    score=$(echo "$output" | sed -n "s/^Camp ${camp}.*score=\([0-9,]*\).*/\1/p" | tr -d ',')
    echo "${score:-0}"
}

# 后台进程管理
PID1=""
PID2=""
PID_OBS=""

cleanup() {
    if [ -n "$PID1" ] || [ -n "$PID2" ] || [ -n "$PID_OBS" ]; then
        echo ""
        echo "Stopping battle processes..."
        [ -n "$PID_OBS" ] && kill "$PID_OBS" 2>/dev/null
        [ -n "$PID1" ] && kill "$PID1" 2>/dev/null
        [ -n "$PID2" ] && kill "$PID2" 2>/dev/null
        wait "$PID_OBS" 2>/dev/null
        wait "$PID1" 2>/dev/null
        wait "$PID2" 2>/dev/null
        PID_OBS=""
        PID1=""
        PID2=""
    fi
}

# observer 轮询循环（后台运行）
run_observer_loop() {
    local uid="$1" ava_id="$2" events_file="$3" state_file="$4"
    local match_id="$5" camp_a="$6" duration_sec="$7"
    local interval=30
    local seq=0
    local start_time=$SECONDS

    while true; do
        local elapsed=$(( SECONDS - start_time ))
        if [ $elapsed -ge $duration_sec ]; then
            break
        fi
        $CMD ava_observe "$uid" "$ava_id" \
            --state "$state_file" --output "$events_file" \
            --strategy-a "$V1" --strategy-b "$V2" \
            --match-id "$match_id" --camp-a "$camp_a" \
            --elapsed "$elapsed" --seq "$seq" > /dev/null 2>&1
        ((seq++))
        sleep "$interval"
    done
}

trap cleanup EXIT INT TERM

# ── 单场对战函数 ────────────────────────────────────────

run_single_match() {
    local match_idx="$1" round_num="$2" match_in_round="$3"
    local v_team1="$4" v_team2="$5"

    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "  Round $round_num Match $match_in_round"
    echo "  Team1=$v_team1  Team2=$v_team2"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""

    # 存储本场版本分配
    MATCH_V_TEAM1[$match_idx]="$v_team1"
    MATCH_V_TEAM2[$match_idx]="$v_team2"

    # 1. 探测空闲战场 ID
    echo "[Match] Finding free AVA battlefield ID..."
    local ava_id
    ava_id=$(find_free_ava_id)
    if [ -z "$ava_id" ]; then
        echo "ERROR: 无法找到空闲战场 ID" >&2
        return 1
    fi
    echo "  -> ava_id=$ava_id"

    # 2. 创建战场
    echo "[Match] Create AVA battlefield..."
    cli uid_ava_create "$ava_id" "duration=2" || true

    # 3. 全员退出（清理旧状态）+ 全员加入
    echo "[Match] Leave all (cleanup)..."
    cli uid_ava_leave_all "$ava_id"
    echo "[Match] Join all accounts..."
    cli uid_ava_join_all "$ava_id"

    # 4. 补给资源
    echo "[Match] Adding resources..."
    for uid in "${ALL_UIDS[@]}"; do
        $CMD add_gem "$uid" 10000000 > /dev/null 2>&1
        for sid in "${SOLDIER_IDS[@]}"; do
            $CMD add_soldiers "$uid" "$sid" 1000000 > /dev/null 2>&1
        done
    done
    echo "  [OK] ${#ALL_UIDS[@]} accounts supplied"

    # 5. 记录起始兵力/积分
    echo "[Match] Recording starting state..."
    local soldiers_t1_start soldiers_t2_start
    soldiers_t1_start=$($CMD get_team_soldiers 1 2>/dev/null)
    soldiers_t2_start=$($CMD get_team_soldiers 2 2>/dev/null)

    local score_start_output camp1_start camp2_start
    score_start_output=$($CMD get_ava_score "$SCORE_UID" "$ava_id" 2>/dev/null)
    camp1_start=$(parse_camp_score "$score_start_output" 1)
    camp2_start=$(parse_camp_score "$score_start_output" 2)
    echo "  Soldiers: T1=$soldiers_t1_start  T2=$soldiers_t2_start"
    echo "  Scores:   Camp1=$camp1_start  Camp2=$camp2_start"

    # 6. 归档旧日志
    if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
        mv logs "logs.r${round_num}m${match_in_round}.$(date +%H%M%S)"
    fi
    mkdir -p logs

    # 7. 启动双方对战
    echo "[Match] Starting battle (${DURATION_MINUTES}min)..."
    echo "  Team1: --l2-prompt $v_team1"
    echo "  Team2: --l2-prompt $v_team2"

    $CMD --team 1 run --ava "$ava_id" --l2-prompt "$v_team1" &
    PID1=$!
    $CMD --team 2 run --ava "$ava_id" --l2-prompt "$v_team2" &
    PID2=$!

    # 7b. 启动观察者循环（后台独立进程调用）
    local events_file="logs/events_r${round_num}m${match_in_round}.jsonl"
    local state_file="logs/observer_state_r${round_num}m${match_in_round}.json"
    local match_id="${V1}_vs_${V2}_r${round_num}m${match_in_round}"
    local camp_a=1
    if [ "$v_team1" != "$V1" ]; then
        camp_a=2
    fi
    run_observer_loop "$SCORE_UID" "$ava_id" "$events_file" "$state_file" \
        "$match_id" "$camp_a" "$DURATION_SECONDS" &
    PID_OBS=$!

    # 8. 等待
    echo "[Match] Waiting ${DURATION_MINUTES} minutes..."
    sleep "$DURATION_SECONDS"

    # 9. 停止对战
    echo "[Match] Time's up, stopping..."
    cleanup

    # 9b. 写入 MATCH_END 并导出 CSV
    if [ -f "$state_file" ]; then
        $CMD ava_observe_end \
            --state "$state_file" --output "$events_file" \
            --strategy-a "$V1" --strategy-b "$V2" --match-id "$match_id"
    fi
    if [ -f "$events_file" ]; then
        echo "[Match] Exporting events to CSV ($CSV_FILE)..."
        $CMD ava_export_csv "$events_file" --csv "$CSV_FILE"
    fi

    # 10. 记录结束兵力/积分
    local soldiers_t1_end soldiers_t2_end
    soldiers_t1_end=$($CMD get_team_soldiers 1 2>/dev/null)
    soldiers_t2_end=$($CMD get_team_soldiers 2 2>/dev/null)

    local score_end_output camp1_end camp2_end
    score_end_output=$($CMD get_ava_score "$SCORE_UID" "$ava_id" 2>/dev/null)
    camp1_end=$(parse_camp_score "$score_end_output" 1)
    camp2_end=$(parse_camp_score "$score_end_output" 2)

    # 计算 delta
    local score_camp1=$((camp1_end - camp1_start))
    local score_camp2=$((camp2_end - camp2_start))
    local loss_t1=$((soldiers_t1_start - soldiers_t1_end))
    local loss_t2=$((soldiers_t2_start - soldiers_t2_end))

    # 存储结果
    MATCH_SCORE_CAMP1[$match_idx]=$score_camp1
    MATCH_SCORE_CAMP2[$match_idx]=$score_camp2
    MATCH_LOSS_TEAM1[$match_idx]=$loss_t1
    MATCH_LOSS_TEAM2[$match_idx]=$loss_t2

    echo "[Match] Result: Score Camp1=$score_camp1 Camp2=$score_camp2 | Loss T1=$loss_t1 T2=$loss_t2"

    # 11. 全员退出
    echo "[Match] Leave all..."
    cli uid_ava_leave_all "$ava_id"
}

# ── 主流程 ──────────────────────────────────────────────

echo "══════════════════════════════════════════════════════"
echo "  AVA A/B Test: $V1 vs $V2"
echo "  Rounds=$ROUNDS (${TOTAL_MATCHES} matches)  Duration=${DURATION_MINUTES}min/match"
echo "══════════════════════════════════════════════════════"

match_idx=0
for ((round=1; round<=ROUNDS; round++)); do
    # Match 1: Team1=V1, Team2=V2
    run_single_match $match_idx $round 1 "$V1" "$V2"
    ((match_idx++))

    # Match 2: Team1=V2, Team2=V1 (交换阵营)
    run_single_match $match_idx $round 2 "$V2" "$V1"
    ((match_idx++))
done

# ── 汇总输出 ────────────────────────────────────────────

echo ""
echo "══════════════════════════════════════════════════════"
echo "  A/B Test Summary: $V1 vs $V2"
echo "  Rounds: $ROUNDS (${TOTAL_MATCHES} matches)  Duration: ${DURATION_MINUTES}min/match"
echo "══════════════════════════════════════════════════════"
echo ""

# 按版本聚合
v1_total_score=0
v1_total_loss=0
v1_wins=0
v2_total_score=0
v2_total_loss=0
v2_wins=0

for ((i=0; i<match_idx; i++)); do
    local_v_t1="${MATCH_V_TEAM1[$i]}"
    local_v_t2="${MATCH_V_TEAM2[$i]}"
    s_camp1="${MATCH_SCORE_CAMP1[$i]}"
    s_camp2="${MATCH_SCORE_CAMP2[$i]}"
    l_t1="${MATCH_LOSS_TEAM1[$i]}"
    l_t2="${MATCH_LOSS_TEAM2[$i]}"

    # Team1 的版本得分 = Camp1 分数, Team2 的版本得分 = Camp2 分数
    if [ "$local_v_t1" = "$V1" ]; then
        v1_score=$s_camp1; v1_loss=$l_t1
        v2_score=$s_camp2; v2_loss=$l_t2
    else
        v2_score=$s_camp1; v2_loss=$l_t1
        v1_score=$s_camp2; v1_loss=$l_t2
    fi

    # 计算 round/match 编号
    local_round=$(( i / 2 + 1 ))
    local_match=$(( i % 2 + 1 ))
    diff=$((v1_score - v2_score))

    if [ $diff -ge 0 ]; then
        winner="$V1 +$diff"
    else
        winner="$V2 +$((-diff))"
    fi

    echo "  Round $local_round Match $local_match: Team1=$local_v_t1  Team2=$local_v_t2"
    echo "    Score:  $V1=$v1_score  $V2=$v2_score  ($winner)"
    echo "    Losses: $V1=$v1_loss  $V2=$v2_loss"
    echo ""

    # 累加
    v1_total_score=$((v1_total_score + v1_score))
    v1_total_loss=$((v1_total_loss + v1_loss))
    v2_total_score=$((v2_total_score + v2_score))
    v2_total_loss=$((v2_total_loss + v2_loss))

    if [ $v1_score -gt $v2_score ]; then
        ((v1_wins++))
    elif [ $v2_score -gt $v1_score ]; then
        ((v2_wins++))
    fi
done

# 平均值
if [ $match_idx -gt 0 ]; then
    v1_avg_score=$((v1_total_score / match_idx))
    v1_avg_loss=$((v1_total_loss / match_idx))
    v2_avg_score=$((v2_total_score / match_idx))
    v2_avg_loss=$((v2_total_loss / match_idx))
else
    v1_avg_score=0; v1_avg_loss=0
    v2_avg_score=0; v2_avg_loss=0
fi

echo "──────────────────────────────────────────────────────"
echo "  TOTALS (${match_idx} matches):"
echo "    $V1: avg_score=$v1_avg_score  avg_loss=$v1_avg_loss  wins=${v1_wins}/${match_idx}"
echo "    $V2: avg_score=$v2_avg_score  avg_loss=$v2_avg_loss  wins=${v2_wins}/${match_idx}"
echo "══════════════════════════════════════════════════════"
