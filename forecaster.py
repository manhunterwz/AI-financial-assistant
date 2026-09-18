"""
forecaster.py
-------------
Forecasts next month's total spending (and per-category spending) from
transaction history.

Approach: aggregate expenses into monthly totals, then fit an ordinary
least-squares Linear Regression of amount ~ month_index. This is a
deliberately simple, explainable model (a straight-line trend) rather than
something like ARIMA/Prophet/LSTM - with only a handful of months of data,
a simple trend generalizes better and is much easier to defend in a viva
than a complex model that's effectively overfitting noise. The README
explains how to swap in a more sophisticated model once real, longer
transaction history is available.

Run: python forecaster.py
Outputs: forecast_plot.png, and prints the next-month forecast.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

DATA_PATH = "data/transactions_sample.csv"

def _monthly_totals(df, category=None):
    d = df[df["type"] == "expense"].copy()
    if category:
        d = d[d["category"] == category]
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d["date"].dt.to_period("M")
    monthly = d.groupby("month")["amount"].sum().sort_index()
    return monthly

def forecast_next_month(df, category=None):
    monthly = _monthly_totals(df, category)
    if len(monthly) < 2:
        # not enough history for a trend - fall back to the last known value
        return float(monthly.iloc[-1]) if len(monthly) else 0.0, monthly
    X = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly.values
    model = LinearRegression().fit(X, y)
    next_month_pred = model.predict([[len(monthly)]])[0]
    return max(0.0, float(next_month_pred)), monthly

def main():
    df = pd.read_csv(DATA_PATH)

    total_forecast, total_monthly = forecast_next_month(df)
    print(f"Historical monthly totals:\n{total_monthly}\n")
    print(f"Forecast for next month (overall): Rs {total_forecast:,.2f}\n")

    categories = sorted(df[df["type"] == "expense"]["category"].unique())
    by_category = {}
    for cat in categories:
        pred, _ = forecast_next_month(df, category=cat)
        by_category[cat] = round(pred, 2)
        print(f"  {cat:20s} -> Rs {pred:,.2f}")

    # plot overall trend + forecast point
    months = [str(m) for m in total_monthly.index]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(months, total_monthly.values, marker="o", color="#1F6F54", label="Actual")
    ax.plot([months[-1], "Next month"], [total_monthly.values[-1], total_forecast],
            marker="o", linestyle="--", color="#E8A33D", label="Forecast")
    ax.set_ylabel("Total spend (Rs)")
    ax.set_title("Monthly Spending Trend & Next-Month Forecast")
    ax.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("forecast_plot.png", dpi=150)
    print("\nSaved forecast_plot.png")

if __name__ == "__main__":
    main()
