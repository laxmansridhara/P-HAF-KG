from pathlib import Path
import json
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.2
# Precision, Recall and F1 Comparison
#
# Source:
# data/processed/ml/gold_test/gold_500_final_metrics.json
#
# Values are read directly from the real evaluation output.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. INPUT FILE
# ------------------------------------------------------------

METRICS_FILE = (
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
    / "figure_5_2_precision_recall_f1.png"
)


# ------------------------------------------------------------
# 4. LOAD REAL RESULTS
# ------------------------------------------------------------

if not METRICS_FILE.exists():
    raise FileNotFoundError(
        f"Evaluation file not found:\n{METRICS_FILE}"
    )


with open(
    METRICS_FILE,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


# ------------------------------------------------------------
# 5. EXTRACT ACTUAL RESULTS
# ------------------------------------------------------------

models = data["models"]

svm = models["svm"]

kg = models["p_haf_kg"]


# ------------------------------------------------------------
# 6. METRIC LABELS
# ------------------------------------------------------------

metric_labels = [
    "Micro Precision",
    "Micro Recall",
    "Micro F1",
    "Macro Precision",
    "Macro Recall",
    "Macro F1"
]


svm_values = [
    svm["micro_precision"],
    svm["micro_recall"],
    svm["micro_f1"],
    svm["macro_precision"],
    svm["macro_recall"],
    svm["macro_f1"]
]


kg_values = [
    kg["micro_precision"],
    kg["micro_recall"],
    kg["micro_f1"],
    kg["macro_precision"],
    kg["macro_recall"],
    kg["macro_f1"]
]


# ------------------------------------------------------------
# 7. PRINT REAL VALUES
# ------------------------------------------------------------

print("\nREAL VALUES FROM gold_500_final_metrics.json")
print("=" * 70)

print("\nTF-IDF + Linear SVM")

print(f"Micro Precision : {svm['micro_precision']:.4f}")
print(f"Micro Recall    : {svm['micro_recall']:.4f}")
print(f"Micro F1        : {svm['micro_f1']:.4f}")
print(f"Macro Precision : {svm['macro_precision']:.4f}")
print(f"Macro Recall    : {svm['macro_recall']:.4f}")
print(f"Macro F1        : {svm['macro_f1']:.4f}")


print("\nP-HAF-KG V2.1")

print(f"Micro Precision : {kg['micro_precision']:.4f}")
print(f"Micro Recall    : {kg['micro_recall']:.4f}")
print(f"Micro F1        : {kg['micro_f1']:.4f}")
print(f"Macro Precision : {kg['macro_precision']:.4f}")
print(f"Macro Recall    : {kg['macro_recall']:.4f}")
print(f"Macro F1        : {kg['macro_f1']:.4f}")

print("=" * 70)


# ------------------------------------------------------------
# 8. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(12, 7)
)


x = list(range(len(metric_labels)))

width = 0.36


# ------------------------------------------------------------
# 9. BARS
# ------------------------------------------------------------

svm_bars = ax.bar(
    [i - width / 2 for i in x],
    svm_values,
    width,
    label="TF-IDF + Linear SVM"
)


kg_bars = ax.bar(
    [i + width / 2 for i in x],
    kg_values,
    width,
    label="P-HAF-KG V2.1"
)


# ------------------------------------------------------------
# 10. TITLE / AXES
# ------------------------------------------------------------

ax.set_title(
    "Precision, Recall and F1 Performance on the Independent 500-Product Gold Set",
    fontsize=14,
    pad=15
)

ax.set_ylabel(
    "Score",
    fontsize=11
)

ax.set_xticks(x)

ax.set_xticklabels(
    metric_labels,
    rotation=20,
    ha="right",
    fontsize=10
)

ax.set_ylim(
    0,
    1.0
)


# ------------------------------------------------------------
# 11. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 12. LABEL BARS
# ------------------------------------------------------------

def add_labels(bars):

    for bar in bars:

        value = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.02,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=8.5
        )


add_labels(svm_bars)

add_labels(kg_bars)


# ------------------------------------------------------------
# 13. LEGEND
# ------------------------------------------------------------

ax.legend(
    loc="upper left"
)


# ------------------------------------------------------------
# 14. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 15. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 70)

print("Figure 5.2 generated successfully.")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nFile exists:", OUTPUT_FILE.exists())

if OUTPUT_FILE.exists():
    print(
        "File size:",
        OUTPUT_FILE.stat().st_size,
        "bytes"
    )

print("=" * 70)