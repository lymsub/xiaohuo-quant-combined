# 高客秘书整合版 v2.6（OpenClaw Skill）

## 项目概述

高客秘书是为 OpenClaw 设计的全功能量化投资 Skill，整合了股票筛选、个股分析、收益跟踪、投资报告、早报视频等核心功能，支持**五源自动降级**（Tushare/AkShare/新浪/腾讯/Baostock）和 SQLite 本地缓存，提供飞书富文本卡片和通用输出两种模式。

**核心特点：**
- 🚀 OpenClaw 一键安装，开箱即用
- 💬 完全自然语言对话，无需记命令
- 🔒 强制数据真实，绝不编造数据
- 🎯 五源自动降级，稳定可靠
- 📊 完整报告模板，专业分析

### 核心功能

- **个股分析报告**：深度量化分析，包含技术指标、策略信号、回测结果和 AI 分析
- **今日涨幅榜**：实时涨幅榜，支持缓存和非交易日处理
- **股票推荐**：多维度综合评分，智能推荐
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
- ffmpeg（用于视频生成，可选）

### 安装步骤（OpenClaw 自动安装）

高客秘书作为 OpenClaw Skill 安装，**无需手动操作**！

#### 安装方式

1. 在 OpenClaw 中找到并安装 "高客秘书" skill
2. OpenClaw 会自动完成：
   - 创建独立的 Python 虚拟环境
   - 安装所有依赖包
   - 初始化本地数据库
   - 配置默认参数

3. 配置（可选但推荐）：
   - 配置 Tushare Token（提升数据稳定性）
   - 配置火山云 API（用于 AI 分析和视频生成）
   - 配置飞书 Webhook（用于自动推送报告）

#### 验证安装

安装成功后，在 OpenClaw 聊天中说：
```
启动高客秘书
```

或直接使用命令测试：
```bash
# 查看今日涨幅榜
分析今天的涨幅榜

# 分析个股
分析一下600519
```

---

## 📋 配置说明（重要！必看）

配置是高客秘书的核心部分，请仔细阅读！

### 配置文件位置

所有配置文件默认位于用户主目录下：
```
~/.xiaohuo_quant/
├── token.txt              # Tushare Token（可选）
├── quant_data.db          # SQLite 数据库（自动创建）
└── custom_config.json     # 自定义配置（可选）
```

---

### 1. 数据配置（必须）

#### 1.1 Tushare Token（可选但推荐）

Tushare 是主要数据源之一，配置后可获得更稳定的数据服务。

**获取方式：**
- 访问 https://tushare.pro/ 注册账号
- 在个人中心获取 Token

**配置方式：**
```bash
# 方式一：使用配置文件
echo "your_tushare_token_here" > ~/.xiaohuo_quant/token.txt

# 方式二：使用环境变量
export TUSHARE_API_KEY="your_tushare_token_here"

# 方式三：使用命令行配置
python scripts/config.py --tushare your_tushare_token_here
```

**验证配置：**
```bash
python scripts/config.py --check
```

---

#### 1.2 数据降级机制（无需配置，自动工作）

高客秘书内置**五源自动降级机制**，无需任何配置即可工作：

| 数据源 | 优先级 | 说明 | 状态 |
|--------|--------|------|------|
| SQLite 缓存 | 1 | 本地数据库，速度最快 | ✅ 总是启用 |
| Tushare | 2 | 需要 Token | ⚙️ 可选配置 |
| AkShare | 3 | 开源库，免费 | ✅ 自动启用 |
| 新浪财经 | 4 | 实时行情 | ✅ 自动启用 |
| 腾讯财经 | 5 | 实时行情 | ✅ 自动启用 |
| Baostock | 6 | 历史数据 | ✅ 自动启用 |

**降级逻辑：**
- 如果 Tushare 不可用（无 Token 或限流），自动切换到 AkShare
- 如果 AkShare 失败，切换到新浪/腾讯
- 如果所有 API 都失败，使用本地缓存（如果有）
- **永远不返回默认值或编造数据！**

---

### 2. 火山云 API 配置（用于 AI 功能）

火山云 API 用于：
- AI 个股分析
- 早报视频生成
- 语音合成

#### 2.1 获取火山云 API Key

1. 访问火山方舟：https://www.volcengine.com/product/ark
2. 注册/登录账号
3. 创建一个应用，获取 API Key

#### 2.2 配置方式

```bash
# 方式一：环境变量（推荐）
export ARK_API_KEY="your_ark_api_key_here"
# 或者
export VOLC_ARK_API_KEY="your_ark_api_key_here"
# 或者
export DOUBAO_API_KEY="your_ark_api_key_here"

# 方式二：自定义配置文件
# 创建 ~/.xiaohuo_quant/custom_config.json
{
  "douban": {
    "api_key": "your_ark_api_key_here",
    "api_base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "video_model": "doubao-seedance-1-5-pro-251215",
    "video_duration": 12
  }
}
```

---

### 3. 飞书推送配置（可选）

配置后可将报告自动推送到飞书群。

#### 3.1 获取飞书 Webhook

1. 在飞书群中添加"自定义机器人"
2. 获取 Webhook URL

#### 3.2 配置方式

```bash
# 方式一：环境变量
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
export FEISHU_PUSH_ENABLED="true"
export FEISHU_SEND_VIDEO="true"

# 方式二：自定义配置文件
# ~/.xiaohuo_quant/custom_config.json
{
  "feishu": {
    "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "push_enabled": true,
    "send_video_directly": true
  }
}
```

---

### 4. 对象存储配置（可选）

配置后可将视频上传到对象存储（如火山云 TOS）。

```bash
# 环境变量
export COS_ENDPOINT="https://your-bucket.tos-cn-beijing.volces.com/"
export COS_UPLOAD_ENABLED="true"

# 或配置文件
{
  "cos": {
    "endpoint": "https://your-bucket.tos-cn-beijing.volces.com/",
    "upload_enabled": true
  }
}
```

---

### 5. 早报配置（可选）

```bash
# 环境变量
export MORNING_REPORT_VIDEO_ENABLED="false"  # 是否生成视频

# 配置文件
{
  "morning_report": {
    "enabled": true,
    "run_time": "08:30",
    "video_enabled": false,
    "push_enabled": true
  }
}
```

---

### 完整配置示例

`~/.xiaohuo_quant/custom_config.json`:

```json
{
  "douban": {
    "api_key": "your_ark_api_key",
    "api_base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "video_model": "doubao-seedance-1-5-pro-251215",
    "video_style": "专业金融早报背景，抽象科技感动态数据流动画，蓝色紫色渐变光效，粒子流动，数字波浪，无任何文字和K线图，简洁大气科技感，适合财经新闻播报场景",
    "video_duration": 12
  },
  "cos": {
    "endpoint": "https://lyming.tos-cn-beijing.volces.com/",
    "upload_enabled": true
  },
  "feishu": {
    "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "push_enabled": true,
    "send_video_directly": true
  },
  "morning_report": {
    "enabled": true,
    "run_time": "08:30",
    "video_enabled": false,
    "push_enabled": true
  }
}
```

---

## 如何使用（OpenClaw 自然语言）

高客秘书完全支持自然语言对话，无需记命令！

---

### 1. 今日涨幅榜

```
看一下今天的涨幅榜
今天什么股票涨得好？
```

---

### 2. 股票推荐

```
推荐几只今天值得关注的股票
有什么好的股票推荐？
```

---

### 3. 个股分析

```
分析一下600519
帮我看看茅台这只股票怎么样
```

---

### 4. 持仓管理

```
我买了100股600519，价格150
添加持仓 600519 100股
查看我的持仓
```

---

### 5. 收益跟踪

```
我今天的收益怎么样？
午盘收益报告
收盘收益
```

---

### 6. 投资报告

```
生成今日投资报告
给我一个完整的分析
```

---

### 7. 配置管理

```
设置我的飞书 webhook
配置一下 Tushare token
检查配置
```

---

## （可选）开发者使用命令行

如果你想直接用命令行测试或开发：

```bash
cd scripts

# 进入虚拟环境
source venv/bin/activate

# 今日涨幅榜
python get_today_gainers.py

# 个股分析
python quant_analyzer_v22.py --code 600519 --days 90

# 股票推荐
python recommend_stocks.py

# 检查配置
python config.py --check

# 主程序
python main.py --help
```

---

## 数据存储

- **数据库**：SQLite 数据库，位于 `~/.xiaohuo_quant/quant_data.db`
- **配置文件**：位于 `~/.xiaohuo_quant/custom_config.json`
- **Token 文件**：位于 `~/.xiaohuo_quant/token.txt`

---

## 常见问题

### 1. 数据获取失败？

**答**：不用担心！高客秘书有五源自动降级机制：

- 如果 Tushare 限流 → 自动用 AkShare
- 如果 AkShare 失败 → 自动用新浪/腾讯
- 如果都失败 → 用本地缓存

**唯一不会做的事**：编造虚假数据！

---

### 2. 我没有 Tushare Token 怎么办？

**答**：完全可以用！只配置 Tushare Token 是推荐，但不是必须的。系统默认使用 AkShare、新浪、腾讯财经，这些都是免费的。

---

### 3. 我不想配置火山云 API 可以吗？

**答**：可以！火山云 API 只用于：
- AI 个股分析（文字部分）
- 视频生成

即使不配置，**所有核心量化分析功能都可以正常使用**！

---

### 4. 如何验证配置是否正确？

```bash
cd scripts
./venv/bin/python config.py --check
```

---

### 5. 如何设置定时任务？

提供了自动化脚本：

```bash
cd scripts
bash setup_cron.sh  # 设置定时任务
```

**默认定时任务：**
- 08:30 - 早报生成
- 11:30 - 午盘收益报告
- 15:30 - 收盘收益报告
- 每小时 - 投资机会扫描

---

## 技术架构

### 核心组件

1. **数据层**：五源自动降级（Tushare、AkShare、新浪/腾讯财经、Baostock）
2. **存储层**：SQLite 本地缓存，速度优先
3. **分析层**：量化分析、策略回测
4. **报告层**：多格式报告生成（文本、富文本卡片、视频）
5. **调度层**：定时任务管理、节假日判断

### 数据流

```
用户输入 → 意图识别 → 功能执行 → 五源数据获取 → 缓存优先 → 降级处理 → 分析计算 → 报告生成 → 智能输出
```

---

## 安全注意事项

- **敏感信息**：所有 API Key 和 Token 均通过环境变量或本地配置文件管理，无硬编码
- **数据安全**：本地数据库存储，不依赖外部服务
- **操作安全**：所有交易操作均需用户确认，系统仅提供分析和建议
- **数据真实性**：代码强制禁止编造数据，接口失败时抛出异常而不是返回默认值

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 联系方式

如有问题，请通过 GitHub Issues 联系我们。

---

**高客秘书整合版 v2.6 - OpenClaw Skill，五源自动降级，强制数据真实，完整报告模板，开箱即用！** 🚀
