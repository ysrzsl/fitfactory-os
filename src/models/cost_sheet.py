"""成本核算表"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .base import Base

class CostSheet(Base):
    __tablename__ = "cost_sheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    order_amount = Column(Float, default=0, comment="订单金额")
    material_cost = Column(Float, default=0, comment="物料成本")
    labor_cost = Column(Float, default=0, comment="人工成本（计件汇总）")
    overhead = Column(Float, default=0, comment="分摊费用（水电/房租等）")
    total_cost = Column(Float, default=0, comment="总成本")
    gross_profit = Column(Float, default=0, comment="毛利")
    profit_rate = Column(Float, default=0, comment="毛利率%")
    calculated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
