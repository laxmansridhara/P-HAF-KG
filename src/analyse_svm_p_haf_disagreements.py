import csv
from pathlib import Path
from collections import Counter


# ============================================================
# SVM ↔ P-HAF-KG DISAGREEMENT ANALYSIS
# ============================================================

csv.field_size_limit(10_000_000)


# ============================================================
# FILES
# ============================================================

TEST_FILE = Path(
    "data/processed/ml/test_candidate.csv"
)

SVM_PREDICTIONS_FILE = Path(
    "data/processed/ml/svm_model/"
    "silver_test_predictions.csv"
)

P_HAF_FILE = Path(
    "data/processed/scan/"
    "p_haf_kg_v2_1_large_scale_4535553.csv"
)

OUTPUT_DIR = Path(
    "data/processed/ml/disagreement"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR /
    "svm_p_haf_disagreements.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR /
    "disagreement_summary.txt"
)


# ============================================================
# LABELS
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
# HELPER
# ============================================================

def split_labels(text):
    """
    Convert a semicolon-separated allergen string
    into a set.
    """

    if not text:
        return set()

    return {
        value.strip()
        for value in text.split(";")
        if value.strip()
    }


def labels_to_string(labels):
    """
    Convert a set of labels into a stable string.
    """

    return ";".join(
        sorted(labels)
    )


# ============================================================
# STEP 1
# LOAD TEST DATA
# ============================================================

print("=" * 70)
print("SVM ↔ P-HAF-KG DISAGREEMENT ANALYSIS")
print("=" * 70)

print("\nLoading test candidate...")

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

        test_lookup[code] = {
            "product_name":
                row.get("product_name") or "",

            "ingredient_text":
                row.get("ingredient_text") or "",
        }


print(
    f"Test products loaded: "
    f"{len(test_lookup):,}"
)


# ============================================================
# STEP 2
# LOAD SVM PREDICTIONS
# ============================================================

print("\nLoading SVM predictions...")

svm_predictions = {}

with SVM_PREDICTIONS_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    prediction_rows = 0

    for row in reader:

        code = (
            row.get("product_code") or ""
        ).strip()

        if not code:
            continue

        predicted = set()

        for allergen in TARGET_ALLERGENS:

            value = (
                row.get(
                    f"pred_{allergen}"
                ) or "0"
            ).strip()

            if value == "1":
                predicted.add(allergen)

        svm_predictions[code] = predicted

        prediction_rows += 1


print(
    f"SVM predictions loaded: "
    f"{prediction_rows:,}"
)


# ============================================================
# STEP 3
# LOAD P-HAF-KG OUTPUT
# ============================================================

print("\nLoading P-HAF-KG output...")

p_haf_lookup = {}

with P_HAF_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    p_haf_rows = 0

    for row in reader:

        code = (
            row.get("code") or ""
        ).strip()

        if not code:
            continue

        # ----------------------------------------------------
        # Only retain products in the silver test candidate.
        # ----------------------------------------------------

        if code not in test_lookup:
            continue


        p_haf_lookup[code] = {
            "confirmed":
                split_labels(
                    row.get(
                        "confirmed_allergens"
                    ) or ""
                ),

            "potential":
                split_labels(
                    row.get(
                        "potential_allergens"
                    ) or ""
                ),

            "direct_matches":
                (
                    row.get(
                        "direct_matches"
                    ) or ""
                ),

            "precautionary_matches":
                (
                    row.get(
                        "precautionary_matches"
                    ) or ""
                ),

            "special_threshold_matches":
                (
                    row.get(
                        "special_threshold_matches"
                    ) or ""
                ),
        }

        p_haf_rows += 1


print(
    f"P-HAF-KG test rows matched: "
    f"{p_haf_rows:,}"
)


# ============================================================
# STEP 4
# COMPARE SYSTEMS
# ============================================================

print("\n")
print("=" * 70)
print("COMPARING SVM AND P-HAF-KG")
print("=" * 70)


results = []

agreement_count = 0
disagreement_count = 0


disagreement_type_counts = Counter()


for code, test_row in test_lookup.items():

    svm_labels = svm_predictions.get(
        code,
        set()
    )

    p_haf_data = p_haf_lookup.get(
        code
    )


    if p_haf_data is None:

        continue


    kg_confirmed = p_haf_data[
        "confirmed"
    ]

    kg_potential = p_haf_data[
        "potential"
    ]


    # --------------------------------------------------------
    # Compare SVM against CONFIRMED P-HAF-KG labels.
    # --------------------------------------------------------

    svm_only = (
        svm_labels -
        kg_confirmed
    )

    kg_only = (
        kg_confirmed -
        svm_labels
    )

    common = (
        svm_labels &
        kg_confirmed
    )


    exact_agreement = (
        svm_labels ==
        kg_confirmed
    )


    # --------------------------------------------------------
    # Categorise the row.
    # --------------------------------------------------------

    if exact_agreement:

        agreement = "exact_agreement"

        agreement_count += 1

    else:

        agreement = "disagreement"

        disagreement_count += 1


        # ----------------------------------------------------
        # More detailed disagreement type.
        # ----------------------------------------------------

        if svm_only and kg_only:

            disagreement_type = (
                "both_sides_different"
            )

        elif svm_only:

            disagreement_type = (
                "svm_only_prediction"
            )

        elif kg_only:

            disagreement_type = (
                "kg_only_prediction"
            )

        else:

            disagreement_type = (
                "unknown"
            )


        disagreement_type_counts[
            disagreement_type
        ] += 1


    # --------------------------------------------------------
    # Potential overlap
    # --------------------------------------------------------

    svm_potential_overlap = (
        svm_labels &
        kg_potential
    )


    results.append({

        "product_code":
            code,

        "product_name":
            test_row[
                "product_name"
            ],

        "ingredient_text":
            test_row[
                "ingredient_text"
            ],

        "svm_predicted":
            labels_to_string(
                svm_labels
            ),

        "p_haf_confirmed":
            labels_to_string(
                kg_confirmed
            ),

        "p_haf_potential":
            labels_to_string(
                kg_potential
            ),

        "common_labels":
            labels_to_string(
                common
            ),

        "svm_only":
            labels_to_string(
                svm_only
            ),

        "kg_only":
            labels_to_string(
                kg_only
            ),

        "svm_potential_overlap":
            labels_to_string(
                svm_potential_overlap
            ),

        "agreement":
            agreement,

        "disagreement_type":
            (
                disagreement_type
                if not exact_agreement
                else ""
            ),

        "direct_matches":
            p_haf_data[
                "direct_matches"
            ],

        "precautionary_matches":
            p_haf_data[
                "precautionary_matches"
            ],

        "special_threshold_matches":
            p_haf_data[
                "special_threshold_matches"
            ],
    })


# ============================================================
# STEP 5
# SAVE COMPLETE COMPARISON
# ============================================================

fieldnames = [
    "product_code",
    "product_name",
    "ingredient_text",
    "svm_predicted",
    "p_haf_confirmed",
    "p_haf_potential",
    "common_labels",
    "svm_only",
    "kg_only",
    "svm_potential_overlap",
    "agreement",
    "disagreement_type",
    "direct_matches",
    "precautionary_matches",
    "special_threshold_matches",
]


print("\nSaving comparison file...")

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        results
    )


# ============================================================
# STEP 6
# OVERALL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("OVERALL COMPARISON")
print("=" * 70)


total_compared = len(results)


print(
    f"Products compared: "
    f"{total_compared:,}"
)

print(
    f"Exact agreement:    "
    f"{agreement_count:,}"
)

print(
    f"Disagreement:       "
    f"{disagreement_count:,}"
)


if total_compared:

    agreement_percentage = (
        agreement_count /
        total_compared *
        100
    )

    disagreement_percentage = (
        disagreement_count /
        total_compared *
        100
    )

    print(
        f"Agreement rate:     "
        f"{agreement_percentage:.2f}%"
    )

    print(
        f"Disagreement rate:  "
        f"{disagreement_percentage:.2f}%"
    )


# ============================================================
# STEP 7
# DISAGREEMENT TYPES
# ============================================================

print("\n")
print("=" * 70)
print("DISAGREEMENT TYPES")
print("=" * 70)


for category, count in (
    disagreement_type_counts
    .most_common()
):

    print(
        f"{category:30s} "
        f"{count:8,}"
    )


# ============================================================
# STEP 8
# PER-ALLERGEN DISAGREEMENTS
# ============================================================

svm_only_counts = Counter()
kg_only_counts = Counter()

potential_overlap_counts = Counter()


for result in results:

    for allergen in split_labels(
        result["svm_only"]
    ):

        svm_only_counts[
            allergen
        ] += 1


    for allergen in split_labels(
        result["kg_only"]
    ):

        kg_only_counts[
            allergen
        ] += 1


    for allergen in split_labels(
        result[
            "svm_potential_overlap"
        ]
    ):

        potential_overlap_counts[
            allergen
        ] += 1


print("\n")
print("=" * 70)
print("SVM-ONLY PREDICTIONS")
print("=" * 70)

for allergen, count in (
    svm_only_counts.most_common()
):

    print(
        f"{allergen:20s} "
        f"{count:8,}"
    )


print("\n")
print("=" * 70)
print("P-HAF-KG-ONLY CONFIRMED PREDICTIONS")
print("=" * 70)

for allergen, count in (
    kg_only_counts.most_common()
):

    print(
        f"{allergen:20s} "
        f"{count:8,}"
    )


print("\n")
print("=" * 70)
print("SVM PREDICTION + P-HAF POTENTIAL EVIDENCE")
print("=" * 70)

for allergen, count in (
    potential_overlap_counts.most_common()
):

    print(
        f"{allergen:20s} "
        f"{count:8,}"
    )


# ============================================================
# STEP 9
# IDENTIFY INTERESTING CASES
# ============================================================

interesting = []


for result in results:

    svm_only = split_labels(
        result["svm_only"]
    )

    kg_only = split_labels(
        result["kg_only"]
    )

    potential_overlap = split_labels(
        result[
            "svm_potential_overlap"
        ]
    )


    # --------------------------------------------------------
    # Priority 1:
    # KG confirmed but SVM missed.
    # --------------------------------------------------------

    if kg_only:

        priority = 1

    # --------------------------------------------------------
    # Priority 2:
    # SVM prediction conflicts with KG potential evidence.
    # --------------------------------------------------------

    elif potential_overlap:

        priority = 2

    # --------------------------------------------------------
    # Priority 3:
    # SVM predicts something KG does not support.
    # --------------------------------------------------------

    elif svm_only:

        priority = 3

    else:

        continue


    interesting.append(
        (
            priority,
            result
        )
    )


interesting.sort(
    key=lambda x: x[0]
)


INTERESTING_FILE = (
    OUTPUT_DIR /
    "priority_disagreements.csv"
)


with INTERESTING_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for _, result in interesting:

        writer.writerow(result)


# ============================================================
# STEP 10
# SUMMARY FILE
# ============================================================

with SUMMARY_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "P-HAF-KG V2.1 / SVM DISAGREEMENT ANALYSIS\n"
    )

    f.write(
        "=" * 70 + "\n\n"
    )

    f.write(
        f"Products compared: "
        f"{total_compared:,}\n"
    )

    f.write(
        f"Exact agreement: "
        f"{agreement_count:,}\n"
    )

    f.write(
        f"Disagreement: "
        f"{disagreement_count:,}\n"
    )

    if total_compared:

        f.write(
            f"Agreement rate: "
            f"{agreement_count / total_compared * 100:.2f}%\n"
        )

        f.write(
            f"Disagreement rate: "
            f"{disagreement_count / total_compared * 100:.2f}%\n"
        )


    f.write("\nDISAGREEMENT TYPES\n")
    f.write("-" * 70 + "\n")

    for category, count in (
        disagreement_type_counts
        .most_common()
    ):

        f.write(
            f"{category}: {count:,}\n"
        )


# ============================================================
# END
# ============================================================

print("\n")
print("=" * 70)
print("DISAGREEMENT ANALYSIS COMPLETE")
print("=" * 70)

print(
    f"\nComparison saved to:\n{OUTPUT_FILE}"
)

print(
    f"\nPriority cases saved to:\n"
    f"{INTERESTING_FILE}"
)

print(
    f"\nSummary saved to:\n"
    f"{SUMMARY_FILE}"
)

print("\n")
print("=" * 70)
print("END")
print("=" * 70)
