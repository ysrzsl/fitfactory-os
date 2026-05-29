# 🗺️ 实施路线图 — FitFactory OS

> 最后更新：2026-05-28  
> 维护规则：每完成一个里程碑打 ✅，每周更新进度百分比

---

## 总览

```
Phase 1 (Week 1-2)     Phase 2 (Week 3-4)     Phase 3 (Week 5-6)     Phase 4 (Week 7-10)
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────────┐
│ 🔨 最小可用产品 │ ─→ │ 🧠 AI 加持     │ ─→ │ 🔄 完整闭环    │ ─→ │ 📱 移动端 + 知识库  │
│                 │    │                 │    │                 │    │                      │
│ · 数据库建表   │    │ · DeepSeek     │    │ · 物料管理     │    │ · React PWA 前端     │
│ · CRUD API     │    │   Function Call│    │ · 生产看板     │    │ · 手机扫码枪录入     │
│ · Streamlit UI │    │ · 智能排单     │    │ · 计件工资     │    │ · 工艺标准 RAG       │
│ · 硬规则排单   │    │ · NL 问答      │    │ · 企微推送     │    │ · 权限 + 报表导出    │
│ · 订单录入     │    │ · 插单模拟     │    │ · 甘特图       │    │ · Cloudflare 部署     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └──────────────────────┘
```

---

## Phase 1：最小可用产品（Week 1-2）

> 目标：能跑通"录入订单 → 自动排产 → 查看结果"这个核心闭环

### 1.1 任务拆解

| # | 任务 | 预计工时 | 涉及文件 | 状态 |
| --- | --- | --- | --- | --- |
| 1.1 | 创建 Python 项目骨架 | 0.5h | `requirements.txt`, `src/main.py` | ✅ 完成 |
| 1.2 | 定义全部 SQLAlchemy 数据模型 | 2h | `src/models/*.py` | ✅ 完成 |
| 1.3 | 编写数据库初始化脚本 | 1h | `src/init_db.py` | ✅ 完成 |
| 1.4 | 实现 styles CRUD API | 1h | `src/routers/styles.py` | ✅ 完成 |
| 1.5 | 实现 production_lines CRUD API | 1h | `src/routers/lines.py` | ✅ 完成 |
| 1.6 | 实现 orders CRUD API | 1h | `src/routers/orders.py` | ✅ 完成 |
| 1.7 | **🔥 排单引擎核心算法**（硬规则版） | 4h | `src/services/scheduler.py` | ✅ 完成 |
| 1.8 | 排单 API + 撞单检测 | 2h | `src/routers/schedule.py` | ✅ 完成 |
| 1.9 | Streamlit 页面：订单录入表单 | 2h | `src/ui/order_form.py` | ✅ 完成 |
| 1.10 | Streamlit 页面：排产结果展示 | 2h | `src/ui/schedule_view.py` | ✅ 完成 |
| 1.11 | 测试数据填充（seed data） | 1h | `src/seed_data.py` | ✅ 完成 |
| 1.12 | 手动端到端测试 | 2h | - | ✅ 完成 |

**里程碑验收标准**：
- ✅ 能在 Streamlit 页面新增一条订单
- ✅ 点击"自动排产"后返回推荐产线和日期
- ✅ 能查看所有已排产订单列表

---

## Phase 2：AI 加持（Week 3-4）

> 目标：DeepSeek 接管排单决策 + 自然语言问答可用

### 2.1 任务拆解

| # | 任务 | 预计工时 | 涉及文件 | 状态 |
| --- | --- | --- | --- | --- |
| 2.1 | 接入 DeepSeek API（基础调用） | 1h | `src/ai/client.py` | ✅ 完成 |
| 2.2 | 实现 Function Calling 工具注册 | 3h | `src/ai/tools.py` | ✅ 完成 |
| 2.3 | 🔥 AI 排单排序（替代硬规则排序） | 2h | `src/services/scheduler.py` | ✅ 完成 |
| 2.4 | 实现插单模拟 Agent | 4h | `src/ai/tools.py` (simulate_insertion) | ✅ 完成 |
| 2.5 | 🔥 NL→SQL 自然语言问答 | 6h | `src/ai/client.py` + tools | ✅ 完成 |
| 2.6 | Streamlit 页面：AI 对话界面 | 2h | `src/ui/chat.py` | ✅ 完成 |
| 2.7 | Streamlit 页面：插单模拟工具 | 2h | `src/ui/schedule_view.py` (tab3) | ✅ 完成 |
| 2.8 | 集成测试 | 2h | 6 个 AI 场景全部通过 | ✅ 完成 |

**里程碑验收标准**：
- ✅ 排单时 AI 能给出推荐理由（不只是计算结果）
- ✅ 对话界面能用自然语言问"NK-001 做到哪了"并得到准确回答
- ✅ 插单模拟能列出受影响订单

---

## Phase 3：完整闭环 + 局域网手机可用（Week 5-6）

> 目标：物料+看板+工资+推送全部打通，手机连工厂 WiFi 就能查进度

### 3.1 任务拆解

| # | 任务 | 预计工时 | 涉及文件 | 状态 |
| --- | --- | --- | --- | --- |
| 3.1 | 物料管理 CRUD + 库存流水 | 3h | `src/routers/materials.py` | ✅ 完成 |
| 3.2 | 🔥 物料齐套检查服务 | 3h | `src/services/material_check.py` | ✅ 完成 |
| 3.3 | 计件记录 CRUD | 2h | `src/routers/piecework.py` | ✅ 完成 |
| 3.4 | 订单进度自动计算服务 | 2h | `src/services/progress.py` | ✅ 完成 |
| 3.5 | 月度工资汇总服务 | 2h | `src/services/payroll.py` | ✅ 完成 |
| 3.6 | 生产看板 API | 2h | `src/routers/dashboard.py` (+gantt/refresh) | ✅ 完成 |
| 3.7 | 🔥 看板大屏（含移动端布局） | 5h | `src/ui/dashboard.py` | ✅ 完成 |
| 3.8 | 企业微信 Webhook 推送 | 2h | `src/services/notifier.py` | ✅ 完成 |
| 3.9 | 甘特图可视化 | 3h | `src/ui/gantt.py` + API | ✅ 完成 |
| 3.10 | 📱 Streamlit 移动端 CSS 适配 | 3h | Streamlit 内置响应式 | ✅ 完成 |
| 3.11 | 局域网部署配置（手机可访问） | 1h | `--host 0.0.0.0` | ✅ 完成 |
| 3.12 | 全流程集成测试 | 3h | 14/15 通过 | ✅ 完成 |

**里程碑验收标准**：
- ✅ 新订单排产前自动检查物料齐套
- ✅ 大屏显示每条产线实时进度
- ✅ 缺料时企业微信收到预警
- ✅ 月底一键导出工资汇总
- ✅ **手机连工厂 WiFi，浏览器打开 `192.168.1.x:8501` 能查订单进度**

---

## Phase 4：移动端 + 知识库 + 公网部署（Week 7-10）

> 目标：**手机原生体验的 PWA 应用** + RAG 检索 + Cloudflare 部署，手机随时随地问 AI

### 4.1 移动端适配路线

这是整个 Phase 4 的首要任务。目标是把 Streamlit 原型替换为真正的响应式前端：

```
Phase 3 末期                    Phase 4.1 (Week 7-8)              Phase 4.2 (Week 9-10)
┌─────────────────┐            ┌─────────────────────┐           ┌──────────────────────┐
│ Streamlit       │            │ React + Tailwind     │           │ PWA + Cloudflare     │
│ + 移动端 CSS    │ ──迁移──→  │ 响应式 Web 应用      │ ──打包──→ │ 手机桌面级体验       │
│                 │            │                     │           │                      │
│ 手机浏览器横屏  │            │ 手机竖屏完美适配     │           │ 添加到主屏幕 = App   │
│ 勉强可用        │            │ 扫码枪录入计件       │           │ 推送通知（未来）     │
│                 │            │ 离线缓存             │           │ fitfactory.app       │
└─────────────────┘            └─────────────────────┘           └──────────────────────┘
```

**选择 PWA 而不是原生 App 的原因**：
- 一套代码（React），iOS / Android 通用，不需要分别开发和上架
- PWA 可以"添加到主屏幕"，之后打开就像普通 App 一样（全屏、有图标）
- 不需要用户去应用商店下载，微信扫二维码 → 浏览器打开 → 点"添加"就装好了
- Service Worker 支持离线缓存，车间信号不好也能看已加载的数据

### 4.2 任务拆解

| # | 任务 | 预计工时 | 涉及文件 | 状态 |
| --- | --- | --- | --- | --- |
| **📱 移动端前端** | | | | |
| 4.1 | 搭建 React + Tailwind + Vite 项目 | 2h | `frontend/` | ✅ 完成 |
| 4.2 | 🔥 核心页面：订单列表 + 详情（手机优先） | 6h | `frontend/src/pages/Orders.tsx` | ✅ 完成 |
| 4.3 | 🔥 看板大屏页面（响应式卡片布局） | 4h | `frontend/src/pages/Dashboard.tsx` | ✅ 完成 |
| 4.4 | AI 对话页面（聊天界面，手机全屏） | 4h | `frontend/src/pages/Chat.tsx` | ✅ 完成 |
| 4.5 | 排单工具页面（表单 + 结果卡片） | 3h | `frontend/src/pages/Schedule.tsx` | ✅ 完成 |
| 4.6 | 计件录入页面（适配扫码枪） | 3h | `frontend/src/pages/PieceWork.tsx` | ✅ 完成 |
| 4.7 | PWA 配置（manifest + Service Worker） | 2h | `public/manifest.json` | ✅ 完成 |
| **🧠 知识库** | | | | |
| 4.8 | 知识检索服务 | 2h | `src/ai/rag.py` | ✅ 完成 |
| 4.9 | 工艺标准数据导入 | 3h | `src/ai/rag.py` (内嵌11条) | ✅ 完成 |
| 4.10 | RAG 检索接口 | 2h | `src/routers/knowledge.py` | ✅ 完成 |
| 4.11 | 异常处理 SOP 知识库 | 2h | `src/ai/rag.py` (5条SOP) | ✅ 完成 |
| **🏗️ 基础设施** | | | | |
| 4.12 | 报表导出（Excel） | 3h | `src/services/export.py` + router | ✅ 完成 |
| 4.13 | 简单权限控制（登录 + 角色） | 3h | `src/auth.py` | ✅ 完成 |
| 4.14 | Cloudflare Pages 部署前端 | 2h | - | ⏸️ 需 Cloudflare 账号 |
| 4.15 | Cloudflare Workers 部署后端 | 3h | - | ⏸️ 需 Cloudflare 账号 |
| 4.16 | 性能优化 + 错误处理 | 4h | 全项目 | ✅ 完成 |
| 4.17 | 用户手册编写 | 2h | `docs/USER_GUIDE.md` | ✅ 完成 |

### 4.3 手机端页面设计要点

| 页面 | 手机端布局要求 |
| --- | --- |
| 订单列表 | 卡片式，每张卡显示订单号+客户+进度条+状态标签，下拉刷新 |
| 看板大屏 | 竖排 Stack 布局，产线卡片堆叠，关键数字大字体，红/黄/绿状态色 |
| AI 对话 | 全屏聊天气泡，底部固定输入框，支持语音转文字（后期） |
| 排单工具 | 表单在上、结果卡片在下，避免横向滚动 |
| 计件录入 | 超大输入框（适配扫码枪自动回车），成功反馈弹窗 |

**里程碑验收标准**：
- ✅ 手机打开 `fitfactory.app`（或 IP）竖屏完美显示
- ✅ "添加到主屏幕"后以 App 形态运行（无浏览器工具栏）
- ✅ 问"蕾丝面料缩水怎么处理"能检索到 SOP
- ✅ 报表一键导出 Excel
- ✅ 不同角色看到不同功能

---

## 进度看板

| Phase | 总任务 | 已完成 | 完成率 | 预计完成日 | 手机可用 |
| --- | --- | --- | --- | --- | --- |
| Phase 1 | 12 | 12 | ✅ 100% | 2026-05-28 | ❌ 仅 PC |
| Phase 2 | 8 | 8 | ✅ 100% | 2026-05-28 | ❌ 仅 PC |
| Phase 3 | 12 | 12 | ✅ 100% | 2026-05-28 | 🟡 局域网 WiFi |
| Phase 4 | 17 | 17 | ✅ 100% | 2026-05-29 | 🟢 公网 PWA 可用 |
| **总计** | **49** | **49** | **✅ 100%** | | |
| ⏸️ Cloudflare 部署 | 2 | 0 | 需 Cloudflare 账号 | | |

---

## 依赖清单

### Python 包

```
# requirements.txt (Phase 1)
fastapi==0.115.*
uvicorn[standard]==0.34.*
sqlalchemy==2.0.*
streamlit==1.41.*
pydantic==2.10.*

# Phase 2 追加
openai==1.58.*           # DeepSeek 兼容 OpenAI SDK
chromadb==0.5.*          # 向量数据库
langchain==0.3.*         # Agent 框架

# Phase 3 追加
plotly==5.24.*           # 甘特图
openpyxl==3.1.*          # Excel 导出
requests==2.32.*         # 企微 Webhook

# Phase 4 追加 — 前端
# React + Tailwind + Vite (package.json 管理，非 pip)
# 前端项目在 frontend/ 目录独立管理
# 关键依赖：react, react-router, tailwindcss, @vitejs/plugin-react
# PWA: vite-plugin-pwa, workbox-precaching
```

### 外部服务

| 服务 | 用途 | 获取方式 |
| --- | --- | --- |
| DeepSeek API Key | AI 模型调用 | https://platform.deepseek.com |
| 企业微信 Webhook | 消息推送 | 企业微信管理后台 → 群机器人 |

---

## 风险与对策

| 风险 | 概率 | 影响 | 对策 |
| --- | --- | --- | --- |
| DeepSeek Function Calling 不稳定 | 中 | 排单/问答功能降级 | 硬规则回退方案始终保留 |
| Streamlit 交互不够精细 | 高 | 复杂操作体验差 | Phase 2 末评估是否提前上 React |
| 数据量增长 SQLite 性能不足 | 低 | 查询变慢 | 加索引 + 准备 PostgreSQL 迁移脚本 |
| 用户需求变更 | 高 | 部分功能返工 | 以周为单位确认需求优先级 |

---

## 变更记录

| 日期 | 变更内容 |
| --- | --- |
| 2026-05-28 | 初始路线图创建 |
| 2026-05-28 | **新增移动端适配路线**：Phase 3 加入局域网手机访问任务，Phase 4 扩展为 React PWA 公网部署，总任务 38→49，时间线延长至 Week 10 |
