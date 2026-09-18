import csv
import re
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_normalized.csv"
)


def normalize_text(text):
    """Normalize ingredient text for matching."""

    text = text.lower()

    # Replace accented characters approximately
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

    # Normalize punctuation
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ==============================================
# LOAD KNOWLEDGE BASE
# ==============================================

with KNOWLEDGE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    knowledge_rows = list(
        csv.DictReader(f)
    )


# Sort longest terms first.
# This prevents shorter terms such as
# "milk" from matching before
# "milk powder".

knowledge_rows.sort(
    key=lambda row: len(
        row["ingredient"]
    ),
    reverse=True
)


# ==============================================
# LOAD TEST DATA
# ==============================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = list(
        csv.DictReader(f)
    )


results = []


# ==============================================
# MATCH INGREDIENT KNOWLEDGE
# ==============================================

for row in test_rows:

    original_text = row[
        "ingredients_text"
    ]

    normalized_text = normalize_text(
        original_text
    )

    matches = []

    for knowledge in knowledge_rows:

        ingredient = normalize_text(
            knowledge["ingredient"]
        )

        if ingredient in normalized_text:

            matches.append({
                "ingredient": knowledge[
                    "ingredient"
                ],
                "allergen": knowledge[
                    "allergen"
                ],
                "evidence_type": knowledge[
                    "evidence_type"
                ],
                "confidence": knowledge[
                    "confidence"
                ]
            })


    # Remove duplicate relationships
    unique_matches = []

    seen = set()

    for match in matches:

        key = (
            match["ingredient"],
            match["allergen"]
        )

        if key not in seen:

            seen.add(key)

            unique_matches.append(
                match
            )


    predicted_allergens = sorted(
        set(
            match["allergen"]
            for match in unique_matches
        )
    )


    matched_ingredients = sorted(
        set(
            match["ingredient"]
            for match in unique_matches
        )
    )


    results.append({

        "code": row["code"],

        "product_name": row[
            "product_name"
        ],

        "ingredients_text": original_text,

        "matched_ingredients":
            ";".join(
                matched_ingredients
            ),

        "predicted_allergens":
            ";".join(
                predicted_allergens
            ),

        "match_count":
            str(len(unique_matches)),

    })


# ==============================================
# SAVE
# ==============================================

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
            "ingredients_text",
            "matched_ingredients",
            "predicted_allergens",
            "match_count"
        ]
    )

    writer.writeheader()

    writer.writerows(
        results
    )


print(
    "===== P-HAF-KG NORMALISATION ====="
)

print(
    "Products processed:",
    len(results)
)

print(
    "Output:",
    OUTPUT_FILE
)


# ==============================================
# SHOW EXAMPLES
# ==============================================

print(
    "\n===== SAMPLE MATCHES ====="
)

for result in results[:10]:

    print(
        "\nProduct:",
        result["product_name"]
    )

    print(
        "Matched:",
        result["matched_ingredients"]
    )

    print(
        "Predicted:",
        result["predicted_allergens"]
    )
