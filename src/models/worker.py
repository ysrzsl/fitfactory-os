"""工人基础信息表"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from .base import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_name = Column(String(50), unique=True, nullable=False)
    worker_id = Column(String(30), comment="工号")
    base_salary = Column(Float, default=2500, comment="月底薪")
    social_insurance = Column(Float, default=400, comment="社保个人部分扣除")
    position = Column(String(50), comment="岗位：裁剪/缝制/质检/包装/组长")
    hire_date = Column(Date, comment="入职日期")
    created_at = Column(DateTime, server_default=func.now())
