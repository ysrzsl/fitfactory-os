"""操作日志中间件"""
import os
from datetime import datetime
from fastapi import Request

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'audit.log')


async def audit_middleware(request: Request, call_next):
    """记录所有写操作到日志"""
    start = datetime.now()
    response = await call_next(request)
    elapsed = (datetime.now() - start).total_seconds()

    # 只记录写操作
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{start.isoformat()}] {request.method} {request.url.path} → {response.status_code} ({elapsed:.2f}s)\n")

    return response
