from pathlib import Path
import json
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.1
# Overall Model Comparison
#
# Source:
# data/processed/ml/gold_test/gold_500_final_metrics.json
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
# 3. CORRECT FIGURE OUTPUT FOLDER
# ------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_5_1_overall_model_comparison.png"
)


# ------------------------------------------------------------
# 4. LOAD REAL EVALUATION RESULTS
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
hybrid = models["hybrid"]


# ------------------------------------------------------------
# 6. PRINT VALUES
# ------------------------------------------------------------

print("\nREAL VALUES FROM gold_500_final_metrics.json")
print("=" * 65)

print("\nTF-IDF + Linear SVM")
print(f"Micro-F1    : {svm['micro_f1']:.4f}")
print(f"Macro-F1    : {svm['macro_f1']:.4f}")
print(f"Exact Match : {svm['exact_match']:.4f}")

print("\nP-HAF-KG V2.1")
print(f"Micro-F1    : {kg['micro_f1']:.4f}")
print(f"Macro-F1    : {kg['macro_f1']:.4f}")
print(f"Exact Match : {kg['exact_match']:.4f}")

print("\nHybrid")
print(f"Micro-F1    : {hybrid['micro_f1']:.4f}")
print(f"Macro-F1    : {hybrid['macro_f1']:.4f}")
print(f"Exact Match : {hybrid['exact_match']:.4f}")

print("=" * 65)


# ------------------------------------------------------------
# 7. PREPARE PLOT DATA
# ------------------------------------------------------------

model_names = [
    "TF-IDF + Linear SVM",
    "P-HAF-KG V2.1",
    "Hybrid"
]

micro_f1 = [
    svm["micro_f1"],
    kg["micro_f1"],
    hybrid["micro_f1"]
]

macro_f1 = [
    svm["macro_f1"],
    kg["macro_f1"],
    hybrid["macro_f1"]
]

exact_match = [
    svm["exact_match"],
    kg["exact_match"],
    hybrid["exact_match"]
]


# ------------------------------------------------------------
# 8. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(11, 6.5)
)


x = list(range(len(model_names)))

width = 0.24


bars1 = ax.bar(
    [i - width for i in x],
    micro_f1,
    width,
    label="Micro-F1"
)

bars2 = ax.bar(
    x,
    macro_f1,
    width,
    label="Macro-F1"
)

bars3 = ax.bar(
    [i + width for i in x],
    exact_match,
    width,
    label="Exact Match"
)


# ------------------------------------------------------------
# 9. TITLES / AXES
# ------------------------------------------------------------

ax.set_title(
    "Overall Model Performance on the Independent 500-Product Gold Set",
    fontsize=14,
    pad=15
)

ax.set_ylabel(
    "Score",
    fontsize=11
)

ax.set_xticks(x)

ax.set_xticklabels(
    model_names,
    fontsize=10
)

ax.set_ylim(
    0,
    1.0
)


# ------------------------------------------------------------
# 10. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 11. BAR LABELS
# ------------------------------------------------------------

def add_labels(bars):

    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=9
        )


add_labels(bars1)
add_labels(bars2)
add_labels(bars3)


# ------------------------------------------------------------
# 12. LEGEND
# ------------------------------------------------------------

ax.legend(
    loc="upper left"
)


# ------------------------------------------------------------
# 13. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 14. VERIFY FILE
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 65)

print("Figure 5.1 generated successfully.")

print("\nSaved exactly to:")

print(OUTPUT_FILE)

print("\nFile exists:", OUTPUT_FILE.exists())

if OUTPUT_FILE.exists():

    print(
        "File size:",
        OUTPUT_FILE.stat().st_size,
        "bytes"
    )

print("=" * 65)