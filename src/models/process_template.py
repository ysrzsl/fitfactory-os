"""工艺路线模板表"""
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from .base import Base

class ProcessTemplate(Base):
    __tablename__ = "process_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    style_code = Column(String(50), unique=True, nullable=False)
    # [{"step":1, "process":"裁剪", "machine":"裁床", "time_min":2, "qc_required":true}, ...]
    steps = Column(JSON, nullable=False, comment="工序步骤列表")
    total_time_min = Column(Integer, default=0, comment="单件总工时(分钟)")
    created_at = Column(DateTime, server_default=func.now())
