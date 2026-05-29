"""成本核算服务"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.order import Order
from src.models.piece_work import PieceWorkRecord
from src.models.cost_sheet import CostSheet


def calc_order_cost(order_number: str, db: Session, order_amount: float = 0, overhead: float = 0) -> CostSheet:
    """计算单张订单的成本"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order: return None

    # 人工成本 = 该订单所有计件工资汇总
    labor = db.query(func.sum(PieceWorkRecord.quantity * PieceWorkRecord.unit_price)).filter(
        PieceWorkRecord.order_number == order_number
    ).scalar() or 0

    # 物料成本 = 从款式BOM × 物料单价估算（简化版用固定值）
    # 实际可以查询 material_availability 表
    material = db.query(func.sum(func.coalesce(
        PieceWorkRecord.quantity * 0.5, 0  # 简化：每件估算0.5元物料
    ))).filter(PieceWorkRecord.order_number == order_number).scalar() or 0

    total = material + labor + overhead
    profit = order_amount - total
    rate = round(profit / order_amount * 100, 1) if order_amount > 0 else 0

    # upsert
    sheet = db.query(CostSheet).filter(CostSheet.order_number == order_number).first()
    if sheet:
        sheet.order_amount = order_amount
        sheet.material_cost = round(material, 2)
        sheet.labor_cost = round(labor, 2)
        sheet.overhead = overhead
        sheet.total_cost = round(total, 2)
        sheet.gross_profit = round(profit, 2)
        sheet.profit_rate = rate
    else:
        sheet = CostSheet(order_number=order_number, order_amount=order_amount,
                          material_cost=round(material, 2), labor_cost=round(labor, 2),
                          overhead=overhead, total_cost=round(total, 2),
                          gross_profit=round(profit, 2), profit_rate=rate)
        db.add(sheet)
    db.commit()
    return sheet


def get_all_costs(db: Session) -> list[dict]:
    """获取所有订单成本汇总"""
    sheets = db.query(CostSheet).order_by(CostSheet.gross_profit.desc()).all()
    return [
        {"order_number": s.order_number, "order_amount": s.order_amount,
         "material_cost": s.material_cost, "labor_cost": s.labor_cost,
         "overhead": s.overhead, "total_cost": s.total_cost,
         "gross_profit": s.gross_profit, "profit_rate": s.profit_rate}
        for s in sheets
    ]


def get_profit_summary(db: Session) -> dict:
    """毛利汇总"""
    sheets = db.query(CostSheet).all()
    if not sheets: return {"total_revenue": 0, "total_cost": 0, "total_profit": 0, "avg_rate": 0, "count": 0}
    rev = sum(s.order_amount or 0 for s in sheets)
    cost = sum(s.total_cost or 0 for s in sheets)
    profit = rev - cost
    return {
        "total_revenue": round(rev, 2), "total_cost": round(cost, 2),
        "total_profit": round(profit, 2),
        "avg_rate": round(profit / rev * 100, 1) if rev > 0 else 0,
        "count": len(sheets),
    }
