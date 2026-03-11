#!/bin/bash
# test_sync.sh — 数据同步集成测试
#
# 测试 data_sync 模块：并发账号同步 + 地图解析
#
# 用法:
#   ./test_sync.sh                    # 默认 test 环境
#   ./test_sync.sh --mock             # mock 环境

set -uo pipefail
cd "$(dirname "$0")"

# 确保 Python 输出 UTF-8（Windows 兼容）
export PYTHONIOENCODING=utf-8

# ── 配置 ────────────────────────────────────────────────
TEST_UID=20010366
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

# 执行 CLI 命令，显示命令和首行输出，返回全部 stdout
cli() {
    $CMD $ENV_FLAG "$@" 2>&1
}

# 显示执行的命令
show_cmd() {
    echo "  执行: $CMD ${ENV_FLAG:+$ENV_FLAG }$*"
}

# 显示输出（截断至最多一行，超长截断到120字符）
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

# 检查输出包含指定关键词
check_contains() {
    local name="$1" keyword="$2" output="$3"
    # 提取匹配行（取第一行匹配）
    local matched
    matched=$(echo "$output" | grep -m1 "$keyword" || true)
    if [ -n "$matched" ]; then
        # 截断匹配行
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

# ── 开始测试 ────────────────────────────────────────────

echo "数据同步集成测试 (DataSync)"
echo "  UID:  $TEST_UID"
echo "  ENV:  ${ENV_FLAG:-test}"

# ==============================================================
# Test 1: sync 基础 — 命令执行成功，输出含摘要
# ==============================================================
echo ""
echo "=================================================="
echo "Test 1: sync 全量同步"
echo "=================================================="

show_cmd "sync"
OUTPUT=$(cli sync)
show_output "$OUTPUT"
check_contains "同步完成" "同步完成" "$OUTPUT"
check_contains "账号数量" "账号:" "$OUTPUT"
check_contains "建筑数量" "建筑:" "$OUTPUT"
check_contains "敌方数量" "敌方:" "$OUTPUT"

# ==============================================================
# Test 2: 单账号 sync
# ==============================================================
echo ""
echo "=================================================="
echo "Test 2: sync 单账号"
echo "=================================================="

show_cmd "sync $TEST_UID"
SINGLE_OUTPUT=$(cli sync $TEST_UID)
show_output "$SINGLE_OUTPUT"
check_contains "单账号同步" "同步完成" "$SINGLE_OUTPUT"
check_contains "坐标信息" "坐标" "$SINGLE_OUTPUT"
check_contains "兵种信息" "兵种" "$SINGLE_OUTPUT"

# ==============================================================
# Test 3: JSON 输出 — 合法 JSON + 包含关键字段
# ==============================================================
echo ""
echo "=================================================="
echo "Test 3: sync --json"
echo "=================================================="

show_cmd "sync --json"
JSON_OUTPUT=$(cli sync --json)
# 显示 JSON 首行
show_output "$JSON_OUTPUT"

# 验证 JSON 合法性
if echo "$JSON_OUTPUT" | python -m json.tool > /dev/null 2>&1; then
    printf "  [\033[32mPASS\033[0m] JSON 合法性 → python -m json.tool 验证通过\n"
    ((PASS++))
    RESULTS+=("PASS|JSON 合法性|python -m json.tool 验证通过")
else
    printf "  [\033[31mFAIL\033[0m] JSON 合法性 → python -m json.tool 验证失败\n"
    ((FAIL++))
    RESULTS+=("FAIL|JSON 合法性|python -m json.tool 验证失败")
fi

# 用 python 提取关键字段计数
SUMMARY=$(echo "$JSON_OUTPUT" | python -c "
import sys, json
d = json.load(sys.stdin)
print(f\"accounts={len(d.get('accounts',{}))} buildings={len(d.get('buildings',[]))} enemies={len(d.get('enemies',[]))} errors={len(d.get('errors',[]))}\")
" 2>&1)
echo "  解析: $SUMMARY"
check_contains "JSON 含 accounts" "accounts=" "$SUMMARY"

# ==============================================================
# Test 4: 单账号 JSON
# ==============================================================
echo ""
echo "=================================================="
echo "Test 4: sync <uid> --json"
echo "=================================================="

show_cmd "sync $TEST_UID --json"
SINGLE_JSON=$(cli sync $TEST_UID --json)
show_output "$SINGLE_JSON"

# 验证含 uid 字段
if echo "$SINGLE_JSON" | python -c "import sys,json; d=json.load(sys.stdin); assert d.get('uid')==$TEST_UID" 2>/dev/null; then
    printf "  [\033[32mPASS\033[0m] 单账号 JSON → uid=%s 匹配\n" "$TEST_UID"
    ((PASS++))
    RESULTS+=("PASS|单账号 JSON|uid=$TEST_UID 匹配")
else
    printf "  [\033[31mFAIL\033[0m] 单账号 JSON → uid 不匹配或 JSON 非法\n"
    ((FAIL++))
    RESULTS+=("FAIL|单账号 JSON|uid 不匹配或 JSON 非法")
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
