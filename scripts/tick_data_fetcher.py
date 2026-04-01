#!/usr/bin/env python3
"""
统一的分时数据获取工具
支持获取任意时间点的价格：开盘价、11:30午市价、任意时间点价格
"""

import akshare as ak
import pandas as pd
from datetime import datetime, date, time
from typing import Optional, Tuple, Dict, Any


class TickDataFetcher:
    """分时数据获取器"""
    
    def __init__(self):
        self.today = date.today().strftime('%Y%m%d')
    
    def _convert_code(self, ts_code: str) -> str:
        """转换股票代码格式"""
        code = ts_code
        if '.' in code:
            code = code.split('.')[0]
        return code
    
    def get_tick_data(self, ts_code: str) -> Optional[pd.DataFrame]:
        """
        获取今日完整分时数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            分时数据DataFrame，失败返回None
        """
        try:
            code = self._convert_code(ts_code)
            
            df = ak.stock_zh_a_hist_min_em(
                symbol=code,
                period="1",
                start_date=self.today,
                end_date=self.today,
                adjust="qfq"
            )
            
            if df is not None and len(df) > 0:
                return df
            
        except Exception as e:
            print(f"⚠️  获取 {ts_code} 分时数据失败: {e}")
        
        return None
    
    def get_price_at_time(self, ts_code: str, target_time: str) -> Optional[float]:
        """
        获取指定时间点的价格
        
        Args:
            ts_code: 股票代码
            target_time: 目标时间，格式 "HH:MM" 或 "HH:MM:SS"
            
        Returns:
            指定时间点的价格，失败返回None
        """
        df = self.get_tick_data(ts_code)
        if df is None or len(df) == 0:
            return None
        
        if '时间' not in df.columns or '收盘' not in df.columns:
            return None
        
        # 寻找目标时间
        target_time_str = target_time
        if len(target_time_str) == 5:  # "HH:MM"
            target_time_str += ":00"
        
        # 精确匹配
        mask = df['时间'].astype(str).str.contains(target_time_str, na=False)
        matched = df[mask]
        
        if len(matched) > 0:
            return float(matched.iloc[0]['收盘'])
        
        # 如果没找到精确匹配，找最近的时间点
        print(f"⚠️  未找到精确时间 {target_time}，尝试找最近的时间点")
        
        # 尝试找目标时间前后的数据
        time_parts = target_time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # 找同一小时的数据
        hour_str = f"{hour:02d}:"
        hour_mask = df['时间'].astype(str).str.contains(hour_str, na=False)
        hour_data = df[hour_mask]
        
        if len(hour_data) > 0:
            # 返回该小时最后一条数据的价格
            return float(hour_data.iloc[-1]['收盘'])
        
        return None
    
    def get_open_price(self, ts_code: str) -> Optional[float]:
        """
        获取今日开盘价
        
        Args:
            ts_code: 股票代码
            
        Returns:
            开盘价，失败返回None
        """
        df = self.get_tick_data(ts_code)
        if df is None or len(df) == 0:
            return None
        
        if '开盘' in df.columns:
            return float(df.iloc[0]['开盘'])
        
        return None
    
    def get_1130_price(self, ts_code: str) -> Optional[float]:
        """
        获取11:30午市收盘价格
        
        Args:
            ts_code: 股票代码
            
        Returns:
            11:30价格，失败返回None
        """
        return self.get_price_at_time(ts_code, "11:30")
    
    def get_close_price(self, ts_code: str) -> Optional[float]:
        """
        获取今日收盘价格（如果已收盘）
        
        Args:
            ts_code: 股票代码
            
        Returns:
            收盘价，失败返回None
        """
        df = self.get_tick_data(ts_code)
        if df is None or len(df) == 0:
            return None
        
        if '收盘' in df.columns:
            return float(df.iloc[-1]['收盘'])
        
        return None
    
    def get_price_range(self, ts_code: str) -> Optional[Dict[str, Any]]:
        """
        获取今日价格区间信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            价格区间信息字典，失败返回None
        """
        df = self.get_tick_data(ts_code)
        if df is None or len(df) == 0:
            return None
        
        result = {}
        
        if '开盘' in df.columns:
            result['open'] = float(df.iloc[0]['开盘'])
        
        if '最高' in df.columns:
            result['high'] = float(df['最高'].max())
        
        if '最低' in df.columns:
            result['low'] = float(df['最低'].min())
        
        if '收盘' in df.columns:
            result['close'] = float(df.iloc[-1]['收盘'])
        
        price_1130 = self.get_1130_price(ts_code)
        if price_1130 is not None:
            result['close_1130'] = price_1130
        
        return result


# 便捷函数
def get_tick_data_fetcher() -> TickDataFetcher:
    """获取分时数据获取器"""
    return TickDataFetcher()


if __name__ == '__main__':
    # 测试代码
    print('测试分时数据获取器...')
    print('='*80)
    
    fetcher = get_tick_data_fetcher()
    
    test_stocks = [
        ('600115', '中国东航'),
        ('603283', '赛腾股份'),
        ('300969', '恒帅股份'),
    ]
    
    for code, name in test_stocks:
        print(f'\n{name}({code}):')
        
        # 获取开盘价
        open_price = fetcher.get_open_price(code)
        if open_price:
            print(f'  今日开盘: ¥{open_price:.2f}')
        
        # 获取11:30价格
        price_1130 = fetcher.get_1130_price(code)
        if price_1130:
            print(f'  11:30价格: ¥{price_1130:.2f}')
        
        # 获取价格区间
        price_range = fetcher.get_price_range(code)
        if price_range:
            print(f'  价格区间:')
            for key, value in price_range.items():
                print(f'    {key}: ¥{value:.2f}')
    
    print('\n' + '='*80)
    print('测试完成！')
