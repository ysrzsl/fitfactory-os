"""
订单进度自动计算服务
从计件记录汇总 → 更新 order_progress 表
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.piece_work import PieceWorkRecord
from src.models.order import Order
from src.models.order_progress import OrderProgress


def update_order_progress(order_number: str, db: Session) -> OrderProgress:
    """汇总计件记录，更新订单进度"""
    total_completed = db.query(func.sum(PieceWorkRecord.quantity)).filter(
        PieceWorkRecord.order_number == order_number
    ).scalar() or 0

    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        return None

    remaining = max(0, order.total_quantity - total_completed)
    rate = round(total_completed / order.total_quantity * 100, 1) if order.total_quantity > 0 else 0

    progress = db.query(OrderProgress).filter(
        OrderProgress.order_number == order_number
    ).first()

    if progress:
        progress.completed_qty = total_completed
        progress.remaining_qty = remaining
        progress.completion_rate = rate
    else:
        progress = OrderProgress(
            order_number=order_number,
            completed_qty=total_completed,
            remaining_qty=remaining,
            completion_rate=rate,
        )
        db.add(progress)

    # 自动更新订单状态
    if rate >= 100:
        order.status = "COMPLETED"
    elif rate > 0 and order.status == "SCHEDULED":
        order.status = "IN_PROGRESS"

    db.commit()
    return progress


def update_all_progress(db: Session) -> int:
    """批量更新所有在产订单进度"""
    active_orders = db.query(Order).filter(
        Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
    ).all()

    count = 0
    for order in active_orders:
        update_order_progress(order.order_number, db)
        count += 1
    return count
