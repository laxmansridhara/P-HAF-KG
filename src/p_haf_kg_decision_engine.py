import csv
import json
from pathlib import Path


# ============================================================
# FILES
# ============================================================

EVIDENCE_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2_1.csv"
)

PROFILE_FILE = Path(
    "data/processed/user_allergy_profile_14.json"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_decisions_14_v2_1.csv"
)


# ============================================================
# ALLERGEN DISPLAY NAMES
# ============================================================

ALLERGEN_NAMES = {
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
# HELPERS
# ============================================================

def parse_set(value):

    if not value:
        return set()

    return {
        item.strip()
        for item in value.split(";")
        if item.strip()
    }


def display_allergens(allergens):

    return ";".join(
        ALLERGEN_NAMES.get(
            allergen,
            allergen
        )
        for allergen in sorted(allergens)
    )


# ============================================================
# LOAD USER PROFILE
# ============================================================

with PROFILE_FILE.open(
    "r",
    encoding="utf-8"
) as f:

    profile = json.load(f)


USER_ALLERGIES = set(
    profile.get(
        "allergies",
        []
    )
)


if not USER_ALLERGIES:

    raise ValueError(
        "User allergy profile contains no allergies."
    )


invalid = [
    allergen
    for allergen in USER_ALLERGIES
    if allergen not in ALLERGEN_NAMES
]

if invalid:

    raise ValueError(
        f"Invalid allergens in user profile: {invalid}"
    )


# ============================================================
# LOAD EVIDENCE
# ============================================================

with EVIDENCE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(
        csv.DictReader(f)
    )


results = []


# ============================================================
# PROCESS PRODUCTS
# ============================================================

for row in rows:

    confirmed = parse_set(
        row.get(
            "confirmed_allergens",
            ""
        )
    )

    potential = parse_set(
        row.get(
            "potential_allergens",
            ""
        )
    )

    threshold = parse_set(
        row.get(
            "sulphite_threshold_allergens",
            ""
        )
    )

    # --------------------------------------------------------
    # USER-ALLERGY MATCHING
    # --------------------------------------------------------

    confirmed_matches = (
        USER_ALLERGIES & confirmed
    )

    threshold_matches = (
        USER_ALLERGIES & threshold
    )

    potential_matches = (
        USER_ALLERGIES & potential
    )

    # --------------------------------------------------------
    # DECISION PRIORITY
    #
    # 1. Confirmed
    # 2. Threshold
    # 3. Precautionary
    # 4. No detected user allergen
    # --------------------------------------------------------

    if confirmed_matches:

        decision = "NOT SUITABLE"

        risk = "CONFIRMED"

        matched = confirmed_matches

        reason = (
            "The product is not suitable because "
            "the model detected confirmed allergen(s) "
            "matching the user's allergy profile."
        )

    elif threshold_matches:

        decision = "NOT SUITABLE"

        risk = "THRESHOLD"

        matched = threshold_matches

        reason = (
            "The product may be unsuitable because "
            "the model detected threshold-related "
            "evidence matching the user's allergy profile."
        )

    elif potential_matches:

        decision = "POTENTIAL RISK"

        risk = "PRECAUTIONARY"

        matched = potential_matches

        reason = (
            "The product may pose a risk because "
            "the model detected precautionary evidence "
            "associated with the user's allergy profile."
        )

    else:

        decision = "SUITABLE"

        risk = "NO DETECTED USER ALLERGEN"

        matched = set()

        reason = (
            "The model did not detect a confirmed, "
            "threshold, or precautionary allergen "
            "matching the current user allergy profile."
        )

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    results.append({

        "code":
            row.get(
                "code",
                ""
            ),

        "product_name":
            row.get(
                "product_name",
                ""
            ),

        "user_allergies":
            display_allergens(
                USER_ALLERGIES
            ),

        "confirmed_allergens":
            row.get(
                "confirmed_allergens",
                ""
            ),

        "potential_allergens":
            row.get(
                "potential_allergens",
                ""
            ),

        "sulphite_threshold_allergens":
            row.get(
                "sulphite_threshold_allergens",
                ""
            ),

        "decision":
            decision,

        "risk":
            risk,

        "matched_user_allergens":
            display_allergens(
                matched
            ),

        "reason":
            reason,
    })


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [
        "code",
        "product_name",
        "user_allergies",
        "confirmed_allergens",
        "potential_allergens",
        "sulphite_threshold_allergens",
        "decision",
        "risk",
        "matched_user_allergens",
        "reason",
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        results
    )


# ============================================================
# SUMMARY
# ============================================================

summary = {
    "NOT SUITABLE": 0,
    "POTENTIAL RISK": 0,
    "SUITABLE": 0,
}


for result in results:

    summary[
        result["decision"]
    ] += 1


print(
    "===== P-HAF-KG V2.1 PERSONALIZED DECISION ENGINE ====="
)

print(
    f"Products processed: {len(results)}"
)

print(
    "User allergies:",
    display_allergens(
        USER_ALLERGIES
    )
)

print()

print(
    "===== DECISION SUMMARY ====="
)

print(
    "NOT SUITABLE:",
    summary["NOT SUITABLE"]
)

print(
    "POTENTIAL RISK:",
    summary["POTENTIAL RISK"]
)

print(
    "SUITABLE:",
    summary["SUITABLE"]
)

print()

print(
    "===== SAMPLE DECISIONS ====="
)

for result in results[:10]:

    print()

    print(
        "Product:",
        result["product_name"]
    )

    print(
        "Decision:",
        result["decision"]
    )

    print(
        "Risk:",
        result["risk"]
    )

    print(
        "Matched:",
        result["matched_user_allergens"]
    )

    print(
        "Reason:",
        result["reason"]
    )

print()

print(
    "Output:",
    OUTPUT_FILE
)