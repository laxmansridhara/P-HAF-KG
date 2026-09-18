from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.11
# Gold-Test Set Composition
#
# REAL SOURCE:
# data/processed/ml/gold_test/
# gold_test_annotation_completed.csv
#
# Composition is calculated directly from the actual
# gold_evidence_level column.
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
    / "gold_test_annotation_completed.csv"
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
    / "figure_5_11_gold_test_set_composition.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nGold annotation file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD ACTUAL CSV
# ------------------------------------------------------------

print("\nLoading gold-test annotation file...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY COLUMNS
# ------------------------------------------------------------

required_columns = [
    "gold_id",
    "gold_confirmed_allergens",
    "gold_potential_allergens",
    "gold_evidence_level",
    "review_status"
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
# 7. BASIC CHECK
# ------------------------------------------------------------

total_products = len(df)

print(
    f"\nTotal gold-test products: {total_products}"
)


# ------------------------------------------------------------
# 8. EVIDENCE-LEVEL COUNTS
# ------------------------------------------------------------

evidence_counts = (
    df["gold_evidence_level"]
    .fillna("missing")
    .astype(str)
    .str.strip()
    .str.lower()
    .value_counts()
)


print("\nACTUAL GOLD EVIDENCE-LEVEL COUNTS")
print("=" * 70)

for level, count in evidence_counts.items():

    print(
        f"{level}: {int(count)}"
    )

print("=" * 70)


# ------------------------------------------------------------
# 9. REQUIRED ORDER
# ------------------------------------------------------------

preferred_order = [
    "none",
    "direct",
    "precautionary",
    "mixed",
    "missing"
]


available_levels = [
    level
    for level in preferred_order
    if level in evidence_counts.index
]


remaining_levels = [
    level
    for level in evidence_counts.index
    if level not in available_levels
]


final_order = (
    available_levels
    + remaining_levels
)


counts = [
    int(evidence_counts[level])
    for level in final_order
]


percentages = [
    count / total_products * 100
    for count in counts
]


# ------------------------------------------------------------
# 10. PRINT PERCENTAGES
# ------------------------------------------------------------

print("\nGOLD-TEST COMPOSITION")
print("=" * 70)

for level, count, percentage in zip(
    final_order,
    counts,
    percentages
):

    print(
        f"{level}: "
        f"{count} "
        f"({percentage:.2f}%)"
    )

print("=" * 70)


# ------------------------------------------------------------
# 11. REVIEW STATUS CHECK
# ------------------------------------------------------------

print("\nREVIEW STATUS")
print("=" * 70)

review_counts = (
    df["review_status"]
    .fillna("missing")
    .astype(str)
    .str.strip()
    .str.lower()
    .value_counts()
)

for status, count in review_counts.items():

    print(
        f"{status}: {int(count)}"
    )

print("=" * 70)


# ------------------------------------------------------------
# 12. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(10, 6.5)
)


x = list(
    range(len(final_order))
)


bars = ax.bar(
    x,
    counts
)


# ------------------------------------------------------------
# 13. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Composition of the Independent 500-Product Gold Test Set",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 14. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Number of Products",
    fontsize=11
)


ax.set_xlabel(
    "Gold Evidence Level",
    fontsize=11
)


ax.set_xticks(
    x
)


display_labels = [
    level.replace(
        "_",
        " "
    ).title()
    for level in final_order
]


ax.set_xticklabels(
    display_labels,
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

maximum = max(
    counts
)


for bar, count, percentage in zip(
    bars,
    counts,
    percentages
):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        bar.get_height()
        + maximum * 0.02,

        f"{count}\n({percentage:.1f}%)",

        ha="center",
        va="bottom",

        fontsize=9
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
# 18. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 70)

print(
    "Figure 5.11 generated from the actual "
    "gold-test annotation CSV."
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

print("=" * 70)