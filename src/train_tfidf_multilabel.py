import csv
import json
import time
from pathlib import Path

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
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
# LARGE-SCALE TF-IDF MULTILABEL NLP MODEL
# ============================================================

# ------------------------------------------------------------
# Allow very large CSV fields.
# Some ingredient_text values are larger than Python's
# default 131,072-character CSV limit.
# ------------------------------------------------------------

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
    "data/processed/ml/tfidf_model"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TARGET ALLERGENS
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
# LOAD DATASET
# ============================================================

def load_dataset(path):
    """
    Load ingredient text and confirmed-allergen labels.

    Returns
    -------
    texts : list[str]
        Ingredient text for each product.

    labels : list[set[str]]
        Confirmed allergens for each product.
    """

    texts = []
    labels = []

    with path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            # ------------------------------------------------
            # Ingredient text
            # ------------------------------------------------

            text = (
                row.get("ingredient_text") or ""
            ).strip()

            if not text:
                continue


            # ------------------------------------------------
            # Confirmed allergen labels
            #
            # IMPORTANT:
            # Potential allergens are NOT used as the primary
            # ML target in this experiment.
            # ------------------------------------------------

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
print("LARGE-SCALE TF-IDF MULTILABEL MODEL")
print("=" * 70)


start_time = time.time()


# ============================================================
# LOAD TRAINING DATA
# ============================================================

print("\nLoading training data...")

X_train_text, y_train_labels = load_dataset(
    TRAIN_FILE
)

print(
    f"Training samples: {len(X_train_text):,}"
)


# ============================================================
# LOAD VALIDATION DATA
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

print("\n")
print("=" * 70)
print("MULTILABEL ENCODING")
print("=" * 70)


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
    f"Number of labels: "
    f"{Y_train.shape[1]}"
)


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

print("\nTraining label distribution:")
print("-" * 70)

for index, label in enumerate(
    TARGET_ALLERGENS
):

    count = int(
        Y_train[:, index].sum()
    )

    print(
        f"{label:20s} {count:10,}"
    )


print("\nValidation label distribution:")
print("-" * 70)

for index, label in enumerate(
    TARGET_ALLERGENS
):

    count = int(
        Y_val[:, index].sum()
    )

    print(
        f"{label:20s} {count:10,}"
    )


# ============================================================
# TF-IDF FEATURE EXTRACTION
# ============================================================

print("\n")
print("=" * 70)
print("TF-IDF FEATURE EXTRACTION")
print("=" * 70)


vectorizer = TfidfVectorizer(

    # Convert text to lowercase.
    lowercase=True,

    # Normalise accented characters.
    strip_accents="unicode",

    # Use individual words and adjacent word pairs.
    ngram_range=(1, 2),

    # Ignore extremely rare terms.
    min_df=2,

    # Ignore terms appearing in almost every document.
    max_df=0.98,

    # Log-scaled term-frequency transformation.
    sublinear_tf=True,

    # Prevent an unnecessarily huge feature matrix.
    max_features=100_000,
)


print("Fitting TF-IDF...")

X_train = vectorizer.fit_transform(
    X_train_text
)


# ------------------------------------------------------------
# IMPORTANT FIX
#
# Make the sparse matrix writable before scikit-learn
# performs sparse operations.
# ------------------------------------------------------------

X_train = X_train.copy()


print(
    f"Training matrix: "
    f"{X_train.shape}"
)


print("Transforming validation data...")

X_val = vectorizer.transform(
    X_val_text
)


# ------------------------------------------------------------
# IMPORTANT FIX
# ------------------------------------------------------------

X_val = X_val.copy()


print(
    f"Validation matrix: "
    f"{X_val.shape}"
)


# ============================================================
# TRAIN MODEL
# ============================================================

print("\n")
print("=" * 70)
print("TRAINING LOGISTIC REGRESSION")
print("=" * 70)


classifier = OneVsRestClassifier(

    LogisticRegression(

        # Maximum optimisation iterations.
        max_iter=1000,

        # Regularisation strength.
        C=2.0,

        # Efficient solver for this sparse binary setup.
        solver="liblinear",
    ),

    # --------------------------------------------------------
    # IMPORTANT:
    # Use one process instead of multiple joblib workers.
    #
    # This avoids the WRITEBACKIFCOPY / read-only sparse
    # matrix error encountered on the current environment.
    # --------------------------------------------------------

    n_jobs=1,
)


print("Training model...")

classifier.fit(
    X_train,
    Y_train
)


# ============================================================
# VALIDATION PREDICTION
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

print("\n")
print("=" * 70)
print("CALCULATING METRICS")
print("=" * 70)


# ------------------------------------------------------------
# Micro metrics
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Macro metrics
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Hamming loss
# ------------------------------------------------------------

hamming = hamming_loss(
    Y_val,
    Y_pred,
)


# ------------------------------------------------------------
# Exact-match accuracy
#
# All 13 labels must be correct for a product.
# ------------------------------------------------------------

exact_match = np.mean(
    np.all(
        Y_val == Y_pred,
        axis=1
    )
)


# ============================================================
# OVERALL VALIDATION RESULTS
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
# PER-ALLERGEN PERFORMANCE
# ============================================================

print("\n")
print("=" * 70)
print("PER-ALLERGEN PERFORMANCE")
print("=" * 70)


report = classification_report(
    Y_val,
    Y_pred,
    target_names=TARGET_ALLERGENS,
    zero_division=0,
)

print(report)


# ============================================================
# SAVE PREDICTIONS
# ============================================================

PREDICTIONS_FILE = (
    OUTPUT_DIR /
    "validation_predictions.csv"
)


with PREDICTIONS_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)


    header = [
        "product_index"
    ]


    for label in TARGET_ALLERGENS:

        header.append(
            f"true_{label}"
        )


    for label in TARGET_ALLERGENS:

        header.append(
            f"pred_{label}"
        )


    writer.writerow(
        header
    )


    for index in range(
        len(Y_val)
    ):

        row = [
            index
        ]


        # True labels
        row.extend(
            Y_val[index].tolist()
        )


        # Predicted labels
        row.extend(
            Y_pred[index].tolist()
        )


        writer.writerow(
            row
        )


# ============================================================
# SAVE METRICS
# ============================================================

elapsed_seconds = (
    time.time() - start_time
)


METRICS_FILE = (
    OUTPUT_DIR /
    "validation_metrics.json"
)


metrics = {

    "model":
        "TF-IDF + One-vs-Rest Logistic Regression",

    "task":
        "13-label confirmed allergen multilabel classification",

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
        float(elapsed_seconds),
}


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
# SAVE MODEL PARAMETERS
# ============================================================

PARAMETERS_FILE = (
    OUTPUT_DIR /
    "model_parameters.json"
)


parameters = {

    "vectorizer": {

        "lowercase":
            True,

        "strip_accents":
            "unicode",

        "ngram_range":
            [1, 2],

        "min_df":
            2,

        "max_df":
            0.98,

        "sublinear_tf":
            True,

        "max_features":
            100_000,
    },


    "classifier": {

        "model":
            "OneVsRest Logistic Regression",

        "C":
            2.0,

        "max_iter":
            1000,

        "solver":
            "liblinear",

        "n_jobs":
            1,
    },


    "labels":
        TARGET_ALLERGENS,


    "target_definition":
        "confirmed_allergens only",

    "potential_allergens_usage":
        "excluded from primary ML target",
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


# ============================================================
# SAVE VOCABULARY SIZE
# ============================================================

VOCAB_FILE = (
    OUTPUT_DIR /
    "tfidf_vocabulary_size.txt"
)


with VOCAB_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    f.write(
        str(
            len(
                vectorizer.vocabulary_
            )
        )
    )


# ============================================================
# FINAL INFORMATION
# ============================================================

print("\n")
print("=" * 70)
print("MODEL TRAINING COMPLETE")
print("=" * 70)


print(
    f"Training samples:    "
    f"{len(X_train_text):,}"
)

print(
    f"Validation samples:  "
    f"{len(X_val_text):,}"
)

print(
    f"TF-IDF features:     "
    f"{X_train.shape[1]:,}"
)

print(
    f"Training time:       "
    f"{elapsed_seconds:.2f} seconds"
)


print("\nSaved files:")

print(
    METRICS_FILE
)

print(
    PARAMETERS_FILE
)

print(
    PREDICTIONS_FILE
)

print(
    VOCAB_FILE
)


print("\n")
print("=" * 70)
print("END")
print("=" * 70)