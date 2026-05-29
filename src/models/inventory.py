"""入库/出库流水表"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_code = Column(String(50), ForeignKey("materials.material_code"), comment="物料编码")
    transaction_type = Column(String(20), comment="IN / OUT")
    quantity = Column(Float, nullable=False, comment="数量")
    related_order = Column(String(50), comment="关联订单号（出库时）")
    operator = Column(String(50), comment="操作人")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<InventoryTx {self.transaction_type} {self.material_code} x{self.quantity}>"
