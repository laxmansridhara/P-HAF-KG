import csv
from pathlib import Path

INPUT_FILE = Path(
    "data/processed/tfidf_error_analysis.csv"
)

OUTPUT_FILE = Path(
    "data/processed/tfidf_error_review.csv"
)


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    rows = list(csv.DictReader(f))


for row in rows:
    row["reviewed_confirmed_allergens"] = ""
    row["reviewed_potential_allergens"] = ""
    row["review_decision"] = ""
    row["review_notes"] = ""


fields = [
    "code",
    "product_name",
    "true_labels",
    "predicted_labels",
    "false_positives",
    "false_negatives",
    "evidence_level",
    "ingredients_text",
    "reviewed_confirmed_allergens",
    "reviewed_potential_allergens",
    "review_decision",
    "review_notes",
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
    writer.writerows(rows)


print("===== ERROR REVIEW FILE =====")
print("Cases:", len(rows))
print("Output:", OUTPUT_FILE)
