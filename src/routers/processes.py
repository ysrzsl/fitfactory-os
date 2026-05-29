"""工艺路线 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.main import get_db
from src.models.process_template import ProcessTemplate

router = APIRouter()

class TemplateCreate(BaseModel): style_code: str; steps: list[dict]

@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    return db.query(ProcessTemplate).all()

@router.get("/{style_code}")
def get_template(style_code: str, db: Session = Depends(get_db)):
    t = db.query(ProcessTemplate).filter(ProcessTemplate.style_code == style_code).first()
    if not t: raise HTTPException(404)
    return {"style_code": t.style_code, "steps": t.steps, "total_time_min": t.total_time_min}

@router.post("/", status_code=201)
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    total = sum(s.get("time_min", 0) for s in data.steps)
    t = ProcessTemplate(style_code=data.style_code, steps=data.steps, total_time_min=total)
    db.add(t); db.commit(); db.refresh(t); return t

@router.delete("/{style_code}", status_code=204)
def delete_template(style_code: str, db: Session = Depends(get_db)):
    t = db.query(ProcessTemplate).filter(ProcessTemplate.style_code == style_code).first()
    if not t: raise HTTPException(404)
    db.delete(t); db.commit()
