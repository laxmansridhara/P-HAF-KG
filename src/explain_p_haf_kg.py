import csv
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/p_haf_kg_evidence.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_explanations.csv"
)


# ==================================================
# USER ALLERGY PROFILE
# ==================================================

# Change this later when we connect the system
# to an actual user profile.

USER_ALLERGIES = {
    "peanut",
    # "milk",
    # "egg",
    # "soy",
    # "wheat_gluten",
    # "sesame",
    # "tree_nut",
}


ALLERGEN_LABELS = {
    "peanut": "Peanut",
    "milk": "Milk",
    "egg": "Egg",
    "soy": "Soy",
    "wheat_gluten": "Wheat/Gluten",
    "sesame": "Sesame",
    "tree_nut": "Tree nuts",
}


# ==================================================
# HELPERS
# ==================================================

def split_values(value):

    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


def label_allergen(allergen):

    return ALLERGEN_LABELS.get(
        allergen,
        allergen.replace("_", " ").title()
    )


def format_matches(value):

    if not value:
        return []

    return [
        x.strip()
        for x in value.split(";")
        if x.strip()
    ]


# ==================================================
# EXPLANATION GENERATOR
# ==================================================

def generate_explanation(row):

    confirmed = split_values(
        row["confirmed_allergens"]
    )

    potential = split_values(
        row["potential_allergens"]
    )

    user_confirmed = (
        confirmed &
        USER_ALLERGIES
    )

    user_potential = (
        potential &
        USER_ALLERGIES
    )

    direct_matches = format_matches(
        row["direct_matches"]
    )

    precautionary_matches = format_matches(
        row["precautionary_matches"]
    )


    # ==================================================
    # DECISION
    # ==================================================

    if user_confirmed:

        decision = "NOT SUITABLE"

        risk_level = "CONFIRMED"

    elif user_potential:

        decision = "POTENTIAL RISK"

        risk_level = "PRECAUTIONARY"

    else:

        decision = "SUITABLE"

        risk_level = "NO DETECTED USER ALLERGEN"


    # ==================================================
    # EXPLANATION
    # ==================================================

    explanation_parts = []


    if user_confirmed:

        allergen_names = ", ".join(
            label_allergen(x)
            for x in sorted(
                user_confirmed
            )
        )

        explanation_parts.append(
            f"The product is not suitable because "
            f"the model detected the confirmed allergen(s): "
            f"{allergen_names}."
        )


        relevant_direct = []

        for match in direct_matches:

            for allergen in user_confirmed:

                if (
                    f"-> {allergen}"
                    in match
                ):

                    relevant_direct.append(
                        match
                    )


        if relevant_direct:

            explanation_parts.append(
                "Direct ingredient evidence: "
                + "; ".join(
                    relevant_direct
                )
                + "."
            )


    elif user_potential:

        allergen_names = ", ".join(
            label_allergen(x)
            for x in sorted(
                user_potential
            )
        )

        explanation_parts.append(
            f"The product may pose a risk because "
            f"the model detected precautionary evidence "
            f"associated with: {allergen_names}."
        )


        relevant_potential = []

        for match in precautionary_matches:

            for allergen in user_potential:

                if (
                    f"-> {allergen}"
                    in match
                ):

                    relevant_potential.append(
                        match
                    )


        if relevant_potential:

            explanation_parts.append(
                "Precautionary evidence: "
                + "; ".join(
                    relevant_potential
                )
                + "."
            )


    else:

        explanation_parts.append(
            "The model did not detect a confirmed "
            "or precautionary allergen matching "
            "the current user allergy profile."
        )


    # ==================================================
    # GENERAL MODEL EVIDENCE
    # ==================================================

    confirmed_text = "; ".join(
        label_allergen(x)
        for x in sorted(
            confirmed
        )
    )

    potential_text = "; ".join(
        label_allergen(x)
        for x in sorted(
            potential
        )
    )


    return {

        "decision":
            decision,

        "risk_level":
            risk_level,

        "user_allergies":
            ";".join(
                sorted(
                    USER_ALLERGIES
                )
            ),

        "user_confirmed_allergens":
            ";".join(
                sorted(
                    user_confirmed
                )
            ),

        "user_potential_allergens":
            ";".join(
                sorted(
                    user_potential
                )
            ),

        "model_confirmed_allergens":
            confirmed_text,

        "model_potential_allergens":
            potential_text,

        "explanation":
            " ".join(
                explanation_parts
            ),

    }


# ==================================================
# LOAD INPUT
# ==================================================

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(
        csv.DictReader(f)
    )


# ==================================================
# GENERATE EXPLANATIONS
# ==================================================

results = []


for row in rows:

    explanation = generate_explanation(
        row
    )

    output = {

        "code":
            row["code"],

        "product_name":
            row["product_name"],

        "ingredients_text":
            row.get(
                "ingredients_text",
                ""
            ),

    }

    output.update(
        explanation
    )

    results.append(
        output
    )


# ==================================================
# SAVE
# ==================================================

fieldnames = [
    "code",
    "product_name",
    "ingredients_text",
    "decision",
    "risk_level",
    "user_allergies",
    "user_confirmed_allergens",
    "user_potential_allergens",
    "model_confirmed_allergens",
    "model_potential_allergens",
    "explanation",
]


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        results
    )


# ==================================================
# DISPLAY SAMPLE RESULTS
# ==================================================

print(
    "===== P-HAF-KG EXPLAINABILITY ====="
)

print(
    "Products processed:",
    len(results)
)

print(
    "User allergies:",
    ", ".join(
        label_allergen(x)
        for x in sorted(
            USER_ALLERGIES
        )
    )
)

print(
    "Output:",
    OUTPUT_FILE
)


print(
    "\n===== SAMPLE EXPLANATIONS ====="
)


for row in results[:10]:

    print(
        "\nProduct:",
        row["product_name"]
    )

    print(
        "Decision:",
        row["decision"]
    )

    print(
        "Risk:",
        row["risk_level"]
    )

    print(
        "Explanation:",
        row["explanation"]
    )
