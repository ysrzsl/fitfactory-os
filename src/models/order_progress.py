"""订单生产进度快照表"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class OrderProgress(Base):
    __tablename__ = "order_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), ForeignKey("orders.order_number"), unique=True, comment="关联订单")
    completed_qty = Column(Integer, default=0, comment="已完成件数")
    in_progress_qty = Column(Integer, default=0, comment="在制件数")
    remaining_qty = Column(Integer, default=0, comment="剩余件数")
    completion_rate = Column(Float, default=0.0, comment="完成百分比")
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<OrderProgress {self.order_number}: {self.completion_rate:.1f}%>"
