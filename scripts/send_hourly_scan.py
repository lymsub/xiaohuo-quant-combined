#!/usr/bin/env python3
"""发送每小时市场扫描报告"""

import json
import os
import subprocess
import glob
from datetime import datetime

# 切换到脚本目录
os.chdir('/root/.openclaw/workspace/skills/xiaohuo-quant-secretary/scripts')

# 获取最新涨幅榜文件
csv_files = sorted(glob.glob('today_gainers_*.csv'), key=os.path.getmtime, reverse=True)
if not csv_files:
    print("No gainers file found")
    exit(1)

latest_file = csv_files[0]
print(f"Using file: {latest_file}")

# 读取前3只股票
stocks = []
with open(latest_file, 'r', encoding='utf-8') as f:
    header = f.readline()  # 跳过标题
    for i, line in enumerate(f):
        if i >= 3:
            break
        parts = line.strip().split(',')
        if len(parts) >= 5:
            code = parts[0].strip('"')
            name = parts[1].strip('"')
            price = parts[2].strip('"')
            change_pct = parts[3].strip('"')
            
            # 涨跌幅颜色
            try:
                pct = float(change_pct)
                emoji = "🟢" if pct > 0 else "🔴" if pct < 0 else "⚪"
            except:
                emoji = "⚪"
            
            stocks.append(f"{emoji} **{name}** ({code}) ¥{price} {change_pct}%")

# 构建股票内容
if stocks:
    stock_content = "\n".join([f">{s}" for s in stocks])
else:
    stock_content = ">⚠️ 暂无数据，请稍后重试"

scan_time = datetime.now().strftime('%Y-%m-%d %H:%M')

# 构建卡片消息
card = {
    "config": {
        "wide_screen_mode": True,
        "enable_forward": True
    },
    "header": {
        "title": {
            "tag": "plain_text",
            "content": f"🔥 高客秘书每小时市场机会扫描 - {scan_time}"
        },
        "template": "green"
    },
    "elements": [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"✅ 已完成全市场短线机会扫描，筛选出当前最优质的3只股票！\n\n{stock_content}\n\n扫描时间：{scan_time}\n\n如需对某只股票进行深度分析，直接回复股票代码即可~\n\n⚠️ 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。"
            }
        }
    ]
}

card_json = json.dumps(card, ensure_ascii=False)
print(card_json)

# 发送消息
cmd = [
    'openclaw', 'message', 'send',
    '--channel', 'feishu',
    '--target', 'chat:oc_407a74081dd85d531ca4426ab3d7f71a',
    '--card', card_json
]

result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
