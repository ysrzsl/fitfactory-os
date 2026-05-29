"""质量管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from datetime import date, datetime
from src.main import get_db
from src.models.qc_record import QCRecord

router = APIRouter()


class QCCreate(BaseModel):
    order_number: str; inspect_date: date; batch_size: int; defect_count: int = 0
    defect_type: str | None = None; severity: str = "MINOR"
    inspector: str | None = None; result: str = "PASS"; notes: str | None = None


class QCOut(BaseModel):
    id: int; order_number: str; inspect_date: date; batch_size: int; defect_count: int
    defect_rate: float; defect_type: str | None; severity: str
    inspector: str | None; result: str; notes: str | None
    class Config: from_attributes = True


@router.get("/", response_model=List[QCOut])
def list_qc(order_number: str | None = Query(None), limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(QCRecord).order_by(QCRecord.inspect_date.desc())
    if order_number: q = q.filter(QCRecord.order_number == order_number)
    return q.limit(limit).all()


@router.post("/", response_model=QCOut, status_code=201)
def create_qc(data: QCCreate, db: Session = Depends(get_db)):
    rate = round(data.defect_count / data.batch_size * 100, 2) if data.batch_size > 0 else 0
    r = QCRecord(**data.model_dump(), defect_rate=rate); db.add(r); db.commit(); db.refresh(r); return r


@router.get("/stats")
def qc_stats(db: Session = Depends(get_db)):
    """AQL 质量统计"""
    total = db.query(QCRecord).count()
    if total == 0: return {"message": "暂无质检记录"}
    pass_count = db.query(QCRecord).filter(QCRecord.result == "PASS").count()
    avg_rate = db.query(func.avg(QCRecord.defect_rate)).scalar() or 0

    # 缺陷类型分布
    defects = db.query(QCRecord.defect_type, func.count()).filter(
        QCRecord.defect_count > 0
    ).group_by(QCRecord.defect_type).order_by(func.count().desc()).all()

    return {
        "total_inspections": total,
        "pass_rate": round(pass_count / total * 100, 1),
        "avg_defect_rate": round(avg_rate, 2),
        "defect_types": [{"type": d[0] or "未分类", "count": d[1]} for d in defects],
    }
