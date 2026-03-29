#!/bin/bash
# 小火量化 - 定时任务设置脚本
# 用于设置每天定时同步数据的 cron 任务

set -e

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="/root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts/venv"
SYNC_SCRIPT="/root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts/sync_data.py"

# 要同步的股票列表（可自定义）
STOCK_CODES=${1:-"300919,600519,000001"}

# 定时任务时间（默认：每个交易日下午 15:30）
CRON_TIME=${2:-"30 15 * * 1-5"}

echo "🚀 小火量化 - 定时任务设置"
echo "================================"

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ 虚拟环境不存在，请先运行 install.sh"
    exit 1
fi

# 检查同步脚本
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "❌ 同步脚本不存在: $SYNC_SCRIPT"
    exit 1
fi

# 获取 Python 解释器路径
PYTHON_BIN="$VENV_DIR/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Python 解释器不存在: $PYTHON_BIN"
    exit 1
fi

# 检查 Token
TOKEN_FILE="$HOME/.xiaohuo_quant/token.txt"
if [ ! -f "$TOKEN_FILE" ]; then
    echo "⚠️  Token 文件不存在，请先配置 Tushare Token"
    echo "   方式1: 设置环境变量 TUSHARE_TOKEN"
    echo "   方式2: 将 Token 保存到 $TOKEN_FILE"
    echo ""
    read -p "是否继续设置定时任务？(yes/no): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 已取消"
        exit 1
    fi
fi

# 构建 cron 命令
CRON_CMD="$CRON_TIME cd $PROJECT_DIR && $PYTHON_BIN $SYNC_SCRIPT --codes $STOCK_CODES >> $HOME/.xiaohuo_quant/sync.log 2>&1"

echo ""
echo "📋 定时任务配置:"
echo "   项目目录: $PROJECT_DIR"
echo "   股票列表: $STOCK_CODES"
echo "   执行时间: $CRON_TIME"
echo "   日志文件: $HOME/.xiaohuo_quant/sync.log"
echo ""
echo "📝 Cron 命令:"
echo "   $CRON_CMD"
echo ""

# 创建日志目录
mkdir -p "$HOME/.xiaohuo_quant"

# 询问是否添加到 crontab
read -p "是否添加到 crontab？(yes/no): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 检查是否已存在相同的任务
    (crontab -l 2>/dev/null || true) | grep -F "$SYNC_SCRIPT" && {
        echo ""
        echo "⚠️  检测到已存在的定时任务，正在移除..."
        (crontab -l 2>/dev/null || true) | grep -v "$SYNC_SCRIPT" | crontab -
    }
    
    # 添加新任务
    (crontab -l 2>/dev/null || true; echo "$CRON_CMD") | crontab -
    
    echo ""
    echo "✅ 定时任务已添加到 crontab！"
    echo ""
    echo "📋 当前 crontab:"
    crontab -l
    echo ""
    echo "📖 常用命令:"
    echo "   查看任务: crontab -l"
    echo "   编辑任务: crontab -e"
    echo "   查看日志: tail -f $HOME/.xiaohuo_quant/sync.log"
else
    echo ""
    echo "⏭️  已跳过，你可以手动添加以下命令到 crontab:"
    echo ""
    echo "$CRON_CMD"
    echo ""
fi

echo ""
echo "✅ 设置完成！"
