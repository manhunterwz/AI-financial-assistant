import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Financial Dashboard")

API_BASE_URL = "http://localhost:8000/api"

# Date range filter
months = ["September 2026", "August 2026", "July 2026", "June 2026", "May 2026", "April 2026"]
selected_month = st.selectbox("Select Month", months)

with st.spinner("Fetching analytics..."):
    try:
        res = requests.get(f"{API_BASE_URL}/analytics", timeout=5)
        res.raise_for_status()
        data = res.json()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Income", f"₹{data.get('total_income', 0):,.2f}", data.get('income_delta', "0%"))
        col2.metric("Total Expenses", f"₹{data.get('total_expenses', 0):,.2f}", data.get('expenses_delta', "0%"))
        col3.metric("Savings", f"₹{data.get('savings', 0):,.2f}", data.get('savings_delta', "0%"))
        col4.metric("Savings Rate", f"{data.get('savings_rate', 0)}%", data.get('savings_rate_delta', "0%"))
        
        dti = data.get('dti_ratio', 0)
        dti_color = "#f43f5e" if dti > 36 else "#10b981"
        col5.markdown(f"<div><div style='font-size: 0.9rem; color: #94a3b8; font-family: sans-serif; margin-bottom: -5px;'>DTI Ratio</div><div style='font-size: 2rem; font-family: sans-serif; font-weight: 600; color: {dti_color};'>{dti}%</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("#### Top Spending Categories")
            top_cat = data.get("top_categories", [])
            if top_cat:
                df_cat = pd.DataFrame(top_cat)
                fig_donut = px.pie(df_cat, values='amount', names='category', hole=0.6,
                                  color_discrete_sequence=['#10b981', '#059669', '#3b82f6', '#2563eb', '#94a3b8'])
                fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9', margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("No spending data available.")
                
        with c2:
            st.markdown("#### Monthly Expense Trend")
            trend = data.get("monthly_trend", [])
            if trend:
                df_trend = pd.DataFrame(trend)
                fig_bar = px.bar(df_trend, x='month', y='amount', color_discrete_sequence=['#10b981'])
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9', margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No trend data available.")
                
        with c3:
            st.markdown("#### Fixed vs Variable")
            fixed_var = data.get("fixed_vs_variable", {})
            if fixed_var:
                df_fv = pd.DataFrame(list(fixed_var.items()), columns=['Type', 'Amount'])
                fig_fv = px.pie(df_fv, values='Amount', names='Type',
                               color_discrete_sequence=['#f43f5e', '#3b82f6'])
                fig_fv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9', margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_fv, use_container_width=True)
            else:
                st.info("No fixed/variable data available.")
                
    except requests.exceptions.RequestException:
        st.error("Could not fetch analytics data. Ensure the backend is running.")

st.markdown("---")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Anomaly Alerts")
    try:
        res_ano = requests.get(f"{API_BASE_URL}/ml/anomalies", timeout=5)
        res_ano.raise_for_status()
        anomalies = res_ano.json()
        if anomalies:
            for ano in anomalies[:3]: # show top 3
                st.warning(f"{ano.get('description', 'Unknown')} - ₹{ano.get('amount', 0):,.2f}")
        else:
            st.success("No anomalous spending detected.")
    except requests.exceptions.RequestException:
        st.error("Could not fetch anomaly alerts.")

with col_b:
    st.markdown("#### Expense Predictions")
    try:
        res_pred = requests.get(f"{API_BASE_URL}/ml/predictions", timeout=5)
        res_pred.raise_for_status()
        predictions = res_pred.json().get("predictions", {})
        if predictions:
            df_pred = pd.DataFrame(list(predictions.items()), columns=['Category', 'Predicted Amount'])
            fig_pred = px.bar(df_pred, x='Predicted Amount', y='Category', orientation='h', color_discrete_sequence=['#3b82f6'])
            fig_pred.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9')
            st.plotly_chart(fig_pred, use_container_width=True)
        else:
            st.info("No predictions available.")
    except requests.exceptions.RequestException:
        st.error("Could not fetch predictions.")
