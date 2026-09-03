import csv
import json
from pathlib import Path


# ============================================================
# FILES
# ============================================================

INPUT_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2_1.csv"
)

PROFILE_FILE = Path(
    "data/processed/user_allergy_profile_14.json"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_explanations_14_v2_1.csv"
)


# ============================================================
# 14 ALLERGEN DISPLAY NAMES
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


def display_allergen(allergen):

    return ALLERGEN_NAMES.get(
        allergen,
        allergen
    )


def format_allergens(allergens):

    if not allergens:
        return ""

    return "; ".join(
        display_allergen(allergen)
        for allergen in sorted(allergens)
    )


def parse_evidence(value):

    evidence = []

    if not value:
        return evidence

    for item in value.split(";"):

        item = item.strip()

        if not item:
            continue

        if "->" not in item:
            continue

        ingredient, allergen = item.split(
            "->",
            1
        )

        evidence.append(
            (
                ingredient.strip(),
                allergen.strip()
            )
        )

    return evidence


def format_evidence(evidence):

    if not evidence:
        return ""

    return "; ".join(
        f"{ingredient} -> "
        f"{display_allergen(allergen)}"
        for ingredient, allergen in evidence
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
        "No allergies found in user profile."
    )


# ============================================================
# LOAD EVIDENCE
# ============================================================

with INPUT_FILE.open(
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

    direct_evidence = parse_evidence(
        row.get(
            "direct_matches",
            ""
        )
    )

    precautionary_evidence = parse_evidence(
        row.get(
            "precautionary_matches",
            ""
        )
    )

    threshold_evidence = parse_evidence(
        row.get(
            "sulphite_threshold_evidence",
            ""
        )
    )

    # ========================================================
    # MATCH USER PROFILE
    # ========================================================

    confirmed_matches = (
        USER_ALLERGIES & confirmed
    )

    threshold_matches = (
        USER_ALLERGIES & threshold
    )

    potential_matches = (
        USER_ALLERGIES & potential
    )


    # ========================================================
    # CONFIRMED
    # ========================================================

    if confirmed_matches:

        decision = "NOT SUITABLE"

        risk = "CONFIRMED"

        matched = confirmed_matches

        relevant_evidence = [
            item
            for item in direct_evidence
            if item[1] in matched
        ]

        evidence_text = format_evidence(
            relevant_evidence
        )

        explanation = (
            "The product is not suitable because "
            "the model detected confirmed allergen(s) "
            "matching the user's allergy profile: "
            f"{format_allergens(matched)}."
        )

        if evidence_text:

            explanation += (
                " Direct ingredient evidence: "
                f"{evidence_text}."
            )


    # ========================================================
    # THRESHOLD
    # ========================================================

    elif threshold_matches:

        decision = "NOT SUITABLE"

        risk = "THRESHOLD"

        matched = threshold_matches

        relevant_evidence = [
            item
            for item in threshold_evidence
            if item[1] in matched
        ]

        evidence_text = format_evidence(
            relevant_evidence
        )

        explanation = (
            "The product may be unsuitable because "
            "the model detected threshold-related "
            "evidence associated with: "
            f"{format_allergens(matched)}."
        )

        if evidence_text:

            explanation += (
                " Threshold evidence: "
                f"{evidence_text}."
            )


    # ========================================================
    # PRECAUTIONARY
    # ========================================================

    elif potential_matches:

        decision = "POTENTIAL RISK"

        risk = "PRECAUTIONARY"

        matched = potential_matches

        relevant_evidence = [
            item
            for item in precautionary_evidence
            if item[1] in matched
        ]

        evidence_text = format_evidence(
            relevant_evidence
        )

        explanation = (
            "The product may pose a risk because "
            "the model detected precautionary evidence "
            "associated with: "
            f"{format_allergens(matched)}."
        )

        if evidence_text:

            explanation += (
                " Precautionary evidence: "
                f"{evidence_text}."
            )


    # ========================================================
    # SUITABLE
    # ========================================================

    else:

        decision = "SUITABLE"

        risk = "NO DETECTED USER ALLERGEN"

        matched = set()

        evidence_text = ""

        explanation = (
            "The model did not detect a confirmed, "
            "threshold, or precautionary allergen "
            "matching the current user allergy profile."
        )


    # ========================================================
    # SAVE RESULT
    # ========================================================

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
            format_allergens(
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
            format_allergens(
                matched
            ),

        "evidence":
            evidence_text,

        "explanation":
            explanation,
    })


# ============================================================
# SAVE CSV
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
        "evidence",
        "explanation",
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
    "===== P-HAF-KG V2.1 PERSONALIZED EXPLANATION ENGINE ====="
)

print(
    f"Products processed: {len(results)}"
)

print(
    "User allergies:",
    format_allergens(
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
    "===== SAMPLE EXPLANATIONS ====="
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
        "Evidence:",
        result["evidence"]
    )

    print(
        "Explanation:",
        result["explanation"]
    )

print()

print(
    "Output:",
    OUTPUT_FILE
)