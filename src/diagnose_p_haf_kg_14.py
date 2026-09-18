import csv
from pathlib import Path
from collections import Counter


EVIDENCE_FILE = Path(
    "data/processed/p_haf_kg_evidence_14.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_14_diagnostics.csv"
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


with EVIDENCE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(
        csv.DictReader(f)
    )


diagnostics = []

confirmed_counts = Counter()
potential_counts = Counter()
special_counts = Counter()


for row in rows:

    confirmed = set(
        x.strip()
        for x in row[
            "confirmed_allergens"
        ].split(";")
        if x.strip()
    )

    potential = set(
        x.strip()
        for x in row[
            "potential_allergens"
        ].split(";")
        if x.strip()
    )

    special = set(
        x.strip()
        for x in row[
            "special_threshold_matches"
        ].split(";")
        if x.strip()
    )


    for allergen in confirmed:
        confirmed_counts[allergen] += 1

    for allergen in potential:
        potential_counts[allergen] += 1

    for match in special:
        allergen = match.split(
            " -> "
        )[-1]

        special_counts[allergen] += 1


    diagnostics.append({

        "code": row["code"],

        "product_name":
            row["product_name"],

        "confirmed":
            row["confirmed_allergens"],

        "potential":
            row["potential_allergens"],

        "direct_matches":
            row["direct_matches"],

        "precautionary_matches":
            row["precautionary_matches"],

        "special_threshold":
            row["special_threshold_matches"],

    })


# ==================================================
# SAVE DIAGNOSTICS
# ==================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "code",
        "product_name",
        "confirmed",
        "potential",
        "direct_matches",
        "precautionary_matches",
        "special_threshold",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        diagnostics
    )


# ==================================================
# REPORT
# ==================================================

print(
    "===== P-HAF-KG V2 DIAGNOSTICS ====="
)

print(
    "Products:",
    len(rows)
)


print(
    "\n===== CONFIRMED ALLERGEN COUNTS ====="
)

for allergen in ALLERGENS:

    print(
        f"{allergen:<18}: "
        f"{confirmed_counts.get(allergen, 0)}"
    )


print(
    "\n===== POTENTIAL ALLERGEN COUNTS ====="
)

for allergen in ALLERGENS:

    print(
        f"{allergen:<18}: "
        f"{potential_counts.get(allergen, 0)}"
    )


print(
    "\n===== SPECIAL THRESHOLD COUNTS ====="
)

for allergen in ALLERGENS:

    count = special_counts.get(
        allergen,
        0
    )

    if count:

        print(
            f"{allergen:<18}: {count}"
        )


print(
    "\n===== FIRST 20 EVIDENCE RECORDS ====="
)


for row in diagnostics[:20]:

    print(
        "\nProduct:",
        row["product_name"]
    )

    print(
        "Code:",
        row["code"]
    )

    print(
        "Confirmed:",
        row["confirmed"]
    )

    print(
        "Potential:",
        row["potential"]
    )

    print(
        "Direct:",
        row["direct_matches"]
    )

    print(
        "Precautionary:",
        row["precautionary_matches"]
    )

    print(
        "Sulphite threshold:",
        row["special_threshold"]
    )


print(
    "\nSaved:"
)

print(
    OUTPUT_FILE
)
