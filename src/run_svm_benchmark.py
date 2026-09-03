import os
import json
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import (
    f1_score,
    hamming_loss,
    accuracy_score,
    precision_score,
    recall_score
)


# ============================================================
# P-HAF-KG V2.1
# SUPERVISED ML BASELINE: TF-IDF + LINEAR SVM
# ============================================================

TRAIN_FILE = "data/processed/train.csv"
TEST_FILE = "data/processed/test.csv"

OUTPUT_PREDICTIONS = (
    "data/processed/baseline_svm_predictions.csv"
)

OUTPUT_METRICS = (
    "data/processed/baseline_svm_metrics.csv"
)

MODEL_NAME = "TF-IDF + Linear SVM"


# ============================================================
# HELPERS
# ============================================================

def parse_labels(value):
    """
    Convert:
        'peanut;milk;soy'
    into:
        ['peanut', 'milk', 'soy']

    Missing values become [].
    """

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


def calculate_exact_match(y_true, y_pred):
    """
    Exact Match Rate:
    percentage of samples where the COMPLETE
    predicted allergen set exactly matches
    the ground-truth allergen set.
    """

    return accuracy_score(y_true, y_pred)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("TF-IDF + LINEAR SVM MULTI-LABEL BENCHMARK")
print("=" * 70)

print("\nLoading training data:")
print(TRAIN_FILE)

train_df = pd.read_csv(TRAIN_FILE)

print("Training shape:", train_df.shape)

print("\nLoading test data:")
print(TEST_FILE)

test_df = pd.read_csv(TEST_FILE)

print("Test shape:", test_df.shape)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "ingredients_text",
    "confirmed_allergens"
]

for column in required_columns:

    if column not in train_df.columns:
        raise ValueError(
            f"Missing column in train.csv: {column}"
        )

    if column not in test_df.columns:
        raise ValueError(
            f"Missing column in test.csv: {column}"
        )


# ============================================================
# PREPARE TEXT
# ============================================================

X_train = (
    train_df["ingredients_text"]
    .fillna("")
    .astype(str)
)

X_test = (
    test_df["ingredients_text"]
    .fillna("")
    .astype(str)
)


# ============================================================
# PREPARE MULTI-LABEL TARGET
# ============================================================

y_train_labels = (
    train_df["confirmed_allergens"]
    .apply(parse_labels)
    .tolist()
)

y_test_labels = (
    test_df["confirmed_allergens"]
    .apply(parse_labels)
    .tolist()
)


print("\nExample training labels:")

for i in range(min(5, len(y_train_labels))):
    print(
        i + 1,
        "->",
        y_train_labels[i]
    )


# ============================================================
# LABEL ENCODING
# ============================================================

mlb = MultiLabelBinarizer()

y_train = mlb.fit_transform(
    y_train_labels
)

y_test = mlb.transform(
    y_test_labels
)

print("\nAllergen classes:")
print(list(mlb.classes_))

print(
    "\nNumber of allergen classes:",
    len(mlb.classes_)
)


# ============================================================
# TF-IDF
# ============================================================

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

X_train_tfidf = vectorizer.fit_transform(
    X_train
)

X_test_tfidf = vectorizer.transform(
    X_test
)

print(
    "Training TF-IDF shape:",
    X_train_tfidf.shape
)

print(
    "Test TF-IDF shape:",
    X_test_tfidf.shape
)

print(
    "Vocabulary size:",
    len(vectorizer.vocabulary_)
)


# ============================================================
# LINEAR SVM
# ============================================================

print("\n" + "=" * 70)
print("STEP 2: LINEAR SVM")
print("=" * 70)

classifier = OneVsRestClassifier(
    LinearSVC(
        C=1.0,
        class_weight="balanced",
        random_state=42
    )
)

print("Training Linear SVM...")

classifier.fit(
    X_train_tfidf,
    y_train
)

print("Training complete.")


# ============================================================
# PREDICTION
# ============================================================

print("\n" + "=" * 70)
print("STEP 3: PREDICTION")
print("=" * 70)

y_pred = classifier.predict(
    X_test_tfidf
)

print(
    "Prediction matrix:",
    y_pred.shape
)


# ============================================================
# METRICS
# ============================================================

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

exact_match = calculate_exact_match(
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


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("LINEAR SVM RESULTS")
print("=" * 70)

print(
    f"Micro F1          : {micro_f1:.4f}"
)

print(
    f"Macro F1          : {macro_f1:.4f}"
)

print(
    f"Hamming Loss      : {hamming:.4f}"
)

print(
    f"Exact Match Rate  : {exact_match:.4f}"
)

print(
    f"Micro Precision   : {micro_precision:.4f}"
)

print(
    f"Micro Recall      : {micro_recall:.4f}"
)


# ============================================================
# CONVERT PREDICTIONS TO LABEL NAMES
# ============================================================

predicted_labels = mlb.inverse_transform(
    y_pred
)

true_labels = mlb.inverse_transform(
    y_test
)


# ============================================================
# SAVE PRODUCT-LEVEL PREDICTIONS
# ============================================================

prediction_rows = []

for i in range(len(test_df)):

    prediction_rows.append({

        "code":
            test_df.iloc[i]["code"],

        "product_name":
            test_df.iloc[i]["product_name"],

        "ingredients_text":
            test_df.iloc[i]["ingredients_text"],

        "true_allergens":
            ";".join(true_labels[i]),

        "predicted_allergens":
            ";".join(predicted_labels[i]),

        "correct":
            true_labels[i] == predicted_labels[i]
    })


prediction_df = pd.DataFrame(
    prediction_rows
)

os.makedirs(
    "data/processed",
    exist_ok=True
)

prediction_df.to_csv(
    OUTPUT_PREDICTIONS,
    index=False
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics_df = pd.DataFrame([
    {
        "model":
            MODEL_NAME,

        "train_products":
            len(train_df),

        "test_products":
            len(test_df),

        "tfidf_features":
            X_train_tfidf.shape[1],

        "micro_f1":
            micro_f1,

        "macro_f1":
            macro_f1,

        "hamming_loss":
            hamming,

        "exact_match_rate":
            exact_match,

        "micro_precision":
            micro_precision,

        "micro_recall":
            micro_recall
    }
])

metrics_df.to_csv(
    OUTPUT_METRICS,
    index=False
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    "Predictions:"
)
print(
    os.path.abspath(OUTPUT_PREDICTIONS)
)

print(
    "\nMetrics:"
)
print(
    os.path.abspath(OUTPUT_METRICS)
)

print("\n" + "=" * 70)
print("SVM BENCHMARK COMPLETE")
print("=" * 70)
