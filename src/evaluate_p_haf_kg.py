import csv
from pathlib import Path

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
    multilabel_confusion_matrix,
)


TEST_FILE = Path(
    "data/processed/test.csv"
)

PREDICTION_FILE = Path(
    "data/processed/p_haf_kg_predictions.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_metrics.csv"
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


# ==================================================
# HELPER
# ==================================================

def parse_allergens(value):
    """
    Convert semicolon-separated allergen string
    into a set.
    """

    if not value:
        return set()

    return {
        item.strip()
        for item in value.split(";")
        if item.strip()
    }


# ==================================================
# LOAD GROUND TRUTH
# ==================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = list(
        csv.DictReader(f)
    )


# ==================================================
# LOAD PREDICTIONS
# ==================================================

with PREDICTION_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    prediction_rows = list(
        csv.DictReader(f)
    )


# ==================================================
# INDEX PREDICTIONS BY CODE
# ==================================================

prediction_by_code = {
    row["code"]: row
    for row in prediction_rows
}


# ==================================================
# BUILD LABEL MATRICES
# ==================================================

y_true = []
y_pred = []

evaluation_rows = []


for row in test_rows:

    code = row["code"]

    if code not in prediction_by_code:

        raise ValueError(
            f"Missing P-HAF-KG prediction for code: {code}"
        )


    prediction = prediction_by_code[
        code
    ]


    true_allergens = parse_allergens(
        row["confirmed_allergens"]
    )

    predicted_allergens = parse_allergens(
        prediction[
            "predicted_confirmed_allergens"
        ]
    )


    true_vector = [
        1 if allergen in true_allergens
        else 0
        for allergen in ALLERGENS
    ]


    predicted_vector = [
        1 if allergen in predicted_allergens
        else 0
        for allergen in ALLERGENS
    ]


    y_true.append(
        true_vector
    )

    y_pred.append(
        predicted_vector
    )


    evaluation_rows.append({

        "code": code,

        "product_name":
            row["product_name"],

        "ground_truth":
            ";".join(
                sorted(true_allergens)
            ),

        "prediction":
            ";".join(
                sorted(predicted_allergens)
            ),

        "potential":
            prediction[
                "predicted_potential_allergens"
            ],

    })


# ==================================================
# METRICS
# ==================================================

macro_precision = precision_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

macro_recall = recall_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

macro_f1 = f1_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

micro_f1 = f1_score(
    y_true,
    y_pred,
    average="micro",
    zero_division=0
)

hamming = hamming_loss(
    y_true,
    y_pred
)


# ==================================================
# PER-ALLERGEN METRICS
# ==================================================

per_precision = precision_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0
)

per_recall = recall_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0
)

per_f1 = f1_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0
)


# ==================================================
# CONFUSION MATRICES
# ==================================================

confusion = multilabel_confusion_matrix(
    y_true,
    y_pred
)


# ==================================================
# PRINT RESULTS
# ==================================================

print(
    "===== P-HAF-KG EVALUATION ====="
)

print(
    "Test products:",
    len(test_rows)
)

print(
    "\n===== PER-ALLERGEN RESULTS ====="
)


for i, allergen in enumerate(
    ALLERGENS
):

    tn, fp, fn, tp = (
        confusion[i].ravel()
    )

    print(
        f"{allergen:<15}"
        f"Precision={per_precision[i]:.4f} "
        f"Recall={per_recall[i]:.4f} "
        f"F1={per_f1[i]:.4f} "
        f"TP={tp} "
        f"FP={fp} "
        f"FN={fn}"
    )


print(
    "\n===== OVERALL ====="
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
    f"Micro F1:        {micro_f1:.4f}"
)

print(
    f"Hamming Loss:   {hamming:.4f}"
)


# ==================================================
# SAVE METRICS
# ==================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "allergen",
        "precision",
        "recall",
        "f1",
        "true_positive",
        "false_positive",
        "false_negative",
    ])


    for i, allergen in enumerate(
        ALLERGENS
    ):

        tn, fp, fn, tp = (
            confusion[i].ravel()
        )

        writer.writerow([
            allergen,
            per_precision[i],
            per_recall[i],
            per_f1[i],
            tp,
            fp,
            fn,
        ])


    writer.writerow([
        "MACRO",
        macro_precision,
        macro_recall,
        macro_f1,
        "",
        "",
        "",
    ])


    writer.writerow([
        "MICRO_F1",
        "",
        "",
        micro_f1,
        "",
        "",
        "",
    ])


    writer.writerow([
        "HAMMING_LOSS",
        "",
        "",
        hamming,
        "",
        "",
        "",
    ])


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)


# ==================================================
# SAVE PRODUCT-LEVEL EVALUATION
# ==================================================

PRODUCT_OUTPUT = Path(
    "data/processed/p_haf_kg_product_evaluation.csv"
)


with PRODUCT_OUTPUT.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "code",
            "product_name",
            "ground_truth",
            "prediction",
            "potential",
        ]
    )

    writer.writeheader()

    writer.writerows(
        evaluation_rows
    )


print(
    "Product-level evaluation saved to:"
)

print(
    PRODUCT_OUTPUT
)
