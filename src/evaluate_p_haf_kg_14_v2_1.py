import csv
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

PREDICTION_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2_1.csv"
)

METRICS_FILE = Path(
    "data/processed/p_haf_kg_14_v2_1_metrics.csv"
)

PRODUCT_FILE = Path(
    "data/processed/p_haf_kg_14_v2_1_product_evaluation.csv"
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


def parse_labels(value):
    if not value:
        return set()

    return set(
        x.strip()
        for x in value.split(";")
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

    test_rows = list(
        csv.DictReader(f)
    )


ground_truth = {}

for row in test_rows:

    ground_truth[
        row["code"]
    ] = parse_labels(
        row["confirmed_allergens"]
    )


# ============================================================
# LOAD PREDICTIONS
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
# METRIC STORAGE
# ============================================================

metrics = []

total_tp = 0
total_fp = 0
total_fn = 0

total_label_errors = 0
total_labels = 0


# ============================================================
# PRODUCT EVALUATION
# ============================================================

product_results = []


for row in prediction_rows:

    code = row["code"]

    truth = ground_truth.get(
        code,
        set()
    )

    prediction = parse_labels(
        row["confirmed_allergens"]
    )

    potential = parse_labels(
        row["potential_allergens"]
    )

    tp = truth & prediction

    fp = prediction - truth

    fn = truth - prediction

    exact = (
        truth == prediction
    )


    product_results.append({

        "code":
            code,

        "product_name":
            row["product_name"],

        "ground_truth":
            ";".join(
                sorted(truth)
            ),

        "prediction":
            ";".join(
                sorted(prediction)
            ),

        "potential":
            ";".join(
                sorted(potential)
            ),

        "true_positive":
            ";".join(
                sorted(tp)
            ),

        "false_positive":
            ";".join(
                sorted(fp)
            ),

        "false_negative":
            ";".join(
                sorted(fn)
            ),

        "exact_match":
            str(exact),

    })


# ============================================================
# PER-ALLERGEN METRICS
# ============================================================

for allergen in ALLERGENS:

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for row in prediction_rows:

        code = row["code"]

        truth = ground_truth.get(
            code,
            set()
        )

        prediction = parse_labels(
            row["confirmed_allergens"]
        )

        if allergen in truth and allergen in prediction:
            tp += 1

        elif allergen not in truth and allergen in prediction:
            fp += 1

        elif allergen in truth and allergen not in prediction:
            fn += 1

        else:
            tn += 1


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
            2 * precision * recall
            / (precision + recall)
        )
    else:
        f1 = 0.0


    metrics.append({

        "allergen":
            allergen,

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

        "tn":
            tn,

    })


    total_tp += tp
    total_fp += fp
    total_fn += fn

    total_label_errors += (
        fp + fn
    )

    total_labels += (
        tp + fp + fn + tn
    )


# ============================================================
# MACRO METRICS
# ============================================================

macro_precision = (
    sum(
        x["precision"]
        for x in metrics
    )
    / len(metrics)
)


macro_recall = (
    sum(
        x["recall"]
        for x in metrics
    )
    / len(metrics)
)


macro_f1 = (
    sum(
        x["f1"]
        for x in metrics
    )
    / len(metrics)
)


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

hamming_loss = (
    total_label_errors
    / total_labels
)


# ============================================================
# EXACT MATCH COUNT
# ============================================================

exact_matches = sum(
    1
    for row in product_results
    if row["exact_match"] == "True"
)


# ============================================================
# PRINT RESULTS
# ============================================================

print(
    "===== P-HAF-KG V2.1 EVALUATION ====="
)

print(
    "Test products:",
    len(prediction_rows)
)

print(
    "\n===== PER-ALLERGEN RESULTS ====="
)

for x in metrics:

    print(
        f"{x['allergen']:<18}"
        f"Precision={x['precision']:.4f} "
        f"Recall={x['recall']:.4f} "
        f"F1={x['f1']:.4f} "
        f"TP={x['tp']} "
        f"FP={x['fp']} "
        f"FN={x['fn']}"
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
    f"Exact Matches:   {exact_matches}"
)

print(
    f"Exact Match Rate: "
    f"{exact_matches / len(prediction_rows):.4f}"
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
        "exact_matches",
        exact_matches
    ])

    writer.writerow([
        "exact_match_rate",
        exact_matches / len(prediction_rows)
    ])


# ============================================================
# SAVE PRODUCT EVALUATION
# ============================================================

with PRODUCT_FILE.open(
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
    METRICS_FILE
)

print(
    "Product-level evaluation saved to:"
)

print(
    PRODUCT_FILE
)
