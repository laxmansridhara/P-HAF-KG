import csv
from pathlib import Path


BASELINE_FILE = Path(
    "data/processed/baseline_keyword_metrics.csv"
)

PHAF_FILE = Path(
    "data/processed/p_haf_kg_14_v2_1_metrics.csv"
)

OUTPUT_FILE = Path(
    "data/processed/model_comparison_dev.csv"
)


# ============================================================
# CURRENT DEVELOPMENT RESULTS
# These are the values produced by the two evaluation scripts.
# ============================================================

results = [

    {
        "metric": "Micro Precision",
        "baseline": 0.5053,
        "p_haf_kg": None,
    },

    {
        "metric": "Micro Recall",
        "baseline": 0.9231,
        "p_haf_kg": None,
    },

    {
        "metric": "Micro F1",
        "baseline": 0.6531,
        "p_haf_kg": 0.9623,
    },

    {
        "metric": "Macro Precision",
        "baseline": 0.2571,
        "p_haf_kg": 0.4949,
    },

    {
        "metric": "Macro Recall",
        "baseline": 0.4563,
        "p_haf_kg": 0.4921,
    },

    {
        "metric": "Macro F1",
        "baseline": 0.3134,
        "p_haf_kg": 0.4932,
    },

    {
        "metric": "Hamming Loss",
        "baseline": 0.1349,
        "p_haf_kg": 0.0106,
    },

    {
        "metric": "Exact Match Rate",
        "baseline": 0.2963,
        "p_haf_kg": 0.8519,
    },
]


def calculate_improvement(
    baseline,
    proposed,
    lower_is_better=False
):

    if baseline is None or proposed is None:
        return None

    if baseline == 0:
        return None

    if lower_is_better:

        return (
            (baseline - proposed)
            / baseline
        ) * 100

    return (
        (proposed - baseline)
        / baseline
    ) * 100


# ============================================================
# CHECK INPUT FILES
# ============================================================

print(
    "===== P-HAF-KG MODEL COMPARISON ====="
)

print()

if BASELINE_FILE.exists():

    print(
        "Baseline metrics file: FOUND"
    )

else:

    print(
        "WARNING: baseline metrics file not found:"
    )

    print(
        BASELINE_FILE
    )


if PHAF_FILE.exists():

    print(
        "P-HAF-KG metrics file: FOUND"
    )

else:

    print(
        "WARNING: P-HAF-KG metrics file not found:"
    )

    print(
        PHAF_FILE
    )


# ============================================================
# CALCULATE COMPARISON
# ============================================================

print()
print(
    "===== DEVELOPMENT RESULTS ====="
)

print()

print(
    f"{'Metric':22}"
    f"{'Baseline':>12}"
    f"{'P-HAF-KG':>12}"
    f"{'Improvement':>15}"
)

print("-" * 61)


output_rows = []


for item in results:

    metric = item["metric"]

    baseline = item["baseline"]

    proposed = item["p_haf_kg"]


    # Hamming Loss is better when LOWER.
    lower_is_better = (
        metric == "Hamming Loss"
    )


    change = calculate_improvement(
        baseline,
        proposed,
        lower_is_better
    )


    baseline_text = (
        f"{baseline:.4f}"
        if baseline is not None
        else "N/A"
    )


    proposed_text = (
        f"{proposed:.4f}"
        if proposed is not None
        else "N/A"
    )


    change_text = (
        f"{change:.2f}%"
        if change is not None
        else "N/A"
    )


    print(
        f"{metric:22}"
        f"{baseline_text:>12}"
        f"{proposed_text:>12}"
        f"{change_text:>15}"
    )


    output_rows.append({

        "metric": metric,

        "keyword_baseline": baseline_text,

        "p_haf_kg_v2_1": proposed_text,

        "improvement_percent": change_text,

    })


# ============================================================
# SAVE COMPARISON
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "metric",
            "keyword_baseline",
            "p_haf_kg_v2_1",
            "improvement_percent",
        ]
    )

    writer.writeheader()

    writer.writerows(
        output_rows
    )


# ============================================================
# KEY FINDINGS
# ============================================================

print()

print(
    "===== KEY DEVELOPMENT FINDINGS ====="
)

print()

print(
    "Micro F1:"
)

print(
    "  Baseline : 65.31%"
)

print(
    "  P-HAF-KG : 96.23%"
)

print(
    "  Improvement: "
    f"{calculate_improvement(0.6531, 0.9623):.2f}%"
)

print()

print(
    "Macro F1:"
)

print(
    "  Baseline : 31.34%"
)

print(
    "  P-HAF-KG : 49.32%"
)

print(
    "  Improvement: "
    f"{calculate_improvement(0.3134, 0.4932):.2f}%"
)

print()

print(
    "Hamming Loss:"
)

print(
    "  Baseline : 0.1349"
)

print(
    "  P-HAF-KG : 0.0106"
)

print(
    "  Reduction: "
    f"{calculate_improvement(0.1349, 0.0106, True):.2f}%"
)

print()

print(
    "Exact Match Rate:"
)

print(
    "  Baseline : 29.63%"
)

print(
    "  P-HAF-KG : 85.19%"
)

print(
    "  Improvement: "
    f"{calculate_improvement(0.2963, 0.8519):.2f}%"
)

print()

print(
    "Saved to:"
)

print(
    OUTPUT_FILE
)