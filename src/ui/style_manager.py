"""款式管理页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests
import json

API = "http://localhost:8000/api"


def render():
    st.title("👗 款式管理")

    tab1, tab2 = st.tabs(["📝 新增款式", "📋 款式列表"])

    with tab1:
        st.subheader("注册新款式")
        with st.form("style_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                style_code = st.text_input("款号 *", placeholder="NK-2026-001")
                style_name = st.text_input("款式名称", placeholder="蕾丝无钢圈内衣")
                category = st.selectbox("类别", ["内衣", "文胸", "睡衣", "运动", "其他"])
            with col2:
                st.caption("标准日产能（件/天）")
                capacity_json = st.text_area(
                    "产能配置 (JSON)",
                    value='{"缝制一车间A线": 500, "缝制二车间B线": 450}',
                    height=100,
                    help="格式: {\"产线名\": 日产能}"
                )
                st.caption("物料清单 BOM")
                bom_json = st.text_area(
                    "BOM (JSON)",
                    value='{"蕾丝面料": "0.15米", "肩带": "2根", "背钩": "1个"}',
                    height=100,
                    help="格式: {\"物料名\": \"单件用量\"}"
                )

            if st.form_submit_button("✅ 注册款式", type="primary", use_container_width=True):
                if not style_code:
                    st.error("款号为必填")
                else:
                    try:
                        cap = json.loads(capacity_json)
                        bom = json.loads(bom_json) if bom_json else None
                        resp = requests.post(f"{API}/styles/", json={
                            "style_code": style_code,
                            "style_name": style_name,
                            "category": category,
                            "standard_capacity": cap,
                            "bom_data": bom,
                        })
                        if resp.status_code == 201:
                            st.success(f"款式 {style_code} 注册成功")
                        else:
                            st.error(f"失败: {resp.json().get('detail', resp.text)}")
                    except json.JSONDecodeError:
                        st.error("JSON 格式错误，请检查产能和 BOM 配置")
                    except requests.ConnectionError:
                        st.error("❌ 后端未连接")

    with tab2:
        try:
            resp = requests.get(f"{API}/styles/")
            if resp.status_code == 200:
                styles = resp.json()
                if not styles:
                    st.info("暂无款式")
                else:
                    for s in styles:
                        with st.expander(f"👗 {s['style_code']} — {s.get('style_name', '未命名')}"):
                            cols = st.columns(3)
                            cols[0].caption(f"类别: {s.get('category', '-')}")
                            cols[1].caption("产能配置:")
                            for line, cap in s.get("standard_capacity", {}).items():
                                cols[1].text(f"  {line}: {cap}件/天")
                            cols[2].caption("BOM:")
                            for mat, qty in s.get("bom_data", {}).items():
                                cols[2].text(f"  {mat}: {qty}")
        except requests.ConnectionError:
            st.warning("⚠️ 后端未连接")
