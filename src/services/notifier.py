"""
企业微信消息推送服务
支持 Webhook 推送和本地日志降级
"""
import requests
import json
from datetime import datetime
from src.config import WECOM_WEBHOOK_URL


def send_notification(message: str, priority: str = "MEDIUM") -> bool:
    """
    发送通知

    priority:
      HIGH   → 立即推送企微 + 本地日志
      MEDIUM → 仅本地日志（后续可改为聚合推送）
      LOW    → 本地日志

    返回是否推送成功
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{priority}] {message}"

    # 始终记录本地日志
    try:
        with open("data/notifications.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception:
        pass

    # HIGH 优先级推送企微
    if priority == "HIGH" and WECOM_WEBHOOK_URL:
        try:
            resp = requests.post(WECOM_WEBHOOK_URL, json={
                "msgtype": "markdown",
                "markdown": {"content": f"## FitFactory OS 通知\n\n{message}\n\n> {timestamp}"}
            }, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    return True  # 非 HIGH 优先级或日志成功即返回 True


# ── 常用通知模板 ────────────────────────────────────────
def notify_shortage(material_name: str, current: float, safety: float, unit: str):
    """缺料预警"""
    msg = f"⚠️ **缺料预警**\n物料: {material_name}\n当前库存: {current}{unit}\n安全库存: {safety}{unit}\n缺 {round(safety-current,2)}{unit}"
    send_notification(msg, "HIGH")


def notify_order_delayed(order_number: str, customer: str, delay_days: int):
    """订单延期"""
    msg = f"🚨 **订单延期**\n订单 {order_number}（{customer}）\n预计延期 {delay_days} 天"
    send_notification(msg, "HIGH")


def notify_order_complete(order_number: str, customer: str):
    """订单完成"""
    msg = f"✅ **订单完成**\n订单 {order_number}（{customer}）已完成，可安排发货"
    send_notification(msg, "MEDIUM")


def notify_daily_report(report: str):
    """日报摘要"""
    send_notification(report, "MEDIUM")
