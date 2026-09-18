import csv
import re
from pathlib import Path


# ==================================================
# P-HAF-KG V2
# 14-ALLERGEN EVIDENCE LAYER
# ==================================================

TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge_14.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_evidence_14.csv"
)


# ==================================================
# TEXT NORMALISATION
# ==================================================

def normalize_text(text):
    """
    Normalise text for robust ingredient matching.

    This keeps letters/numbers and converts accented
    characters to their approximate ASCII forms.
    """

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


# ==================================================
# PRECAUTIONARY PHRASES
# ==================================================

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
    r"\bpeut contenir des traces\b",
    r"\bcontient des traces\b",
    r"\btraces de\b",
    r"\btrace de\b",
    r"\bpresence possible\b",
    r"\bfabrique dans une usine\b",
    r"\bfabrique dans un atelier\b",
    r"\bproduit dans une usine\b",
]


def is_precautionary(context):
    """
    Determine whether a local context indicates
    precautionary allergen information.
    """

    context = normalize_text(
        context
    )

    for pattern in PRECAUTIONARY_PATTERNS:

        if re.search(
            pattern,
            context
        ):

            return True

    return False


# ==================================================
# LOAD KNOWLEDGE BASE
# ==================================================

with KNOWLEDGE_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    knowledge_raw = list(
        csv.DictReader(f)
    )


# ==================================================
# CLEAN KNOWLEDGE BASE
# ==================================================

knowledge = []

seen_knowledge = set()

for item in knowledge_raw:

    ingredient = normalize_text(
        item["ingredient"]
    )

    allergen = item[
        "allergen"
    ].strip()

    evidence_type = item[
        "evidence_type"
    ].strip()

    confidence = item[
        "confidence"
    ].strip()

    language = item[
        "language"
    ].strip()

    key = (
        ingredient,
        allergen,
        evidence_type,
        language,
    )

    if key in seen_knowledge:
        continue

    seen_knowledge.add(
        key
    )

    knowledge.append({
        "ingredient": ingredient,
        "allergen": allergen,
        "evidence_type": evidence_type,
        "confidence": confidence,
        "language": language,
    })


# ==================================================
# LONGEST TERMS FIRST
# ==================================================

knowledge.sort(
    key=lambda x: len(
        x["ingredient"]
    ),
    reverse=True
)


# ==================================================
# LOAD TEST DATA
# ==================================================

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


# ==================================================
# PROCESS PRODUCTS
# ==================================================

for row in test_rows:

    original_text = row[
        "ingredients_text"
    ]

    text = normalize_text(
        original_text
    )

    confirmed_allergens = set()

    potential_allergens = set()

    direct_matches = set()

    precautionary_matches = set()

    special_threshold_matches = set()


    # ==================================================
    # MATCH KNOWLEDGE RELATIONSHIPS
    # ==================================================

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

        if not ingredient:
            continue


        # ----------------------------------------------
        # WORD-BOUNDARY MATCH
        # ----------------------------------------------

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(ingredient)
            + r"(?![a-z0-9])"
        )


        matches = re.finditer(
            pattern,
            text
        )


        for match in matches:

            # ------------------------------------------
            # LOCAL CONTEXT
            # ------------------------------------------

            start = max(
                0,
                match.start() - 150
            )

            end = min(
                len(text),
                match.end() + 150
            )

            context = text[
                start:end
            ]


            # ------------------------------------------
            # PRECAUTIONARY DETECTION
            # ------------------------------------------

            precautionary = (
                is_precautionary(
                    context
                )
            )


            # ==================================================
            # SPECIAL SULPHITE HANDLING
            # ==================================================

            if evidence_type == "special_threshold":

                special_threshold_matches.add(
                    f"{ingredient} -> {allergen}"
                )

                # We deliberately DO NOT add
                # sulphites to confirmed allergens here.
                #
                # The regulatory threshold requires
                # additional information.
                #
                # Therefore this is retained as
                # special evidence for later handling.

                continue


            # ==================================================
            # PRECAUTIONARY EVIDENCE
            # ==================================================

            if precautionary:

                potential_allergens.add(
                    allergen
                )

                precautionary_matches.add(
                    f"{ingredient} -> {allergen}"
                )

            else:

                # ==================================================
                # DIRECT EVIDENCE
                # ==================================================

                confirmed_allergens.add(
                    allergen
                )

                direct_matches.add(
                    f"{ingredient} -> {allergen}"
                )


    # ==================================================
    # IMPORTANT:
    # CONFIRMED ALLERGENS OVERRIDE POTENTIAL
    # ==================================================

    potential_allergens -= (
        confirmed_allergens
    )


    # ==================================================
    # SORTED OUTPUT
    # ==================================================

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


    # ==================================================
    # SAVE RESULT
    # ==================================================

    results.append({

        "code": row[
            "code"
        ],

        "product_name": row[
            "product_name"
        ],

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


# ==================================================
# WRITE OUTPUT
# ==================================================

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


# ==================================================
# REPORT
# ==================================================

print(
    "===== P-HAF-KG V2 EVIDENCE LAYER ====="
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


# ==================================================
# SAMPLE RESULTS
# ==================================================

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
        "Sulphite threshold evidence:",
        result[
            "special_threshold_matches"
        ]
    )
