#!/usr/bin/env python3

"""
P-HAF-KG V2.1
IMAGE -> OCR -> KNOWLEDGE GRAPH -> PERSONALISED DECISION PIPELINE

Pipeline:
    1. Read food-label image
    2. Run Tesseract OCR
    3. Load P-HAF-KG knowledge base
    4. Detect confirmed and precautionary allergen evidence
    5. Load user allergy profile
    6. Apply personalised decision rules
    7. Generate human-readable explanation

This is a symbolic / knowledge-based system.
No generative AI model is used in the explanation layer.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import unicodedata
import subprocess
from collections import defaultdict
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OCR_OUTPUT = OUTPUT_DIR / "ocr_label_text.txt"

PIPELINE_OUTPUT = (
    OUTPUT_DIR
    / "p_haf_kg_image_analysis_result.json"
)


# ============================================================
# ALLERGEN NAMES
# ============================================================

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
    "tree_nut": "Tree Nuts",
}


# ============================================================
# NORMALISATION
# ============================================================

def normalise_text(text: str) -> str:
    """
    Normalise OCR / ingredient text.

    Operations:
    - lowercase
    - remove accents
    - normalise punctuation
    - collapse whitespace
    """

    if text is None:
        return ""

    text = str(text)

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = text.lower()

    text = text.replace("’", "'")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"[^a-z0-9À-ÿ\s\-_]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SAFE TERM MATCHING
# ============================================================

def ingredient_matches_text(
    ingredient: str,
    text: str
) -> bool:
    """
    Determine whether a knowledge-base ingredient term
    genuinely occurs in OCR text.

    Important:
    Very short terms such as German 'ei' must NOT be
    matched as arbitrary substrings.

    Examples:

        'ei' matches:
            'ei'
            'ei, milch'

        'ei' does NOT match:
            'ingredients'
            'protein'
            'leavening'

    Longer terms can be matched as phrases or within
    compound ingredient words such as:

        weizen -> weizenmehl
        gerste -> gerstenmalz
        malz -> gerstenmalz
    """

    ingredient = normalise_text(ingredient)
    text = normalise_text(text)

    if not ingredient or not text:
        return False

    # --------------------------------------------------------
    # Multi-word phrases
    # --------------------------------------------------------

    if " " in ingredient:
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(ingredient)
            + r"(?![a-z0-9])"
        )

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return True

        return False

    # --------------------------------------------------------
    # Very short terms
    # --------------------------------------------------------

    if len(ingredient) <= 3:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(ingredient)
            + r"(?![a-z0-9])"
        )

        return bool(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    # --------------------------------------------------------
    # Longer single terms
    # --------------------------------------------------------

    # Exact word match
    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(ingredient)
        + r"(?![a-z0-9])"
    )

    if re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    ):
        return True

    # Compound-word match.
    #
    # Examples:
    #   weizen -> weizenmehl
    #   gerste -> gerstenmalz
    #   malz -> gerstenmalz
    #
    # This is only allowed for terms of length >= 4.
    compound_pattern = (
        r"(?<![a-z0-9])"
        + re.escape(ingredient)
        + r"[a-z0-9]+"
    )

    if re.search(
        compound_pattern,
        text,
        flags=re.IGNORECASE
    ):
        return True

    return False


# ============================================================
# TESSERACT
# ============================================================

def find_tesseract() -> str | None:
    """
    Locate the Tesseract executable.
    """

    possible_paths = [
        "tesseract",
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]

    for path in possible_paths:

        try:

            result = subprocess.run(
                [path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return path

        except (
            FileNotFoundError,
            PermissionError,
            OSError,
        ):
            continue

    return None


# ============================================================
# OCR
# ============================================================

def run_ocr(
    image_path: Path,
    languages: str = "eng+fra+deu"
) -> str:
    """
    Run Tesseract OCR on the supplied image.
    """

    tesseract = find_tesseract()

    if tesseract is None:

        raise RuntimeError(
            "Tesseract was not found. "
            "Install it with Homebrew and make sure "
            "it is available in PATH."
        )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    command = [
        tesseract,
        str(image_path),
        "stdout",
        "-l",
        languages,
        "--psm",
        "6",
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Tesseract OCR failed:\n"
            + result.stderr
        )

    text = result.stdout.strip()

    if not text:

        raise RuntimeError(
            "Tesseract returned empty OCR text."
        )

    return text


# ============================================================
# KNOWLEDGE BASE
# ============================================================

def detect_column(
    fieldnames,
    candidates
):
    """
    Find a column name using several possible names.
    """

    if not fieldnames:
        return None

    normalised = {
        str(name).strip().lower(): name
        for name in fieldnames
    }

    for candidate in candidates:

        candidate_key = candidate.lower()

        if candidate_key in normalised:
            return normalised[candidate_key]

    return None


def load_knowledge_base():

    if not KNOWLEDGE_BASE.exists():

        raise FileNotFoundError(
            f"Knowledge base not found:\n"
            f"{KNOWLEDGE_BASE}"
        )

    relationships = []

    with open(
        KNOWLEDGE_BASE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames or []

        ingredient_column = detect_column(
            fieldnames,
            [
                "ingredient",
                "term",
                "keyword",
                "ingredient_term",
            ]
        )

        allergen_column = detect_column(
            fieldnames,
            [
                "allergen",
                "allergen_name",
                "target_allergen",
            ]
        )

        evidence_column = detect_column(
            fieldnames,
            [
                "evidence_type",
                "type",
                "match_type",
            ]
        )

        confidence_column = detect_column(
            fieldnames,
            [
                "confidence",
                "weight",
                "score",
            ]
        )

        language_column = detect_column(
            fieldnames,
            [
                "language",
                "lang",
            ]
        )

        if ingredient_column is None:
            raise RuntimeError(
                "Could not identify ingredient column "
                f"in {KNOWLEDGE_BASE}"
            )

        if allergen_column is None:
            raise RuntimeError(
                "Could not identify allergen column "
                f"in {KNOWLEDGE_BASE}"
            )

        for row in reader:

            ingredient = (
                row.get(ingredient_column)
                or ""
            ).strip()

            allergen = (
                row.get(allergen_column)
                or ""
            ).strip().lower()

            evidence_type = (
                row.get(evidence_column)
                if evidence_column
                else "direct"
            )

            evidence_type = (
                evidence_type
                or "direct"
            ).strip().lower()

            confidence = (
                row.get(confidence_column)
                if confidence_column
                else "1.0"
            )

            language = (
                row.get(language_column)
                if language_column
                else ""
            )

            if not ingredient or not allergen:
                continue

            if allergen not in ALLERGEN_NAMES:
                continue

            relationships.append(
                {
                    "ingredient": ingredient,
                    "allergen": allergen,
                    "evidence_type": evidence_type,
                    "confidence": confidence,
                    "language": language,
                }
            )

    return relationships


# ============================================================
# ALLERGEN DETECTION
# ============================================================

def detect_allergens(
    text: str,
    relationships
):
    """
    Detect allergen evidence from OCR text.

    Returns:

        confirmed
        potential
        direct_evidence
        precautionary_evidence
    """

    confirmed = defaultdict(list)
    potential = defaultdict(list)

    direct_evidence = []
    precautionary_evidence = []

    for relationship in relationships:

        ingredient = relationship["ingredient"]
        allergen = relationship["allergen"]
        evidence_type = relationship["evidence_type"]

        if not ingredient_matches_text(
            ingredient,
            text
        ):
            continue

        display_name = ALLERGEN_NAMES.get(
            allergen,
            allergen
        )

        evidence = (
            f"{ingredient} -> {display_name}"
        )

        if evidence_type == "direct":

            confirmed[
                allergen
            ].append(evidence)

            direct_evidence.append(
                {
                    "ingredient": ingredient,
                    "allergen": allergen,
                    "allergen_name": display_name,
                    "evidence_type": "direct",
                    "evidence": evidence,
                }
            )

        elif evidence_type in (
            "precautionary",
            "potential",
        ):

            potential[
                allergen
            ].append(evidence)

            precautionary_evidence.append(
                {
                    "ingredient": ingredient,
                    "allergen": allergen,
                    "allergen_name": display_name,
                    "evidence_type": "precautionary",
                    "evidence": evidence,
                }
            )

    # Remove duplicate evidence
    for allergen in list(confirmed.keys()):

        confirmed[allergen] = sorted(
            set(confirmed[allergen])
        )

    for allergen in list(potential.keys()):

        potential[allergen] = sorted(
            set(potential[allergen])
        )

    direct_evidence = unique_evidence(
        direct_evidence
    )

    precautionary_evidence = unique_evidence(
        precautionary_evidence
    )

    return (
        dict(confirmed),
        dict(potential),
        direct_evidence,
        precautionary_evidence,
    )


def unique_evidence(items):

    seen = set()
    output = []

    for item in items:

        key = (
            item["ingredient"],
            item["allergen"],
            item["evidence_type"],
        )

        if key in seen:
            continue

        seen.add(key)
        output.append(item)

    return output


# ============================================================
# USER PROFILE
# ============================================================

def load_user_profile():

    if not USER_PROFILE.exists():

        raise FileNotFoundError(
            f"User allergy profile not found:\n"
            f"{USER_PROFILE}"
        )

    with open(
        USER_PROFILE,
        "r",
        encoding="utf-8"
    ) as file:

        profile = json.load(file)

    allergies = profile.get(
        "allergies",
        []
    )

    allergies = [
        str(allergen).strip().lower()
        for allergen in allergies
        if str(allergen).strip()
    ]

    return profile, allergies


# ============================================================
# DECISION ENGINE
# ============================================================

def make_decision(
    confirmed,
    potential,
    user_allergies
):
    """
    Decision priority:

        1. Confirmed allergen
           -> NOT SUITABLE

        2. Precautionary allergen
           -> POTENTIAL RISK

        3. No matching allergen
           -> SUITABLE
    """

    confirmed_matches = [
        allergen
        for allergen in user_allergies
        if allergen in confirmed
    ]

    potential_matches = [
        allergen
        for allergen in user_allergies
        if allergen in potential
    ]

    if confirmed_matches:

        return {
            "decision": "NOT SUITABLE",
            "risk": "CONFIRMED",
            "matched_allergens": confirmed_matches,
        }

    if potential_matches:

        return {
            "decision": "POTENTIAL RISK",
            "risk": "PRECAUTIONARY",
            "matched_allergens": potential_matches,
        }

    return {
        "decision": "SUITABLE",
        "risk": "NO DETECTED USER ALLERGEN",
        "matched_allergens": [],
    }


# ============================================================
# EXPLANATION
# ============================================================

def build_explanation(
    decision,
    risk,
    matched_allergens,
    confirmed,
    potential,
):
    """
    Generate deterministic explanations from evidence.

    No LLM is used here.
    """

    matched_names = [
        ALLERGEN_NAMES.get(
            allergen,
            allergen
        )
        for allergen in matched_allergens
    ]

    matched_text = "; ".join(
        matched_names
    )

    if decision == "NOT SUITABLE":

        evidence_items = []

        for allergen in matched_allergens:

            evidence_items.extend(
                confirmed.get(
                    allergen,
                    []
                )
            )

        evidence_items = sorted(
            set(evidence_items)
        )

        evidence_text = "; ".join(
            evidence_items
        )

        if evidence_text:

            return (
                "The product is not suitable because "
                "the P-HAF-KG model detected confirmed "
                "allergen(s) matching the user's allergy "
                f"profile: {matched_text}. "
                "Direct ingredient evidence: "
                f"{evidence_text}."
            )

        return (
            "The product is not suitable because "
            "the P-HAF-KG model detected confirmed "
            "allergen(s) matching the user's allergy "
            f"profile: {matched_text}."
        )

    if decision == "POTENTIAL RISK":

        evidence_items = []

        for allergen in matched_allergens:

            evidence_items.extend(
                potential.get(
                    allergen,
                    []
                )
            )

        evidence_items = sorted(
            set(evidence_items)
        )

        evidence_text = "; ".join(
            evidence_items
        )

        if evidence_text:

            return (
                "The product may pose a risk because "
                "the P-HAF-KG model detected "
                "precautionary evidence associated "
                f"with: {matched_text}. "
                "Precautionary evidence: "
                f"{evidence_text}."
            )

        return (
            "The product may pose a risk because "
            "the P-HAF-KG model detected "
            "precautionary evidence associated "
            f"with: {matched_text}."
        )

    return (
        "The model did not detect a confirmed, "
        "threshold, or precautionary allergen "
        "matching the current user allergy profile."
    )


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_evidence_section(
    title,
    evidence_dict
):

    print()
    print(
        f"===== {title} ====="
    )

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

        for evidence in evidence_dict[
            allergen
        ]:

            print(
                f"  {evidence}"
            )


def format_allergen_names(
    allergens
):

    names = [
        ALLERGEN_NAMES.get(
            allergen,
            allergen
        )
        for allergen in allergens
    ]

    return "; ".join(names)


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    image_path,
    ocr_text,
    confirmed,
    potential,
    direct_evidence,
    precautionary_evidence,
    user_profile,
    user_allergies,
    decision_result,
    explanation,
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    result = {
        "model": "P-HAF-KG",
        "model_version": "2.1",
        "pipeline": [
            "image",
            "tesseract_ocr",
            "knowledge_base",
            "allergen_detection",
            "user_profile",
            "decision_engine",
            "explanation_engine",
        ],
        "image": str(image_path),
        "ocr": {
            "engine": "Tesseract",
            "languages": "eng+fra+deu",
            "text": ocr_text,
        },
        "knowledge_base": {
            "path": str(KNOWLEDGE_BASE),
            "relationship_count": None,
        },
        "confirmed_allergens": {
            allergen: values
            for allergen, values
            in confirmed.items()
        },
        "potential_allergens": {
            allergen: values
            for allergen, values
            in potential.items()
        },
        "direct_evidence": direct_evidence,
        "precautionary_evidence": precautionary_evidence,
        "user_profile": {
            "profile_version": user_profile.get(
                "profile_version"
            ),
            "allergies": user_allergies,
            "allergy_names": [
                ALLERGEN_NAMES.get(
                    allergen,
                    allergen
                )
                for allergen in user_allergies
            ],
        },
        "decision": decision_result[
            "decision"
        ],
        "risk": decision_result[
            "risk"
        ],
        "matched_user_allergens": (
            decision_result[
                "matched_allergens"
            ]
        ),
        "matched_user_allergen_names": [
            ALLERGEN_NAMES.get(
                allergen,
                allergen
            )
            for allergen
            in decision_result[
                "matched_allergens"
            ]
        ],
        "explanation": explanation,
    }

    with open(
        PIPELINE_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    with open(
        OCR_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            ocr_text
        )

    return result


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print(
        "===== P-HAF-KG V2.1 "
        "IMAGE -> OCR -> DECISION PIPELINE ====="
    )

    # --------------------------------------------------------
    # Validate command line
    # --------------------------------------------------------

    if len(sys.argv) < 2:

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

    if not image_path.is_absolute():

        image_path = (
            PROJECT_ROOT
            / image_path
        )

    image_path = image_path.resolve()

    print()
    print(
        f"Image: {image_path}"
    )

    # --------------------------------------------------------
    # Step 1 - OCR
    # --------------------------------------------------------

    print()
    print(
        "Step 1: Running OCR..."
    )

    try:

        ocr_text = run_ocr(
            image_path,
            languages="eng+fra+deu"
        )

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        sys.exit(1)

    print(
        "OCR completed."
    )

    print()
    print(
        "===== OCR TEXT ====="
    )

    print(
        ocr_text
    )

    # --------------------------------------------------------
    # Step 2 - Knowledge base
    # --------------------------------------------------------

    print()
    print(
        "Step 2: Loading P-HAF-KG knowledge base..."
    )

    try:

        relationships = (
            load_knowledge_base()
        )

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        sys.exit(1)

    print(
        "Knowledge relationships:",
        len(relationships)
    )

    # --------------------------------------------------------
    # Step 3 - Evidence detection
    # --------------------------------------------------------

    print()
    print(
        "Step 3: Detecting allergen evidence..."
    )

    (
        confirmed,
        potential,
        direct_evidence,
        precautionary_evidence,
    ) = detect_allergens(
        ocr_text,
        relationships
    )

    print_evidence_section(
        "CONFIRMED ALLERGENS",
        confirmed
    )

    print_evidence_section(
        "POTENTIAL / PRECAUTIONARY",
        potential
    )

    # --------------------------------------------------------
    # Step 4 - User profile
    # --------------------------------------------------------

    print()
    print(
        "Step 4: Loading user allergy profile..."
    )

    try:

        user_profile, user_allergies = (
            load_user_profile()
        )

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        sys.exit(1)

    print(
        "User allergies:",
        format_allergen_names(
            user_allergies
        )
        if user_allergies
        else "None"
    )

    # --------------------------------------------------------
    # Step 5 - Personalised decision
    # --------------------------------------------------------

    print()
    print(
        "Step 5: Personalised decision..."
    )

    decision_result = make_decision(
        confirmed,
        potential,
        user_allergies
    )

    decision = decision_result[
        "decision"
    ]

    risk = decision_result[
        "risk"
    ]

    matched_allergens = (
        decision_result[
            "matched_allergens"
        ]
    )

    matched_names = format_allergen_names(
        matched_allergens
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = build_explanation(
        decision,
        risk,
        matched_allergens,
        confirmed,
        potential,
    )

    # --------------------------------------------------------
    # Final decision
    # --------------------------------------------------------

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

    print(
        "Matched user allergens:",
        matched_names
        if matched_names
        else "None"
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    print()
    print(
        "===== EXPLANATION ====="
    )

    print(
        explanation
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_results(
        image_path=image_path,
        ocr_text=ocr_text,
        confirmed=confirmed,
        potential=potential,
        direct_evidence=direct_evidence,
        precautionary_evidence=precautionary_evidence,
        user_profile=user_profile,
        user_allergies=user_allergies,
        decision_result=decision_result,
        explanation=explanation,
    )

    print()
    print(
        "===== PIPELINE COMPLETE ====="
    )

    print()
    print(
        "Saved OCR text:"
    )

    print(
        OCR_OUTPUT
    )

    print()
    print(
        "Saved analysis:"
    )

    print(
        PIPELINE_OUTPUT
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()