# FitFactory OS — 项目功能清单

> 服装厂智能工作台 | 60/60 任务完成 | 2026-05-29
> **公网演示**: https://ffos.ysrzsl.us.ci

---

## 一、系统概览

| 项目 | 详情 |
| --- | --- |
| 定位 | 服装厂厂长助理 AI 工作台 |
| 架构 | FastAPI + React PWA + SQLite |
| AI 引擎 | DeepSeek Chat + 9 Function Calling 工具 |
| 部署 | Railway(后端) + Vercel(前端) + Cloudflare(域名) |
| 数据表 | 18 张 |

---

## 二、功能模块

### 📅 生产排单引擎
自动排产 / 撞单检测 / 插单模拟 / 批量排产 / 产能预警 / AI 智能排序

### 📦 物料管理
物料CRUD / 入库出库 / 齐套检查(BOM核验) / 缺料预警 / 采购建议 / 仓库库位

### 📊 生产看板
全局统计 / 产线状态 / 订单追踪 / 延期预警(红黄绿) / 日报 / 甘特图 / 30秒自动刷新

### 💰 计件工资
计件录入 / 月度汇总 / 底薪+计件+奖惩-社保 = 实发 / 异常检测(偏离>30%标红)

### 📈 成本核算
物料(BOM×单价) + 人工(计件汇总) + 分摊 = 成本 / 营收 - 成本 = 毛利 / 一键核算全部

### 👥 客户管理
客户档案 / A/B/C等级 / 联系人 / 累计订单金额 / 欠款标红

### 🔍 质量管理
质检记录 / 抽检不良率 / AQL统计(合格率/不良率) / 缺陷分布排行

### 🔧 设备管理
设备台账 / 维保记录 / 保养到期预警 / 停机时长统计

### 🔗 工艺路线
款式工序模板 / 单件工时 / 质检点标注

### 📋 SOP 流程
5套标准流程(延期/质量/设备/插单/缺料) 可视化展示

### 💬 AI 智能问答
9个工具: query_database / get_order_status / simulate_insertion / get_production_lines / get_upcoming_orders / get_dashboard_stats / get_delay_warnings / run_auto_schedule / **search_knowledge(RAG)**

### 📁 报表导出
订单/工资/物料 → Excel(.xlsx)

### 🔔 消息推送
企业微信Webhook / 缺料/延期/完成/日报推送 / 本地日志

### 📥 数据导入
CSV模板下载 / 4表批量导入 / 震动反馈

---

## 三、数据模型 (18 张表)

| 表 | 说明 |
| --- | --- |
| `styles` | 款式 + BOM + 产能 |
| `production_lines` | 产线 + 状态 + 可用日期 |
| `orders` | 订单 + 交期 + 排产结果 |
| `materials` | 物料 + 库存 + 安全库存 + 仓库库位 |
| `inventory_transactions` | 出入库流水 |
| `material_availability` | 齐套检查结果 |
| `piece_work_records` | 计件工单 |
| `order_progress` | 订单进度快照 |
| `craft_standards` | 工艺标准 |
| `exception_events` | 异常事件 |
| `workers` | 工人基础信息(底薪/社保) |
| `salary_adjustments` | 奖惩记录 |
| `customers` | 客户档案(A/B/C等级) |
| `cost_sheets` | 成本核算 |
| `qc_records` | 质检记录(AQL) |
| `equipment` | 设备台账 |
| `maintenance_records` | 维保记录 |
| `process_templates` | 工艺路线模板 |

---

## 四、前端界面

### React PWA (手机优先 · iPhone 14 尺寸)

| 页面 | 移动端特性 |
| --- | --- |
| 💬 AI 助手 | 聊天气泡 + 底部固定输入 + 对话缓存 |
| 📋 订单 | 卡片列表 + 中文状态筛选 |
| 📅 排单 | 三 Tab + AI排序 |
| 📊 看板 | 响应式网格 + 红黄绿 + 自动刷新 |
| 💰 计件 | 人员排名 → 工资条明细 |
| 📈 成本 | 一键核算 + 毛利排行 |
| 👥 客户 | A/B/C分级 + 欠款标红 |
| 🔍 质量 | AQL统计 + 缺陷分布 |
| 🔧 设备 | 保养预警 + 维保记录 |
| 🔗 工艺 | 工序模板可视化 |
| 📋 SOP | 5套流程图 |
| 📥 导入 | CSV模板下载 + 批量导入 |

PC端侧边栏 + 移动端底部导航。亮色/暗色双主题。字体大中小三档。Ctrl+K全局搜索。

---

## 五、技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| AI | DeepSeek Chat (Function Calling) + RAG知识库 |
| 前端 | React 19 + TypeScript + Vite 8 + Tailwind CSS 4 |
| PWA | manifest.json + 响应式 + 离线优化 |
| 导出 | openpyxl (Excel) |
| 部署 | Railway(后端) + Vercel(前端) + Cloudflare(域名) |

---

## 六、部署地址

| 服务 | 地址 |
| --- | --- |
| 前端 | https://ffos.ysrzsl.us.ci |
| 后端 | https://fitfactory-os-production.up.railway.app |
| 代码 | https://github.com/ysrzsl/fitfactory-os |

---

*文档更新: 2026-05-29 · FitFactory OS v1.0*
