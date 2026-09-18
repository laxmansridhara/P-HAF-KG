import csv
from pathlib import Path

TEST_FILE = Path("data/processed/test.csv")
REVIEW_FILE = Path("data/processed/tfidf_error_review.csv")
BACKUP_FILE = Path("data/processed/test_before_review.csv")


def normalize_code(value):
    """
    Normalize product codes so that:
    00000259 -> 259
    00259    -> 259
    259      -> 259
    """
    value = str(value).strip()

    if not value:
        return ""

    normalized = value.lstrip("0")

    # If the code consists entirely of zeros
    if normalized == "":
        return "0"

    return normalized


# ==================================================
# LOAD TEST SET
# ==================================================

with TEST_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    test_rows = list(csv.DictReader(f))


if not test_rows:
    raise ValueError("test.csv is empty.")


# ==================================================
# LOAD REVIEW FILE
# ==================================================

with REVIEW_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    review_rows = list(csv.DictReader(f))


if not review_rows:
    raise ValueError("tfidf_error_review.csv is empty.")


# ==================================================
# BUILD REVIEW DICTIONARY
# ==================================================

reviews = {}

for row in review_rows:

    decision = row[
        "review_decision"
    ].strip().upper()

    if decision not in ("KEEP", "CHANGE"):
        continue

    code = normalize_code(
        row["code"]
    )

    reviews[code] = {
        "decision": decision,

        "confirmed": row[
            "reviewed_confirmed_allergens"
        ].strip(),

        "potential": row[
            "reviewed_potential_allergens"
        ].strip(),

        "notes": row[
            "review_notes"
        ].strip(),
    }


# ==================================================
# BACKUP ORIGINAL TEST SET
# ==================================================

fields = list(test_rows[0].keys())

with BACKUP_FILE.open(
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


print("Backup created:")
print(BACKUP_FILE)


# ==================================================
# APPLY REVIEW
# ==================================================

reviewed = 0
changed = 0
kept = 0


for row in test_rows:

    code = normalize_code(
        row["code"]
    )

    if code not in reviews:
        continue

    review = reviews[code]

    reviewed += 1

    # ----------------------------------------------
    # CHANGE
    # ----------------------------------------------

    if review["decision"] == "CHANGE":

        row["confirmed_allergens"] = (
            review["confirmed"]
        )

        row["potential_allergens"] = (
            review["potential"]
        )

        row["evidence_level"] = "REVIEWED"

        changed += 1

    # ----------------------------------------------
    # KEEP
    # ----------------------------------------------

    elif review["decision"] == "KEEP":

        # Keep the existing confirmed/potential
        # labels but mark the product as reviewed.
        row["evidence_level"] = "REVIEWED"

        kept += 1


# ==================================================
# FIND UNMATCHED REVIEW CODES
# ==================================================

test_codes = {
    normalize_code(row["code"])
    for row in test_rows
}

unmatched = []

for code in reviews:

    if code not in test_codes:
        unmatched.append(code)


# ==================================================
# SAVE UPDATED TEST SET
# ==================================================

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


# ==================================================
# FINAL REPORT
# ==================================================

print()
print("===== REVIEW APPLICATION =====")

print(
    "Test products:",
    len(test_rows)
)

print(
    "Review entries:",
    len(reviews)
)

print(
    "Reviewed cases:",
    reviewed
)

print(
    "Changed labels:",
    changed
)

print(
    "Kept labels:",
    kept
)

print(
    "Expected reviewed cases:",
    20
)

print(
    "Expected changed labels:",
    9
)

print(
    "Expected kept labels:",
    11
)

if unmatched:

    print()
    print(
        "WARNING - Unmatched review codes:"
    )

    for code in unmatched:
        print(code)

else:

    print()
    print(
        "All review codes matched successfully."
    )

print()
print("Backup:")
print(BACKUP_FILE)

print()
print("Updated:")
print(TEST_FILE)
