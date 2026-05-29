# FitFactory OS — 服装厂智能工作台

> 代号：**FitFactory OS**  
> 定位：从"人追事"到"事追人"的服装厂数字化中枢  
> 目标用户：服装厂厂长助理（200~500 人内衣/服装厂）

---

## 项目一句话描述

一个**能理解工厂日常语言、能跨模块调用数据、能做推演计算的 AI Agent**，让助理从操作员变成指挥官。

---

## 文档索引

| 文档 | 内容 | 链接 |
| --- | --- | --- |
| 🏗️ 系统架构 | 技术选型、数据流、部署方案 | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| 🗄️ 数据库设计 | 全部数据表定义、字段说明、关系图 | [DATABASE.md](docs/DATABASE.md) |
| 🧩 功能模块 | 六大模块详细设计、API 设计 | [MODULES.md](docs/MODULES.md) |
| 🗺️ 实施路线图 | 四阶段计划、里程碑、进度追踪 | [ROADMAP.md](docs/ROADMAP.md) |

---

## 核心功能一览

| 模块 | 一句话 | 解决什么痛点 |
| --- | --- | --- |
| 📅 生产排单引擎 | AI 自动排产 + 撞单检测 + 插单模拟 | Excel 拖拽排期，撞单靠肉眼 |
| 📦 物料管理 | 齐套检查 + 缺料预警 + 采购建议 | 发现缺料时已来不及 |
| 📊 生产进度看板 | 实时看板 + 延期预警 | 下车间挨个问"做到哪了" |
| 💰 计件工资 | 自动汇总 + 异常标记 | 月底手抄计件单对账 |
| 💬 AI 智能问答 | 自然语言查订单/进度/工资/产线效率 | 翻 Excel 半天才能回答老板 |
| 🔔 消息推送 | 企业微信自动推送预警/通知 | 信息靠吼、电话、微信群 |

---

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Streamlit（Phase 1）→ React + Tailwind（Phase 2） |
| 后端 | FastAPI (Python) |
| 主数据库 | SQLite（本地）→ PostgreSQL（多用户） |
| 向量数据库 | Chroma → Cloudflare Vectorize |
| AI 模型 | DeepSeek API (Function Calling) |
| 消息推送 | 企业微信机器人 Webhook |

---

## 快速开始

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python src/init_db.py

# 启动服务
uvicorn src.main:app --reload
```

---

## 项目结构

```
fitfactory-os/
├── README.md                ← 本文件
├── docs/
│   ├── ARCHITECTURE.md      ← 系统架构文档
│   ├── DATABASE.md          ← 数据库设计文档
│   ├── MODULES.md           ← 功能模块设计文档
│   └── ROADMAP.md           ← 实施路线图
├── src/
│   ├── main.py              ← FastAPI 入口
│   ├── models/              ← SQLAlchemy 数据模型
│   ├── routers/             ← API 路由
│   ├── services/            ← 业务逻辑（排单引擎等）
│   ├── ai/                  ← DeepSeek Agent 相关
│   └── utils/               ← 工具函数
├── tests/
├── requirements.txt
└── .env.example
```

---

*最后更新：2026-05-28*
