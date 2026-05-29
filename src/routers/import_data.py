"""CSV/Excel 批量导入 API"""
import csv, io, json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from src.main import get_db

router = APIRouter()

# ── 模板定义 ────────────────────────────────────────────
TEMPLATES = {
    "orders": {
        "headers": ["order_number", "customer_name", "style_code", "total_quantity", "delivery_date", "priority"],
        "sample": ["SO-20260701", "金狐狸服饰", "NK-2026-001", "5000", "2026-07-15", "NORMAL"],
    },
    "styles": {
        "headers": ["style_code", "style_name", "category", "standard_capacity"],
        "sample": ["NK-2026-004", "无缝运动内衣", "内衣", '{"缝制一车间A线":400}'],
    },
    "materials": {
        "headers": ["material_code", "material_name", "category", "unit", "safety_stock", "current_stock", "supplier_name", "lead_time_days"],
        "sample": ["MAT-FAB-004", "弹力网眼面料", "面料", "米", "200", "800", "绍兴纺织", "7"],
    },
    "piecework": {
        "headers": ["worker_name", "order_number", "quantity", "process_name", "unit_price", "work_date"],
        "sample": ["张丽", "SO-20260701", "200", "缝制", "0.5", "2026-07-02"],
    },
}


@router.get("/template/{table}")
def download_template(table: str):
    """下载 CSV 导入模板（含表头 + 示例数据）"""
    if table not in TEMPLATES:
        raise HTTPException(400, f"不支持的表: {table}。支持: {list(TEMPLATES.keys())}")

    t = TEMPLATES[table]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(t["headers"])
    writer.writerow(t["sample"])
    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=template_{table}.csv"}
    )


@router.post("/{table}")
async def import_table(table: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """导入 CSV/Excel 到指定表"""
    content = await file.read()
    rows = _parse_csv(content)
    if not rows:
        raise HTTPException(400, "文件为空或格式错误")

    count = 0
    if table == "orders":
        count = _import_orders(rows, db)
    elif table == "styles":
        count = _import_styles(rows, db)
    elif table == "materials":
        count = _import_materials(rows, db)
    elif table == "piecework":
        count = _import_piecework(rows, db)
    else:
        raise HTTPException(400, f"不支持的表: {table}")

    return {"table": table, "count": count, "message": f"成功导入 {count} 条记录"}


def _parse_csv(content: bytes) -> list[dict]:
    """解析 CSV 内容"""
    text = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


def _import_orders(rows: list[dict], db: Session) -> int:
    from src.models.order import Order
    count = 0
    for r in rows:
        if not r.get('order_number'): continue
        existing = db.query(Order).filter(Order.order_number == r['order_number']).first()
        if existing: continue
        try:
            order = Order(
                order_number=r['order_number'],
                customer_name=r.get('customer_name', ''),
                style_code=r.get('style_code', ''),
                total_quantity=int(r.get('total_quantity', 0)),
                delivery_date=datetime.strptime(r.get('delivery_date', '2026-01-01'), '%Y-%m-%d').date(),
                priority=r.get('priority', 'NORMAL'),
                status='PENDING',
            )
            db.add(order); count += 1
        except Exception: continue
    db.commit()
    return count


def _import_styles(rows: list[dict], db: Session) -> int:
    from src.models.style import Style
    count = 0
    for r in rows:
        if not r.get('style_code'): continue
        existing = db.query(Style).filter(Style.style_code == r['style_code']).first()
        if existing: continue
        try:
            cap = json.loads(r.get('standard_capacity', '{}'))
        except: cap = {}
        style = Style(style_code=r['style_code'], style_name=r.get('style_name',''), category=r.get('category',''), standard_capacity=cap)
        db.add(style); count += 1
    db.commit()
    return count


def _import_materials(rows: list[dict], db: Session) -> int:
    from src.models.material import Material
    count = 0
    for r in rows:
        if not r.get('material_code'): continue
        existing = db.query(Material).filter(Material.material_code == r['material_code']).first()
        if existing: continue
        m = Material(
            material_code=r['material_code'], material_name=r.get('material_name',''), category=r.get('category',''),
            unit=r.get('unit',''), safety_stock=float(r.get('safety_stock',0)),
            current_stock=float(r.get('current_stock',0)), supplier_name=r.get('supplier_name',''),
        )
        db.add(m); count += 1
    db.commit()
    return count


def _import_piecework(rows: list[dict], db: Session) -> int:
    from src.models.piece_work import PieceWorkRecord
    count = 0
    for r in rows:
        try:
            pw = PieceWorkRecord(
                worker_name=r['worker_name'], order_number=r.get('order_number',''), quantity=int(r.get('quantity',0)),
                process_name=r.get('process_name',''), unit_price=float(r.get('unit_price',0)),
                work_date=datetime.strptime(r.get('work_date','2026-01-01'),'%Y-%m-%d').date(),
            )
            db.add(pw); count += 1
        except Exception: continue
    db.commit()
    return count
