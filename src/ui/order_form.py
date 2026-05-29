"""订单管理页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests
from datetime import date, timedelta

API = "http://localhost:8000/api"


def render():
    st.title("📋 订单管理")
    tab1, tab2, tab3 = st.tabs(["📝 新增订单", "📋 订单列表", "🔍 到期预警"])

    # ── Tab 1: 新增订单 ─────────────────────────────────
    with tab1:
        st.subheader("录入新订单")
        with st.form("order_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                order_number = st.text_input("订单号 *", placeholder="SO-20260601")
                customer_name = st.text_input("客户名称", placeholder="金狐狸服饰")
                style_code = st.text_input("款号 *", placeholder="NK-2026-001")
            with col2:
                total_quantity = st.number_input("订单件数 *", min_value=1, value=1000, step=100)
                delivery_date = st.date_input("交期 *", value=date.today() + timedelta(days=30))
                priority = st.selectbox("优先级", ["NORMAL", "HIGH", "LOW"])

            submitted = st.form_submit_button("✅ 创建订单", type="primary", use_container_width=True)
            if submitted:
                if not order_number or not style_code:
                    st.error("订单号和款号为必填")
                else:
                    try:
                        resp = requests.post(f"{API}/orders/", json={
                            "order_number": order_number,
                            "customer_name": customer_name,
                            "style_code": style_code,
                            "total_quantity": total_quantity,
                            "delivery_date": str(delivery_date),
                            "priority": priority,
                        })
                        if resp.status_code == 201:
                            st.success(f"订单 {order_number} 创建成功！")
                            st.info("→ 切换到「生产排单」页面进行自动排产")
                        elif resp.status_code == 409:
                            st.error(f"订单 {order_number} 已存在")
                        else:
                            st.error(f"创建失败: {resp.json().get('detail', resp.text)}")
                    except requests.ConnectionError:
                        st.error("❌ 无法连接后端，请确保 FastAPI 已启动 (uvicorn src.main:app --reload)")

    # ── Tab 2: 订单列表 ─────────────────────────────────
    with tab2:
        status_filter = st.selectbox("状态筛选", ["全部", "PENDING", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "DELAYED"])
        try:
            params = {}
            if status_filter != "全部":
                params["status"] = status_filter
            resp = requests.get(f"{API}/orders/", params=params)
            if resp.status_code == 200:
                orders = resp.json()
                if not orders:
                    st.info("暂无订单")
                else:
                    for o in orders:
                        status_emoji = {
                            "PENDING": "⏳", "SCHEDULED": "📅", "IN_PROGRESS": "🔧",
                            "COMPLETED": "✅", "DELAYED": "🚨"
                        }.get(o["status"], "❓")
                        with st.container():
                            cols = st.columns([2, 2, 1, 1, 1, 1, 1])
                            cols[0].markdown(f"**{o['order_number']}**")
                            cols[1].caption(o.get("customer_name", "-"))
                            cols[2].caption(o.get("style_code", "-"))
                            cols[3].metric("件数", o["total_quantity"])
                            cols[4].caption(str(o["delivery_date"]))
                            cols[5].markdown(f"{status_emoji} {o['status']}")
                            if cols[6].button("排产", key=f"sch_{o['order_number']}", disabled=o["status"] != "PENDING"):
                                try:
                                    sch_resp = requests.post(f"{API}/schedule/auto", json={"order_number": o["order_number"]})
                                    if sch_resp.status_code == 200:
                                        result = sch_resp.json()
                                        if result.get("recommended"):
                                            st.success(f"排产成功 → {result['recommended']['line']}")
                                            st.rerun()
                                        else:
                                            st.warning(result.get("warnings", ["无可用产线"]))
                                except:
                                    st.error("排产失败")
                            st.divider()
            else:
                st.error("获取订单列表失败")
        except requests.ConnectionError:
            st.warning("⚠️ 后端未连接")

    # ── Tab 3: 到期预警 ─────────────────────────────────
    with tab3:
        days = st.slider("未来几天内到期", 1, 30, 7)
        try:
            resp = requests.get(f"{API}/orders/due/upcoming", params={"days": days})
            if resp.status_code == 200:
                due_orders = resp.json()
                if not due_orders:
                    st.success(f"未来 {days} 天内无到期订单 ✅")
                else:
                    st.warning(f"未来 {days} 天内有 {len(due_orders)} 张订单到期：")
                    for o in due_orders:
                        days_left = (date.fromisoformat(str(o["delivery_date"])) - date.today()).days
                        color = "🔴" if days_left <= 3 else ("🟡" if days_left <= 7 else "🟢")
                        st.markdown(f"{color} **{o['order_number']}** - {o.get('customer_name','')} - {days_left}天后")
        except requests.ConnectionError:
            st.warning("⚠️ 后端未连接")
