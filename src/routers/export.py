"""报表导出 API"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from src.main import get_db
from src.services.export import export_orders, export_payroll, export_materials

router = APIRouter()


@router.get("/orders")
def download_orders(db: Session = Depends(get_db)):
    """导出订单 Excel"""
    excel = export_orders(db)
    return StreamingResponse(excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=orders.xlsx"})


@router.get("/payroll")
def download_payroll(year: int = Query(None), month: int = Query(None), db: Session = Depends(get_db)):
    """导出工资 Excel"""
    if year is None: year = date.today().year
    if month is None: month = date.today().month
    excel = export_payroll(db, year, month)
    return StreamingResponse(excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=payroll_{year}{month:02d}.xlsx"})


@router.get("/materials")
def download_materials(db: Session = Depends(get_db)):
    """导出物料库存 Excel"""
    excel = export_materials(db)
    return StreamingResponse(excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=materials.xlsx"})
