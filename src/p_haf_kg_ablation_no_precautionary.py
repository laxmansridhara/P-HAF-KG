import csv
from pathlib import Path

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
)


TEST_FILE = Path(
    "data/processed/test.csv"
)

EVIDENCE_FILE = Path(
    "data/processed/p_haf_kg_evidence.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_ablation_no_precautionary.csv"
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


def parse_allergens(value):
    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


# ==================================================
# LOAD TEST DATA
# ==================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    test_rows = list(
        csv.DictReader(f)
    )


# ==================================================
# LOAD P-HAF-KG EVIDENCE
# ==================================================

with EVIDENCE_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    evidence_rows = list(
        csv.DictReader(f)
    )


evidence_by_code = {
    row["code"]: row
    for row in evidence_rows
}


# ==================================================
# BUILD ABLATION PREDICTIONS
# ==================================================

y_true = []
y_pred = []

prediction_rows = []


for row in test_rows:

    code = row["code"]

    if code not in evidence_by_code:
        raise ValueError(
            f"Missing evidence for product: {code}"
        )

    evidence = evidence_by_code[code]

    # IMPORTANT:
    # Only direct/confirmed allergens are used.
    #
    # potential_allergens are deliberately ignored.
    #
    # This tests the contribution of the
    # precautionary evidence layer.

    predicted = parse_allergens(
        evidence["confirmed_allergens"]
    )

    actual = parse_allergens(
        row["confirmed_allergens"]
    )

    true_vector = [
        1 if allergen in actual else 0
        for allergen in ALLERGENS
    ]

    pred_vector = [
        1 if allergen in predicted else 0
        for allergen in ALLERGENS
    ]

    y_true.append(true_vector)
    y_pred.append(pred_vector)

    prediction_rows.append({
        "code": code,
        "product_name": row["product_name"],
        "ground_truth": ";".join(
            sorted(actual)
        ),
        "prediction": ";".join(
            sorted(predicted)
        ),
    })


# ==================================================
# METRICS
# ==================================================

macro_precision = precision_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0,
)

macro_recall = recall_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0,
)

macro_f1 = f1_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0,
)

micro_f1 = f1_score(
    y_true,
    y_pred,
    average="micro",
    zero_division=0,
)

hamming = hamming_loss(
    y_true,
    y_pred,
)


per_precision = precision_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0,
)

per_recall = recall_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0,
)

per_f1 = f1_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0,
)


# ==================================================
# PRINT
# ==================================================

print(
    "===== P-HAF-KG ABLATION ====="
)

print(
    "Experiment: WITHOUT precautionary evidence"
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

    print(
        f"{allergen:<15}"
        f"Precision={per_precision[i]:.4f} "
        f"Recall={per_recall[i]:.4f} "
        f"F1={per_f1[i]:.4f}"
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
# SAVE PRODUCT PREDICTIONS
# ==================================================

with OUTPUT_FILE.open(
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
        ],
    )

    writer.writeheader()

    writer.writerows(
        prediction_rows
    )


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)
