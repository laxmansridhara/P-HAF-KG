import csv
import json
import time
from pathlib import Path

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
    classification_report,
)


# ============================================================
# P-HAF-KG V2.1
# SVM SILVER TEST EVALUATION
# ============================================================

csv.field_size_limit(10_000_000)


# ============================================================
# FILES
# ============================================================

TRAIN_FILE = Path(
    "data/processed/ml/train.csv"
)

TEST_FILE = Path(
    "data/processed/ml/test_candidate.csv"
)

OUTPUT_DIR = Path(
    "data/processed/ml/svm_model"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LABELS
# ============================================================

TARGET_ALLERGENS = [
    "celery",
    "crustaceans",
    "egg",
    "fish",
    "lupin",
    "milk",
    "molluscs",
    "mustard",
    "peanut",
    "sesame",
    "soy",
    "tree_nut",
    "wheat_gluten",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(path):

    texts = []
    labels = []
    codes = []

    with path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            text = (
                row.get("ingredient_text") or ""
            ).strip()

            if not text:
                continue

            label_string = (
                row.get(
                    "confirmed_allergens"
                ) or ""
            ).strip()

            row_labels = {
                x.strip()
                for x in label_string.split(";")
                if x.strip()
            }

            row_labels = {
                x
                for x in row_labels
                if x in TARGET_ALLERGENS
            }

            texts.append(text)
            labels.append(row_labels)

            codes.append(
                row.get("product_code") or ""
            )

    return texts, labels, codes


# ============================================================
# START
# ============================================================

print("=" * 70)
print("SVM SILVER TEST EVALUATION")
print("=" * 70)

start_time = time.time()


# ============================================================
# LOAD TRAIN
# ============================================================

print("\nLoading training data...")

X_train_text, y_train_labels, _ = load_dataset(
    TRAIN_FILE
)

print(
    f"Training samples: {len(X_train_text):,}"
)


# ============================================================
# LOAD TEST
# ============================================================

print("\nLoading silver test candidate...")

X_test_text, y_test_labels, test_codes = load_dataset(
    TEST_FILE
)

print(
    f"Test samples: {len(X_test_text):,}"
)


# ============================================================
# MULTILABEL ENCODING
# ============================================================

print("\nEncoding labels...")

mlb = MultiLabelBinarizer(
    classes=TARGET_ALLERGENS
)

Y_train = mlb.fit_transform(
    y_train_labels
)

Y_test = mlb.transform(
    y_test_labels
)


# ============================================================
# TF-IDF
# ============================================================

print("\n")
print("=" * 70)
print("TF-IDF FEATURE EXTRACTION")
print("=" * 70)

vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.98,
    sublinear_tf=True,
    max_features=100_000,
)

print("Fitting TF-IDF using TRAINING DATA ONLY...")

X_train = vectorizer.fit_transform(
    X_train_text
)

X_train = X_train.copy()

print(
    f"Training matrix: {X_train.shape}"
)

print("Transforming TEST DATA...")

X_test = vectorizer.transform(
    X_test_text
)

X_test = X_test.copy()

print(
    f"Test matrix: {X_test.shape}"
)


# ============================================================
# SVM
# ============================================================

print("\n")
print("=" * 70)
print("TRAINING LINEAR SVM")
print("=" * 70)

classifier = OneVsRestClassifier(
    LinearSVC(
        C=1.0,
        max_iter=5000,
    ),
    n_jobs=1,
)

print(
    "Training on TRAINING DATA ONLY..."
)

classifier.fit(
    X_train,
    Y_train
)


# ============================================================
# TEST PREDICTION
# ============================================================

print("\n")
print("=" * 70)
print("GENERATING SILVER TEST PREDICTIONS")
print("=" * 70)

Y_pred = classifier.predict(
    X_test
)


# ============================================================
# METRICS
# ============================================================

micro_precision = precision_score(
    Y_test,
    Y_pred,
    average="micro",
    zero_division=0,
)

micro_recall = recall_score(
    Y_test,
    Y_pred,
    average="micro",
    zero_division=0,
)

micro_f1 = f1_score(
    Y_test,
    Y_pred,
    average="micro",
    zero_division=0,
)

macro_precision = precision_score(
    Y_test,
    Y_pred,
    average="macro",
    zero_division=0,
)

macro_recall = recall_score(
    Y_test,
    Y_pred,
    average="macro",
    zero_division=0,
)

macro_f1 = f1_score(
    Y_test,
    Y_pred,
    average="macro",
    zero_division=0,
)

hamming = hamming_loss(
    Y_test,
    Y_pred
)

exact_match = np.mean(
    np.all(
        Y_test == Y_pred,
        axis=1
    )
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("SILVER TEST RESULTS")
print("=" * 70)

print(
    f"Micro Precision: {micro_precision:.4f}"
)

print(
    f"Micro Recall:    {micro_recall:.4f}"
)

print(
    f"Micro F1:        {micro_f1:.4f}"
)

print(
    f"Macro Precision: {macro_precision:.4f}"
)

print(
    f"Macro Recall:    {macro_recall:.4f}"
)

print(
    f"Macro F1:        {macro_f1:.4f}"
)

print(
    f"Hamming Loss:    {hamming:.4f}"
)

print(
    f"Exact Match:     {exact_match:.4f}"
)


# ============================================================
# PER-ALLERGEN RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("PER-ALLERGEN SILVER TEST PERFORMANCE")
print("=" * 70)

report_text = classification_report(
    Y_test,
    Y_pred,
    target_names=TARGET_ALLERGENS,
    zero_division=0,
)

print(report_text)


# ============================================================
# SAVE TEST PREDICTIONS
# ============================================================

PREDICTION_FILE = (
    OUTPUT_DIR /
    "silver_test_predictions.csv"
)

with PREDICTION_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)

    header = [
        "product_code"
    ]

    for label in TARGET_ALLERGENS:
        header.append(
            f"true_{label}"
        )

    for label in TARGET_ALLERGENS:
        header.append(
            f"pred_{label}"
        )

    writer.writerow(header)

    for index, code in enumerate(
        test_codes
    ):

        output_row = [code]

        output_row.extend(
            Y_test[index].tolist()
        )

        output_row.extend(
            Y_pred[index].tolist()
        )

        writer.writerow(output_row)


# ============================================================
# SAVE METRICS
# ============================================================

elapsed = (
    time.time() - start_time
)

metrics = {
    "model":
        "TF-IDF + One-vs-Rest Linear SVM",

    "evaluation":
        "silver_test",

    "train_samples":
        len(X_train_text),

    "test_samples":
        len(X_test_text),

    "tfidf_features":
        int(X_train.shape[1]),

    "micro_precision":
        float(micro_precision),

    "micro_recall":
        float(micro_recall),

    "micro_f1":
        float(micro_f1),

    "macro_precision":
        float(macro_precision),

    "macro_recall":
        float(macro_recall),

    "macro_f1":
        float(macro_f1),

    "hamming_loss":
        float(hamming),

    "exact_match":
        float(exact_match),

    "training_and_evaluation_time_seconds":
        float(elapsed),
}


METRICS_FILE = (
    OUTPUT_DIR /
    "silver_test_metrics.json"
)

with METRICS_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metrics,
        f,
        indent=2
    )


# ============================================================
# SAVE MODEL CONFIGURATION
# ============================================================

CONFIG_FILE = (
    OUTPUT_DIR /
    "silver_test_configuration.json"
)

configuration = {
    "vectorizer": {
        "lowercase": True,
        "strip_accents": "unicode",
        "ngram_range": [1, 2],
        "min_df": 2,
        "max_df": 0.98,
        "sublinear_tf": True,
        "max_features": 100_000,
    },

    "classifier": {
        "model": "OneVsRest LinearSVC",
        "C": 1.0,
        "max_iter": 5000,
        "n_jobs": 1,
    },

    "target":
        "confirmed_allergens only",

    "test_type":
        "silver holdout; labels generated by P-HAF-KG V2.1",

    "random_seed":
        42,
}


with CONFIG_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        configuration,
        f,
        indent=2
    )


# ============================================================
# END
# ============================================================

print("\n")
print("=" * 70)
print("SILVER TEST EVALUATION COMPLETE")
print("=" * 70)

print(
    f"Training samples: {len(X_train_text):,}"
)

print(
    f"Test samples:     {len(X_test_text):,}"
)

print(
    f"TF-IDF features:   {X_train.shape[1]:,}"
)

print(
    f"Elapsed time:      {elapsed:.2f} seconds"
)

print("\nSaved:")

print(
    METRICS_FILE
)

print(
    PREDICTION_FILE
)

print(
    CONFIG_FILE
)

print("\n")
print("=" * 70)
print("END")
print("=" * 70)
