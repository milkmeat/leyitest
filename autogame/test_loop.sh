#!/bin/bash
# test_loop.sh — 主循环集成测试
#
# 测试 AIController 主循环: 5 阶段编排 + 日志输出
#
# 用法:
#   ./test_loop.sh                    # 默认 test 环境
#   ./test_loop.sh --mock             # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

# 确保 Python 输出 UTF-8（Windows 兼容）
export PYTHONIOENCODING=utf-8

# ── 配置 ────────────────────────────────────────────────
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

cli() {
    $CMD $ENV_FLAG "$@" 2>&1
}

show_cmd() {
    echo "  执行: $CMD ${ENV_FLAG:+$ENV_FLAG }$*"
}

show_output() {
    local first_line
    first_line=$(echo "$1" | head -1)
    if [ ${#first_line} -gt 120 ]; then
        first_line="${first_line:0:120}..."
    fi
    local total_lines
    total_lines=$(echo "$1" | wc -l)
    if [ "$total_lines" -gt 1 ]; then
        echo "  输出: ${first_line}  (共${total_lines}行)"
    else
        echo "  输出: ${first_line}"
    fi
}

check_contains() {
    local name="$1" keyword="$2" output="$3"
    local matched
    matched=$(echo "$output" | grep -m1 "$keyword" || true)
    if [ -n "$matched" ]; then
        if [ ${#matched} -gt 100 ]; then
            matched="${matched:0:100}..."
        fi
        printf "  [\033[32mPASS\033[0m] %s → %s\n" "$name" "$matched"
        ((PASS++))
        RESULTS+=("PASS|$name|$matched")
    else
        printf "  [\033[31mFAIL\033[0m] %s: 输出中未找到 \"%s\"\n" "$name" "$keyword"
        ((FAIL++))
        RESULTS+=("FAIL|$name|未找到 \"$keyword\"")
    fi
}

# ── 清理旧日志 ────────────────────────────────────────────
rm -f logs/loop_*.json 2>/dev/null

# ── 开始测试 ────────────────────────────────────────────

echo "主循环集成测试 (AIController)"
echo "  ENV:  ${ENV_FLAG:-test}"

# ==============================================================
# Test 1: 单轮运行
# ==============================================================
echo ""
echo "=================================================="
echo "Test 1: 单轮运行 (--once)"
echo "=================================================="

show_cmd "run --once --loop.interval_seconds 0"
OUTPUT=$(cli run --once --loop.interval_seconds 0)
EXIT_CODE=$?
show_output "$OUTPUT"

check_contains "loop #1 标记" "loop #1" "$OUTPUT"
check_contains "账号同步" "账号" "$OUTPUT"

if [ "$EXIT_CODE" -eq 0 ]; then
    printf "  [\033[32mPASS\033[0m] 退出码 → 0\n"
    ((PASS++))
    RESULTS+=("PASS|退出码|0")
else
    printf "  [\033[31mFAIL\033[0m] 退出码 → %d (期望 0)\n" "$EXIT_CODE"
    ((FAIL++))
    RESULTS+=("FAIL|退出码|$EXIT_CODE")
fi

# ==============================================================
# Test 2: 多轮运行
# ==============================================================
echo ""
echo "=================================================="
echo "Test 2: 多轮运行 (--rounds 2)"
echo "=================================================="

show_cmd "run --rounds 2 --loop.interval_seconds 0"
OUTPUT2=$(cli run --rounds 2 --loop.interval_seconds 0)
EXIT_CODE2=$?
show_output "$OUTPUT2"

check_contains "loop #2 标记" "loop #2" "$OUTPUT2"

if [ "$EXIT_CODE2" -eq 0 ]; then
    printf "  [\033[32mPASS\033[0m] 退出码 → 0\n"
    ((PASS++))
    RESULTS+=("PASS|多轮退出码|0")
else
    printf "  [\033[31mFAIL\033[0m] 退出码 → %d (期望 0)\n" "$EXIT_CODE2"
    ((FAIL++))
    RESULTS+=("FAIL|多轮退出码|$EXIT_CODE2")
fi

# ==============================================================
# Test 3: 阶段耗时输出
# ==============================================================
echo ""
echo "=================================================="
echo "Test 3: 阶段耗时标记"
echo "=================================================="

# 复用 OUTPUT2
check_contains "[sync] 标记" "\\[sync\\]" "$OUTPUT2"
check_contains "[L2] 标记" "\\[L2\\]" "$OUTPUT2"
check_contains "[L1] 标记" "\\[L1\\]" "$OUTPUT2"
check_contains "[action] 标记" "\\[action\\]" "$OUTPUT2"

# ==============================================================
# Test 4: stub 标记
# ==============================================================
echo ""
echo "=================================================="
echo "Test 4: stub 标记"
echo "=================================================="

check_contains "stub 关键词" "stub" "$OUTPUT2"

# ==============================================================
# Test 5: 日志文件
# ==============================================================
echo ""
echo "=================================================="
echo "Test 5: 日志文件"
echo "=================================================="

if ls logs/loop_*.json 1>/dev/null 2>&1; then
    LOG_COUNT=$(ls logs/loop_*.json | wc -l)
    printf "  [\033[32mPASS\033[0m] 日志文件 → 找到 %d 个 JSON 文件\n" "$LOG_COUNT"
    ((PASS++))
    RESULTS+=("PASS|日志文件|找到 ${LOG_COUNT} 个 JSON 文件")

    # 验证 JSON 合法性
    FIRST_LOG=$(ls logs/loop_*.json | head -1)
    if python -m json.tool "$FIRST_LOG" > /dev/null 2>&1; then
        printf "  [\033[32mPASS\033[0m] JSON 合法性 → %s 验证通过\n" "$FIRST_LOG"
        ((PASS++))
        RESULTS+=("PASS|JSON 合法性|$FIRST_LOG 验证通过")
    else
        printf "  [\033[31mFAIL\033[0m] JSON 合法性 → %s 验证失败\n" "$FIRST_LOG"
        ((FAIL++))
        RESULTS+=("FAIL|JSON 合法性|$FIRST_LOG 验证失败")
    fi
else
    printf "  [\033[31mFAIL\033[0m] 日志文件 → logs/ 目录下无 JSON 文件\n"
    ((FAIL++))
    RESULTS+=("FAIL|日志文件|logs/ 目录下无 JSON 文件")
fi

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
