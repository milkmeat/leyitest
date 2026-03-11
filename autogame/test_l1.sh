#!/bin/bash
# test_l1.sh — L1 小队队长验证
# 用法: bash test_l1.sh [--mock]

set -e
cd "$(dirname "$0")"

MOCK_FLAG="--mock"

PASS=0
FAIL=0

# 用 python 检查输出中是否包含指定关键字（避免 Windows 编码问题）
py_contains() {
    local keyword="$1"
    python -c "
import sys
data = sys.stdin.buffer.read().decode('utf-8', errors='replace')
sys.exit(0 if '$keyword' in data else 1)
"
}

echo "=== L1 小队队长测试 ==="

# Test 1: l1_decide dry-run 生成指令
echo "[Test 1] l1_decide --dry-run"
OUTPUT_FILE=$(mktemp)
python src/main.py $MOCK_FLAG l1_decide 1 --dry-run > "$OUTPUT_FILE" 2>&1 || true

echo -n "  生成指令 ... "
if cat "$OUTPUT_FILE" | py_contains "SCOUT"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    cat "$OUTPUT_FILE"
    FAIL=$((FAIL + 1))
fi
rm -f "$OUTPUT_FILE"

# Test 2: l1_decide --json 输出结构
echo "[Test 2] l1_decide --dry-run --json"
OUTPUT=$(python src/main.py $MOCK_FLAG l1_decide 1 --dry-run --json 2>&1 || true)

echo -n "  包含 action ... "
if echo "$OUTPUT" | grep -q "action"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "  包含 uid ... "
if echo "$OUTPUT" | grep -q "uid"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Test 3: 无效 squad_id
echo "[Test 3] 无效 squad_id"
echo -n "  squad_id=999 报错 ... "
RESULT=$(python src/main.py $MOCK_FLAG l1_decide 999 --dry-run 2>&1 || true)
if echo "$RESULT" | grep -q "FAIL"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    echo "  输出: $RESULT"
    FAIL=$((FAIL + 1))
fi

# Test 4: 主循环 run --once --dry-run
echo "[Test 4] run --once --dry-run"
OUTPUT_FILE=$(mktemp)
python src/main.py $MOCK_FLAG run --once --dry-run --loop.interval_seconds 0 > "$OUTPUT_FILE" 2>&1 || true

echo -n "  主循环完成 ... "
if cat "$OUTPUT_FILE" | py_contains "AIController"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    cat "$OUTPUT_FILE"
    FAIL=$((FAIL + 1))
fi

echo -n "  L1 生成指令 ... "
if cat "$OUTPUT_FILE" | py_contains "[L1]"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    cat "$OUTPUT_FILE"
    FAIL=$((FAIL + 1))
fi
rm -f "$OUTPUT_FILE"

echo ""
echo "=== 结果: $PASS passed, $FAIL failed ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
