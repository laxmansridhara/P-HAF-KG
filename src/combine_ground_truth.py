import csv
from pathlib import Path

BATCH1 = Path("data/processed/ground_truth_batch_01.csv")
BATCH2 = Path("data/processed/ground_truth_batch_02.csv")
OUTPUT = Path("data/processed/ground_truth_final.csv")

fields = [
    "code",
    "product_name",
    "ingredients_text",
    "candidate_category",
    "confirmed_allergens",
    "potential_allergens",
    "evidence_level",
    "is_food",
    "review_status",
]

rows = []

for file in [BATCH1, BATCH2]:

    with file.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            # Keep only the common experimental fields
            clean_row = {
                field: row.get(field, "")
                for field in fields
            }

            rows.append(clean_row)


# Check duplicate product codes
codes = [row["code"] for row in rows]

duplicates = {
    code for code in codes
    if code and codes.count(code) > 1
}

if duplicates:
    raise ValueError(
        f"Duplicate product codes found: {duplicates}"
    )


with OUTPUT.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(rows)


print("===== FINAL GROUND TRUTH =====")
print("Batch 1:", 70)
print("Batch 2:", 85)
print("Total:", len(rows))
print("Unique products:", len(set(codes)))
print("Output:", OUTPUT)
