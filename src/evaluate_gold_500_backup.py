import csv
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
)


# ============================================================
# P-HAF-KG V2.1 — FINAL 500-PRODUCT GOLD EVALUATION
# ============================================================

csv.field_size_limit(10_000_000)


# ============================================================
# PATHS
# ============================================================

TRAIN_FILE = Path(
    "data/processed/ml/train.csv"
)

GOLD_FILE = Path(
    "data/processed/ml/gold_test/gold_test_annotation_completed.csv"
)

OUTPUT_DIR = Path(
    "data/processed/ml/gold_test"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


SVM_OUTPUT = (
    OUTPUT_DIR /
    "svm_gold_predictions.csv"
)

KG_OUTPUT = (
    OUTPUT_DIR /
    "p_haf_kg_gold_predictions.csv"
)

HYBRID_OUTPUT = (
    OUTPUT_DIR /
    "hybrid_gold_predictions.csv"
)

METRICS_OUTPUT = (
    OUTPUT_DIR /
    "gold_500_final_metrics.json"
)

PER_CLASS_OUTPUT = (
    OUTPUT_DIR /
    "gold_500_per_allergen_metrics.csv"
)

SUMMARY_OUTPUT = (
    OUTPUT_DIR /
    "gold_500_evaluation_summary.txt"
)


# ============================================================
# EXACT 13 ALLERGEN CLASSES
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
# HELPERS
# ============================================================

def parse_labels(value):
    """
    Parse semicolon-separated allergen labels.
    """

    if value is None:
        return set()

    value = str(value).strip()

    if not value or value.lower() == "nan":
        return set()

    return {
        x.strip().lower()
        for x in value.split(";")
        if x.strip()
    }


def labels_to_string(labels):
    """
    Save labels in fixed project order.
    """

    label_set = set(labels)

    return ";".join(
        allergen
        for allergen in TARGET_ALLERGENS
        if allergen in label_set
    )


def normalize_text(text):
    """
    Lightweight normalization for KG matching.

    The gold evaluation uses ingredient text only.
    """

    if text is None:
        return ""

    text = str(text).lower()

    text = text.replace("’", "'")
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# LOAD TRAINING DATA
# ============================================================

print("=" * 80)
print("P-HAF-KG V2.1 — FINAL 500-PRODUCT GOLD EVALUATION")
print("=" * 80)

start_time = time.time()

print("\nLoading SVM training data...")
print(TRAIN_FILE)

train_df = pd.read_csv(
    TRAIN_FILE
)

print(
    f"Training rows loaded: {len(train_df):,}"
)


# ============================================================
# LOAD GOLD DATA
# ============================================================

print("\nLoading gold annotation file...")
print(GOLD_FILE)

gold_df = pd.read_csv(
    GOLD_FILE
)

print(
    f"Gold rows loaded: {len(gold_df):,}"
)


if len(gold_df) != 500:
    raise ValueError(
        f"Expected exactly 500 gold products, "
        f"but found {len(gold_df)}."
    )


required_gold_columns = [
    "gold_id",
    "product_code",
    "product_name",
    "ingredient_text",
    "gold_confirmed_allergens",
    "gold_potential_allergens",
    "gold_evidence_level",
    "review_status",
]


missing_columns = [
    col
    for col in required_gold_columns
    if col not in gold_df.columns
]


if missing_columns:
    raise ValueError(
        "Missing gold columns: "
        + ", ".join(missing_columns)
    )


# ============================================================
# CHECK GOLD REVIEW STATUS
# ============================================================

review_statuses = (
    gold_df["review_status"]
    .fillna("")
    .astype(str)
    .str.lower()
    .str.strip()
)


if not (review_statuses == "reviewed").all():
    bad = int(
        (review_statuses != "reviewed").sum()
    )

    raise ValueError(
        f"{bad} gold rows are not marked 'reviewed'."
    )


# ============================================================
# GOLD LABEL MATRICES
# ============================================================

gold_confirmed_labels = [
    parse_labels(x)
    for x in gold_df[
        "gold_confirmed_allergens"
    ]
]

gold_potential_labels = [
    parse_labels(x)
    for x in gold_df[
        "gold_potential_allergens"
    ]
]


mlb = MultiLabelBinarizer(
    classes=TARGET_ALLERGENS
)

Y_gold = mlb.fit_transform(
    gold_confirmed_labels
)


# ============================================================
# TRAINING TEXT / LABELS
# EXACTLY MATCHING train_svm_multilabel.py
# ============================================================

train_text = (
    train_df["ingredient_text"]
    .fillna("")
    .astype(str)
    .str.strip()
)

train_labels = [
    parse_labels(x)
    for x in train_df[
        "confirmed_allergens"
    ]
]


valid_indices = [
    i
    for i, text in enumerate(train_text)
    if text
]


X_train_text = [
    train_text.iloc[i]
    for i in valid_indices
]

y_train_labels = [
    train_labels[i]
    for i in valid_indices
]


Y_train = mlb.transform(
    y_train_labels
)


print(
    f"\nUsable SVM training samples: "
    f"{len(X_train_text):,}"
)


# ============================================================
# TF-IDF
# EXACT TRAINING CONFIGURATION
# ============================================================

print("\n" + "=" * 80)
print("TRAINING TF-IDF + LINEAR SVM")
print("=" * 80)

vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.98,
    sublinear_tf=True,
    max_features=100_000,
)


print("Fitting TF-IDF...")

X_train = vectorizer.fit_transform(
    X_train_text
)

print(
    f"Training TF-IDF matrix: "
    f"{X_train.shape}"
)


# ============================================================
# TRAIN LINEAR SVM
# EXACT TRAINING CONFIGURATION
# ============================================================

classifier = OneVsRestClassifier(

    LinearSVC(
        C=1.0,
        max_iter=5000,
    ),

    n_jobs=1,
)


print("Training Linear SVM...")

classifier.fit(
    X_train,
    Y_train
)

print("SVM training complete.")


# ============================================================
# GOLD TEXT
# ============================================================

gold_text = (
    gold_df["ingredient_text"]
    .fillna("")
    .astype(str)
    .tolist()
)


# ============================================================
# SVM GOLD PREDICTIONS
# ============================================================

print("\nGenerating SVM predictions for 500 gold products...")

X_gold = vectorizer.transform(
    gold_text
)

Y_svm = classifier.predict(
    X_gold
)


svm_label_sets = []

for row in Y_svm:
    svm_label_sets.append(
        {
            TARGET_ALLERGENS[j]
            for j, value in enumerate(row)
            if value == 1
        }
    )


# ============================================================
# SAVE SVM PREDICTIONS
# ============================================================

svm_rows = []

for i in range(len(gold_df)):

    svm_rows.append({

        "gold_id":
            gold_df.iloc[i]["gold_id"],

        "product_code":
            gold_df.iloc[i]["product_code"],

        "product_name":
            gold_df.iloc[i]["product_name"],

        "ingredient_text":
            gold_df.iloc[i]["ingredient_text"],

        "gold_confirmed_allergens":
            labels_to_string(
                gold_confirmed_labels[i]
            ),

        "svm_predicted_allergens":
            labels_to_string(
                svm_label_sets[i]
            ),

        "exact_match":
            gold_confirmed_labels[i]
            == svm_label_sets[i],

    })


pd.DataFrame(
    svm_rows
).to_csv(
    SVM_OUTPUT,
    index=False
)


# ============================================================
# P-HAF-KG V2.1
# ============================================================

print("\n" + "=" * 80)
print("RUNNING P-HAF-KG V2.1")
print("=" * 80)


# ------------------------------------------------------------
# Knowledge-base loading
# ------------------------------------------------------------

KB_CANDIDATES = [
    Path(
        "data/processed/"
        "ingredient_allergen_knowledge_14.csv"
    ),

    Path(
        "data/processed/"
        "ingredient_allergen_knowledge_13.csv"
    ),

    Path(
        "data/processed/"
        "ingredient_allergen_knowledge.csv"
    ),
]


KB_FILE = None

for candidate in KB_CANDIDATES:

    if candidate.exists():

        KB_FILE = candidate

        break


if KB_FILE is None:

    raise FileNotFoundError(
        "Could not find ingredient allergen knowledge base."
    )


print(
    f"Knowledge base: {KB_FILE}"
)


kb_df = pd.read_csv(
    KB_FILE
)


print(
    f"Knowledge-base rows: {len(kb_df):,}"
)


print(
    "Knowledge-base columns:",
    list(kb_df.columns)
)


# ============================================================
# IDENTIFY KB COLUMNS
# ============================================================

possible_ingredient_columns = [
    "ingredient",
    "ingredient_term",
    "term",
    "pattern",
    "keyword",
    "ingredient_text",
]


possible_allergen_columns = [
    "allergen",
    "allergen_class",
    "target_allergen",
    "class",
]


ingredient_column = None
allergen_column = None


for col in possible_ingredient_columns:

    if col in kb_df.columns:

        ingredient_column = col

        break


for col in possible_allergen_columns:

    if col in kb_df.columns:

        allergen_column = col

        break


if ingredient_column is None:

    raise ValueError(
        "Could not identify ingredient column "
        "in knowledge base."
    )


if allergen_column is None:

    raise ValueError(
        "Could not identify allergen column "
        "in knowledge base."
    )


# ============================================================
# BUILD SIMPLE DIRECT-TERM INDEX
# ============================================================

direct_terms = {
    allergen: set()
    for allergen in TARGET_ALLERGENS
}


for _, row in kb_df.iterrows():

    allergen = str(
        row[allergen_column]
    ).strip().lower()

    ingredient = str(
        row[ingredient_column]
    ).strip().lower()

    if (
        allergen in direct_terms
        and ingredient
        and ingredient != "nan"
    ):

        direct_terms[
            allergen
        ].add(
            normalize_text(ingredient)
        )


# ============================================================
# ADD IMPORTANT PROJECT-SPECIFIC TERMS
# ============================================================

manual_terms = {

    "celery": [
        "celery",
        "celeriac",
        "celery seed",
        "celery seeds",
    ],

    "crustaceans": [
        "shrimp",
        "prawn",
        "prawns",
        "crab",
        "lobster",
        "crayfish",
        "langoustine",
        "crustacean",
    ],

    "egg": [
        "egg",
        "eggs",
        "egg white",
        "egg yolk",
        "albumin",
        "ovalbumin",
        "lysozyme",
    ],

    "fish": [
        "fish",
        "salmon",
        "tuna",
        "mackerel",
        "anchovy",
        "anchovies",
        "cod",
        "haddock",
        "trout",
        "sardine",
        "sardines",
    ],

    "lupin": [
        "lupin",
        "lupine",
    ],

    "milk": [
        "milk",
        "milk powder",
        "skim milk",
        "skimmed milk",
        "whole milk",
        "cream",
        "butter",
        "cheese",
        "whey",
        "lactose",
        "casein",
        "caseinate",
        "yogurt",
        "yoghurt",
        "yoghurt powder",
        "cultured milk",
        "milk protein",
        "milk proteins",
        "grana padano",
    ],

    "molluscs": [
        "mollusc",
        "molluscs",
        "mussel",
        "mussels",
        "oyster",
        "oysters",
        "squid",
        "octopus",
        "cuttlefish",
        "clam",
        "clams",
        "scallop",
        "scallops",
    ],

    "mustard": [
        "mustard",
        "mustard seed",
        "mustard seeds",
    ],

    "peanut": [
        "peanut",
        "peanuts",
        "arachide",
        "arachides",
        "groundnut",
        "groundnuts",
    ],

    "sesame": [
        "sesame",
        "sesame seed",
        "sesame seeds",
        "tahini",
    ],

    "soy": [
        "soy",
        "soya",
        "soybean",
        "soybeans",
        "soy flour",
        "soy flour",
        "soy lecithin",
        "soya lecithin",
        "soy protein",
        "soya protein",
        "soy sauce",
        "soya sauce",
        "tamari",
    ],

    "tree_nut": [
        "almond",
        "almonds",
        "hazelnut",
        "hazelnuts",
        "walnut",
        "walnuts",
        "cashew",
        "cashews",
        "pistachio",
        "pistachios",
        "pecan",
        "pecans",
        "macadamia",
        "macadamias",
        "brazil nut",
        "brazil nuts",
        "brazilian nut",
        "brazilian nuts",
        "nut",
        "nuts",
    ],

    "wheat_gluten": [
        "wheat",
        "wheat flour",
        "wheat flour",
        "wheat gluten",
        "gluten",
        "gluten flour",
        "spelt",
        "dinkel",
        "rye",
        "barley",
        "barley malt",
        "durum wheat",
        "semolina",
        "bulgur",
        "couscous",
        "farina",
        "farine de froment",
        "tarwebloem",
        "tarwegluten",
    ],
}


for allergen, terms in manual_terms.items():

    for term in terms:

        direct_terms[
            allergen
        ].add(
            normalize_text(term)
        )


# ============================================================
# PHRASES THAT SHOULD NOT TRIGGER TREE_NUT
# ============================================================

TREE_NUT_FALSE_POSITIVES = [
    "coconut",
    "coconut milk",
    "coconut oil",
    "nutmeg",
    "muskad",
    "noix de muscade",
]


# ============================================================
# PRECAUTIONARY LANGUAGE
# ============================================================

PRECAUTIONARY_PATTERNS = [
    "may contain",
    "may contain traces",
    "contains traces",
    "traces of",
    "trace of",
    "manufactured in a facility",
    "made in a facility",
    "processed in a facility",
    "produced in a facility",
    "shared equipment",
    "shared facility",
    "can contain",
    "could contain",
]


# ============================================================
# TOKEN-BOUNDARY MATCH
# ============================================================

def term_present(text, term):

    if not term:

        return False

    if term in TREE_NUT_FALSE_POSITIVES:

        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(term)
        + r"(?![a-z0-9])"
    )

    return re.search(
        pattern,
        text
    ) is not None


# ============================================================
# PROJECT-STYLE KG PREDICTION
# ============================================================

def kg_predict(text):

    text = normalize_text(
        text
    )

    confirmed = set()
    potential = set()

    if not text:

        return confirmed, potential


    # --------------------------------------------------------
    # Split precautionary region from ingredient region.
    # --------------------------------------------------------

    precautionary_positions = []

    for pattern in PRECAUTIONARY_PATTERNS:

        pos = text.find(
            pattern
        )

        if pos >= 0:

            precautionary_positions.append(
                pos
            )


    if precautionary_positions:

        first_precautionary = min(
            precautionary_positions
        )

        ingredient_region = (
            text[:first_precautionary]
        )

        precautionary_region = (
            text[first_precautionary:]
        )

    else:

        ingredient_region = text
        precautionary_region = ""


    # --------------------------------------------------------
    # Direct ingredients
    # --------------------------------------------------------

    for allergen, terms in direct_terms.items():

        for term in terms:

            if term_present(
                ingredient_region,
                term
            ):

                confirmed.add(
                    allergen
                )

                break


    # --------------------------------------------------------
    # Precautionary warnings
    # --------------------------------------------------------

    for allergen, terms in direct_terms.items():

        if allergen in confirmed:

            continue

        for term in terms:

            if term_present(
                precautionary_region,
                term
            ):

                potential.add(
                    allergen
                )

                break


    # --------------------------------------------------------
    # Explicit "contains X" statements
    # Treat as confirmed evidence.
    # --------------------------------------------------------

    contains_positions = []

    for match in re.finditer(
        r"\bcontains\b",
        text
    ):

        contains_positions.append(
            match.start()
        )


    for pos in contains_positions:

        segment = text[pos:]

        next_warning = len(segment)

        for pattern in PRECAUTIONARY_PATTERNS:

            p = segment.find(
                pattern
            )

            if p > 0:

                next_warning = min(
                    next_warning,
                    p
                )

        segment = segment[
            :next_warning
        ]

        for allergen, terms in direct_terms.items():

            for term in terms:

                if term_present(
                    segment,
                    term
                ):

                    confirmed.add(
                        allergen
                    )

                    potential.discard(
                        allergen
                    )

                    break


    return confirmed, potential


# ============================================================
# RUN KG
# ============================================================

kg_rows = []

kg_confirmed_matrix = np.zeros(
    (
        len(gold_df),
        len(TARGET_ALLERGENS)
    ),
    dtype=int
)


kg_potential_matrix = np.zeros(
    (
        len(gold_df),
        len(TARGET_ALLERGENS)
    ),
    dtype=int
)


kg_confirmed_sets = []
kg_potential_sets = []


for i, text in enumerate(gold_text):

    confirmed, potential = kg_predict(
        text
    )

    kg_confirmed_sets.append(
        confirmed
    )

    kg_potential_sets.append(
        potential
    )

    for j, allergen in enumerate(
        TARGET_ALLERGENS
    ):

        if allergen in confirmed:

            kg_confirmed_matrix[
                i, j
            ] = 1

        elif allergen in potential:

            kg_potential_matrix[
                i, j
            ] = 1


    kg_rows.append({

        "gold_id":
            gold_df.iloc[i]["gold_id"],

        "product_code":
            gold_df.iloc[i]["product_code"],

        "product_name":
            gold_df.iloc[i]["product_name"],

        "ingredient_text":
            gold_df.iloc[i]["ingredient_text"],

        "gold_confirmed_allergens":
            labels_to_string(
                gold_confirmed_labels[i]
            ),

        "kg_confirmed_allergens":
            labels_to_string(
                confirmed
            ),

        "kg_potential_allergens":
            labels_to_string(
                potential
            ),

    })


pd.DataFrame(
    kg_rows
).to_csv(
    KG_OUTPUT,
    index=False
)


# ============================================================
# HYBRID DECISION LAYER
# ============================================================

print("\n" + "=" * 80)
print("GENERATING HYBRID DECISIONS")
print("=" * 80)


hybrid_rows = []


hybrid_confirmed_sets = []
hybrid_candidate_sets = []
hybrid_potential_sets = []


for i in range(
    len(gold_df)
):

    kg_confirmed = kg_confirmed_sets[i]
    kg_potential = kg_potential_sets[i]

    svm_positive = svm_label_sets[i]


    # --------------------------------------------------------
    # 1. KG direct evidence = CONFIRMED
    # --------------------------------------------------------

    hybrid_confirmed = set(
        kg_confirmed
    )


    # --------------------------------------------------------
    # 2. KG precautionary evidence = POTENTIAL
    # --------------------------------------------------------

    hybrid_potential = (
        kg_potential
        - hybrid_confirmed
    )


    # --------------------------------------------------------
    # 3. SVM positive without KG evidence
    # = AI candidate / human review
    # --------------------------------------------------------

    hybrid_candidate = (
        svm_positive
        - hybrid_confirmed
        - hybrid_potential
    )


    hybrid_confirmed_sets.append(
        hybrid_confirmed
    )

    hybrid_potential_sets.append(
        hybrid_potential
    )

    hybrid_candidate_sets.append(
        hybrid_candidate
    )


    hybrid_rows.append({

        "gold_id":
            gold_df.iloc[i]["gold_id"],

        "product_code":
            gold_df.iloc[i]["product_code"],

        "product_name":
            gold_df.iloc[i]["product_name"],

        "gold_confirmed_allergens":
            labels_to_string(
                gold_confirmed_labels[i]
            ),

        "kg_confirmed_allergens":
            labels_to_string(
                kg_confirmed
            ),

        "kg_potential_allergens":
            labels_to_string(
                kg_potential
            ),

        "svm_predicted_allergens":
            labels_to_string(
                svm_positive
            ),

        "hybrid_confirmed_allergens":
            labels_to_string(
                hybrid_confirmed
            ),

        "hybrid_potential_allergens":
            labels_to_string(
                hybrid_potential
            ),

        "hybrid_ai_candidates":
            labels_to_string(
                hybrid_candidate
            ),

    })


pd.DataFrame(
    hybrid_rows
).to_csv(
    HYBRID_OUTPUT,
    index=False
)


# ============================================================
# METRIC FUNCTION
# ============================================================

def calculate_metrics(
    y_true,
    y_pred,
    model_name
):

    return {

        "model":
            model_name,

        "micro_precision":
            float(
                precision_score(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0
                )
            ),

        "micro_recall":
            float(
                recall_score(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0
                )
            ),

        "micro_f1":
            float(
                f1_score(
                    y_true,
                    y_pred,
                    average="micro",
                    zero_division=0
                )
            ),

        "macro_precision":
            float(
                precision_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0
                )
            ),

        "macro_recall":
            float(
                recall_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0
                )
            ),

        "macro_f1":
            float(
                f1_score(
                    y_true,
                    y_pred,
                    average="macro",
                    zero_division=0
                )
            ),

        "hamming_loss":
            float(
                hamming_loss(
                    y_true,
                    y_pred
                )
            ),

        "exact_match":
            float(
                np.mean(
                    np.all(
                        y_true == y_pred,
                        axis=1
                    )
                )
            ),
    }


# ============================================================
# PRIMARY CONFIRMED-LABEL EVALUATION
# ============================================================

svm_metrics = calculate_metrics(
    Y_gold,
    Y_svm,
    "TF-IDF + Linear SVM"
)


kg_metrics = calculate_metrics(
    Y_gold,
    kg_confirmed_matrix,
    "P-HAF-KG V2.1"
)


hybrid_confirmed_matrix = np.zeros_like(
    Y_gold
)


for i in range(
    len(gold_df)
):

    for j, allergen in enumerate(
        TARGET_ALLERGENS
    ):

        if allergen in hybrid_confirmed_sets[i]:

            hybrid_confirmed_matrix[
                i, j
            ] = 1


hybrid_metrics = calculate_metrics(
    Y_gold,
    hybrid_confirmed_matrix,
    "Hybrid KG + SVM"
)


# ============================================================
# PER-ALLERGEN METRICS
# ============================================================

per_class_rows = []


for j, allergen in enumerate(
    TARGET_ALLERGENS
):

    gold_col = Y_gold[:, j]


    for model_name, prediction_matrix in [

        (
            "TF-IDF + Linear SVM",
            Y_svm
        ),

        (
            "P-HAF-KG V2.1",
            kg_confirmed_matrix
        ),

        (
            "Hybrid KG + SVM",
            hybrid_confirmed_matrix
        ),

    ]:

        pred_col = prediction_matrix[
            :, j
        ]


        per_class_rows.append({

            "model":
                model_name,

            "allergen":
                allergen,

            "support":
                int(
                    gold_col.sum()
                ),

            "precision":
                float(
                    precision_score(
                        gold_col,
                        pred_col,
                        zero_division=0
                    )
                ),

            "recall":
                float(
                    recall_score(
                        gold_col,
                        pred_col,
                        zero_division=0
                    )
                ),

            "f1":
                float(
                    f1_score(
                        gold_col,
                        pred_col,
                        zero_division=0
                    )
                ),

        })


per_class_df = pd.DataFrame(
    per_class_rows
)


per_class_df.to_csv(
    PER_CLASS_OUTPUT,
    index=False
)


# ============================================================
# DISAGREEMENT ANALYSIS
# ============================================================

svm_exact = 0
kg_exact = 0
hybrid_exact = 0

svm_vs_kg_disagreement = 0

kg_only_confirmed = 0
svm_only_candidate = 0


for i in range(
    len(gold_df)
):

    if (
        gold_confirmed_labels[i]
        == svm_label_sets[i]
    ):

        svm_exact += 1


    if (
        gold_confirmed_labels[i]
        == kg_confirmed_sets[i]
    ):

        kg_exact += 1


    if (
        gold_confirmed_labels[i]
        == hybrid_confirmed_sets[i]
    ):

        hybrid_exact += 1


    if (
        kg_confirmed_sets[i]
        != svm_label_sets[i]
    ):

        svm_vs_kg_disagreement += 1


    if (
        kg_confirmed_sets[i]
        - svm_label_sets[i]
    ):

        kg_only_confirmed += 1


    if (
        svm_label_sets[i]
        - kg_confirmed_sets[i]
    ):

        svm_only_candidate += 1


# ============================================================
# HYBRID REVIEW STATISTICS
# ============================================================

total_ai_candidates = sum(
    len(x)
    for x in hybrid_candidate_sets
)

total_potential = sum(
    len(x)
    for x in hybrid_potential_sets
)

total_confirmed = sum(
    len(x)
    for x in hybrid_confirmed_sets
)


# ============================================================
# FINAL METRICS JSON
# ============================================================

metrics = {

    "dataset":
        "500-product independent gold test set",

    "gold_products":
        int(len(gold_df)),

    "allergen_classes":
        TARGET_ALLERGENS,

    "gold_annotation_source":
        str(GOLD_FILE),

    "gold_annotation_status":
        "reviewed",

    "svm_configuration": {

        "model":
            "OneVsRest LinearSVC",

        "C":
            1.0,

        "max_iter":
            5000,

        "tfidf_ngram_range":
            [1, 2],

        "tfidf_min_df":
            2,

        "tfidf_max_df":
            0.98,

        "tfidf_sublinear_tf":
            True,

        "tfidf_max_features":
            100_000,

    },

    "models": {

        "svm":
            svm_metrics,

        "p_haf_kg":
            kg_metrics,

        "hybrid":
            hybrid_metrics,

    },

    "exact_product_match": {

        "svm":
            svm_exact / len(gold_df),

        "p_haf_kg":
            kg_exact / len(gold_df),

        "hybrid":
            hybrid_exact / len(gold_df),

    },

    "system_disagreement": {

        "products_with_svm_kg_disagreement":
            svm_vs_kg_disagreement,

        "kg_only_confirmed_products":
            kg_only_confirmed,

        "svm_only_candidate_products":
            svm_only_candidate,

    },

    "hybrid_decision_counts": {

        "confirmed_allergen_predictions":
            total_confirmed,

        "potential_allergen_predictions":
            total_potential,

        "ai_candidate_predictions":
            total_ai_candidates,

    },

    "evaluation_note":
        "SVM is evaluated against independently reviewed "
        "gold labels. P-HAF-KG is evaluated by confirmed "
        "allergen predictions. Hybrid retains KG direct "
        "evidence as confirmed, KG precautionary evidence "
        "as potential, and SVM-only positives as AI "
        "candidate/review signals rather than confirmed "
        "allergens.",

}


with METRICS_OUTPUT.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metrics,
        f,
        indent=2
    )


# ============================================================
# HUMAN-READABLE SUMMARY
# ============================================================

elapsed = (
    time.time()
    - start_time
)


with SUMMARY_OUTPUT.open(
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "P-HAF-KG V2.1 — FINAL 500-PRODUCT GOLD EVALUATION\n"
    )

    f.write(
        "=" * 70
        + "\n\n"
    )

    f.write(
        f"Gold products: {len(gold_df):,}\n"
    )

    f.write(
        f"Allergen classes: {len(TARGET_ALLERGENS)}\n"
    )

    f.write(
        f"Evaluation time: {elapsed:.2f} seconds\n\n"
    )


    for result in [
        svm_metrics,
        kg_metrics,
        hybrid_metrics,
    ]:

        f.write(
            f"{result['model']}\n"
        )

        f.write(
            "-" * 50
            + "\n"
        )

        f.write(
            f"Micro Precision: "
            f"{result['micro_precision']:.4f}\n"
        )

        f.write(
            f"Micro Recall:    "
            f"{result['micro_recall']:.4f}\n"
        )

        f.write(
            f"Micro F1:        "
            f"{result['micro_f1']:.4f}\n"
        )

        f.write(
            f"Macro Precision: "
            f"{result['macro_precision']:.4f}\n"
        )

        f.write(
            f"Macro Recall:    "
            f"{result['macro_recall']:.4f}\n"
        )

        f.write(
            f"Macro F1:        "
            f"{result['macro_f1']:.4f}\n"
        )

        f.write(
            f"Hamming Loss:    "
            f"{result['hamming_loss']:.4f}\n"
        )

        f.write(
            f"Exact Match:     "
            f"{result['exact_match']:.4f}\n\n"
        )


    f.write(
        "Hybrid decision counts\n"
    )

    f.write(
        "-" * 50
        + "\n"
    )

    f.write(
        f"Confirmed: "
        f"{total_confirmed:,}\n"
    )

    f.write(
        f"Potential: "
        f"{total_potential:,}\n"
    )

    f.write(
        f"AI candidates: "
        f"{total_ai_candidates:,}\n"
    )


# ============================================================
# CONSOLE OUTPUT
# ============================================================

print("\n" + "=" * 80)
print("FINAL GOLD EVALUATION RESULTS")
print("=" * 80)


for result in [
    svm_metrics,
    kg_metrics,
    hybrid_metrics,
]:

    print(
        f"\n{result['model']}"
    )

    print(
        f"  Micro Precision: "
        f"{result['micro_precision']:.4f}"
    )

    print(
        f"  Micro Recall:    "
        f"{result['micro_recall']:.4f}"
    )

    print(
        f"  Micro F1:        "
        f"{result['micro_f1']:.4f}"
    )

    print(
        f"  Macro F1:        "
        f"{result['macro_f1']:.4f}"
    )

    print(
        f"  Hamming Loss:    "
        f"{result['hamming_loss']:.4f}"
    )

    print(
        f"  Exact Match:     "
        f"{result['exact_match']:.4f}"
    )


print("\nFiles saved:")

print(
    SVM_OUTPUT
)

print(
    KG_OUTPUT
)

print(
    HYBRID_OUTPUT
)

print(
    METRICS_OUTPUT
)

print(
    PER_CLASS_OUTPUT
)

print(
    SUMMARY_OUTPUT
)

print(
    f"\nCompleted in {elapsed:.2f} seconds."
)

print(
    "\nGOLD EVALUATION COMPLETE."
)
