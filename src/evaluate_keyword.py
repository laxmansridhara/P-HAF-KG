import csv
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/baseline_keyword_results.csv"
)

OUTPUT_FILE = Path(
    "data/processed/baseline_keyword_metrics.csv"
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


def to_set(value):
    if not value:
        return set()

    return {
        item.strip()
        for item in value.split(";")
        if item.strip()
    }


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


metrics = []

for allergen in ALLERGENS:

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for row in rows:

        actual = allergen in to_set(
            row["confirmed_allergens"]
        )

        predicted = allergen in to_set(
            row["predicted_allergens"]
        )

        if actual and predicted:
            tp += 1

        elif not actual and predicted:
            fp += 1

        elif actual and not predicted:
            fn += 1

        else:
            tn += 1

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    metrics.append({
        "allergen": allergen,
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    })


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "allergen",
        "TP",
        "FP",
        "FN",
        "TN",
        "precision",
        "recall",
        "f1",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(metrics)


print("\n===== BASELINE 1 RESULTS =====")

for row in metrics:

    print(
        f"{row['allergen']:15}"
        f" Precision={row['precision']:.4f}"
        f" Recall={row['recall']:.4f}"
        f" F1={row['f1']:.4f}"
    )

print("\nSaved to:")
print(OUTPUT_FILE)
