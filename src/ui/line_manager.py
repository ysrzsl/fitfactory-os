"""产线管理页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests
from datetime import date

API = "http://localhost:8000/api"


def render():
    st.title("🏭 产线管理")

    tab1, tab2 = st.tabs(["📝 新增产线", "📋 产线列表"])

    with tab1:
        st.subheader("注册新产线")
        with st.form("line_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                line_name = st.text_input("产线名称 *", placeholder="缝制一车间A线")
                operator_count = st.number_input("产线人数", min_value=1, value=20)
            with col2:
                status = st.selectbox("状态", ["IDLE", "BUSY", "MAINTAIN"])
                available_from = st.date_input("最早可用日期", value=date.today())

            if st.form_submit_button("✅ 注册产线", type="primary", use_container_width=True):
                if not line_name:
                    st.error("产线名称为必填")
                else:
                    try:
                        resp = requests.post(f"{API}/lines/", json={
                            "line_name": line_name,
                            "operator_count": operator_count,
                            "status": status,
                            "available_from": str(available_from) if status != "IDLE" else str(date.today()),
                        })
                        if resp.status_code == 201:
                            st.success(f"产线 {line_name} 注册成功")
                        else:
                            st.error(f"失败: {resp.json().get('detail', resp.text)}")
                    except requests.ConnectionError:
                        st.error("❌ 后端未连接")

    with tab2:
        try:
            resp = requests.get(f"{API}/lines/")
            if resp.status_code == 200:
                lines = resp.json()
                if not lines:
                    st.info("暂无产线")
                else:
                    for l in lines:
                        emoji = {"IDLE": "🟢", "BUSY": "🔵", "MAINTAIN": "🔴"}.get(l["status"], "⚪")
                        cols = st.columns([2, 1, 1, 1])
                        cols[0].markdown(f"**{emoji} {l['line_name']}**")
                        cols[1].caption(f"人数: {l.get('operator_count', '-')}")
                        cols[2].caption(f"状态: {l['status']}")
                        cols[3].caption(f"可用: {l.get('available_from', '今天')}")
                        st.divider()
        except requests.ConnectionError:
            st.warning("⚠️ 后端未连接")
