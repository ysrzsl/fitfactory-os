"""生产看板 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta

from src.main import get_db
from src.models.order import Order
from src.models.order_progress import OrderProgress
from src.models.piece_work import PieceWorkRecord
from src.models.production_line import ProductionLine

router = APIRouter()


@router.get("/overview")
def dashboard_overview(db: Session = Depends(get_db)):
    """车间总览数据"""
    today = date.today()

    # 订单统计
    total_orders = db.query(Order).count()
    pending = db.query(Order).filter(Order.status == "PENDING").count()
    in_progress = db.query(Order).filter(Order.status == "IN_PROGRESS").count()
    scheduled = db.query(Order).filter(Order.status == "SCHEDULED").count()
    completed = db.query(Order).filter(Order.status == "COMPLETED").count()
    delayed = db.query(Order).filter(Order.status == "DELAYED").count()

    # 待排产订单（PENDING 状态）
    pending_orders = db.query(Order).filter(Order.status == "PENDING").count()

    # 产线状态
    lines = db.query(ProductionLine).all()
    line_summary = []
    for l in lines:
        # 该产线上正在进行的订单
        active_order = db.query(Order).filter(
            Order.assigned_line == l.line_name,
            Order.status.in_(["IN_PROGRESS", "SCHEDULED"]),
        ).first()

        line_summary.append({
            "line_name": l.line_name,
            "status": l.status,
            "operator_count": l.operator_count,
            "active_order": active_order.order_number if active_order else None,
            "active_style": active_order.style_code if active_order else None,
        })

    # 今日产量
    today_output = db.query(func.sum(PieceWorkRecord.quantity)).filter(
        PieceWorkRecord.work_date == today
    ).scalar() or 0

    # 本周到期订单
    week_end = today + timedelta(days=7)
    due_this_week = db.query(Order).filter(
        Order.delivery_date.between(today, week_end),
        Order.status != "COMPLETED",
    ).count()

    return {
        "stats": {
            "total_orders": total_orders,
            "pending": pending,
            "scheduled": scheduled,
            "in_progress": in_progress,
            "completed": completed,
            "delayed": delayed,
            "pending_schedule": pending_orders,
            "today_output": today_output,
            "due_this_week": due_this_week,
        },
        "lines": line_summary,
    }


@router.get("/order/{order_number}")
def order_tracking(order_number: str, db: Session = Depends(get_db)):
    """单个订单的进度追踪"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        return {"error": "订单不存在"}

    # 进度
    progress = db.query(OrderProgress).filter(
        OrderProgress.order_number == order_number
    ).first()

    # 各工序产量
    process_stats = db.query(
        PieceWorkRecord.process_name,
        func.sum(PieceWorkRecord.quantity).label("total")
    ).filter(
        PieceWorkRecord.order_number == order_number
    ).group_by(PieceWorkRecord.process_name).all()

    # 按日计件趋势
    from sqlalchemy import desc
    daily_records = db.query(
        PieceWorkRecord.work_date,
        func.sum(PieceWorkRecord.quantity).label("daily_total")
    ).filter(
        PieceWorkRecord.order_number == order_number
    ).group_by(PieceWorkRecord.work_date).order_by(
        PieceWorkRecord.work_date
    ).limit(30).all()

    return {
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "style_code": order.style_code,
        "total_quantity": order.total_quantity,
        "delivery_date": str(order.delivery_date),
        "assigned_line": order.assigned_line,
        "start_date": str(order.start_date) if order.start_date else None,
        "end_date": str(order.end_date) if order.end_date else None,
        "status": order.status,
        "progress": {
            "completed_qty": progress.completed_qty if progress else 0,
            "completion_rate": progress.completion_rate if progress else 0,
            "remaining_qty": progress.remaining_qty if progress else order.total_quantity,
        },
        "by_process": [{"process": p, "quantity": t} for p, t in process_stats],
        "daily_trend": [{"date": str(d), "quantity": q} for d, q in daily_records],
    }


@router.get("/delays")
def delay_warnings(db: Session = Depends(get_db)):
    """延期预警列表"""
    today = date.today()
    delayed = db.query(Order).filter(
        Order.status == "DELAYED",
    ).all()

    # 还有即将延期的（进度落后）
    at_risk = []
    orders_in_progress = db.query(Order).filter(
        Order.status.in_(["IN_PROGRESS", "SCHEDULED"]),
        Order.end_date.isnot(None),
    ).all()

    for o in orders_in_progress:
        progress = db.query(OrderProgress).filter(
            OrderProgress.order_number == o.order_number
        ).first()
        if not progress or not o.start_date:
            continue

        # 预期进度 vs 实际进度
        total_days = (o.end_date - o.start_date).days + 1
        elapsed = (today - o.start_date).days + 1
        expected_rate = min(elapsed / total_days, 1.0)
        actual_rate = progress.completion_rate / 100.0 if progress.completion_rate else 0

        if actual_rate < expected_rate * 0.8:  # 落后 20% 以上
            at_risk.append({
                "order_number": o.order_number,
                "customer_name": o.customer_name,
                "expected_rate": round(expected_rate * 100, 1),
                "actual_rate": round(actual_rate * 100, 1),
                "gap": round((expected_rate - actual_rate) * 100, 1),
                "end_date": str(o.end_date),
            })

    return {
        "delayed": [{"order_number": o.order_number, "customer": o.customer_name} for o in delayed],
        "at_risk": at_risk,
    }


@router.get("/gantt")
def gantt_data(db: Session = Depends(get_db)):
    """甘特图数据：产线 × 时间 × 订单"""
    orders = db.query(Order).filter(
        Order.assigned_line.isnot(None),
        Order.start_date.isnot(None),
        Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
    ).order_by(Order.start_date.asc()).all()

    lines = {}
    for o in orders:
        if o.assigned_line not in lines:
            lines[o.assigned_line] = []
        lines[o.assigned_line].append({
            "order_number": o.order_number,
            "customer": o.customer_name or "",
            "start": str(o.start_date),
            "end": str(o.end_date),
            "status": o.status,
            "quantity": o.total_quantity,
        })

    return {"lines": lines, "updated": str(date.today())}


@router.post("/refresh-progress")
def refresh_progress(db: Session = Depends(get_db)):
    """手动刷新所有订单进度"""
    from src.services.progress import update_all_progress
    count = update_all_progress(db)
    return {"updated": count, "message": f"已刷新 {count} 张订单进度"}


@router.get("/daily-report")
def daily_report(db: Session = Depends(get_db)):
    """今日日报"""
    today = date.today()

    today_output = db.query(func.sum(PieceWorkRecord.quantity)).filter(
        PieceWorkRecord.work_date == today
    ).scalar() or 0

    worker_count = db.query(PieceWorkRecord.worker_name).filter(
        PieceWorkRecord.work_date == today
    ).distinct().count()

    completed_today = db.query(Order).filter(
        Order.status == "COMPLETED",
    ).count()

    new_orders_today = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()

    return {
        "date": str(today),
        "today_output": today_output,
        "workers_on_duty": worker_count,
        "completed_orders_total": completed_today,
        "new_orders_today": new_orders_today,
    }
