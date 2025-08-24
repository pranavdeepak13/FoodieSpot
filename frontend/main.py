import streamlit as st
import requests
import uuid

st.set_page_config(page_title="🍽️ FoodieSpot AI Assistant", layout="centered")
st.title("🍽️ FoodieSpot AI Chatbot")

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "conversation" not in st.session_state:
    st.session_state.conversation = []

for msg in st.session_state.conversation:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("How can I help you today?")
if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    res = requests.post("http://localhost:8000/query", json={
        "user_id": st.session_state.user_id,
        "user_input": user_input
    })
    bot_reply = res.json()["response"]

    st.session_state.conversation.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
