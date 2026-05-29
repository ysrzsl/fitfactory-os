"""物料管理 API（含库存流水 + 齐套检查）"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from src.main import get_db
from src.models.material import Material
from src.models.inventory import InventoryTransaction

router = APIRouter()

class MaterialCreate(BaseModel):
    material_code: str; material_name: str | None = None; category: str | None = None
    unit: str | None = None; safety_stock: float = 0; current_stock: float = 0
    supplier_name: str | None = None; lead_time_days: int = 7

class MaterialUpdate(BaseModel):
    material_name: str | None = None; category: str | None = None; unit: str | None = None
    safety_stock: float | None = None; current_stock: float | None = None
    supplier_name: str | None = None; lead_time_days: int | None = None

class MaterialOut(BaseModel):
    id: int; material_code: str; material_name: str | None; category: str | None
    unit: str | None; safety_stock: float; current_stock: float
    supplier_name: str | None; lead_time_days: int; created_at: datetime | None
    class Config: from_attributes = True

class TransactionCreate(BaseModel):
    material_code: str; transaction_type: str; quantity: float
    related_order: str | None = None; operator: str | None = None

class TransactionOut(BaseModel):
    id: int; material_code: str; transaction_type: str; quantity: float
    related_order: str | None; operator: str | None; created_at: datetime | None
    class Config: from_attributes = True

# ── 列表 + 固定路径（必须在 /{code} 之前）───────────────
@router.get("/", response_model=List[MaterialOut])
def list_materials(category: str | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(Material)
    if category: q = q.filter(Material.category == category)
    return q.all()

@router.get("/shortage-alert")
def shortage_alert(db: Session = Depends(get_db)):
    items = db.query(Material).filter(Material.current_stock < Material.safety_stock).all()
    return [{"material_code": m.material_code, "material_name": m.material_name,
             "current_stock": m.current_stock, "safety_stock": m.safety_stock,
             "shortage": round(m.safety_stock - m.current_stock, 2),
             "unit": m.unit, "supplier": m.supplier_name} for m in items]

@router.get("/check/{order_number}")
def check_material(order_number: str, db: Session = Depends(get_db)):
    from src.models.order import Order
    from src.services.material_check import check_order_material
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order: raise HTTPException(404, f"订单 {order_number} 不存在")
    return check_order_material(order_number, order.style_code, order.total_quantity, db)

@router.get("/purchase-suggestion")
def purchase_suggestion(db: Session = Depends(get_db)):
    from src.services.material_check import get_purchase_suggestions
    return get_purchase_suggestions(db)

# ── 按编码操作 ──────────────────────────────────────────
@router.get("/{code}", response_model=MaterialOut)
def get_material(code: str, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.material_code == code).first()
    if not m: raise HTTPException(404, f"物料 {code} 不存在")
    return m

@router.post("/", response_model=MaterialOut, status_code=201)
def create_material(data: MaterialCreate, db: Session = Depends(get_db)):
    if db.query(Material).filter(Material.material_code == data.material_code).first():
        raise HTTPException(409, f"物料 {data.material_code} 已存在")
    m = Material(**data.model_dump()); db.add(m); db.commit(); db.refresh(m)
    return m

@router.put("/{code}", response_model=MaterialOut)
def update_material(code: str, data: MaterialUpdate, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.material_code == code).first()
    if not m: raise HTTPException(404, f"物料 {code} 不存在")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(m, k, v)
    db.commit(); db.refresh(m); return m

@router.delete("/{code}", status_code=204)
def delete_material(code: str, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.material_code == code).first()
    if not m: raise HTTPException(404); db.delete(m); db.commit()

# ── 库存流水 ────────────────────────────────────────────
@router.get("/transactions/", response_model=List[TransactionOut])
def list_transactions(material_code: str | None = Query(None), limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(InventoryTransaction)
    if material_code: q = q.filter(InventoryTransaction.material_code == material_code)
    return q.order_by(InventoryTransaction.created_at.desc()).limit(limit).all()

@router.post("/transactions/in", response_model=TransactionOut)
def stock_in(data: TransactionCreate, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.material_code == data.material_code).first()
    if not m: raise HTTPException(404, f"物料 {data.material_code} 不存在")
    m.current_stock += data.quantity
    tx = InventoryTransaction(material_code=data.material_code, transaction_type="IN",
        quantity=data.quantity, related_order=data.related_order, operator=data.operator)
    db.add(tx); db.commit(); db.refresh(tx); return tx

@router.post("/transactions/out", response_model=TransactionOut)
def stock_out(data: TransactionCreate, db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.material_code == data.material_code).first()
    if not m: raise HTTPException(404, f"物料 {data.material_code} 不存在")
    if m.current_stock < data.quantity:
        raise HTTPException(400, f"库存不足：需要 {data.quantity}{m.unit}，当前 {m.current_stock}{m.unit}")
    m.current_stock -= data.quantity
    tx = InventoryTransaction(material_code=data.material_code, transaction_type="OUT",
        quantity=data.quantity, related_order=data.related_order, operator=data.operator)
    db.add(tx); db.commit(); db.refresh(tx); return tx
