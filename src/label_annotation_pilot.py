import csv
from pathlib import Path

INPUT_FILE = Path("data/processed/annotation_pilot_30.csv")
OUTPUT_FILE = Path("data/processed/ground_truth_30.csv")

labels = {
    "00000000013": ("", "", "UNCERTAIN"),
    "00000020": ("peanut;tree_nut", "", "DIRECT"),
    "00000137": ("peanut", "", "DIRECT"),
    "00000231": ("soy;milk", "", "DIRECT"),
    "00000259": ("milk;soy;peanut", "tree_nut;wheat_gluten", "DIRECT"),
    "00000321": ("tree_nut", "", "DIRECT"),
    "00000452": ("wheat_gluten;milk;egg;soy;tree_nut", "peanut;lupin;sesame", "DIRECT"),
    "00000833": ("", "", "UNCERTAIN"),
    "0000128884525": ("peanut", "tree_nut", "DIRECT"),
    "0000159457878": ("milk;peanut;wheat_gluten;soy;egg", "tree_nut", "DIRECT"),
    "0000200000002": ("peanut", "", "DIRECT"),
    "0000200000015": ("tree_nut", "peanut;sesame", "DIRECT"),
    "0000210320102": ("soy;milk", "peanut;tree_nut;egg;wheat_gluten;sesame;shellfish", "DIRECT"),
    "00002171": ("coconut", "peanut;tree_nut;sesame", "DIRECT"),
    "0000231312345": ("milk;wheat_gluten;egg;peanut", "", "DIRECT"),
    "0000252828288": ("wheat_gluten;milk;soy;egg;peanut", "", "DIRECT"),
    "0000281756504": ("wheat_gluten;soy;milk;peanut;tree_nut;egg", "", "DIRECT"),
    "0000380102109": ("milk;tree_nut;peanut", "", "DIRECT"),
    "00004221": ("milk;peanut", "", "DIRECT"),
    "0000433821500": ("wheat_gluten;peanut;milk;egg", "", "DIRECT"),
    "00004559": ("peanut;wheat_gluten;soy", "", "DIRECT"),
    "00004902": ("soy", "milk;egg;wheat_gluten;peanut", "DIRECT"),
    "0000500000050": ("peanut", "", "DIRECT"),
    "0000600020002": ("milk;soy", "wheat_gluten;egg;peanut;tree_nut", "DIRECT"),
    "0000609154005": ("milk;soy", "peanut;tree_nut", "DIRECT"),
    "0000609983810": ("milk;peanut;soy", "", "DIRECT"),
    "00006910": ("wheat_gluten;peanut", "", "DIRECT"),
    "0000790430018": ("peanut;milk;soy", "", "DIRECT"),
    "0000790430063": ("peanut;milk;soy", "", "DIRECT"),
    "0000790430070": ("peanut;milk;soy", "", "DIRECT"),
}

with open(INPUT_FILE, encoding="utf-8", errors="replace", newline="") as f:
    rows = list(csv.DictReader(f))

print("Input rows:", len(rows))

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
    "review_status",
]

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for row in rows:
        confirmed, potential, evidence = labels.get(
            row["code"],
            ("", "", "UNCERTAIN")
        )

        writer.writerow({
            "code": row["code"],
            "product_name": row["product_name"],
            "ingredients_text": row["ingredients_text"],
            "allergens": row["allergens"],
            "allergens_en": row["allergens_en"],
            "additives_en": row["additives_en"],
            "confirmed_allergens": confirmed,
            "potential_allergens": potential,
            "evidence_level": evidence,
            "evidence_text": row["ingredients_text"],
            "review_status": "MANUALLY_REVIEWED",
        })

print("Ground-truth dataset created.")
print("Products:", len(rows))
print("Output:", OUTPUT_FILE)
