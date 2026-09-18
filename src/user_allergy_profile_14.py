import json
from pathlib import Path


OUTPUT_FILE = Path(
    "data/processed/user_allergy_profile_14.json"
)


ALLERGENS = {
    "celery": "Celery",
    "wheat_gluten": "Cereals containing gluten",
    "crustaceans": "Crustaceans",
    "egg": "Egg",
    "fish": "Fish",
    "lupin": "Lupin",
    "milk": "Milk",
    "molluscs": "Molluscs",
    "mustard": "Mustard",
    "peanut": "Peanuts",
    "sesame": "Sesame",
    "soy": "Soybeans",
    "sulphites": "Sulphur dioxide and sulphites",
    "tree_nut": "Tree nuts",
}


# ============================================================
# USER PROFILE
# Change this list when testing different users
# ============================================================

USER_ALLERGIES = [
    "peanut",
    "milk",
    "egg",
]


# ============================================================
# VALIDATION
# ============================================================

invalid = [
    allergen
    for allergen in USER_ALLERGIES
    if allergen not in ALLERGENS
]

if invalid:
    raise ValueError(
        f"Invalid allergen(s): {invalid}"
    )


# Remove duplicates while preserving order
USER_ALLERGIES = list(
    dict.fromkeys(USER_ALLERGIES)
)


# ============================================================
# CREATE PROFILE
# ============================================================

profile = {
    "profile_version": "1.0",

    "allergy_count": len(
        USER_ALLERGIES
    ),

    "allergies": USER_ALLERGIES,

    "allergy_names": [
        ALLERGENS[a]
        for a in USER_ALLERGIES
    ],
}


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        profile,
        f,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# DISPLAY
# ============================================================

print(
    "===== P-HAF-KG V2.1 USER ALLERGY PROFILE ====="
)

print(
    "Profile version:",
    profile["profile_version"]
)

print(
    "Number of allergies:",
    profile["allergy_count"]
)

print()

print("Selected allergies:")

for allergen in USER_ALLERGIES:

    print(
        f"- {ALLERGENS[allergen]}"
    )

print()

print(
    "Saved to:"
)

print(
    OUTPUT_FILE
)
