import csv
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

ERROR_FILE = Path(
    "data/processed/p_haf_kg_14_v2_error_analysis.csv"
)


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


with ERROR_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    error_rows = list(
        csv.DictReader(f)
    )


print(
    "===== P-HAF-KG V2 ERROR PRODUCT INSPECTION ====="
)

print(
    "Error products:",
    len(error_rows)
)


for error in error_rows:

    code = error["code"]

    row = test_rows.get(code)

    print("\n" + "=" * 80)

    print(
        "CODE:",
        code
    )

    print(
        "PRODUCT:",
        error["product_name"]
    )

    print(
        "GROUND TRUTH:",
        error["ground_truth"]
    )

    print(
        "PREDICTION:",
        error["prediction"]
    )

    print(
        "POTENTIAL:",
        error["potential"]
    )

    print(
        "FALSE POSITIVE:",
        error["false_positive"]
    )

    print(
        "FALSE NEGATIVE:",
        error["false_negative"]
    )

    if row:

        print(
            "\nORIGINAL INGREDIENT TEXT:"
        )

        print(
            row["ingredients_text"]
        )

    else:

        print(
            "\nWARNING: product not found in test.csv"
        )


print(
    "\n" + "=" * 80
)

print(
    "Inspection complete."
)
