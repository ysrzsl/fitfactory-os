"""设备管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date, datetime
from src.main import get_db
from src.models.equipment import Equipment
from src.models.maintenance import MaintenanceRecord

router = APIRouter()

class EquipCreate(BaseModel): equip_code: str; equip_name: str | None = None; equip_type: str | None = None; production_line: str | None = None; buy_date: date | None = None; maintain_interval_days: int = 30
class MaintCreate(BaseModel): equip_code: str; record_type: str; description: str | None = None; cost: float = 0; technician: str | None = None; record_date: date; downtime_hours: float = 0

@router.get("/")
def list_equip(type: str | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(Equipment)
    if type: q = q.filter(Equipment.equip_type == type)
    return q.all()

@router.post("/", status_code=201)
def create_equip(data: EquipCreate, db: Session = Depends(get_db)):
    if db.query(Equipment).filter(Equipment.equip_code == data.equip_code).first():
        raise HTTPException(409)
    e = Equipment(**data.model_dump()); db.add(e); db.commit(); db.refresh(e); return e

@router.put("/{code}")
def update_equip(code: str, status: str = Query(...), db: Session = Depends(get_db)):
    e = db.query(Equipment).filter(Equipment.equip_code == code).first()
    if not e: raise HTTPException(404)
    e.status = status; db.commit(); return {"ok": True}

@router.get("/maintenance/{equip_code}")
def list_maint(equip_code: str, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(MaintenanceRecord).filter(MaintenanceRecord.equip_code == equip_code).order_by(MaintenanceRecord.record_date.desc()).limit(limit).all()

@router.post("/maintenance", status_code=201)
def create_maint(data: MaintCreate, db: Session = Depends(get_db)):
    m = MaintenanceRecord(**data.model_dump()); db.add(m); db.commit(); db.refresh(m)
    if data.record_type == "MAINTAIN":
        e = db.query(Equipment).filter(Equipment.equip_code == data.equip_code).first()
        if e: e.last_maintain = data.record_date; db.commit()
    return m

@router.get("/alerts")
def maint_alerts(days: int = 7, db: Session = Depends(get_db)):
    """保养到期预警"""
    from datetime import timedelta
    today = date.today()
    eqs = db.query(Equipment).filter(Equipment.status != "SCRAPPED").all()
    alerts = []
    for e in eqs:
        if e.last_maintain:
            next_due = e.last_maintain + timedelta(days=e.maintain_interval_days)
            if next_due <= today + timedelta(days=days):
                alerts.append({"equip_code": e.equip_code, "equip_name": e.equip_name, "last_maintain": str(e.last_maintain), "due_date": str(next_due), "overdue": next_due <= today})
    return alerts
