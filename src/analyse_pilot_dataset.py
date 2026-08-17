import csv
from collections import Counter

INPUT_FILE = "data/processed/pilot_dataset.csv"

rows = []

with open(INPUT_FILE, "r", encoding="utf-8", errors="replace", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        rows.append(row)

print("\n===== PILOT DATASET ANALYSIS =====")

print(f"Total products: {len(rows)}")

print("\nMissing values:")

for column in reader.fieldnames:
    missing = sum(
        1 for row in rows
        if not row.get(column, "").strip()
    )

    print(f"{column}: {missing}/{len(rows)} missing")

print("\nProducts containing allergen information:")

allergen_count = sum(
    1 for row in rows
    if row.get("allergens_en", "").strip()
)

print(f"allergens_en available: {allergen_count}/{len(rows)}")

print("\nProducts containing ingredient information:")

ingredient_count = sum(
    1 for row in rows
    if row.get("ingredients_text", "").strip()
)

print(f"ingredients_text available: {ingredient_count}/{len(rows)}")

print("\nProducts containing additive information:")

additive_count = sum(
    1 for row in rows
    if row.get("additives_en", "").strip()
)

print(f"additives_en available: {additive_count}/{len(rows)}")

print("\n===== SAMPLE PRODUCTS =====")

for i, row in enumerate(rows[:10], start=1):

    print(f"\n{i}. {row.get('product_name', '')}")

    print(
        "Ingredients:",
        row.get("ingredients_text", "")[:250]
    )

    print(
        "Allergens:",
        row.get("allergens_en", "")
    )

    print(
        "Additives:",
        row.get("additives_en", "")
    )
