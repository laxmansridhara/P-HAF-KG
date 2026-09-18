import csv
import re
from pathlib import Path


# ============================================================
# P-HAF-KG V2
# IMPROVED 14-ALLERGEN EVIDENCE SEGMENTATION
# ============================================================

TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge_14.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2.csv"
)


# ============================================================
# 1. TEXT NORMALISATION
# ============================================================

def normalize_text(text):

    text = str(text).lower()

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


# ============================================================
# 2. PRECAUTIONARY PHRASES
# ============================================================

PRECAUTIONARY_PATTERNS = [

    # English
    r"\bmay contain\b",
    r"\bmay contain traces\b",
    r"\bcan contain\b",
    r"\bcan contain traces\b",
    r"\bcontains traces\b",
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

    # French
    r"\bpeut contenir\b",
    r"\bcontient des traces\b",
    r"\btraces de\b",
    r"\btrace de\b",
    r"\bpourrait contenir\b",
    r"\bpresence possible\b",
    r"\bfabrique dans une usine\b",
    r"\bfabrique dans un atelier\b",
    r"\bproduit dans une usine\b",
]


# ============================================================
# 3. PRECAUTIONARY SENTENCE DETECTION
# ============================================================

def is_precautionary_sentence(sentence):

    sentence = normalize_text(
        sentence
    )

    for pattern in PRECAUTIONARY_PATTERNS:

        if re.search(
            pattern,
            sentence
        ):
            return True

    return False


# ============================================================
# 4. SPLIT TEXT INTO EVIDENCE SEGMENTS
# ============================================================

def split_evidence_segments(text):

    """
    Split product text into relatively independent
    evidence segments.

    The objective is to avoid assigning the
    precautionary status of one statement to
    unrelated ingredient terms elsewhere.
    """

    text = str(text)

    # Keep common separators as boundaries.
    segments = re.split(
        r"(?<=[\.\!\?;])\s+|\n+",
        text
    )

    cleaned = []

    for segment in segments:

        segment = segment.strip()

        if not segment:
            continue

        cleaned.append(
            segment
        )

    return cleaned


# ============================================================
# 5. LOAD KNOWLEDGE BASE
# ============================================================

with KNOWLEDGE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    knowledge_raw = list(
        csv.DictReader(f)
    )


# ============================================================
# 6. CLEAN KNOWLEDGE
# ============================================================

knowledge = []

seen = set()

for item in knowledge_raw:

    ingredient_original = (
        item["ingredient"].strip()
    )

    ingredient = normalize_text(
        ingredient_original
    )

    allergen = (
        item["allergen"].strip()
    )

    evidence_type = (
        item["evidence_type"].strip()
    )

    confidence = (
        item["confidence"].strip()
    )

    language = (
        item["language"].strip()
    )

    if not ingredient:
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

        "ingredient":
            ingredient,

        "ingredient_original":
            ingredient_original,

        "allergen":
            allergen,

        "evidence_type":
            evidence_type,

        "confidence":
            confidence,

        "language":
            language,
    })


# ============================================================
# 7. LONGEST TERMS FIRST
# ============================================================

knowledge.sort(
    key=lambda x: len(
        x["ingredient"]
    ),
    reverse=True
)


# ============================================================
# 8. LOAD TEST DATA
# ============================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = list(
        csv.DictReader(f)
    )


results = []


# ============================================================
# 9. PROCESS PRODUCTS
# ============================================================

for row in test_rows:

    original_text = row[
        "ingredients_text"
    ]

    confirmed_allergens = set()

    potential_allergens = set()

    direct_matches = set()

    precautionary_matches = set()

    special_threshold_matches = set()


    # --------------------------------------------------------
    # Split into evidence segments
    # --------------------------------------------------------

    segments = split_evidence_segments(
        original_text
    )


    # --------------------------------------------------------
    # Process each segment independently
    # --------------------------------------------------------

    for segment in segments:

        normalized_segment = normalize_text(
            segment
        )

        if not normalized_segment:
            continue


        precautionary_segment = (
            is_precautionary_sentence(
                segment
            )
        )


        # ----------------------------------------------------
        # Match knowledge terms
        # ----------------------------------------------------

        for item in knowledge:

            ingredient = item[
                "ingredient"
            ]

            allergen = item[
                "allergen"
            ]

            evidence_type = item[
                "evidence_type"
            ]


            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(ingredient)
                + r"(?![a-z0-9])"
            )


            matches = re.finditer(
                pattern,
                normalized_segment
            )


            for match in matches:

                match_string = (
                    f"{item['ingredient_original']}"
                    f" -> "
                    f"{allergen}"
                )


                # =================================================
                # SPECIAL THRESHOLD EVIDENCE
                # =================================================

                if evidence_type == "special_threshold":

                    special_threshold_matches.add(
                        match_string
                    )

                    continue


                # =================================================
                # PRECAUTIONARY EVIDENCE
                # =================================================

                if precautionary_segment:

                    potential_allergens.add(
                        allergen
                    )

                    precautionary_matches.add(
                        match_string
                    )

                else:

                    # =================================================
                    # DIRECT EVIDENCE
                    # =================================================

                    confirmed_allergens.add(
                        allergen
                    )

                    direct_matches.add(
                        match_string
                    )


    # ============================================================
    # 10. CONFIRMED OVERRIDES POTENTIAL
    # ============================================================

    potential_allergens -= (
        confirmed_allergens
    )


    # ============================================================
    # 11. CREATE OUTPUT STRINGS
    # ============================================================

    confirmed_string = ";".join(
        sorted(
            confirmed_allergens
        )
    )

    potential_string = ";".join(
        sorted(
            potential_allergens
        )
    )

    direct_string = ";".join(
        sorted(
            direct_matches
        )
    )

    precautionary_string = ";".join(
        sorted(
            precautionary_matches
        )
    )

    special_string = ";".join(
        sorted(
            special_threshold_matches
        )
    )


    # ============================================================
    # 12. SAVE RESULT
    # ============================================================

    results.append({

        "code":
            row["code"],

        "product_name":
            row["product_name"],

        "confirmed_allergens":
            confirmed_string,

        "potential_allergens":
            potential_string,

        "direct_matches":
            direct_string,

        "precautionary_matches":
            precautionary_string,

        "special_threshold_matches":
            special_string,

    })


# ============================================================
# 13. WRITE OUTPUT
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

        "confirmed_allergens",

        "potential_allergens",

        "direct_matches",

        "precautionary_matches",

        "special_threshold_matches",

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
# 14. REPORT
# ============================================================

print(
    "===== P-HAF-KG V2 IMPROVED EVIDENCE LAYER ====="
)

print(
    "Products processed:",
    len(results)
)

print(
    "Unique knowledge relationships:",
    len(knowledge)
)

print(
    "Output:",
    OUTPUT_FILE
)


# ============================================================
# 15. SAMPLE RESULTS
# ============================================================

print(
    "\n===== SAMPLE RESULTS ====="
)


for result in results[:10]:

    print(
        "\nProduct:",
        result[
            "product_name"
        ]
    )

    print(
        "Confirmed:",
        result[
            "confirmed_allergens"
        ]
    )

    print(
        "Potential:",
        result[
            "potential_allergens"
        ]
    )

    print(
        "Direct:",
        result[
            "direct_matches"
        ]
    )

    print(
        "Precautionary:",
        result[
            "precautionary_matches"
        ]
    )

    print(
        "Sulphite threshold:",
        result[
            "special_threshold_matches"
        ]
    )
