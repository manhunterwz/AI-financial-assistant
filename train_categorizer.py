"""
train_categorizer.py
---------------------
Trains a text classifier that reads a transaction description (e.g. "Swiggy
order") and predicts an expense category (e.g. "Food").

Pipeline: TF-IDF (bag-of-words, weighted by term importance) -> Multinomial
Naive Bayes. This combination is the standard baseline for short-text
classification: it's fast to train, needs very little data, and - unlike a
neural model - its decisions are easy to inspect and explain in a viva
("the word 'swiggy' has a high likelihood under Food, so that dominates the
posterior").

Run: python train_categorizer.py
Outputs:
  - categorizer_model.pkl   (the fitted sklearn Pipeline, ready to predict)
  - confusion_matrix.png    (visual evaluation)
  - metrics.txt             (accuracy + full classification report)
"""
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay

DATA_PATH = "data/transactions_sample.csv"
MODEL_PATH = "categorizer_model.pkl"

def main():
    df = pd.read_csv(DATA_PATH)
    df = df[df["type"] == "expense"].copy()  # only expenses have a category to learn

    X = df["description"]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)),
        ("clf", MultinomialNB(alpha=0.3)),
    ])
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)

    print(f"Test accuracy: {acc:.3f}\n")
    print(report)

    with open("metrics.txt", "w") as f:
        f.write(f"Test accuracy: {acc:.3f}\n\n")
        f.write(report)

    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(7, 6))
    disp.plot(ax=ax, xticks_rotation=45, colorbar=False, cmap="Greens")
    plt.title("Expense Categorizer - Confusion Matrix")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=150)
    print("Saved confusion_matrix.png and metrics.txt")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")

    # quick sanity check on a few unseen-style descriptions
    samples = ["Swiggy order late night", "Uber to college", "Netflix renewal",
               "Hospital bill payment", "Bought a new phone"]
    preds = pipeline.predict(samples)
    print("\nSample predictions:")
    for s, p in zip(samples, preds):
        print(f"  {s!r:40s} -> {p}")

if __name__ == "__main__":
    main()
