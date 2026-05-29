"""
FitFactory OS - Streamlit 主页面
启动: streamlit run src/ui/app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st

st.set_page_config(
    page_title="FitFactory OS",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 侧边栏导航 ──────────────────────────────────────────
st.sidebar.title("🏭 FitFactory OS")
st.sidebar.caption("服装厂智能工作台 v0.1")

page = st.sidebar.radio(
    "导航",
    ["💬 AI 助手", "📋 订单管理", "📅 生产排单", "📊 生产看板", "📦 物料管理", "💰 计件工资", "📅 甘特图", "🏭 产线管理", "👗 款式管理"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("Phase 3 · 完整闭环")

# ── 页面路由 ────────────────────────────────────────────
if page == "💬 AI 助手":
    from src.ui.chat import render; render()
elif page == "📋 订单管理":
    from src.ui.order_form import render; render()
elif page == "📅 生产排单":
    from src.ui.schedule_view import render; render()
elif page == "📊 生产看板":
    from src.ui.dashboard import render; render()
elif page == "📦 物料管理":
    from src.ui.material_manager import render; render()
elif page == "💰 计件工资":
    from src.ui.payroll_view import render; render()
elif page == "📅 甘特图":
    from src.ui.gantt import render; render()
elif page == "🏭 产线管理":
    from src.ui.line_manager import render; render()
elif page == "👗 款式管理":
    from src.ui.style_manager import render; render()
