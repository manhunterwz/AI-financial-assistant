import streamlit as st
import requests
import os
import pandas as pd
from datetime import date

st.set_page_config(page_title="Transactions", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Transactions")

API_BASE_URL = "http://localhost:8000/api"

# Fetch categories
categories = ["Auto-detect (ML)"]
try:
    res_cat = requests.get(f"{API_BASE_URL}/categories", timeout=5)
    if res_cat.status_code == 200:
        categories.extend(res_cat.json())
except requests.exceptions.RequestException:
    categories.extend(["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Salary"])

if "scan_desc" not in st.session_state:
    st.session_state.scan_desc = ""
if "scan_amount" not in st.session_state:
    st.session_state.scan_amount = 0.0
if "scan_date" not in st.session_state:
    st.session_state.scan_date = date.today()

st.markdown("### AI Bill Scanner")
captured_image = st.camera_input("Scan Bill / Receipt")

if captured_image is not None:
    if st.session_state.get("last_scanned") != captured_image.id:
        with st.spinner("Scanning with Gemini Vision..."):
            try:
                files = {"file": ("receipt.jpg", captured_image.getvalue(), "image/jpeg")}
                res_scan = requests.post(f"{API_BASE_URL}/transactions/scan-receipt", files=files, timeout=10)
                res_scan.raise_for_status()
                scan_data = res_scan.json()
                
                st.session_state.scan_amount = float(scan_data.get("amount", 0.0))
                st.session_state.scan_desc = scan_data.get("description", "")
                
                scan_date_str = scan_data.get("date")
                if scan_date_str:
                    try:
                        st.session_state.scan_date = date.fromisoformat(scan_date_str)
                    except ValueError:
                        pass
                st.session_state.last_scanned = captured_image.id
                st.success("Receipt scanned successfully! Data pre-filled below.")
            except requests.exceptions.RequestException as e:
                st.error("Failed to scan receipt.")

with st.expander("Add New Transaction", expanded=True):
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            desc = st.text_input("Description", value=st.session_state.scan_desc, placeholder="E.g., Groceries")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, value=st.session_state.scan_amount)
            t_type = st.selectbox("Type", ["Expense", "Income"])
            is_fixed_expense = st.checkbox("Is Fixed Expense?", value=False)
        with col2:
            t_date = st.date_input("Date", value=st.session_state.scan_date)
            cat = st.selectbox("Category", categories)
        
        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            if not desc or amount <= 0:
                st.error("Please provide valid description and amount.")
            else:
                payload = {
                    "description": desc,
                    "amount": float(amount),
                    "type": t_type.lower(),
                    "category": None if cat == "Auto-detect (ML)" else cat,
                    "transaction_date": t_date.isoformat(),
                    "is_fixed_expense": is_fixed_expense
                }
                try:
                    res_post = requests.post(f"{API_BASE_URL}/transactions", json=payload, timeout=5)
                    res_post.raise_for_status()
                    st.success("Transaction added successfully!")
                    st.session_state.scan_desc = ""
                    st.session_state.scan_amount = 0.0
                    st.session_state.scan_date = date.today()
                except requests.exceptions.RequestException:
                    st.error("Failed to add transaction. Backend may be down.")

st.markdown("### Recent Transactions")

try:
    res_trans = requests.get(f"{API_BASE_URL}/transactions", timeout=5)
    res_trans.raise_for_status()
    transactions = res_trans.json()
    if transactions:
        df = pd.DataFrame(transactions)
        
        def highlight_anomalies(row):
            if row.get('is_anomaly', False):
                return ['background-color: rgba(244, 63, 94, 0.2)'] * len(row)
            return [''] * len(row)
            
        display_cols = ['transaction_date', 'description', 'category', 'type', 'amount', 'is_anomaly', 'is_fixed_expense']
        df_display = df[[c for c in display_cols if c in df.columns]]
        df_display = df_display.sort_values(by='transaction_date', ascending=False)
        
        df_display['amount'] = df_display['amount'].apply(lambda x: f"₹{x:,.2f}")
        
        st.dataframe(df_display.style.apply(highlight_anomalies, axis=1), use_container_width=True)
    else:
        st.info("No transactions found.")
except requests.exceptions.RequestException:
    st.error("Could not fetch transactions. Ensure backend is running.")
