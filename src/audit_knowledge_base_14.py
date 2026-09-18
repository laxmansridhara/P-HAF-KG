import csv
from pathlib import Path
from collections import Counter


FILE = Path(
    "data/processed/ingredient_allergen_knowledge_14.csv"
)


EXPECTED = {
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
}


with FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(
        csv.DictReader(f)
    )


print(
    "===== P-HAF-KG V2 KNOWLEDGE BASE AUDIT ====="
)

print(
    "Total relationships:",
    len(rows)
)


# ==================================================
# FIELD CHECK
# ==================================================

required_fields = {
    "ingredient",
    "allergen",
    "evidence_type",
    "confidence",
    "language",
}


actual_fields = set(
    rows[0].keys()
) if rows else set()


missing_fields = (
    required_fields
    - actual_fields
)


print(
    "\nMissing fields:",
    sorted(missing_fields)
)


# ==================================================
# ALLERGEN CHECK
# ==================================================

observed = Counter(
    row["allergen"].strip()
    for row in rows
)


print(
    "\n===== ALLERGEN COVERAGE ====="
)


for allergen in sorted(
    EXPECTED
):

    print(
        f"{allergen:<18}: "
        f"{observed.get(allergen, 0)}"
    )


missing_allergens = (
    EXPECTED
    - set(observed.keys())
)


print(
    "\nMissing allergen categories:",
    sorted(missing_allergens)
)


# ==================================================
# INVALID ALLERGENS
# ==================================================

invalid = sorted(
    set(observed.keys())
    - EXPECTED
)


print(
    "Invalid allergen categories:",
    invalid
)


# ==================================================
# EMPTY INGREDIENTS
# ==================================================

empty_ingredients = [
    row
    for row in rows
    if not row["ingredient"].strip()
]


print(
    "\nEmpty ingredient terms:",
    len(empty_ingredients)
)


# ==================================================
# DUPLICATES
# ==================================================

keys = []

for row in rows:

    keys.append(
        (
            row["ingredient"].strip().lower(),
            row["allergen"].strip(),
            row["evidence_type"].strip(),
            row["language"].strip(),
        )
    )


duplicate_count = (
    len(keys)
    - len(set(keys))
)


print(
    "Duplicate relationships:",
    duplicate_count
)


# ==================================================
# EVIDENCE TYPES
# ==================================================

evidence_counts = Counter(
    row["evidence_type"].strip()
    for row in rows
)


print(
    "\n===== EVIDENCE TYPES ====="
)

for evidence, count in sorted(
    evidence_counts.items()
):

    print(
        f"{evidence:<20}: {count}"
    )


# ==================================================
# LANGUAGE
# ==================================================

language_counts = Counter(
    row["language"].strip()
    for row in rows
)


print(
    "\n===== LANGUAGE ====="
)

for language, count in sorted(
    language_counts.items()
):

    print(
        f"{language:<10}: {count}"
    )


# ==================================================
# CONFIDENCE
# ==================================================

bad_confidence = []

for row in rows:

    try:

        value = float(
            row["confidence"]
        )

        if not 0 <= value <= 1:

            bad_confidence.append(
                row
            )

    except ValueError:

        bad_confidence.append(
            row
        )


print(
    "\nInvalid confidence values:",
    len(bad_confidence)
)


# ==================================================
# FINAL CHECK
# ==================================================

passed = True


if missing_fields:
    passed = False

if missing_allergens:
    passed = False

if invalid:
    passed = False

if empty_ingredients:
    passed = False

if duplicate_count:
    passed = False

if bad_confidence:
    passed = False


print(
    "\n===== FINAL CHECK ====="
)


if passed:

    print(
        "PASS - knowledge base is structurally valid."
    )

else:

    print(
        "REVIEW REQUIRED - audit found issues."
    )
