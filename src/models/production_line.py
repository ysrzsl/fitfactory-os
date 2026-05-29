"""生产线表"""
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .base import Base


class ProductionLine(Base):
    __tablename__ = "production_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_name = Column(String(50), unique=True, nullable=False, comment="产线名称：缝制一车间A线")
    operator_count = Column(Integer, comment="产线人数")
    status = Column(String(20), default="IDLE", comment="IDLE/BUSY/MAINTAIN")

    # 产线释放日期——排产撞单检测的核心字段
    available_from = Column(Date, nullable=True, comment="产线最早可用日期")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<ProductionLine {self.line_name} [{self.status}]>"
