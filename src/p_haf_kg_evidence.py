import csv
import re
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_evidence.csv"
)


# ==================================================
# TEXT NORMALISATION
# ==================================================

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
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ==================================================
# PRECAUTIONARY PHRASES
# English + French
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
    r"\bcross[- ]contact\b",

    # French
    r"\bpeut contenir\b",
    r"\bpeut contenir des traces\b",
    r"\bpeut contenir des traces de\b",
    r"\bcontient des traces\b",
    r"\btraces de\b",
    r"\btrace de\b",
    r"\bpresence possible\b",
    r"\bfabrique dans une usine\b",
    r"\bfabrique dans un atelier\b",
    r"\bproduit dans une usine\b",
]


def is_precautionary(context):

    context = normalize_text(context)

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
# REMOVE DUPLICATE KNOWLEDGE RELATIONSHIPS
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

    key = (
        ingredient,
        allergen
    )

    if key in seen_knowledge:
        continue

    seen_knowledge.add(key)

    knowledge.append({
        "ingredient": ingredient,
        "allergen": allergen,
        "evidence_type": item[
            "evidence_type"
        ],
        "confidence": item[
            "confidence"
        ]
    })


# Longest terms first
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

    direct_allergens = set()

    potential_allergens = set()

    direct_matches = set()

    precautionary_matches = set()


    # ----------------------------------------------
    # MATCH KNOWLEDGE RELATIONSHIPS
    # ----------------------------------------------

    for item in knowledge:

        ingredient = item[
            "ingredient"
        ]

        if not ingredient:
            continue


        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(ingredient)
            + r"(?![a-z0-9])"
        )


        for match in re.finditer(
            pattern,
            text
        ):

            # Local context
            start = max(
                0,
                match.start() - 100
            )

            end = min(
                len(text),
                match.end() + 100
            )

            context = text[
                start:end
            ]


            allergen = item[
                "allergen"
            ]


            # --------------------------------------
            # EVIDENCE CLASSIFICATION
            # --------------------------------------

            if is_precautionary(
                context
            ):

                potential_allergens.add(
                    allergen
                )

                precautionary_matches.add(
                    ingredient
                    + " -> "
                    + allergen
                )

            else:

                direct_allergens.add(
                    allergen
                )

                direct_matches.add(
                    ingredient
                    + " -> "
                    + allergen
                )


    # ----------------------------------------------
    # DIRECT EVIDENCE OVERRIDES POTENTIAL
    # ----------------------------------------------

    potential_allergens -= (
        direct_allergens
    )


    results.append({

        "code": row["code"],

        "product_name": row[
            "product_name"
        ],

        "confirmed_allergens":
            ";".join(
                sorted(
                    direct_allergens
                )
            ),

        "potential_allergens":
            ";".join(
                sorted(
                    potential_allergens
                )
            ),

        "direct_matches":
            ";".join(
                sorted(
                    direct_matches
                )
            ),

        "precautionary_matches":
            ";".join(
                sorted(
                    precautionary_matches
                )
            ),

    })


# ==================================================
# SAVE
# ==================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "code",
            "product_name",
            "confirmed_allergens",
            "potential_allergens",
            "direct_matches",
            "precautionary_matches",
        ]
    )

    writer.writeheader()

    writer.writerows(
        results
    )


# ==================================================
# SUMMARY
# ==================================================

print(
    "===== P-HAF-KG EVIDENCE LAYER v2 ====="
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


print(
    "\n===== SAMPLE RESULTS ====="
)

for result in results[:10]:

    print(
        "\nProduct:",
        result["product_name"]
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
