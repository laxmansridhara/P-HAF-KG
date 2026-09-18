#!/usr/bin/env python3

import csv
import json
from pathlib import Path


# ============================================================
# P-HAF-KG V2.1
# IMAGE ANALYSIS -> CLEAN CSV EXPORT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RESULT_JSON = (
    BASE_DIR
    / "data"
    / "processed"
    / "p_haf_kg_image_analysis_result.json"
)

OUTPUT_CSV = (
    BASE_DIR
    / "data"
    / "processed"
    / "p_haf_kg_image_analysis_result.csv"
)


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def load_json():

    if not RESULT_JSON.exists():
        raise FileNotFoundError(
            f"Analysis result not found:\n{RESULT_JSON}\n\n"
            "Run scan_and_analyse_label.py first."
        )

    with open(
        RESULT_JSON,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_value(data, *keys, default=""):

    for key in keys:

        if key in data:

            value = data[key]

            if value is None:
                return default

            return value

    return default


def format_allergen_dict(allergens):

    if not allergens:
        return ""

    if isinstance(allergens, dict):

        names = []

        for allergen in allergens.keys():

            display_names = {
                "egg": "Egg",
                "milk": "Milk",
                "peanut": "Peanuts",
                "soy": "Soy",
                "wheat_gluten": "Wheat/Gluten",
                "tree_nut": "Tree Nuts",
                "sesame": "Sesame",
                "mustard": "Mustard",
                "celery": "Celery",
                "fish": "Fish",
                "crustaceans": "Crustaceans",
                "molluscs": "Molluscs",
                "lupin": "Lupin",
                "sulphites": "Sulphites"
            }

            names.append(
                display_names.get(
                    allergen,
                    allergen
                )
            )

        return "; ".join(sorted(set(names)))

    if isinstance(allergens, list):

        return "; ".join(
            str(item)
            for item in allergens
        )

    return str(allergens)


def format_user_allergies(profile):

    if not profile:
        return ""

    if isinstance(profile, dict):

        names = profile.get(
            "allergy_names",
            []
        )

        if names:
            return "; ".join(names)

        allergies = profile.get(
            "allergies",
            []
        )

        return "; ".join(
            str(item)
            for item in allergies
        )

    if isinstance(profile, list):

        return "; ".join(
            str(item)
            for item in profile
        )

    return str(profile)


def format_evidence(evidence):

    if not evidence:
        return ""

    results = []

    if isinstance(evidence, list):

        for item in evidence:

            if isinstance(item, dict):

                text = item.get(
                    "evidence",
                    ""
                )

                if text:
                    results.append(text)

            else:

                results.append(str(item))

    elif isinstance(evidence, dict):

        for allergen_data in evidence.values():

            if isinstance(allergen_data, list):

                for item in allergen_data:

                    if isinstance(item, dict):

                        text = item.get(
                            "evidence",
                            ""
                        )

                        if text:
                            results.append(text)

                    else:

                        results.append(str(item))

    else:

        results.append(str(evidence))

    return "; ".join(
        dict.fromkeys(results)
    )


def format_ocr_text(ocr):

    if not ocr:
        return ""

    if isinstance(ocr, dict):

        return str(
            ocr.get(
                "text",
                ""
            )
        )

    return str(ocr)


# ------------------------------------------------------------
# BUILD CLEAN RECORD
# ------------------------------------------------------------

def build_record(data):

    model_version = get_value(
        data,
        "model_version",
        default="P-HAF-KG V2.1"
    )

    if model_version == "2.1":
        model_version = "P-HAF-KG V2.1"

    image = get_value(
        data,
        "image",
        "image_path",
        "source_image"
    )

    # Keep only filename rather than user's
    # complete local filesystem path.
    if image:

        image = Path(
            str(image)
        ).name

    ocr = get_value(
        data,
        "ocr_text",
        "ocr",
        "text"
    )

    confirmed = get_value(
        data,
        "confirmed_allergens",
        "confirmed"
    )

    potential = get_value(
        data,
        "potential_allergens",
        "potential",
        "precautionary_allergens",
        "precautionary"
    )

    user_profile = get_value(
        data,
        "user_allergies",
        "allergies",
        "user_profile"
    )

    matched = get_value(
        data,
        "matched_user_allergens",
        "matched_allergens"
    )

    decision = get_value(
        data,
        "decision",
        "final_decision"
    )

    risk = get_value(
        data,
        "risk",
        "risk_level"
    )

    evidence = get_value(
        data,
        "evidence",
        "direct_evidence"
    )

    explanation = get_value(
        data,
        "explanation",
        "reason"
    )

    return {

        "model_version":
            model_version,

        "image":
            image,

        "ocr_text":
            format_ocr_text(ocr),

        "confirmed_allergens":
            format_allergen_dict(
                confirmed
            ),

        "potential_precautionary_allergens":
            format_allergen_dict(
                potential
            ),

        "user_allergies":
            format_user_allergies(
                user_profile
            ),

        "matched_user_allergens":
            format_allergen_dict(
                matched
            ),

        "decision":
            decision,

        "risk":
            risk,

        "evidence":
            format_evidence(
                evidence
            ),

        "explanation":
            explanation
    }


# ------------------------------------------------------------
# SAVE CSV
# ------------------------------------------------------------

def save_csv(record):

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [

        "model_version",

        "image",

        "ocr_text",

        "confirmed_allergens",

        "potential_precautionary_allergens",

        "user_allergies",

        "matched_user_allergens",

        "decision",

        "risk",

        "evidence",

        "explanation"
    ]

    with open(
        OUTPUT_CSV,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerow(record)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print(
        "===== P-HAF-KG V2.1 "
        "IMAGE ANALYSIS -> CLEAN CSV ====="
    )

    print()

    print(
        "Input:"
    )

    print(
        RESULT_JSON
    )

    print()

    data = load_json()

    record = build_record(
        data
    )

    save_csv(
        record
    )

    print(
        "===== EXPORT COMPLETE ====="
    )

    print()

    print(
        f"Model version: "
        f"{record['model_version']}"
    )

    print(
        f"Image: "
        f"{record['image']}"
    )

    print(
        f"Confirmed allergens: "
        f"{record['confirmed_allergens']}"
    )

    print(
        f"Potential/precautionary: "
        f"{record['potential_precautionary_allergens']}"
    )

    print(
        f"User allergies: "
        f"{record['user_allergies']}"
    )

    print(
        f"Matched user allergens: "
        f"{record['matched_user_allergens']}"
    )

    print(
        f"Decision: "
        f"{record['decision']}"
    )

    print(
        f"Risk: "
        f"{record['risk']}"
    )

    print()

    print(
        "Output:"
    )

    print(
        OUTPUT_CSV
    )


if __name__ == "__main__":
    main()