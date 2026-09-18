import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

TRAIN_FILE = Path("data/processed/train.csv")
TEST_FILE = Path("data/processed/test.csv")

OUTPUT_FILE = Path(
    "data/processed/tfidf_error_analysis.csv"
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


def parse_labels(value):

    if not value:
        return set()

    return {
        x.strip()
        for x in value.split(";")
        if x.strip()
    }


def make_matrix(rows):

    matrix = []

    for row in rows:

        labels = parse_labels(
            row["confirmed_allergens"]
        )

        matrix.append([
            int(allergen in labels)
            for allergen in ALLERGENS
        ])

    return matrix


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

with TRAIN_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    train_rows = list(csv.DictReader(f))


with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = list(csv.DictReader(f))


X_train_text = [
    row["ingredients_text"]
    for row in train_rows
]

X_test_text = [
    row["ingredients_text"]
    for row in test_rows
]


y_train = make_matrix(train_rows)
y_test = make_matrix(test_rows)


# --------------------------------------------------
# TF-IDF
# --------------------------------------------------

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
    sublinear_tf=True
)

X_train = vectorizer.fit_transform(
    X_train_text
)

X_test = vectorizer.transform(
    X_test_text
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = OneVsRestClassifier(
    LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )
)

model.fit(
    X_train,
    y_train
)

y_pred = model.predict(X_test)


# --------------------------------------------------
# ERROR ANALYSIS
# --------------------------------------------------

results = []

error_counts = {
    allergen: {
        "FP": 0,
        "FN": 0,
        "TP": 0,
        "TN": 0
    }
    for allergen in ALLERGENS
}


for row_index, row in enumerate(test_rows):

    true_labels = set(
        allergen
        for i, allergen in enumerate(ALLERGENS)
        if y_test[row_index][i] == 1
    )

    predicted_labels = set(
        allergen
        for i, allergen in enumerate(ALLERGENS)
        if y_pred[row_index][i] == 1
    )

    false_positive = predicted_labels - true_labels
    false_negative = true_labels - predicted_labels

    # Update counts
    for allergen in ALLERGENS:

        true_value = y_test[row_index][
            ALLERGENS.index(allergen)
        ]

        predicted_value = y_pred[row_index][
            ALLERGENS.index(allergen)
        ]

        if true_value == 1 and predicted_value == 1:
            error_counts[allergen]["TP"] += 1

        elif true_value == 0 and predicted_value == 1:
            error_counts[allergen]["FP"] += 1

        elif true_value == 1 and predicted_value == 0:
            error_counts[allergen]["FN"] += 1

        else:
            error_counts[allergen]["TN"] += 1


    # Only save products where a mistake occurred
    if false_positive or false_negative:

        results.append({
            "code": row["code"],
            "product_name": row["product_name"],
            "true_labels": ";".join(
                sorted(true_labels)
            ),
            "predicted_labels": ";".join(
                sorted(predicted_labels)
            ),
            "false_positives": ";".join(
                sorted(false_positive)
            ),
            "false_negatives": ";".join(
                sorted(false_negative)
            ),
            "evidence_level": row[
                "evidence_level"
            ],
            "ingredients_text": row[
                "ingredients_text"
            ],
        })


# --------------------------------------------------
# PRINT SUMMARY
# --------------------------------------------------

print("\n===== TF-IDF ERROR ANALYSIS =====")

print(
    "Test products:",
    len(test_rows)
)

print(
    "Products with at least one error:",
    len(results)
)


print("\n===== ERROR COUNTS =====")

for allergen in ALLERGENS:

    values = error_counts[allergen]

    print(
        f"{allergen:15} "
        f"TP={values['TP']} "
        f"FP={values['FP']} "
        f"FN={values['FN']} "
        f"TN={values['TN']}"
    )


print("\n===== PRODUCT-LEVEL ERRORS =====")

for i, result in enumerate(results, 1):

    print("\n" + "=" * 80)

    print(f"ERROR CASE {i}")

    print("Product:",
          result["product_name"])

    print("Code:",
          result["code"])

    print("True:",
          result["true_labels"])

    print("Predicted:",
          result["predicted_labels"])

    print("False positives:",
          result["false_positives"])

    print("False negatives:",
          result["false_negatives"])

    print("Evidence:",
          result["evidence_level"])

    print(
        "Ingredients:",
        result["ingredients_text"][:1200]
    )


# --------------------------------------------------
# SAVE
# --------------------------------------------------

fields = [
    "code",
    "product_name",
    "true_labels",
    "predicted_labels",
    "false_positives",
    "false_negatives",
    "evidence_level",
    "ingredients_text",
]


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()
    writer.writerows(results)


print("\nSaved to:")
print(OUTPUT_FILE)
