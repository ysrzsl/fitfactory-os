"""质检记录表"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from .base import Base

class QCRecord(Base):
    __tablename__ = "qc_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), nullable=False, index=True)
    inspect_date = Column(Date, nullable=False)
    batch_size = Column(Integer, default=0, comment="抽检批量")
    defect_count = Column(Integer, default=0, comment="不合格数")
    defect_rate = Column(Float, default=0, comment="不合格率%")
    defect_type = Column(String(50), comment="缺陷类型：尺寸/色差/线头/污渍/破洞/其他")
    severity = Column(String(10), default="MINOR", comment="MAJOR/MINOR/CRITICAL")
    inspector = Column(String(50), comment="质检员")
    result = Column(String(20), default="PASS", comment="PASS/REWORK/REJECT")
    notes = Column(String(300))
    created_at = Column(DateTime, server_default=func.now())
