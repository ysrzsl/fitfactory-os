# 🗄️ 数据库设计文档 — FitFactory OS

> 最后更新：2026-05-29 · 18 张表  
> 新增: workers / salary_adjustments / customers / cost_sheets / qc_records / equipment / maintenance_records / process_templates

---

## 1. ER 关系总图

```
                    ┌──────────────────┐
                    │     styles       │
                    │ (产品款式主数据)  │
                    │                  │
                    │ style_code (PK)  │
                    │ standard_capacity│
                    │ bom_data (JSON)  │
                    └────────┬─────────┘
                             │ 1:N
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              │
    ┌─────────────┐  ┌───────────────┐      │
    │   orders    │  │   materials   │      │
    │ (客户订单)  │  │ (物料主数据)  │      │
    │             │  │               │      │
    │ style_code  │  │ material_code │      │
    │ (FK)        │  │ (PK)          │      │
    └──────┬──────┘  └───────┬───────┘      │
           │                 │              │
     ┌─────┼─────┐           │              │
     │     │     │           ▼              │
     ▼     ▼     ▼  ┌────────────────┐     │
┌─────────┐ ┌──────────────┐ │inventory_tx   │     │
│ piece_  │ │   order_     │ │(入库/出库)    │     │
│ work_   │ │  progress    │ └───────┬───────┘     │
│ records │ │ (进度快照)   │         │             │
│         │ │              │         ▼             │
│order(FK)│ │order(FK)     │ ┌────────────────┐    │
└─────────┘ └──────────────┘ │material_avail  │    │
                             │(物料齐套检查)  │    │
                             │order(FK)       │    │
                             │material(FK)    │────┘
                             └────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│ production_lines    │     │   exception_events   │
│ (生产线)            │     │ (异常事件记录)       │
│                     │     │                      │
│ line_name (PK)      │     │ order_number (FK)    │
│ available_from      │     │ event_type           │
│ status              │     │ severity             │
└─────────────────────┘     └──────────────────────┘

┌──────────────────────┐
│  craft_standards     │
│  (工艺标准知识库)    │
│                      │
│  style_code          │
│  embedding_id ───────┼──→ Chroma 向量库
│  quality_check_points│
└──────────────────────┘
```

---

## 2. 表详细定义

### 2.1 styles — 产品款式表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | 自增主键 |
| style_code | VARCHAR(50) | UNIQUE, NOT NULL | 款号，如 "NK-2026-001" |
| style_name | VARCHAR(100) | | 款式名称，如 "蕾丝无钢圈内衣" |
| category | VARCHAR(50) | | 类别：内衣/文胸/睡衣/运动 |
| standard_capacity | JSON | NOT NULL | `{"产线A": 500, "产线B": 450}` 件/天 |
| bom_data | JSON | | `{"面料A":"0.15米", "肩带":"2根"}` |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | | 最后更新时间 |

```sql
CREATE TABLE styles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    style_code VARCHAR(50) UNIQUE NOT NULL,
    style_name VARCHAR(100),
    category VARCHAR(50),
    standard_capacity JSON NOT NULL,
    bom_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

---

### 2.2 production_lines — 生产线表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | 自增主键 |
| line_name | VARCHAR(50) | UNIQUE, NOT NULL | 如 "缝制一车间A线" |
| operator_count | INTEGER | | 产线人数 |
| status | VARCHAR(20) | DEFAULT 'IDLE' | IDLE/BUSY/MAINTAIN |
| available_from | DATE | | 产线释放日期，排产核心字段 |
| created_at | DATETIME | DEFAULT NOW | |
| updated_at | DATETIME | | |

```sql
CREATE TABLE production_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_name VARCHAR(50) UNIQUE NOT NULL,
    operator_count INTEGER,
    status VARCHAR(20) DEFAULT 'IDLE',
    available_from DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

---

### 2.3 orders — 客户订单表 ⭐ 核心

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| order_number | VARCHAR(50) | UNIQUE, NOT NULL | 订单号，如 "SO-20260501" |
| customer_name | VARCHAR(100) | | 客户名称 |
| style_code | VARCHAR(50) | FK → styles.style_code | 关联款号 |
| total_quantity | INTEGER | NOT NULL | 订单总件数 |
| delivery_date | DATE | NOT NULL | 客户要求交期 |
| assigned_line | VARCHAR(50) | | AI 排产分配产线 |
| start_date | DATE | | 预计开工日期（排产后填入） |
| end_date | DATE | | 预计完工日期（排产后填入） |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING/SCHEDULED/IN_PROGRESS/COMPLETED/DELAYED |
| priority | VARCHAR(10) | DEFAULT 'NORMAL' | HIGH/NORMAL/LOW |
| created_at | DATETIME | DEFAULT NOW | |
| updated_at | DATETIME | | |

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(100),
    style_code VARCHAR(50) REFERENCES styles(style_code),
    total_quantity INTEGER NOT NULL,
    delivery_date DATE NOT NULL,
    assigned_line VARCHAR(50),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'PENDING',
    priority VARCHAR(10) DEFAULT 'NORMAL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

**状态流转**：
```
PENDING ──→ SCHEDULED ──→ IN_PROGRESS ──→ COMPLETED
   │                          │
   └──────────────────────────┴──→ DELAYED (延期)
```

---

### 2.4 materials — 物料主数据表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| material_code | VARCHAR(50) | UNIQUE, NOT NULL | "FAB-LACE-001" |
| material_name | VARCHAR(100) | | "蕾丝面料" |
| category | VARCHAR(50) | | 面料/辅料/包装/耗材 |
| unit | VARCHAR(20) | | 米/根/个/卷/公斤 |
| safety_stock | FLOAT | DEFAULT 0 | 安全库存警戒线 |
| current_stock | FLOAT | DEFAULT 0 | 当前库存 |
| supplier_name | VARCHAR(100) | | 供应商 |
| lead_time_days | INTEGER | DEFAULT 7 | 采购提前期（天） |
| created_at | DATETIME | DEFAULT NOW | |

---

### 2.5 inventory_transactions — 库存流水表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| material_code | VARCHAR(50) | FK | |
| transaction_type | VARCHAR(20) | | IN / OUT |
| quantity | FLOAT | NOT NULL | 数量 |
| related_order | VARCHAR(50) | | 出库关联订单 |
| operator | VARCHAR(50) | | 操作人 |
| created_at | DATETIME | DEFAULT NOW | |

---

### 2.6 material_availability — 物料齐套检查结果

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| order_number | VARCHAR(50) | FK | |
| material_code | VARCHAR(50) | | |
| required_qty | FLOAT | | 需要多少 |
| available_qty | FLOAT | | 库存可用多少 |
| shortage_qty | FLOAT | | 缺多少 |
| status | VARCHAR(20) | | READY / SHORTAGE |
| check_time | DATETIME | DEFAULT NOW | |

---

### 2.7 piece_work_records — 计件工单表 ⭐

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| worker_name | VARCHAR(50) | NOT NULL | 工人姓名 |
| worker_id | VARCHAR(30) | | 工号 |
| order_number | VARCHAR(50) | FK | |
| style_code | VARCHAR(50) | | |
| production_line | VARCHAR(50) | | 所在产线 |
| process_name | VARCHAR(50) | | 工序：裁剪/缝制/质检/包装 |
| quantity | INTEGER | NOT NULL | 当日产量 |
| unit_price | FLOAT | | 工序单价 |
| work_date | DATE | NOT NULL | |
| recorded_by | VARCHAR(50) | | 记录人 |
| created_at | DATETIME | DEFAULT NOW | |

---

### 2.8 order_progress — 订单进度快照

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| order_number | VARCHAR(50) | FK, UNIQUE | |
| completed_qty | INTEGER | DEFAULT 0 | 已完成件数 |
| in_progress_qty | INTEGER | DEFAULT 0 | 在制件数 |
| remaining_qty | INTEGER | DEFAULT 0 | 剩余件数 |
| completion_rate | FLOAT | DEFAULT 0.0 | 完成百分比 |
| last_updated | DATETIME | DEFAULT NOW | |

---

### 2.9 craft_standards — 工艺标准知识库

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| style_code | VARCHAR(50) | | |
| process_name | VARCHAR(100) | | 工序名称 |
| machine_type | VARCHAR(50) | | 所需设备 |
| standard_time_sec | FLOAT | | 标准工时（秒/件） |
| quality_check_points | TEXT | | 质检要点（全文检索/向量化） |
| difficulty_level | INTEGER | | 难度 1-5 |
| embedding_id | VARCHAR(100) | | Chroma 向量 ID |
| created_at | DATETIME | DEFAULT NOW | |

---

### 2.10 exception_events — 异常事件表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PK, AUTO | |
| order_number | VARCHAR(50) | FK | |
| event_type | VARCHAR(50) | | DELAY/QUALITY_ISSUE/MACHINE_FAULT/INSERTION |
| description | TEXT | | |
| severity | VARCHAR(20) | | LOW/MEDIUM/HIGH/CRITICAL |
| resolved | BOOLEAN | DEFAULT FALSE | |
| created_at | DATETIME | DEFAULT NOW | |

---

## 3. 索引策略

```sql
-- 高频查询字段加速
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_delivery ON orders(delivery_date);
CREATE INDEX idx_orders_style ON orders(style_code);
CREATE INDEX idx_orders_line ON orders(assigned_line);

CREATE INDEX idx_piecework_date ON piece_work_records(work_date);
CREATE INDEX idx_piecework_worker ON piece_work_records(worker_name);
CREATE INDEX idx_piecework_order ON piece_work_records(order_number);

CREATE INDEX idx_material_code ON materials(material_code);
CREATE INDEX idx_inventory_mat ON inventory_transactions(material_code);
CREATE INDEX idx_inventory_date ON inventory_transactions(created_at);

CREATE INDEX idx_exception_order ON exception_events(order_number);
CREATE INDEX idx_exception_type ON exception_events(event_type);
```

---

## 4. 迁移记录

| 日期 | 版本 | 变更内容 |
| --- | --- | --- |
| 2026-05-28 | v0.1 | 初始 10 张表设计，基于需求分析 |
