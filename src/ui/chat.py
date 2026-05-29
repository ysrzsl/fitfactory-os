"""AI 助手对话页面"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import requests

API = "http://localhost:8000/api"


def render():
    st.title("💬 AI 厂长助理")

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "你好！我是 AI 厂长助理 👋\n\n你可以问我：\n- \"SO-20260601 现在做到哪了？\"\n- \"下周有哪些订单要交？\"\n- \"产线状态怎么样？\"\n- \"帮我排一下 SO-20260604\"\n- \"模拟插 3000 件 NK-2026-003 会怎样？\""}
        ]

    # 清空按钮
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 新对话"):
            try:
                requests.post(f"{API}/chat/reset")
            except:
                pass
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()

    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    if prompt := st.chat_input("输入你的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    resp = requests.post(f"{API}/chat/", json={"message": prompt})
                    if resp.status_code == 200:
                        reply = resp.json()["reply"]
                    else:
                        reply = f"❌ 出错了: {resp.text}"
                except requests.ConnectionError:
                    reply = "⚠️ 后端未连接，请启动 FastAPI: `python3 -m uvicorn src.main:app --reload`"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
