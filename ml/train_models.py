import pandas as pd
import logging
from pathlib import Path

from categorizer import ExpenseCategorizer
from anomaly_detector import AnomalyDetector
from expense_predictor import ExpensePredictor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    root_dir = Path(__file__).parent.parent
    data_path = root_dir / 'data' / 'sample_transactions.csv'
    
    if not data_path.exists():
        logging.error(f"Data file not found at {data_path}. Cannot train models.")
        return

    logging.info("Loading transaction data...")
    df = pd.read_csv(data_path)
    
    if 'description' not in df.columns or 'category' not in df.columns or 'amount' not in df.columns or 'date' not in df.columns:
        logging.error("Missing required columns in dataset.")
        return

    logging.info("Training Expense Categorizer...")
    categorizer = ExpenseCategorizer()
    categorizer.train(df['description'].fillna(''), df['category'].fillna('Unknown'))
    logging.info("Expense Categorizer trained successfully.")
    
    logging.info("Training Anomaly Detector...")
    anomaly_detector = AnomalyDetector()
    anomaly_detector.train(df)
    logging.info("Anomaly Detector trained successfully.")
    
    logging.info("Training Expense Predictor...")
    expense_predictor = ExpensePredictor()
    expense_predictor.train(df)
    logging.info("Expense Predictor trained successfully.")
    
    logging.info("All models trained and saved to ml/trained_models/.")

if __name__ == '__main__':
    main()
