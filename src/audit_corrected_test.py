import csv
from pathlib import Path

TEST_FILE = Path("data/processed/test.csv")

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


with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


print("===== CORRECTED TEST SET AUDIT =====")
print("Total test products:", len(rows))


print("\n===== CONFIRMED ALLERGEN COUNTS =====")

total_confirmed = 0

for allergen in ALLERGENS:

    count = 0

    for row in rows:

        labels = parse_labels(
            row["confirmed_allergens"]
        )

        if allergen in labels:
            count += 1

    total_confirmed += count

    print(
        f"{allergen:15}: {count}"
    )


print("\n===== MULTI-LABEL DISTRIBUTION =====")

distribution = {
    "0": 0,
    "1": 0,
    "2": 0,
    "3": 0,
    "4+": 0,
}


for row in rows:

    labels = parse_labels(
        row["confirmed_allergens"]
    )

    n = len(labels)

    if n == 0:
        distribution["0"] += 1

    elif n == 1:
        distribution["1"] += 1

    elif n == 2:
        distribution["2"] += 1

    elif n == 3:
        distribution["3"] += 1

    else:
        distribution["4+"] += 1


for key, value in distribution.items():

    print(
        f"{key:4}: {value}"
    )


print("\n===== REVIEWED PRODUCTS =====")

reviewed = 0

for row in rows:

    if row["evidence_level"] == "REVIEWED":
        reviewed += 1


print(
    "Reviewed:",
    reviewed
)

print(
    "Not reviewed:",
    len(rows) - reviewed
)


print("\n===== PRODUCTS WITH NO CONFIRMED ALLERGEN =====")

negative = 0

for row in rows:

    labels = parse_labels(
        row["confirmed_allergens"]
    )

    if not labels:

        negative += 1

        print(
            row["code"],
            "|",
            row["product_name"]
        )


print(
    "\nNegative products:",
    negative
)


print("\n===== DATA QUALITY =====")

missing_codes = sum(
    1 for row in rows
    if not row["code"].strip()
)

missing_ingredients = sum(
    1 for row in rows
    if not row["ingredients_text"].strip()
)

print(
    "Missing codes:",
    missing_codes
)

print(
    "Missing ingredient text:",
    missing_ingredients
)


print("\n===== FINAL CHECK =====")

if (
    len(rows) == 27
    and reviewed == 20
    and missing_codes == 0
    and missing_ingredients == 0
):

    print(
        "PASS - corrected test set is ready for baseline evaluation."
    )

else:

    print(
        "WARNING - inspect the dataset before evaluation."
    )
