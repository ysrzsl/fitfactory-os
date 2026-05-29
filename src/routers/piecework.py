"""计件工单 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from datetime import date, datetime

from src.main import get_db
from src.models.piece_work import PieceWorkRecord

router = APIRouter()


class PieceWorkCreate(BaseModel):
    worker_name: str
    worker_id: str | None = None
    order_number: str
    style_code: str | None = None
    production_line: str | None = None
    process_name: str | None = None
    quantity: int
    unit_price: float | None = None
    work_date: date
    recorded_by: str | None = None


class PieceWorkOut(BaseModel):
    id: int
    worker_name: str
    worker_id: str | None
    order_number: str
    style_code: str | None
    production_line: str | None
    process_name: str | None
    quantity: int
    unit_price: float | None
    work_date: date
    recorded_by: str | None
    created_at: datetime | None
    class Config: from_attributes = True


@router.get("/", response_model=List[PieceWorkOut])
def list_records(
    work_date: date | None = Query(None),
    worker_name: str | None = Query(None),
    order_number: str | None = Query(None),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(PieceWorkRecord)
    if work_date: q = q.filter(PieceWorkRecord.work_date == work_date)
    if worker_name: q = q.filter(PieceWorkRecord.worker_name == worker_name)
    if order_number: q = q.filter(PieceWorkRecord.order_number == order_number)
    return q.order_by(PieceWorkRecord.work_date.desc()).limit(limit).all()


@router.post("/", response_model=PieceWorkOut, status_code=201)
def create_record(data: PieceWorkCreate, db: Session = Depends(get_db)):
    r = PieceWorkRecord(**data.model_dump())
    db.add(r); db.commit(); db.refresh(r)
    return r


@router.post("/batch", status_code=201)
def batch_create(records: List[PieceWorkCreate], db: Session = Depends(get_db)):
    """批量导入计件记录"""
    items = [PieceWorkRecord(**r.model_dump()) for r in records]
    db.add_all(items); db.commit()
    return {"count": len(items)}


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    r = db.query(PieceWorkRecord).filter(PieceWorkRecord.id == record_id).first()
    if not r: raise HTTPException(404)
    db.delete(r); db.commit()
