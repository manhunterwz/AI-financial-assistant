import streamlit as st
import requests
import os

st.set_page_config(page_title="Profile & Goals", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Profile & Goals")

API_BASE_URL = "http://localhost:8000/api"

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Add Savings Goal")
    with st.form("goal_form"):
        goal_name = st.text_input("Goal Name", placeholder="E.g., Emergency Fund, Vacation")
        target_amt = st.number_input("Target Amount (₹)", min_value=0.0, step=1000.0)
        current_amt = st.number_input("Current Amount (₹)", min_value=0.0, step=1000.0)
        
        submitted = st.form_submit_button("Create Goal")
        if submitted:
            if not goal_name or target_amt <= 0:
                st.error("Please provide a valid goal name and target > 0.")
            else:
                payload = {
                    "name": goal_name,
                    "target_amount": target_amt,
                    "current_amount": current_amt
                }
                try:
                    res_post = requests.post(f"{API_BASE_URL}/goals", json=payload, timeout=5)
                    res_post.raise_for_status()
                    st.success("Goal added successfully!")
                    st.rerun()
                except requests.exceptions.RequestException:
                    st.error("Failed to add goal.")

with col2:
    st.markdown("### Current Goals")
    try:
        res_goals = requests.get(f"{API_BASE_URL}/goals", timeout=5)
        if res_goals.status_code == 200:
            goals = res_goals.json()
            if goals:
                for goal in goals:
                    name = goal.get("name", "Goal")
                    target = goal.get("target_amount", 1)
                    current = goal.get("current_amount", 0)
                    progress = min(current / target, 1.0) if target > 0 else 0
                    progress_pct = progress * 100
                    
                    st.markdown(f"""
                        <div style="padding: 1.5rem; border-radius: 8px; background: rgba(255,255,255,0.05); margin-bottom: 1.5rem; border-left: 4px solid #10b981;">
                            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px;">
                                <h4 style="margin: 0; color: #f1f5f9;">{name}</h4>
                                <span style="color: #94a3b8; font-size: 0.9rem;">₹{current:,.2f} / ₹{target:,.2f}</span>
                            </div>
                            <div style="width: 100%; background-color: #1e293b; border-radius: 4px; height: 12px; overflow: hidden;">
                                <div style="width: {progress_pct}%; background-color: #10b981; height: 100%; transition: width 0.3s ease;"></div>
                            </div>
                            <div style="text-align: right; font-size: 0.8rem; color: #10b981; margin-top: 4px;">{progress_pct:.1f}% Complete</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No savings goals found. Create one to get started!")
    except Exception:
        st.error("Failed to fetch goals.")
