import csv
from pathlib import Path

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss
)

TEST_FILE = Path(
    "data/processed/test.csv"
)

OUTPUT_FILE = Path(
    "data/processed/baseline_keyword_final_metrics.csv"
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


KEYWORDS = {

    "peanut": [
        "peanut",
        "groundnut",
        "arachide",
        "cacahuète",
        "erdnuss",
    ],

    "milk": [
        "milk",
        "lait",
        "milk powder",
        "whey",
        "casein",
        "caseinate",
        "cream",
        "butter",
        "cheese",
        "lactose",
        "milch",
    ],

    "egg": [
        "egg",
        "oeuf",
        "albumen",
        "egg white",
        "egg yolk",
        "mayonnaise",
    ],

    "soy": [
        "soy",
        "soya",
        "soja",
        "soybean",
        "lecithin",
        "tofu",
        "edamame",
    ],

    "wheat_gluten": [
        "wheat",
        "wheat flour",
        "flour",
        "gluten",
        "barley",
        "rye",
        "spelt",
        "durum",
        "semolina",
    ],

    "sesame": [
        "sesame",
        "sésame",
        "sesam",
        "tahini",
    ],

    "tree_nut": [
        "almond",
        "almonds",
        "amande",
        "cashew",
        "cashews",
        "noix",
        "walnut",
        "walnuts",
        "hazelnut",
        "hazelnuts",
        "pecan",
        "pistachio",
        "pistachios",
        "brazil nut",
        "macadamia",
    ],
}


def parse_labels(value):

    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


def predict(text, allergen):

    text = text.lower()

    for keyword in KEYWORDS[allergen]:

        if keyword.lower() in text:
            return 1

    return 0


with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


y_true = []
y_pred = []

for row in rows:

    text = row["ingredients_text"]

    true_labels = parse_labels(
        row["confirmed_allergens"]
    )

    true_row = []
    pred_row = []

    for allergen in ALLERGENS:

        true_row.append(
            int(allergen in true_labels)
        )

        pred_row.append(
            predict(text, allergen)
        )

    y_true.append(true_row)
    y_pred.append(pred_row)


print("\n===== FINAL BASELINE 1: KEYWORD =====")

results = []

for i, allergen in enumerate(ALLERGENS):

    precision = precision_score(
        [row[i] for row in y_true],
        [row[i] for row in y_pred],
        zero_division=0
    )

    recall = recall_score(
        [row[i] for row in y_true],
        [row[i] for row in y_pred],
        zero_division=0
    )

    f1 = f1_score(
        [row[i] for row in y_true],
        [row[i] for row in y_pred],
        zero_division=0
    )

    results.append({
        "allergen": allergen,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    })

    print(
        f"{allergen:15} "
        f"Precision={precision:.4f} "
        f"Recall={recall:.4f} "
        f"F1={f1:.4f}"
    )


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

hl = hamming_loss(
    y_true,
    y_pred
)


print("\n===== OVERALL =====")

print(f"Macro Precision: {macro_precision:.4f}")
print(f"Macro Recall:    {macro_recall:.4f}")
print(f"Macro F1:        {macro_f1:.4f}")
print(f"Micro F1:        {micro_f1:.4f}")
print(f"Hamming Loss:   {hl:.4f}")


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "allergen",
            "precision",
            "recall",
            "f1"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


print("\nSaved to:")
print(OUTPUT_FILE)
