import csv
import json
import re
import subprocess
import sys
from pathlib import Path


# ============================================================
# P-HAF-KG V2.1
# IMAGE -> OCR -> KNOWLEDGE GRAPH -> PERSONALIZED DECISION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

KNOWLEDGE_BASE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ingredient_allergen_knowledge_14.csv"
)

USER_PROFILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "user_allergy_profile_14.json"
)

OCR_LANGUAGES = "eng+fra+deu"


# ------------------------------------------------------------
# Allergen display names
# ------------------------------------------------------------

ALLERGEN_NAMES = {
    "celery": "Celery",
    "wheat_gluten": "Wheat/Gluten",
    "crustaceans": "Crustaceans",
    "egg": "Egg",
    "fish": "Fish",
    "lupin": "Lupin",
    "milk": "Milk",
    "molluscs": "Molluscs",
    "mustard": "Mustard",
    "peanut": "Peanuts",
    "sesame": "Sesame",
    "soy": "Soy",
    "sulphites": "Sulphites",
    "tree_nut": "Tree nuts",
}


# ------------------------------------------------------------
# Text normalisation
# ------------------------------------------------------------

def normalise(text):
    """
    Basic text normalisation used for matching OCR text
    against the P-HAF-KG knowledge base.
    """

    text = text.lower()

    text = text.replace("’", "'")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Convert repeated whitespace to one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ------------------------------------------------------------
# OCR
# ------------------------------------------------------------

def run_ocr(image_path):
    """
    Run Tesseract OCR.

    Languages:
        English + French + German
    """

    command = [
        "tesseract",
        str(image_path),
        "stdout",
        "-l",
        OCR_LANGUAGES,
        "--psm",
        "6",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Tesseract OCR failed:\n"
            + result.stderr
        )

    return result.stdout


# ------------------------------------------------------------
# Knowledge base
# ------------------------------------------------------------

def load_knowledge_base():

    relationships = []

    if not KNOWLEDGE_BASE.exists():

        raise FileNotFoundError(
            "Knowledge base not found:\n"
            f"{KNOWLEDGE_BASE}"
        )

    with open(
        KNOWLEDGE_BASE,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            ingredient = normalise(
                row.get("ingredient", "")
            )

            allergen = row.get(
                "allergen",
                ""
            ).strip()

            evidence_type = row.get(
                "evidence_type",
                ""
            ).strip().lower()

            if not ingredient or not allergen:
                continue

            relationships.append(
                {
                    "ingredient": ingredient,
                    "allergen": allergen,
                    "evidence_type": evidence_type,
                }
            )

    return relationships


# ------------------------------------------------------------
# Allergen evidence detection
# ------------------------------------------------------------

def detect_allergens(
    ocr_text,
    knowledge
):
    """
    Match OCR text against the P-HAF-KG
    ingredient-allergen relationships.

    Returns:

        confirmed
        potential

    Both are dictionaries:

        allergen -> evidence list
    """

    text = normalise(ocr_text)

    confirmed = {}
    potential = {}

    for relationship in knowledge:

        ingredient = relationship["ingredient"]
        allergen = relationship["allergen"]
        evidence_type = relationship["evidence_type"]

        if ingredient not in text:
            continue

        evidence = (
            f"{ingredient} -> "
            f"{ALLERGEN_NAMES.get(allergen, allergen)}"
        )

        if evidence_type == "direct":

            confirmed.setdefault(
                allergen,
                []
            ).append(evidence)

        elif evidence_type == "precautionary":

            potential.setdefault(
                allergen,
                []
            ).append(evidence)

    return confirmed, potential


# ------------------------------------------------------------
# User allergy profile
# ------------------------------------------------------------

def load_user_profile():

    if not USER_PROFILE.exists():

        raise FileNotFoundError(
            "User allergy profile not found:\n"
            f"{USER_PROFILE}"
        )

    with open(
        USER_PROFILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_user_allergies(profile):

    # Your actual JSON uses:
    #
    # "allergies": [
    #     "peanut",
    #     "milk",
    #     "egg"
    # ]

    allergies = profile.get(
        "allergies",
        []
    )

    return {
        str(allergen).strip().lower()
        for allergen in allergies
        if str(allergen).strip()
    }


# ------------------------------------------------------------
# Personalised decision engine
# ------------------------------------------------------------

def make_decision(
    confirmed,
    potential,
    user_allergies
):

    confirmed_matches = (
        set(confirmed.keys())
        & user_allergies
    )

    potential_matches = (
        set(potential.keys())
        & user_allergies
    )

    # Confirmed allergen always has priority
    if confirmed_matches:

        return (
            "NOT SUITABLE",
            "CONFIRMED",
            confirmed_matches,
        )

    # Precautionary evidence
    if potential_matches:

        return (
            "POTENTIAL RISK",
            "PRECAUTIONARY",
            potential_matches,
        )

    # Nothing matching the user's profile
    return (
        "SUITABLE",
        "NO DETECTED USER ALLERGEN",
        set(),
    )


# ------------------------------------------------------------
# Display evidence
# ------------------------------------------------------------

def print_evidence(
    title,
    evidence_dict
):

    print(title)

    if not evidence_dict:

        print("None")
        return

    for allergen in sorted(
        evidence_dict.keys()
    ):

        display_name = ALLERGEN_NAMES.get(
            allergen,
            allergen
        )

        print(display_name)

        for evidence in evidence_dict[allergen]:

            print(
                f"  {evidence}"
            )


# ------------------------------------------------------------
# Explanation
# ------------------------------------------------------------

def create_explanation(
    decision,
    risk,
    matched,
    confirmed,
    potential
):

    matched_names = [
        ALLERGEN_NAMES.get(
            allergen,
            allergen
        )
        for allergen in sorted(matched)
    ]

    matched_text = "; ".join(
        matched_names
    )

    if decision == "NOT SUITABLE":

        evidence = []

        for allergen in sorted(
            matched
        ):

            evidence.extend(
                confirmed.get(
                    allergen,
                    []
                )
            )

        evidence_text = "; ".join(
            evidence
        )

        return (
            "The product is not suitable because "
            "the P-HAF-KG model detected confirmed "
            "allergen(s) matching the user's allergy "
            f"profile: {matched_text}. "
            "Direct ingredient evidence: "
            f"{evidence_text}."
        )

    if decision == "POTENTIAL RISK":

        evidence = []

        for allergen in sorted(
            matched
        ):

            evidence.extend(
                potential.get(
                    allergen,
                    []
                )
            )

        evidence_text = "; ".join(
            evidence
        )

        return (
            "The product may pose a risk because "
            "the P-HAF-KG model detected "
            "precautionary evidence associated "
            f"with: {matched_text}. "
            "Precautionary evidence: "
            f"{evidence_text}."
        )

    return (
        "The P-HAF-KG model did not detect a "
        "confirmed or precautionary allergen "
        "matching the current user allergy profile."
    )


# ------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------

def main():

    print(
        "===== P-HAF-KG IMAGE -> OCR -> "
        "DECISION PIPELINE ====="
    )

    if len(sys.argv) != 2:

        print()
        print(
            "Usage:"
        )

        print(
            "python3 src/scan_and_analyse_label.py "
            "data/raw/food_label.jpg"
        )

        sys.exit(1)

    image_path = Path(
        sys.argv[1]
    )

    print(
        f"Image: {image_path}"
    )

    print()

    # --------------------------------------------------------
    # Validate image
    # --------------------------------------------------------

    if not image_path.exists():

        print(
            f"ERROR: Image not found: "
            f"{image_path}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Step 1: OCR
    # --------------------------------------------------------

    print(
        "Step 1: Running OCR..."
    )

    try:

        ocr_text = run_ocr(
            image_path
        )

    except Exception as error:

        print(
            f"ERROR during OCR: {error}"
        )

        sys.exit(1)

    print(
        "OCR completed."
    )

    print()

    # --------------------------------------------------------
    # Display OCR text
    # --------------------------------------------------------

    print(
        "===== OCR TEXT ====="
    )

    if ocr_text.strip():

        print(
            ocr_text.strip()
        )

    else:

        print(
            "WARNING: OCR returned no text."
        )

    print()

    # --------------------------------------------------------
    # Step 2: Knowledge base
    # --------------------------------------------------------

    print(
        "Step 2: Loading P-HAF-KG knowledge base..."
    )

    try:

        knowledge = load_knowledge_base()

    except Exception as error:

        print(
            f"ERROR loading knowledge base: "
            f"{error}"
        )

        sys.exit(1)

    print(
        f"Knowledge relationships: "
        f"{len(knowledge)}"
    )

    print()

    # --------------------------------------------------------
    # Step 3: Allergen detection
    # --------------------------------------------------------

    print(
        "Step 3: Detecting allergen evidence..."
    )

    confirmed, potential = detect_allergens(
        ocr_text,
        knowledge
    )

    print()

    print_evidence(
        "===== CONFIRMED ALLERGENS =====",
        confirmed
    )

    print()

    print_evidence(
        "===== POTENTIAL / PRECAUTIONARY =====",
        potential
    )

    print()

    # --------------------------------------------------------
    # Step 4: User profile
    # --------------------------------------------------------

    print(
        "Step 4: Loading user allergy profile..."
    )

    try:

        profile = load_user_profile()

        user_allergies = get_user_allergies(
            profile
        )

    except Exception as error:

        print(
            f"ERROR loading user profile: "
            f"{error}"
        )

        sys.exit(1)

    user_display_names = [
        ALLERGEN_NAMES.get(
            allergen,
            allergen
        )
        for allergen in sorted(
            user_allergies
        )
    ]

    print(
        "User allergies: "
        + (
            "; ".join(
                user_display_names
            )
            if user_display_names
            else "None"
        )
    )

    print()

    # --------------------------------------------------------
    # Step 5: Personalised decision
    # --------------------------------------------------------

    print(
        "Step 5: Personalised decision..."
    )

    decision, risk, matched = make_decision(
        confirmed,
        potential,
        user_allergies
    )

    print()

    print(
        "===== FINAL DECISION ====="
    )

    print(
        f"Decision: {decision}"
    )

    print(
        f"Risk: {risk}"
    )

    if matched:

        matched_names = [
            ALLERGEN_NAMES.get(
                allergen,
                allergen
            )
            for allergen in sorted(
                matched
            )
        ]

        print(
            "Matched user allergens: "
            + "; ".join(
                matched_names
            )
        )

    else:

        print(
            "Matched user allergens: None"
        )

    # --------------------------------------------------------
    # Step 6: Explanation
    # --------------------------------------------------------

    print()

    print(
        "===== EXPLANATION ====="
    )

    explanation = create_explanation(
        decision,
        risk,
        matched,
        confirmed,
        potential
    )

    print(
        explanation
    )

    print()

    print(
        "===== PIPELINE COMPLETE ====="
    )


if __name__ == "__main__":

    main()