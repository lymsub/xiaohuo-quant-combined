#!/bin/bash
cd /root/.openclaw/workspace/skills/xiaohuo-quant-secretary/scripts
source venv/bin/activate

# 获取今日涨幅榜
python get_today_gainers.py > /dev/null 2>&1

# 读取最新结果（使用缓存文件）
GAINERS_FILE=$(ls -t today_gainers_*.csv 2>/dev/null | head -1)
SCAN_TIME=$(date +%Y-%m-%d\ %H:%M:%S)

# 如果有缓存文件，读取前3只股票
STOCK_CONTENT=""
if [ -n "$GAINERS_FILE" ] && [ -f "$GAINERS_FILE" ]; then
    # 读取前3只股票
    STOCK_CONTENT=$(head -4 "$GAINERS_FILE" | tail -3 | while IFS=, read -r code name price change_pct volume; do
        # 跳过标题行
        if [ "$code" != "code" ]; then
            # 去除可能的引号
            code=$(echo "$code" | tr -d '"')
            name=$(echo "$name" | tr -d '"')
            price=$(echo "$price" | tr -d '"')
            change_pct=$(echo "$change_pct" | tr -d '"')
            volume=$(echo "$volume" | tr -d '"')
            
            # 涨跌幅颜色
            if (( $(echo "$change_pct > 0" | bc -l) )); then
                emoji="🟢"
            elif (( $(echo "$change_pct < 0" | bc -l) )); then
                emoji="🔴"
            else
                emoji="⚪"
            fi
            
            echo ">$emoji **$name** ($code) ¥$price ${change_pct}%"
        fi
    done | tr '\n' '\\n')
fi

# 如果没有获取到数据，显示提示
if [ -z "$STOCK_CONTENT" ]; then
    STOCK_CONTENT=">⚠️ 暂无数据，请稍后重试"
fi

# 发送报告
openclaw message send --channel feishu --target chat:oc_407a74081dd85d531ca4426ab3d7f71a --card '
{
  "config": {
    "wide_screen_mode": true,
    "enable_forward": true
  },
  "header": {
    "title": {
      "tag": "plain_text",
      "content": "🔥 高客秘书每小时市场机会扫描 - '"$SCAN_TIME"'"
    },
    "template": "green"
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "✅ 已完成全市场短线机会扫描，筛选出当前最优质的3只股票！\n\n'"$STOCK_CONTENT"'\n\n扫描时间：'"$SCAN_TIME"'\n\n如需对某只股票进行深度分析，直接回复股票代码即可~ \n\n⚠️ 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。"
      }
    }
  ]
}
'
