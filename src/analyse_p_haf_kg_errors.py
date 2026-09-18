import csv
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/p_haf_kg_product_evaluation.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_error_analysis.csv"
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


def parse(value):
    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    rows = list(
        csv.DictReader(f)
    )


analysis_rows = []

tp_counts = {
    allergen: 0
    for allergen in ALLERGENS
}

fp_counts = {
    allergen: 0
    for allergen in ALLERGENS
}

fn_counts = {
    allergen: 0
    for allergen in ALLERGENS
}


exact_correct = 0


for row in rows:

    truth = parse(
        row["ground_truth"]
    )

    prediction = parse(
        row["prediction"]
    )

    true_positive = (
        truth & prediction
    )

    false_positive = (
        prediction - truth
    )

    false_negative = (
        truth - prediction
    )

    for allergen in true_positive:
        tp_counts[allergen] += 1

    for allergen in false_positive:
        fp_counts[allergen] += 1

    for allergen in false_negative:
        fn_counts[allergen] += 1

    if truth == prediction:
        status = "EXACT_MATCH"
        exact_correct += 1

    elif false_positive and false_negative:
        status = "FP_AND_FN"

    elif false_positive:
        status = "FALSE_POSITIVE"

    elif false_negative:
        status = "FALSE_NEGATIVE"

    else:
        status = "OTHER"

    analysis_rows.append({
        "code": row["code"],
        "product_name": row["product_name"],
        "ground_truth": row["ground_truth"],
        "prediction": row["prediction"],
        "potential": row["potential"],
        "status": status,
        "true_positive": ";".join(
            sorted(true_positive)
        ),
        "false_positive": ";".join(
            sorted(false_positive)
        ),
        "false_negative": ";".join(
            sorted(false_negative)
        ),
    })


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
            "potential",
            "status",
            "true_positive",
            "false_positive",
            "false_negative",
        ]
    )

    writer.writeheader()
    writer.writerows(
        analysis_rows
    )


print(
    "===== P-HAF-KG ERROR ANALYSIS ====="
)

print(
    "Test products:",
    len(rows)
)

print(
    "Exact matches:",
    exact_correct
)

print(
    "Non-exact:",
    len(rows) - exact_correct
)


print(
    "\n===== ALLERGEN ERROR COUNTS ====="
)

for allergen in ALLERGENS:

    print(
        f"{allergen:<15}"
        f"TP={tp_counts[allergen]} "
        f"FP={fp_counts[allergen]} "
        f"FN={fn_counts[allergen]}"
    )


print(
    "\n===== PRODUCT-LEVEL ERRORS ====="
)

for row in analysis_rows:

    if row["status"] != "EXACT_MATCH":

        print(
            "\nCode:",
            row["code"]
        )

        print(
            "Product:",
            row["product_name"]
        )

        print(
            "Ground truth:",
            row["ground_truth"]
        )

        print(
            "Prediction:",
            row["prediction"]
        )

        print(
            "False positive:",
            row["false_positive"]
        )

        print(
            "False negative:",
            row["false_negative"]
        )


print(
    "\nSaved:"
)

print(
    OUTPUT_FILE
)
