"""维修保养记录表"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from .base import Base

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equip_code = Column(String(50), nullable=False, index=True, comment="设备编号")
    record_type = Column(String(20), comment="MAINTAIN(保养)/REPAIR(维修)")
    description = Column(String(300), comment="问题描述/保养内容")
    cost = Column(Float, default=0, comment="费用")
    technician = Column(String(50), comment="维修/保养人")
    record_date = Column(Date, nullable=False)
    downtime_hours = Column(Float, default=0, comment="停机时长(小时)")
    created_at = Column(DateTime, server_default=func.now())
