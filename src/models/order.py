"""客户订单表 —— 核心"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, comment="订单号 SO-20260501")
    customer_name = Column(String(100), comment="客户名称")
    style_code = Column(String(50), ForeignKey("styles.style_code"), comment="关联款号")

    total_quantity = Column(Integer, nullable=False, comment="订单总件数")
    delivery_date = Column(Date, nullable=False, comment="客户要求交期")

    # 排产结果字段（由排单引擎填入）
    assigned_line = Column(String(50), nullable=True, comment="分配的产线")
    start_date = Column(Date, nullable=True, comment="预计开工日期")
    end_date = Column(Date, nullable=True, comment="预计完工日期")

    status = Column(String(20), default="PENDING",
                    comment="PENDING/SCHEDULED/IN_PROGRESS/COMPLETED/DELAYED")
    priority = Column(String(10), default="NORMAL", comment="HIGH/NORMAL/LOW")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Order {self.order_number}: {self.customer_name} [{self.status}]>"
