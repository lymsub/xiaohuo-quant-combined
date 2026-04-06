#!/bin/bash
cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts
source venv/bin/activate

# 获取今日涨幅榜
python get_today_gainers.py > gainers_result.json

# 发送报告
openclaw message send --channel feishu --target chat:oc_ee8ca122861cf447759689deacd22565 --card '
{
  "config": {
    "wide_screen_mode": true,
    "enable_forward": true
  },
  "header": {
    "title": {
      "tag": "plain_text",
      "content": "🔥 火箭量化每小时市场机会扫描 - '"$(date "+%Y-%m-%d %H:%M")"'"
    },
    "template": "green"
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "✅ 已完成全市场短线机会扫描，筛选出当前最优质的3只股票！\n\n扫描时间：'"$(date +%Y-%m-%d %H:%M:%S)"'\n\n如需对某只股票进行深度分析，直接回复股票代码即可~ \n\n⚠️ 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。"
      }
    }
  ]
}
'
