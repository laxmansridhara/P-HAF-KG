import csv
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/controlled_pilot_dataset.csv"
)

OUTPUT_FILE = Path(
    "data/processed/final_annotation_dataset.csv"
)

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))

fields = [
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
    "is_food",
    "review_status",
]

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
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
            "is_food": "",
            "review_status": "PENDING",
        })

print("Final annotation template created.")
print("Products:", len(rows))
print("Output:", OUTPUT_FILE)
