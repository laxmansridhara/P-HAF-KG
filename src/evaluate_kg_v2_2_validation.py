import csv
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
)


# ============================================================
# P-HAF-KG V2.1 vs V2.2 DEVELOPMENT EVALUATION
# Validation set only — NOT the 500-product gold test
# ============================================================

csv.field_size_limit(10_000_000)

BASE = Path(".")

VALIDATION_FILE = (
    BASE / "data/processed/ml/validation.csv"
)

KG_SOURCE = (
    BASE /
    "src/p_haf_kg_evidence_14_v2_1_final_dev.py"
)

V21_KB = (
    BASE /
    "data/processed/ingredient_allergen_knowledge_14.csv"
)

V22_KB = (
    BASE /
    "data/processed/ingredient_allergen_knowledge_14_v2_2_dev.csv"
)

OUTPUT_DIR = (
    BASE /
    "data/processed/ml/v2_2_development"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TARGET CLASSES
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
# OUTPUTS
# ============================================================

PREDICTIONS_OUTPUT = (
    OUTPUT_DIR /
    "v2_1_v2_2_validation_predictions.csv"
)

METRICS_OUTPUT = (
    OUTPUT_DIR /
    "v2_1_v2_2_validation_metrics.json"
)

PER_CLASS_OUTPUT = (
    OUTPUT_DIR /
    "v2_1_v2_2_validation_per_allergen.csv"
)

SUMMARY_OUTPUT = (
    OUTPUT_DIR /
    "v2_1_v2_2_validation_summary.txt"
)


# ============================================================
# HELPERS
# ============================================================

def parse_labels(value):

    if value is None:
        return set()

    value = str(value).strip()

    if not value:
        return set()

    if value.lower() == "nan":
        return set()

    return {
        x.strip().lower()
        for x in value.split(";")
        if x.strip()
        and x.strip().lower() in TARGET_ALLERGENS
    }


def labels_to_string(labels):

    labels = set(labels)

    return ";".join(
        allergen
        for allergen in TARGET_ALLERGENS
        if allergen in labels
    )


def calculate_metrics(
    y_true,
    y_pred,
):

    return {

        "micro_precision":
            float(
                precision_score(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0,
                )
            ),

        "micro_recall":
            float(
                recall_score(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0,
                )
            ),

        "micro_f1":
            float(
                f1_score(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0,
                )
            ),

        "macro_precision":
            float(
                precision_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0,
                )
            ),

        "macro_recall":
            float(
                recall_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0,
                )
            ),

        "macro_f1":
            float(
                f1_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0,
                )
            ),

        "hamming_loss":
            float(
                hamming_loss(
                    y_true,
                    y_pred,
                )
            ),

        "exact_match":
            float(
                np.mean(
                    np.all(
                        y_true == y_pred,
                        axis=1,
                    )
                )
            ),
    }


# ============================================================
# LOAD VALIDATION SET
# ============================================================

print("=" * 80)
print("P-HAF-KG V2.1 vs V2.2 — VALIDATION DEVELOPMENT EVALUATION")
print("=" * 80)

start = time.time()

validation_df = pd.read_csv(
    VALIDATION_FILE,
    dtype=str,
).fillna("")

if len(validation_df) != 14814:

    raise ValueError(
        f"Expected 14,814 validation rows; "
        f"found {len(validation_df)}."
    )


required_columns = [
    "product_code",
    "product_name",
    "ingredient_text",
    "confirmed_allergens",
    "potential_allergens",
]

missing = [
    col
    for col in required_columns
    if col not in validation_df.columns
]

if missing:

    raise ValueError(
        "Missing validation columns: "
        + ", ".join(missing)
    )


texts = (
    validation_df["ingredient_text"]
    .astype(str)
    .tolist()
)

gold_sets = [
    parse_labels(value)
    for value in validation_df[
        "confirmed_allergens"
    ]
]


# ============================================================
# LOAD EXACT V2.1 FUNCTIONS
# ============================================================

print("\nLoading exact V2.1 prediction logic...")

source_text = KG_SOURCE.read_text(
    encoding="utf-8"
)

cut_marker = "# 9. LOAD TEST DATA"

if cut_marker not in source_text:

    raise RuntimeError(
        "Could not locate V2.1 source boundary."
    )

source_prefix = source_text.split(
    cut_marker,
    1
)[0]


namespace = {
    "__name__": "v2_2_validation"
}

exec(
    compile(
        source_prefix,
        str(KG_SOURCE),
        "exec",
    ),
    namespace,
)


normalize_text = namespace[
    "normalize_text"
]

split_evidence_segments = namespace[
    "split_evidence_segments"
]

is_precautionary_sentence = namespace[
    "is_precautionary_sentence"
]

is_excluded_match = namespace[
    "is_excluded_match"
]


# ============================================================
# KNOWLEDGE LOADER
# ============================================================

def load_knowledge(path):

    knowledge = []

    seen = set()

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:

        rows = csv.DictReader(f)

        for item in rows:

            ingredient_original = (
                (item.get("ingredient") or "")
                .strip()
            )

            ingredient = normalize_text(
                ingredient_original
            )

            allergen = (
                (item.get("allergen") or "")
                .strip()
                .lower()
            )

            evidence_type = (
                (item.get("evidence_type") or "")
                .strip()
            )

            confidence = (
                (item.get("confidence") or "")
                .strip()
            )

            language = (
                (item.get("language") or "")
                .strip()
            )

            if not ingredient:
                continue

            if allergen not in TARGET_ALLERGENS:
                continue

            key = (
                ingredient,
                allergen,
                evidence_type,
                language,
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


    knowledge.sort(
        key=lambda x: len(
            x["ingredient"]
        ),
        reverse=True,
    )

    return knowledge


# ============================================================
# EXACT V2.1-STYLE PREDICTOR
# ============================================================

def predict_with_knowledge(
    original_text,
    knowledge,
):

    confirmed = set()
    potential = set()

    direct_matches = set()
    precautionary_matches = set()
    special_threshold_matches = set()


    segments = split_evidence_segments(
        original_text
    )


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


        for item in knowledge:

            ingredient = item["ingredient"]
            allergen = item["allergen"]
            evidence_type = item[
                "evidence_type"
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
                normalized_segment,
            ):

                if is_excluded_match(
                    ingredient,
                    allergen,
                    normalized_segment,
                    match.start(),
                    match.end(),
                ):

                    continue


                match_string = (
                    f"{item['ingredient_original']}"
                    f" -> "
                    f"{allergen}"
                )


                if (
                    evidence_type
                    == "special_threshold"
                ):

                    special_threshold_matches.add(
                        match_string
                    )

                    continue


                if precautionary_segment:

                    potential.add(
                        allergen
                    )

                    precautionary_matches.add(
                        match_string
                    )

                else:

                    confirmed.add(
                        allergen
                    )

                    direct_matches.add(
                        match_string
                    )


    potential -= confirmed


    return (
        confirmed,
        potential,
        direct_matches,
        precautionary_matches,
        special_threshold_matches,
    )


# ============================================================
# LOAD BOTH KNOWLEDGE BASES
# ============================================================

print(
    f"\nV2.1 knowledge base: {V21_KB}"
)

knowledge_v21 = load_knowledge(
    V21_KB
)

print(
    f"V2.1 relationships used: "
    f"{len(knowledge_v21):,}"
)


print(
    f"\nV2.2 knowledge base: {V22_KB}"
)

knowledge_v22 = load_knowledge(
    V22_KB
)

print(
    f"V2.2 relationships used: "
    f"{len(knowledge_v22):,}"
)


# ============================================================
# RUN V2.1 AND V2.2
# ============================================================

print("\nRunning V2.1 and V2.2 over validation set...")

v21_sets = []
v21_potential_sets = []

v22_sets = []
v22_potential_sets = []

prediction_rows = []


for i, text in enumerate(texts):

    v21 = predict_with_knowledge(
        text,
        knowledge_v21,
    )

    v22 = predict_with_knowledge(
        text,
        knowledge_v22,
    )


    v21_confirmed = v21[0]
    v21_potential = v21[1]

    v22_confirmed = v22[0]
    v22_potential = v22[1]


    v21_sets.append(
        v21_confirmed
    )

    v21_potential_sets.append(
        v21_potential
    )

    v22_sets.append(
        v22_confirmed
    )

    v22_potential_sets.append(
        v22_potential
    )


    prediction_rows.append({

        "product_code":
            validation_df.iloc[i][
                "product_code"
            ],

        "product_name":
            validation_df.iloc[i][
                "product_name"
            ],

        "ingredient_text":
            text,

        "gold_confirmed_allergens":
            labels_to_string(
                gold_sets[i]
            ),

        "v21_confirmed_allergens":
            labels_to_string(
                v21_confirmed
            ),

        "v21_potential_allergens":
            labels_to_string(
                v21_potential
            ),

        "v22_confirmed_allergens":
            labels_to_string(
                v22_confirmed
            ),

        "v22_potential_allergens":
            labels_to_string(
                v22_potential
            ),

    })


    if (
        (i + 1) % 1000 == 0
        or i + 1 == len(texts)
    ):

        print(
            f"Processed "
            f"{i + 1:,}/{len(texts):,}"
        )


prediction_df = pd.DataFrame(
    prediction_rows
)

prediction_df.to_csv(
    PREDICTIONS_OUTPUT,
    index=False,
)


# ============================================================
# BUILD MATRICES
# ============================================================

Y_gold = np.zeros(
    (
        len(texts),
        len(TARGET_ALLERGENS)
    ),
    dtype=int,
)

Y_v21 = np.zeros_like(
    Y_gold
)

Y_v22 = np.zeros_like(
    Y_gold
)


for i in range(
    len(texts)
):

    for j, allergen in enumerate(
        TARGET_ALLERGENS
    ):

        if allergen in gold_sets[i]:
            Y_gold[i, j] = 1

        if allergen in v21_sets[i]:
            Y_v21[i, j] = 1

        if allergen in v22_sets[i]:
            Y_v22[i, j] = 1


# ============================================================
# METRICS
# ============================================================

v21_metrics = calculate_metrics(
    Y_gold,
    Y_v21,
)

v22_metrics = calculate_metrics(
    Y_gold,
    Y_v22,
)


# ============================================================
# PER-CLASS METRICS
# ============================================================

per_class_rows = []


for j, allergen in enumerate(
    TARGET_ALLERGENS
):

    gold_col = Y_gold[:, j]

    v21_col = Y_v21[:, j]

    v22_col = Y_v22[:, j]


    for model_name, pred_col in [
        ("P-HAF-KG V2.1", v21_col),
        ("P-HAF-KG V2.2", v22_col),
    ]:

        per_class_rows.append({

            "model":
                model_name,

            "allergen":
                allergen,

            "support":
                int(gold_col.sum()),

            "precision":
                float(
                    precision_score(
                        gold_col,
                        pred_col,
                        zero_division=0,
                    )
                ),

            "recall":
                float(
                    recall_score(
                        gold_col,
                        pred_col,
                        zero_division=0,
                    )
                ),

            "f1":
                float(
                    f1_score(
                        gold_col,
                        pred_col,
                        zero_division=0,
                    )
                ),

        })


per_class_df = pd.DataFrame(
    per_class_rows
)

per_class_df.to_csv(
    PER_CLASS_OUTPUT,
    index=False,
)


# ============================================================
# CHANGE ANALYSIS
# ============================================================

improved_products = 0
worsened_products = 0
unchanged_products = 0

v22_new_confirmed = 0
v22_removed_confirmed = 0

v22_recovered_gold = 0
v22_new_false_positive = 0


for i in range(
    len(texts)
):

    v21 = v21_sets[i]
    v22 = v22_sets[i]
    gold = gold_sets[i]


    v21_exact = (
        v21 == gold
    )

    v22_exact = (
        v22 == gold
    )


    if v22_exact and not v21_exact:
        improved_products += 1

    elif (
        v21_exact
        and not v22_exact
    ):
        worsened_products += 1

    else:
        unchanged_products += 1


    newly_confirmed = (
        v22 - v21
    )

    removed_confirmed = (
        v21 - v22
    )


    v22_new_confirmed += (
        len(newly_confirmed)
    )

    v22_removed_confirmed += (
        len(removed_confirmed)
    )


    for allergen in newly_confirmed:

        if allergen in gold:
            v22_recovered_gold += 1
        else:
            v22_new_false_positive += 1


# ============================================================
# METRICS DELTA
# ============================================================

delta = {

    "micro_f1":
        v22_metrics["micro_f1"]
        - v21_metrics["micro_f1"],

    "macro_f1":
        v22_metrics["macro_f1"]
        - v21_metrics["macro_f1"],

    "exact_match":
        v22_metrics["exact_match"]
        - v21_metrics["exact_match"],

    "hamming_loss":
        v22_metrics["hamming_loss"]
        - v21_metrics["hamming_loss"],

}


# ============================================================
# SAVE METRICS
# ============================================================

elapsed = time.time() - start


metrics = {

    "dataset":
        "14,814-product validation development set",

    "validation_products":
        len(texts),

    "non_empty_ingredient_text":
        int(
            sum(
                bool(str(x).strip())
                for x in texts
            )
        ),

    "v21_relationships":
        len(knowledge_v21),

    "v22_relationships":
        len(knowledge_v22),

    "v21":
        v21_metrics,

    "v22":
        v22_metrics,

    "delta_v22_minus_v21":
        delta,

    "product_level_change": {

        "improved":
            improved_products,

        "worsened":
            worsened_products,

        "unchanged":
            unchanged_products,

    },

    "prediction_change": {

        "new_v22_confirmed_allergen_instances":
            v22_new_confirmed,

        "removed_v22_confirmed_allergen_instances":
            v22_removed_confirmed,

        "new_v22_confirmed_instances_matching_gold":
            v22_recovered_gold,

        "new_v22_confirmed_false_positive_instances":
            v22_new_false_positive,

    },

    "v22_change_set":
        [
            "soya -> soy",
            "blé -> wheat_gluten",
            "céleri -> celery",
            "sésame -> sesame",
            "poisson -> fish",
            "poissons -> fish",
            "mollusque -> molluscs",
            "mollusques -> molluscs",
            "crustacé -> crustaceans",
            "crustacés -> crustaceans",
            "amandes -> tree_nut",
            "noisettes -> tree_nut",
            "haselnüsse -> tree_nut",
            "erdnüsse -> peanut",
        ],

    "evaluation_purpose":
        "Development comparison only. "
        "The independent 500-product gold "
        "evaluation remains frozen and was "
        "not used to tune V2.2.",

    "elapsed_seconds":
        elapsed,
}


with METRICS_OUTPUT.open(
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        metrics,
        f,
        indent=2,
    )


# ============================================================
# HUMAN-READABLE SUMMARY
# ============================================================

with SUMMARY_OUTPUT.open(
    "w",
    encoding="utf-8",
) as f:

    f.write(
        "P-HAF-KG V2.1 vs V2.2\n"
    )

    f.write(
        "VALIDATION DEVELOPMENT EVALUATION\n"
    )

    f.write("=" * 70 + "\n\n")

    f.write(
        f"Validation products: {len(texts):,}\n"
    )

    f.write(
        f"V2.1 relationships: {len(knowledge_v21):,}\n"
    )

    f.write(
        f"V2.2 relationships: {len(knowledge_v22):,}\n\n"
    )


    for name, result in [
        ("P-HAF-KG V2.1", v21_metrics),
        ("P-HAF-KG V2.2", v22_metrics),
    ]:

        f.write(
            f"{name}\n"
        )

        f.write("-" * 50 + "\n")

        f.write(
            f"Micro Precision: {result['micro_precision']:.4f}\n"
        )

        f.write(
            f"Micro Recall:    {result['micro_recall']:.4f}\n"
        )

        f.write(
            f"Micro F1:        {result['micro_f1']:.4f}\n"
        )

        f.write(
            f"Macro Precision: {result['macro_precision']:.4f}\n"
        )

        f.write(
            f"Macro Recall:    {result['macro_recall']:.4f}\n"
        )

        f.write(
            f"Macro F1:        {result['macro_f1']:.4f}\n"
        )

        f.write(
            f"Hamming Loss:    {result['hamming_loss']:.4f}\n"
        )

        f.write(
            f"Exact Match:     {result['exact_match']:.4f}\n\n"
        )


    f.write("V2.2 DELTA\n")
    f.write("-" * 50 + "\n")

    for key, value in delta.items():
        f.write(
            f"{key}: {value:+.6f}\n"
        )

    f.write("\nProduct-level change\n")
    f.write("-" * 50 + "\n")

    f.write(
        f"Improved: {improved_products:,}\n"
    )

    f.write(
        f"Worsened: {worsened_products:,}\n"
    )

    f.write(
        f"Unchanged: {unchanged_products:,}\n"
    )

    f.write("\nPrediction change\n")
    f.write("-" * 50 + "\n")

    f.write(
        f"New V2.2 confirmed: "
        f"{v22_new_confirmed:,}\n"
    )

    f.write(
        f"New confirmed matching gold: "
        f"{v22_recovered_gold:,}\n"
    )

    f.write(
        f"New confirmed false positives: "
        f"{v22_new_false_positive:,}\n"
    )


# ============================================================
# CONSOLE
# ============================================================

print("\n" + "=" * 80)
print("V2.1 vs V2.2 VALIDATION RESULTS")
print("=" * 80)

for name, result in [
    ("P-HAF-KG V2.1", v21_metrics),
    ("P-HAF-KG V2.2", v22_metrics),
]:

    print(f"\n{name}")

    print(
        f"  Micro Precision: {result['micro_precision']:.4f}"
    )

    print(
        f"  Micro Recall:    {result['micro_recall']:.4f}"
    )

    print(
        f"  Micro F1:        {result['micro_f1']:.4f}"
    )

    print(
        f"  Macro F1:        {result['macro_f1']:.4f}"
    )

    print(
        f"  Hamming Loss:    {result['hamming_loss']:.4f}"
    )

    print(
        f"  Exact Match:     {result['exact_match']:.4f}"
    )


print("\nDELTA — V2.2 minus V2.1")

print(
    f"Micro F1:     {delta['micro_f1']:+.6f}"
)

print(
    f"Macro F1:     {delta['macro_f1']:+.6f}"
)

print(
    f"Exact Match:  {delta['exact_match']:+.6f}"
)

print(
    f"Hamming Loss: {delta['hamming_loss']:+.6f}"
)


print("\nPRODUCT-LEVEL CHANGE")

print(
    f"Improved:   {improved_products:,}"
)

print(
    f"Worsened:   {worsened_products:,}"
)

print(
    f"Unchanged:  {unchanged_products:,}"
)


print("\nPREDICTION CHANGE")

print(
    f"New V2.2 confirmed: "
    f"{v22_new_confirmed:,}"
)

print(
    f"New confirmed matching gold: "
    f"{v22_recovered_gold:,}"
)

print(
    f"New confirmed false positives: "
    f"{v22_new_false_positive:,}"
)


print("\nSaved:")
print(PREDICTIONS_OUTPUT)
print(METRICS_OUTPUT)
print(PER_CLASS_OUTPUT)
print(SUMMARY_OUTPUT)

print(
    f"\nElapsed: {elapsed:.2f} seconds"
)

print(
    "\nV2.2 DEVELOPMENT EVALUATION COMPLETE."
)
