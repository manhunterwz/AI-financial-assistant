import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class ExpenseCategorizer:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.models_dir = Path(__file__).parent / 'trained_models'
        self.vectorizer_path = self.models_dir / 'tfidf_vectorizer.pkl'
        self.classifier_path = self.models_dir / 'categorizer.pkl'

    def train(self, descriptions, categories):
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer = TfidfVectorizer(max_features=1000)
        X = self.vectorizer.fit_transform(descriptions)
        
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.classifier.fit(X, categories)
        
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.classifier, self.classifier_path)

    def predict(self, description):
        if self.vectorizer is None or self.classifier is None:
            if not self.vectorizer_path.exists() or not self.classifier_path.exists():
                raise FileNotFoundError("Models not trained yet.")
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.classifier = joblib.load(self.classifier_path)
        
        X = self.vectorizer.transform([description])
        category = self.classifier.predict(X)[0]
        proba = self.classifier.predict_proba(X)[0]
        confidence = max(proba)
        
        return category, float(confidence)
