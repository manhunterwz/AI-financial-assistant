"""
app.py
------
A small Flask REST API that serves the trained ML models. This is the
"real" backend: in a production deployment, the web app (the React frontend
in ai_financial_assistant.jsx) would call these endpoints instead of the
lightweight client-side approximations it uses for the in-chat demo.

Endpoints:
  GET  /api/health                 -> {"status": "ok"}
  POST /api/categorize             -> body: {"description": "Swiggy order"}
                                       returns: {"category": "Food", "confidence": 0.87}
  GET  /api/forecast                -> next month's predicted total + per-category
  POST /api/transactions/reload     -> re-aggregates forecast from an updated CSV

Run: python app.py
Then, e.g.: curl -X POST http://localhost:5000/api/categorize \
              -H "Content-Type: application/json" -d '{"description":"Uber ride"}'
"""
import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

from forecaster import forecast_next_month

MODEL_PATH = "categorizer_model.pkl"
DATA_PATH = "data/transactions_sample.csv"

app = Flask(__name__)
CORS(app)

_model = None
_df = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError("Model not found - run `python train_categorizer.py` first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def get_data():
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH)
    return _df

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/categorize", methods=["POST"])
def categorize():
    body = request.get_json(force=True) or {}
    description = (body.get("description") or "").strip()
    if not description:
        return jsonify({"error": "description is required"}), 400

    model = get_model()
    category = model.predict([description])[0]
    proba = model.predict_proba([description])[0]
    confidence = float(max(proba))

    return jsonify({"category": category, "confidence": round(confidence, 3)})

@app.route("/api/forecast")
def forecast():
    df = get_data()
    total_pred, total_monthly = forecast_next_month(df)

    categories = sorted(df[df["type"] == "expense"]["category"].unique())
    by_category = {}
    for cat in categories:
        pred, _ = forecast_next_month(df, category=cat)
        by_category[cat] = round(pred, 2)

    return jsonify({
        "next_month_total": round(total_pred, 2),
        "by_category": by_category,
        "history": {str(k): round(float(v), 2) for k, v in total_monthly.items()},
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
