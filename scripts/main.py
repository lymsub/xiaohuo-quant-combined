#!/usr/bin/env python3
"""
火箭量化整合版 v2.6 - 主入口程序
整合：股票分析 + 持仓管理 + 收益跟踪 + 投资报告 + 投资机会筛选
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, date
from pathlib import Path

# 添加当前目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from database import QuantDatabase, get_db
from portfolio_manager import PortfolioManager, get_portfolio_manager, format_portfolio_table
from return_tracker import ReturnTracker, get_return_tracker, format_return_report
from investment_report import InvestmentReportGenerator, get_report_generator, format_investment_report


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def handle_portfolio_command(args):
    """处理持仓管理命令"""
    manager = get_portfolio_manager()
    
    if args.subcommand == 'list':
        print_header("📊 当前持仓")
        portfolio = manager.list_portfolio(status=args.status)
        print(format_portfolio_table(portfolio))
    
    elif args.subcommand == 'add':
        print_header("➕ 添加持仓")
        result = manager.add_stock(
            ts_code=args.code,
            buy_price=args.price,
            quantity=args.quantity,
            buy_date=args.date,
            notes=args.notes
        )
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
    
    elif args.subcommand == 'sell':
        print_header("💰 卖出持仓")
        result = manager.sell_stock(
            position_id=args.id,
            sell_price=args.price,
            sell_date=args.date,
            notes=args.notes
        )
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
    
    elif args.subcommand == 'remove':
        print_header("🗑️ 删除持仓")
        result = manager.remove_position(position_id=args.id)
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
    
    elif args.subcommand == 'summary':
        print_header("📈 持仓摘要")
        summary = manager.get_portfolio_summary()
        status_icon = "🟢" if summary['profit_status'] == 'profit' else "🔴"
        profit_str = f"+{summary['total_profit']:.2f}" if summary['total_profit'] >= 0 else f"{summary['total_profit']:.2f}"
        profit_pct_str = f"+{summary['total_profit_pct']:.2f}%" if summary['total_profit_pct'] >= 0 else f"{summary['total_profit_pct']:.2f}%"
        
        print(f"{status_icon} 持仓数: {summary['total_count']}")
        print(f"💰 总成本: ¥{summary['total_cost']:.2f}")
        print(f"📊 总市值: ¥{summary['total_market_value']:.2f}")
        print(f"📈 总收益: ¥{profit_str} ({profit_pct_str})")


def handle_return_command(args):
    """处理收益跟踪命令"""
    tracker = get_return_tracker()
    
    if args.subcommand == 'track':
        print_header("📈 收益跟踪")
        result = tracker.track_return(tracking_time=args.time)
        print(format_return_report(result))
    
    elif args.subcommand == 'history':
        print_header("📊 历史收益")
        history = tracker.get_history(limit=args.limit)
        for record in history:
            time_label = "午盘" if record['tracking_time'] == 'midday' else "收盘"
            status_icon = "🟢" if record['daily_return_pct'] >= 0 else "🔴"
            print(f"{record['tracking_date']} {time_label}: {status_icon} {record['daily_return_pct']:+.2f}% (累计: {record['total_return_pct']:+.2f}%)")


def handle_report_command(args):
    """处理投资报告命令"""
    generator = get_report_generator()
    
    if args.subcommand == 'daily':
        print_header("📄 每日投资报告")
        report = generator.generate_daily_report()
        print(format_investment_report(report))
    
    elif args.subcommand == 'midday':
        print_header("☀️ 午间报告")
        report = generator.generate_midday_report()
        print(format_investment_report(report))


def handle_opportunity_command(args):
    """处理投资机会筛选命令"""
    print_header("🎯 投资机会筛选")
    print("正在获取今日涨幅榜...")
    
    # 调用现有的涨幅榜筛选
    cmd = [sys.executable, str(SCRIPT_DIR / 'get_today_gainers.py')]
    subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    
    print("\n💡 提示：对哪只股票感兴趣？直接说 '分析股票代码' 即可！")


def handle_task_command(args):
    """处理定时任务命令"""
    print_header(f"⚡ 执行定时任务: {args.task}")
    
    if args.task == 'midday_report':
        # 午盘报告
        generator = get_report_generator()
        report = generator.generate_midday_report()
        print(format_investment_report(report))
    
    elif args.task == 'daily_report':
        # 每日报告
        generator = get_report_generator()
        report = generator.generate_daily_report()
        print(format_investment_report(report))
    
    elif args.task == 'opportunity':
        # 投资机会筛选
        handle_opportunity_command(args)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🔥 火箭量化整合版 v2.6 - 智能投资助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 股票分析
  %(prog)s analyze --code 300750 --days 90
  
  # 持仓管理
  %(prog)s portfolio list
  %(prog)s portfolio add --code 600519 --price 1800 --quantity 100
  %(prog)s portfolio sell --id 1 --price 1900
  %(prog)s portfolio summary
  
  # 收益跟踪
  %(prog)s return track --time close
  %(prog)s return history --limit 10
  
  # 投资报告
  %(prog)s report daily
  %(prog)s report midday
  
  # 投资机会
  %(prog)s opportunity
  
  # 定时任务（用于cron）
  %(prog)s task --task midday_report
  %(prog)s task --task daily_report
  %(prog)s task --task opportunity
        """
    )
    
    subparsers = parser.add_subparsers(title='命令', dest='command', help='可用命令')
    
    # ========== 股票分析命令 ==========
    analyze_parser = subparsers.add_parser('analyze', help='分析股票')
    analyze_parser.add_argument('--code', required=True, help='股票代码 (如: 300750, 600519)')
    analyze_parser.add_argument('--days', type=int, default=90, help='分析天数 (默认: 90)')
    analyze_parser.add_argument('--output', help='输出JSON文件路径')
    
    # ========== 涨幅榜命令 ==========
    gainers_parser = subparsers.add_parser('gainers', help='查看今日涨幅榜')
    
    # ========== 推荐股票命令 ==========
    recommend_parser = subparsers.add_parser('recommend', help='获取今日股票推荐')
    
    # ========== 持仓管理命令 ==========
    portfolio_parser = subparsers.add_parser('portfolio', help='持仓管理')
    portfolio_subparsers = portfolio_parser.add_subparsers(dest='subcommand', help='持仓操作')
    
    # 列出持仓
    list_parser = portfolio_subparsers.add_parser('list', help='列出持仓')
    list_parser.add_argument('--status', default='holding', choices=['holding', 'sold', 'all'], help='持仓状态 (默认: holding)')
    
    # 添加持仓
    add_parser = portfolio_subparsers.add_parser('add', help='添加持仓（买入）')
    add_parser.add_argument('--code', required=True, help='股票代码')
    add_parser.add_argument('--price', type=float, required=True, help='买入价格')
    add_parser.add_argument('--quantity', type=int, required=True, help='数量（股）')
    add_parser.add_argument('--date', help='买入日期 (默认: 今天)')
    add_parser.add_argument('--notes', help='备注')
    
    # 卖出持仓
    sell_parser = portfolio_subparsers.add_parser('sell', help='卖出持仓')
    sell_parser.add_argument('--id', type=int, required=True, help='持仓ID')
    sell_parser.add_argument('--price', type=float, help='卖出价格 (默认: 最新价)')
    sell_parser.add_argument('--date', help='卖出日期 (默认: 今天)')
    sell_parser.add_argument('--notes', help='备注')
    
    # 删除持仓
    remove_parser = portfolio_subparsers.add_parser('remove', help='删除持仓（谨慎使用）')
    remove_parser.add_argument('--id', type=int, required=True, help='持仓ID')
    
    # 持仓摘要
    summary_parser = portfolio_subparsers.add_parser('summary', help='持仓摘要')
    
    # ========== 收益跟踪命令 ==========
    return_parser = subparsers.add_parser('return', help='收益跟踪')
    return_subparsers = return_parser.add_subparsers(dest='subcommand', help='收益操作')
    
    # 跟踪收益
    track_parser = return_subparsers.add_parser('track', help='跟踪当前收益')
    track_parser.add_argument('--time', default='close', choices=['midday', 'close'], help='时间点 (默认: close)')
    
    # 历史收益
    history_parser = return_subparsers.add_parser('history', help='历史收益')
    history_parser.add_argument('--limit', type=int, default=30, help='显示记录数 (默认: 30)')
    
    # ========== 投资报告命令 ==========
    report_parser = subparsers.add_parser('report', help='投资报告')
    report_subparsers = report_parser.add_subparsers(dest='subcommand', help='报告类型')
    
    # 每日报告
    daily_report_parser = report_subparsers.add_parser('daily', help='每日投资报告')
    
    # 午间报告
    midday_report_parser = report_subparsers.add_parser('midday', help='午间报告')
    
    # ========== 投资机会命令 ==========
    opportunity_parser = subparsers.add_parser('opportunity', help='投资机会筛选')
    
    # ========== 定时任务命令 ==========
    task_parser = subparsers.add_parser('task', help='执行定时任务（用于cron）')
    task_parser.add_argument('--task', required=True, choices=['midday_report', 'daily_report', 'opportunity'], help='任务类型')
    
    # ========== 解析参数并执行 ==========
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n" + "=" * 80)
        print("  🔥 火箭量化整合版 v2.6 - 快速开始")
        print("=" * 80)
        print("\n🎯 快速使用：")
        print("  1. 分析股票:     python main.py analyze --code 300750")
        print("  2. 查看涨幅榜:   python main.py gainers")
        print("  3. 管理持仓:     python main.py portfolio --help")
        print("  4. 收益跟踪:     python main.py return --help")
        print("  5. 投资报告:     python main.py report --help")
        print("  6. 设置定时任务: ./setup_tasks.sh")
        return
    
    # 执行对应命令
    if args.command == 'analyze':
        print_header(f"📊 分析股票: {args.code}")
        cmd = [sys.executable, str(SCRIPT_DIR / 'quant_analyzer_v22.py'), '--code', args.code, '--days', str(args.days)]
        if args.output:
            cmd.extend(['--output', args.output])
        subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    
    elif args.command == 'gainers':
        print_header("🚀 今日涨幅榜")
        cmd = [sys.executable, str(SCRIPT_DIR / 'get_today_gainers.py')]
        subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    
    elif args.command == 'recommend':
        print_header("🎯 今日股票推荐")
        cmd = [sys.executable, str(SCRIPT_DIR / 'recommend_stocks.py')]
        subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    
    elif args.command == 'portfolio':
        handle_portfolio_command(args)
    
    elif args.command == 'return':
        handle_return_command(args)
    
    elif args.command == 'report':
        handle_report_command(args)
    
    elif args.command == 'opportunity':
        handle_opportunity_command(args)
    
    elif args.command == 'task':
        handle_task_command(args)


if __name__ == '__main__':
    main()
