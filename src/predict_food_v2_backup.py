#!/usr/bin/env python3

from pathlib import Path
import csv
import re
import sys
import joblib


# ============================================================
# PATHS
# ============================================================

ROOT = Path(".")

KNOWLEDGE_FILE = (
    ROOT / "data/processed/ingredient_allergen_knowledge_14.csv"
)

MODEL_DIR = ROOT / "models/svm_allergen"

VECTORIZER_FILE = MODEL_DIR / "tfidf_vectorizer.joblib"
SVM_FILE = MODEL_DIR / "svm_allergen_model.joblib"


# ============================================================
# ALLERGENS
# ============================================================

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


# ============================================================
# NORMALISATION
# ============================================================

def normalize_text(text):
    text = str(text or "").lower()

    replacements = {
        "\u00e9": "e",
        "\u00e8": "e",
        "\u00ea": "e",
        "\u00eb": "e",
        "\u00e0": "a",
        "\u00e2": "a",
        "\u00e4": "a",
        "\u00ee": "i",
        "\u00ef": "i",
        "\u00f4": "o",
        "\u00f6": "o",
        "\u00f9": "u",
        "\u00fb": "u",
        "\u00fc": "u",
        "\u00e7": "c",
        "\u00df": "ss",
        "\u0153": "oe",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\s\.\!\?;\n]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# PHRASE-LEVEL EXCLUSIONS
# ============================================================

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

    # English plant-based milk phrases.
    # Prevent generic "milk -> milk" from firing
    # inside non-dairy milk alternatives.
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

        phrase_pattern = (
            r"(?<![a-z0-9])"
            + re.escape(phrase)
            + r"(?![a-z0-9])"
        )

        for phrase_match in re.finditer(
            phrase_pattern,
            text
        ):
            phrase_start = phrase_match.start()
            phrase_end = phrase_match.end()

            if start >= phrase_start and end <= phrase_end:
                return True

    return False


# ============================================================
# PRECAUTIONARY PATTERNS
# ============================================================

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

    for pattern in PRECAUTIONARY_PATTERNS:
        if re.search(pattern, sentence):
            return True

    return False


# ============================================================
# EVIDENCE SEGMENTS
# ============================================================

def split_evidence_segments(text):
    text = str(text)

    segments = re.split(
        r"(?<=[\.\!\?;])\s+|\n+",
        text
    )

    return [
        segment.strip()
        for segment in segments
        if segment.strip()
    ]


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():
    knowledge_raw = []

    with KNOWLEDGE_FILE.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as f:
        knowledge_raw = list(csv.DictReader(f))

    knowledge = []
    seen = set()

    for item in knowledge_raw:

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

        confidence = (
            item.get("confidence", "").strip()
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
            "confidence": confidence,
            "language": language,
        })

    # Same ordering principle as V2.1:
    # longest terms first.
    knowledge.sort(
        key=lambda x: len(x["ingredient"]),
        reverse=True
    )

    return knowledge


# ============================================================
# KG INFERENCE
# ============================================================

def run_kg(ingredient_text, knowledge):

    confirmed = set()
    potential = set()

    direct_matches = []
    precautionary_matches = []

    normalized_original = normalize_text(
        ingredient_text
    )

    segments = split_evidence_segments(
        ingredient_text
    )

    for segment in segments:

        normalized_segment = normalize_text(
            segment
        )

        if not normalized_segment:
            continue

        precautionary_segment = (
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

                match_string = (
                    f"{item['ingredient_original']} -> {allergen}"
                )

                if evidence_type == "special_threshold":
                    continue

                if precautionary_segment:
                    potential.add(allergen)
                    precautionary_matches.append(
                        match_string
                    )
                else:
                    confirmed.add(allergen)
                    direct_matches.append(
                        match_string
                    )

    # Confirmed always overrides potential.
    potential -= confirmed

    return {
        "confirmed": sorted(confirmed),
        "potential": sorted(potential),
        "direct_matches": sorted(set(direct_matches)),
        "precautionary_matches": sorted(
            set(precautionary_matches)
        ),
    }


# ============================================================
# SVM INFERENCE
# ============================================================

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


# ============================================================
# HYBRID FUSION
# ============================================================

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

    # KG evidence remains authoritative.
    confirmed = set(
        kg_confirmed
    )

    potential = (
        kg_potential
        - confirmed
    )

    # SVM predictions unsupported by KG
    # become review candidates.
    review_candidates = (
        svm_predictions
        - kg_confirmed
        - kg_potential
    )

    # SVM prediction of a KG potential allergen
    # is treated as an upgrade signal.
    upgraded = (
        svm_predictions
        & kg_potential
    )

    confirmed.update(
        upgraded
    )

    potential -= upgraded

    return {
        "confirmed": sorted(confirmed),
        "potential": sorted(potential),
        "review_candidates": sorted(
            review_candidates
        ),
    }


# ============================================================
# DISPLAY
# ============================================================

def print_list(title, values):

    print(title)

    if not values:
        print("  None")
        return

    for value in values:
        print(f"  ✓ {value}")


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:
        print(
            'Usage:\n'
            'python src/predict_food.py '
            '"wheat flour, milk powder, soy lecithin"'
        )
        sys.exit(1)

    ingredient_text = " ".join(
        sys.argv[1:]
    ).strip()

    if not ingredient_text:
        print("ERROR: Ingredient text is empty.")
        sys.exit(1)

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
    print("P-HAF-KG V2.1 + SVM FOOD ANALYSIS")
    print("=" * 72)

    print()
    print("Ingredient text:")
    print(f"  {ingredient_text}")

    print()
    print("Loading P-HAF-KG knowledge base...")
    knowledge = load_knowledge_base()

    print(
        f"Knowledge relationships loaded: "
        f"{len(knowledge)}"
    )

    print()
    print("Running P-HAF-KG V2.1 evidence analysis...")
    kg = run_kg(
        ingredient_text,
        knowledge
    )

    print()
    print("Running trained SVM...")
    svm = run_svm(
        ingredient_text
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

    hybrid = hybrid_decision(
        kg,
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
