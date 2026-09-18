#!/usr/bin/env python3

from pathlib import Path
import csv
import re
import sys
import joblib



# PATHS


ROOT = Path(".")

KNOWLEDGE_FILE = (
    ROOT / "data/processed/ingredient_allergen_knowledge_14.csv"
)

MODEL_DIR = ROOT / "models/svm_allergen"

VECTORIZER_FILE = MODEL_DIR / "tfidf_vectorizer.joblib"
SVM_FILE = MODEL_DIR / "svm_allergen_model.joblib"



# ALLERGENS


ALLERGENS = [
    "celery",
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
    "tree_nut",
    "wheat_gluten",
]


def parse_allergies(value):
    if not value:
        return set()

    values = value.replace("|", ",").replace(";", ",")

    return {
        item.strip()
        for item in values.split(",")
        if item.strip() in ALLERGENS
    }



# NORMALISATION


def normalize_text(text):
    text = str(text or "").lower()

    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ä": "a",
        "á": "a",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
        "œ": "oe",
        "ß": "ss",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text



# PHRASE EXCLUSIONS


PHRASE_EXCLUSIONS = {
    "noix de muscade": {"tree_nut"},
    "noix de coco": {"tree_nut"},

    "lait d amande": {"milk"},
    "lait damande": {"milk"},
    "lait de soja": {"milk"},
    "lait de coco": {"milk"},
    "lait de noisette": {"milk"},
    "lait d avoine": {"milk"},
    "lait de riz": {"milk"},

    # English plant-based milk alternatives.
    "almond milk": {"milk"},
    "coconut milk": {"milk"},
    "soy milk": {"milk"},
    "oat milk": {"milk"},
    "rice milk": {"milk"},
    "hazelnut milk": {"milk"},
}


def is_excluded_match(
    ingredient,
    allergen,
    text,
    start,
    end
):
    for phrase, excluded_allergens in PHRASE_EXCLUSIONS.items():

        if allergen not in excluded_allergens:
            continue

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(phrase)
            + r"(?![a-z0-9])"
        )

        for phrase_match in re.finditer(
            pattern,
            text
        ):
            if (
                start >= phrase_match.start()
                and end <= phrase_match.end()
            ):
                return True

    return False



# PRECAUTIONARY PATTERNS


PRECAUTIONARY_PATTERNS = [

    # English
    r"\bmay contain\b",
    r"\bmay contain traces\b",
    r"\bmay contain traces of\b",
    r"\bcan contain\b",
    r"\bcan contain traces\b",
    r"\bcan contain traces of\b",
    r"\bcontains traces\b",
    r"\bcontains traces of\b",
    r"\btraces of\b",
    r"\btrace of\b",
    r"\bpossible presence\b",
    r"\bpossibly contains\b",
    r"\bshared equipment\b",
    r"\bshared equipment with\b",
    r"\bmanufactured on equipment\b",
    r"\bmanufactured in a facility\b",
    r"\bproduced in a facility\b",
    r"\bmade in a facility\b",
    r"\bcross contact\b",
    r"\bcross contact with\b",
    r"\bcross contamination\b",
    r"\bfactory where\b",
    r"\bfactory in which\b",
    r"\bwhere .* are used\b",

    # French
    r"\bpeut contenir\b",
    r"\bpeut contenir des traces\b",
    r"\bpeut contenir des traces de\b",
    r"\bcontient des traces\b",
    r"\bcontient des traces de\b",
    r"\btraces de\b",
    r"\btrace de\b",
    r"\btraces eventuelles\b",
    r"\btrace eventuelle\b",
    r"\bpourrait contenir\b",
    r"\bpourrait contenir des traces\b",
    r"\bp r e s e n c e possible\b",
    r"\bpresence possible\b",
    r"\bfabrique dans une usine\b",
    r"\bfabrique dans un atelier\b",
    r"\bproduit dans une usine\b",
    r"\bproduit dans un atelier\b",
    r"\bfabrique ou\b",
    r"\bdans une fabrique\b",
    r"\bdans une usine\b",

    # German
    r"\bkann spuren enthalten\b",
    r"\bkann spuren von\b",
    r"\bspuren von\b",
    r"\bspuren enthalten\b",
]


def is_precautionary_sentence(sentence):
    sentence = normalize_text(sentence)

    return any(
        re.search(pattern, sentence)
        for pattern in PRECAUTIONARY_PATTERNS
    )



# EVIDENCE SEGMENTS


def split_evidence_segments(text):
    return [
        segment.strip()
        for segment in re.split(
            r"(?<=[\.\!\?;])\s+|\n+",
            str(text)
        )
        if segment.strip()
    ]



# KNOWLEDGE BASE


def load_knowledge_base():

    with KNOWLEDGE_FILE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        rows = list(csv.DictReader(f))

    knowledge = []
    seen = set()

    for item in rows:

        ingredient_original = (
            item.get("ingredient", "").strip()
        )

        ingredient = normalize_text(
            ingredient_original
        )

        allergen = (
            item.get("allergen", "").strip()
        )

        evidence_type = (
            item.get("evidence_type", "").strip()
        )

        language = (
            item.get("language", "").strip()
        )

        if not ingredient:
            continue

        if allergen not in ALLERGENS:
            continue

        key = (
            ingredient,
            allergen,
            evidence_type,
            language
        )

        if key in seen:
            continue

        seen.add(key)

        knowledge.append({
            "ingredient": ingredient,
            "ingredient_original": ingredient_original,
            "allergen": allergen,
            "evidence_type": evidence_type,
            "language": language,
        })

    knowledge.sort(
        key=lambda item: len(item["ingredient"]),
        reverse=True
    )

    return knowledge



# KG ANALYSIS


def run_kg(ingredient_text, knowledge):

    confirmed = set()
    potential = set()

    direct_matches = []
    precautionary_matches = []

    for segment in split_evidence_segments(
        ingredient_text
    ):

        normalized_segment = normalize_text(
            segment
        )

        if not normalized_segment:
            continue

        precautionary = (
            is_precautionary_sentence(segment)
        )

        for item in knowledge:

            ingredient = item["ingredient"]
            allergen = item["allergen"]
            evidence_type = item["evidence_type"]

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(ingredient)
                + r"(?![a-z0-9])"
            )

            for match in re.finditer(
                pattern,
                normalized_segment
            ):

                if is_excluded_match(
                    ingredient,
                    allergen,
                    normalized_segment,
                    match.start(),
                    match.end()
                ):
                    continue

                evidence = (
                    f"{item['ingredient_original']} "
                    f"-> {allergen}"
                )

                if evidence_type == "special_threshold":
                    continue

                if precautionary:
                    potential.add(allergen)
                    precautionary_matches.append(
                        evidence
                    )
                else:
                    confirmed.add(allergen)
                    direct_matches.append(
                        evidence
                    )

    potential -= confirmed

    return {
        "confirmed": sorted(confirmed),
        "potential": sorted(potential),
        "direct_matches": sorted(set(direct_matches)),
        "precautionary_matches": sorted(
            set(precautionary_matches)
        ),
    }



# SVM


def run_svm(ingredient_text):

    vectorizer = joblib.load(
        VECTORIZER_FILE
    )

    model = joblib.load(
        SVM_FILE
    )

    X = vectorizer.transform(
        [ingredient_text]
    )

    prediction = model.predict(X)[0]

    return sorted([
        allergen
        for allergen, value in zip(
            ALLERGENS,
            prediction
        )
        if int(value) == 1
    ])



# HYBRID


def hybrid_decision(kg, svm):

    kg_confirmed = set(
        kg["confirmed"]
    )

    kg_potential = set(
        kg["potential"]
    )

    svm_predictions = set(
        svm
    )

    confirmed = set(
        kg_confirmed
    )

    potential = (
        kg_potential
        - confirmed
    )

    # A potential KG allergen becomes confirmed only
    # when the SVM independently supports it.
    upgraded = (
        svm_predictions
        & kg_potential
    )

    confirmed.update(
        upgraded
    )

    potential -= upgraded

    # SVM predictions with no KG evidence remain
    # review candidates and are not confirmed.
    review_candidates = (
        svm_predictions
        - kg_confirmed
        - kg_potential
    )

    return {
        "confirmed": sorted(confirmed),
        "potential": sorted(potential),
        "review_candidates": sorted(
            review_candidates
        ),
    }



# PERSONALISED DECISION


def personalised_decision(
    confirmed,
    potential,
    review_candidates,
    user_allergies
):

    confirmed_matches = (
        set(confirmed)
        & user_allergies
    )

    potential_matches = (
        set(potential)
        & user_allergies
    )

    review_matches = (
        set(review_candidates)
        & user_allergies
    )

    if confirmed_matches:
        return (
            "NOT SUITABLE",
            confirmed_matches,
            potential_matches,
            review_matches,
        )

    if potential_matches:
        return (
            "POTENTIAL RISK",
            confirmed_matches,
            potential_matches,
            review_matches,
        )

    if review_matches:
        return (
            "REVIEW RECOMMENDED",
            confirmed_matches,
            potential_matches,
            review_matches,
        )

    return (
        "SUITABLE",
        confirmed_matches,
        potential_matches,
        review_matches,
    )



# DISPLAY


def print_list(title, values):

    print(title)

    if not values:
        print("  None")
        return

    for value in sorted(values):
        print(f"  ✓ {value}")



# ARGUMENT PARSING


def parse_arguments():

    args = sys.argv[1:]

    if not args:
        print(
            'Usage:\n'
            'python src/predict_food.py '
            '"ingredient text" '
            '--allergies milk,peanut'
        )
        sys.exit(1)

    if "--allergies" in args:

        index = args.index("--allergies")

        ingredient_args = args[:index]

        if index + 1 >= len(args):
            print(
                "ERROR: --allergies requires "
                "a comma-separated allergen list."
            )
            sys.exit(1)

        allergy_value = args[index + 1]

    else:

        ingredient_args = args
        allergy_value = ""

    ingredient_text = " ".join(
        ingredient_args
    ).strip()

    if not ingredient_text:
        print("ERROR: Ingredient text is empty.")
        sys.exit(1)

    user_allergies = parse_allergies(
        allergy_value
    )

    return ingredient_text, user_allergies



# MAIN


def main():

    ingredient_text, user_allergies = (
        parse_arguments()
    )

    if not KNOWLEDGE_FILE.exists():
        print(
            f"ERROR: Knowledge base not found: "
            f"{KNOWLEDGE_FILE}"
        )
        sys.exit(1)

    if not VECTORIZER_FILE.exists():
        print(
            f"ERROR: Vectorizer not found: "
            f"{VECTORIZER_FILE}"
        )
        sys.exit(1)

    if not SVM_FILE.exists():
        print(
            f"ERROR: SVM model not found: "
            f"{SVM_FILE}"
        )
        sys.exit(1)

    print()
    print("=" * 72)
    print("P-HAF-KG V2.1 + SVM PERSONALISED FOOD ANALYSIS")
    print("=" * 72)

    print()
    print("Ingredient text:")
    print(f"  {ingredient_text}")

    print()
    print_list(
        "User allergy profile:",
        user_allergies
    )

    knowledge = load_knowledge_base()

    print()
    print(
        f"Knowledge relationships loaded: "
        f"{len(knowledge)}"
    )

    kg = run_kg(
        ingredient_text,
        knowledge
    )

    svm = run_svm(
        ingredient_text
    )

    hybrid = hybrid_decision(
        kg,
        svm
    )

    print()
    print_list(
        "KG confirmed allergens:",
        kg["confirmed"]
    )

    print()
    print_list(
        "KG potential allergens:",
        kg["potential"]
    )

    print()
    print_list(
        "SVM predictions:",
        svm
    )

    print()
    print("-" * 72)
    print("FINAL HYBRID RESULT")
    print("-" * 72)

    print()
    print_list(
        "Confirmed:",
        hybrid["confirmed"]
    )

    print()
    print_list(
        "Potential / precautionary:",
        hybrid["potential"]
    )

    print()
    print_list(
        "AI candidates for review:",
        hybrid["review_candidates"]
    )

    decision, confirmed_matches, potential_matches, review_matches = (
        personalised_decision(
            hybrid["confirmed"],
            hybrid["potential"],
            hybrid["review_candidates"],
            user_allergies
        )
    )

    print()
    print("=" * 72)
    print("PERSONALISED DECISION")
    print("=" * 72)

    print()
    print(f"Decision: {decision}")

    if confirmed_matches:
        print()
        print_list(
            "Confirmed user-allergy matches:",
            confirmed_matches
        )

        print(
            "\nReason: confirmed allergen evidence "
            "matches the user's allergy profile."
        )

    elif potential_matches:
        print()
        print_list(
            "Potential user-allergy matches:",
            potential_matches
        )

        print(
            "\nReason: precautionary allergen evidence "
            "matches the user's allergy profile."
        )

    elif review_matches:
        print()
        print_list(
            "AI review candidates matching user profile:",
            review_matches
        )

        print(
            "\nReason: the SVM identified a candidate "
            "without KG-confirmed or KG-potential evidence."
        )

    else:
        print(
            "\nNo confirmed or potential allergen "
            "matches the user's allergy profile."
        )

    print()
    print("-" * 72)
    print("EVIDENCE")
    print("-" * 72)

    print()
    print_list(
        "Direct evidence:",
        kg["direct_matches"]
    )

    print()
    print_list(
        "Precautionary evidence:",
        kg["precautionary_matches"]
    )

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
