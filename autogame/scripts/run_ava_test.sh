#!/bin/bash
# run_ava_test.sh - 运行 AVA 战场 L1+L0 测试
#
# 功能：
# 1. 调用 prepare_alpha.sh 准备战场
# 2. 启动主循环，使用 mock L2 指令
# 3. 持续运行，每循环打印队员位置和建筑控制状态
#
# 用法: bash scripts/run_ava_test.sh [target_x] [target_y] [l1_prompt]
#   target_x: 目标建筑 X 坐标，默认 154
#   target_y: 目标建筑 Y 坐标，默认 170
#   l1_prompt: L1 prompt 模板名称，默认 ava

set -e

# 配置参数
TARGET_X=${1:-154}
TARGET_Y=${2:-170}
L1_PROMPT=${3:-ava}
LVL_ID=29999
CAMP_ID=1

# 构建 mock L2 指令
MOCK_L2="[小队 1 (Alpha)] 控制 建筑 pos:(${TARGET_X}, ${TARGET_Y})"

echo "======================================"
echo "AVA 战场 L1+L0 测试"
echo "======================================"
echo "目标建筑: (${TARGET_X}, ${TARGET_Y})"
echo "Mock L2: ${MOCK_L2}"
echo "L1 Prompt: ${L1_PROMPT}"
echo "======================================"
echo ""

# 1. 准备战场
echo "→ 步骤 1: 准备战场..."
bash scripts/prepare_alpha.sh "$LVL_ID" "$CAMP_ID"
echo ""

# 2. 启动测试
echo "→ 步骤 2: 启动主循环测试..."
echo "命令: python src/main.py run --mock-l2 \"${MOCK_L2}\" --l1-prompt ${L1_PROMPT}"
echo ""
echo "按 Ctrl+C 停止测试"
echo "======================================"
echo ""

python src/main.py run \
    --mock-l2 "$MOCK_L2" \
    --l1-prompt "$L1_PROMPT" \
    --loop.interval_seconds 0
