"""
综合工资计算服务
工资 = 底薪 + 计件工资 + 奖惩 ± 补贴 - 社保
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from calendar import monthrange
from src.models.piece_work import PieceWorkRecord
from src.models.worker import Worker
from src.models.salary_adjustment import SalaryAdjustment


def calc_monthly_payroll(year: int, month: int, db: Session) -> list[dict]:
    """按月计算所有工人综合工资"""
    _, last_day = monthrange(year, month)
    start = date(year, month, 1)
    end = date(year, month, last_day)

    workers = db.query(Worker).all()
    if not workers:
        return []

    # 预加载当月计件汇总
    piece_sums = {}
    rows = db.query(
        PieceWorkRecord.worker_name,
        func.sum(PieceWorkRecord.quantity).label("total_qty"),
        func.sum(PieceWorkRecord.quantity * PieceWorkRecord.unit_price).label("total_piece_pay"),
    ).filter(PieceWorkRecord.work_date.between(start, end)).group_by(PieceWorkRecord.worker_name).all()
    for r in rows:
        piece_sums[r.worker_name] = {"qty": r.total_qty or 0, "pay": round(r.total_piece_pay or 0, 2)}

    # 预加载当月奖惩
    adj_sums = {}
    adjs = db.query(
        SalaryAdjustment.worker_name,
        func.sum(SalaryAdjustment.amount).label("total_adj"),
    ).filter(SalaryAdjustment.adjust_date.between(start, end)).group_by(SalaryAdjustment.worker_name).all()
    for a in adjs:
        adj_sums[a.worker_name] = round(a.total_adj or 0, 2)

    result = []
    for w in workers:
        piece = piece_sums.get(w.worker_name, {"qty": 0, "pay": 0})
        adj = adj_sums.get(w.worker_name, 0)
        base = w.base_salary or 2500
        si = w.social_insurance or 400

        gross = base + piece["pay"] + (adj if adj > 0 else 0)
        net = gross - abs(adj) if adj < 0 else gross
        net -= si

        result.append({
            "worker_name": w.worker_name,
            "worker_id": w.worker_id,
            "position": w.position,
            "base_salary": base,
            "piece_qty": piece["qty"],
            "piece_pay": piece["pay"],
            "adjustments": adj,
            "social_insurance": si,
            "gross_pay": round(gross, 2),
            "net_pay": round(net, 2),
        })

    result.sort(key=lambda x: x["net_pay"], reverse=True)

    # 异常检测
    nets = [w["net_pay"] for w in result]
    if nets:
        avg = sum(nets) / len(nets)
        for w in result:
            dev = round((w["net_pay"] - avg) / avg * 100, 1) if avg > 0 else 0
            w["deviation_pct"] = dev
            w["anomaly"] = abs(dev) > 30

    return result


def get_worker_detail(worker_name: str, year: int, month: int, db: Session) -> dict:
    """单人工资明细"""
    _, last_day = monthrange(year, month)
    start, end = date(year, month, 1), date(year, month, last_day)

    w = db.query(Worker).filter(Worker.worker_name == worker_name).first()
    if not w: return {}

    # 计件明细
    pieces = db.query(PieceWorkRecord).filter(
        PieceWorkRecord.worker_name == worker_name,
        PieceWorkRecord.work_date.between(start, end),
    ).order_by(PieceWorkRecord.work_date).all()

    piece_total = sum(p.quantity * (p.unit_price or 0) for p in pieces)

    # 奖惩明细
    adjs = db.query(SalaryAdjustment).filter(
        SalaryAdjustment.worker_name == worker_name,
        SalaryAdjustment.adjust_date.between(start, end),
    ).order_by(SalaryAdjustment.adjust_date).all()

    adj_total = sum(a.amount for a in adjs)

    gross = (w.base_salary or 2500) + piece_total + max(0, adj_total)
    net = gross + min(0, adj_total) - (w.social_insurance or 400)

    return {
        "worker_name": w.worker_name, "worker_id": w.worker_id, "position": w.position,
        "base_salary": w.base_salary,
        "piece_records": [{"date": str(p.work_date), "order": p.order_number, "process": p.process_name, "qty": p.quantity, "price": p.unit_price, "pay": round(p.quantity*(p.unit_price or 0),2)} for p in pieces],
        "piece_total": round(piece_total, 2),
        "adjustments": [{"date": str(a.adjust_date), "type": a.adjust_type, "amount": a.amount, "reason": a.reason} for a in adjs],
        "adj_total": round(adj_total, 2),
        "social_insurance": w.social_insurance or 400,
        "gross_pay": round(gross, 2),
        "net_pay": round(net, 2),
    }
