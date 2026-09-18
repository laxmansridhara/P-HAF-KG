import csv
from pathlib import Path
from collections import Counter

FILE = Path(
    "data/processed/ground_truth_batch_01.csv"
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

with FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:
    rows = list(csv.DictReader(f))


def parse(value):
    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


print("\n===== GROUND TRUTH QUALITY CHECK =====")

print("Total rows:", len(rows))

status_counts = Counter(
    row["review_status"]
    for row in rows
)

evidence_counts = Counter(
    row["evidence_level"]
    for row in rows
)

print("\nReview status:")
for key, value in status_counts.items():
    print(f"{key:12}: {value}")

print("\nEvidence level:")
for key, value in evidence_counts.items():
    print(f"{key:12}: {value}")


print("\n===== CONFIRMED ALLERGEN COUNTS =====")

for allergen in ALLERGENS:

    count = sum(
        allergen in parse(row["confirmed_allergens"])
        for row in rows
        if row["review_status"] == "KEEP"
    )

    print(f"{allergen:15}: {count}")


print("\n===== POTENTIAL ALLERGEN COUNTS =====")

for allergen in ALLERGENS:

    count = sum(
        allergen in parse(row["potential_allergens"])
        for row in rows
        if row["review_status"] == "KEEP"
    )

    print(f"{allergen:15}: {count}")


print("\n===== EXCLUDED PRODUCTS =====")

for i, row in enumerate(rows, 1):

    if row["review_status"] == "EXCLUDE":

        print(
            f"{i:2}. "
            f"{row['product_name']} "
            f"| {row['evidence_level']}"
        )


print("\n===== MULTI-ALLERGEN PRODUCTS =====")

for i, row in enumerate(rows, 1):

    labels = parse(row["confirmed_allergens"])

    if (
        row["review_status"] == "KEEP"
        and len(labels) >= 3
    ):

        print(
            f"{i:2}. "
            f"{row['product_name']} "
            f"-> {', '.join(sorted(labels))}"
        )
