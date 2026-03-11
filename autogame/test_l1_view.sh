#!/bin/bash
# test_l1_view.sh — L1 局部视图验证
# 用法: bash test_l1_view.sh [--mock]

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

echo "=== L1 局部视图测试 ==="

# Test 1: 文本模式
echo "[Test 1] 文本模式"
OUTPUT_FILE=$(mktemp)
python src/main.py $MOCK_FLAG l1_view 1 > "$OUTPUT_FILE" 2>&1 || true

for kw in "Alpha" "uid=" "type="; do
    echo -n "  包含 '$kw' ... "
    if cat "$OUTPUT_FILE" | py_contains "$kw"; then
        echo "PASS"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        FAIL=$((FAIL + 1))
    fi
done
rm -f "$OUTPUT_FILE"

# Test 2: JSON 模式
echo "[Test 2] JSON 模式"
OUTPUT=$(python src/main.py $MOCK_FLAG l1_view 1 --json 2>&1 || true)

for kw in "squad_id" "members" "enemies" "buildings"; do
    echo -n "  包含 '$kw' ... "
    if echo "$OUTPUT" | grep -q "$kw"; then
        echo "PASS"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        FAIL=$((FAIL + 1))
    fi
done

# Test 3: 无效 squad_id
echo "[Test 3] 无效 squad_id"
echo -n "  squad_id=999 报错 ... "
RESULT=$(python src/main.py $MOCK_FLAG l1_view 999 2>&1 || true)
if echo "$RESULT" | grep -q "FAIL"; then
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
