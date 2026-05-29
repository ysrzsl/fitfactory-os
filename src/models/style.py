"""产品款式表"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base


class Style(Base):
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    style_code = Column(String(50), unique=True, nullable=False, comment="款号，如 NK-2026-001")
    style_name = Column(String(100), comment="款式名称，如 蕾丝无钢圈内衣")
    category = Column(String(50), comment="类别：内衣/文胸/睡衣/运动")

    # 核心排产数据：不同产线做该款式的日产能（件/天）
    # 格式：{"缝制一车间A线": 500, "缝制二车间B线": 450}
    standard_capacity = Column(JSON, nullable=False, comment="各产线标准日产能")

    # BOM (物料清单) 简化版
    # 格式：{"蕾丝面料": "0.15米", "肩带": "2根", "背钩": "1个"}
    bom_data = Column(JSON, comment="物料清单，单件耗料")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Style {self.style_code}: {self.style_name}>"
