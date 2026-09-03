import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss
)


# ============================================================
# CONFIGURATION
# ============================================================

TRAIN_FILE = Path(
    "data/processed/train.csv"
)

TEST_FILE = Path(
    "data/processed/test.csv"
)

ALLERGENS = [
    "peanut",
    "milk",
    "egg",
    "soy",
    "wheat_gluten",
    "sesame",
    "tree_nut",
]


METRICS_FILE = Path(
    "data/processed/baseline_tfidf_final_metrics.csv"
)

PREDICTION_FILE = Path(
    "data/processed/baseline_tfidf_predictions.csv"
)


# ============================================================
# LABEL PARSER
# ============================================================

def parse_labels(value):

    if not value:
        return set()

    return {
        x.strip().lower()
        for x in value.split(";")
        if x.strip()
    }


# ============================================================
# CREATE MULTI-LABEL MATRIX
# ============================================================

def make_matrix(rows):

    matrix = []

    for row in rows:

        labels = parse_labels(
            row["confirmed_allergens"]
        )

        matrix.append([
            int(allergen in labels)
            for allergen in ALLERGENS
        ])

    return matrix


# ============================================================
# LOAD TRAINING DATA
# ============================================================

with TRAIN_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    train_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# LOAD TEST DATA
# ============================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# EXTRACT TEXT
# ============================================================

X_train_text = [
    row["ingredients_text"]
    for row in train_rows
]

X_test_text = [
    row["ingredients_text"]
    for row in test_rows
]


# ============================================================
# CREATE LABEL MATRICES
# ============================================================

y_train = make_matrix(
    train_rows
)

y_test = make_matrix(
    test_rows
)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("FINAL BASELINE 2: TF-IDF + LOGISTIC REGRESSION")
print("=" * 70)

print(
    "Training products:",
    len(train_rows)
)

print(
    "Testing products:",
    len(test_rows)
)


# ============================================================
# TF-IDF
# ============================================================

print("\n===== TF-IDF =====")

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
    sublinear_tf=True
)


X_train = vectorizer.fit_transform(
    X_train_text
)

X_test = vectorizer.transform(
    X_test_text
)


print(
    "Training TF-IDF shape:",
    X_train.shape
)

print(
    "Test TF-IDF shape:",
    X_test.shape
)

print(
    "Vocabulary size:",
    X_train.shape[1]
)


# ============================================================
# MULTI-LABEL LOGISTIC REGRESSION
# ============================================================

print(
    "\n===== ONE-VS-REST LOGISTIC REGRESSION ====="
)

model = OneVsRestClassifier(
    LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )
)


model.fit(
    X_train,
    y_train
)

print(
    "Training complete."
)


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(
    X_test
)


print(
    "\nPrediction matrix:",
    y_pred.shape
)


# ============================================================
# PER-ALLERGEN RESULTS
# ============================================================

print(
    "\n===== PER-ALLERGEN RESULTS ====="
)

results = []


for i, allergen in enumerate(
    ALLERGENS
):

    true_values = [
        row[i]
        for row in y_test
    ]

    predicted_values = [
        row[i]
        for row in y_pred
    ]


    precision = precision_score(
        true_values,
        predicted_values,
        zero_division=0
    )


    recall = recall_score(
        true_values,
        predicted_values,
        zero_division=0
    )


    f1 = f1_score(
        true_values,
        predicted_values,
        zero_division=0
    )


    support = sum(
        true_values
    )


    results.append({

        "allergen":
            allergen,

        "precision":
            precision,

        "recall":
            recall,

        "f1":
            f1,

        "support":
            support
    })


    print(
        f"{allergen:15} "
        f"Precision={precision:.4f} "
        f"Recall={recall:.4f} "
        f"F1={f1:.4f} "
        f"Support={support}"
    )


# ============================================================
# OVERALL METRICS
# ============================================================

macro_precision = precision_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)


macro_recall = recall_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)


macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
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


micro_f1 = f1_score(
    y_test,
    y_pred,
    average="micro",
    zero_division=0
)


hl = hamming_loss(
    y_test,
    y_pred
)


# ============================================================
# EXACT MATCH
# ============================================================

exact_matches = 0


for i in range(
    len(y_test)
):

    if list(y_test[i]) == list(
        y_pred[i]
    ):

        exact_matches += 1


exact_match_rate = (
    exact_matches
    / len(y_test)
)


# ============================================================
# DISPLAY OVERALL RESULTS
# ============================================================

print(
    "\n===== OVERALL RESULTS ====="
)

print(
    f"Macro Precision   : "
    f"{macro_precision:.4f}"
)

print(
    f"Macro Recall      : "
    f"{macro_recall:.4f}"
)

print(
    f"Macro F1          : "
    f"{macro_f1:.4f}"
)

print(
    f"Micro Precision   : "
    f"{micro_precision:.4f}"
)

print(
    f"Micro Recall      : "
    f"{micro_recall:.4f}"
)

print(
    f"Micro F1          : "
    f"{micro_f1:.4f}"
)

print(
    f"Hamming Loss      : "
    f"{hl:.4f}"
)

print(
    f"Exact Match Rate  : "
    f"{exact_match_rate:.4f}"
)

print(
    f"Exact Matches     : "
    f"{exact_matches}/{len(y_test)}"
)


# ============================================================
# SAVE METRICS
# ============================================================

with METRICS_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "model",
        "metric",
        "value",
        "test_products"
    ])


    metrics = [

        (
            "TF-IDF + Logistic Regression",
            "Macro Precision",
            macro_precision
        ),

        (
            "TF-IDF + Logistic Regression",
            "Macro Recall",
            macro_recall
        ),

        (
            "TF-IDF + Logistic Regression",
            "Macro F1",
            macro_f1
        ),

        (
            "TF-IDF + Logistic Regression",
            "Micro Precision",
            micro_precision
        ),

        (
            "TF-IDF + Logistic Regression",
            "Micro Recall",
            micro_recall
        ),

        (
            "TF-IDF + Logistic Regression",
            "Micro F1",
            micro_f1
        ),

        (
            "TF-IDF + Logistic Regression",
            "Hamming Loss",
            hl
        ),

        (
            "TF-IDF + Logistic Regression",
            "Exact Match Rate",
            exact_match_rate
        )
    ]


    for model_name, metric, value in metrics:

        writer.writerow([
            model_name,
            metric,
            f"{value:.6f}",
            len(y_test)
        ])


# ============================================================
# SAVE PREDICTIONS
# ============================================================

with PREDICTION_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "code",
        "product_name",
        "true_allergens",
        "predicted_allergens"
    ])


    for i, row in enumerate(
        test_rows
    ):

        true_labels = [
            ALLERGENS[j]
            for j, value
            in enumerate(y_test[i])
            if value == 1
        ]


        predicted_labels = [
            ALLERGENS[j]
            for j, value
            in enumerate(y_pred[i])
            if value == 1
        ]


        writer.writerow([

            row.get(
                "code",
                ""
            ),

            row.get(
                "product_name",
                ""
            ),

            ";".join(
                true_labels
            ),

            ";".join(
                predicted_labels
            )
        ])


# ============================================================
# FINAL OUTPUT
# ============================================================

print(
    "\n===== FILES SAVED ====="
)

print(
    "Metrics:"
)

print(
    METRICS_FILE
)

print(
    "\nPredictions:"
)

print(
    PREDICTION_FILE
)

print(
    "\n===== TF-IDF BASELINE COMPLETE ====="
)