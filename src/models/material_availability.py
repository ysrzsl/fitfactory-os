"""物料齐套检查结果（缓存表）"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class MaterialAvailability(Base):
    __tablename__ = "material_availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), ForeignKey("orders.order_number"), comment="关联订单")
    material_code = Column(String(50), comment="物料编码")
    required_qty = Column(Float, comment="需要数量")
    available_qty = Column(Float, comment="库存可用数量")
    shortage_qty = Column(Float, comment="缺料数量")
    status = Column(String(20), comment="READY / SHORTAGE")
    check_time = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<MaterialAvail {self.order_number}/{self.material_code} [{self.status}]>"
