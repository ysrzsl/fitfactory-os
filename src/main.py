"""FastAPI 主入口"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL
from src.models import Base

# ── 数据库引擎 ──────────────────────────────────────────
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)

# 自动建表（开发模式，生产环境用 init_db.py）
Base.metadata.create_all(bind=engine)


# ── FastAPI 应用 ────────────────────────────────────────
app = FastAPI(
    title="FitFactory OS",
    description="服装厂智能工作台 —— 生产排单 + AI 决策辅助",
    version="0.1.0",
)

# CORS（允许 Streamlit 前端跨域调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 操作日志中间件
from src.middleware import audit_middleware
app.middleware("http")(audit_middleware)


# ── 依赖注入 ────────────────────────────────────────────
def get_db():
    """FastAPI 依赖：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── 注册路由 ────────────────────────────────────────────
from src.routers import styles, production_lines, orders, schedule, dashboard, chat, materials, piecework, payroll, knowledge, export, import_data, customers, cost, quality, equipment, processes

app.include_router(styles.router, prefix="/api/styles", tags=["款式管理"])
app.include_router(production_lines.router, prefix="/api/lines", tags=["产线管理"])
app.include_router(orders.router, prefix="/api/orders", tags=["订单管理"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["生产排单"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["生产看板"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI 助手"])
app.include_router(materials.router, prefix="/api/materials", tags=["物料管理"])
app.include_router(piecework.router, prefix="/api/piecework", tags=["计件工单"])
app.include_router(payroll.router, prefix="/api/payroll", tags=["工资管理"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(export.router, prefix="/api/export", tags=["报表导出"])
app.include_router(import_data.router, prefix="/api/import", tags=["数据导入"])
app.include_router(customers.router, prefix="/api/customers", tags=["客户管理"])
app.include_router(cost.router, prefix="/api/cost", tags=["成本核算"])
app.include_router(quality.router, prefix="/api/quality", tags=["质量管理"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["设备管理"])
app.include_router(processes.router, prefix="/api/processes", tags=["工艺路线"])


# ── 健康检查 ────────────────────────────────────────────
@app.get("/")
def root():
    return {"app": "FitFactory OS", "version": "0.1.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── 启动入口 ────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
