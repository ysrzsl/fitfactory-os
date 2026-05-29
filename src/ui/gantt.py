"""甘特图页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st, requests
from datetime import date
API = "http://localhost:8000/api"

def render():
    st.title("📅 排产甘特图")
    try:
        resp = requests.get(f"{API}/dashboard/gantt")
        if resp.status_code != 200:
            st.warning("暂无排产数据")
            return
        data = resp.json()
        lines = data.get("lines", {})
        if not lines:
            st.info("暂无已排产订单")
            return

        # 颜色映射
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#00BCD4", "#8BC34A", "#FF5722"]

        for i, (line_name, orders) in enumerate(lines.items()):
            st.subheader(f"🏭 {line_name}")
            color = colors[i % len(colors)]

            for o in orders:
                cols = st.columns([1, 3])
                cols[0].markdown(f"**{o['order_number']}**")
                cols[0].caption(f"{o.get('customer','')} | {o.get('quantity',0)}件")
                # 简易进度条
                start = date.fromisoformat(o["start"])
                end = date.fromisoformat(o["end"])
                total_days = (end - start).days + 1
                today = date.today()
                elapsed = max(0, (today - start).days + 1)
                elapsed = min(elapsed, total_days)
                pct = elapsed / total_days if total_days > 0 else 0

                cols[1].markdown(f"`{o['start']}` → `{o['end']}` ({total_days}天)")
                cols[1].progress(pct)
            st.divider()
    except requests.ConnectionError:
        st.warning("后端未连接")
