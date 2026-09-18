import csv
import random
from pathlib import Path
from collections import Counter


# ============================================================
# P-HAF-KG V2.1
# CORRECTED ML DATASET EXTRACTION
# ============================================================

SOURCE_FILE = Path(
    "data/en.openfoodfacts.org.products (1).csv"
)

P_HAF_FILE = Path(
    "data/processed/scan/p_haf_kg_v2_1_large_scale_4535553.csv"
)

OUTPUT_DIR = Path(
    "data/processed/ml"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_SEED = 42

MAX_PER_ALLERGEN = 15_000
MAX_NEGATIVE = 30_000

csv.field_size_limit(10_000_000)

random.seed(RANDOM_SEED)


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
# STEP 1
# READ ALL P-HAF-KG LABELS
# ============================================================

print("=" * 70)
print("STEP 1 — READING P-HAF-KG OUTPUT")
print("=" * 70)

label_lookup = {}

positive_codes = set()
negative_codes = set()

total_p_haf = 0


with P_HAF_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        total_p_haf += 1

        code = (
            row.get("code") or ""
        ).strip()

        if not code:
            continue


        confirmed_text = (
            row.get("confirmed_allergens") or ""
        ).strip()

        potential_text = (
            row.get("potential_allergens") or ""
        ).strip()


        confirmed = {
            x.strip()
            for x in confirmed_text.split(";")
            if x.strip()
        }

        potential = {
            x.strip()
            for x in potential_text.split(";")
            if x.strip()
        }


        # ----------------------------------------------------
        # IMPORTANT:
        # Primary ML target = CONFIRMED allergens
        # Potential allergens remain separate evidence.
        # ----------------------------------------------------

        confirmed = {
            x for x in confirmed
            if x in TARGET_ALLERGENS
        }

        potential = {
            x for x in potential
            if x in TARGET_ALLERGENS
        }


        label_lookup[code] = {
            "confirmed_allergens":
                ";".join(sorted(confirmed)),

            "potential_allergens":
                ";".join(sorted(potential)),
        }


        # Product has confirmed allergen(s)
        if confirmed:

            positive_codes.add(code)

        # Product has NO confirmed allergens
        else:

            negative_codes.add(code)


print(
    f"P-HAF-KG rows read: {total_p_haf:,}"
)

print(
    f"Positive products: {len(positive_codes):,}"
)

print(
    f"Negative products available: {len(negative_codes):,}"
)


# ============================================================
# STEP 2
# LIMIT NEGATIVE CANDIDATES
# ============================================================

negative_codes = list(
    negative_codes
)

random.shuffle(
    negative_codes
)

negative_codes = set(
    negative_codes[:MAX_NEGATIVE]
)


target_codes = (
    positive_codes |
    negative_codes
)


print(
    f"\nTarget products to recover from "
    f"OpenFoodFacts: {len(target_codes):,}"
)


# ============================================================
# STEP 3
# RECOVER INGREDIENT TEXT
# ============================================================

print("\n")
print("=" * 70)
print("STEP 2 — MATCHING ORIGINAL INGREDIENT TEXT")
print("=" * 70)


dataset = []

matched = 0
missing_ingredients = 0


with SOURCE_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(
        f,
        delimiter="\t"
    )


    for row in reader:

        code = (
            row.get("code") or ""
        ).strip()

        if not code:
            continue


        if code not in target_codes:
            continue


        ingredient_text = (
            row.get("ingredients_text") or ""
        ).strip()


        if not ingredient_text:

            missing_ingredients += 1
            continue


        product_name = (
            row.get("product_name") or ""
        ).strip()


        labels = label_lookup[code]


        dataset.append({
            "product_code":
                code,

            "product_name":
                product_name,

            "ingredient_text":
                ingredient_text,

            "confirmed_allergens":
                labels["confirmed_allergens"],

            "potential_allergens":
                labels["potential_allergens"],
        })


        matched += 1


        if matched % 50_000 == 0:

            print(
                f"Matched {matched:,} products..."
            )


print(
    f"\nUsable products: {len(dataset):,}"
)

print(
    f"Missing ingredient text: "
    f"{missing_ingredients:,}"
)


# ============================================================
# STEP 4
# CLASS DISTRIBUTION
# ============================================================

print("\n")
print("=" * 70)
print("STEP 3 — CONFIRMED ALLERGEN DISTRIBUTION")
print("=" * 70)


class_counts = Counter()

negative_count = 0


for row in dataset:

    confirmed = {
        x.strip()
        for x in row[
            "confirmed_allergens"
        ].split(";")
        if x.strip()
    }


    if not confirmed:

        negative_count += 1

    else:

        for allergen in confirmed:

            class_counts[allergen] += 1


for allergen, count in class_counts.most_common():

    print(
        f"{allergen:20s} {count:10,}"
    )


print(
    f"\nNo confirmed allergen: "
    f"{negative_count:,}"
)


# ============================================================
# STEP 5
# BALANCED MULTILABEL SAMPLING
# ============================================================

print("\n")
print("=" * 70)
print("STEP 4 — BALANCED DATASET")
print("=" * 70)


by_code = {
    row["product_code"]: row
    for row in dataset
}


codes = list(
    by_code.keys()
)

random.shuffle(
    codes
)


selected_codes = set()

selected_counts = Counter()


# ------------------------------------------------------------
# First: select positive examples
# ------------------------------------------------------------

for code in codes:

    row = by_code[code]


    confirmed = {
        x.strip()
        for x in row[
            "confirmed_allergens"
        ].split(";")
        if x.strip()
    }


    if not confirmed:
        continue


    # Determine whether adding this product
    # improves coverage for at least one class.

    useful = False

    for allergen in confirmed:

        if (
            selected_counts[allergen]
            < MAX_PER_ALLERGEN
        ):

            useful = True
            break


    if not useful:
        continue


    selected_codes.add(code)


    for allergen in confirmed:

        if (
            selected_counts[allergen]
            < MAX_PER_ALLERGEN
        ):

            selected_counts[allergen] += 1


# ------------------------------------------------------------
# Second: add negative products
# ------------------------------------------------------------

negative_selected = 0


for code in codes:

    if negative_selected >= MAX_NEGATIVE:
        break


    if code in selected_codes:
        continue


    row = by_code[code]


    if not row[
        "confirmed_allergens"
    ].strip():

        selected_codes.add(code)

        negative_selected += 1


silver_dataset = [
    by_code[code]
    for code in selected_codes
]


random.shuffle(
    silver_dataset
)


print(
    f"Silver dataset: "
    f"{len(silver_dataset):,}"
)

print(
    f"Negative examples: "
    f"{negative_selected:,}"
)


# ============================================================
# STEP 6
# SAVE COMPLETE SILVER DATASET
# ============================================================

FIELDNAMES = [
    "product_code",
    "product_name",
    "ingredient_text",
    "confirmed_allergens",
    "potential_allergens",
]


SILVER_FILE = (
    OUTPUT_DIR /
    "silver_dataset.csv"
)


with SILVER_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=FIELDNAMES
    )

    writer.writeheader()

    writer.writerows(
        silver_dataset
    )


print(
    f"\nSaved:\n{SILVER_FILE}"
)


# ============================================================
# STEP 7
# CREATE RANDOM HOLDOUTS
#
# These are SILVER holdouts only.
# Final gold test data comes later.
# ============================================================

print("\n")
print("=" * 70)
print("STEP 5 — INITIAL HOLDOUT SPLIT")
print("=" * 70)


# ------------------------------------------------------------
# Shuffle once using fixed seed
# ------------------------------------------------------------

random.shuffle(
    silver_dataset
)


n = len(
    silver_dataset
)


train_end = int(
    n * 0.80
)

validation_end = int(
    n * 0.90
)


train_data = (
    silver_dataset[:train_end]
)

validation_data = (
    silver_dataset[
        train_end:validation_end
    ]
)

test_candidate_data = (
    silver_dataset[
        validation_end:
    ]
)


def write_dataset(
    path,
    rows
):

    with path.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES
        )

        writer.writeheader()

        writer.writerows(rows)


TRAIN_FILE = (
    OUTPUT_DIR /
    "train_initial.csv"
)

VALIDATION_FILE = (
    OUTPUT_DIR /
    "validation_initial.csv"
)

TEST_FILE = (
    OUTPUT_DIR /
    "test_candidate_initial.csv"
)


write_dataset(
    TRAIN_FILE,
    train_data
)

write_dataset(
    VALIDATION_FILE,
    validation_data
)

write_dataset(
    TEST_FILE,
    test_candidate_data
)


print(
    f"Training:       {len(train_data):,}"
)

print(
    f"Validation:     {len(validation_data):,}"
)

print(
    f"Test candidate: {len(test_candidate_data):,}"
)


# ============================================================
# STEP 8
# REPORT LABEL DISTRIBUTION IN EACH SPLIT
# ============================================================

def count_labels(rows):

    counts = Counter()

    negatives = 0

    for row in rows:

        labels = {
            x.strip()
            for x in row[
                "confirmed_allergens"
            ].split(";")
            if x.strip()
        }


        if not labels:

            negatives += 1

        for label in labels:

            counts[label] += 1


    return counts, negatives


for name, rows in [
    ("TRAIN", train_data),
    ("VALIDATION", validation_data),
    ("TEST CANDIDATE", test_candidate_data),
]:

    counts, negatives = count_labels(
        rows
    )


    print("\n")
    print(
        f"{name} LABEL DISTRIBUTION"
    )

    print("-" * 50)

    for allergen in TARGET_ALLERGENS:

        print(
            f"{allergen:20s} "
            f"{counts[allergen]:8,}"
        )

    print(
        f"{'NO ALLERGEN':20s} "
        f"{negatives:8,}"
    )


print("\n")
print("=" * 70)
print("EXTRACTION COMPLETE")
print("=" * 70)