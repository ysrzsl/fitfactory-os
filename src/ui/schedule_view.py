"""生产排单页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests

API = "http://localhost:8000/api"


def render():
    st.title("📅 生产排单")
    tab1, tab2, tab3, tab4 = st.tabs(["⚡ 自动排产", "📦 批量排产", "🔮 插单模拟", "⚠️ 撞单检测"])

    # ── Tab 1: 自动排产 ─────────────────────────────────
    with tab1:
        st.subheader("对单个 PENDING 订单执行自动排产")
        try:
            resp = requests.get(f"{API}/orders/", params={"status": "PENDING"})
            pending_orders = resp.json() if resp.status_code == 200 else []
        except:
            pending_orders = []

        if not pending_orders:
            st.info("没有待排产订单。请先在「订单管理」页面创建订单。")
        else:
            order_options = [f"{o['order_number']} - {o.get('customer_name','')} ({o['total_quantity']}件)" for o in pending_orders]
            selected = st.selectbox("选择待排产订单", order_options)
            if st.button("🚀 执行自动排产", type="primary"):
                order_number = selected.split(" - ")[0]
                try:
                    sch_resp = requests.post(f"{API}/schedule/auto", json={"order_number": order_number})
                    if sch_resp.status_code == 200:
                        result = sch_resp.json()
                        st.divider()

                        rec = result.get("recommended")
                        if rec:
                            st.success(f"### ✅ 推荐方案：{rec['line']}")
                            cols = st.columns(4)
                            cols[0].metric("开工日期", str(rec["start_date"]))
                            cols[1].metric("完工日期", str(rec["end_date"]))
                            cols[2].metric("工作天数", rec["work_days"])
                            cols[3].metric("日产能", f"{rec['daily_capacity']}件/天")
                            if rec["on_time"]:
                                st.success("✅ 按时交付")
                            else:
                                st.error("⚠️ 可能延期")

                        # 备选方案
                        alts = result.get("alternatives", [])
                        if alts:
                            st.divider()
                            st.caption("备选方案：")
                            for a in alts:
                                st.text(f"  → {a['line']}: {a['start_date']} ~ {a['end_date']} ({a['work_days']}天) {'✅' if a['on_time'] else '⚠️'}")

                        # 撞单
                        conflicts = result.get("conflicts", [])
                        if conflicts:
                            st.divider()
                            st.warning(f"⚠️ 与 {len(conflicts)} 张订单有冲突：")
                            for c in conflicts:
                                st.text(f"  🚨 {c['order_number']} ({c.get('customer_name','')}) 重叠 {c['overlap_days']} 天")

                        # 警告
                        for w in result.get("warnings", []):
                            st.warning(w)
                except requests.ConnectionError:
                    st.error("❌ 后端未连接")

    # ── Tab 2: 批量排产 ─────────────────────────────────
    with tab2:
        st.subheader("批量排产所有 PENDING 订单")
        if st.button("📦 批量排产全部待排产订单", type="primary"):
            try:
                pending = [o["order_number"] for o in pending_orders] if pending_orders else []
                if not pending:
                    st.info("没有待排产订单")
                else:
                    resp = requests.post(f"{API}/schedule/batch", json={"order_numbers": pending})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"已排产 {data['scheduled']} 张订单")
                        for r in data["results"]:
                            icon = "✅" if r.get("on_time") else "⚠️"
                            st.text(f"{icon} {r['order_number']} → {r.get('assigned_line','?')}: {r.get('start_date','?')} ~ {r.get('end_date','?')}")
            except requests.ConnectionError:
                st.error("❌ 后端未连接")

    # ── Tab 3: 插单模拟 ─────────────────────────────────
    with tab3:
        st.subheader("🔮 模拟插入新订单的影响")
        col1, col2 = st.columns(2)
        with col1:
            sim_style = st.text_input("款号", "NK-2026-001", key="sim_style")
            sim_qty = st.number_input("件数", min_value=1, value=3000, step=100, key="sim_qty")
        with col2:
            from datetime import date, timedelta
            sim_date = st.date_input("期望开工日期", value=date.today() + timedelta(days=3), key="sim_date")

        if st.button("🔮 模拟插单", type="primary"):
            try:
                sim_resp = requests.post(f"{API}/schedule/simulate-insertion", json={
                    "style_code": sim_style,
                    "quantity": sim_qty,
                    "desired_start_date": str(sim_date),
                })
                if sim_resp.status_code == 200:
                    result = sim_resp.json()
                    st.divider()
                    st.info(f"**推荐产线**: {result.get('recommended_line')} | {result.get('start_date')} → {result.get('end_date')} | {result.get('work_days')}天")

                    affected = result.get("affected_orders", [])
                    if affected:
                        st.warning(f"⚠️ 影响 {len(affected)} 张已有订单：")
                        for a in affected:
                            st.markdown(f"- 🚨 **{a['order_number']}** ({a.get('customer_name','')}): {a['original_end']} → {a['new_end']} (延期 {a['delay_days']}天)")
                    else:
                        st.success("✅ 不影响已有订单")
                else:
                    st.error(f"模拟失败: {sim_resp.text}")
            except requests.ConnectionError:
                st.error("❌ 后端未连接")

    # ── Tab 4: 撞单检测 ─────────────────────────────────
    with tab4:
        st.subheader("⚠️ 全量撞单检测")
        if st.button("🔍 检测撞单"):
            try:
                resp = requests.get(f"{API}/schedule/conflicts")
                if resp.status_code == 200:
                    data = resp.json()
                    if data["conflict_count"] == 0:
                        st.success("✅ 无撞单")
                    else:
                        st.error(f"🚨 发现 {data['conflict_count']} 处撞单：")
                        for c in data["conflicts"]:
                            st.markdown(f"- {c['line']}: **{c['order_a']}** ↔ **{c['order_b']}** 重叠 {c['overlap_days']} 天")
            except requests.ConnectionError:
                st.error("❌ 后端未连接")
