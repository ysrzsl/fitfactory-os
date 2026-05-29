"""
物料齐套检查服务
按订单 BOM 检查所有物料库存是否满足生产需求
"""
from sqlalchemy.orm import Session
from src.models.style import Style
from src.models.material import Material
from src.models.material_availability import MaterialAvailability


def parse_bom_qty(bom_value: str) -> tuple[float, str]:
    """解析 BOM 中的用量字符串，如 '0.15米' → (0.15, '米')"""
    import re
    match = re.match(r'([\d.]+)\s*(\D+)', str(bom_value))
    if match:
        return float(match.group(1)), match.group(2)
    return 0, ''


def check_order_material(order_number: str, style_code: str, total_quantity: int, db: Session) -> dict:
    """
    检查某订单的物料是否齐套

    返回:
      {"all_ready": bool, "items": [{"material_name": str, "required": float, "available": float, "shortage": float, "status": str}]}
    """
    style = db.query(Style).filter(Style.style_code == style_code).first()
    if not style or not style.bom_data:
        return {"all_ready": True, "items": [], "message": "该款式无 BOM 数据"}

    items = []
    all_ready = True

    for material_name, bom_value in style.bom_data.items():
        per_piece, unit = parse_bom_qty(bom_value)
        required = per_piece * total_quantity

        # 模糊匹配物料名称
        material = db.query(Material).filter(
            Material.material_name.contains(material_name)
        ).first()

        available = material.current_stock if material else 0
        shortage = max(0, required - available)
        status = "READY" if shortage == 0 else "SHORTAGE"

        if status == "SHORTAGE":
            all_ready = False

        items.append({
            "material_name": material_name,
            "material_code": material.material_code if material else "未知",
            "required": round(required, 2),
            "unit": unit,
            "available": round(available, 2),
            "shortage": round(shortage, 2),
            "status": status,
        })

        # 缓存到数据库
        existing = db.query(MaterialAvailability).filter(
            MaterialAvailability.order_number == order_number,
            MaterialAvailability.material_code == (material.material_code if material else material_name),
        ).first()

        if existing:
            existing.required_qty = required
            existing.available_qty = available
            existing.shortage_qty = shortage
            existing.status = status
        else:
            db.add(MaterialAvailability(
                order_number=order_number,
                material_code=material.material_code if material else material_name,
                required_qty=required,
                available_qty=available,
                shortage_qty=shortage,
                status=status,
            ))

    db.commit()
    return {"all_ready": all_ready, "items": items}


def get_purchase_suggestions(db: Session) -> list[dict]:
    """生成采购建议：待排产订单所需物料 - 当前库存"""
    from src.models.order import Order

    pending_orders = db.query(Order).filter(Order.status == "PENDING").all()
    demand: dict[str, dict] = {}  # {material_name: {"required": float, "unit": str}}

    for order in pending_orders:
        style = db.query(Style).filter(Style.style_code == order.style_code).first()
        if not style or not style.bom_data:
            continue
        for material_name, bom_value in style.bom_data.items():
            per_piece, unit = parse_bom_qty(bom_value)
            required = per_piece * order.total_quantity
            if material_name not in demand:
                demand[material_name] = {"required": 0, "unit": unit}
            demand[material_name]["required"] += required

    suggestions = []
    for material_name, info in demand.items():
        material = db.query(Material).filter(
            Material.material_name.contains(material_name)
        ).first()
        available = material.current_stock if material else 0
        shortage = max(0, info["required"] - available)
        if shortage > 0:
            suggestions.append({
                "material_name": material_name,
                "material_code": material.material_code if material else "未知",
                "total_required": round(info["required"], 2),
                "available": round(available, 2),
                "need_purchase": round(shortage, 2),
                "unit": info["unit"],
                "supplier": material.supplier_name if material else "",
                "lead_time_days": material.lead_time_days if material else 7,
            })

    return suggestions
