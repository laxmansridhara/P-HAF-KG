import csv
import random
from pathlib import Path
from collections import Counter


# ============================================================
# P-HAF-KG V2.1
# MULTILABEL STRATIFIED DATASET SPLIT
# ============================================================

INPUT_FILE = Path(
    "data/processed/ml/silver_dataset.csv"
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

TRAIN_RATIO = 0.80
VALIDATION_RATIO = 0.10
TEST_RATIO = 0.10

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


random.seed(RANDOM_SEED)

csv.field_size_limit(10_000_000)


# ============================================================
# STEP 1 — LOAD DATA
# ============================================================

print("=" * 70)
print("MULTILABEL STRATIFIED SPLIT")
print("=" * 70)

print("\nReading:")
print(INPUT_FILE)


rows = []

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        rows.append(row)


print(
    f"Rows loaded: {len(rows):,}"
)


# ============================================================
# STEP 2 — EXTRACT MULTILABEL TARGETS
# ============================================================

row_labels = []

label_totals = Counter()

negative_indices = []


for index, row in enumerate(rows):

    labels = {
        x.strip()
        for x in (
            row.get("confirmed_allergens") or ""
        ).split(";")
        if x.strip()
    }

    labels = {
        x
        for x in labels
        if x in TARGET_ALLERGENS
    }

    row_labels.append(labels)

    if not labels:

        negative_indices.append(index)

    else:

        for label in labels:
            label_totals[label] += 1


print("\nOverall label distribution:")
print("-" * 70)

for label in TARGET_ALLERGENS:

    print(
        f"{label:20s} "
        f"{label_totals[label]:10,}"
    )

print(
    f"{'NO ALLERGEN':20s} "
    f"{len(negative_indices):10,}"
)


# ============================================================
# STEP 3 — TARGET SPLIT SIZES
# ============================================================

total = len(rows)


target_sizes = {
    "train": int(total * TRAIN_RATIO),
    "validation": int(total * VALIDATION_RATIO),
}

target_sizes["test"] = (
    total
    - target_sizes["train"]
    - target_sizes["validation"]
)


print("\nTarget split sizes:")
print("-" * 70)

for split, size in target_sizes.items():

    print(
        f"{split:15s} {size:10,}"
    )


# ============================================================
# STEP 4 — TARGET LABEL COUNTS PER SPLIT
# ============================================================

split_ratios = {
    "train": TRAIN_RATIO,
    "validation": VALIDATION_RATIO,
    "test": TEST_RATIO,
}


target_label_counts = {
    split: {}
    for split in split_ratios
}


for split, ratio in split_ratios.items():

    for label in TARGET_ALLERGENS:

        target_label_counts[split][label] = (
            label_totals[label] * ratio
        )


# ============================================================
# STEP 5 — CREATE LABEL -> ROW INDEX MAP
# ============================================================

label_to_indices = {
    label: []
    for label in TARGET_ALLERGENS
}


for index, labels in enumerate(row_labels):

    for label in labels:

        label_to_indices[label].append(index)


# ============================================================
# STEP 6 — ITERATIVE MULTILABEL STRATIFICATION
# ============================================================

print("\n")
print("=" * 70)
print("ITERATIVE MULTILABEL STRATIFICATION")
print("=" * 70)


# Assignment of each row.
assignment = {}

# Current number of rows assigned.
split_sizes = {
    "train": 0,
    "validation": 0,
    "test": 0,
}

# Current label counts.
current_label_counts = {
    split: Counter()
    for split in split_ratios
}


unassigned = set(
    range(total)
)


# ------------------------------------------------------------
# Process rarest labels first.
# This protects minority allergen classes.
# ------------------------------------------------------------

labels_by_rarity = sorted(
    TARGET_ALLERGENS,
    key=lambda label: label_totals[label]
)


for label in labels_by_rarity:

    candidate_indices = [
        index
        for index in label_to_indices[label]
        if index in unassigned
    ]


    # Randomise equal-priority rows.
    random.shuffle(candidate_indices)


    for index in candidate_indices:

        labels = row_labels[index]


        # ----------------------------------------------------
        # Calculate how much each split still needs
        # this particular label.
        # ----------------------------------------------------

        label_need = {}

        for split in split_ratios:

            desired = target_label_counts[
                split
            ][label]

            current = current_label_counts[
                split
            ][label]

            label_need[split] = (
                desired - current
            )


        # ----------------------------------------------------
        # Calculate available row capacity.
        # ----------------------------------------------------

        capacity = {}

        for split in split_ratios:

            capacity[split] = (
                target_sizes[split]
                - split_sizes[split]
            )


        # ----------------------------------------------------
        # Choose the split needing the label most.
        #
        # Tie-breaker:
        # choose the split with the largest
        # remaining overall capacity.
        # ----------------------------------------------------

        ordered_splits = sorted(
            split_ratios.keys(),
            key=lambda split: (
                label_need[split],
                capacity[split]
            ),
            reverse=True
        )


        chosen_split = ordered_splits[0]


        # ----------------------------------------------------
        # Assign row.
        # ----------------------------------------------------

        assignment[index] = chosen_split

        unassigned.remove(index)

        split_sizes[
            chosen_split
        ] += 1


        for row_label in labels:

            current_label_counts[
                chosen_split
            ][row_label] += 1


# ============================================================
# STEP 7 — ASSIGN REMAINING ROWS
#
# These are mainly negative examples.
# ============================================================

remaining_indices = list(
    unassigned
)

random.shuffle(
    remaining_indices
)


for index in remaining_indices:

    capacity = {
        split: (
            target_sizes[split]
            - split_sizes[split]
        )
        for split in split_ratios
    }


    chosen_split = max(
        capacity,
        key=capacity.get
    )


    assignment[index] = chosen_split

    split_sizes[
        chosen_split
    ] += 1


# ============================================================
# STEP 8 — BUILD FINAL ROW LISTS
# ============================================================

train_rows = []
validation_rows = []
test_rows = []


for index, row in enumerate(rows):

    split = assignment[index]

    if split == "train":

        train_rows.append(row)

    elif split == "validation":

        validation_rows.append(row)

    else:

        test_rows.append(row)


# ============================================================
# STEP 9 — SHUFFLE EACH SPLIT
# ============================================================

random.shuffle(train_rows)
random.shuffle(validation_rows)
random.shuffle(test_rows)


# ============================================================
# STEP 10 — SAVE
# ============================================================

fieldnames = [
    "product_code",
    "product_name",
    "ingredient_text",
    "confirmed_allergens",
    "potential_allergens",
]


def write_csv(
    path,
    data
):

    with path.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(data)


TRAIN_FILE = (
    OUTPUT_DIR /
    "train.csv"
)

VALIDATION_FILE = (
    OUTPUT_DIR /
    "validation.csv"
)

TEST_FILE = (
    OUTPUT_DIR /
    "test_candidate.csv"
)


write_csv(
    TRAIN_FILE,
    train_rows
)

write_csv(
    VALIDATION_FILE,
    validation_rows
)

write_csv(
    TEST_FILE,
    test_rows
)


# ============================================================
# STEP 11 — VERIFY SPLITS
# ============================================================

def analyse_split(data):

    counts = Counter()

    negatives = 0

    for row in data:

        labels = {
            x.strip()
            for x in (
                row.get(
                    "confirmed_allergens"
                ) or ""
            ).split(";")
            if x.strip()
        }

        labels = {
            x
            for x in labels
            if x in TARGET_ALLERGENS
        }


        if not labels:

            negatives += 1

        else:

            for label in labels:

                counts[label] += 1


    return counts, negatives


print("\n")
print("=" * 70)
print("FINAL MULTILABEL SPLIT")
print("=" * 70)


print(
    f"\nTRAIN:       {len(train_rows):,}"
)

print(
    f"VALIDATION:  {len(validation_rows):,}"
)

print(
    f"TEST:        {len(test_rows):,}"
)


for name, data in [
    ("TRAIN", train_rows),
    ("VALIDATION", validation_rows),
    ("TEST", test_rows),
]:

    counts, negatives = analyse_split(
        data
    )


    print("\n")
    print(
        f"{name} LABEL DISTRIBUTION"
    )

    print("-" * 70)


    for label in TARGET_ALLERGENS:

        overall = label_totals[label]
        split_count = counts[label]

        percentage = (
            split_count / overall * 100
            if overall
            else 0
        )


        print(
            f"{label:20s} "
            f"{split_count:8,} "
            f"({percentage:6.2f}% of total)"
        )


    print(
        f"{'NO ALLERGEN':20s} "
        f"{negatives:8,}"
    )


# ============================================================
# STEP 12 — CHECK PRODUCT-CODE UNIQUENESS
# ============================================================

train_codes = {
    row["product_code"]
    for row in train_rows
}

validation_codes = {
    row["product_code"]
    for row in validation_rows
}

test_codes = {
    row["product_code"]
    for row in test_rows
}


overlap_train_validation = (
    train_codes &
    validation_codes
)

overlap_train_test = (
    train_codes &
    test_codes
)

overlap_validation_test = (
    validation_codes &
    test_codes
)


print("\n")
print("=" * 70)
print("LEAKAGE CHECK")
print("=" * 70)

print(
    "Train/Validation overlap:",
    len(overlap_train_validation)
)

print(
    "Train/Test overlap:",
    len(overlap_train_test)
)

print(
    "Validation/Test overlap:",
    len(overlap_validation_test)
)


# ============================================================
# END
# ============================================================

print("\n")
print("=" * 70)
print("MULTILABEL SPLIT COMPLETE")
print("=" * 70)

print("\nFiles created:")

print(TRAIN_FILE)
print(VALIDATION_FILE)
print(TEST_FILE)
