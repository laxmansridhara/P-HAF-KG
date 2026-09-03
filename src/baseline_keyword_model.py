import csv
import re
from pathlib import Path

TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge_14.csv"
)

OUTPUT_FILE = Path(
    "data/processed/baseline_keyword_predictions.csv"
)


# ============================================================
# TEXT NORMALISATION
# ============================================================

def normalize_text(text):
    text = str(text).lower()

    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ä": "a",
        "á": "a",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# LOAD KNOWLEDGE TERMS
# ============================================================

with KNOWLEDGE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    knowledge_rows = list(
        csv.DictReader(f)
    )


# ============================================================
# PREPARE UNIQUE KEYWORD TERMS
#
# IMPORTANT:
# This baseline intentionally does NOT use:
# - evidence type
# - precautionary evidence
# - sulphite threshold logic
# - P-HAF-KG decision rules
#
# It simply asks:
# "Does an allergen-associated ingredient term occur
#  in the ingredient text?"
# ============================================================

keyword_terms = []

seen = set()

for row in knowledge_rows:

    ingredient = normalize_text(
        row["ingredient"]
    )

    allergen = row["allergen"].strip()

    if not ingredient:
        continue

    key = (
        ingredient,
        allergen
    )

    if key in seen:
        continue

    seen.add(key)

    keyword_terms.append({
        "ingredient": ingredient,
        "allergen": allergen
    })


# Longest terms first
keyword_terms.sort(
    key=lambda x: len(
        x["ingredient"]
    ),
    reverse=True
)


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
# PREDICTION
# ============================================================

results = []

for row in test_rows:

    original_text = row[
        "ingredients_text"
    ]

    text = normalize_text(
        original_text
    )

    predicted_allergens = set()
    matched_terms = set()

    for item in keyword_terms:

        ingredient = item[
            "ingredient"
        ]

        allergen = item[
            "allergen"
        ]

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(ingredient)
            + r"(?![a-z0-9])"
        )

        if re.search(
            pattern,
            text
        ):

            predicted_allergens.add(
                allergen
            )

            matched_terms.add(
                f"{ingredient} -> {allergen}"
            )

    results.append({

        "code":
            row["code"],

        "product_name":
            row["product_name"],

        "ground_truth":
            row["confirmed_allergens"],

        "predicted_allergens":
            ";".join(
                sorted(
                    predicted_allergens
                )
            ),

        "matched_terms":
            ";".join(
                sorted(
                    matched_terms
                )
            ),

    })


# ============================================================
# SAVE
# ============================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "code",
        "product_name",
        "ground_truth",
        "predicted_allergens",
        "matched_terms"
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        results
    )


# ============================================================
# SUMMARY
# ============================================================

print(
    "===== KEYWORD BASELINE ====="
)

print(
    "Test products:",
    len(test_rows)
)

print(
    "Unique keyword relationships:",
    len(keyword_terms)
)

print(
    "Output:",
    OUTPUT_FILE
)

print(
    "\n===== SAMPLE PREDICTIONS ====="
)

for result in results[:10]:

    print(
        "\nProduct:",
        result["product_name"]
    )

    print(
        "Ground truth:",
        result["ground_truth"]
    )

    print(
        "Prediction:",
        result["predicted_allergens"]
    )

    print(
        "Matched:",
        result["matched_terms"]
    )
