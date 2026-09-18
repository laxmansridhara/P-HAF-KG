import csv
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

PREDICTION_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2_1.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_14_v2_1_error_analysis.csv"
)


def parse_labels(value):
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

    test_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


# ============================================================
# LOAD V2.1 PREDICTIONS
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


errors = []


# ============================================================
# ANALYSE PRODUCTS
# ============================================================

for row in prediction_rows:

    code = row["code"]

    truth_row = test_rows.get(code)

    if truth_row is None:
        continue

    ground_truth = parse_labels(
        truth_row["confirmed_allergens"]
    )

    prediction = parse_labels(
        row["confirmed_allergens"]
    )

    potential = parse_labels(
        row["potential_allergens"]
    )

    if ground_truth == prediction:
        continue

    true_positive = (
        ground_truth & prediction
    )

    false_positive = (
        prediction - ground_truth
    )

    false_negative = (
        ground_truth - prediction
    )

    errors.append({

        "code": code,

        "product_name":
            truth_row["product_name"],

        "ground_truth":
            ";".join(
                sorted(ground_truth)
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
                sorted(true_positive)
            ),

        "false_positive":
            ";".join(
                sorted(false_positive)
            ),

        "false_negative":
            ";".join(
                sorted(false_negative)
            ),

        "ingredients_text":
            truth_row["ingredients_text"],

        "direct_matches":
            row["direct_matches"],

        "precautionary_matches":
            row["precautionary_matches"],

        "sulphite_threshold_evidence":
            row.get(
                "sulphite_threshold_evidence",
                ""
            ),

    })


# ============================================================
# PRINT SUMMARY
# ============================================================

print(
    "===== P-HAF-KG V2.1 ERROR ANALYSIS ====="
)

print(
    "Test products:",
    len(prediction_rows)
)

print(
    "Exact matches:",
    len(prediction_rows) - len(errors)
)

print(
    "Non-exact:",
    len(errors)
)


# ============================================================
# PRINT ERRORS
# ============================================================

print(
    "\n===== REMAINING ERRORS ====="
)


for error in errors:

    print(
        "\n" + "=" * 80
    )

    print(
        "Code:",
        error["code"]
    )

    print(
        "Product:",
        error["product_name"]
    )

    print(
        "Ground truth:",
        error["ground_truth"]
    )

    print(
        "Prediction:",
        error["prediction"]
    )

    print(
        "Potential:",
        error["potential"]
    )

    print(
        "True positive:",
        error["true_positive"]
    )

    print(
        "False positive:",
        error["false_positive"]
    )

    print(
        "False negative:",
        error["false_negative"]
    )

    print(
        "\nORIGINAL INGREDIENT TEXT:"
    )

    print(
        error["ingredients_text"]
    )

    print(
        "\nDIRECT MATCHES:"
    )

    print(
        error["direct_matches"]
    )

    print(
        "\nPRECAUTIONARY MATCHES:"
    )

    print(
        error["precautionary_matches"]
    )

    print(
        "\nSULPHITE THRESHOLD:"
    )

    print(
        error["sulphite_threshold_evidence"]
    )


# ============================================================
# SAVE
# ============================================================

fieldnames = [
    "code",
    "product_name",
    "ground_truth",
    "prediction",
    "potential",
    "true_positive",
    "false_positive",
    "false_negative",
    "ingredients_text",
    "direct_matches",
    "precautionary_matches",
    "sulphite_threshold_evidence",
]


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        errors
    )


print(
    "\nSaved:"
)

print(
    OUTPUT_FILE
)
