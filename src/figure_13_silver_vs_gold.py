from pathlib import Path
import json
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.12
# Silver-Set vs Independent Gold-Set SVM Performance
#
# REAL SOURCES:
# data/processed/ml/svm_model/silver_test_metrics.json
# data/processed/ml/gold_test/gold_500_final_metrics.json
#
# Values are read directly from the project evaluation files.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. INPUT FILES
# ------------------------------------------------------------

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ml"
    / "svm_model"
    / "silver_test_metrics.json"
)

GOLD_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ml"
    / "gold_test"
    / "gold_500_final_metrics.json"
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
    / "figure_5_12_silver_vs_gold_performance.png"
)


# ------------------------------------------------------------
# 4. CHECK FILES
# ------------------------------------------------------------

if not SILVER_FILE.exists():

    raise FileNotFoundError(
        f"Silver metrics file not found:\n{SILVER_FILE}"
    )


if not GOLD_FILE.exists():

    raise FileNotFoundError(
        f"Gold metrics file not found:\n{GOLD_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL METRICS
# ------------------------------------------------------------

print("\nLoading Silver-set metrics...")

with open(
    SILVER_FILE,
    "r",
    encoding="utf-8"
) as file:

    silver = json.load(file)


print("Loading independent Gold-set metrics...")

with open(
    GOLD_FILE,
    "r",
    encoding="utf-8"
) as file:

    gold_data = json.load(file)


# ------------------------------------------------------------
# 6. EXTRACT SVM GOLD RESULTS
# ------------------------------------------------------------

if "models" not in gold_data:

    raise ValueError(
        "The Gold metrics JSON does not contain 'models'."
    )


if "svm" not in gold_data["models"]:

    raise ValueError(
        "The Gold metrics JSON does not contain SVM results."
    )


gold = gold_data["models"]["svm"]


# ------------------------------------------------------------
# 7. PREPARE ACTUAL VALUES
# ------------------------------------------------------------

metric_labels = [
    "Micro Precision",
    "Micro Recall",
    "Micro F1",
    "Macro Precision",
    "Macro Recall",
    "Macro F1",
    "Exact Match"
]


silver_values = [
    silver["micro_precision"],
    silver["micro_recall"],
    silver["micro_f1"],
    silver["macro_precision"],
    silver["macro_recall"],
    silver["macro_f1"],
    silver["exact_match"]
]


gold_values = [
    gold["micro_precision"],
    gold["micro_recall"],
    gold["micro_f1"],
    gold["macro_precision"],
    gold["macro_recall"],
    gold["macro_f1"],
    gold["exact_match"]
]


# ------------------------------------------------------------
# 8. PRINT REAL VALUES
# ------------------------------------------------------------

print("\nREAL SILVER-SET VALUES")
print("=" * 75)

for label, value in zip(
    metric_labels,
    silver_values
):

    print(
        f"{label}: {value:.4f}"
    )


print("\nREAL INDEPENDENT GOLD-SET VALUES")
print("=" * 75)

for label, value in zip(
    metric_labels,
    gold_values
):

    print(
        f"{label}: {value:.4f}"
    )

print("=" * 75)


# ------------------------------------------------------------
# 9. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(13, 7)
)


x = list(
    range(len(metric_labels))
)


width = 0.36


silver_bars = ax.bar(
    [
        i - width / 2
        for i in x
    ],
    silver_values,
    width,
    label="Silver test"
)


gold_bars = ax.bar(
    [
        i + width / 2
        for i in x
    ],
    gold_values,
    width,
    label="Independent 500-product gold test"
)


# ------------------------------------------------------------
# 10. TITLE
# ------------------------------------------------------------

ax.set_title(
    "TF-IDF + Linear SVM Performance: Silver Test vs Independent Gold Test",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 11. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Score",
    fontsize=11
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    metric_labels,
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

            value + 0.02,

            f"{value:.3f}",

            ha="center",
            va="bottom",

            fontsize=8
        )


add_labels(silver_bars)

add_labels(gold_bars)


# ------------------------------------------------------------
# 14. LEGEND
# ------------------------------------------------------------

ax.legend(
    loc="upper right"
)


# ------------------------------------------------------------
# 15. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 16. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.12 generated from the actual Silver and Gold "
    "evaluation JSON files."
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