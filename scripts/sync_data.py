#!/usr/bin/env python3
"""
小火量化 - 数据同步脚本
定时从 Tushare 获取行情和基本面数据并存储到 SQLite 数据库
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("错误：缺少必要的依赖。请运行：pip install pandas numpy")
    sys.exit(1)

try:
    import tushare as ts
except ImportError:
    print("错误：缺少 tushare。请运行：pip install tushare")
    sys.exit(1)

from database import QuantDatabase


class DataSyncer:
    """数据同步器"""
    
    def __init__(self, tushare_token: str):
        self.token = tushare_token
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
        self.db = QuantDatabase()
    
    def sync_stock_list(self) -> int:
        """同步股票列表"""
        print("📋 正在同步股票列表...")
        try:
            df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date,is_hs')
            if df is not None and not df.empty:
                count = self.db.save_stock_basic(df)
                print(f"✅ 同步了 {count} 只股票信息")
                return count
            return 0
        except Exception as e:
            print(f"❌ 同步股票列表失败: {e}")
            return 0
    
    def sync_daily_quotes(self, ts_code: str, days: int = 365) -> int:
        """
        同步单只股票的日线数据
        
        Args:
            ts_code: 股票代码
            days: 同步天数
            
        Returns:
            保存的记录数
        """
        try:
            # 获取上次同步日期
            last_sync = self.db.get_sync_status('daily', ts_code)
            
            end_date = datetime.now()
            if last_sync:
                # 从上次同步日期的下一天开始
                start_date = datetime.strptime(last_sync, '%Y-%m-%d') + timedelta(days=1)
                # 最多同步指定天数
                if (end_date - start_date).days > days:
                    start_date = end_date - timedelta(days=days)
            else:
                # 首次同步，获取指定天数的数据
                start_date = end_date - timedelta(days=days)
            
            # 格式化日期
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            # 如果开始日期大于结束日期，说明已经是最新的了
            if start_date > end_date:
                print(f"⏭️  {ts_code} 已经是最新数据")
                return 0
            
            # 获取数据
            df = self.pro.daily(ts_code=ts_code, start_date=start_str, end_date=end_str)
            
            if df is not None and not df.empty:
                df = df.sort_values('trade_date')
                df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                count = self.db.save_daily_quotes(ts_code, df)
                print(f"✅ {ts_code}: 同步了 {count} 条日线数据 ({start_str} 至 {end_str})")
                return count
            else:
                print(f"ℹ️  {ts_code}: 没有新数据 ({start_str} 至 {end_str})")
                return 0
                
        except Exception as e:
            print(f"❌ {ts_code}: 同步失败 - {e}")
            return 0
    
    def sync_multiple_stocks(self, ts_codes: list, days: int = 365) -> dict:
        """
        同步多只股票的数据
        
        Args:
            ts_codes: 股票代码列表
            days: 同步天数
            
        Returns:
            同步统计字典
        """
        stats = {
            'total': len(ts_codes),
            'success': 0,
            'failed': 0,
            'total_records': 0
        }
        
        print(f"\n🚀 开始同步 {len(ts_codes)} 只股票的数据...\n")
        
        for i, ts_code in enumerate(ts_codes, 1):
            print(f"[{i}/{len(ts_codes)}] ", end="")
            count = self.sync_daily_quotes(ts_code, days)
            if count >= 0:
                stats['success'] += 1
                stats['total_records'] += count
            else:
                stats['failed'] += 1
        
        return stats
    
    def sync_financial_indicators(self, ts_code: str, periods: int = 10) -> int:
        """
        同步单只股票的财务指标
        
        Args:
            ts_code: 股票代码
            periods: 获取的期数（默认10期）
            
        Returns:
            保存的记录数
        """
        try:
            print(f"📊 同步 {ts_code} 财务指标...")
            
            # 获取财务指标
            df = self.pro.fina_indicator(ts_code=ts_code)
            
            if df is not None and not df.empty:
                # 只保留最近的 periods 期
                if len(df) > periods:
                    df = df.head(periods)
                
                count = self.db.save_financial_indicators(ts_code, df)
                print(f"✅ {ts_code}: 同步了 {count} 条财务指标")
                return count
            else:
                print(f"ℹ️  {ts_code}: 没有财务指标数据")
                return 0
                
        except Exception as e:
            print(f"❌ {ts_code}: 同步财务指标失败 - {e}")
            return -1
    
    def sync_multiple_financial(self, ts_codes: list, periods: int = 10) -> dict:
        """
        同步多只股票的财务指标
        
        Args:
            ts_codes: 股票代码列表
            periods: 每只股票获取的期数
            
        Returns:
            同步统计字典
        """
        stats = {
            'total': len(ts_codes),
            'success': 0,
            'failed': 0,
            'total_records': 0
        }
        
        print(f"\n🚀 开始同步 {len(ts_codes)} 只股票的财务指标...\n")
        
        for i, ts_code in enumerate(ts_codes, 1):
            print(f"[{i}/{len(ts_codes)}] ", end="")
            count = self.sync_financial_indicators(ts_code, periods)
            if count >= 0:
                stats['success'] += 1
                stats['total_records'] += count
            else:
                stats['failed'] += 1
        
        return stats
    
    def sync_all_stocks(self, days: int = 30, batch_size: int = 100) -> dict:
        """
        同步所有股票的数据（慎用，API调用次数多）
        
        Args:
            days: 同步天数
            batch_size: 每批处理的股票数
            
        Returns:
            同步统计字典
        """
        # 先同步股票列表
        self.sync_stock_list()
        
        # 获取所有股票代码
        stock_df = self.db.get_stock_basic()
        if stock_df.empty:
            print("❌ 没有股票数据")
            return {'total': 0, 'success': 0, 'failed': 0, 'total_records': 0}
        
        ts_codes = stock_df['ts_code'].tolist()
        return self.sync_multiple_stocks(ts_codes, days)
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _load_token_from_store() -> str:
    """从存储中加载 Token"""
    token = os.getenv('TUSHARE_TOKEN')
    if token:
        return token
    
    config_dir = Path.home() / '.xiaohuo_quant'
    env_file = config_dir / 'token.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if 'TUSHARE_TOKEN' in line and '=' in line:
                value = line.split('=', 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ['TUSHARE_TOKEN'] = value
                    return value
    
    token_file = config_dir / 'token.txt'
    if token_file.exists():
        value = token_file.read_text().strip()
        if value:
            os.environ['TUSHARE_TOKEN'] = value
            return value
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='小火量化 - 数据同步工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 同步单只股票最近一年的数据
  python sync_data.py --code 300919
  
  # 同步多只股票
  python sync_data.py --codes 300919,600519,000001
  
  # 同步所有股票最近30天的数据（慎用）
  python sync_data.py --all --days 30
  
  # 同步股票列表
  python sync_data.py --stock-list
  
  # 同步单只股票的财务指标
  python sync_data.py --financial --code 300919
  
  # 同步多只股票的财务指标
  python sync_data.py --financial --codes 300919,600519
        """
    )
    
    parser.add_argument('--token', type=str, 
                        help='Tushare Token（也可设置TUSHARE_TOKEN环境变量）')
    parser.add_argument('--code', type=str, 
                        help='单只股票代码')
    parser.add_argument('--codes', type=str, 
                        help='多只股票代码，用逗号分隔')
    parser.add_argument('--all', action='store_true',
                        help='同步所有股票（慎用，API调用次数多）')
    parser.add_argument('--stock-list', action='store_true',
                        help='只同步股票列表')
    parser.add_argument('--days', type=int, default=365,
                        help='同步天数（默认365天）')
    parser.add_argument('--stats', action='store_true',
                        help='显示数据库统计信息')
    parser.add_argument('--financial', action='store_true',
                        help='同步财务指标（而非日线行情）')
    parser.add_argument('--periods', type=int, default=10,
                        help='财务指标期数（默认10期）')
    
    args = parser.parse_args()
    
    # 获取token
    token = args.token or _load_token_from_store()
    if not token and not args.stats:
        print("❌ 错误：请提供Tushare Token（--token参数或TUSHARE_TOKEN环境变量）")
        print("获取Token：https://tushare.pro/register")
        sys.exit(1)
    
    # 只显示统计信息
    if args.stats:
        with QuantDatabase() as db:
            stats = db.get_stats()
            print("\n" + "="*60)
            print("📊 数据库统计信息")
            print("="*60)
            print(f"📈 日线数据量: {stats['daily_quotes_count']:,} 条")
            print(f"📋 股票信息数: {stats['stock_basic_count']:,} 只")
            print(f"📊 财务指标数: {stats['financial_indicators_count']:,} 条")
            print(f"🔢 唯一股票数（行情）: {stats['unique_stocks']:,} 只")
            print(f"🔢 唯一股票数（财务）: {stats['unique_financial_stocks']:,} 只")
            print(f"📅 日期范围: {stats['date_range'][0]} 至 {stats['date_range'][1]}")
            print(f"📁 数据库路径: {stats['db_path']}")
            print("="*60 + "\n")
        return
    
    # 执行同步
    with DataSyncer(token) as syncer:
        if args.stock_list:
            syncer.sync_stock_list()
        
        elif args.financial:
            # 同步财务指标
            if args.code:
                # 标准化股票代码
                ts_code = args.code
                if not ts_code.endswith(('.SZ', '.SH', '.BJ')):
                    if ts_code.startswith('6'):
                        ts_code = ts_code + '.SH'
                    elif ts_code.startswith(('8', '4')):
                        ts_code = ts_code + '.BJ'
                    else:
                        ts_code = ts_code + '.SZ'
                
                syncer.sync_financial_indicators(ts_code, args.periods)
            
            elif args.codes:
                code_list = args.codes.split(',')
                ts_codes = []
                for code in code_list:
                    code = code.strip()
                    if not code.endswith(('.SZ', '.SH', '.BJ')):
                        if code.startswith('6'):
                            code = code + '.SH'
                        elif code.startswith(('8', '4')):
                            code = code + '.BJ'
                        else:
                            code = code + '.SZ'
                    ts_codes.append(code)
                
                stats = syncer.sync_multiple_financial(ts_codes, args.periods)
                print(f"\n📊 财务指标同步完成: {stats['success']}/{stats['total']} 成功, "
                      f"共 {stats['total_records']} 条记录")
        
        else:
            # 同步日线行情（默认）
            if args.code:
                # 标准化股票代码
                ts_code = args.code
                if not ts_code.endswith(('.SZ', '.SH', '.BJ')):
                    if ts_code.startswith('6'):
                        ts_code = ts_code + '.SH'
                    elif ts_code.startswith(('8', '4')):
                        ts_code = ts_code + '.BJ'
                    else:
                        ts_code = ts_code + '.SZ'
                
                syncer.sync_daily_quotes(ts_code, args.days)
            
            elif args.codes:
                code_list = args.codes.split(',')
                ts_codes = []
                for code in code_list:
                    code = code.strip()
                    if not code.endswith(('.SZ', '.SH', '.BJ')):
                        if code.startswith('6'):
                            code = code + '.SH'
                        elif code.startswith(('8', '4')):
                            code = code + '.BJ'
                        else:
                            code = code + '.SZ'
                    ts_codes.append(code)
                
                stats = syncer.sync_multiple_stocks(ts_codes, args.days)
                print(f"\n📊 同步完成: {stats['success']}/{stats['total']} 成功, "
                      f"共 {stats['total_records']} 条记录")
            
            elif args.all:
                confirm = input(f"⚠️  警告：同步所有股票会调用大量API，确定继续吗？(yes/no): ")
                if confirm.lower() == 'yes':
                    stats = syncer.sync_all_stocks(args.days)
                    print(f"\n📊 同步完成: {stats['success']}/{stats['total']} 成功, "
                          f"共 {stats['total_records']} 条记录")
                else:
                    print("❌ 已取消")


if __name__ == '__main__':
    main()
