import csv
import random
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/final_annotation_dataset.csv"
)

BATCH1_FILE = Path(
    "data/processed/ground_truth_batch_01.csv"
)

OUTPUT_FILE = Path(
    "data/processed/annotation_batch_02.csv"
)

random.seed(42)

TARGETS = {
    "sesame": 25,
    "precautionary": 20,
    "hard_case": 20,
    "negative": 20,
}


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


rows = read_csv(INPUT_FILE)
batch1 = read_csv(BATCH1_FILE)

# Remove products already reviewed in Batch 1
reviewed_codes = {
    row["code"]
    for row in batch1
}

remaining = [
    row
    for row in rows
    if row["code"] not in reviewed_codes
]


def text_of(row):
    return " ".join([
        row.get("product_name", ""),
        row.get("ingredients_text", ""),
        row.get("allergens", ""),
        row.get("allergens_en", ""),
    ]).lower()


def candidate_contains(row, keyword):
    return keyword.lower() in text_of(row)


def select_candidates(pool, number, selected_codes):
    available = [
        row for row in pool
        if row["code"] not in selected_codes
    ]

    random.shuffle(available)

    selected = available[:number]

    for row in selected:
        selected_codes.add(row["code"])

    return selected


selected = []
selected_codes = set()

# --------------------------------------------------
# 1. SESAME PRIORITY
# --------------------------------------------------

sesame_pool = [
    row for row in remaining
    if any(
        word in text_of(row)
        for word in [
            "sesame",
            "sésame",
            "sesam",
            "tahini"
        ]
    )
]

batch = select_candidates(
    sesame_pool,
    TARGETS["sesame"],
    selected_codes
)

selected.extend(batch)


# --------------------------------------------------
# 2. PRECAUTIONARY STATEMENTS
# --------------------------------------------------

precautionary_pool = [
    row for row in remaining
    if any(
        phrase in text_of(row)
        for phrase in [
            "may contain",
            "may contain traces",
            "traces of",
            "kann spuren",
            "spuren von",
            "peut contenir",
            "traces éventuelles",
            "shared equipment",
            "shared facility",
            "same facility",
            "manufactured in a facility"
        ]
    )
]

batch = select_candidates(
    precautionary_pool,
    TARGETS["precautionary"],
    selected_codes
)

selected.extend(batch)


# --------------------------------------------------
# 3. HARD CASES
# Products containing multiple allergen keywords
# --------------------------------------------------

hard_case_pool = []

for row in remaining:

    text = text_of(row)

    keywords = [
        "peanut",
        "milk",
        "lait",
        "egg",
        "soy",
        "soya",
        "wheat",
        "gluten",
        "sesame",
        "almond",
        "cashew",
        "walnut",
        "hazelnut",
        "pistachio",
    ]

    matches = sum(
        keyword in text
        for keyword in keywords
    )

    if matches >= 3:
        hard_case_pool.append(row)

batch = select_candidates(
    hard_case_pool,
    TARGETS["hard_case"],
    selected_codes
)

selected.extend(batch)


# --------------------------------------------------
# 4. NEGATIVE / LOW-KEYWORD PRODUCTS
# --------------------------------------------------

negative_pool = []

for row in remaining:

    text = text_of(row)

    allergen_keywords = [
        "peanut",
        "milk",
        "lait",
        "milch",
        "egg",
        "oeuf",
        "soy",
        "soya",
        "soja",
        "wheat",
        "gluten",
        "flour",
        "sesame",
        "sésame",
        "almond",
        "cashew",
        "walnut",
        "hazelnut",
        "pistachio",
        "tree nut",
    ]

    matches = sum(
        keyword in text
        for keyword in allergen_keywords
    )

    if matches == 0:
        negative_pool.append(row)

batch = select_candidates(
    negative_pool,
    TARGETS["negative"],
    selected_codes
)

selected.extend(batch)


# --------------------------------------------------
# Fill remaining places if some categories
# did not have enough examples
# --------------------------------------------------

if len(selected) < 80:

    remaining_pool = [
        row for row in remaining
        if row["code"] not in selected_codes
    ]

    random.shuffle(remaining_pool)

    needed = 80 - len(selected)

    for row in remaining_pool[:needed]:
        selected.append(row)
        selected_codes.add(row["code"])


# --------------------------------------------------
# Write Batch 2
# --------------------------------------------------

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

        writer.writerow({
            "code": row.get("code", ""),
            "product_name": row.get("product_name", ""),
            "ingredients_text": row.get("ingredients_text", ""),
            "allergens": row.get("allergens", ""),
            "allergens_en": row.get("allergens_en", ""),
            "additives_en": row.get("additives_en", ""),
            "candidate_category": "",
            "confirmed_allergens": "",
            "potential_allergens": "",
            "evidence_level": "",
            "evidence_text": "",
            "is_food": "",
            "review_status": "PENDING",
        })


print("===== ANNOTATION BATCH 2 =====")
print("Previously reviewed:", len(reviewed_codes))
print("Remaining candidates:", len(remaining))
print("Batch 2 products:", len(selected))
print("Output:", OUTPUT_FILE)
