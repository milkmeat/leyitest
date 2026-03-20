#!/bin/bash
# prepare_alpha.sh - 准备 Alpha 小队进入 AVA 战场
#
# 功能：
# 1. 先检查成员状态，已进入的跳过
# 2. 只对未进入的成员执行：添加到名单 → 进入战场
#
# 用法: bash scripts/prepare_alpha.sh [lvl_id] [camp_id]
#   lvl_id: 战场 ID，默认 29999
#   camp_id: 阵营 ID，默认 1

set -e  # 遇到错误立即退出

# 配置参数
LVL_ID=${1:-29999}
CAMP_ID=${2:-1}

# Alpha 小队成员 UID 列表（来自 config/squads.yaml）
ALPHA_MEMBERS=(
    20010643
    20010644
    20010645
    20010646
    20010647
)

echo "======================================"
echo "Prepare Alpha Squad for AVA Battle"
echo "======================================"
echo "Battle ID: $LVL_ID"
echo "Camp ID: $CAMP_ID"
echo "======================================"
echo ""

# 检查 main.py 是否存在
if [ ! -f "src/main.py" ]; then
    echo "Error: src/main.py not found, please run from project root"
    exit 1
fi

# 1. 检查成员状态
echo "Step 1: Checking member AVA battle status..."
ALREADY_IN=()
NEED_ENTER=()

for uid in "${ALPHA_MEMBERS[@]}"; do
    # 查询 AVA 状态
    OUTPUT=$(python src/main.py uid_ava_status "$uid" 2>&1)

    # 提取 lvl_id 值（避免中文乱码）
    # 输出格式: "uid=20010643 xxx lvl_id=29999" 或 "uid=20010644 xxx lvl_id=0"
    CURRENT_LVL=$(echo "$OUTPUT" | grep -o "lvl_id=[0-9]*" | cut -d"=" -f2)

    if [ -z "$CURRENT_LVL" ]; then
        CURRENT_LVL="0"
    fi

    echo "  uid=$uid: lvl_id=$CURRENT_LVL"

    # 检查是否已在目标战场中
    if [ "$CURRENT_LVL" = "$LVL_ID" ]; then
        ALREADY_IN+=("$uid")
    elif [ "$CURRENT_LVL" != "0" ]; then
        # 在其他战场中
        echo "    WARNING: uid=$uid is in different battle ($CURRENT_LVL), will re-enter"
        NEED_ENTER+=("$uid")
    else
        # 在普通地图
        NEED_ENTER+=("$uid")
    fi
done

echo ""
echo "Status Summary:"
echo "  Already in battle (${#ALREADY_IN[@]}): ${ALREADY_IN[@]:-none}"
echo "  Need to enter (${#NEED_ENTER[@]}): ${NEED_ENTER[@]:-none}"
echo ""

# 2. 处理未进入的成员
if [ ${#NEED_ENTER[@]} -eq 0 ]; then
    echo "Step 2: All members already in battle, skipping"
else
    echo "Step 2: Adding members to whitelist and entering battle..."

    for uid in "${NEED_ENTER[@]}"; do
        echo ""
        echo "  > Processing uid=$uid:"

        # 2.1 添加到准入名单
        echo "    - Adding to whitelist (lvl_id=$LVL_ID, camp_id=$CAMP_ID)..."
        python src/main.py uid_ava_add "$LVL_ID" "$uid" "$CAMP_ID" 2>&1 | grep -E "(ret_code|OK|FAIL|Error)" || true

        # 2.2 进入战场
        echo "    - Entering battle..."
        python src/main.py uid_ava_enter "$LVL_ID" "$uid" 2>&1 | grep -E "(ret_code|OK|FAIL|Error|lvl_id)" || true

        # 等待一秒避免请求过快
        sleep 1
    done
fi

echo ""

# 3. 最终状态确认
echo "Step 3: Final status confirmation..."
for uid in "${ALPHA_MEMBERS[@]}"; do
    OUTPUT=$(python src/main.py uid_ava_status "$uid" 2>&1)
    CURRENT_LVL=$(echo "$OUTPUT" | grep -o "lvl_id=[0-9]*" | cut -d"=" -f2)
    if [ "$CURRENT_LVL" = "$LVL_ID" ]; then
        STATUS="IN BATTLE (lvl_id=$CURRENT_LVL)"
    elif [ "$CURRENT_LVL" = "0" ]; then
        STATUS="NOT IN BATTLE"
    else
        STATUS="IN OTHER BATTLE (lvl_id=$CURRENT_LVL)"
    fi
    echo "  - uid=$uid: $STATUS"
done

echo ""
echo "======================================"
echo "Preparation Complete!"
echo "Already in battle: ${#ALREADY_IN[@]}"
echo "Newly entered: ${#NEED_ENTER[@]}"
echo "======================================"
