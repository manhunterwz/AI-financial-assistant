import pandas as pd

class BudgetRecommender:
    def recommend(self, historical_df):
        df = historical_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
            
        max_date = df['date'].max()
        if pd.isna(max_date):
            return {}
            
        three_months_ago = max_date - pd.DateOffset(months=3)
        recent_df = df[df['date'] > three_months_ago]
        
        if recent_df.empty:
            return {}
            
        recent_df['month_period'] = recent_df['date'].dt.to_period('M')
        monthly_category_expenses = recent_df.groupby(['month_period', 'category'])['amount'].sum().reset_index()
        
        num_months = recent_df['month_period'].nunique()
        avg_expenses = monthly_category_expenses.groupby('category')['amount'].sum() / num_months
        
        recommendations = (avg_expenses * 1.05).to_dict()
        
        return recommendations
