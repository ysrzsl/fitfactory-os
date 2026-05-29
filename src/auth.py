"""简单认证模块"""
from fastapi import HTTPException, Header
from typing import Optional

# 简单密码认证（Phase 4 版本，后续可升级为 JWT）
ADMIN_PASSWORD = "admin123"  # 生产环境请修改
VIEWER_PASSWORD = "view123"

USERS = {
    "admin": {"password": ADMIN_PASSWORD, "role": "admin"},
    "viewer": {"password": VIEWER_PASSWORD, "role": "viewer"},
}


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """验证简单的 Bearer Token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="请提供认证信息")

    # 支持 Bearer token 或 Basic auth
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        # token 格式: username:password (base64)
        import base64
        try:
            decoded = base64.b64decode(token).decode()
            username, password = decoded.split(":", 1)
        except Exception:
            raise HTTPException(status_code=401, detail="无效的认证格式")
    elif authorization.startswith("Basic "):
        import base64
        try:
            decoded = base64.b64decode(authorization[6:]).decode()
            username, password = decoded.split(":", 1)
        except Exception:
            raise HTTPException(status_code=401, detail="无效的认证格式")
    else:
        raise HTTPException(status_code=401, detail="不支持的认证方式")

    user = USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {"username": username, "role": user["role"]}
