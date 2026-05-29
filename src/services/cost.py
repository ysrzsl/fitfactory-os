"""成本核算服务 - BOM 真实物料成本"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.order import Order
from src.models.style import Style
from src.models.piece_work import PieceWorkRecord
from src.models.cost_sheet import CostSheet

# 物料单价估算（元/单位）
MATERIAL_PRICES = {
    "蕾丝面料": 15, "弹力面料": 12, "纯棉面料": 10, "真丝面料": 30,
    "弹力网眼面料": 13, "肩带": 0.5, "背钩": 0.3, "胸垫": 1.0,
    "包装袋": 0.2, "水洗标": 0.1, "蕾丝花边": 3, "哺乳扣": 0.8,
    "吊带": 0.6, "弹力网眼": 13,
}

# 各款式估算订单金额（用于演示 · 出厂价）
ORDER_AMOUNTS = {
    "内衣": 25, "文胸": 35, "睡衣": 50,
}  # 每件售价


def calc_order_cost(order_number: str, db: Session, order_amount: float = 0, overhead: float = 0) -> CostSheet:
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order: return None

    # 人工成本（无计件数据时按 0.6元/件估算）
    labor = db.query(func.sum(PieceWorkRecord.quantity * PieceWorkRecord.unit_price)).filter(
        PieceWorkRecord.order_number == order_number
    ).scalar() or 0
    if labor == 0:
        labor = order.total_quantity * 0.6

    # 物料成本 = BOM × 单价
    material = 0
    style = db.query(Style).filter(Style.style_code == order.style_code).first()
    if style and style.bom_data:
        for mat_name, per_piece_str in style.bom_data.items():
            qty = float(str(per_piece_str).split('米')[0].split('根')[0].split('个')[0].split('片')[0].strip())
            price = next((v for k, v in MATERIAL_PRICES.items() if k in mat_name), 0.5)
            material += qty * price * order.total_quantity

    # 如果没有订单金额，按售价估算
    if order_amount <= 0 and style:
        price_per = next((v for k, v in ORDER_AMOUNTS.items() if k == style.category), 18)
        order_amount = price_per * order.total_quantity

    total = material + labor + overhead
    profit = order_amount - total
    rate = round(profit / order_amount * 100, 1) if order_amount > 0 else 0

    sheet = db.query(CostSheet).filter(CostSheet.order_number == order_number).first()
    if sheet:
        sheet.order_amount = round(order_amount, 2); sheet.material_cost = round(material, 2)
        sheet.labor_cost = round(labor, 2); sheet.overhead = overhead
        sheet.total_cost = round(total, 2); sheet.gross_profit = round(profit, 2)
        sheet.profit_rate = rate
    else:
        sheet = CostSheet(order_number=order_number, order_amount=round(order_amount, 2),
                          material_cost=round(material, 2), labor_cost=round(labor, 2),
                          overhead=overhead, total_cost=round(total, 2),
                          gross_profit=round(profit, 2), profit_rate=rate)
        db.add(sheet)
    db.commit()
    return sheet


def get_all_costs(db: Session) -> list[dict]:
    sheets = db.query(CostSheet).order_by(CostSheet.gross_profit.desc()).all()
    return [{"order_number": s.order_number, "order_amount": s.order_amount,
             "material_cost": s.material_cost, "labor_cost": s.labor_cost,
             "overhead": s.overhead, "total_cost": s.total_cost,
             "gross_profit": s.gross_profit, "profit_rate": s.profit_rate} for s in sheets]


def get_profit_summary(db: Session) -> dict:
    sheets = db.query(CostSheet).all()
    if not sheets: return {"total_revenue": 0, "total_cost": 0, "total_profit": 0, "avg_rate": 0, "count": 0}
    rev = sum(s.order_amount or 0 for s in sheets)
    cost = sum(s.total_cost or 0 for s in sheets)
    profit = rev - cost
    return {"total_revenue": round(rev, 2), "total_cost": round(cost, 2),
            "total_profit": round(profit, 2),
            "avg_rate": round(profit / rev * 100, 1) if rev > 0 else 0, "count": len(sheets)}
