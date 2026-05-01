import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

model = None
vectorizer = None

def load_model():
    global model, vectorizer
    try:
        path = os.path.join(os.path.dirname(__file__), "dataset.csv")
        data = pd.read_csv(path, names=["text"], header=None)

        texts = []
        labels = []
        current_label = None

        for line in data["text"]:
            line = str(line).strip().lower()

            if line.startswith("#"):
                if "high" in line:
                    current_label = 2
                elif "medium" in line:
                    current_label = 1
                elif "safe" in line:
                    current_label = 0
                continue

            if line:
                texts.append(line)
                labels.append(current_label)

        vectorizer = TfidfVectorizer(ngram_range=(1,2))
        X = vectorizer.fit_transform(texts)

        model = LogisticRegression(max_iter=1000)
        model.fit(X, labels)

    except Exception as e:
        print("MODEL ERROR:", e)

load_model()

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

def predict(text):
    if model is None or vectorizer is None:
        return "Safe", 50

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = max(model.predict_proba(vec)[0])

    if pred == 2:
        return "High", round(prob * 100)
    elif pred == 1:
        return "Medium", round(prob * 100)
    else:
        return "Safe", round(prob * 100)
