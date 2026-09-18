from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.3
# Per-Allergen F1 Comparison
#
# Source:
# data/processed/ml/gold_test/gold_500_per_allergen_metrics.csv
#
# Values are read directly from the actual project output.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. INPUT CSV
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
    / "figure_5_3_per_allergen_f1.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput CSV not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL DATA
# ------------------------------------------------------------

print("\nLoading per-allergen evaluation CSV...")

df = pd.read_csv(INPUT_FILE)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY COLUMNS
# ------------------------------------------------------------

required_columns = [
    "model",
    "allergen",
    "support",
    "precision",
    "recall",
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


print("\nColumns found:")

for column in df.columns:
    print(f"  - {column}")


# ------------------------------------------------------------
# 7. DISPLAY ACTUAL MODEL NAMES
# ------------------------------------------------------------

print("\nModels found in CSV:")

for model in df["model"].dropna().unique():
    print(f"  - {model}")


# ------------------------------------------------------------
# 8. USE THE EXACT MODEL NAMES FROM THE CSV
# ------------------------------------------------------------

SVM_MODEL = "TF-IDF + Linear SVM"

KG_MODEL = "P-HAF-KG V2.1"


# ------------------------------------------------------------
# 9. FILTER PRIMARY COMPARISON MODELS
# ------------------------------------------------------------

plot_df = df[
    df["model"].isin(
        [
            SVM_MODEL,
            KG_MODEL
        ]
    )
].copy()


if plot_df.empty:
    raise ValueError(
        "No rows were found for the expected model names."
    )


# ------------------------------------------------------------
# 10. CHECK THAT BOTH MODELS EXIST
# ------------------------------------------------------------

models_found = set(
    plot_df["model"].unique()
)


if SVM_MODEL not in models_found:
    raise ValueError(
        f"Missing model in CSV: {SVM_MODEL}"
    )


if KG_MODEL not in models_found:
    raise ValueError(
        f"Missing model in CSV: {KG_MODEL}"
    )


# ------------------------------------------------------------
# 11. LIST ALL ALLERGENS
# ------------------------------------------------------------

allergens = (
    plot_df["allergen"]
    .dropna()
    .unique()
    .tolist()
)


print(
    f"\nAllergen categories found: {len(allergens)}"
)


for allergen in allergens:
    print(
        f"  - {allergen}"
    )


# ------------------------------------------------------------
# 12. PRINT ACTUAL F1 VALUES
# ------------------------------------------------------------

print("\nREAL F1 VALUES USED FOR FIGURE 5.3")
print("=" * 75)

for allergen in allergens:

    rows = plot_df[
        plot_df["allergen"] == allergen
    ]

    print(f"\n{allergen}")

    for _, row in rows.iterrows():

        print(
            f"  {row['model']}: "
            f"F1={row['f1']:.4f}, "
            f"support={int(row['support'])}"
        )

print("=" * 75)


# ------------------------------------------------------------
# 13. PIVOT TO WIDE FORMAT
# ------------------------------------------------------------

f1_table = plot_df.pivot(
    index="allergen",
    columns="model",
    values="f1"
)


# ------------------------------------------------------------
# 14. ORDER THE 13 PRIMARY ALLERGENS
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


available_order = [
    allergen
    for allergen in preferred_order
    if allergen in f1_table.index
]


remaining = [
    allergen
    for allergen in f1_table.index
    if allergen not in available_order
]


final_order = (
    available_order
    + remaining
)


f1_table = f1_table.loc[
    final_order
]


# ------------------------------------------------------------
# 15. PREPARE VALUES
# ------------------------------------------------------------

svm_values = f1_table[
    SVM_MODEL
].tolist()


kg_values = f1_table[
    KG_MODEL
].tolist()


x = list(
    range(len(f1_table.index))
)


width = 0.36


# ------------------------------------------------------------
# 16. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(14, 7)
)


svm_bars = ax.bar(
    [
        i - width / 2
        for i in x
    ],
    svm_values,
    width,
    label="TF-IDF + Linear SVM"
)


kg_bars = ax.bar(
    [
        i + width / 2
        for i in x
    ],
    kg_values,
    width,
    label="P-HAF-KG V2.1"
)


# ------------------------------------------------------------
# 17. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Per-Allergen F1 Performance on the Independent 500-Product Gold Set",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 18. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "F1 Score",
    fontsize=11
)

ax.set_xlabel(
    "Allergen Category",
    fontsize=11
)

ax.set_xticks(x)

ax.set_xticklabels(
    f1_table.index,
    rotation=35,
    ha="right",
    fontsize=9
)

ax.set_ylim(
    0,
    1.0
)


# ------------------------------------------------------------
# 19. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 20. BAR LABELS
# ------------------------------------------------------------

def add_labels(bars):

    for bar in bars:

        value = bar.get_height()

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 0.018,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=7.5
        )


add_labels(svm_bars)

add_labels(kg_bars)


# ------------------------------------------------------------
# 21. LEGEND
# ------------------------------------------------------------

ax.legend(
    loc="upper left"
)


# ------------------------------------------------------------
# 22. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 23. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.3 generated from the actual "
    "gold_500_per_allergen_metrics.csv."
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