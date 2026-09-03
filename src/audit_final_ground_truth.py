import csv
from pathlib import Path
from collections import Counter

FILE = Path("data/processed/ground_truth_final.csv")

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


with FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:
    rows = list(csv.DictReader(f))


print("\n===== FINAL DATASET AUDIT =====")

print("Total products:", len(rows))

status = Counter(row["review_status"] for row in rows)
evidence = Counter(row["evidence_level"] for row in rows)

print("\nReview status:")
for key, value in status.items():
    print(f"{key:15}: {value}")

print("\nEvidence level:")
for key, value in evidence.items():
    print(f"{key:15}: {value}")


keep_rows = [
    row
    for row in rows
    if row["review_status"] == "KEEP"
]


print("\nKEEP products:", len(keep_rows))


print("\n===== CONFIRMED ALLERGENS =====")

for allergen in ALLERGENS:

    count = sum(
        allergen in parse(row["confirmed_allergens"])
        for row in keep_rows
    )

    print(f"{allergen:15}: {count}")


print("\n===== POTENTIAL ALLERGENS =====")

for allergen in ALLERGENS:

    count = sum(
        allergen in parse(row["potential_allergens"])
        for row in keep_rows
    )

    print(f"{allergen:15}: {count}")


print("\n===== PRODUCTS WITH NO CONFIRMED TARGET ALLERGEN =====")

negative_count = 0

for row in keep_rows:

    labels = parse(row["confirmed_allergens"])

    if not labels:
        negative_count += 1

print("Negative products:", negative_count)


print("\n===== MULTI-ALLERGEN DISTRIBUTION =====")

multi_counts = Counter()

for row in keep_rows:

    labels = parse(row["confirmed_allergens"])

    if len(labels) == 0:
        category = "0"
    elif len(labels) == 1:
        category = "1"
    elif len(labels) == 2:
        category = "2"
    elif len(labels) == 3:
        category = "3"
    else:
        category = "4+"

    multi_counts[category] += 1


for key in ["0", "1", "2", "3", "4+"]:
    print(f"{key:5}: {multi_counts[key]}")


print("\n===== DATA QUALITY CHECKS =====")

missing_ingredients = sum(
    not row["ingredients_text"].strip()
    for row in rows
)

missing_codes = sum(
    not row["code"].strip()
    for row in rows
)

print("Missing product codes:", missing_codes)
print("Missing ingredient text:", missing_ingredients)


print("\n===== READY FOR EXPERIMENT? =====")

if len(keep_rows) >= 100:
    print("YES - sufficient products for pilot evaluation.")
else:
    print("NO - dataset needs more products.")
