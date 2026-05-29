"""异常事件记录表"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class ExceptionEvent(Base):
    __tablename__ = "exception_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), ForeignKey("orders.order_number"), comment="关联订单")
    event_type = Column(String(50), comment="DELAY/QUALITY_ISSUE/MACHINE_FAULT/INSERTION")
    description = Column(Text, comment="异常描述")
    severity = Column(String(20), comment="LOW/MEDIUM/HIGH/CRITICAL")
    resolved = Column(Boolean, default=False, comment="是否已解决")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<ExceptionEvent {self.event_type} [{self.severity}] resolved={self.resolved}>"
