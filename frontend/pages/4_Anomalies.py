import streamlit as st
import requests
import os

st.set_page_config(page_title="Anomaly Detection", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Anomaly Detection")

API_BASE_URL = "http://localhost:8000/api"

try:
    res = requests.get(f"{API_BASE_URL}/ml/anomalies", timeout=10)
    res.raise_for_status()
    anomalies = res.json()
    
    if not anomalies:
        st.success("No unusual spending detected.")
    else:
        total_anomalies = len(anomalies)
        total_amount = sum(a.get("amount", 0) for a in anomalies)
        
        col1, col2 = st.columns(2)
        col1.metric("Total Anomalies Found", total_anomalies)
        col2.metric("Total Amount Flagged", f"₹{total_amount:,.2f}")
        
        st.markdown("---")
        
        for a in anomalies:
            with st.container():
                score = a.get("anomaly_score", 0.5)
                # color coding
                color = "#10b981" # default green shouldn't happen for anomaly but fallback
                severity_text = "Mild"
                if score > 0.8:
                    color = "#f43f5e" # rose
                    severity_text = "Severe"
                elif score > 0.5:
                    color = "#f97316" # orange
                    severity_text = "Moderate"
                else:
                    color = "#eab308" # yellow
                
                st.markdown(f"#### {a.get('description', 'Unknown Transaction')}")
                st.markdown(f"**Amount:** ₹{a.get('amount', 0):,.2f} | **Date:** {a.get('transaction_date', 'N/A')} | **Category:** {a.get('category', 'N/A')}")
                
                # Severity bar
                html_bar = f'''
                <p style="margin-bottom: 2px; font-size: 0.9em;">Severity: {severity_text} (Score: {score:.2f})</p>
                <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 4px;">
                    <div style="width: {score*100}%; background-color: {color}; height: 10px; border-radius: 4px;"></div>
                </div>
                <br>
                '''
                st.markdown(html_bar, unsafe_allow_html=True)
                
except requests.exceptions.RequestException:
    st.error("Could not fetch anomaly data from backend.")
