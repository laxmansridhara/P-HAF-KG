from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.13
# Per-Allergen F1 Matrix
#
# REAL SOURCE:
# data/processed/ml/gold_test/gold_500_per_allergen_metrics.csv
#
# Values are read directly from the project output.
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
    / "gold_500_per_allergen_metrics.csv"
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
    / "figure_5_13_allergen_f1_matrix.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput CSV not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL CSV
# ------------------------------------------------------------

print("\nLoading per-allergen metrics...")

df = pd.read_csv(INPUT_FILE)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY COLUMNS
# ------------------------------------------------------------

required_columns = [
    "model",
    "allergen",
    "f1"
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
# 7. EXACT MODEL NAMES
# ------------------------------------------------------------

primary_models = [
    "TF-IDF + Linear SVM",
    "P-HAF-KG V2.1"
]


plot_df = df[
    df["model"].isin(primary_models)
].copy()


if plot_df.empty:
    raise ValueError(
        "No primary-model rows were found."
    )


# ------------------------------------------------------------
# 8. PIVOT
# ------------------------------------------------------------

matrix = plot_df.pivot(
    index="allergen",
    columns="model",
    values="f1"
)


# ------------------------------------------------------------
# 9. ORDER ALLERGENS
# ------------------------------------------------------------

preferred_order = [
    "celery",
    "crustaceans",
    "egg",
    "fish",
    "lupin",
    "milk",
    "molluscs",
    "mustard",
    "peanut",
    "sesame",
    "soy",
    "tree_nut",
    "wheat_gluten"
]


ordered_allergens = [
    allergen
    for allergen in preferred_order
    if allergen in matrix.index
]


remaining = [
    allergen
    for allergen in matrix.index
    if allergen not in ordered_allergens
]


matrix = matrix.loc[
    ordered_allergens + remaining
]


# ------------------------------------------------------------
# 10. PRINT ACTUAL VALUES
# ------------------------------------------------------------

print("\nREAL PER-ALLERGEN F1 MATRIX")
print("=" * 70)

print(
    matrix.to_string(
        float_format=lambda x: f"{x:.4f}"
    )
)

print("=" * 70)


# ------------------------------------------------------------
# 11. CREATE PLOT
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(8, 10)
)


image = ax.imshow(
    matrix.values,
    aspect="auto",
    vmin=0,
    vmax=1
)


# ------------------------------------------------------------
# 12. AXES
# ------------------------------------------------------------

ax.set_xticks(
    range(len(matrix.columns))
)

ax.set_xticklabels(
    [
        "TF-IDF + Linear SVM",
        "P-HAF-KG V2.1"
    ],
    rotation=20,
    ha="right",
    fontsize=9
)


ax.set_yticks(
    range(len(matrix.index))
)

ax.set_yticklabels(
    matrix.index,
    fontsize=9
)


# ------------------------------------------------------------
# 13. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Per-Allergen F1 Performance on the Independent Gold Set",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 14. VALUE LABELS
# ------------------------------------------------------------

for row in range(
    len(matrix.index)
):

    for column in range(
        len(matrix.columns)
    ):

        value = matrix.iloc[
            row,
            column
        ]

        ax.text(
            column,
            row,
            f"{value:.2f}",
            ha="center",
            va="center",
            fontsize=8
        )


# ------------------------------------------------------------
# 15. COLOR SCALE
# ------------------------------------------------------------

colorbar = fig.colorbar(
    image,
    ax=ax
)

colorbar.set_label(
    "F1 Score"
)


# ------------------------------------------------------------
# 16. LAYOUT
# ------------------------------------------------------------

fig.tight_layout()


# ------------------------------------------------------------
# 17. SAVE
# ------------------------------------------------------------

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
    "Figure 5.13 generated from the actual "
    "per-allergen metrics CSV."
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