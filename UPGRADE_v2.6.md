# 🔥 高客秘书 v2.6 升级说明

## 📋 升级概述

高客秘书已从 v2.2 升级到 v2.6，新增了以下核心功能：

### ✅ 新增功能

1. **📊 持仓管理**
   - 添加持仓（买入）
   - 卖出持仓
   - 删除持仓
   - 查看持仓列表
   - 持仓摘要

2. **📈 收益跟踪（定时任务）**
   - 午盘收益跟踪（11:35）
   - 收盘收益跟踪（15:05）
   - 收益归因分析
   - 基准对比（沪深300）
   - 历史收益查询

3. **📄 投资报告（定时任务）**
   - 午间报告（11:35）
   - 每日投资报告（15:05）
   - 结合持仓、收益、财经资讯
   - 市场点评
   - 操作建议

4. **🎯 投资机会筛选（定时任务）**
   - 每天4次筛选（9:35, 11:00, 13:30, 14:50）
   - 结合今日涨幅榜
   - 智能推荐

---

## 🚀 快速开始

### 1. 测试新功能

```bash
cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts

# 查看帮助
./venv/bin/python main.py --help

# 查看持仓帮助
./venv/bin/python main.py portfolio --help

# 查看收益跟踪帮助
./venv/bin/python main.py return --help

# 查看投资报告帮助
./venv/bin/python main.py report --help
```

### 2. 添加测试持仓

```bash
# 先查看当前持仓（应该是空的）
./venv/bin/python main.py portfolio list

# 添加一个测试持仓（宁德时代）
./venv/bin/python main.py portfolio add --code 300750.SZ --price 400 --quantity 100

# 再添加一个（贵州茅台）
./venv/bin/python main.py portfolio add --code 600519.SH --price 1800 --quantity 10

# 查看持仓列表
./venv/bin/python main.py portfolio list

# 查看持仓摘要
./venv/bin/python main.py portfolio summary
```

### 3. 测试收益跟踪

```bash
# 跟踪当前收益
./venv/bin/python main.py return track --time close

# 查看历史收益
./venv/bin/python main.py return history --limit 10
```

### 4. 测试投资报告

```bash
# 生成午间报告
./venv/bin/python main.py report midday

# 生成每日投资报告
./venv/bin/python main.py report daily
```

### 5. 测试投资机会筛选

```bash
# 筛选投资机会
./venv/bin/python main.py opportunity
```

---

## ⏰ 设置定时任务

### 自动设置（推荐）

```bash
cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts
chmod +x setup_tasks.sh
./setup_tasks.sh
```

### 手动设置

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（根据你的实际路径调整）

# ============================================================
# 🔥 高客秘书定时任务 v2.6
# ============================================================

# 午盘收益跟踪（11:35，周一到周五）
35 11 * * 1-5 cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts && ./venv/bin/python main.py --task midday_report >> /root/.xiaohuo_quant/midday.log 2>&1

# 收盘收益跟踪 + 投资报告（15:05，周一到周五）
5 15 * * 1-5 cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts && ./venv/bin/python main.py --task daily_report >> /root/.xiaohuo_quant/daily.log 2>&1

# 投资机会筛选（每天4次：9:35, 11:00, 13:30, 14:50）
35 9 * * 1-5 cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts && ./venv/bin/python main.py --task opportunity >> /root/.xiaohuo_quant/opportunity.log 2>&1
0 11 * * 1-5 cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts && ./venv/bin/python main.py --task opportunity >> /root/.xiaohuo_quant/opportunity.log 2>&1
30 13 * * 1-5 cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts && ./venv/bin/python main.py --task opportunity >> /root/.xiaohuo_quant/opportunity.log 2>&1
50 14 * * 1-5 cd /root/.openclaw/workspace/skills/xiaohuo-quant-combined/scripts && ./venv/bin/python main.py --task opportunity >> /root/.xiaohuo_quant/opportunity.log 2>&1
```

---

## 📁 文件结构

```
skills/xiaohuo-quant-combined/scripts/
├── main.py                    # 🆕 主入口程序（整合所有功能）
├── portfolio_manager.py       # 🆕 持仓管理模块
├── return_tracker.py          # 🆕 收益跟踪模块
├── investment_report.py       # 🆕 投资报告模块
├── setup_tasks.sh            # 🆕 定时任务设置脚本
├── database.py                # ✅ 已升级（新增持仓表）
├── quant_analyzer_v22.py     # 股票分析模块（保持不变）
├── get_today_gainers.py      # 涨幅榜筛选（保持不变）
├── recommend_stocks.py        # 股票推荐（保持不变）
├── config.py                  # 配置管理（保持不变）
├── data_source.py             # 数据源管理（保持不变）
└── venv/                      # 虚拟环境
```

---

## 🎯 演示流程（给评委看）

### 场景1：展示持仓管理

```
1. 查看当前持仓
   命令：./venv/bin/python main.py portfolio list

2. 添加持仓（模拟买入）
   命令：./venv/bin/python main.py portfolio add --code 300750.SZ --price 400 --quantity 100

3. 查看持仓详情
   命令：./venv/bin/python main.py portfolio list

4. 查看持仓摘要
   命令：./venv/bin/python main.py portfolio summary
```

### 场景2：展示收益跟踪

```
1. 跟踪当前收益
   命令：./venv/bin/python main.py return track --time close

2. 展示归因分析
   - 最大贡献者
   - 最大拖累者
   - 胜率统计
   - 基准对比
```

### 场景3：展示投资报告

```
1. 生成每日投资报告
   命令：./venv/bin/python main.py report daily

2. 展示报告内容
   - 收益概览
   - 持仓详情
   - 市场点评
   - 相关资讯
   - 操作建议
```

### 场景4：展示定时任务（主动推送）

```
展示 cron 任务列表：
crontab -l

展示日志文件：
tail -f /root/.xiaohuo_quant/daily.log
```

---

## 📊 数据库升级

已在 `database.py` 中新增3个表：

1. **portfolio** - 持仓表
   - 持仓ID、股票代码、名称、买入价、数量、买入日期、状态、备注

2. **return_tracking** - 收益跟踪表
   - 跟踪日期、时间、总市值、总成本、收益率、日收益、基准收益、归因数据

3. **investment_reports** - 投资报告表
   - 报告日期、类型、内容、摘要

---

## ⚠️ 注意事项

1. **先测试再设置定时任务**
   - 先手动测试各功能正常
   - 确认无误后再设置 cron

2. **日志文件位置**
   - 午盘报告：`/root/.xiaohuo_quant/midday.log`
   - 收盘报告：`/root/.xiaohuo_quant/daily.log`
   - 机会筛选：`/root/.xiaohuo_quant/opportunity.log`

3. **检查 cron 状态**
   ```bash
   # 查看任务
   crontab -l
   
   # 查看日志
   tail -f /var/log/syslog
   ```

---

## 🎉 升级完成！

现在高客秘书 v2.6 已经具备：
- ✅ 持仓管理（落地感）
- ✅ 收益跟踪 + 归因分析
- ✅ 投资报告（每日 + 午间）
- ✅ 投资机会筛选（每天4次）
- ✅ 定时任务自动推送（主动行为）

**给评委的展示效果：**
1. "看，这是我的持仓！"（展示持仓列表）
2. "每天中午和收盘，系统会自动给我发收益报告！"（展示定时任务）
3. "这是今天的投资报告！"（展示报告内容）
4. "系统还会自动筛选投资机会！"（展示机会筛选）
