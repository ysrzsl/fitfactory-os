"""工艺标准知识库表"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from .base import Base


class CraftStandard(Base):
    __tablename__ = "craft_standards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    style_code = Column(String(50), comment="款号")
    process_name = Column(String(100), comment="工序名称")
    machine_type = Column(String(50), comment="所需设备")
    standard_time_sec = Column(Float, comment="标准工时（秒/件）")
    quality_check_points = Column(Text, comment="质检要点（全文检索/向量化）")
    difficulty_level = Column(Integer, comment="难度等级 1-5")
    embedding_id = Column(String(100), nullable=True, comment="Chroma 向量库中的 ID")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CraftStandard {self.style_code}/{self.process_name}>"
