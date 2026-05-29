"""
生产排单引擎 —— 核心算法（硬规则版）

排单逻辑：
  1. 查款式 → 获取各产线日产能
  2. 筛选可选产线（IDLE 或 available_from ≤ 目标开工日）
  3. 计算每条候选产线的工作天数 → 完工日期
  4. 按优先级排序：交期达标 > 产能利用率 > 产线偏好
  5. 返回推荐方案 + 备选方案 + 冲突信息
"""
import math
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScheduleCandidate:
    """单条产线的排产候选方案"""
    line_name: str
    start_date: date
    end_date: date
    work_days: int
    daily_capacity: int
    on_time: bool          # 是否满足交期
    line_status: str       # 产线当前状态
    utilization: float     # 本次排入后的产能利用率


@dataclass
class ConflictInfo:
    """撞单信息"""
    order_number: str
    customer_name: str
    start_date: date
    end_date: date
    overlap_days: int


@dataclass
class ScheduleResult:
    """排单引擎输出"""
    order_number: str
    total_quantity: int
    delivery_date: date
    recommended: Optional[ScheduleCandidate] = None
    alternatives: list[ScheduleCandidate] = field(default_factory=list)
    conflicts: list[ConflictInfo] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def calc_work_days(total_qty: int, daily_cap: int) -> int:
    """计算所需工作天数（向上取整）"""
    if daily_cap <= 0:
        return 999
    return math.ceil(total_qty / daily_cap)


def calc_end_date(start: date, work_days: int) -> date:
    """从起始日期 + 工作天数计算完工日期（含头尾）"""
    return start + timedelta(days=work_days - 1)


def detect_conflicts(
    new_start: date,
    new_end: date,
    line_name: str,
    existing_orders: list,
    exclude_order: str | None = None,
) -> list[ConflictInfo]:
    """
    检测新排产与已有排产的冲突（撞单检测）

    existing_orders: [{"order_number": str, "customer_name": str, "start_date": date, "end_date": date}, ...]
    """
    conflicts = []
    for eo in existing_orders:
        if exclude_order and eo["order_number"] == exclude_order:
            continue
        if eo.get("assigned_line") != line_name:
            continue
        if eo.get("start_date") is None or eo.get("end_date") is None:
            continue

        # 日期区间是否重叠
        if new_start <= eo["end_date"] and new_end >= eo["start_date"]:
            overlap_start = max(new_start, eo["start_date"])
            overlap_end = min(new_end, eo["end_date"])
            overlap_days = (overlap_end - overlap_start).days + 1
            conflicts.append(ConflictInfo(
                order_number=eo["order_number"],
                customer_name=eo.get("customer_name", ""),
                start_date=eo["start_date"],
                end_date=eo["end_date"],
                overlap_days=max(overlap_days, 0),
            ))

    return sorted(conflicts, key=lambda c: c.overlap_days, reverse=True)


def auto_schedule(order_data: dict, styles: dict, lines: dict, existing_orders: list) -> ScheduleResult:
    """
    核心排单算法

    参数:
      order_data: {"order_number", "style_code", "total_quantity", "delivery_date", "priority"}
      styles:     {style_code: {"standard_capacity": {"产线A": 500, ...}}}
      lines:      {line_name: {"status": "IDLE", "available_from": date(2026,6,1)}}
      existing_orders: [{"order_number", "assigned_line", "start_date", "end_date", "customer_name"}]

    返回: ScheduleResult
    """
    result = ScheduleResult(
        order_number=order_data["order_number"],
        total_quantity=order_data["total_quantity"],
        delivery_date=order_data["delivery_date"],
    )

    style_code = order_data["style_code"]
    if style_code not in styles:
        result.warnings.append(f"款式 {style_code} 不存在")
        return result

    capacities = styles[style_code].get("standard_capacity", {})
    if not capacities:
        result.warnings.append(f"款式 {style_code} 未配置标准产能")
        return result

    today = date.today()

    # 为每条产线生成候选方案
    candidates: list[ScheduleCandidate] = []
    for line_name, daily_cap in capacities.items():
        if daily_cap <= 0:
            continue

        line_info = lines.get(line_name, {})
        line_status = line_info.get("status", "IDLE")
        available_from = line_info.get("available_from", today)

        # 跳过维护中的产线
        if line_status == "MAINTAIN":
            continue

        work_days = calc_work_days(order_data["total_quantity"], daily_cap)

        # 空闲产线从今天或 available_from 开始
        # 忙碌产线从 available_from 开始
        if line_status == "IDLE":
            start = max(available_from, today) if available_from else today
        else:
            if not available_from:
                continue  # 忙碌但没有释放日期，跳过
            start = available_from

        end = calc_end_date(start, work_days)
        on_time = end <= order_data["delivery_date"]

        # 简单利用率：本次占用天数 / 未来 30 天
        utilization = work_days / 30.0

        candidates.append(ScheduleCandidate(
            line_name=line_name,
            start_date=start,
            end_date=end,
            work_days=work_days,
            daily_capacity=daily_cap,
            on_time=on_time,
            line_status=line_status,
            utilization=round(utilization, 3),
        ))

    if not candidates:
        result.warnings.append("没有可用的产线")
        return result

    # 排序：交期达标优先 → 产能利用率低优先（负载均衡）→ 工作天数少优先
    candidates.sort(key=lambda c: (
        not c.on_time,       # True 排前面
        c.utilization,       # 利用率低优先
        c.work_days,         # 天数少优先
    ))

    # 尝试 AI 排序
    try:
        candidates = _ai_rank(candidates, order_data)
    except Exception:
        pass  # AI 不可用时保留硬规则排序

    result.recommended = candidates[0]
    result.alternatives = candidates[1:]

    # 撞单检测：检查推荐方案是否与已有排产冲突
    if result.recommended:
        result.conflicts = detect_conflicts(
            result.recommended.start_date,
            result.recommended.end_date,
            result.recommended.line_name,
            existing_orders,
        )

    # 警告信息
    if result.recommended and not result.recommended.on_time:
        delay = (result.recommended.end_date - order_data["delivery_date"]).days
        result.warnings.append(f"推荐方案将延期 {delay} 天交付")
    if result.conflicts:
        result.warnings.append(f"与 {len(result.conflicts)} 张订单存在时间冲突")

    return result


def simulate_insertion(
    style_code: str,
    quantity: int,
    desired_start: date,
    styles: dict,
    lines: dict,
    existing_orders: list,
) -> dict:
    """
    插单模拟：模拟插入一张新订单后对现有排产的影响

    返回:
      {
        "can_insert": bool,
        "recommended_line": str,
        "start_date": date,
        "end_date": date,
        "affected_orders": [{"order_number": str, "original_end": date, "new_end": date, "delay_days": int}],
        "summary": str
      }
    """
    if style_code not in styles:
        return {"can_insert": False, "error": f"款式 {style_code} 不存在"}

    capacities = styles[style_code].get("standard_capacity", {})
    best_line = None
    best_start = None
    best_end = None
    min_affected = float("inf")

    for line_name, daily_cap in capacities.items():
        line_info = lines.get(line_name, {})
        if line_info.get("status") == "MAINTAIN":
            continue

        available = line_info.get("available_from", date.today())
        start = max(desired_start, available) if available else desired_start
        work_days = calc_work_days(quantity, daily_cap)
        end = calc_end_date(start, work_days)

        # 统计受影响订单数
        affected = sum(
            1 for eo in existing_orders
            if eo.get("assigned_line") == line_name
            and eo.get("start_date") and eo.get("end_date")
            and start <= eo["end_date"] and end >= eo["start_date"]
        )

        if affected < min_affected:
            min_affected = affected
            best_line = line_name
            best_start = start
            best_end = end

    if not best_line:
        return {"can_insert": False, "error": "没有可用产线"}

    # 计算受影响订单的具体情况
    affected_orders = []
    for eo in existing_orders:
        if eo.get("assigned_line") != best_line:
            continue
        if not (eo.get("start_date") and eo.get("end_date")):
            continue
        if best_start <= eo["end_date"] and best_end >= eo["start_date"]:
            push_days = (best_end - eo["start_date"]).days + 1
            new_end = eo["end_date"] + timedelta(days=push_days)
            affected_orders.append({
                "order_number": eo["order_number"],
                "customer_name": eo.get("customer_name", ""),
                "original_end": str(eo["end_date"]),
                "new_end": str(new_end),
                "delay_days": push_days,
            })

    can_insert = affected_orders == [] or all(a["delay_days"] <= 3 for a in affected_orders)

    return {
        "can_insert": can_insert,
        "recommended_line": best_line,
        "start_date": str(best_start),
        "end_date": str(best_end),
        "work_days": calc_work_days(quantity, capacities[best_line]),
        "affected_orders": affected_orders,
        "affected_count": len(affected_orders),
        "summary": f"排至 {best_line}，{best_start} → {best_end}，影响 {len(affected_orders)} 张订单"
    }


def _ai_rank(candidates: list[ScheduleCandidate], order_data: dict) -> list[ScheduleCandidate]:
    """使用 DeepSeek AI 对候选排产方案进行智能排序"""
    import json
    from src.ai.client import chat

    ctx = {
        "order": {
            "order_number": order_data["order_number"],
            "quantity": order_data["total_quantity"],
            "delivery_date": str(order_data["delivery_date"]),
            "priority": order_data.get("priority", "NORMAL"),
        },
        "candidates": [
            {
                "line": c.line_name,
                "start": str(c.start_date),
                "end": str(c.end_date),
                "work_days": c.work_days,
                "daily_capacity": c.daily_capacity,
                "on_time": c.on_time,
                "line_status": c.line_status,
                "utilization": c.utilization,
            }
            for c in candidates
        ]
    }

    prompt = f"""你是服装厂排单专家。以下是订单和候选产线方案，请按优先级排序。

排序规则：
1. 交期达标优先（on_time=true 排前面）
2. HIGH 优先级订单优先占用最早空档
3. 产线负载均衡：优先选利用率低的产线
4. 工作天数少优先

请返回 best 和 ranked 两个字段。
- best: 推荐方案的 line 名称
- ranked: 所有方案按推荐顺序排列的 line 名称列表

只返回 JSON，不要其他文字：
{{"best": "产线名", "ranked": ["产线1", "产线2", ...]}}

数据：
{json.dumps(ctx, ensure_ascii=False, indent=2)}"""

    messages = [{"role": "user", "content": prompt}]
    resp = chat(messages, tools=None, model="deepseek-chat")
    content = resp.choices[0].message.content or "{}"

    # 提取 JSON
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1].rsplit("\n```", 1)[0]

    try:
        ranking = json.loads(content)
    except json.JSONDecodeError:
        return candidates  # 解析失败，保留原顺序

    ranked_names = ranking.get("ranked", [])
    name_map = {c.line_name: c for c in candidates}
    reordered = [name_map[n] for n in ranked_names if n in name_map]
    # 补充未被 AI 排序的
    for c in candidates:
        if c not in reordered:
            reordered.append(c)
    return reordered
