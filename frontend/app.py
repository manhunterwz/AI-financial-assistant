import streamlit as st
import os

st.set_page_config(page_title="AI Financial Assistant", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("AI Financial Assistant")
st.markdown("### Intelligent insights and anomaly detection for your personal finances")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("#### Dashboard")
        st.markdown("Gain insights into your spending habits, track savings, and visualize your financial health with AI-powered analytics.")

with col2:
    with st.container():
        st.markdown("#### Transactions")
        st.markdown("Manage your transactions with automated machine learning categorizations and spot unusual activity instantly.")

with col3:
    with st.container():
        st.markdown("#### AI Assistant")
        st.markdown("Chat with your personal financial advisor to get answers about your spending, budget plans, and recommendations.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #94a3b8;'>Powered by Machine Learning | FastAPI + Streamlit</p>", unsafe_allow_html=True)
