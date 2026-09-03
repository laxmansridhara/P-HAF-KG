import os
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import (
    f1_score,
    hamming_loss,
    accuracy_score,
    precision_score,
    recall_score
)

TRAIN_FILE = "data/processed/train.csv"
TEST_FILE = "data/processed/test.csv"

OUTPUT_PREDICTIONS = "data/processed/baseline_random_forest_predictions.csv"
OUTPUT_METRICS = "data/processed/baseline_random_forest_metrics.csv"


def parse_labels(value):
    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    return [
        x.strip().lower()
        for x in value.split(";")
        if x.strip()
    ]


print("=" * 70)
print("TF-IDF + RANDOM FOREST MULTI-LABEL BENCHMARK")
print("=" * 70)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

print("\nTraining shape:", train_df.shape)
print("Test shape:", test_df.shape)

# ------------------------------------------------------------
# TEXT
# ------------------------------------------------------------

X_train = train_df["ingredients_text"].fillna("").astype(str)
X_test = test_df["ingredients_text"].fillna("").astype(str)

# ------------------------------------------------------------
# LABELS
# ------------------------------------------------------------

y_train_labels = train_df["confirmed_allergens"].apply(parse_labels).tolist()
y_test_labels = test_df["confirmed_allergens"].apply(parse_labels).tolist()

mlb = MultiLabelBinarizer()

y_train = mlb.fit_transform(y_train_labels)
y_test = mlb.transform(y_test_labels)

print("\nAllergen classes:")
print(list(mlb.classes_))
print("Number of classes:", len(mlb.classes_))

# ------------------------------------------------------------
# TF-IDF
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 1: TF-IDF")
print("=" * 70)

vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.98,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("Training TF-IDF:", X_train_tfidf.shape)
print("Test TF-IDF:", X_test_tfidf.shape)
print("Vocabulary:", len(vectorizer.vocabulary_))

# ------------------------------------------------------------
# RANDOM FOREST
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 2: RANDOM FOREST")
print("=" * 70)

classifier = OneVsRestClassifier(
    RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
)

print("Training Random Forest...")

classifier.fit(
    X_train_tfidf,
    y_train
)

print("Training complete.")

# ------------------------------------------------------------
# PREDICTION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 3: PREDICTION")
print("=" * 70)

y_pred = classifier.predict(X_test_tfidf)

print("Prediction matrix:", y_pred.shape)

# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

micro_f1 = f1_score(
    y_test,
    y_pred,
    average="micro",
    zero_division=0
)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)

hamming = hamming_loss(
    y_test,
    y_pred
)

exact_match = accuracy_score(
    y_test,
    y_pred
)

micro_precision = precision_score(
    y_test,
    y_pred,
    average="micro",
    zero_division=0
)

micro_recall = recall_score(
    y_test,
    y_pred,
    average="micro",
    zero_division=0
)

# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RANDOM FOREST RESULTS")
print("=" * 70)

print(f"Micro F1          : {micro_f1:.4f}")
print(f"Macro F1          : {macro_f1:.4f}")
print(f"Hamming Loss      : {hamming:.4f}")
print(f"Exact Match Rate  : {exact_match:.4f}")
print(f"Micro Precision   : {micro_precision:.4f}")
print(f"Micro Recall      : {micro_recall:.4f}")

# ------------------------------------------------------------
# LABEL NAMES
# ------------------------------------------------------------

true_labels = mlb.inverse_transform(y_test)
predicted_labels = mlb.inverse_transform(y_pred)

# ------------------------------------------------------------
# PRODUCT PREDICTIONS
# ------------------------------------------------------------

rows = []

for i in range(len(test_df)):

    rows.append({
        "code": test_df.iloc[i]["code"],
        "product_name": test_df.iloc[i]["product_name"],
        "ingredients_text": test_df.iloc[i]["ingredients_text"],
        "true_allergens": ";".join(true_labels[i]),
        "predicted_allergens": ";".join(predicted_labels[i]),
        "correct": true_labels[i] == predicted_labels[i]
    })

prediction_df = pd.DataFrame(rows)

prediction_df.to_csv(
    OUTPUT_PREDICTIONS,
    index=False
)

# ------------------------------------------------------------
# METRICS CSV
# ------------------------------------------------------------

metrics_df = pd.DataFrame([{
    "model": "TF-IDF + Random Forest",
    "train_products": len(train_df),
    "test_products": len(test_df),
    "tfidf_features": X_train_tfidf.shape[1],
    "micro_f1": micro_f1,
    "macro_f1": macro_f1,
    "hamming_loss": hamming,
    "exact_match_rate": exact_match,
    "micro_precision": micro_precision,
    "micro_recall": micro_recall
}])

metrics_df.to_csv(
    OUTPUT_METRICS,
    index=False
)

# ------------------------------------------------------------
# COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(os.path.abspath(OUTPUT_PREDICTIONS))
print(os.path.abspath(OUTPUT_METRICS))

print("\n" + "=" * 70)
print("RANDOM FOREST BENCHMARK COMPLETE")
print("=" * 70)
