import streamlit as st
import requests
import os
import datetime

st.set_page_config(page_title="Budgets", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Budgets")

API_BASE_URL = "http://localhost:8000/api"

# AI Recommendations
st.markdown("### AI Recommendations")
if st.button("Get AI Budget Recommendations"):
    with st.spinner("Analyzing your spending to suggest budgets..."):
        try:
            res_rec = requests.get(f"{API_BASE_URL}/ml/recommendations", timeout=10)
            res_rec.raise_for_status()
            recs = res_rec.json().get("recommendations", {})
            if recs:
                cols = st.columns(len(recs))
                for i, (cat, amt) in enumerate(recs.items()):
                    with cols[i % len(cols)]:
                        with st.container():
                            st.markdown(f"**{cat}**")
                            st.markdown(f"₹{amt:,.2f}")
                            if st.button(f"Set this budget", key=f"set_{cat}"):
                                try:
                                    payload = {"category": cat, "budget_limit": amt, "month": datetime.date.today().strftime("%Y-%m")}
                                    res_set = requests.post(f"{API_BASE_URL}/budgets", json=payload, timeout=5)
                                    res_set.raise_for_status()
                                    st.success(f"Budget set for {cat}!")
                                except Exception as e:
                                    st.error("Failed to set budget")
            else:
                st.info("No recommendations available.")
        except requests.exceptions.RequestException:
            st.error("Could not fetch recommendations.")

st.markdown("---")
st.markdown("### Current Budgets")

# Add Budget Form
with st.expander("Create New Budget"):
    with st.form("budget_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            b_cat = st.text_input("Category")
        with col2:
            b_limit = st.number_input("Budget Limit (₹)", min_value=1.0)
        with col3:
            b_month = st.text_input("Month (YYYY-MM)", value=datetime.date.today().strftime("%Y-%m"))
            
        submitted = st.form_submit_button("Add Budget")
        if submitted and b_cat and b_limit:
            payload = {"category": b_cat, "budget_limit": b_limit, "month": b_month}
            try:
                r = requests.post(f"{API_BASE_URL}/budgets", json=payload, timeout=5)
                r.raise_for_status()
                st.success("Budget added!")
            except:
                st.error("Failed to add budget.")

# Display Budgets
try:
    res_budgets = requests.get(f"{API_BASE_URL}/budgets", timeout=5)
    res_analytics = requests.get(f"{API_BASE_URL}/analytics", timeout=5)
    if res_budgets.status_code == 200 and res_analytics.status_code == 200:
        budgets = res_budgets.json()
        analytics = res_analytics.json()
        spent_by_cat = {item['category']: item['amount'] for item in analytics.get('top_categories', [])}
        
        if budgets:
            for b in budgets:
                cat = b.get('category')
                limit = b.get('budget_limit', 1)
                spent = spent_by_cat.get(cat, 0)
                progress = min(spent / limit, 1.0)
                
                # Determine color based on usage
                color = "green"
                if progress > 0.75:
                    color = "orange"
                if progress >= 1.0:
                    color = "red"
                
                st.markdown(f"**{cat}** (Month: {b.get('month')})")
                st.markdown(f"Spent: ₹{spent:,.2f} / ₹{limit:,.2f}")
                # Simple progress bar styling in html to control colors
                html_bar = f'''
                <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 4px;">
                    <div style="width: {progress*100}%; background-color: {color}; height: 10px; border-radius: 4px;"></div>
                </div>
                <br>
                '''
                st.markdown(html_bar, unsafe_allow_html=True)
                
                if st.button("Delete", key=f"del_{b.get('id', cat)}"):
                    if b.get('id'):
                        requests.delete(f"{API_BASE_URL}/budgets/{b.get('id')}", timeout=5)
                        st.rerun()
        else:
            st.info("No budgets configured.")
except requests.exceptions.RequestException:
    st.error("Failed to load budgets. Backend may be down.")
