#!/usr/bin/env python3
"""
双数据源管理器
支持 Tushare 和 AkShare 作为数据源，形成互补
"""

import os
import sys
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class DataSourceManager:
    """双数据源管理器"""
    
    # 数据源优先级
    SOURCE_PRIORITY = ['tushare', 'akshare']
    
    # 数据源能力
    SOURCE_CAPABILITIES = {
        'tushare': {
            'stock_list': True,
            'daily_quotes': True,
            'financial_indicators': True,  # 需要高级权限
            'stock_basic': True,
        },
        'akshare': {
            'stock_list': True,
            'daily_quotes': True,
            'financial_indicators': False,  # AkShare 可能没有
            'stock_basic': True,
        }
    }
    
    def __init__(self, tushare_token: Optional[str] = None, 
                 preferred_source: str = 'tushare',
                 enable_fallback: bool = True):
        """
        初始化数据源管理器
        
        Args:
            tushare_token: Tushare Token
            preferred_source: 首选数据源 ('tushare' 或 'akshare')
            enable_fallback: 是否启用备用数据源
        """
        self.tushare_token = tushare_token
        self.preferred_source = preferred_source
        self.enable_fallback = enable_fallback
        
        # 初始化数据源
        self.tushare_available = False
        self.akshare_available = False
        self.tushare_pro = None
        self.akshare = None
        
        self._init_sources()
    
    def _init_sources(self):
        """初始化数据源"""
        # 尝试初始化 Tushare（只有当有 token 时才初始化）
        if self.tushare_token and self.tushare_token.strip() and self.tushare_token != "dummy_token_for_akshare":
            try:
                import tushare as ts
                ts.set_token(self.tushare_token)
                self.tushare_pro = ts.pro_api()
                self.tushare_available = True
                print(f"✅ Tushare 数据源已初始化")
            except Exception as e:
                print(f"⚠️  Tushare 初始化失败: {e}")
        else:
            print(f"ℹ️  未提供 Tushare Token，跳过 Tushare 初始化")
        
        # 尝试初始化 AkShare
        try:
            import akshare as ak
            self.akshare = ak
            self.akshare_available = True
            print(f"✅ AkShare 数据源已初始化")
        except Exception as e:
            print(f"⚠️  AkShare 初始化失败: {e}")
    
    def get_available_sources(self) -> list:
        """获取可用的数据源列表"""
        available = []
        if self.tushare_available:
            available.append('tushare')
        if self.akshare_available:
            available.append('akshare')
        return available
    
    def get_stock_list(self, source: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
        """
        获取股票列表
        
        Args:
            source: 指定数据源，None则自动选择
            
        Returns:
            (DataFrame, 使用的数据源名称)
        """
        sources = self._get_source_order(source, 'stock_list')
        
        for src in sources:
            try:
                if src == 'tushare':
                    df = self._get_stock_list_tushare()
                    return df, 'tushare'
                elif src == 'akshare':
                    df = self._get_stock_list_akshare()
                    return df, 'akshare'
            except Exception as e:
                print(f"⚠️  {src} 获取股票列表失败: {e}")
                continue
        
        raise Exception("所有数据源都无法获取股票列表")
    
    def get_daily_quotes(self, ts_code: str, start_date: str, end_date: str,
                         source: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
        """
        获取日线行情
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            source: 指定数据源，None则自动选择
            
        Returns:
            (DataFrame, 使用的数据源名称)
        """
        sources = self._get_source_order(source, 'daily_quotes')
        
        for src in sources:
            try:
                if src == 'tushare':
                    df = self._get_daily_quotes_tushare(ts_code, start_date, end_date)
                    return df, 'tushare'
                elif src == 'akshare':
                    df = self._get_daily_quotes_akshare(ts_code, start_date, end_date)
                    return df, 'akshare'
            except Exception as e:
                print(f"⚠️  {src} 获取日线行情失败: {e}")
                continue
        
        raise Exception(f"所有数据源都无法获取 {ts_code} 的日线行情")
    
    def _get_source_order(self, specified_source: Optional[str], 
                         capability: str) -> list:
        """
        获取数据源使用顺序
        
        Args:
            specified_source: 指定的数据源
            capability: 需要的能力
            
        Returns:
            数据源顺序列表
        """
        if specified_source:
            # 如果指定了数据源，只检查该数据源是否可用且有该能力
            if specified_source == 'tushare' and self.tushare_available:
                if self.SOURCE_CAPABILITIES['tushare'].get(capability, False):
                    return ['tushare']
            elif specified_source == 'akshare' and self.akshare_available:
                if self.SOURCE_CAPABILITIES['akshare'].get(capability, False):
                    return ['akshare']
            raise Exception(f"指定的数据源 {specified_source} 不可用或不支持 {capability}")
        
        # 自动选择数据源
        order = []
        
        # 首先尝试首选数据源
        if self.preferred_source == 'tushare' and self.tushare_available:
            if self.SOURCE_CAPABILITIES['tushare'].get(capability, False):
                order.append('tushare')
        elif self.preferred_source == 'akshare' and self.akshare_available:
            if self.SOURCE_CAPABILITIES['akshare'].get(capability, False):
                order.append('akshare')
        
        # 如果启用备用数据源，添加其他可用数据源
        if self.enable_fallback:
            for src in self.SOURCE_PRIORITY:
                if src not in order:
                    available = (src == 'tushare' and self.tushare_available) or \
                               (src == 'akshare' and self.akshare_available)
                    if available and self.SOURCE_CAPABILITIES[src].get(capability, False):
                        order.append(src)
        
        if not order:
            raise Exception(f"没有可用的数据源支持 {capability}")
        
        return order
    
    # ============================================
    # Tushare 数据源实现
    # ============================================
    
    def _get_stock_list_tushare(self) -> pd.DataFrame:
        """从 Tushare 获取股票列表"""
        df = self.tushare_pro.stock_basic(exchange='', list_status='L', 
                                          fields='ts_code,symbol,name,area,industry,market,list_date')
        return df
    
    def _get_daily_quotes_tushare(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从 Tushare 获取日线行情"""
        df = self.tushare_pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            df = df.sort_values('trade_date')
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        return df
    
    # ============================================
    # AkShare 数据源实现
    # ============================================
    
    def _get_stock_list_akshare(self) -> pd.DataFrame:
        """从 AkShare 获取股票列表"""
        df = self.akshare.stock_info_a_code_name()
        # 转换为 Tushare 兼容格式
        df = df.rename(columns={'code': 'symbol', 'name': 'name'})
        df['ts_code'] = df['symbol'].apply(self._convert_to_ts_code)
        return df
    
    def _get_daily_quotes_akshare(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从 AkShare 获取日线行情"""
        # 转换股票代码格式
        symbol = self._convert_from_ts_code(ts_code)
        
        # 转换日期格式
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        start_str = start_dt.strftime('%Y%m%d')
        end_str = end_dt.strftime('%Y%m%d')
        
        df = self.akshare.stock_zh_a_hist_tx(symbol=symbol, start_date=start_str, end_date=end_str)
        
        if df is not None and not df.empty:
            # 转换为 Tushare 兼容格式
            df = df.rename(columns={
                'date': 'trade_date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'amount': 'amount'
            })
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df['ts_code'] = ts_code
            
            # 计算额外字段（模仿 Tushare）
            if len(df) > 1:
                df['pre_close'] = df['close'].shift(1)
                df['change'] = df['close'] - df['pre_close']
                df['pct_chg'] = df['change'] / df['pre_close'] * 100
        
        return df
    
    def _convert_to_ts_code(self, symbol: str) -> str:
        """转换为 Tushare 格式的股票代码"""
        symbol = str(symbol)
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith(('8', '4')):
            return f"{symbol}.BJ"
        else:
            return f"{symbol}.SZ"
    
    def _convert_from_ts_code(self, ts_code: str) -> str:
        """从 Tushare 格式转换回普通格式"""
        if '.' in ts_code:
            return ts_code.split('.')[0]
        return ts_code


# ============================================
# 便捷函数
# ============================================

def get_data_manager(tushare_token: Optional[str] = None, 
                    preferred_source: str = 'tushare',
                    enable_fallback: bool = True) -> DataSourceManager:
    """获取数据源管理器"""
    return DataSourceManager(tushare_token, preferred_source, enable_fallback)


if __name__ == '__main__':
    print("="*80)
    print("🚀 测试双数据源管理器")
    print("="*80)
    
    # 尝试加载 Token
    token = None
    token_file = Path.home() / '.xiaohuo_quant' / 'token.txt'
    if token_file.exists():
        token = token_file.read_text().strip()
    
    # 创建数据源管理器
    mgr = get_data_manager(token, preferred_source='tushare', enable_fallback=True)
    
    print(f"\n📊 可用数据源: {mgr.get_available_sources()}")
    
    # 测试获取股票列表
    print("\n1️⃣  测试获取股票列表...")
    try:
        df_list, source = mgr.get_stock_list()
        print(f"✅ 成功从 {source} 获取 {len(df_list)} 只股票")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试获取日线行情
    print("\n2️⃣  测试获取日线行情...")
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        df_hist, source = mgr.get_daily_quotes('600519.SH', start_date, end_date)
        print(f"✅ 成功从 {source} 获取 {len(df_hist)} 条日线数据")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)
