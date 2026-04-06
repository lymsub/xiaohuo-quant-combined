#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券商早报自动生成 + 视频生成 + 飞书推送模块
"""
import os
import sys
import json
import time
import requests
import akshare as ak
from datetime import datetime
from typing import Dict, List, Any

from config import DOUBAN_CONFIG, FEISHU_CONFIG, MORNING_REPORT_CONFIG

# 配置
CONFIG = {
    **DOUBAN_CONFIG,
    **FEISHU_CONFIG,
    **MORNING_REPORT_CONFIG
}

class MorningReportGenerator:
    def __init__(self):
        self.report_date = datetime.now().strftime("%Y-%m-%d")
        self.data = {}
    
    def fetch_market_data(self) -> Dict[str, Any]:
        """拉取早盘市场数据"""
        print(f"[{self.report_date}] 开始拉取早盘市场数据...")
        
        try:
            # 1. 大盘指数数据
            print("拉取大盘指数...")
            # 上证指数
            sh_index = ak.stock_zh_index_spot_em()
            sh = sh_index[sh_index['代码'] == '000001'].iloc[0]
            
            # 深证成指
            sz_index = ak.stock_zh_index_spot_em()
            sz = sz_index[sz_index['代码'] == '399001'].iloc[0]
            
            # 创业板指
            cyb = sz_index[sz_index['代码'] == '399006'].iloc[0]
            
            self.data["index"] = {
                "sh": {
                    "name": "上证指数",
                    "current": round(sh['最新价'], 2),
                    "change": round(sh['涨跌幅'], 2),
                    "change_amount": round(sh['涨跌额'], 2)
                },
                "sz": {
                    "name": "深证成指",
                    "current": round(sz['最新价'], 2),
                    "change": round(sz['涨跌幅'], 2),
                    "change_amount": round(sz['涨跌额'], 2)
                },
                "cyb": {
                    "name": "创业板指",
                    "current": round(cyb['最新价'], 2),
                    "change": round(cyb['涨跌幅'], 2),
                    "change_amount": round(cyb['涨跌额'], 2)
                }
            }
            
            # 2. 涨跌家数
            print("拉取涨跌家数...")
            market_info = ak.stock_a_general_em()
            self.data["market"] = {
                "up_count": market_info['上涨家数'].iloc[0],
                "down_count": market_info['下跌家数'].iloc[0],
                "equal_count": market_info['平盘数'].iloc[0],
                "north_bound": round(market_info['北向资金'].iloc[0]/10000, 2) if '北向资金' in market_info else 0,
                "south_bound": round(market_info['南向资金'].iloc[0]/10000, 2) if '南向资金' in market_info else 0
            }
            
            # 3. 热门板块
            print("拉取热门板块...")
            board_em = ak.stock_board_concept_name_em()
            top_boards = board_em.head(5)
            self.data["hot_boards"] = []
            for _, row in top_boards.iterrows():
                self.data["hot_boards"].append({
                    "name": row['板块名称'],
                    "change": round(row['涨跌幅'], 2),
                    "lead_stock": row['领涨股票']
                })
            
            # 4. 龙虎榜数据（前一日）
            print("拉取龙虎榜数据...")
            lhb = ak.stock_lhb_detail_em(start_date=self.report_date, end_date=self.report_date)
            if not lhb.empty:
                top_lhb = lhb.head(3)
                self.data["lhb"] = []
                for _, row in top_lhb.iterrows():
                    self.data["lhb"].append({
                        "name": row['名称'],
                        "code": row['代码'],
                        "reason": row['解读']
                    })
            
            print("市场数据拉取完成！")
            return self.data
            
        except Exception as e:
            print(f"拉取市场数据失败: {e}")
            return {}
    
    def generate_report_text(self) -> str:
        """生成早报文案"""
        if not self.data:
            self.fetch_market_data()
        
        index = self.data.get("index", {})
        market = self.data.get("market", {})
        hot_boards = self.data.get("hot_boards", [])
        lhb = self.data.get("lhb", [])
        
        # 生成文案
        report = f"""各位投资者早上好！今天是{self.report_date}，欢迎收看今日券商早报。

【大盘指数】
昨日收盘：
上证指数报{index.get('sh', {}).get('current', 0)}点，涨跌幅{index.get('sh', {}).get('change', 0)}%
深证成指报{index.get('sz', {}).get('current', 0)}点，涨跌幅{index.get('sz', {}).get('change', 0)}%
创业板指报{index.get('cyb', {}).get('current', 0)}点，涨跌幅{index.get('cyb', {}).get('change', 0)}%

【市场概览】
上涨家数{market.get('up_count', 0)}家，下跌家数{market.get('down_count', 0)}家
北向资金净流入{market.get('north_bound', 0)}亿元，南向资金净流入{market.get('south_bound', 0)}亿元

【热门板块】
昨日涨幅靠前的板块有：
{''.join([f'- {board["name"]}，涨幅{board["change"]}%，领涨股{board["lead_stock"]}\n' for board in hot_boards])}
【龙虎榜动向】
昨日上榜龙虎榜的热门个股：
{''.join([f'- {stock["name"]}({stock["code"]})，{stock["reason"]}\n' for stock in lhb])}
【今日操作提示】
关注北向资金流向，以及热门板块的持续性，操作上建议控制仓位，逢低布局业绩确定性高的优质标的。

投资有风险，入市需谨慎。以上内容仅供参考，不构成投资建议。
"""
        return report
    
    def generate_video(self, report_text: str) -> str:
        """调用豆包API生成视频"""
        if not CONFIG["doubao_api_key"]:
            print("警告：未配置豆包API Key，跳过视频生成")
            return ""
        
        print("正在调用豆包API生成视频...")
        headers = {
            "Authorization": f"Bearer {CONFIG['doubao_api_key']}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
生成1分钟财经早报视频，要求：
1. 风格：{CONFIG['video_style']}
2. 时长：约{CONFIG['video_duration']}秒
3. 配音：专业男性财经主播声音
4. 内容：{report_text}
5. 画面：配合内容展示相关数据图表、K线图等元素
"""
        
        payload = {
            "model": "doubao-vid-seed-v1",
            "prompt": prompt,
            "aspect_ratio": "16:9"
        }
        
        try:
            response = requests.post(CONFIG["doubao_video_api"], headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("id"):
                video_id = result["id"]
                print(f"视频生成任务已提交，ID: {video_id}")
                
                # 轮询查询结果
                for _ in range(30):  # 最多等5分钟
                    time.sleep(10)
                    status_url = f"{CONFIG['doubao_video_api']}/{video_id}"
                    status_resp = requests.get(status_url, headers=headers)
                    status_resp.raise_for_status()
                    status_data = status_resp.json()
                    
                    if status_data.get("status") == "completed":
                        video_url = status_data.get("video_url", "")
                        print(f"视频生成完成！URL: {video_url}")
                        return video_url
                    elif status_data.get("status") == "failed":
                        print(f"视频生成失败: {status_data.get('error', '')}")
                        return ""
                
                print("视频生成超时")
                return ""
            else:
                print(f"API返回错误: {result}")
                return ""
                
        except Exception as e:
            print(f"调用豆包API失败: {e}")
            return ""
    
    def push_to_feishu(self, report_text: str, video_url: str = "") -> bool:
        """推送到飞书"""
        if not CONFIG["feishu_webhook"]:
            print("警告：未配置飞书Webhook，跳过推送")
            return False
        
        print("正在推送到飞书...")
        headers = {"Content-Type": "application/json"}
        
        # 构造消息
        content = f"🚀 【{self.report_date} 券商早报】\n\n{report_text}"
        
        if video_url:
            content += f"\n\n🎬 早报视频: {video_url}"
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        try:
            response = requests.post(CONFIG["feishu_webhook"], headers=headers, json=payload)
            response.raise_for_status()
            print("推送成功！")
            return True
        except Exception as e:
            print(f"推送到飞书失败: {e}")
            return False
    
    def run(self) -> bool:
        """执行完整流程"""
        print(f"========== {self.report_date} 券商早报生成开始 ==========")
        
        # 1. 拉取数据
        data = self.fetch_market_data()
        if not data:
            print("数据拉取失败，终止流程")
            return False
        
        # 2. 生成文案
        report_text = self.generate_report_text()
        print("\n生成的早报文案：")
        print(report_text)
        
        # 3. 生成视频（如果有API Key）
        video_url = ""
        if CONFIG["doubao_api_key"]:
            video_url = self.generate_video(report_text)
        
        # 4. 推送飞书
        self.push_to_feishu(report_text, video_url)
        
        print(f"========== {self.report_date} 券商早报生成完成 ==========")
        return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="券商早报生成工具")
    parser.add_argument("--test", action="store_true", help="测试模式：仅拉取数据生成文案，不生成视频、不推送")
    parser.add_argument("--no-video", action="store_true", help="不生成视频")
    parser.add_argument("--no-push", action="store_true", help="不推送飞书")
    args = parser.parse_args()
    
    generator = MorningReportGenerator()
    
    if args.test:
        print("【测试模式】仅生成文案")
        data = generator.fetch_market_data()
        if data:
            report = generator.generate_report_text()
            print("\n" + "="*80)
            print(report)
            print("="*80)
            print("\n✅ 测试成功！早报文案生成完成")
        else:
            print("❌ 测试失败，数据拉取失败")
    else:
        # 正常运行
        generator.run()
