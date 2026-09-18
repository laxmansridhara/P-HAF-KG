from pathlib import Path
import json


# ==================================================
# P-HAF-KG V2
# UK 14 REGULATED ALLERGEN CATEGORIES
# ==================================================

ALLERGEN_TAXONOMY = {
    "celery": {
        "name": "Celery",
        "category": "celery",
    },

    "wheat_gluten": {
        "name": "Cereals containing gluten",
        "category": "cereals_containing_gluten",
        "subtypes": [
            "wheat",
            "rye",
            "barley",
            "oats",
        ],
    },

    "crustaceans": {
        "name": "Crustaceans",
        "category": "crustaceans",
    },

    "egg": {
        "name": "Egg",
        "category": "egg",
    },

    "fish": {
        "name": "Fish",
        "category": "fish",
    },

    "lupin": {
        "name": "Lupin",
        "category": "lupin",
    },

    "milk": {
        "name": "Milk",
        "category": "milk",
    },

    "molluscs": {
        "name": "Molluscs",
        "category": "molluscs",
    },

    "mustard": {
        "name": "Mustard",
        "category": "mustard",
    },

    "peanut": {
        "name": "Peanuts",
        "category": "peanuts",
    },

    "sesame": {
        "name": "Sesame",
        "category": "sesame",
    },

    "soy": {
        "name": "Soybeans",
        "category": "soybeans",
    },

    "sulphites": {
        "name": "Sulphur dioxide and sulphites",
        "category": "sulphur_dioxide_sulphites",
        "threshold": "above 10 mg/kg or 10 mg/litre",
    },

    "tree_nut": {
        "name": "Tree nuts",
        "category": "tree_nuts",
    },
}


ALLERGEN_ORDER = [
    "celery",
    "wheat_gluten",
    "crustaceans",
    "egg",
    "fish",
    "lupin",
    "milk",
    "molluscs",
    "mustard",
    "peanut",
    "sesame",
    "soy",
    "sulphites",
    "tree_nut",
]


OUTPUT_FILE = Path(
    "data/processed/allergen_taxonomy_14.json"
)


# ==================================================
# VALIDATION
# ==================================================

assert len(ALLERGEN_TAXONOMY) == 14

assert len(ALLERGEN_ORDER) == 14

assert set(ALLERGEN_ORDER) == set(
    ALLERGEN_TAXONOMY.keys()
)


# ==================================================
# SAVE
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


output = {
    "framework": "P-HAF-KG",
    "version": "2.0",
    "jurisdiction": "UK",
    "allergen_count": 14,
    "allergen_order": ALLERGEN_ORDER,
    "allergens": ALLERGEN_TAXONOMY,
}


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=4,
        ensure_ascii=False
    )


# ==================================================
# DISPLAY
# ==================================================

print(
    "===== P-HAF-KG V2 ALLERGEN TAXONOMY ====="
)

print(
    "Framework: P-HAF-KG"
)

print(
    "Version: 2.0"
)

print(
    "UK regulated allergen categories:",
    len(ALLERGEN_ORDER)
)

print()


for number, allergen in enumerate(
    ALLERGEN_ORDER,
    start=1
):

    info = ALLERGEN_TAXONOMY[
        allergen
    ]

    print(
        f"{number:02d}. "
        f"{allergen:<18} "
        f"-> {info['name']}"
    )


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)
