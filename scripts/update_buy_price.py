#!/usr/bin/env python3
"""
批量更新持仓买入价为2026年4月1日开盘价
"""

from portfolio_manager import get_portfolio_manager
from data_source import get_data_manager

manager = get_portfolio_manager()
data_source = get_data_manager()

# 获取当前持仓
portfolio = manager.list_portfolio(status='holding')
positions = portfolio['positions']

if not positions:
    print("❌ 没有找到持仓数据，请先录入持仓")
    exit()

print(f"📋 共找到 {len(positions)} 只持仓股票，开始更新买入价为2026-04-01开盘价...\n")

success_count = 0
fail_count = 0

for pos in positions:
    ts_code = pos['ts_code']
    position_id = pos['id']
    old_price = pos['buy_price']
    
    try:
        # 获取2026年4月1日的日线数据
        df, source = data_source.get_daily_quotes(ts_code, '20260401', '20260401')
        if df is not None and len(df) > 0:
            open_price = float(df.iloc[0]['open'])
            
            # 更新持仓买入价
            result = manager.update_position(position_id, buy_price=open_price)
            
            if result['success']:
                print(f"✅ {pos['name']}({ts_code}) | 旧买入价: ¥{old_price:.2f} → 新买入价: ¥{open_price:.2f} (数据源: {source})")
                success_count += 1
            else:
                print(f"❌ {pos['name']}({ts_code}) 更新失败: {result['message']}")
                fail_count += 1
        else:
            print(f"❌ {pos['name']}({ts_code}) 获取2026-04-01开盘价失败: 无数据返回")
            fail_count += 1
            
    except Exception as e:
        print(f"❌ {pos['name']}({ts_code}) 处理失败: {str(e)}")
        fail_count += 1

print(f"\n📊 更新完成：成功 {success_count} 只，失败 {fail_count} 只")
