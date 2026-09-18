import csv
from pathlib import Path

TEST_FILE = Path(
    "data/processed/test.csv"
)

PREDICTION_FILE = Path(
    "data/processed/baseline_keyword_predictions.csv"
)

OUTPUT_FILE = Path(
    "data/processed/baseline_keyword_metrics.csv"
)

PRODUCT_OUTPUT_FILE = Path(
    "data/processed/baseline_keyword_product_evaluation.csv"
)

ALLERGENS = [
    "celery",
    "wheat_gluten",
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
    "sulphites",
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
# LOAD BASELINE PREDICTIONS
# ============================================================

with PREDICTION_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    prediction_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# MATCH BY PRODUCT CODE
# ============================================================

prediction_by_code = {
    row["code"]: row
    for row in prediction_rows
}


# ============================================================
# CONFUSION COUNTS
# ============================================================

counts = {
    allergen: {
        "TP": 0,
        "FP": 0,
        "FN": 0,
    }
    for allergen in ALLERGENS
}


product_results = []


# ============================================================
# EVALUATE
# ============================================================

for test_row in test_rows:

    code = test_row["code"]

    prediction_row = prediction_by_code.get(
        code,
        {}
    )

    ground_truth = parse_allergens(
        test_row["confirmed_allergens"]
    )

    prediction = parse_allergens(
        prediction_row.get(
            "predicted_allergens",
            ""
        )
    )

    tp = sorted(
        ground_truth & prediction
    )

    fp = sorted(
        prediction - ground_truth
    )

    fn = sorted(
        ground_truth - prediction
    )

    for allergen in ALLERGENS:

        if (
            allergen in ground_truth
            and allergen in prediction
        ):
            counts[allergen]["TP"] += 1

        elif (
            allergen not in ground_truth
            and allergen in prediction
        ):
            counts[allergen]["FP"] += 1

        elif (
            allergen in ground_truth
            and allergen not in prediction
        ):
            counts[allergen]["FN"] += 1

    product_results.append({

        "code": code,

        "product_name":
            test_row["product_name"],

        "ground_truth":
            ";".join(
                sorted(ground_truth)
            ),

        "prediction":
            ";".join(
                sorted(prediction)
            ),

        "true_positive":
            ";".join(tp),

        "false_positive":
            ";".join(fp),

        "false_negative":
            ";".join(fn),

        "exact_match":
            str(
                ground_truth == prediction
            ),
    })


# ============================================================
# METRICS
# ============================================================

metrics = []

total_tp = 0
total_fp = 0
total_fn = 0

macro_precision = 0.0
macro_recall = 0.0
macro_f1 = 0.0

for allergen in ALLERGENS:

    tp = counts[allergen]["TP"]
    fp = counts[allergen]["FP"]
    fn = counts[allergen]["FN"]

    total_tp += tp
    total_fp += fp
    total_fn += fn

    if tp + fp > 0:
        precision = tp / (tp + fp)
    else:
        precision = 0.0

    if tp + fn > 0:
        recall = tp / (tp + fn)
    else:
        recall = 0.0

    if precision + recall > 0:
        f1 = (
            2 * precision * recall
            / (precision + recall)
        )
    else:
        f1 = 0.0

    macro_precision += precision
    macro_recall += recall
    macro_f1 += f1

    metrics.append({

        "allergen":
            allergen,

        "precision":
            f"{precision:.4f}",

        "recall":
            f"{recall:.4f}",

        "f1":
            f"{f1:.4f}",

        "TP":
            tp,

        "FP":
            fp,

        "FN":
            fn,
    })


# ============================================================
# OVERALL METRICS
# ============================================================

n = len(ALLERGENS)

macro_precision /= n
macro_recall /= n
macro_f1 /= n


if total_tp + total_fp > 0:
    micro_precision = (
        total_tp
        / (total_tp + total_fp)
    )
else:
    micro_precision = 0.0


if total_tp + total_fn > 0:
    micro_recall = (
        total_tp
        / (total_tp + total_fn)
    )
else:
    micro_recall = 0.0


if micro_precision + micro_recall > 0:
    micro_f1 = (
        2
        * micro_precision
        * micro_recall
        / (micro_precision + micro_recall)
    )
else:
    micro_f1 = 0.0


# ============================================================
# HAMMING LOSS
# ============================================================

total_errors = 0
total_labels = (
    len(test_rows)
    * len(ALLERGENS)
)

for row in product_results:

    total_errors += len(
        parse_allergens(
            row["false_positive"]
        )
    )

    total_errors += len(
        parse_allergens(
            row["false_negative"]
        )
    )


hamming_loss = (
    total_errors
    / total_labels
)


# ============================================================
# EXACT MATCH
# ============================================================

exact_matches = sum(
    1
    for row in product_results
    if row["exact_match"] == "True"
)

exact_match_rate = (
    exact_matches / len(test_rows)
    if test_rows
    else 0.0
)


# ============================================================
# PRINT RESULTS
# ============================================================

print(
    "===== KEYWORD BASELINE EVALUATION ====="
)

print(
    "Test products:",
    len(test_rows)
)

print(
    "\n===== PER-ALLERGEN RESULTS ====="
)

for metric in metrics:

    print(
        f"{metric['allergen']:<18}"
        f" Precision={metric['precision']}"
        f" Recall={metric['recall']}"
        f" F1={metric['f1']}"
        f" TP={metric['TP']}"
        f" FP={metric['FP']}"
        f" FN={metric['FN']}"
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
    f"Micro Precision: {micro_precision:.4f}"
)

print(
    f"Micro Recall:    {micro_recall:.4f}"
)

print(
    f"Micro F1:        {micro_f1:.4f}"
)

print(
    f"Hamming Loss:   {hamming_loss:.4f}"
)

print(
    f"Exact Matches:   {exact_matches}"
)

print(
    f"Exact Match Rate: "
    f"{exact_match_rate:.4f}"
)


# ============================================================
# SAVE METRICS
# ============================================================

overall_rows = [

    {
        "metric": "macro_precision",
        "value": f"{macro_precision:.4f}",
    },

    {
        "metric": "macro_recall",
        "value": f"{macro_recall:.4f}",
    },

    {
        "metric": "macro_f1",
        "value": f"{macro_f1:.4f}",
    },

    {
        "metric": "micro_precision",
        "value": f"{micro_precision:.4f}",
    },

    {
        "metric": "micro_recall",
        "value": f"{micro_recall:.4f}",
    },

    {
        "metric": "micro_f1",
        "value": f"{micro_f1:.4f}",
    },

    {
        "metric": "hamming_loss",
        "value": f"{hamming_loss:.4f}",
    },

    {
        "metric": "exact_matches",
        "value": exact_matches,
    },

    {
        "metric": "exact_match_rate",
        "value": f"{exact_match_rate:.4f}",
    },
]


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "metric",
            "value"
        ]
    )

    writer.writeheader()

    writer.writerows(
        overall_rows
    )


# ============================================================
# SAVE PRODUCT EVALUATION
# ============================================================

with PRODUCT_OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "code",
        "product_name",
        "ground_truth",
        "prediction",
        "true_positive",
        "false_positive",
        "false_negative",
        "exact_match",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        product_results
    )


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)

print(
    "Product-level evaluation saved to:"
)

print(
    PRODUCT_OUTPUT_FILE
)
