"""工资调整记录表（奖惩/补贴/扣款）"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from .base import Base


class SalaryAdjustment(Base):
    __tablename__ = "salary_adjustments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_name = Column(String(50), nullable=False)
    adjust_type = Column(String(20), comment="BONUS(奖金)/PENALTY(罚款)/SUBSIDY(补贴)/OTHER")
    amount = Column(Float, nullable=False, comment="金额（正数为加，负数为扣）")
    reason = Column(String(200), comment="原因")
    adjust_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
