"""客户主数据表"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(100), unique=True, nullable=False)
    level = Column(String(10), default="B", comment="A/B/C 客户等级")
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    address = Column(String(200), comment="地址")
    total_orders = Column(Integer, default=0, comment="累计订单数")
    total_amount = Column(Float, default=0, comment="累计金额")
    outstanding = Column(Float, default=0, comment="未结款项")
    notes = Column(String(500), comment="备注")
    created_at = Column(DateTime, server_default=func.now())
