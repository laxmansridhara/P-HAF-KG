import csv
from pathlib import Path

FILE = Path(
    "data/processed/final_annotation_dataset.csv"
)

KEYWORDS = {
    "peanut": ["peanut", "peanuts", "arachide", "cacahuete"],
    "milk": ["milk", "lait", "milch", "whey", "casein", "lactose"],
    "egg": ["egg", "eggs", "œuf", "oeuf"],
    "soy": ["soy", "soya", "soja", "lecithin", "E322"],
    "wheat_gluten": ["wheat", "gluten", "flour", "weizen", "farine"],
    "sesame": ["sesame", "sésame", "sesam"],
    "tree_nut": [
        "almond",
        "hazelnut",
        "walnut",
        "cashew",
        "pistachio",
        "mandel",
        "noix",
    ],
    "precautionary": [
        "may contain",
        "traces of",
        "peut contenir",
        "kann spuren",
        "spuren von",
    ],
}

with FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


print("Total products:", len(rows))
print("\n===== CANDIDATE COVERAGE =====")

for category, words in KEYWORDS.items():

    count = 0

    for row in rows:

        text = " ".join([
            row.get("product_name", ""),
            row.get("ingredients_text", ""),
            row.get("allergens", ""),
            row.get("allergens_en", ""),
        ]).lower()

        if any(word.lower() in text for word in words):
            count += 1

    print(f"{category:18}: {count}")
