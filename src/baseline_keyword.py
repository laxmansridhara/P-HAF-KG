import csv
from pathlib import Path

INPUT_FILE = Path("data/processed/ground_truth_30.csv")
OUTPUT_FILE = Path("data/processed/baseline_keyword_results.csv")

ALLERGEN_KEYWORDS = {
    "peanut": [
        "peanut",
        "peanuts",
        "arachide",
        "cacahuete",
        "cacahuètes",
    ],
    "milk": [
        "milk",
        "lait",
        "milch",
        "whey",
        "casein",
        "lactose",
        "butter",
        "cream",
    ],
    "egg": [
        "egg",
        "eggs",
        "œuf",
        "oeuf",
        "ovalbumin",
    ],
    "soy": [
        "soy",
        "soya",
        "soja",
        "lecithin",
        "lecithins",
    ],
    "wheat_gluten": [
        "wheat",
        "gluten",
        "flour",
        "weizen",
        "farine",
    ],
    "sesame": [
        "sesame",
        "sésame",
        "sesam",
    ],
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


def detect_allergens(text):
    text = text.lower()

    predictions = []

    for allergen, keywords in ALLERGEN_KEYWORDS.items():

        for keyword in keywords:

            if keyword.lower() in text:
                predictions.append(allergen)
                break

    return sorted(set(predictions))


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


results = []

for row in rows:

    predicted = detect_allergens(
        row["ingredients_text"]
    )

    row["predicted_allergens"] = ";".join(predicted)

    results.append(row)


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = list(results[0].keys())

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


print("Baseline 1 completed.")
print("Products analysed:", len(results))
print("Output:", OUTPUT_FILE)
