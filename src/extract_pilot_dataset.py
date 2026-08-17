import csv
from pathlib import Path

INPUT_FILE = Path("data/en.openfoodfacts.org.products (1).csv")
OUTPUT_FILE = Path("data/processed/pilot_dataset.csv")

SELECTED_COLUMNS = [
    "code",
    "product_name",
    "ingredients_text",
    "allergens",
    "allergens_en",
    "additives_en",
]

TARGET_ROWS = 300

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

print("Starting extraction...")
print(f"Input: {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")

with INPUT_FILE.open("r", encoding="utf-8", errors="replace", newline="") as infile:
    reader = csv.DictReader(infile, delimiter="\t")

    missing = [col for col in SELECTED_COLUMNS if col not in reader.fieldnames]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=SELECTED_COLUMNS
        )
        writer.writeheader()

        count = 0

        for row in reader:
            # Keep products that contain ingredient information
            if not row.get("ingredients_text", "").strip():
                continue

            writer.writerow({
                col: row.get(col, "")
                for col in SELECTED_COLUMNS
            })

            count += 1

            if count >= TARGET_ROWS:
                break

print(f"Done. Extracted {count} products.")
print(f"Saved to: {OUTPUT_FILE}")

