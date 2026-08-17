import csv
import re
from pathlib import Path

INPUT_FILE = Path("data/en.openfoodfacts.org.products (1).csv")
OUTPUT_FILE = Path("data/processed/controlled_pilot_dataset.csv")

TARGET_PER_CATEGORY = 60

COLUMNS = [
    "code",
    "product_name",
    "ingredients_text",
    "allergens",
    "allergens_en",
    "additives_en",
]

# Search terms are deliberately broad.
# We will NOT use these matches as ground truth.
PATTERNS = {
    "peanut": [
        r"\bpeanut\b",
        r"\bpeanuts\b",
        r"\barachide\b",
        r"\bcacahu[eè]te\b",
    ],

    "milk": [
        r"\bmilk\b",
        r"\bwhey\b",
        r"\bcasein\b",
        r"\blactose\b",
        r"\bbutter\b",
        r"\bcream\b",
        r"\blait\b",
        r"\bmilch\b",
    ],

    "egg": [
        r"\begg\b",
        r"\beggs\b",
        r"\bœuf\b",
        r"\boeuf\b",
        r"\bovalbumin\b",
        r"\begg\s*white\b",
    ],

    "soy": [
        r"\bsoy\b",
        r"\bsoya\b",
        r"\bsoja\b",
        r"\blecithin\b",
        r"\blecithins\b",
        r"\bE322\b",
    ],

    "wheat_gluten": [
        r"\bwheat\b",
        r"\bgluten\b",
        r"\bflour\b",
        r"\bweizen\b",
        r"\bfarine\b",
        r"\bbl[eé] de\b",
    ],

    "sesame": [
        r"\bsesame\b",
        r"\bs[eé]same\b",
        r"\bsesam\b",
    ],

    "nuts": [
        r"\balmond\b",
        r"\balmond\b",
        r"\bhazelnut\b",
        r"\bwalnut\b",
        r"\bcashew\b",
        r"\bpistachio\b",
        r"\bnoix\b",
        r"\bmandel\b",
    ],

    "precautionary": [
        r"may contain",
        r"may contain traces",
        r"traces of",
        r"peut contenir",
        r"peut contenir des traces",
        r"kann spuren von",
        r"spuren von",
    ],

    "additive_codes": [
        r"\bE\d{3,4}[a-z]?\b",
    ],
}


def find_categories(text):
    text = text.lower()

    found = set()

    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.add(category)
                break

    return found


OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Separate collections for controlled sampling.
samples = {category: [] for category in PATTERNS}

seen_codes = set()

print("Scanning OpenFoodFacts file...")
print("This may take some time because the source file is 12 GB.")

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as infile:

    reader = csv.DictReader(infile, delimiter="\t")

    for row in reader:

        code = row.get("code", "").strip()
        ingredients = row.get("ingredients_text", "").strip()

        if not code or not ingredients:
            continue

        if code in seen_codes:
            continue

        text = " ".join([
            row.get("product_name", ""),
            row.get("ingredients_text", ""),
            row.get("allergens", ""),
            row.get("allergens_en", ""),
            row.get("additives_en", ""),
        ])

        categories = find_categories(text)

        for category in categories:

            if len(samples[category]) < TARGET_PER_CATEGORY:

                samples[category].append({
                    column: row.get(column, "")
                    for column in COLUMNS
                })

        seen_codes.add(code)

        # Stop once every category has enough examples.
        if all(
            len(samples[category]) >= TARGET_PER_CATEGORY
            for category in samples
        ):
            break


# Combine samples while removing duplicate products.
final_rows = []
final_codes = set()

for category_rows in samples.values():

    for row in category_rows:

        code = row["code"]

        if code not in final_codes:
            final_rows.append(row)
            final_codes.add(code)


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
    writer.writerows(final_rows)


print("\n===== CONTROLLED PILOT CREATED =====")
print(f"Products collected: {len(final_rows)}")
print(f"Output: {OUTPUT_FILE}")

print("\nCategory counts:")

for category, rows in samples.items():
    print(f"{category}: {len(rows)}")
