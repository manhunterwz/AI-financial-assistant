import pandas as pd
import joblib
from pathlib import Path
from sklearn.linear_model import LinearRegression

class ExpensePredictor:
    def __init__(self):
        self.models = {}
        self.models_dir = Path(__file__).parent / 'trained_models'
        self.model_path = self.models_dir / 'expense_predictor.pkl'

    def train(self, df):
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        df_local = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_local['date']):
            df_local['date'] = pd.to_datetime(df_local['date'])
            
        df_local['month_period'] = df_local['date'].dt.to_period('M')
        
        monthly_expenses = df_local.groupby(['category', 'month_period'])['amount'].sum().reset_index()
        
        self.models = {}
        for category, group in monthly_expenses.groupby('category'):
            group = group.sort_values('month_period')
            group['month_index'] = range(1, len(group) + 1)
            
            X = group[['month_index']]
            y = group['amount']
            
            if len(X) > 1:
                model = LinearRegression()
                model.fit(X, y)
                self.models[category] = model
                
        joblib.dump(self.models, self.model_path)

    def predict(self, category, next_month_index):
        if not self.models:
            if not self.model_path.exists():
                raise FileNotFoundError("Models not trained yet.")
            self.models = joblib.load(self.model_path)
            
        if category not in self.models:
            return 0.0
            
        model = self.models[category]
        X = pd.DataFrame({'month_index': [next_month_index]})
        prediction = model.predict(X)[0]
        return max(0.0, float(prediction))
