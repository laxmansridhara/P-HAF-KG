import os
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import precision_recall_fscore_support


PHAF_FILE = (
    "data/processed/"
    "p_haf_kg_14_v2_1_product_evaluation.csv"
)

OUTPUT_FILE = (
    "data/processed/"
    "p_haf_kg_per_allergen_metrics.csv"
)


def parse_labels(value):

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    return [
        x.strip().lower()
        for x in value.split(";")
        if x.strip()
    ]


print("=" * 70)
print("P-HAF-KG V2.1 PER-ALLERGEN METRICS")
print("=" * 70)

df = pd.read_csv(PHAF_FILE)

print("\nLoaded:")
print(PHAF_FILE)

print("\nRows:", len(df))

print("\nColumns:")
print(df.columns.tolist())


# ------------------------------------------------------------
# GROUND TRUTH
# ------------------------------------------------------------

true_labels = (
    df["ground_truth"]
    .apply(parse_labels)
    .tolist()
)


# ------------------------------------------------------------
# P-HAF-KG PREDICTIONS
# ------------------------------------------------------------

predicted_labels = (
    df["prediction"]
    .apply(parse_labels)
    .tolist()
)


# ------------------------------------------------------------
# ALL CLASSES
# ------------------------------------------------------------

mlb = MultiLabelBinarizer()

mlb.fit(
    true_labels + predicted_labels
)

classes = list(mlb.classes_)

print("\nAllergen classes:")
print(classes)


# ------------------------------------------------------------
# BINARY MATRICES
# ------------------------------------------------------------

y_true = mlb.transform(true_labels)

y_pred = mlb.transform(predicted_labels)


# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

precision, recall, f1, support = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        average=None,
        labels=range(len(classes)),
        zero_division=0
    )
)


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

rows = []

for i, allergen in enumerate(classes):

    rows.append({
        "model": "P-HAF-KG V2.1",
        "allergen": allergen,
        "precision": precision[i],
        "recall": recall[i],
        "f1": f1[i],
        "support": support[i]
    })


result_df = pd.DataFrame(rows)


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("P-HAF-KG PER-ALLERGEN RESULTS")
print("=" * 70)

print(
    result_df.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    os.path.abspath(
        OUTPUT_FILE
    )
)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
