import csv
from pathlib import Path


TEST_FILE = Path(
    "data/processed/test.csv"
)

PREDICTION_FILE = Path(
    "data/processed/p_haf_kg_evidence_14_v2.csv"
)

OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_14_v2_error_analysis.csv"
)


ALLERGENS = [
    "celery",
    "wheat_gluten",
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
    "sulphites",
    "tree_nut",
]


def split_labels(value):

    return set(
        x.strip()
        for x in str(value).split(";")
        if x.strip()
    )


# ============================================================
# LOAD TEST DATA
# ============================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


# ============================================================
# LOAD PREDICTIONS
# ============================================================

with PREDICTION_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    prediction_rows = {
        row["code"]: row
        for row in csv.DictReader(f)
    }


# ============================================================
# ANALYSIS
# ============================================================

results = []

exact_matches = 0
non_exact = 0


tp_counts = {
    allergen: 0
    for allergen in ALLERGENS
}

fp_counts = {
    allergen: 0
    for allergen in ALLERGENS
}

fn_counts = {
    allergen: 0
    for allergen in ALLERGENS
}


for code, test_row in test_rows.items():

    prediction_row = prediction_rows.get(
        code
    )

    if prediction_row is None:
        continue


    ground_truth = split_labels(
        test_row[
            "confirmed_allergens"
        ]
    )

    prediction = split_labels(
        prediction_row[
            "confirmed_allergens"
        ]
    )


    potential = split_labels(
        prediction_row[
            "potential_allergens"
        ]
    )


    direct = prediction_row[
        "direct_matches"
    ]

    precautionary = prediction_row[
        "precautionary_matches"
    ]

    special_threshold = prediction_row[
        "special_threshold_matches"
    ]


    # --------------------------------------------------------
    # PRODUCT LEVEL
    # --------------------------------------------------------

    if ground_truth == prediction:

        exact_matches += 1

    else:

        non_exact += 1


    true_positive = (
        ground_truth
        & prediction
    )

    false_positive = (
        prediction
        - ground_truth
    )

    false_negative = (
        ground_truth
        - prediction
    )


    # --------------------------------------------------------
    # ALLERGEN COUNTS
    # --------------------------------------------------------

    for allergen in true_positive:

        if allergen in tp_counts:

            tp_counts[
                allergen
            ] += 1


    for allergen in false_positive:

        if allergen in fp_counts:

            fp_counts[
                allergen
            ] += 1


    for allergen in false_negative:

        if allergen in fn_counts:

            fn_counts[
                allergen
            ] += 1


    # --------------------------------------------------------
    # SAVE ONLY NON-EXACT CASES
    # --------------------------------------------------------

    if ground_truth != prediction:

        results.append({

            "code":
                code,

            "product_name":
                test_row[
                    "product_name"
                ],

            "ground_truth":
                ";".join(
                    sorted(
                        ground_truth
                    )
                ),

            "prediction":
                ";".join(
                    sorted(
                        prediction
                    )
                ),

            "potential":
                ";".join(
                    sorted(
                        potential
                    )
                ),

            "true_positive":
                ";".join(
                    sorted(
                        true_positive
                    )
                ),

            "false_positive":
                ";".join(
                    sorted(
                        false_positive
                    )
                ),

            "false_negative":
                ";".join(
                    sorted(
                        false_negative
                    )
                ),

            "direct_matches":
                direct,

            "precautionary_matches":
                precautionary,

            "special_threshold_matches":
                special_threshold,

        })


# ============================================================
# SAVE ERROR ANALYSIS
# ============================================================

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    fieldnames = [

        "code",
        "product_name",
        "ground_truth",
        "prediction",
        "potential",
        "true_positive",
        "false_positive",
        "false_negative",
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
# PRINT REPORT
# ============================================================

print(
    "===== P-HAF-KG V2 ERROR ANALYSIS ====="
)

print(
    "Test products:",
    len(test_rows)
)

print(
    "Exact matches:",
    exact_matches
)

print(
    "Non-exact:",
    non_exact
)


print(
    "\n===== ALLERGEN ERROR COUNTS ====="
)

for allergen in ALLERGENS:

    print(
        f"{allergen:<18}"
        f"TP={tp_counts[allergen]} "
        f"FP={fp_counts[allergen]} "
        f"FN={fn_counts[allergen]}"
    )


print(
    "\n===== PRODUCT-LEVEL ERRORS ====="
)


for row in results:

    print(
        "\nCode:",
        row["code"]
    )

    print(
        "Product:",
        row["product_name"]
    )

    print(
        "Ground truth:",
        row["ground_truth"]
    )

    print(
        "Prediction:",
        row["prediction"]
    )

    print(
        "Potential:",
        row["potential"]
    )

    print(
        "True positive:",
        row["true_positive"]
    )

    print(
        "False positive:",
        row["false_positive"]
    )

    print(
        "False negative:",
        row["false_negative"]
    )

    print(
        "Direct evidence:",
        row["direct_matches"]
    )

    print(
        "Precautionary evidence:",
        row["precautionary_matches"]
    )

    print(
        "Special threshold:",
        row["special_threshold_matches"]
    )


print(
    "\nSaved:"
)

print(
    OUTPUT_FILE
)
