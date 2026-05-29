"""生产排单 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from src.main import get_db
from src.models.style import Style
from src.models.production_line import ProductionLine
from src.models.order import Order
from src.services.scheduler import auto_schedule, simulate_insertion

router = APIRouter()


# ── Schemas ─────────────────────────────────────────────
class ScheduleRequest(BaseModel):
    order_number: str


class BatchScheduleRequest(BaseModel):
    order_numbers: list[str]


class InsertionSimRequest(BaseModel):
    style_code: str
    quantity: int
    desired_start_date: date


# ── 内部辅助函数 ────────────────────────────────────────
def _load_styles(db: Session) -> dict:
    """加载所有款式及其产能到内存字典"""
    styles = {}
    for s in db.query(Style).all():
        styles[s.style_code] = {
            "style_name": s.style_name,
            "standard_capacity": s.standard_capacity or {},
            "bom_data": s.bom_data or {},
        }
    return styles


def _load_lines(db: Session) -> dict:
    """加载所有产线到内存字典"""
    lines = {}
    for l in db.query(ProductionLine).all():
        lines[l.line_name] = {
            "status": l.status,
            "available_from": l.available_from,
            "operator_count": l.operator_count,
        }
    return lines


def _load_existing_orders(db: Session) -> list[dict]:
    """加载已排产但未完成的订单"""
    orders = db.query(Order).filter(
        Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
        Order.assigned_line.isnot(None),
    ).all()
    return [
        {
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "assigned_line": o.assigned_line,
            "start_date": o.start_date,
            "end_date": o.end_date,
        }
        for o in orders
    ]


# ── 排单接口 ────────────────────────────────────────────
@router.post("/auto")
def schedule_order(req: ScheduleRequest, db: Session = Depends(get_db)):
    """对新订单执行自动排产"""
    order = db.query(Order).filter(Order.order_number == req.order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"订单 {req.order_number} 不存在")
    if order.status not in ("PENDING",):
        raise HTTPException(status_code=400, detail=f"订单状态为 {order.status}，无法排产")

    styles = _load_styles(db)
    lines = _load_lines(db)
    existing = _load_existing_orders(db)

    result = auto_schedule(
        order_data={
            "order_number": order.order_number,
            "style_code": order.style_code,
            "total_quantity": order.total_quantity,
            "delivery_date": order.delivery_date,
            "priority": order.priority or "NORMAL",
        },
        styles=styles,
        lines=lines,
        existing_orders=existing,
    )

    # 如果有推荐方案，写入订单
    if result.recommended:
        order.assigned_line = result.recommended.line_name
        order.start_date = result.recommended.start_date
        order.end_date = result.recommended.end_date
        order.status = "SCHEDULED"
        db.commit()

    return {
        "order_number": result.order_number,
        "recommended": {
            "line": result.recommended.line_name if result.recommended else None,
            "start_date": str(result.recommended.start_date) if result.recommended else None,
            "end_date": str(result.recommended.end_date) if result.recommended else None,
            "work_days": result.recommended.work_days if result.recommended else 0,
            "daily_capacity": result.recommended.daily_capacity if result.recommended else 0,
            "on_time": result.recommended.on_time if result.recommended else False,
        } if result.recommended else None,
        "alternatives": [
            {
                "line": a.line_name,
                "start_date": str(a.start_date),
                "end_date": str(a.end_date),
                "work_days": a.work_days,
                "on_time": a.on_time,
            }
            for a in result.alternatives
        ],
        "conflicts": [
            {
                "order_number": c.order_number,
                "customer_name": c.customer_name,
                "overlap_days": c.overlap_days,
            }
            for c in result.conflicts
        ],
        "warnings": result.warnings,
    }


@router.post("/batch")
def schedule_batch(req: BatchScheduleRequest, db: Session = Depends(get_db)):
    """批量排产多个订单（按优先级顺序）"""
    results = []
    for on in req.order_numbers:
        order = db.query(Order).filter(Order.order_number == on).first()
        if not order:
            results.append({"order_number": on, "error": "不存在"})
            continue

        styles = _load_styles(db)
        lines = _load_lines(db)

        # 每次排完要刷新已排产列表（因为前一个订单可能占用产线时间）
        existing = _load_existing_orders(db)

        result = auto_schedule(
            order_data={
                "order_number": order.order_number,
                "style_code": order.style_code,
                "total_quantity": order.total_quantity,
                "delivery_date": order.delivery_date,
                "priority": order.priority or "NORMAL",
            },
            styles=styles,
            lines=lines,
            existing_orders=existing,
        )

        if result.recommended:
            order.assigned_line = result.recommended.line_name
            order.start_date = result.recommended.start_date
            order.end_date = result.recommended.end_date
            order.status = "SCHEDULED"
            db.commit()

        results.append({
            "order_number": on,
            "assigned_line": result.recommended.line_name if result.recommended else None,
            "start_date": str(result.recommended.start_date) if result.recommended else None,
            "end_date": str(result.recommended.end_date) if result.recommended else None,
            "on_time": result.recommended.on_time if result.recommended else False,
            "warnings": result.warnings,
        })

    return {"scheduled": len([r for r in results if "error" not in r]), "results": results}


@router.post("/simulate-insertion")
def simulate_insert(req: InsertionSimRequest, db: Session = Depends(get_db)):
    """插单模拟"""
    styles = _load_styles(db)
    lines = _load_lines(db)
    existing = _load_existing_orders(db)

    return simulate_insertion(
        style_code=req.style_code,
        quantity=req.quantity,
        desired_start=req.desired_start_date,
        styles=styles,
        lines=lines,
        existing_orders=existing,
    )


@router.get("/conflicts")
def list_conflicts(db: Session = Depends(get_db)):
    """检查所有已排产订单是否存在撞单"""
    orders = db.query(Order).filter(
        Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
        Order.assigned_line.isnot(None),
        Order.start_date.isnot(None),
        Order.end_date.isnot(None),
    ).order_by(Order.start_date.asc()).all()

    conflicts = []
    for i, o1 in enumerate(orders):
        for o2 in orders[i + 1:]:
            if o1.assigned_line != o2.assigned_line:
                continue
            if o1.start_date <= o2.end_date and o1.end_date >= o2.start_date:
                overlap_start = max(o1.start_date, o2.start_date)
                overlap_end = min(o1.end_date, o2.end_date)
                conflicts.append({
                    "line": o1.assigned_line,
                    "order_a": o1.order_number,
                    "order_b": o2.order_number,
                    "overlap_start": str(overlap_start),
                    "overlap_end": str(overlap_end),
                    "overlap_days": (overlap_end - overlap_start).days + 1,
                })

    return {"conflict_count": len(conflicts), "conflicts": conflicts}


@router.get("/capacity-warning")
def capacity_warning(days: int = 14, db: Session = Depends(get_db)):
    """未来 N 天产能预警"""
    from collections import defaultdict
    from datetime import date as dt, timedelta

    today = dt.today()
    end = today + timedelta(days=days)

    orders = db.query(Order).filter(
        Order.assigned_line.isnot(None),
        Order.start_date.isnot(None),
        Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
        Order.start_date <= end,
        Order.end_date >= today,
    ).all()

    # 按产线统计每天工作量
    line_load = defaultdict(lambda: defaultdict(int))
    for o in orders:
        for d in range(max((o.start_date - today).days, 0),
                       min((o.end_date - today).days + 1, days)):
            day = today + timedelta(days=d)
            line_load[o.assigned_line][str(day)] += o.total_quantity

    warnings = []
    styles = _load_styles(db)
    for line_name, day_loads in line_load.items():
        daily_cap = 0
        for s in styles.values():
            cap = s.get("standard_capacity", {}).get(line_name, 0)
            if cap > daily_cap:
                daily_cap = cap

        if daily_cap == 0:
            continue

        for day_str, load in day_loads.items():
            if load > daily_cap * 0.9:  # 超过 90% 产能
                warnings.append({
                    "line": line_name,
                    "date": day_str,
                    "load": load,
                    "capacity": daily_cap,
                    "utilization": round(load / daily_cap * 100, 1),
                })

    return {"warning_count": len(warnings), "warnings": warnings}
