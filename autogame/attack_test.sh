#!/bin/bash
# attack_test.sh — AVA 建筑争夺战测试：验证克制兵种自动切换
#
# 用法: ./attack_test.sh
#
# 流程: 创建战场 → A/B 加入 → 移城 → 循环攻击 → 打印报告

set -uo pipefail
cd "$(dirname "$0")"
export PYTHONIOENCODING=utf-8

# ── 配置 ────────────────────────────────────────────────
CMD="python src/main.py"
A_UID=20010643        # 我方
B_UID=20010668        # 敌方
A_CAMP=1
B_CAMP=2
A_POS="178 132"       # 移城目标
B_POS="185 131"
TARGET_X=180          # No.4 Production Shed
TARGET_Y=130
TARGET_KEY=971
LOOP_COUNT=5
MARCH_WAIT=20     # 每次攻击后等待（秒）：行军 6s + 战斗 + 缓冲

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

# ── 开始 ────────────────────────────────────────────────
echo "============================================"
echo "  AVA 建筑争夺战 — 克制兵种切换测试"
echo "============================================"
echo ""

# 1. 创建战场
echo "── Step 1: 创建战场 ──"
AVA_ID=$(find_free_ava_id)
if [ -z "$AVA_ID" ]; then
    echo "[FAIL] 无法找到空闲战场 ID"
    exit 1
fi
echo "  AVA_ID = $AVA_ID"

cli uid_ava_create "$AVA_ID" "duration=2"
echo ""

# 2. 加入战场
echo "── Step 2: 加入战场 ──"
cli uid_ava_add "$AVA_ID" "$A_UID" "$A_CAMP"
cli uid_ava_add "$AVA_ID" "$B_UID" "$B_CAMP"
echo ""

# 3. 进入战场（先退出旧战场）
echo "── Step 3: 进入战场 ──"
echo "  退出旧战场（如有）..."
cli uid_ava_leave "$A_UID" 2>&1 || true
cli uid_ava_leave "$B_UID" 2>&1 || true
echo "  进入新战场 $AVA_ID..."
cli uid_ava_enter "$AVA_ID" "$A_UID"
cli uid_ava_enter "$AVA_ID" "$B_UID"
echo ""

# 4. 等待准备期（账号已入场后再等待）
echo "── Step 4: 等待 4 分钟（3 分钟准备期 + 1 分钟缓冲）──"
sleep 240
echo "  等待结束"
echo ""

# 5. 补兵
echo "── Step 5: 补兵 ──"
cli add_soldiers "$A_UID" 204 1000000
cli add_soldiers "$B_UID" 204 1000000
echo ""

# 6. 更新 env_config 的 lvl_id
echo "── Step 6: 更新配置 lvl_id=$AVA_ID ──"
python -c "
import yaml
with open('config/env_config.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)
cfg['default_header']['lvl_id'] = $AVA_ID
with open('config/env_config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
print('  env_config.yaml lvl_id → $AVA_ID')
"
echo ""

# 7. 移城
echo "── Step 7: 移城 ──"
cli lvl_move_city "$A_UID" "$AVA_ID" $A_POS
cli lvl_move_city "$B_UID" "$AVA_ID" $B_POS
echo ""

# 8. 发现建筑
echo "── Step 8: 发现 No.4 Production Shed ──"
BUILDING_UID=$(python attack_find_building.py "$AVA_ID" "$TARGET_KEY" "$A_UID")
if [ -z "$BUILDING_UID" ]; then
    echo "[FAIL] 未找到 No.4 Production Shed (key=$TARGET_KEY)"
    exit 1
fi
echo "  BUILDING_UID = $BUILDING_UID"
echo ""

# 9. 循环攻击
echo "── Step 9: 循环攻击 $LOOP_COUNT 次 ──"
echo "  格式: [轮次] 攻击方 → 结果 | 选择兵种"
echo "  每次攻击后等待 ${MARCH_WAIT}s（行军+战斗）"
echo ""

declare -a REPORT_LINES

sid_to_tag() {
    case "$1" in
        4)   echo "Basher(4)" ;;
        104) echo "Shooter(104)" ;;
        204) echo "Piercer(204)" ;;
        *)   echo "ID=${1:-?}" ;;
    esac
}

for i in $(seq 1 $LOOP_COUNT); do
    # A 攻击建筑
    output_a=$(cli l0 LVL_ATTACK_BUILDING "$A_UID" "$BUILDING_UID" "$TARGET_X" "$TARGET_Y" 2>&1)
    sid_a=$(echo "$output_a" | tr -d '\n\r' | grep -oP '"soldier":\s*\{[^}]*"\K[0-9]+' | head -1)
    result_a=$(echo "$output_a" | grep -oE "\[OK\]|\[FAIL\]" | tail -1)
    tag_a=$(sid_to_tag "$sid_a")
    echo "  [$i] A($A_UID) → $result_a  兵种=$tag_a"
    REPORT_LINES+=("[$i] A → $result_a  兵种=$tag_a")

    echo "    等待 ${MARCH_WAIT}s..."
    sleep $MARCH_WAIT

    # B 攻击建筑（camp=2 操作敌方账号）
    output_b=$(cli l0 --camp 2 LVL_ATTACK_BUILDING "$B_UID" "$BUILDING_UID" "$TARGET_X" "$TARGET_Y" 2>&1)
    sid_b=$(echo "$output_b" | tr -d '\n\r' | grep -oP '"soldier":\s*\{[^}]*"\K[0-9]+' | head -1)
    result_b=$(echo "$output_b" | grep -oE "\[OK\]|\[FAIL\]" | tail -1)
    tag_b=$(sid_to_tag "$sid_b")
    echo "  [$i] B($B_UID) → $result_b  兵种=$tag_b"
    REPORT_LINES+=("[$i] B → $result_b  兵种=$tag_b")

    if [ "$i" -lt "$LOOP_COUNT" ]; then
        echo "    等待 ${MARCH_WAIT}s..."
        sleep $MARCH_WAIT
    fi
done

# 9. 测试报告
echo ""
echo "============================================"
echo "  测试报告"
echo "============================================"
echo "  战场: $AVA_ID"
echo "  建筑: No.4 Production Shed ($BUILDING_UID)"
echo "  循环: $LOOP_COUNT 轮"
echo ""
for line in "${REPORT_LINES[@]}"; do
    echo "  $line"
done

# 检查兵种是否有变化
all_sids=$(printf "%s\n" "${REPORT_LINES[@]}" | grep -oP "兵种=\K\S+" | sort -u)
sid_count=$(echo "$all_sids" | wc -l | tr -d ' ')
echo ""
if [ "$sid_count" -gt 1 ]; then
    echo "  PASS: 兵种切换验证通过 - 共出现 $sid_count 种不同兵种"
elif [ "$sid_count" -eq 1 ]; then
    echo "  WARN: 兵种未切换 - 始终为 $(echo "$all_sids" | head -1)"
else
    echo "  WARN: 未检测到兵种信息"
fi

# 统计成功/失败
ok_count=$(printf "%s\n" "${REPORT_LINES[@]}" | grep -c "\[OK\]")
fail_count=$(printf "%s\n" "${REPORT_LINES[@]}" | grep -c "\[FAIL\]")
echo "  成功: $ok_count  失败: $fail_count"

echo ""
echo "============================================"
echo "  测试完成"
echo "============================================"
