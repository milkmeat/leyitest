#!/bin/bash
# test_phase1.sh — Phase 1 基础设施整体验收
#
# 顺序运行所有测试脚本，汇总结果
#
# 用法:
#   ./test_phase1.sh                    # 默认 test 环境
#   ./test_phase1.sh --mock             # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

export PYTHONIOENCODING=utf-8

# 传递参数
ARGS="$*"

echo "========================================"
echo "  Phase 1 基础设施验收"
echo "========================================"
echo ""

TOTAL_PASS=0
TOTAL_FAIL=0
REPORT=()

run_suite() {
    local name="$1"
    local script="$2"
    echo "────────────────────────────────────────"
    echo "  运行: $name ($script)"
    echo "────────────────────────────────────────"
    if bash "$script" $ARGS; then
        REPORT+=("PASS|$name")
        ((TOTAL_PASS++))
    else
        REPORT+=("FAIL|$name")
        ((TOTAL_FAIL++))
    fi
    echo ""
}

run_suite "数据同步"    "./test_sync.sh"
run_suite "L0 执行器"   "./test_l0.sh"
run_suite "单兵攻击"    "./test_solo.sh"
run_suite "主循环"      "./test_loop.sh"

# ── 汇总报告 ────────────────────────────────────────────
echo ""
echo "========================================"
echo "  Phase 1 验收报告"
echo "========================================"
for r in "${REPORT[@]}"; do
    IFS='|' read -r status name <<< "$r"
    if [ "$status" = "PASS" ]; then
        printf "  %-12s \033[32mPASS\033[0m\n" "$name:"
    else
        printf "  %-12s \033[31mFAIL\033[0m\n" "$name:"
    fi
done
echo "  ─────────────"

if [ "$TOTAL_FAIL" -eq 0 ]; then
    printf "  Phase 1 完成 \033[32m✅\033[0m\n"
    echo ""
    exit 0
else
    printf "  Phase 1 未通过 \033[31m❌\033[0m (%d/%d 失败)\n" "$TOTAL_FAIL" "$((TOTAL_PASS+TOTAL_FAIL))"
    echo ""
    exit 1
fi
