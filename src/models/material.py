"""物料主数据表"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .base import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_code = Column(String(50), unique=True, nullable=False, comment="FAB-LACE-001")
    material_name = Column(String(100), comment="蕾丝面料")
    category = Column(String(50), comment="面料/辅料/包装/耗材")
    unit = Column(String(20), comment="米/根/个/卷/公斤")
    safety_stock = Column(Float, default=0, comment="安全库存警戒线")
    current_stock = Column(Float, default=0, comment="当前库存")
    supplier_name = Column(String(100), comment="供应商")
    lead_time_days = Column(Integer, default=7, comment="采购提前期（天）")
    warehouse = Column(String(50), default="主仓库", comment="所在仓库")
    location = Column(String(50), comment="库位，如 A01-03")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Material {self.material_code}: {self.material_name} [{self.current_stock}{self.unit}]>"
