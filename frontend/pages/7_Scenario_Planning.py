import streamlit as st
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Scenario Planning", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
st.title("Scenario Planning")

st.markdown("Explore how different financial decisions affect your future.")

tab1, tab2, tab3 = st.tabs(["Career Change", "Major Purchase", "Investment Compounding"])

with tab1:
    st.markdown("### Career Change Simulator")
    col1, col2 = st.columns(2)
    with col1:
        current_salary = st.number_input("Current Monthly Salary (₹)", value=50000)
        new_salary = st.number_input("New Monthly Salary (₹)", value=70000)
        current_expenses = st.number_input("Current Monthly Expenses (₹)", value=25000)
        current_debt = st.number_input("Current Monthly Debt Payments (₹)", value=5000)
        relocation_cost = st.number_input("One-time Relocation Cost (₹)", value=0)
    
    with col2:
        st.markdown("#### Impact Analysis")
        if current_salary > 0 and new_salary > 0:
            old_savings_rate = ((current_salary - current_expenses - current_debt) / current_salary) * 100
            new_savings_rate = ((new_salary - current_expenses - current_debt) / new_salary) * 100
            
            old_dti = (current_debt / current_salary) * 100
            new_dti = (current_debt / new_salary) * 100
            
            months_to_recover = relocation_cost / (new_salary - current_salary) if new_salary > current_salary and relocation_cost > 0 else 0
            
            st.metric("New Savings Rate", f"{new_savings_rate:.1f}%", f"{new_savings_rate - old_savings_rate:.1f}%")
            
            dti_delta = new_dti - old_dti
            st.metric("New DTI Ratio", f"{new_dti:.1f}%", f"{dti_delta:.1f}%", delta_color="inverse")
            
            if relocation_cost > 0:
                if months_to_recover > 0:
                    st.info(f"It will take **{months_to_recover:.1f} months** to recover the relocation cost from the salary increase.")
                else:
                    st.warning("The new salary does not cover the relocation cost in the long run.")

with tab2:
    st.markdown("### Major Purchase Affordability")
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Monthly Income (₹)", value=60000, key="mp_income")
        monthly_debt = st.number_input("Current Monthly Debt (₹)", value=10000, key="mp_debt")
        item_cost = st.number_input("Item Cost (₹)", value=500000)
        down_payment = st.number_input("Down Payment (₹)", value=100000)
        loan_interest = st.number_input("Annual Interest Rate (%)", value=9.5)
        tenure_years = st.number_input("Loan Tenure (Years)", value=5)
        
    with col2:
        st.markdown("#### Affordability Check")
        loan_amount = item_cost - down_payment
        if loan_amount > 0 and tenure_years > 0 and monthly_income > 0:
            r = (loan_interest / 100) / 12
            n = tenure_years * 12
            if r > 0:
                emi = loan_amount * r * ((1 + r)**n) / (((1 + r)**n) - 1)
            else:
                emi = loan_amount / n
                
            new_total_debt = monthly_debt + emi
            new_dti = (new_total_debt / monthly_income) * 100
            
            st.markdown(f"<div style='font-size: 1.5rem; margin-bottom: 10px;'>Estimated EMI: <strong>₹{emi:,.2f}</strong></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 1.2rem; margin-bottom: 20px;'>New DTI Ratio: <strong>{new_dti:.1f}%</strong></div>", unsafe_allow_html=True)
            
            if new_dti > 36:
                st.error("Not Recommended: Your DTI ratio will exceed 36%.")
            else:
                st.success("Safe: Your DTI ratio remains within healthy limits (< 36%).")
        elif loan_amount <= 0:
            st.success("No loan needed. Fully paid with down payment!")

with tab3:
    st.markdown("### Investment Compounding")
    col1, col2 = st.columns([1, 2])
    with col1:
        sip_amount = st.number_input("Monthly SIP (₹)", value=5000)
        expected_return = st.number_input("Expected Annual Return (%)", value=12.0)
        years = st.slider("Investment Horizon (Years)", min_value=1, max_value=40, value=10)
        
    with col2:
        if sip_amount > 0 and years > 0:
            months = years * 12
            r = (expected_return / 100) / 12
            
            data = []
            total_invested = 0
            future_value = 0
            
            for m in range(1, months + 1):
                total_invested += sip_amount
                future_value = (future_value + sip_amount) * (1 + r)
                if m % 12 == 0:
                    data.append({
                        "Year": m // 12,
                        "Total Invested": total_invested,
                        "Future Value": future_value
                    })
            
            df = pd.DataFrame(data)
            fig = px.line(df, x="Year", y=["Total Invested", "Future Value"],
                          color_discrete_sequence=['#94a3b8', '#10b981'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9',
                              legend_title_text='')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"Total Invested: **₹{total_invested:,.2f}** | Estimated Value: <strong style='color:#10b981;'>₹{future_value:,.2f}</strong>", unsafe_allow_html=True)
