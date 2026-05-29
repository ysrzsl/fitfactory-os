"""设备台账表"""
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from .base import Base

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equip_code = Column(String(50), unique=True, nullable=False, comment="设备编号 EQ-001")
    equip_name = Column(String(100), comment="设备名称")
    equip_type = Column(String(50), comment="类型：平缝机/包缝机/熨烫台/裁床/其他")
    production_line = Column(String(50), comment="所属产线")
    status = Column(String(20), default="NORMAL", comment="NORMAL/REPAIR/SCRAPPED")
    buy_date = Column(Date, comment="购置日期")
    last_maintain = Column(Date, comment="上次保养日期")
    maintain_interval_days = Column(Integer, default=30, comment="保养周期(天)")
    created_at = Column(DateTime, server_default=func.now())
