#!/bin/bash
cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts
source venv/bin/activate

# 生成午盘数据
python -c "
from portfolio_manager import get_portfolio_manager
from return_tracker import get_return_tracker
import json

manager = get_portfolio_manager()
portfolio = manager.list_portfolio(status='holding')

tracker = get_return_tracker()
result = tracker.track_return(tracking_time='midday')

output = {
    'portfolio': portfolio,
    'return_tracking': result
}
print(json.dumps(output, ensure_ascii=False))
" > midday_data.json

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
      "content": "🔥 火箭量化午盘收益报告 - '"$(date +%Y-%m-%d)"'"
    },
    "template": "blue"
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "✅ 午盘报告已自动生成，当前持仓上午收益情况已更新！\n\n数据生成时间：'"$(date "+%Y-%m-%d %H:%M:%S")"'\n\n⚠️ 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。"
      }
    }
  ]
}
'
