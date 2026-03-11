#!/bin/bash
# test_llm.sh — LLM 基础设施验证
# 用法: bash test_llm.sh

set -e
cd "$(dirname "$0")"

PASS=0
FAIL=0

check() {
    local desc="$1"
    shift
    echo -n "  $desc ... "
    if "$@" > /dev/null 2>&1; then
        echo "PASS"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== LLM 基础设施测试 ==="

# Test 1: dry-run 模式返回预设 JSON
echo "[Test 1] dry-run 模式"
OUTPUT=$(python src/main.py llm_test --dry-run 2>&1)
echo -n "  返回包含 instructions ... "
if echo "$OUTPUT" | grep -q "instructions"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    echo "  输出: $OUTPUT"
    FAIL=$((FAIL + 1))
fi

echo -n "  返回包含 OK ... "
if echo "$OUTPUT" | grep -q "\[OK\]"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    echo "  输出: $OUTPUT"
    FAIL=$((FAIL + 1))
fi

# Test 2: 真实 API 连通性（配置中已有 key 则测试连通，否则验证优雅失败）
echo "[Test 2] API 连通性 / 无 key 优雅失败"
echo -n "  llm_test 正常退出或报错退出 ... "
RESULT=$(python src/main.py llm_test 2>&1 || true)
if echo "$RESULT" | grep -q "\[OK\]\|\[FAIL\]"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    echo "  输出: $RESULT"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== 结果: $PASS passed, $FAIL failed ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
