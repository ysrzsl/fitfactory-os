"""生产线管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date, datetime

from src.main import get_db
from src.models.production_line import ProductionLine

router = APIRouter()


class LineCreate(BaseModel):
    line_name: str
    operator_count: int | None = None
    status: str = "IDLE"
    available_from: date | None = None


class LineUpdate(BaseModel):
    operator_count: int | None = None
    status: str | None = None
    available_from: date | None = None


class LineOut(BaseModel):
    id: int
    line_name: str
    operator_count: int | None
    status: str
    available_from: date | None
    created_at: datetime | None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[LineOut])
def list_lines(db: Session = Depends(get_db)):
    return db.query(ProductionLine).all()


@router.get("/{line_name}", response_model=LineOut)
def get_line(line_name: str, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.line_name == line_name).first()
    if not line:
        raise HTTPException(status_code=404, detail=f"产线 {line_name} 不存在")
    return line


@router.post("/", response_model=LineOut, status_code=201)
def create_line(data: LineCreate, db: Session = Depends(get_db)):
    if db.query(ProductionLine).filter(ProductionLine.line_name == data.line_name).first():
        raise HTTPException(status_code=409, detail=f"产线 {data.line_name} 已存在")
    line = ProductionLine(**data.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@router.put("/{line_name}", response_model=LineOut)
def update_line(line_name: str, data: LineUpdate, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.line_name == line_name).first()
    if not line:
        raise HTTPException(status_code=404, detail=f"产线 {line_name} 不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(line, key, val)
    db.commit()
    db.refresh(line)
    return line


@router.delete("/{line_name}", status_code=204)
def delete_line(line_name: str, db: Session = Depends(get_db)):
    line = db.query(ProductionLine).filter(ProductionLine.line_name == line_name).first()
    if not line:
        raise HTTPException(status_code=404)
    db.delete(line)
    db.commit()
