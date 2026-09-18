from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.5
# False Positive and False Negative Error Instances
#
# REAL SOURCE:
# data/processed/ml/gold_test/p_haf_kg_error_analysis_500.csv
#
# The CSV stores errors as semicolon-separated allergen lists
# in the "missed" and "false_positive" columns.
# We therefore count individual allergen instances rather than
# counting products.
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
    / "p_haf_kg_error_analysis_500.csv"
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
    / "figure_5_5_error_analysis_fp_fn.png"
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

print("\nLoading error-analysis CSV...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "missed",
    "false_positive"
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
# 7. COUNT INDIVIDUAL ALLEGEN INSTANCES
# ------------------------------------------------------------

def count_allergen_instances(series):
    """
    Count semicolon-separated allergen entries.

    Empty / NaN entries are ignored.
    """

    total = 0

    for value in series:

        if pd.isna(value):
            continue

        text = str(value).strip()

        if not text:
            continue

        allergens = [
            item.strip()
            for item in text.split(";")
            if item.strip()
        ]

        total += len(allergens)

    return total


false_negative_count = count_allergen_instances(
    df["missed"]
)


false_positive_count = count_allergen_instances(
    df["false_positive"]
)


# ------------------------------------------------------------
# 8. COUNT PRODUCTS WITH EACH ERROR TYPE
# ------------------------------------------------------------

fn_products = (
    df["missed"]
    .notna()
    .sum()
)

fp_products = (
    df["false_positive"]
    .notna()
    .sum()
)


# ------------------------------------------------------------
# 9. PRINT ACTUAL RESULTS
# ------------------------------------------------------------

print("\nREAL ERROR RESULTS")
print("=" * 70)

print(
    f"False-negative allergen instances : "
    f"{false_negative_count}"
)

print(
    f"False-positive allergen instances : "
    f"{false_positive_count}"
)

print()

print(
    f"Products containing false negatives : "
    f"{fn_products}"
)

print(
    f"Products containing false positives : "
    f"{fp_products}"
)

print("=" * 70)


# ------------------------------------------------------------
# 10. VERIFY EXPECTED PROJECT COUNTS
# ------------------------------------------------------------

print("\nCOUNT CHECK")

if false_negative_count == 198:
    print("✓ False negatives = 198")
else:
    print(
        f"WARNING: false negatives = "
        f"{false_negative_count}"
    )


if false_positive_count == 277:
    print("✓ False positives = 277")
else:
    print(
        f"WARNING: false positives = "
        f"{false_positive_count}"
    )


# ------------------------------------------------------------
# 11. PLOT DATA
# ------------------------------------------------------------

labels = [
    "False Positive",
    "False Negative"
]


values = [
    false_positive_count,
    false_negative_count
]


# ------------------------------------------------------------
# 12. CREATE FIGURE
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
# 13. TITLE
# ------------------------------------------------------------

ax.set_title(
    "P-HAF-KG False Positive and False Negative Error Instances",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 14. AXIS LABELS
# ------------------------------------------------------------

ax.set_ylabel(
    "Allergen Error Instances",
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
# 15. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 16. BAR LABELS
# ------------------------------------------------------------

maximum = max(values)


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
# 17. SAVE
# ------------------------------------------------------------

fig.tight_layout()


fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)


plt.close(fig)


# ------------------------------------------------------------
# 18. VERIFY OUTPUT
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 70)

print(
    "Figure 5.5 generated from the actual error-analysis CSV."
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

print("=" * 70)