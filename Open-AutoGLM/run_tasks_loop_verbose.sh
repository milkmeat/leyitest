#!/bin/bash

# 循环执行手机任务的脚本（详细输出版本）
# 用法: ./run_tasks_loop_verbose.sh [循环次数] [等待时间(秒)]

# 默认配置
DEFAULT_ITERATIONS=5
DEFAULT_WAIT_TIME=10

# 获取参数
ITERATIONS=${1:-$DEFAULT_ITERATIONS}
WAIT_TIME=${2:-$DEFAULT_WAIT_TIME}

# 任务指令
TASK_COMMAND="/phone 查看任务提示栏，完成第一个任务并领取奖励"

# 日志文件
LOG_FILE="task_loop_$(date +%Y%m%d_%H%M%S).log"
DETAILED_LOG_FILE="task_loop_detailed_$(date +%Y%m%d_%H%M%S).log"
RAW_OUTPUT_DIR="task_loop_outputs_$(date +%Y%m%d_%H%M%S)"

# 创建输出目录
mkdir -p "$RAW_OUTPUT_DIR"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 打印带颜色的消息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo -e "${MAGENTA}[====]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查 Claude Code CLI 是否可用
check_claude_cli() {
    log_debug "正在检查 Claude Code CLI..."
    if ! command -v claude &> /dev/null; then
        log_error "Claude Code CLI 未找到，请确保已安装并在 PATH 中"
        log_error "Claude 命令路径: $(which claude 2>&1 || echo '未找到')"
        exit 1
    fi
    local claude_path=$(which claude)
    log_info "✓ Claude Code CLI 已找到: $claude_path"
}

# 检查 jq 命令（用于解析 JSON）
check_jq() {
    if ! command -v jq &> /dev/null; then
        log_warn "未找到 jq 命令，将无法生成可读格式日志"
        log_warn "建议安装 jq: sudo apt-get install jq"
        return 1
    fi
    log_debug "✓ 找到 jq 命令"
    return 0
}

# 执行单次任务
run_task() {
    local iteration=$1
    local start_time=$(date +%s)
    local task_output_file="$RAW_OUTPUT_DIR/task_${iteration}.log"

    log_section "========================================="
    log_section "第 $iteration/$ITERATIONS 次任务执行"
    log_section "========================================="
    log_info "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_debug "任务命令: $TASK_COMMAND"
    log_debug "输出文件: $task_output_file"
    log_section "-----------------------------------------"

    # 写入任务头信息到详细日志
    {
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "第 $iteration 次任务执行"
        echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "命令: $TASK_COMMAND"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    } >> "$DETAILED_LOG_FILE"

    log_info "开始执行 Claude Code 任务 (详细模式)..."
    log_debug "使用 --print --output-format stream-json --verbose 模式"
    echo ""

    # 使用 Claude Code 的详细输出模式
    # --print: 非交互式模式
    # --output-format stream-json: 流式 JSON 输出，包含所有工具调用
    # --verbose: 显示详细信息
    local exit_code=0
    local json_output_file="$RAW_OUTPUT_DIR/task_${iteration}_json.log"
    local readable_output_file="$RAW_OUTPUT_DIR/task_${iteration}_readable.log"

    # 执行命令并保存 JSON 输出
    echo "$TASK_COMMAND" | claude --model sonnet --print --output-format stream-json --verbose 2>&1 | tee "$json_output_file" | while IFS= read -r line; do
        # 实时显示并解析 JSON
        echo "$line"

        # 尝试提取关键信息并格式化显示（可选）
        if echo "$line" | jq -e '.type == "assistant" and .message.content[0].type == "tool_use"' &>/dev/null; then
            local tool_name=$(echo "$line" | jq -r '.message.content[0].name // empty')
            if [ -n "$tool_name" ]; then
                echo -e "${CYAN}  → 工具调用: $tool_name${NC}" >&2
            fi
        fi
    done

    exit_code=${PIPESTATUS[1]}

    # 同时生成可读版本（从 JSON 提取主要内容）
    log_debug "生成可读版本日志..."
    {
        echo "=== 任务执行摘要 ==="
        echo ""

        # 提取工具调用
        echo "🔧 工具调用:"
        jq -r 'select(.type == "assistant" and .message.content[0].type == "tool_use") | "  • " + .message.content[0].name + ": " + (.message.content[0].input.description // .message.content[0].input.command // "")' "$json_output_file" 2>/dev/null || echo "  (无法解析)"

        echo ""
        echo "📊 最终结果:"
        jq -r 'select(.type == "result") | .result' "$json_output_file" 2>/dev/null || echo "  (无法解析)"

        echo ""
        echo "📈 统计信息:"
        jq -r 'select(.type == "result") | "  • 执行时长: " + (.duration_ms | tostring) + " ms\n  • API 时长: " + (.duration_api_ms | tostring) + " ms\n  • 回合数: " + (.num_turns | tostring) + "\n  • 总成本: $" + (.total_cost_usd | tostring)' "$json_output_file" 2>/dev/null || echo "  (无法解析)"

    } > "$readable_output_file"

    # 将两种格式都追加到详细日志
    {
        echo "=== JSON 格式输出 ==="
        cat "$json_output_file"
        echo ""
        echo "=== 可读格式摘要 ==="
        cat "$readable_output_file"
    } >> "$DETAILED_LOG_FILE"

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 从JSON输出的result行中提取任务名称（如"将1号起居室升至3级"）
    local task_name=$(jq -r 'select(.type == "result") | .result' "$json_output_file" 2>/dev/null | grep -oP '完成.*?任务[：:]\s*"?\K[^"]+(?=")' | head -n 1)

    # 如果提取失败，设为未识别
    if [ -z "$task_name" ]; then
        task_name="未识别"
    fi

    # 保存任务信息到文件（用于后续汇总）
    echo "${iteration}|${task_name}|${duration}" >> "$RAW_OUTPUT_DIR/task_summary.log"

    # 写入任务尾信息到详细日志
    {
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "第 $iteration 次任务执行结束"
        echo "任务名称: $task_name"
        echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "执行耗时: ${duration} 秒"
        echo "退出码: $exit_code"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    } >> "$DETAILED_LOG_FILE"

    echo ""
    log_section "-----------------------------------------"
    log_info "任务名称: $task_name"
    log_info "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "执行耗时: ${duration} 秒"

    if [ $exit_code -eq 0 ]; then
        log_info "✓ 第 $iteration 次任务执行成功"
    else
        log_error "✗ 第 $iteration 次任务执行失败 (退出码: $exit_code)"
        return $exit_code
    fi

    return 0
}

# 主函数
main() {
    local script_start_time=$(date +%s)

    clear
    log_section "╔═══════════════════════════════════════════╗"
    log_section "║    Claude Code 任务循环执行脚本 (详细版)    ║"
    log_section "╚═══════════════════════════════════════════╝"
    echo ""
    log_info "启动时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "工作目录: $(pwd)"
    log_info "循环次数: $ITERATIONS"
    log_info "等待时间: $WAIT_TIME 秒"
    log_info "任务指令: $TASK_COMMAND"
    log_section "-----------------------------------------"
    log_info "日志文件:"
    log_info "  • 简要日志: $LOG_FILE"
    log_info "  • 详细日志: $DETAILED_LOG_FILE"
    log_info "  • 原始输出: $RAW_OUTPUT_DIR/"
    log_section "-----------------------------------------"

    # 检查 CLI
    check_claude_cli

    # 检查 jq
    check_jq

    # 显示 Claude 版本信息
    log_debug "检查 Claude Code 版本..."
    local version_info=$(claude --version 2>&1 | head -n 1)
    log_info "Claude 版本: $version_info"
    log_info "输出模式: --print --output-format stream-json --verbose"
    log_section "========================================="
    echo ""

    # 循环执行任务
    local success_count=0
    local fail_count=0

    # 声明数组用于保存任务信息
    declare -a task_names
    declare -a task_durations
    declare -a task_statuses

    for ((i=1; i<=ITERATIONS; i++)); do
        echo ""
        log_section "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"
        log_section "┃        任务 $i / $ITERATIONS"
        log_section "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        echo ""

        if run_task $i; then
            ((success_count++))
            echo ""
            log_info "═══════════════════════════════════════"
            log_info "✓ ✓ ✓  任务 $i 成功完成  ✓ ✓ ✓"
            log_info "═══════════════════════════════════════"
        else
            ((fail_count++))
            echo ""
            log_error "═══════════════════════════════════════"
            log_error "✗ ✗ ✗  任务 $i 执行失败  ✗ ✗ ✗"
            log_error "═══════════════════════════════════════"
            log_warn "继续执行下一个任务..."
        fi

        # 如果不是最后一次，等待指定时间
        if [ $i -lt $ITERATIONS ]; then
            echo ""
            log_info "⏳ 等待 $WAIT_TIME 秒后执行下一次任务..."
            for ((j=WAIT_TIME; j>0; j--)); do
                printf "\r   ${CYAN}⏳ 倒计时: %2d 秒...${NC}  " $j
                sleep 1
            done
            echo -e "\r   ${GREEN}✓ 等待完成${NC}         "
        fi
    done

    local script_end_time=$(date +%s)
    local total_duration=$((script_end_time - script_start_time))
    local minutes=$(($total_duration / 60))
    local seconds=$(($total_duration % 60))

    # 计算成功率
    local total_tasks=$((success_count + fail_count))
    local success_rate=0
    if [ $total_tasks -gt 0 ]; then
        success_rate=$(awk "BEGIN {printf \"%.1f\", ($success_count / $total_tasks) * 100}")
    fi

    # 统计结果
    echo ""
    echo ""
    log_section "╔═══════════════════════════════════════════╗"
    log_section "║          任务循环执行完成                 ║"
    log_section "╚═══════════════════════════════════════════╝"
    echo ""
    log_info "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "总执行时间: $total_duration 秒 ($minutes 分 $seconds 秒)"
    log_section "-----------------------------------------"
    log_info "执行统计:"
    log_info "  • 总执行次数: $total_tasks"
    log_info "  • ✓ 成功次数: $success_count"
    log_info "  • ✗ 失败次数: $fail_count"
    log_info "  • 成功率: $success_rate%"
    log_section "-----------------------------------------"

    # 打印任务详情汇总
    if [ -f "$RAW_OUTPUT_DIR/task_summary.log" ]; then
        log_info "📋 任务详情汇总:"
        echo ""
        {
            printf "%-5s | %-40s | %-8s\n" "序号" "任务名称" "耗时(秒)"
            echo "------|------------------------------------------|----------"
            while IFS='|' read -r idx name duration; do
                printf "%-5s | %-40s | %-8s\n" "$idx" "${name:0:40}" "$duration"
            done < "$RAW_OUTPUT_DIR/task_summary.log"
        } | tee -a "$LOG_FILE"
        echo ""
    fi

    log_section "-----------------------------------------"
    log_info "日志文件位置:"
    log_info "  • 简要日志: $LOG_FILE"
    log_info "  • 详细日志: $DETAILED_LOG_FILE"
    log_info "  • 原始输出目录: $RAW_OUTPUT_DIR/"
    log_info "  • 任务汇总: $RAW_OUTPUT_DIR/task_summary.log"
    log_section "========================================="
    echo ""

    # 显示快速查看命令
    log_debug "快速查看命令:"
    log_debug "  查看详细日志: less $DETAILED_LOG_FILE"
    log_debug "  查看单个任务: cat $RAW_OUTPUT_DIR/task_N.log"
    log_debug "  查看所有任务: ls -lh $RAW_OUTPUT_DIR/"
    echo ""
}

# 捕获 Ctrl+C
trap 'echo ""; log_warn "收到中断信号，正在退出..."; exit 130' INT TERM

# 执行主函数
main

exit 0
