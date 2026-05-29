import sys, os

# Vercel serverless: 确保项目根目录在 Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLite 存 /tmp（Vercel serverless 唯一可写目录）
os.environ["DB_PATH"] = "/tmp/fitfactory.db"
os.environ["DATABASE_URL"] = "sqlite:////tmp/fitfactory.db"

from src.main import app
from mangum import Mangum

# 冷启动时创建表 + 填充种子数据
from src.config import DATABASE_URL
from sqlalchemy import create_engine
from src.models import Base

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

# 简单种子数据（仅首次）
from sqlalchemy.orm import Session
from src.models.style import Style
from src.models.production_line import ProductionLine
from src.models.order import Order

with Session(engine) as db:
    if db.query(Style).count() == 0:
        from datetime import date, timedelta
        today = date.today()
        db.add(Style(style_code="NK-2026-001", style_name="蕾丝无钢圈内衣", category="内衣",
                      standard_capacity={"缝制一车间A线":500,"缝制二车间B线":450}))
        db.add(Style(style_code="NK-2026-002", style_name="运动无痕文胸", category="文胸",
                      standard_capacity={"缝制一车间A线":400,"缝制二车间B线":380}))
        db.add(ProductionLine(line_name="缝制一车间A线", operator_count=25, status="IDLE"))
        db.add(ProductionLine(line_name="缝制二车间B线", operator_count=22, status="IDLE"))
        db.add(Order(order_number="SO-20260001", customer_name="演示客户", style_code="NK-2026-001",
                      total_quantity=3000, delivery_date=today+timedelta(days=20), status="PENDING"))
        db.commit()

handler = Mangum(app, lifespan="off")
