import csv
import random
from pathlib import Path
from collections import Counter


# ============================================================
# P-HAF-KG V2.1
# GOLD TEST CANDIDATE SELECTOR
# ============================================================
#
# IMPORTANT:
# The generated annotation file is BLINDED.
#
# It does NOT expose:
# - SVM predictions
# - P-HAF-KG confirmed labels
# - P-HAF-KG potential labels
# - disagreement category
#
# Those are stored separately for later evaluation.
# ============================================================


csv.field_size_limit(10_000_000)

RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# ============================================================
# FILES
# ============================================================

TEST_FILE = Path(
    "data/processed/ml/test_candidate.csv"
)

DISAGREEMENT_FILE = Path(
    "data/processed/ml/disagreement/"
    "svm_p_haf_disagreements.csv"
)

OUTPUT_DIR = Path(
    "data/processed/ml/gold_test"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


BLINDED_FILE = (
    OUTPUT_DIR /
    "gold_test_annotation.csv"
)

REFERENCE_FILE = (
    OUTPUT_DIR /
    "gold_test_reference.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR /
    "gold_test_selection_summary.txt"
)


# ============================================================
# TARGET ALLERGENS
# ============================================================

TARGET_ALLERGENS = [
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
# SETTINGS
# ============================================================

TOTAL_GOLD = 500

TARGET_CHALLENGE = 350
TARGET_CONTROL = 150


# ============================================================
# HELPERS
# ============================================================

def split_labels(text):
    """
    Convert semicolon-separated labels to a set.
    """

    if not text:
        return set()

    return {
        value.strip()
        for value in text.split(";")
        if value.strip()
    }


def label_string(labels):
    """
    Convert labels to deterministic text.
    """

    return ";".join(
        sorted(labels)
    )


# ============================================================
# STEP 1
# LOAD TEST DATA
# ============================================================

print("=" * 70)
print("GOLD TEST CANDIDATE SELECTION")
print("=" * 70)

print("\nLoading silver test candidate...")

test_lookup = {}

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        code = (
            row.get("product_code") or ""
        ).strip()

        if not code:
            continue

        ingredient = (
            row.get("ingredient_text") or ""
        ).strip()

        if not ingredient:
            continue

        confirmed = split_labels(
            row.get(
                "confirmed_allergens"
            ) or ""
        )

        potential = split_labels(
            row.get(
                "potential_allergens"
            ) or ""
        )

        test_lookup[code] = {
            "product_code": code,

            "product_name":
                row.get(
                    "product_name"
                ) or "",

            "ingredient_text":
                ingredient,

            "silver_confirmed":
                confirmed,

            "silver_potential":
                potential,
        }


print(
    f"Usable test products: "
    f"{len(test_lookup):,}"
)


# ============================================================
# STEP 2
# LOAD DISAGREEMENT ANALYSIS
# ============================================================

print("\nLoading SVM/P-HAF-KG comparison...")

comparison = {}

with DISAGREEMENT_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        code = (
            row.get("product_code") or ""
        ).strip()

        if code not in test_lookup:
            continue

        svm = split_labels(
            row.get(
                "svm_predicted"
            ) or ""
        )

        kg_confirmed = split_labels(
            row.get(
                "p_haf_confirmed"
            ) or ""
        )

        kg_potential = split_labels(
            row.get(
                "p_haf_potential"
            ) or ""
        )

        svm_only = split_labels(
            row.get(
                "svm_only"
            ) or ""
        )

        kg_only = split_labels(
            row.get(
                "kg_only"
            ) or ""
        )

        potential_overlap = split_labels(
            row.get(
                "svm_potential_overlap"
            ) or ""
        )

        exact_agreement = (
            svm == kg_confirmed
        )


        # ----------------------------------------------------
        # Mutually exclusive disagreement category
        # ----------------------------------------------------

        if exact_agreement:

            disagreement_type = (
                "exact_agreement"
            )

        elif (
            svm_only
            and not kg_only
        ):

            disagreement_type = (
                "svm_only_prediction"
            )

        elif (
            kg_only
            and not svm_only
        ):

            disagreement_type = (
                "kg_only_prediction"
            )

        elif svm_only and kg_only:

            disagreement_type = (
                "both_sides_different"
            )

        else:

            disagreement_type = (
                "other_disagreement"
            )


        comparison[code] = {
            "svm": svm,
            "kg_confirmed": kg_confirmed,
            "kg_potential": kg_potential,
            "svm_only": svm_only,
            "kg_only": kg_only,
            "potential_overlap":
                potential_overlap,
            "exact_agreement":
                exact_agreement,
            "disagreement_type":
                disagreement_type,
        }


print(
    f"Comparison rows loaded: "
    f"{len(comparison):,}"
)


# ============================================================
# STEP 3
# BUILD CANDIDATE POOLS
# ============================================================

agreement_pool = []
kg_only_pool = []
svm_only_pool = []
both_pool = []
potential_pool = []


for code, info in comparison.items():

    if code not in test_lookup:
        continue


    if info["exact_agreement"]:

        agreement_pool.append(code)

    else:

        # ----------------------------------------------------
        # Disagreement pools
        # ----------------------------------------------------

        if (
            info["disagreement_type"]
            == "kg_only_prediction"
        ):

            kg_only_pool.append(code)

        elif (
            info["disagreement_type"]
            == "svm_only_prediction"
        ):

            svm_only_pool.append(code)

        elif (
            info["disagreement_type"]
            == "both_sides_different"
        ):

            both_pool.append(code)


        # ----------------------------------------------------
        # Potential evidence pool
        # ----------------------------------------------------

        if info["potential_overlap"]:

            potential_pool.append(code)


# Shuffle each pool.
for pool in [
    agreement_pool,
    kg_only_pool,
    svm_only_pool,
    both_pool,
    potential_pool,
]:

    random.shuffle(pool)


print("\nCandidate pools:")
print("-" * 70)

print(
    f"Exact agreement controls: "
    f"{len(agreement_pool):,}"
)

print(
    f"KG-only disagreements:    "
    f"{len(kg_only_pool):,}"
)

print(
    f"SVM-only disagreements:   "
    f"{len(svm_only_pool):,}"
)

print(
    f"Both-sides-different:     "
    f"{len(both_pool):,}"
)

print(
    f"Potential-evidence cases: "
    f"{len(potential_pool):,}"
)


# ============================================================
# STEP 4
# SELECT CHALLENGE CASES
# ============================================================

selected_challenge = []
selected_codes = set()


def add_from_pool(
    pool,
    target
):
    """
    Add unique products from a pool.
    """

    added = 0

    for code in pool:

        if len(
            selected_challenge
        ) >= TARGET_CHALLENGE:

            break

        if code in selected_codes:
            continue

        selected_codes.add(code)

        selected_challenge.append(code)

        added += 1

        if added >= target:
            break

    return added


# ------------------------------------------------------------
# Initial quotas
#
# These are intentionally diversified rather than purely
# random.
# ------------------------------------------------------------

add_from_pool(
    kg_only_pool,
    120
)

add_from_pool(
    svm_only_pool,
    80
)

add_from_pool(
    both_pool,
    50
)

add_from_pool(
    potential_pool,
    100
)


# ------------------------------------------------------------
# Fill any remaining challenge slots with unused
# disagreements.
# ------------------------------------------------------------

all_disagreement_codes = []

for pool in [
    kg_only_pool,
    svm_only_pool,
    both_pool,
]:

    all_disagreement_codes.extend(
        pool
    )


random.shuffle(
    all_disagreement_codes
)


for code in all_disagreement_codes:

    if len(
        selected_challenge
    ) >= TARGET_CHALLENGE:

        break

    if code in selected_codes:
        continue

    selected_codes.add(code)

    selected_challenge.append(code)


print(
    f"\nChallenge cases selected: "
    f"{len(selected_challenge):,}"
)


# ============================================================
# STEP 5
# SELECT AGREEMENT CONTROLS
# ============================================================

selected_controls = []


# ------------------------------------------------------------
# First ensure rare allergen representation.
# ------------------------------------------------------------

remaining_agreements = set(
    agreement_pool
)


# Number of control cases requested for
# every allergen where possible.
#
# This is a minimum diversity mechanism,
# not an attempt to force equal prevalence.
CONTROL_PER_CLASS = 5


for allergen in TARGET_ALLERGENS:

    candidates = []

    for code in agreement_pool:

        if code in selected_codes:
            continue

        if code not in remaining_agreements:
            continue


        info = comparison.get(
            code
        )

        if info is None:
            continue


        labels = (
            info["kg_confirmed"]
        )

        if allergen in labels:

            candidates.append(
                code
            )


    random.shuffle(candidates)


    for code in candidates:

        if len(selected_controls) >= (
            TARGET_CONTROL
        ):

            break

        if code in selected_codes:
            continue


        selected_codes.add(code)

        selected_controls.append(
            code
        )

        remaining_agreements.discard(
            code
        )


        # Only a small number of
        # guaranteed examples per class.
        if sum(
            1
            for selected_code
            in selected_controls
            if allergen in comparison[
                selected_code
            ]["kg_confirmed"]
        ) >= CONTROL_PER_CLASS:

            break


    if len(selected_controls) >= (
        TARGET_CONTROL
    ):

        break


# ------------------------------------------------------------
# Fill remaining control slots randomly.
# ------------------------------------------------------------

remaining_pool = list(
    remaining_agreements
)

random.shuffle(
    remaining_pool
)


for code in remaining_pool:

    if len(selected_controls) >= (
        TARGET_CONTROL
    ):

        break

    if code in selected_codes:
        continue

    selected_codes.add(code)

    selected_controls.append(
        code
    )


print(
    f"Control cases selected: "
    f"{len(selected_controls):,}"
)


# ============================================================
# STEP 6
# FILL TO EXACTLY 500
# ============================================================

if len(selected_codes) < TOTAL_GOLD:

    remaining = [
        code
        for code in comparison
        if code not in selected_codes
    ]

    random.shuffle(
        remaining
    )


    for code in remaining:

        if len(selected_codes) >= TOTAL_GOLD:
            break

        selected_codes.add(code)


# ------------------------------------------------------------
# If over the target for any reason, sample down.
# ------------------------------------------------------------

if len(selected_codes) > TOTAL_GOLD:

    selected_codes = set(
        random.sample(
            list(selected_codes),
            TOTAL_GOLD
        )
    )


print(
    f"\nFinal candidate count: "
    f"{len(selected_codes):,}"
)


# ============================================================
# STEP 7
# RANDOMISE FINAL ANNOTATION ORDER
#
# This prevents the reviewer from seeing categories in
# blocks and reduces selection-category bias.
# ============================================================

final_codes = list(
    selected_codes
)

random.shuffle(
    final_codes
)


# ============================================================
# STEP 8
# CREATE BLINDED ANNOTATION FILE
# ============================================================

annotation_fields = [
    "gold_id",
    "product_code",
    "product_name",
    "ingredient_text",
    "gold_confirmed_allergens",
    "gold_potential_allergens",
    "gold_evidence_level",
    "review_notes",
    "reviewer",
    "review_status",
]


print("\nCreating blinded annotation file...")


with BLINDED_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=annotation_fields
    )

    writer.writeheader()


    for number, code in enumerate(
        final_codes,
        start=1
    ):

        row = test_lookup[
            code
        ]


        writer.writerow({

            "gold_id":
                f"GOLD_{number:04d}",

            "product_code":
                row["product_code"],

            "product_name":
                row["product_name"],

            "ingredient_text":
                row["ingredient_text"],

            # ------------------------------------------------
            # THESE ARE INTENTIONALLY BLANK.
            # MANUAL REVIEW WILL FILL THEM.
            # ------------------------------------------------

            "gold_confirmed_allergens":
                "",

            "gold_potential_allergens":
                "",

            "gold_evidence_level":
                "",

            "review_notes":
                "",

            "reviewer":
                "",

            "review_status":
                "",
        })


# ============================================================
# STEP 9
# CREATE REFERENCE FILE
#
# This file contains the machine-generated predictions and
# is kept separate from the blinded annotation file.
# ============================================================

reference_fields = [
    "gold_id",
    "product_code",
    "product_name",
    "svm_predicted",
    "p_haf_confirmed",
    "p_haf_potential",
    "disagreement_type",
    "svm_only",
    "kg_only",
    "potential_overlap",
]


print(
    "Creating reference file..."
)


with REFERENCE_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=reference_fields
    )

    writer.writeheader()


    for number, code in enumerate(
        final_codes,
        start=1
    ):

        info = comparison[
            code
        ]

        row = test_lookup[
            code
        ]


        writer.writerow({

            "gold_id":
                f"GOLD_{number:04d}",

            "product_code":
                code,

            "product_name":
                row["product_name"],

            "svm_predicted":
                label_string(
                    info["svm"]
                ),

            "p_haf_confirmed":
                label_string(
                    info["kg_confirmed"]
                ),

            "p_haf_potential":
                label_string(
                    info["kg_potential"]
                ),

            "disagreement_type":
                info[
                    "disagreement_type"
                ],

            "svm_only":
                label_string(
                    info["svm_only"]
                ),

            "kg_only":
                label_string(
                    info["kg_only"]
                ),

            "potential_overlap":
                label_string(
                    info[
                        "potential_overlap"
                    ]
                ),
        })


# ============================================================
# STEP 10
# ANALYSE SELECTED SET
# ============================================================

selected_counter = Counter()

selected_type_counter = Counter()

selected_disagreement_counter = Counter()

rare_class_presence = Counter()

negative_candidates = 0

multi_allergen_candidates = 0


for code in final_codes:

    info = comparison[
        code
    ]

    confirmed = info[
        "kg_confirmed"
    ]

    potential = info[
        "kg_potential"
    ]


    selected_type_counter[
        info[
            "disagreement_type"
        ]
    ] += 1


    if (
        info["disagreement_type"]
        != "exact_agreement"
    ):

        selected_disagreement_counter[
            info[
                "disagreement_type"
            ]
        ] += 1


    if not confirmed:

        negative_candidates += 1


    if len(confirmed) >= 2:

        multi_allergen_candidates += 1


    for allergen in confirmed:

        selected_counter[
            allergen
        ] += 1

        rare_class_presence[
            allergen
        ] += 1


    for allergen in potential:

        rare_class_presence[
            f"potential:{allergen}"
        ] += 1


# ============================================================
# STEP 11
# SAVE SUMMARY
# ============================================================

with SUMMARY_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "P-HAF-KG V2.1 GOLD TEST CANDIDATE SELECTION\n"
    )

    f.write(
        "=" * 70 + "\n\n"
    )

    f.write(
        f"Random seed: {RANDOM_SEED}\n"
    )

    f.write(
        f"Total selected: {len(final_codes):,}\n"
    )

    f.write(
        f"Target size: {TOTAL_GOLD:,}\n\n"
    )


    f.write(
        "SELECTION COMPOSITION\n"
    )

    f.write(
        "-" * 70 + "\n"
    )

    f.write(
        f"Challenge target: "
        f"{TARGET_CHALLENGE}\n"
    )

    f.write(
        f"Control target: "
        f"{TARGET_CONTROL}\n"
    )

    f.write(
        f"Challenge selected before fill: "
        f"{len(selected_challenge)}\n"
    )

    f.write(
        f"Controls selected before fill: "
        f"{len(selected_controls)}\n"
    )

    f.write(
        f"Products without confirmed KG allergen: "
        f"{negative_candidates}\n"
    )

    f.write(
        f"Products with 2+ confirmed allergens: "
        f"{multi_allergen_candidates}\n\n"
    )


    f.write(
        "MACHINE-GENERATED CATEGORY COUNTS\n"
    )

    f.write(
        "-" * 70 + "\n"
    )


    for category, count in (
        selected_type_counter
        .most_common()
    ):

        f.write(
            f"{category}: {count}\n"
        )


    f.write("\n")

    f.write(
        "CONFIRMED ALLERGEN REPRESENTATION\n"
    )

    f.write(
        "-" * 70 + "\n"
    )


    for allergen in TARGET_ALLERGENS:

        f.write(
            f"{allergen}: "
            f"{selected_counter[allergen]}\n"
        )


    f.write("\n")

    f.write(
        "POTENTIAL EVIDENCE REPRESENTATION\n"
    )

    f.write(
        "-" * 70 + "\n"
    )


    for allergen in TARGET_ALLERGENS:

        count = rare_class_presence[
            f"potential:{allergen}"
        ]

        f.write(
            f"{allergen}: {count}\n"
        )


# ============================================================
# END
# ============================================================

print("\n")
print("=" * 70)
print("GOLD TEST CANDIDATE SELECTION COMPLETE")
print("=" * 70)

print(
    f"\nBlinded annotation file:\n"
    f"{BLINDED_FILE}"
)

print(
    f"\nReference file:\n"
    f"{REFERENCE_FILE}"
)

print(
    f"\nSelection summary:\n"
    f"{SUMMARY_FILE}"
)

print("\n")
print("IMPORTANT:")
print(
    "gold_test_annotation.csv contains NO machine predictions."
)

print(
    "Manually review that file before using the reference file."
)

print("\n")
print("=" * 70)
print("END")
print("=" * 70)
