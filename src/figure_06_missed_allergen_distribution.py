from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.6
# Missed Allergen Distribution
#
# REAL SOURCE:
# data/processed/ml/gold_test/
# p_haf_kg_error_analysis_500.csv
#
# The "missed" column contains semicolon-separated allergen
# categories for each product. This script counts the actual
# missed allergen instances by category.
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
    / "figure_5_6_missed_allergen_distribution.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD ACTUAL CSV
# ------------------------------------------------------------

print("\nLoading error-analysis CSV...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY COLUMN
# ------------------------------------------------------------

if "missed" not in df.columns:
    raise ValueError(
        "The CSV does not contain the required 'missed' column."
    )


# ------------------------------------------------------------
# 7. EXTRACT MISSED ALLERGENS
# ------------------------------------------------------------

missed_counts = {}


for value in df["missed"]:

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

    for allergen in allergens:

        missed_counts[allergen] = (
            missed_counts.get(
                allergen,
                0
            )
            + 1
        )


# ------------------------------------------------------------
# 8. CREATE DATAFRAME
# ------------------------------------------------------------

missed_df = pd.DataFrame(
    [
        {
            "allergen": allergen,
            "missed_instances": count
        }
        for allergen, count in missed_counts.items()
    ]
)


if missed_df.empty:
    raise ValueError(
        "No missed allergen instances were found."
    )


# ------------------------------------------------------------
# 9. SORT BY FREQUENCY
# ------------------------------------------------------------

missed_df = missed_df.sort_values(
    "missed_instances",
    ascending=True
).reset_index(
    drop=True
)


# ------------------------------------------------------------
# 10. PRINT REAL RESULTS
# ------------------------------------------------------------

print("\nREAL MISSED-ALLERGEN COUNTS")
print("=" * 70)

for _, row in missed_df.iterrows():

    print(
        f"{row['allergen']}: "
        f"{int(row['missed_instances'])}"
    )

print("=" * 70)


# ------------------------------------------------------------
# 11. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(11, 7)
)


y_positions = list(
    range(len(missed_df))
)


bars = ax.barh(
    y_positions,
    missed_df["missed_instances"]
)


# ------------------------------------------------------------
# 12. LABELS
# ------------------------------------------------------------

ax.set_yticks(
    y_positions
)

ax.set_yticklabels(
    missed_df["allergen"],
    fontsize=9
)


ax.set_xlabel(
    "Missed Allergen Instances",
    fontsize=11
)


ax.set_ylabel(
    "Allergen Category",
    fontsize=11
)


# ------------------------------------------------------------
# 13. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Distribution of Missed Allergen Instances by Category",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 14. GRID
# ------------------------------------------------------------

ax.grid(
    axis="x",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 15. BAR VALUE LABELS
# ------------------------------------------------------------

maximum = missed_df["missed_instances"].max()


for bar in bars:

    value = int(
        bar.get_width()
    )

    ax.text(
        bar.get_width()
        + maximum * 0.02,

        bar.get_y()
        + bar.get_height() / 2,

        str(value),

        va="center",

        fontsize=9
    )


# ------------------------------------------------------------
# 16. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 17. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 70)

print(
    "Figure 5.6 generated from the actual error-analysis CSV."
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