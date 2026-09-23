import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Financial Advisor", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("AI Financial Advisor")

API_BASE_URL = "http://localhost:8000/api"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Action suggestions
st.markdown("### Quick Questions")
col1, col2, col3, col4 = st.columns(4)
suggested_prompt = None

if col1.button("How much did I spend on food?"): suggested_prompt = "How much did I spend on food?"
if col2.button("Where am I spending the most?"): suggested_prompt = "Where am I spending the most?"
if col3.button("Can I save ₹10,000 this month?"): suggested_prompt = "Can I save ₹10,000 this month?"
if col4.button("Create a budget for next month"): suggested_prompt = "Create a budget for next month"

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask your financial advisor...")
prompt = suggested_prompt if suggested_prompt else user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{API_BASE_URL}/chat", json={"message": prompt}, timeout=15)
                res.raise_for_status()
                response_data = res.json()
                bot_reply = response_data.get("response", "Sorry, I couldn't process that.")
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except requests.exceptions.RequestException:
                error_msg = "Could not connect to AI backend. Please ensure the service is running."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
