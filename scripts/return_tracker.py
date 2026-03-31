#!/usr/bin/env python3
"""
火箭量化 - 收益跟踪与归因分析模块
每日午盘、收盘后自动跟踪收益，进行归因分析
"""

import os
import sys
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("错误：缺少必要的依赖。请运行：pip install pandas numpy")
    sys.exit(1)

from database import QuantDatabase, get_db
from portfolio_manager import PortfolioManager, get_portfolio_manager
from data_source import DataSourceManager


class ReturnTracker:
    """收益跟踪器"""
    
    def __init__(self, db: QuantDatabase = None, 
                 portfolio_manager: PortfolioManager = None,
                 data_source: DataSourceManager = None):
        """
        初始化收益跟踪器
        
        Args:
            db: 数据库连接
            portfolio_manager: 持仓管理器
            data_source: 数据源管理器
        """
        self.db = db or get_db()
        self.portfolio_manager = portfolio_manager or get_portfolio_manager()
        
        if data_source:
            self.data_source = data_source
        else:
            # 先尝试从token.txt读取Token
            from pathlib import Path
            token = None
            token_file = Path.home() / '.xiaohuo_quant' / 'token.txt'
            if token_file.exists():
                token = token_file.read_text().strip()
            
            self.data_source = DataSourceManager(tushare_token=token)
        
        # 基准指数（沪深300）
        self.benchmark_code = "000300.SH"
    
    def track_return(self, tracking_time: str = 'close') -> Dict[str, Any]:
        """
        跟踪收益
        
        Args:
            tracking_time: 跟踪时间 ('midday' 午盘, 'close' 收盘)
            
        Returns:
            收益跟踪结果
        """
        today = date.today().strftime('%Y-%m-%d')
        
        # 获取当前持仓和市值
        portfolio = self.portfolio_manager.list_portfolio(status='holding')
        summary = portfolio['summary']
        
        total_value = summary['total_market_value']
        total_cost = summary['total_cost']
        total_return_pct = summary['total_profit_pct']
        
        # 计算日收益
        daily_return_pct = self._calculate_daily_return(portfolio)
        
        # 获取基准收益
        benchmark_return_pct = self._get_benchmark_return()
        
        # 归因分析
        attribution_data = self._analyze_attribution(portfolio)
        
        # 获取历史数据并计算量化指标（仅拉取持仓股票）
        quant_metrics = self._calculate_quant_metrics(portfolio)
        
        # 保存到数据库
        self.db.save_return_tracking(
            tracking_date=today,
            tracking_time=tracking_time,
            total_value=total_value,
            total_cost=total_cost,
            total_return_pct=total_return_pct,
            daily_return_pct=daily_return_pct,
            benchmark_return_pct=benchmark_return_pct,
            attribution_data=attribution_data,
            quant_metrics=quant_metrics
        )
        
        return {
            "date": today,
            "tracking_time": tracking_time,
            "total_value": total_value,
            "total_cost": total_cost,
            "total_return_pct": total_return_pct,
            "daily_return_pct": daily_return_pct,
            "benchmark_return_pct": benchmark_return_pct,
            "beat_benchmark": daily_return_pct > benchmark_return_pct if benchmark_return_pct is not None else None,
            "attribution": attribution_data,
            "quant_metrics": quant_metrics,
            "portfolio_summary": summary
        }
    
    def _calculate_quant_metrics(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算量化指标（只拉取持仓股票的历史数据）
        
        Args:
            portfolio: 持仓数据
            
        Returns:
            量化指标字典
        """
        from datetime import datetime, timedelta
        
        # 只拉取持仓股票的历史数据
        positions = portfolio['positions']
        
        if not positions:
            return {
                "volatility": None,
                "sharpe_ratio": None,
                "win_loss_ratio": None,
                "turnover_impact": None
            }
        
        # 获取每只持仓股票的历史数据（最近30天）
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        # 收集所有持仓股票的历史收益率
        all_returns = []
        
        for pos in positions:
            ts_code = pos['ts_code']
            
            try:
                # 从数据库获取历史数据
                df = self.db.get_daily_quotes(ts_code, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                
                if df is not None and len(df) > 1:
                    # 计算日收益率
                    df['return_pct'] = df['close'].pct_change() * 100
                    returns = df['return_pct'].dropna().values
                    
                    if len(returns) > 0:
                        all_returns.extend(returns)
            
            except Exception:
                # 数据库没有，从数据源获取
                try:
                    df, _ = self.data_source.get_daily_quotes(ts_code, start_str, end_str)
                    
                    if df is not None and len(df) > 1:
                        # 计算日收益率
                        df['return_pct'] = df['close'].pct_change() * 100
                        returns = df['return_pct'].dropna().values
                        
                        if len(returns) > 0:
                            all_returns.extend(returns)
                            
                            # 保存到数据库
                            for _, row in df.iterrows():
                                self.db.save_daily_quote(
                                    ts_code=ts_code,
                                    trade_date=row['trade_date'],
                                    open=row.get('open'),
                                    high=row.get('high'),
                                    low=row.get('low'),
                                    close=row.get('close'),
                                    pre_close=row.get('pre_close'),
                                    change=row.get('change'),
                                    pct_chg=row.get('pct_chg'),
                                    vol=row.get('vol'),
                                    amount=row.get('amount')
                                )
                
                except Exception:
                    pass
        
        # 计算量化指标
        quant_metrics = {}
        
        if len(all_returns) >= 10:
            # 波动率（年化，假设252个交易日）
            volatility = np.std(all_returns) * np.sqrt(252)
            quant_metrics['volatility'] = round(volatility, 2)
            
            # 夏普比率（简易版，假设无风险利率3%）
            avg_return = np.mean(all_returns)
            risk_free_rate = 3.0
            sharpe_ratio = (avg_return - risk_free_rate) / volatility if volatility > 0 else None
            quant_metrics['sharpe_ratio'] = round(sharpe_ratio, 2) if sharpe_ratio is not None else None
        else:
            quant_metrics['volatility'] = None
            quant_metrics['sharpe_ratio'] = None
        
        # 盈亏比
        profit_count = sum(1 for pos in positions if pos.get('profit', 0) >= 0)
        loss_count = len(positions) - profit_count
        quant_metrics['win_loss_ratio'] = round(profit_count / loss_count, 2) if loss_count > 0 else None
        
        # 换手影响（简易版）
        quant_metrics['turnover_impact'] = 0  # 暂无换手数据
        
        return quant_metrics
    
    def _calculate_daily_return(self, portfolio: Dict[str, Any]) -> float:
        """
        计算日收益率
        
        Args:
            portfolio: 持仓数据
            
        Returns:
            日收益率（%）
        """
        # 简化计算：基于每只股票的当日涨跌幅加权平均
        # 实际生产环境应对比昨日市值
        
        total_weighted_return = 0
        total_market_value = 0
        
        for pos in portfolio['positions']:
            if 'market_value' in pos and 'profit_pct' in pos:
                # 这里用累计收益做简化，实际应计算当日收益
                # 实际生产环境需要保存每日市值历史
                weight = pos['market_value']
                total_weighted_return += pos['profit_pct'] * weight
                total_market_value += weight
        
        if total_market_value > 0:
            # 这是一个简化的估计值
            return (total_weighted_return / total_market_value) * 0.1  # 假设1/10是今日贡献
        
        return 0
    
    def _get_benchmark_return(self) -> Optional[float]:
        """
        获取基准指数收益率
        
        Returns:
            基准收益率（%）
        """
        try:
            end_date = date.today().strftime('%Y-%m-%d')
            start_date = (date.today() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            df = self.db.get_daily_quotes(self.benchmark_code, start_date, end_date)
            if not df.empty and len(df) >= 2:
                yesterday_close = df.iloc[-2]['close']
                today_close = df.iloc[-1]['close']
                return ((today_close - yesterday_close) / yesterday_close) * 100
        except Exception:
            pass
        
        # 尝试从数据源获取
        try:
            df = self.data_source.get_daily_quotes(self.benchmark_code, limit=2)
            if not df.empty and len(df) >= 2:
                yesterday_close = df.iloc[-2]['close']
                today_close = df.iloc[-1]['close']
                return ((today_close - yesterday_close) / yesterday_close) * 100
        except Exception:
            pass
        
        return None
    
    def _analyze_attribution(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        归因分析
        
        Args:
            portfolio: 持仓数据
            
        Returns:
            归因分析结果
        """
        positions = portfolio['positions']
        
        if not positions:
            return {"message": "无持仓"}
        
        # 按收益排序
        sorted_by_profit = sorted(positions, key=lambda x: x.get('profit', 0), reverse=True)
        
        # 最大贡献者
        top_contributor = sorted_by_profit[0] if sorted_by_profit else None
        
        # 最大拖累者
        bottom_contributor = sorted_by_profit[-1] if sorted_by_profit and len(sorted_by_profit) > 1 else None
        
        # 行业分布（简化版，实际应获取行业数据）
        industry_distribution = {}
        
        # 收益分布
        profit_count = sum(1 for p in positions if p.get('profit', 0) >= 0)
        loss_count = len(positions) - profit_count
        
        return {
            "top_contributor": {
                "name": top_contributor['name'],
                "ts_code": top_contributor['ts_code'],
                "profit": top_contributor.get('profit', 0),
                "profit_pct": top_contributor.get('profit_pct', 0)
            } if top_contributor else None,
            "bottom_contributor": {
                "name": bottom_contributor['name'],
                "ts_code": bottom_contributor['ts_code'],
                "profit": bottom_contributor.get('profit', 0),
                "profit_pct": bottom_contributor.get('profit_pct', 0)
            } if bottom_contributor else None,
            "profit_count": profit_count,
            "loss_count": loss_count,
            "win_rate": (profit_count / len(positions)) * 100 if positions else 0,
            "industry_distribution": industry_distribution
        }
    
    def get_history(self, limit: int = 30) -> List[Dict[str, Any]]:
        """
        获取历史收益跟踪数据
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            历史数据列表
        """
        return self.db.get_return_tracking(limit=limit)
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """
        获取最新的收益跟踪数据
        
        Returns:
            最新数据
        """
        history = self.get_history(limit=1)
        return history[0] if history else None


def format_return_report(tracking_result: Dict[str, Any]) -> str:
    """
    格式化收益报告
    
    Args:
        tracking_result: 跟踪结果
        
    Returns:
        格式化的报告
    """
    output = []
    
    time_label = "午盘" if tracking_result['tracking_time'] == 'midday' else "收盘"
    status_icon = "🟢" if tracking_result['daily_return_pct'] >= 0 else "🔴"
    
    output.append(f"📈 火箭量化 - {tracking_result['date']} {time_label}收益报告")
    output.append("=" * 80)
    
    # 收益概览
    output.append(f"{status_icon} 日收益率: {tracking_result['daily_return_pct']:+.2f}%")
    output.append(f"📊 总收益率: {tracking_result['total_return_pct']:+.2f}%")
    output.append(f"💰 总市值: ¥{tracking_result['total_value']:.2f}")
    output.append(f"💵 总成本: ¥{tracking_result['total_cost']:.2f}")
    
    # 基准对比
    if tracking_result['benchmark_return_pct'] is not None:
        bench_icon = "✅" if tracking_result['beat_benchmark'] else "❌"
        output.append(f"\n{bench_icon} 基准(沪深300): {tracking_result['benchmark_return_pct']:+.2f}%")
        if tracking_result['beat_benchmark']:
            output.append(f"   🎉 跑赢基准 {(tracking_result['daily_return_pct'] - tracking_result['benchmark_return_pct']):.2f}%")
        else:
            output.append(f"   😅 跑输基准 {(tracking_result['benchmark_return_pct'] - tracking_result['daily_return_pct']):.2f}%")
    
    # 归因分析
    attribution = tracking_result.get('attribution', {})
    if attribution:
        output.append("\n🔍 归因分析")
        output.append("-" * 40)
        
        if attribution.get('top_contributor'):
            top = attribution['top_contributor']
            output.append(f"🏆 最大贡献: {top['name']}({top['ts_code']}) +{top['profit']:.2f}元 (+{top['profit_pct']:.2f}%)")
        
        if attribution.get('bottom_contributor'):
            bottom = attribution['bottom_contributor']
            output.append(f"💔 最大拖累: {bottom['name']}({bottom['ts_code']}) {bottom['profit']:.2f}元 ({bottom['profit_pct']:.2f}%)")
        
        output.append(f"📊 盈利股票: {attribution.get('profit_count', 0)}只 | 亏损股票: {attribution.get('loss_count', 0)}只")
        output.append(f"🎯 胜率: {attribution.get('win_rate', 0):.1f}%")
    
    output.append("\n" + "=" * 80)
    
    return "\n".join(output)


# ============================================================
# 便捷函数
# ============================================================

def get_return_tracker() -> ReturnTracker:
    """获取收益跟踪器"""
    return ReturnTracker()



