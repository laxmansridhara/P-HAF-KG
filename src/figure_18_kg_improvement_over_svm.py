from pathlib import Path
import json
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.17
# P-HAF-KG V2.1 Improvement over TF-IDF + Linear SVM
#
# REAL SOURCE:
# data/processed/ml/gold_test/gold_500_final_metrics.json
#
# Percentage improvement is calculated from the actual stored
# model metrics:
#
# improvement (%) = ((P-HAF-KG - SVM) / SVM) * 100
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
    / "figure_5_17_kg_improvement_over_svm.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nMetrics file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL METRICS
# ------------------------------------------------------------

print("\nLoading final Gold-set metrics...")

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


# ------------------------------------------------------------
# 6. VERIFY STRUCTURE
# ------------------------------------------------------------

if "models" not in data:
    raise ValueError(
        "The metrics JSON does not contain a 'models' section."
    )


models = data["models"]


if "svm" not in models:
    raise ValueError(
        "SVM results were not found."
    )


if "p_haf_kg" not in models:
    raise ValueError(
        "P-HAF-KG results were not found."
    )


svm = models["svm"]

kg = models["p_haf_kg"]


# ------------------------------------------------------------
# 7. SELECT ACTUAL METRICS
# ------------------------------------------------------------

metrics = {
    "Micro-F1": (
        svm["micro_f1"],
        kg["micro_f1"]
    ),
    "Macro-F1": (
        svm["macro_f1"],
        kg["macro_f1"]
    ),
    "Exact Match": (
        svm["exact_match"],
        kg["exact_match"]
    )
}


# ------------------------------------------------------------
# 8. CALCULATE IMPROVEMENT
# ------------------------------------------------------------

improvements = {}


for metric_name, (
    svm_value,
    kg_value
) in metrics.items():

    if svm_value == 0:
        raise ValueError(
            f"SVM value for {metric_name} is zero; "
            "percentage improvement cannot be calculated."
        )

    improvement = (
        (kg_value - svm_value)
        / svm_value
        * 100
    )

    improvements[metric_name] = improvement


# ------------------------------------------------------------
# 9. PRINT REAL VALUES
# ------------------------------------------------------------

print("\nREAL GOLD-SET METRICS")
print("=" * 75)

for metric_name, (
    svm_value,
    kg_value
) in metrics.items():

    print(
        f"{metric_name}: "
        f"SVM={svm_value:.6f}, "
        f"P-HAF-KG={kg_value:.6f}"
    )


print("\nCALCULATED P-HAF-KG IMPROVEMENT")
print("=" * 75)

for metric_name, improvement in improvements.items():

    print(
        f"{metric_name}: "
        f"{improvement:.2f}%"
    )

print("=" * 75)


# ------------------------------------------------------------
# 10. PREPARE PLOT
# ------------------------------------------------------------

labels = list(
    improvements.keys()
)

values = [
    improvements[label]
    for label in labels
]


# ------------------------------------------------------------
# 11. CREATE FIGURE
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
# 12. TITLE
# ------------------------------------------------------------

ax.set_title(
    "P-HAF-KG V2.1 Improvement over the TF-IDF + Linear SVM Baseline",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 13. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Improvement over SVM (%)",
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
# 14. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 15. ZERO LINE
# ------------------------------------------------------------

ax.axhline(
    0,
    linewidth=1
)


# ------------------------------------------------------------
# 16. VALUE LABELS
# ------------------------------------------------------------

maximum = max(
    values
)


for bar, value in zip(
    bars,
    values
):

    offset = (
        maximum * 0.025
        if value >= 0
        else -maximum * 0.04
    )

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        value + offset,

        f"{value:.2f}%",

        ha="center",

        va=(
            "bottom"
            if value >= 0
            else "top"
        ),

        fontsize=10
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
print("=" * 75)

print(
    "Figure 5.17 generated from the actual Gold-set metrics."
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