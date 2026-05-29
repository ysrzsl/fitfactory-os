"""计件工单表 —— 每个人每天做了什么工序、做了多少件"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class PieceWorkRecord(Base):
    __tablename__ = "piece_work_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_name = Column(String(50), nullable=False, comment="工人姓名")
    worker_id = Column(String(30), comment="工号")
    order_number = Column(String(50), ForeignKey("orders.order_number"), comment="关联订单")
    style_code = Column(String(50), comment="款号")
    production_line = Column(String(50), comment="所在产线")
    process_name = Column(String(50), comment="工序：裁剪/缝制/质检/包装")
    quantity = Column(Integer, nullable=False, comment="当日产量（件）")
    unit_price = Column(Float, comment="工序单价（元/件）")
    work_date = Column(Date, nullable=False, comment="工作日期")
    recorded_by = Column(String(50), comment="记录人")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<PieceWork {self.worker_name} {self.work_date}: {self.process_name} x{self.quantity}>"
