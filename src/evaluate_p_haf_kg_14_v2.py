import csv
from pathlib import Path
from collections import defaultdict


TEST_FILE = Path(
    "data/processed/test.csv"
)

PREDICTION_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_14_v2_metrics.csv"
)

PRODUCT_OUTPUT = Path(
    "data/processed/p_haf_kg_14_v2_product_evaluation.csv"
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


def split_labels(value):

    return set(
        x.strip()
        for x in str(value).split(";")
        if x.strip()
    )


# ============================================================
# LOAD GROUND TRUTH
# ============================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


# ============================================================
# LOAD PREDICTIONS
# ============================================================

with PREDICTION_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    prediction_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


# ============================================================
# METRIC STORAGE
# ============================================================

metrics = {}

total_tp = 0
total_fp = 0
total_fn = 0

product_results = []


# ============================================================
# PRODUCT-LEVEL EVALUATION
# ============================================================

for code, test_row in test_rows.items():

    prediction_row = prediction_rows.get(
        code
    )

    if prediction_row is None:
        continue


    ground_truth = split_labels(
        test_row[
            "confirmed_allergens"
        ]
    )

    prediction = split_labels(
        prediction_row[
            "confirmed_allergens"
        ]
    )


    potential = split_labels(
        prediction_row[
            "potential_allergens"
        ]
    )


    tp = ground_truth & prediction

    fp = prediction - ground_truth

    fn = ground_truth - prediction


    total_tp += len(tp)
    total_fp += len(fp)
    total_fn += len(fn)


    product_results.append({

        "code":
            code,

        "product_name":
            test_row[
                "product_name"
            ],

        "ground_truth":
            ";".join(
                sorted(
                    ground_truth
                )
            ),

        "prediction":
            ";".join(
                sorted(
                    prediction
                )
            ),

        "potential":
            ";".join(
                sorted(
                    potential
                )
            ),

        "true_positive":
            ";".join(
                sorted(
                    tp
                )
            ),

        "false_positive":
            ";".join(
                sorted(
                    fp
                )
            ),

        "false_negative":
            ";".join(
                sorted(
                    fn
                )
            ),

    })


# ============================================================
# PER-ALLERGEN METRICS
# ============================================================

for allergen in ALLERGENS:

    tp = 0
    fp = 0
    fn = 0

    for code, test_row in test_rows.items():

        prediction_row = prediction_rows.get(
            code
        )

        if prediction_row is None:
            continue


        truth = split_labels(
            test_row[
                "confirmed_allergens"
            ]
        )

        prediction = split_labels(
            prediction_row[
                "confirmed_allergens"
            ]
        )


        truth_positive = (
            allergen in truth
        )

        prediction_positive = (
            allergen in prediction
        )


        if truth_positive and prediction_positive:
            tp += 1

        elif not truth_positive and prediction_positive:
            fp += 1

        elif truth_positive and not prediction_positive:
            fn += 1


    if tp + fp > 0:

        precision = (
            tp / (tp + fp)
        )

    else:

        precision = 0.0


    if tp + fn > 0:

        recall = (
            tp / (tp + fn)
        )

    else:

        recall = 0.0


    if precision + recall > 0:

        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
        )

    else:

        f1 = 0.0


    metrics[allergen] = {

        "precision":
            precision,

        "recall":
            recall,

        "f1":
            f1,

        "tp":
            tp,

        "fp":
            fp,

        "fn":
            fn,

    }


# ============================================================
# MACRO METRICS
# ============================================================

macro_precision = sum(
    x["precision"]
    for x in metrics.values()
) / len(ALLERGENS)


macro_recall = sum(
    x["recall"]
    for x in metrics.values()
) / len(ALLERGENS)


macro_f1 = sum(
    x["f1"]
    for x in metrics.values()
) / len(ALLERGENS)


# ============================================================
# MICRO F1
# ============================================================

if (
    2 * total_tp
    + total_fp
    + total_fn
) > 0:

    micro_f1 = (
        2 * total_tp
        / (
            2 * total_tp
            + total_fp
            + total_fn
        )
    )

else:

    micro_f1 = 0.0


# ============================================================
# HAMMING LOSS
# ============================================================

total_products = len(
    product_results
)

total_labels = (
    total_products
    * len(ALLERGENS)
)

total_errors = (
    total_fp
    + total_fn
)


if total_labels > 0:

    hamming_loss = (
        total_errors
        / total_labels
    )

else:

    hamming_loss = 0.0


# ============================================================
# SAVE METRICS
# ============================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "metric",
        "value"
    ])

    writer.writerow([
        "macro_precision",
        macro_precision
    ])

    writer.writerow([
        "macro_recall",
        macro_recall
    ])

    writer.writerow([
        "macro_f1",
        macro_f1
    ])

    writer.writerow([
        "micro_f1",
        micro_f1
    ])

    writer.writerow([
        "hamming_loss",
        hamming_loss
    ])

    writer.writerow([
        "total_tp",
        total_tp
    ])

    writer.writerow([
        "total_fp",
        total_fp
    ])

    writer.writerow([
        "total_fn",
        total_fn
    ])


# ============================================================
# SAVE PRODUCT EVALUATION
# ============================================================

with PRODUCT_OUTPUT.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "code",
        "product_name",
        "ground_truth",
        "prediction",
        "potential",
        "true_positive",
        "false_positive",
        "false_negative",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        product_results
    )


# ============================================================
# PRINT RESULTS
# ============================================================

print(
    "===== P-HAF-KG V2 EVALUATION ====="
)

print(
    "Test products:",
    total_products
)


print(
    "\n===== PER-ALLERGEN RESULTS ====="
)


for allergen in ALLERGENS:

    m = metrics[
        allergen
    ]

    print(
        f"{allergen:<18} "
        f"Precision={m['precision']:.4f} "
        f"Recall={m['recall']:.4f} "
        f"F1={m['f1']:.4f} "
        f"TP={m['tp']} "
        f"FP={m['fp']} "
        f"FN={m['fn']}"
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
    f"Hamming Loss:   {hamming_loss:.4f}"
)


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)

print(
    "\nProduct-level evaluation saved to:"
)

print(
    PRODUCT_OUTPUT
)
