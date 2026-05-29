"""款式管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from src.main import get_db
from src.models.style import Style

router = APIRouter()


# ── Pydantic Schemas ────────────────────────────────────
class StyleCreate(BaseModel):
    style_code: str
    style_name: str | None = None
    category: str | None = None
    standard_capacity: dict  # {"产线A": 500, "产线B": 450}
    bom_data: dict | None = None


class StyleUpdate(BaseModel):
    style_name: str | None = None
    category: str | None = None
    standard_capacity: dict | None = None
    bom_data: dict | None = None


class StyleOut(BaseModel):
    id: int
    style_code: str
    style_name: str | None
    category: str | None
    standard_capacity: dict
    bom_data: dict | None
    created_at: datetime | None

    class Config:
        from_attributes = True


# ── Routes ──────────────────────────────────────────────
@router.get("/", response_model=List[StyleOut])
def list_styles(db: Session = Depends(get_db)):
    """获取所有款式"""
    return db.query(Style).all()


@router.get("/{style_code}", response_model=StyleOut)
def get_style(style_code: str, db: Session = Depends(get_db)):
    """按款号获取款式详情"""
    style = db.query(Style).filter(Style.style_code == style_code).first()
    if not style:
        raise HTTPException(status_code=404, detail=f"款式 {style_code} 不存在")
    return style


@router.post("/", response_model=StyleOut, status_code=201)
def create_style(data: StyleCreate, db: Session = Depends(get_db)):
    """新增款式"""
    if db.query(Style).filter(Style.style_code == data.style_code).first():
        raise HTTPException(status_code=409, detail=f"款式 {data.style_code} 已存在")
    style = Style(**data.model_dump())
    db.add(style)
    db.commit()
    db.refresh(style)
    return style


@router.put("/{style_code}", response_model=StyleOut)
def update_style(style_code: str, data: StyleUpdate, db: Session = Depends(get_db)):
    """更新款式"""
    style = db.query(Style).filter(Style.style_code == style_code).first()
    if not style:
        raise HTTPException(status_code=404, detail=f"款式 {style_code} 不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(style, key, val)
    db.commit()
    db.refresh(style)
    return style


@router.delete("/{style_code}", status_code=204)
def delete_style(style_code: str, db: Session = Depends(get_db)):
    """删除款式"""
    style = db.query(Style).filter(Style.style_code == style_code).first()
    if not style:
        raise HTTPException(status_code=404, detail=f"款式 {style_code} 不存在")
    db.delete(style)
    db.commit()
