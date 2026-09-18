from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 2.4
# Initial AI/ML Model Comparison
#
# REAL SOURCE:
# data/processed/final_ml_model_comparison.csv
#
# This represents the earlier development/model-selection
# comparison in the project.
#
# It is NOT the final independent 500-product gold evaluation.
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
    / "final_ml_model_comparison.csv"
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
    / "figure_2_4_initial_ai_model_comparison.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nModel comparison file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL CSV
# ------------------------------------------------------------

print("\nLoading initial AI/ML model comparison...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "model",
    "model_type",
    "micro_f1",
    "macro_f1",
    "hamming_loss",
    "exact_match_rate"
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
# 7. PRINT REAL VALUES
# ------------------------------------------------------------

print("\nREAL MODEL-COMPARISON VALUES")
print("=" * 85)

print(
    df[
        [
            "model",
            "model_type",
            "micro_f1",
            "macro_f1",
            "hamming_loss",
            "exact_match_rate"
        ]
    ].to_string(index=False)
)

print("=" * 85)


# ------------------------------------------------------------
# 8. CREATE GROUPED COMPARISON
# ------------------------------------------------------------

models = df["model"].tolist()

micro_f1 = df["micro_f1"].tolist()

macro_f1 = df["macro_f1"].tolist()

exact_match = df["exact_match_rate"].tolist()


# ------------------------------------------------------------
# 9. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(15, 8)
)


x = list(
    range(len(models))
)


width = 0.25


bars_micro = ax.bar(
    [
        i - width
        for i in x
    ],
    micro_f1,
    width,
    label="Micro-F1"
)


bars_macro = ax.bar(
    x,
    macro_f1,
    width,
    label="Macro-F1"
)


bars_exact = ax.bar(
    [
        i + width
        for i in x
    ],
    exact_match,
    width,
    label="Exact Match"
)


# ------------------------------------------------------------
# 10. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Initial AI/ML Model Comparison",
    fontsize=15,
    pad=15
)


# ------------------------------------------------------------
# 11. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Score",
    fontsize=11
)


ax.set_xlabel(
    "Model",
    fontsize=11
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    models,
    rotation=25,
    ha="right",
    fontsize=9
)


ax.set_ylim(
    0,
    1.0
)


# ------------------------------------------------------------
# 12. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 13. VALUE LABELS
# ------------------------------------------------------------

def add_labels(bars):

    for bar in bars:

        value = bar.get_height()

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,

            value + 0.018,

            f"{value:.3f}",

            ha="center",
            va="bottom",

            fontsize=7.5
        )


add_labels(
    bars_micro
)


add_labels(
    bars_macro
)


add_labels(
    bars_exact
)


# ------------------------------------------------------------
# 14. LEGEND
# ------------------------------------------------------------

ax.legend(
    loc="upper left"
)


# ------------------------------------------------------------
# 15. DEVELOPMENT-STAGE NOTE
# ------------------------------------------------------------

ax.text(
    0.5,
    0.02,

    "Development-stage comparison; "
    "final independent evaluation is reported separately on the "
    "500-product gold set.",

    transform=ax.transAxes,

    ha="center",

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
print("=" * 85)

print(
    "Figure 2.4 initial AI/ML comparison generated."
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

print("=" * 85)