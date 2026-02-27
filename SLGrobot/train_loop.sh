#!/bin/bash
# 每70分钟一轮，每轮依次采集资源、训练兵种（间隔10秒）
# 用法: bash train_loop.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RESOURCES=("木材" "石材" "铁块")
TROOPS=("步兵" "骑兵" "远程兵")
INTERVAL=$((70 * 60))  # 70分钟，单位秒

echo "=== 训练循环启动 ==="
echo "每轮采集: ${RESOURCES[*]}"
echo "每轮训练: ${TROOPS[*]}"
echo "轮次间隔: 70 分钟"
echo "按 Ctrl+C 停止"
echo ""

cycle=1
while true; do
    echo "============================================"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 第${cycle}轮开始"
    echo "============================================"

    # --- 采集资源 ---
    for i in "${!RESOURCES[@]}"; do
        res="${RESOURCES[$i]}"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 执行: quest 采集${res}"

        python main.py quest "采集${res}"
        exit_code=$?

        if [ $exit_code -ne 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告: quest 采集${res} 退出码 ${exit_code}"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成: quest 采集${res}"
        fi

        if [ $i -lt $((${#RESOURCES[@]} - 1)) ]; then
            sleep 10
        fi
    done

    sleep 10

    # --- 训练兵种 ---
    for i in "${!TROOPS[@]}"; do
        troop="${TROOPS[$i]}"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 执行: quest 训练${troop}"

        python main.py quest "训练${troop}"
        exit_code=$?

        if [ $exit_code -ne 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告: quest 训练${troop} 退出码 ${exit_code}"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成: quest 训练${troop}"
        fi

        # 最后一个兵种训练完不需要等10秒
        if [ $i -lt $((${#TROOPS[@]} - 1)) ]; then
            sleep 10
        fi
    done

    sleep 10

    # --- 领取奖励 ---
    REWARDS=("领取任务奖励" "领取远征奖励")
    for i in "${!REWARDS[@]}"; do
        reward="${REWARDS[$i]}"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 执行: quest ${reward}"

        python main.py quest "${reward}"
        exit_code=$?

        if [ $exit_code -ne 0 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告: quest ${reward} 退出码 ${exit_code}"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成: quest ${reward}"
        fi

        if [ $i -lt $((${#REWARDS[@]} - 1)) ]; then
            sleep 10
        fi
    done

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 第${cycle}轮完成，等待 70 分钟..."
    cycle=$((cycle + 1))
    sleep $INTERVAL
done
