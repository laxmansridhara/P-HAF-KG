from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.8
# Hybrid SVM-Only Candidate Recovery by Allergen
#
# REAL SOURCE:
# data/processed/ml/gold_test/hybrid_gold_predictions.csv
#
# Values are derived directly from the actual project CSV.
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
    / "figure_5_8_hybrid_candidate_by_allergen.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL DATA
# ------------------------------------------------------------

print("\nLoading hybrid prediction CSV...")

df = pd.read_csv(INPUT_FILE)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY COLUMNS
# ------------------------------------------------------------

required_columns = [
    "gold_id",
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
# 7. PARSE ALLERGEN LISTS
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
# 8. BUILD CANDIDATE RECORDS
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

    # SVM predictions that were not already confirmed by KG
    svm_only = svm_allergens - kg_allergens

    for allergen in sorted(svm_only):

        candidate_records.append(
            {
                "gold_id": row["gold_id"],
                "allergen": allergen,
                "gold_supported": (
                    allergen in gold_allergens
                )
            }
        )


# ------------------------------------------------------------
# 9. CREATE CANDIDATE DATAFRAME
# ------------------------------------------------------------

candidate_df = pd.DataFrame(candidate_records)

if candidate_df.empty:
    raise ValueError(
        "No SVM-only candidates were found."
    )


# ------------------------------------------------------------
# 10. AGGREGATE BY ALLERGEN
# ------------------------------------------------------------

summary = (
    candidate_df
    .groupby("allergen")
    .agg(
        total_candidates=("allergen", "size"),
        gold_supported=("gold_supported", "sum")
    )
)

summary["unsupported"] = (
    summary["total_candidates"]
    - summary["gold_supported"]
)

summary["precision_percent"] = (
    summary["gold_supported"]
    / summary["total_candidates"]
    * 100
)


# ------------------------------------------------------------
# 11. SORT BY TOTAL CANDIDATES
# ------------------------------------------------------------

summary = summary.sort_values(
    "total_candidates",
    ascending=True
)


# ------------------------------------------------------------
# 12. PRINT REAL RESULTS
# ------------------------------------------------------------

print("\nREAL HYBRID CANDIDATE RESULTS BY ALLERGEN")
print("=" * 80)

for allergen, row in summary.iterrows():

    print(
        f"{allergen}: "
        f"total={int(row['total_candidates'])}, "
        f"supported={int(row['gold_supported'])}, "
        f"unsupported={int(row['unsupported'])}, "
        f"precision={row['precision_percent']:.2f}%"
    )

print("=" * 80)


# ------------------------------------------------------------
# 13. CREATE PLOT
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(12, 7)
)


y = list(
    range(len(summary))
)


width = 0.36


# ------------------------------------------------------------
# 14. TOTAL CANDIDATES
# ------------------------------------------------------------

candidate_bars = ax.barh(
    [i - width / 2 for i in y],
    summary["total_candidates"],
    width,
    label="Total SVM-only candidates"
)


# ------------------------------------------------------------
# 15. GOLD-SUPPORTED
# ------------------------------------------------------------

supported_bars = ax.barh(
    [i + width / 2 for i in y],
    summary["gold_supported"],
    width,
    label="Gold-supported candidates"
)


# ------------------------------------------------------------
# 16. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Hybrid SVM-Only Candidate Recovery by Allergen",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 17. AXES
# ------------------------------------------------------------

ax.set_xlabel(
    "Candidate Allergens",
    fontsize=11
)

ax.set_ylabel(
    "Allergen Category",
    fontsize=11
)

ax.set_yticks(
    y
)

ax.set_yticklabels(
    summary.index,
    fontsize=9
)


# ------------------------------------------------------------
# 18. GRID
# ------------------------------------------------------------

ax.grid(
    axis="x",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 19. VALUE LABELS
# ------------------------------------------------------------

maximum = summary["total_candidates"].max()


for bar in candidate_bars:

    value = int(
        bar.get_width()
    )

    ax.text(
        value + maximum * 0.02,
        bar.get_y()
        + bar.get_height() / 2,
        str(value),
        va="center",
        fontsize=8
    )


for bar in supported_bars:

    value = int(
        bar.get_width()
    )

    if value > 0:

        ax.text(
            value + maximum * 0.02,
            bar.get_y()
            + bar.get_height() / 2,
            str(value),
            va="center",
            fontsize=8
        )


# ------------------------------------------------------------
# 20. LEGEND
# ------------------------------------------------------------

ax.legend(
    loc="lower right"
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
print("=" * 80)

print(
    "Figure 5.8 generated from the actual "
    "hybrid_gold_predictions.csv."
)

print("\nSaved to:")
print(OUTPUT_FILE)

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

print("=" * 80)