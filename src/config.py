"""应用配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(Path(__file__).parent.parent / ".env")

# 数据库 - SQLite 本地文件
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).parent.parent / "data" / "fitfactory.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# 确保 data 目录存在
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# DeepSeek API（Phase 2 启用）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 企业微信（Phase 3 启用）
WECOM_WEBHOOK_URL = os.getenv("WECOM_WEBHOOK_URL", "")
