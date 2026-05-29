"""工资 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from src.main import get_db
from src.services.payroll import calc_monthly_payroll, get_worker_detail

router = APIRouter()


@router.get("/monthly")
def monthly_payroll(year: int = Query(None), month: int = Query(None), db: Session = Depends(get_db)):
    """月度工资汇总（人员列表）"""
    if year is None: year = date.today().year
    if month is None: month = date.today().month
    workers = calc_monthly_payroll(year, month, db)
    total = sum(w["net_pay"] for w in workers)
    return {
        "year": year, "month": month,
        "worker_count": len(workers),
        "total_payroll": round(total, 2),
        "workers": workers,
    }


@router.get("/worker/{worker_name}")
def worker_detail(worker_name: str, year: int = Query(None), month: int = Query(None), db: Session = Depends(get_db)):
    """单人工资明细"""
    if year is None: year = date.today().year
    if month is None: month = date.today().month
    return get_worker_detail(worker_name, year, month, db)
