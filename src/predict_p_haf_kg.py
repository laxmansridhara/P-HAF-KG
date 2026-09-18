import csv
from pathlib import Path


EVIDENCE_FILE = Path(
    "data/processed/p_haf_kg_evidence.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_predictions.csv"
)


# ==================================================
# LOAD EVIDENCE OUTPUT
# ==================================================

with EVIDENCE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(
        csv.DictReader(f)
    )


# ==================================================
# CREATE PREDICTIONS
# ==================================================

predictions = []

for row in rows:

    confirmed = (
        row["confirmed_allergens"]
        .strip()
    )

    potential = (
        row["potential_allergens"]
        .strip()
    )

    # Confirmed allergens are the primary
    # safety prediction.
    #
    # Potential allergens are retained
    # separately as precautionary evidence.

    predictions.append({

        "code":
            row["code"],

        "product_name":
            row["product_name"],

        "predicted_confirmed_allergens":
            confirmed,

        "predicted_potential_allergens":
            potential,

        "direct_matches":
            row["direct_matches"],

        "precautionary_matches":
            row["precautionary_matches"],

    })


# ==================================================
# SAVE
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
            "predicted_confirmed_allergens",
            "predicted_potential_allergens",
            "direct_matches",
            "precautionary_matches",
        ]
    )

    writer.writeheader()

    writer.writerows(
        predictions
    )


# ==================================================
# SUMMARY
# ==================================================

print(
    "===== P-HAF-KG PREDICTIONS ====="
)

print(
    "Products:",
    len(predictions)
)

print(
    "Output:",
    OUTPUT_FILE
)


print(
    "\n===== SAMPLE PREDICTIONS ====="
)

for row in predictions[:10]:

    print(
        "\nProduct:",
        row["product_name"]
    )

    print(
        "Confirmed:",
        row[
            "predicted_confirmed_allergens"
        ]
    )

    print(
        "Potential:",
        row[
            "predicted_potential_allergens"
        ]
    )
