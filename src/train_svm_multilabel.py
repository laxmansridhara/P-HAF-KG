import csv
import json
import time
from pathlib import Path

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
    classification_report,
)


# ============================================================
# LARGE-SCALE TF-IDF + LINEAR SVM
# ============================================================

csv.field_size_limit(10_000_000)


# ============================================================
# FILES
# ============================================================

TRAIN_FILE = Path(
    "data/processed/ml/train.csv"
)

VALIDATION_FILE = Path(
    "data/processed/ml/validation.csv"
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

    return texts, labels


# ============================================================
# START
# ============================================================

print("=" * 70)
print("LARGE-SCALE TF-IDF + LINEAR SVM")
print("=" * 70)

start_time = time.time()


# ============================================================
# TRAINING DATA
# ============================================================

print("\nLoading training data...")

X_train_text, y_train_labels = load_dataset(
    TRAIN_FILE
)

print(
    f"Training samples: {len(X_train_text):,}"
)


# ============================================================
# VALIDATION DATA
# ============================================================

print("\nLoading validation data...")

X_val_text, y_val_labels = load_dataset(
    VALIDATION_FILE
)

print(
    f"Validation samples: {len(X_val_text):,}"
)


# ============================================================
# MULTILABEL ENCODING
# ============================================================

mlb = MultiLabelBinarizer(
    classes=TARGET_ALLERGENS
)

Y_train = mlb.fit_transform(
    y_train_labels
)

Y_val = mlb.transform(
    y_val_labels
)


print(
    f"\nNumber of labels: {Y_train.shape[1]}"
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


print("Fitting TF-IDF...")

X_train = vectorizer.fit_transform(
    X_train_text
)

X_train = X_train.copy()

print(
    f"Training matrix: {X_train.shape}"
)


print("Transforming validation data...")

X_val = vectorizer.transform(
    X_val_text
)

X_val = X_val.copy()

print(
    f"Validation matrix: {X_val.shape}"
)


# ============================================================
# TRAIN SVM
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


print("Training model...")

classifier.fit(
    X_train,
    Y_train
)


# ============================================================
# PREDICT
# ============================================================

print("\n")
print("=" * 70)
print("GENERATING VALIDATION PREDICTIONS")
print("=" * 70)


Y_pred = classifier.predict(
    X_val
)


# ============================================================
# METRICS
# ============================================================

micro_precision = precision_score(
    Y_val,
    Y_pred,
    average="micro",
    zero_division=0,
)

micro_recall = recall_score(
    Y_val,
    Y_pred,
    average="micro",
    zero_division=0,
)

micro_f1 = f1_score(
    Y_val,
    Y_pred,
    average="micro",
    zero_division=0,
)

macro_precision = precision_score(
    Y_val,
    Y_pred,
    average="macro",
    zero_division=0,
)

macro_recall = recall_score(
    Y_val,
    Y_pred,
    average="macro",
    zero_division=0,
)

macro_f1 = f1_score(
    Y_val,
    Y_pred,
    average="macro",
    zero_division=0,
)

hamming = hamming_loss(
    Y_val,
    Y_pred
)

exact_match = np.mean(
    np.all(
        Y_val == Y_pred,
        axis=1
    )
)


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("VALIDATION RESULTS")
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
# PER-CLASS REPORT
# ============================================================

print("\n")
print("=" * 70)
print("PER-ALLERGEN PERFORMANCE")
print("=" * 70)

print(
    classification_report(
        Y_val,
        Y_pred,
        target_names=TARGET_ALLERGENS,
        zero_division=0,
    )
)


# ============================================================
# SAVE METRICS
# ============================================================

elapsed = (
    time.time() - start_time
)


metrics = {

    "model":
        "TF-IDF + One-vs-Rest Linear SVM",

    "train_samples":
        len(X_train_text),

    "validation_samples":
        len(X_val_text),

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

    "training_time_seconds":
        float(elapsed),
}


METRICS_FILE = (
    OUTPUT_DIR /
    "validation_metrics.json"
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
# SAVE PARAMETERS
# ============================================================

PARAMETERS_FILE = (
    OUTPUT_DIR /
    "model_parameters.json"
)


parameters = {

    "model":
        "OneVsRest LinearSVC",

    "C":
        1.0,

    "max_iter":
        5000,

    "tfidf_ngram_range":
        [1, 2],

    "tfidf_min_df":
        2,

    "tfidf_max_df":
        0.98,

    "tfidf_sublinear_tf":
        True,

    "tfidf_max_features":
        100_000,

    "labels":
        TARGET_ALLERGENS,

    "target":
        "confirmed_allergens only",
}


with PARAMETERS_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        parameters,
        f,
        indent=2
    )


print("\n")
print("=" * 70)
print("SVM TRAINING COMPLETE")
print("=" * 70)

print(
    f"Training time: {elapsed:.2f} seconds"
)

print(
    f"Metrics saved to:\n{METRICS_FILE}"
)

print(
    f"Parameters saved to:\n{PARAMETERS_FILE}"
)

print("\n")
print("=" * 70)
print("END")
print("=" * 70)
