# AI Financial Assistant — ML Backend

This is the machine-learning half of the project: real, trained models for
the two "AI" jobs that benefit from statistical learning rather than an LLM
call — **expense categorization** and **spending forecasting**. The chat/
advice part of the assistant is handled separately by an LLM (see the
web app's explanation) since that's an open-ended language task, not a
classification/regression one.

## Project structure

```
ai_financial_backend/
├── data/
│   └── transactions_sample.csv   # synthetic sample transaction history
├── generate_data.py              # (re)generates the sample dataset
├── train_categorizer.py          # trains + evaluates the categorizer
├── forecaster.py                 # monthly spend forecasting model
├── app.py                        # Flask REST API serving both models
├── categorizer_model.pkl         # trained model (created by training script)
├── confusion_matrix.png          # evaluation output
├── forecast_plot.png             # forecast output
├── metrics.txt                   # accuracy + classification report
└── requirements.txt
```

## 1. Expense categorizer

**Problem:** given free-text like `"Swiggy order"` or `"Uber ride"`, predict
which of 8 categories it belongs to (Food, Transport, Shopping, Bills &
Utilities, Entertainment, Health, Education, Other).

**Model:** `TfidfVectorizer` (unigrams + bigrams) → `MultinomialNB`.

Why this and not something heavier (BERT, an LLM call, etc.):
- Transaction descriptions are short and keyword-driven ("swiggy", "uber",
  "netflix" are near-perfect category signals) — a bag-of-words model
  captures almost all the useful signal.
- Naive Bayes needs very little training data and trains in milliseconds,
  which matters when the model may need retraining as a user's own
  transaction history grows.
- It's a **generative, probabilistic** model — you can explain a prediction
  in one sentence ("the word 'hospital' has high likelihood under Health"),
  which is much easier to defend in a viva than a black-box deep model.

**Measured performance** (80/20 train/test split, stratified by category):
overall accuracy **93.2%** (see `metrics.txt` and `confusion_matrix.png`
for the full per-class precision/recall — the one notable confusion in
testing was "hospital bill" leaning towards Bills & Utilities instead of
Health, which is a reasonable ambiguity to raise as a discussion point).

Run it:
```bash
python train_categorizer.py
```

## 2. Spending forecaster

**Problem:** predict next month's total spend, and next month's spend per
category, from historical monthly totals.

**Model:** ordinary least-squares **Linear Regression** of
`monthly_total ~ month_index`, fit separately overall and per category.

Why a straight-line trend and not ARIMA/Prophet/LSTM: with only a few
months of history, a simple trend model generalizes better and won't
overfit noise the way a more complex time-series model would. The code is
structured so `forecast_next_month()` is the only function a more advanced
model would need to replace once there's a year+ of real transaction data
to train on — that's a natural "future work" line for your report.

Run it:
```bash
python forecaster.py
```

## 3. Serving both as an API

```bash
pip install -r requirements.txt
python generate_data.py        # (already generated once, re-run any time)
python train_categorizer.py    # produces categorizer_model.pkl
python app.py                  # starts the API on http://localhost:5000
```

Endpoints:
| Method | Path                 | Body                              | Returns                                   |
|--------|----------------------|------------------------------------|--------------------------------------------|
| GET    | `/api/health`         | —                                   | `{"status": "ok"}`                          |
| POST   | `/api/categorize`     | `{"description": "Swiggy order"}`   | `{"category": "Food", "confidence": 0.87}`  |
| GET    | `/api/forecast`       | —                                   | next-month total + per-category + history   |

Tested manually with `curl` — all three endpoints return correct results
against the sample dataset.

## How this fits the full project

The React web app (the interactive demo) is the part your evaluators will
actually click through. Inside Claude.ai's artifact sandbox it can't keep a
Flask process running in the background, so the demo approximates these two
models client-side (a small keyword-rule categorizer, a least-squares trend
computed in JS) and uses a real LLM call for the open-ended advice chat.
**This folder is the real version of those two models** — if you deploy the
React app outside Claude (e.g. on Vercel/Netlify + this Flask API on
Render/Railway), you'd swap the two client-side approximations for real
`fetch()` calls to `/api/categorize` and `/api/forecast`, and nothing else
about the UI needs to change. That mapping — "here's the simplified version
running live, here's the real trained model behind it" — is exactly the
kind of thing worth walking through in a viva.
