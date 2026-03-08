# 🌌 奇点量化交易平台 | Singularity Quant Trading Platform

> **生产级 AI 量化交易系统** - 集成 Azure OpenAI、GCP Vertex AI、多策略引擎、实时市场扫描

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-ready-success)](.)

---

## 📖 目录

- [功能特性](#-功能特性)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [核心模块](#-核心模块)
- [部署指南](#-部署指南)
- [环境变量](#-环境变量)
- [项目结构](#-项目结构)
- [常见问题](#-常见问题)

---

## ✨ 功能特性

### 🎯 核心能力

| 功能 | 描述 |
|------|------|
| **🧠 AI 决策引擎** | Azure OpenAI 生成交易建议，支持自定义策略 |
| **📊 全息指挥舱** | Tkinter GUI 界面，实时展示市场数据 |
| **📡 市场雷达** | 全市场扫描，自动筛选优质标的 |
| **🔬 个股深析** | 单股多维度分析（技术面 + 基本面 + 情绪） |
| **🔥 板块热力** | 实时板块涨跌幅监控 |
| **☁️ 云端集成** | GCP BigQuery / Vertex AI / Cloud Scheduler |

### 🛠️ 技术亮点

- **50+ 技术指标** - 趋势/波动率/动量/成交量分析
- **多策略回测** - 支持历史数据回测验证
- **情绪分析** - NLP 分析市场新闻/社交媒体情绪
- **自动调度** - GCP Cloud Scheduler 定时任务
- **微服务架构** - 模块化设计，易于扩展

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    🎯 GUI 指挥舱 (dashboard.py)              │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │ 定向狙击 │ 板块热力 │ 雷达扫描 │ 单股深析 │              │
│  └──────────┴──────────┴──────────┴──────────┘              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  quant_master │    │    radar.py   │    │ a_share_quant │
│   AI 决策核心  │    │   市场雷达    │    │   A 股量化    │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   data_engine   │
                    │    数据引擎     │
                    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Azure OpenAI │    │  GCP Services │    │  AKShare API  │
│   语言模型    │    │  BigQuery 等  │    │   市场数据    │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## 🚀 快速开始

### 前置要求

- Python 3.13+
- Windows 10/11 或 Linux/macOS
- Azure OpenAI API Key（可选）
- GCP 项目凭证（可选）

### 1️⃣ 克隆项目

```bash
git clone https://github.com/huangruiran666/QUANT-PLATFORM-WINDOWS.git
cd QUANT-PLATFORM-WINDOWS
```

### 2️⃣ 安装依赖

```bash
# 使用 uv（推荐）
pip install uv
uv sync

# 或使用 pip
pip install -r requirements_gcp.txt
```

### 3️⃣ 配置环境变量

复制 `.env.example` 为 `.env` 并填写凭证：

```bash
cp .env.example .env
```

编辑 `.env`：

```ini
# Azure OpenAI
AZURE_OPENAI_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-5-nano

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GCP_PROJECT=your_project_id
```

### 4️⃣ 启动指挥舱

```bash
# 方式 1: 直接运行
python dashboard.py

# 方式 2: 使用启动脚本（Windows）
Launch_Dashboard.bat
```

---

## 📦 核心模块

### 1. GUI 指挥舱 (`dashboard.py`)

4 个核心功能 Tab：

| Tab | 功能 | 快捷键 |
|-----|------|--------|
| 🎯 定向狙击 | 股票列表 + AI 决策建议 | - |
| 🔥 板块热力 | 实时板块涨跌幅 | - |
| 📡 雷达扫描 | 全市场筛选优质标的 | - |
| 🔬 单股深析 | 输入股票代码深度分析 | - |

### 2. AI 决策核心 (`quant_master.py`)

```python
from quant_master import SingularityMassiveCore

# 分析指定股票
core = SingularityMassiveCore()
result = core.run_surgical_audit("贵州茅台")

print(result['action'])  # 买入/卖出/观察
print(result['report'])  # 详细分析报告
```

### 3. 市场雷达 (`radar.py`)

```python
from radar import get_market_radar

# 扫描全市场
candidates = get_market_radar()
print(candidates.head(10))
```

### 4. A 股量化 (`a_share_quant.py`)

```python
from a_share_quant import get_a_share_data, ai_expert_decision

# 获取股票数据
data = get_a_share_data("600519")

# AI 专家决策
report = ai_expert_decision("600519", data)
print(report)
```

### 5. 数据引擎 (`data_engine.py`)

```python
from data_engine import FullSovereignEngine

# 获取全量数据
stocks, sectors, macro, vitals = FullSovereignEngine.get_omni_data()
```

---

## ☁️ 部署指南

### 本地部署（推荐开发使用）

```bash
python dashboard.py
```

### Railway 部署（Web 服务）

1. 访问 [Railway](https://railway.app) 并登录
2. 创建新项目，选择 GitHub 仓库
3. 设置环境变量
4. 自动部署

```bash
# 或使用 CLI
npm i -g @railway/cli
railway login
railway up
```

### Render 部署

1. 访问 [Render](https://render.com)
2. 创建 Web Service
3. 连接 GitHub 仓库
4. 配置构建命令：`pip install -r requirements_gcp.txt`
5. 启动命令：`python main.py`

### GCP 部署（生产环境）

```bash
# 初始化 GCP
python gcp_init.py

# 部署数据管道
python gcp_daily_pipeline.py

# 设置调度器
python gcp_scheduler_setup.py
```

详细部署指南见 [DEPLOY.md](DEPLOY.md)

---

## 🔐 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `AZURE_OPENAI_KEY` | Azure OpenAI API 密钥 | 否 |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 端点 | 否 |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP 凭证文件路径 | 否 |
| `GCP_PROJECT` | GCP 项目 ID | 否 |

**注意：** 所有环境变量均为可选，未设置时使用本地数据源。

---

## 📁 项目结构

```
QUANT-PLATFORM-WINDOWS/
├── 📄 dashboard.py              # GUI 指挥舱（主界面）
├── 📄 quant_master.py           # AI 决策核心
├── 📄 main.py                   # 程序入口
├── 📄 data_engine.py            # 数据引擎
├── 📄 data_router.py            # 数据路由
├── 📄 clients.py                # 客户端单例
│
├── 📈 策略模块
│   ├── a_share_quant.py         # A 股量化
│   ├── ai_search_quant.py       # AI 搜索
│   ├── dual_cloud_quant_v4.py   # 双云策略
│   ├── sentiment_beast.py       # 情绪分析
│   └── radar.py                 # 市场雷达
│
├── ☁️ GCP 集成
│   ├── gcp_init.py              # GCP 初始化
│   ├── gcp_daily_pipeline.py    # 每日管道
│   ├── gcp_automl_launcher.py   # AutoML
│   ├── gcp_feature_engineer.py  # 特征工程
│   ├── gcp_scheduler_daemon.py  # 调度器
│   └── ...
│
├── 🕷️ 数据爬虫
│   └── cloud_scraper/
│       ├── spiders/             # Scrapy 爬虫
│       ├── settings.py
│       └── Dockerfile
│
├── 🔧 工具
│   ├── camber_expert/           # 专家系统
│   └── src/chats/               # 聊天记录
│
├── 📦 部署配置
│   ├── Procfile                 # Railway 配置
│   ├── railway.toml
│   ├── render.yaml
│   └── .gitignore
│
└── 📚 文档
    ├── README.md                # 本文件
    ├── DEPLOY.md                # 部署指南
    └── 一键部署说明.md
```

---

## ❓ 常见问题

### Q: 没有 Azure/GCP 凭证能用吗？

**A:** 可以！项目支持纯本地运行，使用 AKShare 免费数据源。

### Q: 如何添加自定义策略？

**A:** 在 `策略模块` 目录创建新的 `.py` 文件，实现 `analyze()` 函数即可。

### Q: GUI 界面卡顿怎么办？

**A:** 数据加载在后台线程运行，如卡顿请检查网络连接或减少同时分析的股票数量。

### Q: 如何设置定时任务？

**A:** 使用 GCP Cloud Scheduler：
```bash
python gcp_scheduler_setup.py --schedule "0 9 * * *"  # 每天 9 点
```

### Q: 支持哪些市场数据？

**A:** 目前支持：
- ✅ A 股（沪深京）
- ✅ 港股
- ✅ 美股（延迟 15 分钟）
- ✅ 期货/外汇（通过 AKShare）

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📬 联系方式

- **GitHub**: [@huangruiran666](https://github.com/huangruiran666)
- **项目仓库**: [QUANT-PLATFORM-WINDOWS](https://github.com/huangruiran666/QUANT-PLATFORM-WINDOWS)

---

## ⚠️ 免责声明

本项目仅供教育和研究使用，不构成投资建议。使用本软件进行交易存在风险，请谨慎决策。

---

<div align="center">

**🌌 奇点已至，主宰降临**

[⬆️ 返回顶部](#-奇点量化交易平台--singularity-quant-trading-platform)

</div>
