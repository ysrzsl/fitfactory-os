"""
Function Calling 工具注册表
定义 AI Agent 可以调用的所有工具及其执行逻辑
"""
import json
import sys
import os
from datetime import date, datetime, timedelta
from typing import Any

# 确保项目路径可用
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ── 工具定义（OpenAI Function Calling 格式）─────────────────
TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "搜索工艺标准和 SOP 知识库。用于回答工艺问题、操作规范、异常处理流程。如'面料缩水怎么处理''设备故障怎么办''插单流程是什么'",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词，如'缩水'、'故障'、'插单流程'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "执行 SQL 查询数据库。表结构见 DATABASE.md。用于查订单状态、进度、工资、产线效率等",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL 查询语句（仅 SELECT，禁止 INSERT/UPDATE/DELETE）"}
                },
                "required": ["sql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "查询某张订单的详细状态和进度",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {"type": "string", "description": "订单号，如 SO-20260601"}
                },
                "required": ["order_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_insertion",
            "description": "模拟插入一张新订单对现有排产的影响。返回受影响订单列表和延期天数。使用前先确认款式存在",
            "parameters": {
                "type": "object",
                "properties": {
                    "style_code": {"type": "string", "description": "款号"},
                    "quantity": {"type": "integer", "description": "插单件数"},
                    "desired_start_date": {"type": "string", "description": "期望开工日期 YYYY-MM-DD"}
                },
                "required": ["style_code", "quantity", "desired_start_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_production_lines",
            "description": "获取所有产线的状态、当前负载和可用日期",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_orders",
            "description": "查询未来 N 天内需要交付的订单",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "未来天数，默认 7"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboard_stats",
            "description": "获取生产看板统计数据：总订单数、各状态数量、今日产量等",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_delay_warnings",
            "description": "获取延期和即将延期的订单列表",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_auto_schedule",
            "description": "对指定订单执行自动排产",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {"type": "string", "description": "订单号"}
                },
                "required": ["order_number"]
            }
        }
    },
]


# ── 工具执行函数 ─────────────────────────────────────────
def execute_tool(name: str, arguments: str) -> str:
    """根据工具名和参数执行对应操作，返回 JSON 字符串结果"""
    try:
        args = json.loads(arguments) if isinstance(arguments, str) else arguments
    except json.JSONDecodeError:
        args = {}

    try:
        if name == "query_database":
            return _tool_query_db(args.get("sql", ""))
        elif name == "get_order_status":
            return _tool_get_order_status(args.get("order_number", ""))
        elif name == "simulate_insertion":
            return _tool_simulate_insertion(args)
        elif name == "get_production_lines":
            return _tool_get_lines()
        elif name == "get_upcoming_orders":
            return _tool_get_upcoming(args.get("days", 7))
        elif name == "get_dashboard_stats":
            return _tool_get_stats()
        elif name == "get_delay_warnings":
            return _tool_get_delays()
        elif name == "run_auto_schedule":
            return _tool_run_schedule(args.get("order_number", ""))
        elif name == "search_knowledge":
            return _tool_search_knowledge(args.get("query", ""))
        else:
            return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ── 工具实现 ─────────────────────────────────────────────
def _get_db_session():
    """获取数据库会话"""
    from src.config import DATABASE_URL
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def _tool_query_db(sql: str) -> str:
    """执行 SQL 查询"""
    if not sql.strip().upper().startswith("SELECT"):
        return json.dumps({"error": "仅允许 SELECT 查询"}, ensure_ascii=False)

    session = _get_db_session()
    try:
        from sqlalchemy import text
        result = session.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        # 转换日期类型为字符串
        for row in data:
            for k, v in row.items():
                if isinstance(v, (date, datetime)):
                    row[k] = str(v)
        return json.dumps(data, ensure_ascii=False, default=str)
    finally:
        session.close()


def _tool_get_order_status(order_number: str) -> str:
    """查询订单详细状态"""
    session = _get_db_session()
    try:
        from src.models.order import Order
        from src.models.order_progress import OrderProgress

        order = session.query(Order).filter(Order.order_number == order_number).first()
        if not order:
            return json.dumps({"error": f"订单 {order_number} 不存在"}, ensure_ascii=False)

        progress = session.query(OrderProgress).filter(
            OrderProgress.order_number == order_number
        ).first()

        return json.dumps({
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "style_code": order.style_code,
            "total_quantity": order.total_quantity,
            "delivery_date": str(order.delivery_date),
            "assigned_line": order.assigned_line,
            "start_date": str(order.start_date) if order.start_date else None,
            "end_date": str(order.end_date) if order.end_date else None,
            "status": order.status,
            "priority": order.priority,
            "completed_qty": progress.completed_qty if progress else 0,
            "completion_rate": f"{progress.completion_rate:.1f}%" if progress and progress.completion_rate else "0%",
            "remaining_qty": progress.remaining_qty if progress else order.total_quantity,
        }, ensure_ascii=False)
    finally:
        session.close()


def _tool_search_knowledge(query: str) -> str:
    """搜索知识库"""
    from src.ai.rag import search_knowledge
    results = search_knowledge(query, top_k=3)
    if not results:
        return json.dumps({"message": "知识库中暂无相关资料，建议咨询车间组长或工艺主管"}, ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)


def _tool_simulate_insertion(args: dict) -> str:
    """插单模拟"""
    session = _get_db_session()
    try:
        from src.models.style import Style
        from src.models.production_line import ProductionLine
        from src.models.order import Order
        from src.services.scheduler import simulate_insertion as sim_insert

        styles = {}
        for s in session.query(Style).all():
            styles[s.style_code] = {"standard_capacity": s.standard_capacity or {}}

        lines = {}
        for l in session.query(ProductionLine).all():
            lines[l.line_name] = {
                "status": l.status,
                "available_from": l.available_from,
            }

        existing = [
            {
                "order_number": o.order_number,
                "customer_name": o.customer_name,
                "assigned_line": o.assigned_line,
                "start_date": o.start_date,
                "end_date": o.end_date,
            }
            for o in session.query(Order).filter(
                Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
                Order.assigned_line.isnot(None),
            ).all()
        ]

        result = sim_insert(
            style_code=args["style_code"],
            quantity=args["quantity"],
            desired_start=datetime.strptime(args["desired_start_date"], "%Y-%m-%d").date(),
            styles=styles,
            lines=lines,
            existing_orders=existing,
        )
        return json.dumps(result, ensure_ascii=False, default=str)
    finally:
        session.close()


def _tool_get_lines() -> str:
    """获取产线状态"""
    session = _get_db_session()
    try:
        from src.models.production_line import ProductionLine
        from src.models.order import Order

        lines = session.query(ProductionLine).all()
        result = []
        for l in lines:
            active = session.query(Order).filter(
                Order.assigned_line == l.line_name,
                Order.status.in_(["IN_PROGRESS", "SCHEDULED"]),
            ).first()
            result.append({
                "line_name": l.line_name,
                "status": l.status,
                "operator_count": l.operator_count,
                "available_from": str(l.available_from) if l.available_from else "今天",
                "active_order": active.order_number if active else None,
            })
        return json.dumps(result, ensure_ascii=False)
    finally:
        session.close()


def _tool_get_upcoming(days: int) -> str:
    """获取即将到期的订单"""
    session = _get_db_session()
    try:
        from src.models.order import Order
        today = date.today()
        end = today + timedelta(days=days)
        orders = session.query(Order).filter(
            Order.delivery_date.between(today, end),
            Order.status != "COMPLETED",
        ).order_by(Order.delivery_date).all()

        return json.dumps([
            {
                "order_number": o.order_number,
                "customer_name": o.customer_name,
                "delivery_date": str(o.delivery_date),
                "days_left": (o.delivery_date - today).days,
                "status": o.status,
                "priority": o.priority,
            }
            for o in orders
        ], ensure_ascii=False)
    finally:
        session.close()


def _tool_get_stats() -> str:
    """获取看板统计"""
    session = _get_db_session()
    try:
        from src.models.order import Order
        from sqlalchemy import func

        today = date.today()
        stats = {
            "total": session.query(Order).count(),
            "pending": session.query(Order).filter(Order.status == "PENDING").count(),
            "scheduled": session.query(Order).filter(Order.status == "SCHEDULED").count(),
            "in_progress": session.query(Order).filter(Order.status == "IN_PROGRESS").count(),
            "completed": session.query(Order).filter(Order.status == "COMPLETED").count(),
            "delayed": session.query(Order).filter(Order.status == "DELAYED").count(),
        }
        return json.dumps(stats, ensure_ascii=False)
    finally:
        session.close()


def _tool_get_delays() -> str:
    """获取延期预警"""
    session = _get_db_session()
    try:
        from src.models.order import Order
        from src.models.order_progress import OrderProgress

        delayed = session.query(Order).filter(Order.status == "DELAYED").all()
        at_risk = []

        in_progress = session.query(Order).filter(
            Order.status.in_(["IN_PROGRESS", "SCHEDULED"]),
            Order.end_date.isnot(None),
        ).all()

        today = date.today()
        for o in in_progress:
            progress = session.query(OrderProgress).filter(
                OrderProgress.order_number == o.order_number
            ).first()
            if not progress or not o.start_date:
                continue

            total_days = (o.end_date - o.start_date).days + 1
            elapsed = (today - o.start_date).days + 1
            expected_rate = min(elapsed / total_days, 1.0)
            actual_rate = progress.completion_rate / 100.0 if progress.completion_rate else 0

            if actual_rate < expected_rate * 0.8:
                at_risk.append({
                    "order_number": o.order_number,
                    "customer_name": o.customer_name,
                    "expected_rate": f"{expected_rate * 100:.1f}%",
                    "actual_rate": f"{actual_rate * 100:.1f}%",
                    "gap": f"{(expected_rate - actual_rate) * 100:.1f}%",
                })

        return json.dumps({
            "delayed": [{"order_number": o.order_number, "customer": o.customer_name} for o in delayed],
            "at_risk": at_risk,
        }, ensure_ascii=False)
    finally:
        session.close()


def _tool_run_schedule(order_number: str) -> str:
    """执行自动排产"""
    session = _get_db_session()
    try:
        from src.models.order import Order
        from src.models.style import Style
        from src.models.production_line import ProductionLine
        from src.services.scheduler import auto_schedule

        order = session.query(Order).filter(Order.order_number == order_number).first()
        if not order:
            return json.dumps({"error": f"订单 {order_number} 不存在"}, ensure_ascii=False)

        styles = {}
        for s in session.query(Style).all():
            styles[s.style_code] = {"standard_capacity": s.standard_capacity or {}}

        lines = {}
        for l in session.query(ProductionLine).all():
            lines[l.line_name] = {
                "status": l.status,
                "available_from": l.available_from,
            }

        existing = [
            {
                "order_number": o.order_number,
                "customer_name": o.customer_name,
                "assigned_line": o.assigned_line,
                "start_date": o.start_date,
                "end_date": o.end_date,
            }
            for o in session.query(Order).filter(
                Order.status.in_(["SCHEDULED", "IN_PROGRESS"]),
                Order.assigned_line.isnot(None),
            ).all()
        ]

        result = auto_schedule(
            order_data={
                "order_number": order.order_number,
                "style_code": order.style_code,
                "total_quantity": order.total_quantity,
                "delivery_date": order.delivery_date,
                "priority": order.priority or "NORMAL",
            },
            styles=styles,
            lines=lines,
            existing_orders=existing,
        )

        if result.recommended:
            order.assigned_line = result.recommended.line_name
            order.start_date = result.recommended.start_date
            order.end_date = result.recommended.end_date
            order.status = "SCHEDULED"
            session.commit()

        return json.dumps({
            "recommended_line": result.recommended.line_name if result.recommended else None,
            "start_date": str(result.recommended.start_date) if result.recommended else None,
            "end_date": str(result.recommended.end_date) if result.recommended else None,
            "work_days": result.recommended.work_days if result.recommended else 0,
            "on_time": result.recommended.on_time if result.recommended else False,
            "warnings": result.warnings,
        }, ensure_ascii=False)
    finally:
        session.close()
