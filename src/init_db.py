"""
数据库初始化脚本
用法: python -m src.init_db
      或 python src/init_db.py
"""
import os
import sys

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models import Base
from src.config import DATABASE_URL


def init_db():
    """创建所有表"""
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print(f"✅ 数据库初始化完成: {DATABASE_URL}")

    # 列出所有创建的表
    with Session(engine) as session:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 已创建 {len(tables)} 张表:")
        for t in sorted(tables):
            print(f"   - {t}")

    return engine


def reset_db():
    """危险操作：删除所有表后重建"""
    engine = create_engine(DATABASE_URL, echo=True)
    confirm = input("⚠️ 确认删除所有数据并重建？输入 YES 继续: ")
    if confirm != "YES":
        print("已取消")
        return
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("✅ 数据库已重置")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="删除所有表后重建")
    args = parser.parse_args()

    if args.reset:
        reset_db()
    else:
        init_db()
