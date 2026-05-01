import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

<<<<<<< HEAD
model = None
vectorizer = None

def load_model():
    global model, vectorizer
=======
texts = []
labels = []
>>>>>>> 2a18477 (updated rule engine and fixed false positives)

    try:
        path = os.path.join(os.path.dirname(__file__), "dataset.csv")
        data = pd.read_csv(path, names=["text"], header=None)

<<<<<<< HEAD
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
=======
with open("dataset.csv", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip().lower()
        if not line:
            continue

        if line.startswith("#"):
            if "high" in line:
                current_label = 2
            elif "medium" in line:
                current_label = 1
            else:
                current_label = 0
        else:
            texts.append(line)
            labels.append(current_label)

vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=5000, stop_words="english")
X = vectorizer.fit_transform(texts)

model = LogisticRegression(max_iter=200)
model.fit(X, labels)
>>>>>>> 2a18477 (updated rule engine and fixed false positives)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

def predict(text):
<<<<<<< HEAD
    if model is None or vectorizer is None:
        return "Safe", 50

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = max(model.predict_proba(vec)[0])
=======
    text = text.lower().strip()
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X).max()
>>>>>>> 2a18477 (updated rule engine and fixed false positives)

    if pred == 2:
        return "High", round(prob * 100)
    elif pred == 1:
        return "Medium", round(prob * 100)
    else:
<<<<<<< HEAD
        return "Safe", int(prob * 100)
=======
        return "Safe", round(prob * 100)
>>>>>>> 2a18477 (updated rule engine and fixed false positives)
