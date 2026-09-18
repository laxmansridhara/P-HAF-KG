import os
import pandas as pd

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import (
    precision_recall_fscore_support
)

TRAIN_FILE = "data/processed/train.csv"
TEST_FILE = "data/processed/test.csv"

SVM_FILE = "data/processed/baseline_svm_predictions.csv"
RF_FILE = "data/processed/baseline_random_forest_predictions.csv"

OUTPUT_FILE = (
    "data/processed/per_allergen_model_analysis.csv"
)


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


def load_true_labels():

    test_df = pd.read_csv(TEST_FILE)

    labels = (
        test_df["confirmed_allergens"]
        .apply(parse_labels)
        .tolist()
    )

    return labels


def load_predictions(filename):

    df = pd.read_csv(filename)

    predictions = (
        df["predicted_allergens"]
        .fillna("")
        .apply(parse_labels)
        .tolist()
    )

    return predictions


print("=" * 70)
print("P-HAF-KG V2.1 PER-ALLERGEN ERROR ANALYSIS")
print("=" * 70)


# ------------------------------------------------------------
# TRUE LABELS
# ------------------------------------------------------------

true_labels = load_true_labels()


# ------------------------------------------------------------
# LOAD ML PREDICTIONS
# ------------------------------------------------------------

svm_predictions = load_predictions(SVM_FILE)

rf_predictions = load_predictions(RF_FILE)


# ------------------------------------------------------------
# LABEL ENCODING
# ------------------------------------------------------------

mlb = MultiLabelBinarizer()

all_labels = (
    true_labels
    + svm_predictions
    + rf_predictions
)

mlb.fit(all_labels)

classes = list(mlb.classes_)

print("\nAllergen classes:")
print(classes)


# ------------------------------------------------------------
# ENCODE
# ------------------------------------------------------------

y_true = mlb.transform(true_labels)

y_svm = mlb.transform(svm_predictions)

y_rf = mlb.transform(rf_predictions)


# ------------------------------------------------------------
# ANALYSIS FUNCTION
# ------------------------------------------------------------

def calculate_metrics(
    y_true,
    y_pred,
    model_name
):

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            average=None,
            labels=range(len(classes)),
            zero_division=0
        )
    )

    rows = []

    for i, allergen in enumerate(classes):

        rows.append({

            "model":
                model_name,

            "allergen":
                allergen,

            "precision":
                precision[i],

            "recall":
                recall[i],

            "f1":
                f1[i],

            "support":
                support[i]
        })

    return rows


# ------------------------------------------------------------
# CALCULATE SVM
# ------------------------------------------------------------

rows = []

rows.extend(
    calculate_metrics(
        y_true,
        y_svm,
        "TF-IDF + Linear SVM"
    )
)


# ------------------------------------------------------------
# CALCULATE RANDOM FOREST
# ------------------------------------------------------------

rows.extend(
    calculate_metrics(
        y_true,
        y_rf,
        "TF-IDF + Random Forest"
    )
)


# ------------------------------------------------------------
# LOAD P-HAF-KG RESULTS
# ------------------------------------------------------------

PHAF_FILE = (
    "data/processed/"
    "p_haf_kg_14_v2_1_product_evaluation.csv"
)

if os.path.exists(PHAF_FILE):

    phaf_df = pd.read_csv(PHAF_FILE)

    print(
        "\nP-HAF-KG file found:"
    )

    print(PHAF_FILE)

    print(
        "\nColumns:"
    )

    print(
        phaf_df.columns.tolist()
    )

else:

    print(
        "\nWARNING:"
    )

    print(
        "P-HAF-KG product evaluation file "
        "was not found."
    )


# ------------------------------------------------------------
# SAVE ML ANALYSIS
# ------------------------------------------------------------

result_df = pd.DataFrame(rows)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# PRINT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("PER-ALLERGEN RESULTS")
print("=" * 70)

print(
    result_df.to_string(
        index=False
    )
)

print("\nSaved:")

print(
    os.path.abspath(
        OUTPUT_FILE
    )
)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
