#!/bin/bash
# 小火量化 - 轻量安装脚本
# 仅负责：创建虚拟环境 + 调用 config.py 配置向导
# config.py 负责：安装依赖 + 配置 Token + 其他配置

set -e

echo ""
echo "========================================================================"
echo "              🔥 小火量化 - 轻量安装脚本"
echo "========================================================================"
echo ""

# 项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📍 项目目录: $PROJECT_DIR"
echo "📍 脚本目录: $SCRIPT_DIR"
echo ""

# 检查 Python
echo "🔍 检查 Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ Python3 已安装"
PYTHON_BIN="$(which python3)"
echo "   路径: $PYTHON_BIN"
echo ""

# 创建虚拟环境
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 正在创建独立 Python 环境..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    echo "✅ 虚拟环境已创建: $VENV_DIR"
else
    echo "✅ 虚拟环境已存在: $VENV_DIR"
fi
echo ""

# 设置脚本权限
echo "🔧 设置脚本权限..."
chmod +x "$SCRIPT_DIR"/*.py 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
echo "✅ 权限已设置"
echo ""

# 运行配置向导（config.py 负责安装依赖、配置 Token 等）
echo "🚀 运行配置向导（config.py）..."
echo "   config.py 将自动安装依赖、配置 Token 等..."
echo ""
"$VENV_DIR/bin/python" "$SCRIPT_DIR/config.py"
echo ""

# 完成
echo "========================================================================"
echo "              ✅ 小火量化安装完成！"
echo "========================================================================"
echo ""
echo "📋 分工说明："
echo "  • install.sh - 轻量安装：创建虚拟环境 + 调用 config.py"
echo "  • config.py  - 配置管理：安装依赖 + 配置 Token + 其他配置"
echo ""
echo "🚀 快速开始："
echo ""
echo "1. 分析个股："
echo "   cd $SCRIPT_DIR"
echo "   ./venv/bin/python quant_analyzer_v22.py --code 600519"
echo ""
echo "2. 今日涨幅榜："
echo "   cd $SCRIPT_DIR"
echo "   ./venv/bin/python get_today_gainers.py"
echo ""
echo "3. 推荐股票："
echo "   cd $SCRIPT_DIR"
echo "   ./venv/bin/python recommend_stocks.py"
echo ""
echo "4. 检查配置："
echo "   cd $SCRIPT_DIR"
echo "   ./venv/bin/python config.py --check"
echo ""
echo "========================================================================"
echo ""
