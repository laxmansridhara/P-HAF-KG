import csv
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/final_annotation_dataset.csv"
)

OUTPUT_FILE = Path(
    "data/processed/annotation_batch_01.csv"
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
}

TARGET = 10

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:
    rows = list(csv.DictReader(f))

selected = []
selected_codes = set()

for category, keywords in KEYWORDS.items():

    count = 0

    for row in rows:

        if count >= TARGET:
            break

        text = " ".join([
            row.get("product_name", ""),
            row.get("ingredients_text", ""),
            row.get("allergens", ""),
            row.get("allergens_en", ""),
        ]).lower()

        if any(
            keyword.lower() in text
            for keyword in keywords
        ):

            code = row.get("code", "")

            if code not in selected_codes:

                selected.append(row)
                selected_codes.add(code)
                count += 1

print("Selected products:", len(selected))

fields = [
    "code",
    "product_name",
    "ingredients_text",
    "allergens",
    "allergens_en",
    "additives_en",
    "candidate_category",
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

    for row in selected:

        text = " ".join([
            row.get("product_name", ""),
            row.get("ingredients_text", ""),
        ]).lower()

        categories = []

        for category, keywords in KEYWORDS.items():

            if any(
                keyword.lower() in text
                for keyword in keywords
            ):
                categories.append(category)

        writer.writerow({
            "code": row.get("code", ""),
            "product_name": row.get("product_name", ""),
            "ingredients_text": row.get("ingredients_text", ""),
            "allergens": row.get("allergens", ""),
            "allergens_en": row.get("allergens_en", ""),
            "additives_en": row.get("additives_en", ""),
            "candidate_category": ";".join(categories),
            "confirmed_allergens": "",
            "potential_allergens": "",
            "evidence_level": "",
            "evidence_text": "",
            "is_food": "",
            "review_status": "PENDING",
        })

print("Created:", OUTPUT_FILE)
