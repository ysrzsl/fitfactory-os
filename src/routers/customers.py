"""客户管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from src.main import get_db
from src.models.customer import Customer

router = APIRouter()

class CustomerCreate(BaseModel):
    customer_name: str; level: str = "B"; contact_person: str | None = None
    contact_phone: str | None = None; address: str | None = None; notes: str | None = None

class CustomerUpdate(BaseModel):
    level: str | None = None; contact_person: str | None = None
    contact_phone: str | None = None; address: str | None = None
    outstanding: float | None = None; notes: str | None = None

class CustomerOut(BaseModel):
    id: int; customer_name: str; level: str; contact_person: str | None
    contact_phone: str | None; address: str | None
    total_orders: int; total_amount: float; outstanding: float; notes: str | None
    class Config: from_attributes = True


@router.get("/", response_model=List[CustomerOut])
def list_customers(level: str | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(Customer).order_by(Customer.level.asc(), Customer.total_amount.desc())
    if level: q = q.filter(Customer.level == level)
    return q.all()

@router.post("/", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.customer_name == data.customer_name).first():
        raise HTTPException(409, f"客户 {data.customer_name} 已存在")
    c = Customer(**data.model_dump()); db.add(c); db.commit(); db.refresh(c); return c

@router.put("/{name}", response_model=CustomerOut)
def update_customer(name: str, data: CustomerUpdate, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_name == name).first()
    if not c: raise HTTPException(404); 
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(c, k, v)
    db.commit(); db.refresh(c); return c

@router.delete("/{name}", status_code=204)
def delete_customer(name: str, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_name == name).first()
    if not c: raise HTTPException(404)
    db.delete(c); db.commit()
