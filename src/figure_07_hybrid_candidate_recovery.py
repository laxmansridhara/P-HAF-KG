from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.7
# Hybrid SVM-Only Candidate Recovery
#
# REAL SOURCE:
# data/processed/ml/gold_test/hybrid_gold_predictions.csv
#
# Actual columns used:
#   gold_confirmed_allergens
#   kg_confirmed_allergens
#   svm_predicted_allergens
#
# Values are calculated from the actual 500-product CSV.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. INPUT FILE
# ------------------------------------------------------------

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ml"
    / "gold_test"
    / "hybrid_gold_predictions.csv"
)


# ------------------------------------------------------------
# 3. OUTPUT FOLDER
# ------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_5_7_hybrid_candidate_recovery.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL CSV
# ------------------------------------------------------------

print("\nLoading hybrid prediction CSV...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. SHOW COLUMNS
# ------------------------------------------------------------

print("\nColumns found:")

for column in df.columns:

    print(
        f"  - {column}"
    )


print(
    f"\nRows: {len(df)}"
)


# ------------------------------------------------------------
# 7. REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "gold_confirmed_allergens",
    "kg_confirmed_allergens",
    "svm_predicted_allergens"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    raise ValueError(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )


# ------------------------------------------------------------
# 8. PARSE ALLERGEN LISTS
# ------------------------------------------------------------

def parse_allergens(value):

    if pd.isna(value):

        return set()


    text = str(value).strip()


    if not text:

        return set()


    return {
        item.strip()
        for item in text.split(";")
        if item.strip()
    }


# ------------------------------------------------------------
# 9. FIND SVM-ONLY CANDIDATE ALLERGENS
# ------------------------------------------------------------

candidate_records = []


for _, row in df.iterrows():

    svm_allergens = parse_allergens(
        row["svm_predicted_allergens"]
    )


    kg_allergens = parse_allergens(
        row["kg_confirmed_allergens"]
    )


    gold_allergens = parse_allergens(
        row["gold_confirmed_allergens"]
    )


    # SVM predictions not already confirmed by KG
    svm_only_allergens = (
        svm_allergens
        - kg_allergens
    )


    for allergen in sorted(
        svm_only_allergens
    ):

        candidate_records.append(
            {
                "gold_id": row["gold_id"],
                "allergen": allergen,
                "gold_supported": (
                    allergen
                    in gold_allergens
                )
            }
        )


# ------------------------------------------------------------
# 10. BUILD CANDIDATE DATAFRAME
# ------------------------------------------------------------

candidate_df = pd.DataFrame(
    candidate_records
)


if candidate_df.empty:

    raise ValueError(
        "No SVM-only candidate allergens were found."
    )


# ------------------------------------------------------------
# 11. CALCULATE COUNTS
# ------------------------------------------------------------

total_candidates = len(
    candidate_df
)


supported_candidates = int(
    candidate_df["gold_supported"]
    .sum()
)


unsupported_candidates = (
    total_candidates
    - supported_candidates
)


candidate_precision = (
    supported_candidates
    / total_candidates
    * 100
)


# ------------------------------------------------------------
# 12. PRINT ACTUAL RESULTS
# ------------------------------------------------------------

print("\nREAL HYBRID CANDIDATE RESULTS")
print("=" * 72)

print(
    f"Total SVM-only candidates : "
    f"{total_candidates}"
)

print(
    f"Gold-supported candidates : "
    f"{supported_candidates}"
)

print(
    f"Unsupported candidates    : "
    f"{unsupported_candidates}"
)

print(
    f"Candidate precision       : "
    f"{candidate_precision:.2f}%"
)

print("=" * 72)


# ------------------------------------------------------------
# 13. BREAKDOWN BY ALLERGEN
# ------------------------------------------------------------

print("\nCANDIDATES BY ALLERGEN")
print("=" * 72)

by_allergen = (
    candidate_df
    .groupby("allergen")
    .agg(
        candidates=("allergen", "size"),
        supported=("gold_supported", "sum")
    )
)

by_allergen["unsupported"] = (
    by_allergen["candidates"]
    - by_allergen["supported"]
)


for allergen, row in by_allergen.iterrows():

    print(
        f"{allergen}: "
        f"total={int(row['candidates'])}, "
        f"supported={int(row['supported'])}, "
        f"unsupported={int(row['unsupported'])}"
    )

print("=" * 72)


# ------------------------------------------------------------
# 14. PLOT DATA
# ------------------------------------------------------------

labels = [
    "Gold-supported",
    "Unsupported"
]


values = [
    supported_candidates,
    unsupported_candidates
]


# ------------------------------------------------------------
# 15. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(9, 6)
)


x = list(
    range(len(labels))
)


bars = ax.bar(
    x,
    values
)


# ------------------------------------------------------------
# 16. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Hybrid SVM-Only Candidate Recovery on the 500-Product Gold Set",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 17. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Candidate Allergens",
    fontsize=11
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    labels,
    fontsize=10
)


# ------------------------------------------------------------
# 18. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 19. BAR LABELS
# ------------------------------------------------------------

maximum = max(
    values
)


for bar, value in zip(
    bars,
    values
):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        bar.get_height()
        + maximum * 0.02,

        str(value),

        ha="center",
        va="bottom",

        fontsize=11
    )


# ------------------------------------------------------------
# 20. PRECISION ANNOTATION
# ------------------------------------------------------------

ax.text(
    0.5,
    0.94,

    (
        "Gold-supported candidate precision: "
        f"{candidate_precision:.2f}%"
    ),

    transform=ax.transAxes,

    ha="center",

    fontsize=11
)


# ------------------------------------------------------------
# 21. SAVE
# ------------------------------------------------------------

fig.tight_layout()


fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)


plt.close(fig)


# ------------------------------------------------------------
# 22. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 72)

print(
    "Figure 5.7 generated from the actual "
    "hybrid_gold_predictions.csv."
)

print("\nSaved to:")

print(
    OUTPUT_FILE
)

print(
    "\nFile exists:",
    OUTPUT_FILE.exists()
)

if OUTPUT_FILE.exists():

    print(
        "File size:",
        OUTPUT_FILE.stat().st_size,
        "bytes"
    )

print("=" * 72)