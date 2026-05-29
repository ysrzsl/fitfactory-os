"""物料管理页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st, requests, json
API = "http://localhost:8000/api"

def render():
    st.title("📦 物料管理")
    tab1, tab2, tab3, tab4 = st.tabs(["📝 新增物料", "📋 物料列表", "📥 入库/出库", "⚠️ 缺料预警"])

    with tab1:
        with st.form("mat_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input("物料编码 *", "MAT-001")
                name = st.text_input("物料名称", "蕾丝面料")
                cat = st.selectbox("类别", ["面料", "辅料", "包装", "耗材"])
            with c2:
                unit = st.selectbox("单位", ["米", "根", "个", "卷", "公斤"])
                safety = st.number_input("安全库存", min_value=0.0, value=100.0)
                stock = st.number_input("当前库存", min_value=0.0, value=500.0)
            supplier = st.text_input("供应商")
            lead = st.number_input("采购提前期(天)", min_value=1, value=7)
            if st.form_submit_button("✅ 创建", type="primary", use_container_width=True):
                try:
                    resp = requests.post(f"{API}/materials/", json={
                        "material_code": code, "material_name": name, "category": cat,
                        "unit": unit, "safety_stock": safety, "current_stock": stock,
                        "supplier_name": supplier, "lead_time_days": lead,
                    })
                    st.success(f"物料 {code} 创建成功" if resp.status_code == 201 else f"失败: {resp.text}")
                except: st.error("后端未连接")

    with tab2:
        try:
            resp = requests.get(f"{API}/materials/")
            if resp.status_code == 200:
                for m in resp.json():
                    status = "🔴" if m["current_stock"] < m["safety_stock"] else "🟢"
                    cols = st.columns([2, 1, 1, 1, 1])
                    cols[0].markdown(f"{status} **{m['material_code']}** {m.get('material_name','')}")
                    cols[1].caption(f"库存: {m['current_stock']}{m.get('unit','')}")
                    cols[2].caption(f"安全: {m['safety_stock']}")
                    cols[3].caption(m.get("category", ""))
                    cols[4].caption(m.get("supplier_name", ""))
                    st.divider()
        except: st.warning("后端未连接")

    with tab3:
        st.subheader("库存流水")
        trans_type = st.radio("操作", ["📥 入库", "📤 出库"], horizontal=True)
        with st.form("tx_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                mat_code = st.text_input("物料编码", "MAT-001")
                qty = st.number_input("数量", min_value=0.0, value=100.0)
            with c2:
                order = st.text_input("关联订单（出库时）", "")
                operator = st.text_input("操作人", "管理员")
            if st.form_submit_button("提交", type="primary"):
                ep = "transactions/in" if trans_type == "📥 入库" else "transactions/out"
                try:
                    resp = requests.post(f"{API}/materials/{ep}", json={
                        "material_code": mat_code, "quantity": qty,
                        "related_order": order or None, "operator": operator,
                        "transaction_type": "IN" if trans_type == "📥 入库" else "OUT",
                    })
                    st.success("操作成功" if resp.status_code in (200, 201) else f"失败: {resp.text}")
                except: st.error("后端未连接")

    with tab4:
        st.subheader("⚠️ 缺料预警")
        try:
            resp = requests.get(f"{API}/materials/shortage-alert")
            if resp.status_code == 200:
                items = resp.json()
                if not items: st.success("所有物料库存充足 ✅")
                else:
                    for i in items:
                        st.error(f"🔴 **{i['material_name']}** ({i['material_code']}): 库存 {i['current_stock']}{i['unit']}，缺 {i['shortage']}{i['unit']}，供应商: {i.get('supplier','未知')}")
        except: st.warning("后端未连接")
