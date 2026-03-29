
#!/usr/bin/env python3
"""
用 AkShare 实时行情接口获取今日涨幅榜
高效、快速、无频率限制

优化版本：
- 增加交易日检查
- 增加数据时效性验证
- 更好的错误处理
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import pandas as pd
except ImportError:
    print("错误：缺少 pandas。请运行：pip install pandas")
    sys.exit(1)

try:
    import akshare as ak
except ImportError:
    print("错误：缺少 akshare。请运行：pip install akshare")
    sys.exit(1)


def is_trading_day() -> tuple[bool, str]:
    """
    检查今天是否是交易日
    
    Returns:
        (is_trading, message)
    """
    now = datetime.now()
    weekday = now.weekday()  # 0=周一, 5=周六, 6=周日
    
    # 检查是否是周末
    if weekday >= 5:
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return False, f"今天是{day_names[weekday]}（{now.strftime('%Y-%m-%d')}），A股周末休市"
    
    # TODO: 可以增加节假日检查
    return True, "今天是交易日"


def check_data_timeliness(df: pd.DataFrame) -> tuple[bool, str]:
    """
    检查数据的时效性
    
    Args:
        df: 股票数据DataFrame
        
    Returns:
        (is_fresh, message)
    """
    # 检查是否有时间列
    if '时间' in df.columns:
        # 尝试解析时间
        try:
            time_samples = df['时间'].dropna().head(10).tolist()
            if time_samples:
                # 简单检查：如果有时间列，说明可能是实时数据
                return True, f"数据包含时间信息，样本: {time_samples[0]}"
        except:
            pass
    
    # 检查涨跌停数量（如果有大量20%涨跌停，可能是真实交易日数据）
    try:
        def clean_pct(x):
            try:
                if isinstance(x, str):
                    x = x.replace('%', '').strip()
                return float(x)
            except:
                return 0.0
        
        pct_values = df['涨跌幅'].apply(clean_pct)
        limit_up_count = len(pct_values[(pct_values >= 19.9) & (pct_values <= 20.1)])
        
        if limit_up_count > 0:
            return True, f"数据包含{limit_up_count}只20%涨跌停股票，可能是真实交易日数据"
    except:
        pass
    
    # 默认警告
    return False, "无法确认数据时效性，请谨慎参考"


def get_today_gainers(n: int = 10):
    """
    获取今日涨幅榜
    
    Args:
        n: 返回前n只
    """
    print("="*80)
    print("📊 A股行情查询")
    print("="*80)
    
    # 首先检查是否是交易日
    is_trading, trading_msg = is_trading_day()
    print(f"\n📅 {trading_msg}")
    
    if not is_trading:
        print("\n💡 提示：")
        print("   - A股交易时间：周一至周五 9:30-11:30, 13:00-15:00")
        print("   - 周末和法定节假日休市")
        print("   - 您可以选择分析历史数据或等待交易日")
        
        # 询问用户是否继续（非交互模式下直接返回）
        print("\n" + "="*80)
        print("⚠️  警告：当前非交易日，数据可能是历史缓存数据")
        print("="*80)
    
    # 获取实时行情
    print("\n📈 从 AkShare 获取行情数据...")
    try:
        # 使用 AkShare 的东方财富网-沪深京 A 股-实时行情接口
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            print("❌ 没有获取到行情数据")
            return None
        
        print(f"✅ 成功获取 {len(df)} 只股票的行情数据")
        
    except Exception as e:
        print(f"❌ 获取行情数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 检查数据时效性
    is_fresh, fresh_msg = check_data_timeliness(df)
    if not is_fresh:
        print(f"\n⚠️  {fresh_msg}")
    else:
        print(f"\n✅ {fresh_msg}")
    
    # 检查必需的列
    required_columns = ['代码', '名称', '最新价', '涨跌幅']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ 缺少必需的列: {missing_columns}")
        print(f"   可用列: {list(df.columns)}")
        return None
    
    # 清理数据
    print("\n🧹 清理数据...")
    
    # 转换涨跌幅为数值
    def clean_pct_change(x):
        try:
            if isinstance(x, str):
                x = x.replace('%', '').strip()
            return float(x)
        except:
            return 0.0
    
    df['涨跌幅数值'] = df['涨跌幅'].apply(clean_pct_change)
    
    # 按涨跌幅降序排序
    df_sorted = df.sort_values('涨跌幅数值', ascending=False)
    
    # 显示前n只
    print("\n" + "="*80)
    if is_trading and is_fresh:
        print(f"🏆 今日涨幅榜 - 前{n}只")
    else:
        print(f"🏆 涨幅榜（数据时效性待确认）- 前{n}只")
    print("="*80)
    
    top_n = df_sorted.head(n)
    
    # 格式化输出
    print(f"\n{'排名':<6} {'代码':<12} {'名称':<10} {'最新价':<10} {'涨跌幅':<12} {'成交量':<12}")
    print("-"*80)
    
    for i, (_, row) in enumerate(top_n.iterrows(), 1):
        name = str(row['名称'])[:8] if pd.notna(row['名称']) else str(row['代码'])
        change_pct = row['涨跌幅数值']
        change_emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
        
        # 获取成交量（如果有的话）
        volume = row.get('成交量', '-')
        if volume != '-':
            try:
                volume = f"{int(volume):,}"
            except:
                pass
        
        # 获取最新价
        latest_price = row.get('最新价', '-')
        if latest_price != '-':
            try:
                latest_price = f"{float(latest_price):.2f}"
            except:
                pass
        
        print(f"{i:<6} {row['代码']:<12} {name:<10} {latest_price:<10} {change_emoji} {change_pct:>+7.2f}% {volume:<12}")
    
    print("-"*80)
    
    # 保存结果
    output_file = Path(__file__).parent / f"today_gainers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_sorted.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 完整结果已保存到: {output_file}")
    
    # 显示提示信息
    if not is_trading or not is_fresh:
        print("\n" + "="*80)
        print("⚠️  重要提示")
        print("="*80)
        if not is_trading:
            print("   - 当前非交易日，数据可能是历史缓存")
        if not is_fresh:
            print("   - 数据时效性无法确认")
        print("   - 请谨慎参考以上数据")
        print("="*80)
    
    return df_sorted


if __name__ == '__main__':
    result = get_today_gainers(n=10)
    if result is None:
        sys.exit(1)
