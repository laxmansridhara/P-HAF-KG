import csv
import re
from pathlib import Path

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
)


TEST_FILE = Path(
    "data/processed/test.csv"
)

KNOWLEDGE_FILE = Path(
    "data/processed/ingredient_allergen_knowledge.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_ablation_no_normalization.csv"
)


ALLERGENS = [
    "peanut",
    "milk",
    "egg",
    "soy",
    "wheat_gluten",
    "sesame",
    "tree_nut",
]


# ==================================================
# RAW TEXT FUNCTION
# ==================================================

def raw_text(text):
    """
    Ablation condition:
    Do NOT apply the normalisation used by P-HAF-KG.

    Only convert the input to string so that matching
    can be performed safely.
    """

    return str(text)


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

    context = raw_text(context)

    for pattern in PRECAUTIONARY_PATTERNS:

        if re.search(
            pattern,
            context,
            flags=re.IGNORECASE
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
# PREPARE KNOWLEDGE
# ==================================================

knowledge = []

seen_knowledge = set()

for item in knowledge_raw:

    ingredient = raw_text(
        item["ingredient"]
    ).strip()

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

    # IMPORTANT:
    # No normalize_text() here.
    text = raw_text(
        original_text
    )

    direct_allergens = set()

    potential_allergens = set()

    direct_matches = set()

    precautionary_matches = set()


    # ==============================================
    # MATCH KNOWLEDGE RELATIONSHIPS
    # ==============================================

    for item in knowledge:

        ingredient = item[
            "ingredient"
        ]

        if not ingredient:
            continue

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(ingredient)
            + r"(?![a-zA-Z0-9])"
        )

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            # --------------------------------------
            # LOCAL CONTEXT
            # --------------------------------------

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


            # --------------------------------------
            # EVIDENCE TYPE
            # --------------------------------------

            precautionary = (
                is_precautionary(
                    context
                )
            )


            allergen = item[
                "allergen"
            ]


            if precautionary:

                potential_allergens.add(
                    allergen
                )

                precautionary_matches.add(
                    f"{ingredient} -> {allergen}"
                )

            else:

                direct_allergens.add(
                    allergen
                )

                direct_matches.add(
                    f"{ingredient} -> {allergen}"
                )


    # ==============================================
    # CONFIRMED OVERRIDES POTENTIAL
    # ==============================================

    potential_allergens -= (
        direct_allergens
    )


    # ==============================================
    # SAVE RESULT
    # ==============================================

    results.append({

        "code":
            row["code"],

        "product_name":
            row["product_name"],

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
# EVALUATION
# ==================================================

y_true = []

y_pred = []


for result, test_row in zip(
    results,
    test_rows
):

    actual = {
        x.strip()
        for x in test_row[
            "confirmed_allergens"
        ].split(";")
        if x.strip()
    }

    predicted = {
        x.strip()
        for x in result[
            "confirmed_allergens"
        ].split(";")
        if x.strip()
    }


    true_vector = [
        1 if allergen in actual else 0
        for allergen in ALLERGENS
    ]

    pred_vector = [
        1 if allergen in predicted else 0
        for allergen in ALLERGENS
    ]

    y_true.append(
        true_vector
    )

    y_pred.append(
        pred_vector
    )


# ==================================================
# METRICS
# ==================================================

macro_precision = precision_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

macro_recall = recall_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

macro_f1 = f1_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

micro_f1 = f1_score(
    y_true,
    y_pred,
    average="micro",
    zero_division=0
)

hamming = hamming_loss(
    y_true,
    y_pred
)


per_precision = precision_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0
)

per_recall = recall_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0
)

per_f1 = f1_score(
    y_true,
    y_pred,
    average=None,
    zero_division=0
)


# ==================================================
# OUTPUT
# ==================================================

print(
    "===== P-HAF-KG ABLATION ====="
)

print(
    "Experiment: WITHOUT text normalisation"
)

print(
    "Test products:",
    len(test_rows)
)

print(
    "\n===== PER-ALLERGEN RESULTS ====="
)

for i, allergen in enumerate(
    ALLERGENS
):

    print(
        f"{allergen:<15}"
        f"Precision={per_precision[i]:.4f} "
        f"Recall={per_recall[i]:.4f} "
        f"F1={per_f1[i]:.4f}"
    )


print(
    "\n===== OVERALL ====="
)

print(
    f"Macro Precision: {macro_precision:.4f}"
)

print(
    f"Macro Recall:    {macro_recall:.4f}"
)

print(
    f"Macro F1:        {macro_f1:.4f}"
)

print(
    f"Micro F1:        {micro_f1:.4f}"
)

print(
    f"Hamming Loss:   {hamming:.4f}"
)


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


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)
