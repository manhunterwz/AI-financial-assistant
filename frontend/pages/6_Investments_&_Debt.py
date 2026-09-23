import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Investments & Debt", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Investments & Debt")

API_BASE_URL = "http://localhost:8000/api"

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Investments")
    try:
        res_inv = requests.get(f"{API_BASE_URL}/investments", timeout=5)
        if res_inv.status_code == 200:
            investments = res_inv.json()
            if investments:
                df_inv = pd.DataFrame(investments)
                df_grouped = df_inv.groupby("asset_class")["amount"].sum().reset_index()
                fig_inv = px.pie(df_grouped, values='amount', names='asset_class', hole=0.6,
                                 color_discrete_sequence=['#10b981', '#059669', '#3b82f6', '#2563eb', '#94a3b8'])
                fig_inv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9', margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_inv, use_container_width=True)
            else:
                st.info("No investments found.")
    except Exception:
        st.error("Failed to fetch investments.")
        
    with st.expander("Add Investment"):
        with st.form("inv_form"):
            inv_name = st.text_input("Investment Name")
            inv_class = st.selectbox("Asset Class", ["Equity", "Mutual Fund", "Crypto", "Bonds", "Real Estate", "Other"])
            inv_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            if st.form_submit_button("Add Investment"):
                try:
                    payload = {"name": inv_name, "asset_class": inv_class, "amount": inv_amount}
                    r = requests.post(f"{API_BASE_URL}/investments", json=payload, timeout=5)
                    r.raise_for_status()
                    st.success("Investment added!")
                    st.rerun()
                except Exception:
                    st.error("Error adding investment.")

with col2:
    st.markdown("### Active Loans")
    try:
        res_loans = requests.get(f"{API_BASE_URL}/loans", timeout=5)
        if res_loans.status_code == 200:
            loans = res_loans.json()
            if loans:
                for loan in loans:
                    st.markdown(f"""
                        <div style="padding: 1.5rem; border-radius: 8px; background: rgba(255,255,255,0.05); margin-bottom: 1rem; border-left: 4px solid #f43f5e;">
                            <h4 style="margin: 0 0 10px 0; color: #f1f5f9;">{loan.get('name', 'Loan')}</h4>
                            <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 0.9rem;">
                                <div>Principal: <strong style="color: #f1f5f9;">₹{loan.get('principal', 0):,.2f}</strong></div>
                                <div>EMI: <strong style="color: #f1f5f9;">₹{loan.get('emi', 0):,.2f}</strong></div>
                                <div>Remaining: <strong style="color: #f1f5f9;">{loan.get('remaining_months', 0)} mos</strong></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active loans.")
    except Exception:
        st.error("Failed to fetch loans.")
        
    with st.expander("Add Loan"):
        with st.form("loan_form"):
            loan_name = st.text_input("Loan Name")
            loan_principal = st.number_input("Principal Amount (₹)", min_value=0.0, step=1000.0)
            loan_emi = st.number_input("Monthly EMI (₹)", min_value=0.0, step=100.0)
            loan_months = st.number_input("Remaining Months", min_value=0, step=1)
            if st.form_submit_button("Add Loan"):
                try:
                    payload = {"name": loan_name, "principal": loan_principal, "emi": loan_emi, "remaining_months": loan_months}
                    r = requests.post(f"{API_BASE_URL}/loans", json=payload, timeout=5)
                    r.raise_for_status()
                    st.success("Loan added!")
                    st.rerun()
                except Exception:
                    st.error("Error adding loan.")
