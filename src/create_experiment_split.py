import csv
from pathlib import Path
import random

INPUT_FILE = Path(
    "data/processed/ground_truth_final.csv"
)

TRAIN_FILE = Path(
    "data/processed/train.csv"
)

TEST_FILE = Path(
    "data/processed/test.csv"
)

SEED = 42
TEST_RATIO = 0.20

ALLERGENS = [
    "peanut",
    "milk",
    "egg",
    "soy",
    "wheat_gluten",
    "sesame",
    "tree_nut",
]


def parse_labels(value):
    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


# Only use reviewed food products
rows = [
    row
    for row in rows
    if row["review_status"] == "KEEP"
    and row["is_food"] == "YES"
]


# Shuffle reproducibly
random.seed(SEED)
random.shuffle(rows)


test_size = round(len(rows) * TEST_RATIO)

test_rows = rows[:test_size]
train_rows = rows[test_size:]


def counts(data):

    result = {}

    for allergen in ALLERGENS:

        result[allergen] = sum(
            allergen in parse_labels(
                row["confirmed_allergens"]
            )
            for row in data
        )

    return result


train_counts = counts(train_rows)
test_counts = counts(test_rows)


print("\n===== EXPERIMENT SPLIT =====")

print("Total:", len(rows))
print("Training:", len(train_rows))
print("Testing:", len(test_rows))

print("\nTraining allergen counts:")

for allergen, count in train_counts.items():
    print(f"{allergen:15}: {count}")


print("\nTesting allergen counts:")

for allergen, count in test_counts.items():
    print(f"{allergen:15}: {count}")


# Check that every allergen appears in both sets
for allergen in ALLERGENS:

    if train_counts[allergen] == 0:
        raise ValueError(
            f"{allergen} has zero training examples."
        )

    if test_counts[allergen] == 0:
        raise ValueError(
            f"{allergen} has zero testing examples."
        )


fields = list(rows[0].keys())


with TRAIN_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(train_rows)


with TEST_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(test_rows)


print("\nFiles created:")

print(TRAIN_FILE)
print(TEST_FILE)

print("\nSplit successfully created.")
