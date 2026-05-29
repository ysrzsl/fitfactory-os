"""计件工资页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st, requests
from datetime import date
API = "http://localhost:8000/api"

def render():
    st.title("💰 计件工资")
    tab1, tab2 = st.tabs(["📝 录入计件", "📊 工资汇总"])

    with tab1:
        with st.form("pw_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                worker = st.text_input("工人姓名 *")
                order = st.text_input("订单号 *")
                qty = st.number_input("产量（件）*", min_value=1, value=100)
            with c2:
                proc = st.selectbox("工序", ["裁剪", "缝制", "质检", "包装", "其他"])
                price = st.number_input("单价（元/件）", min_value=0.0, value=0.5, step=0.1)
                wdate = st.date_input("日期", date.today())
            if st.form_submit_button("✅ 录入", type="primary", use_container_width=True):
                try:
                    resp = requests.post(f"{API}/piecework/", json={
                        "worker_name": worker, "order_number": order, "quantity": qty,
                        "process_name": proc, "unit_price": price, "work_date": str(wdate),
                        "recorded_by": "管理员",
                    })
                    st.success("录入成功" if resp.status_code == 201 else f"失败: {resp.text}")
                except: st.error("后端未连接")

    with tab2:
        today = date.today()
        c1, c2 = st.columns(2)
        with c1: year = st.number_input("年", 2024, 2030, today.year)
        with c2: month = st.number_input("月", 1, 12, today.month)
        if st.button("📊 查询工资"):
            try:
                resp = requests.get(f"{API}/payroll/monthly", params={"year": year, "month": month})
                if resp.status_code == 200:
                    data = resp.json()
                    st.metric("当月工资总额", f"¥{data['total_payroll']:,.2f}")
                    st.metric("工人数", data["worker_count"])
                    st.divider()
                    for w in data.get("workers", []):
                        anomaly = "⚠️" if w.get("anomaly") else ""
                        with st.expander(f"{anomaly} {w['worker_name']} — ¥{w['total_pay']:,.2f} ({w['total_quantity']}件)"):
                            st.caption(f"工号: {w.get('worker_id','-')}")
                            for proc, info in w.get("processes", {}).items():
                                st.text(f"  {proc}: {info['quantity']}件 × ¥{info['pay']/info['quantity'] if info['quantity'] else 0:.2f} = ¥{info['pay']:,.2f}")
            except: st.warning("后端未连接")
