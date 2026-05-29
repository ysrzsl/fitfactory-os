"""成本核算 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.main import get_db
from src.services.cost import calc_order_cost, get_all_costs, get_profit_summary

router = APIRouter()


class CostCalcRequest(BaseModel):
    order_number: str
    order_amount: float = 0
    overhead: float = 0


@router.post("/calculate")
def calculate_cost(req: CostCalcRequest, db: Session = Depends(get_db)):
    """计算/更新单张订单成本"""
    sheet = calc_order_cost(req.order_number, db, req.order_amount, req.overhead)
    if not sheet: raise HTTPException(404, "订单不存在")
    return {"order_number": sheet.order_number, "total_cost": sheet.total_cost,
            "gross_profit": sheet.gross_profit, "profit_rate": sheet.profit_rate,
            "material_cost": sheet.material_cost, "labor_cost": sheet.labor_cost}


@router.get("/all")
def all_costs(db: Session = Depends(get_db)):
    return get_all_costs(db)


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return get_profit_summary(db)


@router.post("/reset")
def reset_costs(db: Session = Depends(get_db)):
    """清空所有成本数据"""
    from src.models.cost_sheet import CostSheet
    db.query(CostSheet).delete()
    db.commit()
    return {"message": "已清空，请重新核算"}
