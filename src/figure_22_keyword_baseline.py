from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 2.3
# Initial Keyword-Matching Baseline
#
# REAL SOURCE:
# data/processed/baseline_keyword_product_evaluation.csv
#
# The CSV contains product-level TP, FP, FN and exact-match
# results for the initial 27-product baseline evaluation.
#
# Aggregate micro metrics are calculated from the actual
# product-level results.
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
    / "baseline_keyword_product_evaluation.csv"
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
    / "figure_2_3_keyword_matching_baseline.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nBaseline file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL CSV
# ------------------------------------------------------------

print("\nLoading keyword-matching baseline...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "code",
    "product_name",
    "ground_truth",
    "prediction",
    "true_positive",
    "false_positive",
    "false_negative",
    "exact_match"
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
# 7. DISPLAY BASIC INFORMATION
# ------------------------------------------------------------

print(
    f"\nProducts evaluated: {len(df)}"
)


print("\nCSV columns:")

for column in df.columns:

    print(
        f"  - {column}"
    )


# ------------------------------------------------------------
# 8. CONVERT COUNT COLUMNS TO NUMERIC
# ------------------------------------------------------------

count_columns = [
    "true_positive",
    "false_positive",
    "false_negative"
]


for column in count_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0)


# ------------------------------------------------------------
# 9. CALCULATE ACTUAL AGGREGATE COUNTS
# ------------------------------------------------------------

total_true_positive = int(
    df["true_positive"].sum()
)


total_false_positive = int(
    df["false_positive"].sum()
)


total_false_negative = int(
    df["false_negative"].sum()
)


# ------------------------------------------------------------
# 10. CALCULATE MICRO METRICS
# ------------------------------------------------------------

precision_denominator = (
    total_true_positive
    + total_false_positive
)


recall_denominator = (
    total_true_positive
    + total_false_negative
)


if precision_denominator > 0:

    micro_precision = (
        total_true_positive
        / precision_denominator
    )

else:

    micro_precision = 0.0


if recall_denominator > 0:

    micro_recall = (
        total_true_positive
        / recall_denominator
    )

else:

    micro_recall = 0.0


if (
    micro_precision
    + micro_recall
) > 0:

    micro_f1 = (
        2
        * micro_precision
        * micro_recall
        / (
            micro_precision
            + micro_recall
        )
    )

else:

    micro_f1 = 0.0


# ------------------------------------------------------------
# 11. EXACT-MATCH RATE
# ------------------------------------------------------------

exact_match = (
    df["exact_match"]
    .fillna(False)
    .astype(str)
    .str.lower()
    .eq("true")
    .mean()
)


# ------------------------------------------------------------
# 12. PRINT REAL RESULTS
# ------------------------------------------------------------

print("\nREAL KEYWORD-BASELINE RESULTS")
print("=" * 75)

print(
    f"Products evaluated : "
    f"{len(df)}"
)

print(
    f"True positives     : "
    f"{total_true_positive}"
)

print(
    f"False positives    : "
    f"{total_false_positive}"
)

print(
    f"False negatives    : "
    f"{total_false_negative}"
)

print(
    f"Micro Precision    : "
    f"{micro_precision:.4f}"
)

print(
    f"Micro Recall       : "
    f"{micro_recall:.4f}"
)

print(
    f"Micro F1           : "
    f"{micro_f1:.4f}"
)

print(
    f"Exact Match        : "
    f"{exact_match:.4f}"
)

print("=" * 75)


# ------------------------------------------------------------
# 13. PREPARE FIGURE DATA
# ------------------------------------------------------------

labels = [
    "Micro Precision",
    "Micro Recall",
    "Micro F1",
    "Exact Match"
]


values = [
    micro_precision,
    micro_recall,
    micro_f1,
    exact_match
]


# ------------------------------------------------------------
# 14. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(10, 6.5)
)


x = list(
    range(len(labels))
)


bars = ax.bar(
    x,
    values
)


# ------------------------------------------------------------
# 15. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Initial Keyword-Matching Baseline on 27 Evaluated Products",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 16. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Score",
    fontsize=11
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    labels,
    fontsize=10
)


ax.set_ylim(
    0,
    1.0
)


# ------------------------------------------------------------
# 17. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 18. VALUE LABELS
# ------------------------------------------------------------

for bar, value in zip(
    bars,
    values
):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        value + 0.025,

        f"{value:.3f}",

        ha="center",
        va="bottom",

        fontsize=9
    )


# ------------------------------------------------------------
# 19. NOTE
# ------------------------------------------------------------

ax.text(
    0.5,
    0.02,

    "Development-stage keyword baseline; "
    "not the final independent 500-product evaluation.",

    transform=ax.transAxes,

    ha="center",

    fontsize=9
)


# ------------------------------------------------------------
# 20. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 21. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 2.3 keyword-matching baseline generated."
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

print("=" * 75)