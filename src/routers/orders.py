"""订单管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date, datetime

from src.main import get_db
from src.models.order import Order

router = APIRouter()


class OrderCreate(BaseModel):
    order_number: str
    customer_name: str | None = None
    style_code: str
    total_quantity: int
    delivery_date: date
    priority: str = "NORMAL"


class OrderUpdate(BaseModel):
    customer_name: str | None = None
    total_quantity: int | None = None
    delivery_date: date | None = None
    assigned_line: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None
    priority: str | None = None


class OrderOut(BaseModel):
    id: int
    order_number: str
    customer_name: str | None
    style_code: str
    total_quantity: int
    delivery_date: date
    assigned_line: str | None
    start_date: date | None
    end_date: date | None
    status: str
    priority: str
    created_at: datetime | None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[OrderOut])
def list_orders(
    status: str | None = Query(None, description="按状态筛选"),
    priority: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    if priority:
        q = q.filter(Order.priority == priority)
    return q.order_by(Order.delivery_date.asc()).all()


@router.get("/{order_number}", response_model=OrderOut)
def get_order(order_number: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"订单 {order_number} 不存在")
    return order


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    if db.query(Order).filter(Order.order_number == data.order_number).first():
        raise HTTPException(status_code=409, detail=f"订单 {data.order_number} 已存在")
    order = Order(**data.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_number}", response_model=OrderOut)
def update_order(order_number: str, data: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"订单 {order_number} 不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(order, key, val)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_number}", status_code=204)
def delete_order(order_number: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404)
    db.delete(order)
    db.commit()


@router.get("/due/upcoming", response_model=List[OrderOut])
def upcoming_due(days: int = Query(7, description="未来 N 天内到期的订单"), db: Session = Depends(get_db)):
    """查询未来 N 天内到期的订单"""
    from datetime import date as dt, timedelta
    today = dt.today()
    end = today + timedelta(days=days)
    return db.query(Order).filter(
        Order.delivery_date.between(today, end),
        Order.status != "COMPLETED"
    ).order_by(Order.delivery_date.asc()).all()
