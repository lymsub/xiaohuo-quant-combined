# 高客秘书整合版 v2.6

## 项目概述

高客秘书是一套全功能量化投资工具，整合了股票筛选、个股分析、收益跟踪、投资报告、早报视频等核心功能，支持双数据源互补（Tushare + AkShare）和 SQLite 本地缓存，提供飞书富文本卡片和通用输出两种模式。

### 核心功能

- **个股分析报告**：深度量化分析，包含技术指标、策略信号、回测结果和 AI 分析
- **定时投资机会扫描**：每小时自动扫描全市场短线机会
- **收益跟踪**：午盘实时监控 + 收盘完整收益报告
- **投资报告**：专业收益归因 + 财经资讯 + 策略提示
- **早报视频**：自动生成并推送投资早报视频
- **持仓管理**：支持自动按当前价格买入和手动指定价格买入
- **定时任务管理**：自然语言调整定时任务，自动识别节假日

## 快速开始

### 环境要求

- Python 3.8+
- 网络连接（用于获取数据和生成视频）

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/lymsub/xiaohuo-quant-combined.git
cd xiaohuo-quant-combined
```

2. **自动安装**

```bash
# 执行安装脚本
bash scripts/install.sh
```

3. **配置 Tushare Token**（可选，推荐）

```bash
# 在 ~/.xiaohuo_quant/token.txt 中添加你的 Tushare Token
echo "your_tushare_token" > ~/.xiaohuo_quant/token.txt
```

4. **配置火山云 API Key**（用于生成视频和 AI 分析）

```bash
# 设置环境变量或使用命令行
python scripts/main.py config set_volc_key --key your_volc_api_key
```

### 启动方式

```bash
# 启动高客秘书
python scripts/main.py

# 或者直接在聊天中说
# "启动高客秘书"
```

## 核心模块 API

### 1. 数据获取模块 (`data_source.py`)

#### 功能
- 多数据源支持：Tushare（主）、AkShare（备）、新浪/腾讯财经
- 分钟级数据获取
- 数据同步与缓存

#### 核心函数

```python
# 获取数据管理器
def get_data_manager(tushare_token=None, enable_fallback=True, retry_count=3, retry_delay=2):
    """
    获取数据管理器实例
    
    参数:
        tushare_token: Tushare Token
        enable_fallback: 是否启用备用数据源
        retry_count: 重试次数
        retry_delay: 重试间隔（秒）
    
    返回:
        DataSourceManager 实例
    """

# 获取日线数据
def get_daily_quotes(self, ts_code, start_date=None, end_date=None, limit=100, source=None):
    """
    获取股票日线数据
    
    参数:
        ts_code: 股票代码（如 600519.SH）
        start_date: 开始日期（YYYYMMDD）
        end_date: 结束日期（YYYYMMDD）
        limit: 限制条数
        source: 数据源（tushare/akshare/sina/tencent）
    
    返回:
        DataFrame 数据
    """
```

### 2. 量化分析模块 (`quant_analyzer_v22.py`)

#### 功能
- 技术指标计算（MA、MACD、RSI等）
- 信号生成与回测
- 综合诊断与 AI 分析

#### 核心函数

```python
# 分析股票
def analyze_stock(code, days=90, output_file=None):
    """
    分析股票
    
    参数:
        code: 股票代码
        days: 分析天数
        output_file: 输出文件
    
    返回:
        分析结果字典
    """
```

### 3. 投资组合管理模块 (`portfolio_manager.py`)

#### 功能
- 持仓管理
- 买入/卖出操作
- 持仓列表查询

#### 核心函数

```python
# 获取投资组合管理器
def get_portfolio_manager():
    """
    获取投资组合管理器实例
    
    返回:
        PortfolioManager 实例
    """

# 买入股票
def buy_stock(self, ts_code, quantity, price=None):
    """
    买入股票
    
    参数:
        ts_code: 股票代码
        quantity: 数量
        price: 价格（None 则自动获取最新价）
    
    返回:
        操作结果
    """

# 列出持仓
def list_portfolio(self, status='holding'):
    """
    列出持仓
    
    参数:
        status: 状态（holding/sold/all）
    
    返回:
        持仓列表
    """
```

### 4. 收益跟踪模块 (`return_tracker.py`)

#### 功能
- 收益计算与跟踪
- 基准对比（沪深300）
- 归因分析

#### 核心函数

```python
# 获取收益跟踪器
def get_return_tracker():
    """
    获取收益跟踪器实例
    
    返回:
        ReturnTracker 实例
    """

# 跟踪收益
def track_return(self, tracking_time='close'):
    """
    跟踪收益
    
    参数:
        tracking_time: 跟踪时间（midday/close）
    
    返回:
        收益跟踪结果
    """
```

### 5. 股票推荐模块 (`recommend_stocks.py`)

#### 功能
- 股票筛选与推荐
- 综合评分

#### 核心函数

```python
# 推荐股票
def recommend_stocks(top_n=5):
    """
    推荐股票
    
    参数:
        top_n: 推荐数量
    
    返回:
        推荐股票列表
    """
```

### 6. 早报生成模块 (`morning_report.py`)

#### 功能
- 生成投资早报
- 视频生成与上传

#### 核心函数

```python
# 生成早报
def generate_morning_report():
    """
    生成早报
    
    返回:
        早报内容
    """

# 生成早报视频
def generate_morning_video():
    """
    生成早报视频
    
    返回:
        视频链接
    """
```

## 定时任务

### 默认定时任务

| 任务 | 默认时间 | 说明 |
|------|----------|------|
| 早报视频 | 08:30（工作日） | 生成并推送当日投资早报视频 |
| 午盘报告 | 11:30（工作日） | 推送午盘收益监控报告 |
| 收盘报告 | 15:30（工作日） | 推送收盘完整收益报告 |
| 行情扫描 | 每小时（工作日） | 扫描全市场短线投资机会 |

### 调整定时任务

```bash
# 调整早报时间
python scripts/main.py config set_morning_time --time 08:00

# 关闭午盘报告
python scripts/main.py config disable_midday_report

# 启用收盘报告
python scripts/main.py config enable_close_report

# 列出所有定时任务
python scripts/main.py config list_tasks
```

## 命令行使用

### 个股分析

```bash
# 分析股票
python scripts/quant_analyzer_v22.py --code 600519 --days 90

# 分析结果会保存为 {股票代码}_result.json
```

### 查看涨幅榜

```bash
# 查看今日涨幅榜
python scripts/get_today_gainers.py
```

### 推荐股票

```bash
# 获取今日最佳股票推荐
python scripts/recommend_stocks.py
```

### 收益跟踪

```bash
# 查看午盘收益
python scripts/return_tracker.py --time midday

# 查看收盘收益
python scripts/return_tracker.py --time close
```

### 投资报告

```bash
# 生成今日投资报告
python scripts/investment_report.py
```

## 配置说明

### 配置文件

配置文件位于 `~/.xiaohuo_quant/config.json`，包含以下配置项：

```json
{
  "douban": {
    "api_key": "your_volc_api_key",
    "api_base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "video_api": "https://ark.cn-beijing.volces.com/api/v3/videos/generations",
    "video_model": "doubao-seedance-1-5-pro-251215"
  }
}
```

### 环境变量

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| TUSHARE_API_KEY | Tushare Token | "" |
| VOLC_ARK_API_KEY | 火山云 API Key | "" |
| DOUBAO_API_KEY | Doubao API Key | "" |
| ARK_BASE_URL | Ark API 基础 URL | "https://ark.cn-beijing.volces.com/api/v3" |

## 数据存储

- **数据库**：SQLite 数据库，位于 `~/.xiaohuo_quant/quant_data.db`
- **配置文件**：位于 `~/.xiaohuo_quant/config.json`
- **Token 文件**：位于 `~/.xiaohuo_quant/token.txt`

## 常见问题

### 1. 数据获取失败

- **原因**：Tushare Token 无效或额度不足
- **解决**：配置有效的 Tushare Token，或依赖 AkShare 作为备用数据源

### 2. 视频生成失败

- **原因**：火山云 API Key 无效或额度不足
- **解决**：配置有效的火山云 API Key

### 3. 定时任务不执行

- **原因**：可能是节假日或配置问题
- **解决**：检查节假日设置，确保定时任务已启用

### 4. 收益计算不准确

- **原因**：数据同步延迟或计算逻辑问题
- **解决**：确保数据已同步，检查持仓记录是否正确

## 技术架构

### 核心组件

1. **数据层**：多数据源整合（Tushare、AkShare、新浪/腾讯财经）
2. **存储层**：SQLite 本地缓存
3. **分析层**：量化分析、策略回测
4. **报告层**：多格式报告生成（文本、富文本卡片、视频）
5. **调度层**：定时任务管理、节假日判断

### 数据流

```
用户输入 → 意图识别 → 功能执行 → 数据获取 → 分析处理 → 报告生成 → 智能输出
```

## 安全注意事项

- **敏感信息**：所有 API Key 和 Token 均通过环境变量或本地配置文件管理，无硬编码
- **数据安全**：本地数据库存储，不依赖外部服务
- **操作安全**：所有交易操作均需用户确认，系统仅提供分析和建议

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 联系我们。

---

**高客秘书整合版 v2.6 - 股票筛选 + 个股分析 + 收益跟踪 + 投资报告 + 早报视频，双数据源互补，SQLite缓存提速，智能输出模式，AI专业分析！** 🚀