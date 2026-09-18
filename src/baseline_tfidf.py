import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import precision_recall_fscore_support

INPUT_FILE = Path("data/processed/ground_truth_30.csv")

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
        return []

    return [
        x.strip()
        for x in value.split(";")
        if x.strip() in ALLERGENS
    ]


# --------------------------------------------------
# Load data
# --------------------------------------------------

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


# Remove uncertain examples for this first ML experiment.
rows = [
    row
    for row in rows
    if row["evidence_level"] == "DIRECT"
]

texts = [
    row["ingredients_text"]
    for row in rows
]

labels = [
    parse_labels(row["confirmed_allergens"])
    for row in rows
]


print("Usable products:", len(rows))


# --------------------------------------------------
# Convert labels to multi-label binary matrix
# --------------------------------------------------

mlb = MultiLabelBinarizer(
    classes=ALLERGENS
)

Y = mlb.fit_transform(labels)


# --------------------------------------------------
# Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    texts,
    Y,
    test_size=0.30,
    random_state=42
)


print("Training products:", len(X_train))
print("Testing products:", len(X_test))


# --------------------------------------------------
# TF-IDF
# --------------------------------------------------

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1,
    max_features=5000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


# --------------------------------------------------
# Logistic Regression
# --------------------------------------------------

model = OneVsRestClassifier(
    LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )
)

model.fit(
    X_train_tfidf,
    y_train
)


# --------------------------------------------------
# Prediction
# --------------------------------------------------

y_pred = model.predict(X_test_tfidf)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

precision, recall, f1, support = precision_recall_fscore_support(
    y_test,
    y_pred,
    average=None,
    zero_division=0
)


print("\n===== BASELINE 2: TF-IDF + LOGISTIC REGRESSION =====")

for i, allergen in enumerate(ALLERGENS):

    print(
        f"{allergen:15}"
        f" Precision={precision[i]:.4f}"
        f" Recall={recall[i]:.4f}"
        f" F1={f1[i]:.4f}"
        f" Support={support[i]}"
    )


macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
    y_test,
    y_pred,
    average="macro",
    zero_division=0
)

print("\nMacro averages:")
print(f"Precision: {macro_p:.4f}")
print(f"Recall:    {macro_r:.4f}")
print(f"F1:        {macro_f1:.4f}")
