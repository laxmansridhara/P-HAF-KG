import csv
from pathlib import Path

INPUT_FILE = Path("data/processed/controlled_pilot_dataset.csv")
OUTPUT_FILE = Path("data/processed/annotation_pilot_30.csv")

COLUMNS = [
    "code",
    "product_name",
    "ingredients_text",
    "allergens",
    "allergens_en",
    "additives_en",
    "confirmed_allergens",
    "potential_allergens",
    "evidence_level",
    "evidence_text",
    "review_status",
]

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as infile:

    reader = csv.DictReader(infile)

    rows = list(reader)

# Take the first 30 unique products.
rows = rows[:30]

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as outfile:

    writer = csv.DictWriter(
        outfile,
        fieldnames=COLUMNS
    )

    writer.writeheader()

    for row in rows:
        writer.writerow({
            "code": row.get("code", ""),
            "product_name": row.get("product_name", ""),
            "ingredients_text": row.get("ingredients_text", ""),
            "allergens": row.get("allergens", ""),
            "allergens_en": row.get("allergens_en", ""),
            "additives_en": row.get("additives_en", ""),
            "confirmed_allergens": "",
            "potential_allergens": "",
            "evidence_level": "",
            "evidence_text": "",
            "review_status": "PENDING",
        })

print(f"Created: {OUTPUT_FILE}")
print(f"Products: {len(rows)}")
