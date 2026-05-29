"""生产看板页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests

API = "http://localhost:8000/api"


def render():
    st.title("📊 生产看板")

    try:
        # ── 总览 ─────────────────────────────────────────
        overview = requests.get(f"{API}/dashboard/overview").json()

        st.subheader("📈 全局统计")
        stats = overview.get("stats", {})
        cols = st.columns(8)
        cols[0].metric("总订单", stats.get("total_orders", 0))
        cols[1].metric("待排产", stats.get("pending", 0))
        cols[2].metric("已排产", stats.get("scheduled", 0))
        cols[3].metric("进行中", stats.get("in_progress", 0))
        cols[4].metric("已完成", stats.get("completed", 0))
        cols[5].metric("延期", stats.get("delayed", 0), delta=None if stats.get("delayed", 0) == 0 else f"-{stats.get('delayed', 0)}")
        cols[6].metric("今日产量", stats.get("today_output", 0))
        cols[7].metric("本周到期", stats.get("due_this_week", 0))

        # ── 产线状态 ─────────────────────────────────────
        st.divider()
        st.subheader("🏭 产线状态")

        lines = overview.get("lines", [])
        if lines:
            line_cols = st.columns(min(len(lines), 4))
            for i, l in enumerate(lines):
                with line_cols[i % 4]:
                    status_color = {"IDLE": "🟢", "BUSY": "🔵", "MAINTAIN": "🔴"}.get(l["status"], "⚪")
                    st.markdown(f"### {status_color} {l['line_name']}")
                    st.caption(f"状态: {l['status']} | 人数: {l.get('operator_count', '-')}")
                    if l.get("active_order"):
                        st.markdown(f"📋 **{l['active_order']}** ")
                        st.caption(f"款号: {l.get('active_style', '')}")

        # ── 延期预警 ─────────────────────────────────────
        st.divider()
        st.subheader("🚨 延期预警")
        delays = requests.get(f"{API}/dashboard/delays").json()

        delayed_list = delays.get("delayed", [])
        at_risk = delays.get("at_risk", [])

        if delayed_list:
            st.error(f"已延期 {len(delayed_list)} 张订单")
            for d in delayed_list:
                st.markdown(f"- 🚨 **{d['order_number']}** ({d.get('customer', '')})")
        else:
            st.success("暂无延期订单")

        if at_risk:
            st.warning(f"进度落后 {len(at_risk)} 张订单")
            for a in at_risk:
                st.markdown(
                    f"- ⚠️ **{a['order_number']}** ({a.get('customer_name', '')}) "
                    f"预期 {a['expected_rate']}% / 实际 {a['actual_rate']}% (落后 {a['gap']}%)"
                )

        # ── 今日速报 ─────────────────────────────────────
        st.divider()
        st.subheader("📋 今日速报")
        daily = requests.get(f"{API}/dashboard/daily-report").json()
        dcols = st.columns(4)
        dcols[0].metric("日期", daily.get("date", "-"))
        dcols[1].metric("今日产量", daily.get("today_output", 0))
        dcols[2].metric("在岗人数", daily.get("workers_on_duty", 0))
        dcols[3].metric("今日新增订单", daily.get("new_orders_today", 0))

    except requests.ConnectionError:
        st.warning("⚠️ 后端未连接 — 请先启动 FastAPI: uvicorn src.main:app --reload")
