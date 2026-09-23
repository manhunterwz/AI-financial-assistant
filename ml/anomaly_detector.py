import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.models_dir = Path(__file__).parent / 'trained_models'
        self.model_path = self.models_dir / 'anomaly_detector.pkl'

    def train(self, df):
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        df_local = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_local['date']):
            df_local['date'] = pd.to_datetime(df_local['date'])
            
        df_local['day_of_month'] = df_local['date'].dt.day
        
        X = df_local[['amount', 'day_of_month']].fillna(0)
        
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.model.fit(X)
        
        joblib.dump(self.model, self.model_path)

    def predict(self, amount, date_str):
        if self.model is None:
            if not self.model_path.exists():
                raise FileNotFoundError("Model not trained yet.")
            self.model = joblib.load(self.model_path)
            
        date_obj = pd.to_datetime(date_str)
        day_of_month = date_obj.day
        
        X = pd.DataFrame({'amount': [amount], 'day_of_month': [day_of_month]})
        
        prediction = self.model.predict(X)[0]
        score = self.model.decision_function(X)[0]
        
        is_anomaly = prediction == -1
        return bool(is_anomaly), float(score)
