# 🧩 功能模块设计文档 — FitFactory OS

> 最后更新：2026-05-28  
> 维护规则：每个模块开工/完工时更新，API 变更时同步

---

## 模块总览

| 编号 | 模块 | 优先级 | 状态 | 核心价值 |
| --- | --- | --- | --- | --- |
| M1 | 📅 生产排单引擎 | P0 | 设计阶段 | 排单自动化，消除撞单 |
| M2 | 📦 物料管理 | P1 | 设计阶段 | 缺料预警，齐套检查 |
| M3 | 📊 生产进度看板 | P1 | 设计阶段 | 实时追踪，延期预警 |
| M4 | 💰 计件工资 | P2 | 设计阶段 | 工资自动汇总 |
| M5 | 💬 AI 智能问答 | P0 | 设计阶段 | 自然语言即问即答 |
| M6 | 🔔 消息推送 | P2 | 设计阶段 | 预警自动通知 |

---

## M1 📅 生产排单引擎（P0 — 核心中的核心）

### 1.1 功能清单

| 功能 | 说明 | 输入 | 输出 |
| --- | --- | --- | --- |
| 智能排产 | 新订单自动分配产线+日期 | 订单信息 | 推荐产线+开工/完工日期 |
| 撞单检测 | 两条订单抢同一产线同一时段 | 排产计划 | 冲突标记+严重程度 |
| 插单模拟 | "接这个插单会影响什么" | 插单参数 | 受影响订单列表+延期天数 |
| 产能预警 | 未来 N 天负荷超过阈值 | 时间窗口 | 超负荷产线列表 |
| 甘特图预览 | 产线排期可视化 | 产线+时间范围 | 甘特图渲染数据 |

### 1.2 排产算法

```
输入: Order { style_code, total_quantity, delivery_date, priority }

Step 1: 查款式产能
  style = styles.get(style_code)
  capacities = style.standard_capacity  # {"缝制A线": 500, "缝制B线": 450}

Step 2: 物料齐套检查
  material_status = check_material(order)  # 调用 M2

Step 3: 候选产线计算
  candidates = []
  for line_name, daily_cap in capacities:
      line = lines.get(line_name)
      work_days = ceil(total_quantity / daily_cap)
      earliest_start = max(line.available_from, today + material_lead_time)
      end_date = earliest_start + work_days - 1

      candidates.append({
          "line": line_name,
          "start": earliest_start,
          "end": end_date,
          "work_days": work_days,
          "on_time": end_date <= delivery_date,
          "material_ready": material_status.all_ready
      })

Step 4: AI 排序
  prompt = f"""
  订单 {order_number}: {total_quantity}件, 交期 {delivery_date}
  候选排产方案:
  {candidates}

  排序规则优先级:
  1. 交期达标 > 物料齐套 > 产线负载均衡
  2. HIGH 优先级订单优先占用最早空档
  """
  ranked = deepseek.rank(candidates, prompt)

Step 5: 返回最优方案
  return {
      "recommended": ranked[0],
      "alternatives": ranked[1:],
      "conflicts": detect_conflicts(ranked[0])  # 撞单检测
  }
```

### 1.3 撞单检测算法

```
def detect_conflicts(new_schedule):
  查出 new_schedule.line 上已排产的所有订单
  遍历已排产订单:
    如果日期区间重叠:
      标记冲突 → 计算重叠天数 → 列出冲突订单号
  返回冲突列表
```

### 1.4 插单模拟算法

```
def simulate_insertion(style_code, quantity, desired_start):
  1. 找到最早可用产线（同排单 Step 3）
  2. 计算本单占用的日期区间
  3. 查出该产线上该区间内所有已排产订单
  4. 这些订单全部后推 N 天
  5. 递归检查：后推的订单是否又撞了其他订单？
  6. 最终输出：
     - 本单能否排入
     - 受影响订单清单（订单号+客户+原交期+新交期+延期天数）
     - 延期订单中是否有 HIGH 优先级
     - AI 给出的建议措辞
```

### 1.5 API 设计

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/schedule/auto` | POST | 自动排产单个订单 |
| `/api/schedule/batch` | POST | 批量排产（Excel 导入） |
| `/api/schedule/simulate-insertion` | POST | 插单模拟 |
| `/api/schedule/conflicts` | GET | 查询撞单 |
| `/api/schedule/gantt` | GET | 甘特图数据 |
| `/api/schedule/capacity-warning` | GET | 产能预警 |

---

## M2 📦 物料管理（P1）

### 2.1 功能清单

| 功能 | 说明 |
| --- | --- |
| 物料主数据 CRUD | 增删改查物料信息 |
| 入库/出库记录 | 库存流水登记 |
| 齐套检查 | 按订单 BOM 检查所有物料是否够 |
| 缺料预警 | 库存 < 安全库存 → 推送到 M6 |
| 采购建议 | 待排产订单汇总物料需求 → 扣除库存 → 建议采购量 |

### 2.2 齐套检查算法

```
def check_material(order):
  style = get_style(order.style_code)
  bom = style.bom_data  # {"蕾丝面料": "0.15米/件", "肩带": "2根/件", "背钩": "1个/件"}

  results = []
  for material, per_unit in bom:
      qty_per_piece = parse_qty(per_unit)      # "0.15米" → 0.15
      unit = parse_unit(per_unit)               # "0.15米" → 米
      total_needed = qty_per_piece * order.total_quantity

      material_record = materials.get_by_name(material)
      available = material_record.current_stock
      shortage = max(0, total_needed - available)

      results.append({
          "material": material,
          "required": total_needed,
          "available": available,
          "shortage": shortage,
          "status": "READY" if shortage == 0 else "SHORTAGE"
      })

  # 缓存结果到 material_availability 表
  save_availability(order.order_number, results)

  return {
      "all_ready": all(r["status"] == "READY" for r in results),
      "details": results
  }
```

### 2.3 API 设计

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/materials` | GET/POST | 物料列表/新增 |
| `/api/materials/{code}` | GET/PUT/DELETE | 物料详情/修改/删除 |
| `/api/materials/check/{order_number}` | GET | 齐套检查 |
| `/api/inventory/in` | POST | 入库登记 |
| `/api/inventory/out` | POST | 出库登记（关联订单） |
| `/api/materials/shortage-alert` | GET | 缺料预警列表 |
| `/api/materials/purchase-suggestion` | GET | 采购建议 |

---

## M3 📊 生产进度看板（P1）

### 3.1 功能清单

| 功能 | 说明 | 刷新频率 |
| --- | --- | --- |
| 车间总览大屏 | 每条产线+当前订单+完成率 | 每 5 分钟 |
| 订单追踪 | 单笔订单各工序进度 | 实时（计件数据驱动） |
| 延期预警 | 实际进度 vs 计划偏差 > 阈值 | 每 30 分钟 |
| 日报摘要 | 今日产量/完成率/异常汇总 | 每日 18:00 自动生成 |

### 3.2 进度计算

```
def update_order_progress(order_number):
  # 从计件记录汇总
  completed = sum(
    piece_work_records
    .filter(order_number=order_number)
    .aggregate(Sum(quantity))
  )

  order = orders.get(order_number)
  progress = OrderProgress(
      order_number=order_number,
      completed_qty=completed,
      remaining_qty=order.total_quantity - completed,
      completion_rate=completed / order.total_quantity * 100,
      last_updated=now()
  )
  upsert(progress)

  # 检测延期
  expected_completed = calculate_expected(order)  # 按日期线性插值
  if completed < expected_completed * 0.9:  # 落后 10%+
      trigger_alert(order_number, "进度落后")
```

### 3.3 API 设计

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/dashboard/overview` | GET | 车间总览数据 |
| `/api/dashboard/line/{name}` | GET | 单条产线详情 |
| `/api/dashboard/order/{number}` | GET | 订单追踪详情 |
| `/api/dashboard/daily-report` | GET | 日报摘要 |
| `/api/dashboard/delays` | GET | 延期预警列表 |

---

## M4 💰 计件工资（P2）

### 4.1 功能清单

| 功能 | 说明 |
| --- | --- |
| 每日计件录入 | 支持扫码枪/Excel 导入/手动填 |
| 月度工资汇总 | 工人 × 工序 × 单价 × 数量 |
| 异常检测 | 产量暴涨/暴跌标记审查 |
| 工资条导出 | PDF/Excel |

### 4.2 工资计算

```
def calc_monthly_payroll(month):
  records = piece_work_records.filter(work_date between month_start and month_end)

  by_worker = records.group_by('worker_name').aggregate(
      total_quantity=Sum('quantity'),
      total_pay=Sum('quantity * unit_price')
  )

  # 异常检测
  for worker in by_worker:
      avg_daily = worker.total_quantity / working_days
      historical_avg = get_worker_avg(worker.name, last_3_months)
      if abs(avg_daily - historical_avg) / historical_avg > 0.3:  # 偏差 > 30%
          mark_anomaly(worker.name, month)

  return by_worker
```

### 4.3 API 设计

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/piecework/record` | POST | 录入计件 |
| `/api/piecework/batch` | POST | 批量导入 |
| `/api/payroll/monthly` | GET | 月度工资汇总 |
| `/api/payroll/worker/{name}` | GET | 单人工资明细 |
| `/api/payroll/export` | GET | 导出工资条 |

---

## M5 💬 AI 智能问答（P0）

### 5.1 架构

```
用户输入 ──→ FastAPI /chat ──→ DeepSeek Agent
                                    │
                         ┌──────────┼──────────┐
                         │          │          │
                    NL→SQL     RAG检索    Function Call
                    (查数据)   (查知识)   (复杂操作)
```

### 5.2 Agent System Prompt

```
你是服装厂厂长助理 AI。你的工作是用工厂数据回答厂长和助理的问题。

规则：
1. 数据在 SQLite 数据库中，表结构见 DATABASE.md
2. 工艺标准/异常处理 SOP 在 Chroma 向量库中
3. 回答要简洁、带具体数字、用中文
4. 涉及排产决策时，给出理由和备选方案
5. 不确定的事不要编造，说需要人工确认

可用工具：
- query_database(sql) → 执行 SQL 并返回结果
- search_knowledge(query) → 从工艺标准库检索
- get_order_status(order_number)
- simulate_insertion(style_code, quantity, date)
- get_line_efficiency(line_name, days)
- summarize_payroll(month, worker_name)
```

### 5.3 典型问答示例

| 用户问 | AI 执行 | AI 回答 |
| --- | --- | --- |
| "NK-2026-001 做到哪了" | query_database("SELECT * FROM order_progress WHERE order_number='NK-2026-001'") | "已完成 3200/5000 件（64%），缝制一车间A线，预计 12/15 完工，比计划慢 2 天" |
| "下周要交的订单有哪些" | query_database("SELECT * FROM orders WHERE delivery_date BETWEEN '2026-06-02' AND '2026-06-08'") | "3 张订单：SO-01(12/5交, 已完成80%), SO-02(12/6交, 已完成45%⚠️), SO-03(12/7交, 已完工)" |
| "这个月工资最高 5 人" | query_database("SELECT worker_name, SUM(quantity*unit_price) as total FROM piece_work_records WHERE work_date >= '2026-05-01' GROUP BY worker_name ORDER BY total DESC LIMIT 5") | "1.张丽 ¥8,520 2.王芳 ¥7,980 ..." |
| "产线A这个月效率" | get_line_efficiency("缝制一车间A线", 30) | "日均产量 480 件，标准产能 500 件/天，效率 96%，比上月提升 3%" |
| "插 3000 件 NK-002 行不行" | simulate_insertion("NK-002", 3000, "2026-06-10") | "产线A 6/10有空，需6天，6/15完工。但会影响 SO-01(延期7天🚨曼妮芬A级客户)。建议用产线B（6/20完工，晚5天但不动大客户），请确认" |

### 5.4 API 设计

| 端点 | 方法 | 说明 |
| --- | --- | --- |
| `/api/chat` | POST | 自然语言对话 |
| `/api/chat/history` | GET | 对话历史 |
| `/api/knowledge/search` | GET | 工艺知识检索（RAG） |

---

## M6 🔔 消息推送（P2）

### 6.1 推送场景

| 触发条件 | 推送内容模板 | 推送对象 | 频控 |
| --- | --- | --- | --- |
| 物料 < 安全库存 | "⚠️ {物料名} 库存仅剩 {库存} {单位}，低于安全库存 {警戒线}" | 采购/厂长 | 每天 1 次 |
| 订单延期 ≥ 2 天 | "🚨 {订单号}({客户}) 预计延期 {天数} 天，完成率 {百分比}%" | 销售/厂长 | 每天 1 次 |
| 订单完成 | "✅ {订单号}({客户}) 已完成，可安排发货" | 销售/仓库 | 实时 |
| 产线异常停机 | "🔴 {产线} 停机超 2 小时" | 厂长/主任 | 每 2 小时 |
| 日报摘要 | "📋 今日产量 {件数} 件，完成率 {百分比}%，异常 {条数} 条" | 厂长 | 每天 18:00 |
| 产能超标 | "⚠️ {产线} 未来 7 天产能利用率 {百分比}%，建议协调" | 厂长 | 实时 |

### 6.2 实现方案

```python
# 企业微信机器人 Webhook
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

def push_notification(target, message, priority):
    # target: 可映射到企业微信群/个人
    # priority: HIGH 立即推送, MEDIUM 聚合推送, LOW 日报包含
    if priority == "HIGH":
        send_wecom(message)
    elif priority == "MEDIUM":
        add_to_daily_digest(message)
    else:
        log_only(message)

def send_wecom(markdown_text):
    requests.post(WEBHOOK_URL, json={
        "msgtype": "markdown",
        "markdown": {"content": markdown_text}
    })
```

---

## 变更记录

| 日期 | 变更内容 |
| --- | --- |
| 2026-05-28 | 初始六大模块设计 |
