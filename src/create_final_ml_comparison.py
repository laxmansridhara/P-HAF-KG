import pandas as pd
from pathlib import Path

# ============================================================
# P-HAF-KG V2.1 FINAL MODEL COMPARISON
# ============================================================

OUTPUT = Path(
    "data/processed/final_ml_model_comparison.csv"
)

models = [
    {
        "model": "Keyword baseline",
        "model_type": "Lexical / rule-based",
        "micro_f1": 0.6617,
        "macro_f1": 0.6079,
        "hamming_loss": 0.2381,
        "exact_match_rate": 0.2963,
    },
    {
        "model": "TF-IDF + Logistic Regression",
        "model_type": "Supervised ML",
        "micro_f1": 0.6789,
        "macro_f1": 0.6951,
        "hamming_loss": 0.1852,
        "exact_match_rate": 0.2593,
    },
    {
        "model": "TF-IDF + Linear SVM",
        "model_type": "Supervised ML",
        "micro_f1": 0.6972,
        "macro_f1": 0.5843,
        "hamming_loss": 0.1528,
        "exact_match_rate": 0.2963,
    },
    {
        "model": "TF-IDF + Random Forest",
        "model_type": "Supervised ML",
        "micro_f1": 0.7071,
        "macro_f1": 0.6316,
        "hamming_loss": 0.1343,
        "exact_match_rate": 0.3704,
    },
    {
        "model": "P-HAF-KG V2.1",
        "model_type": "Knowledge-based AI",
        "micro_f1": 0.9623,
        "macro_f1": 0.4932,
        "hamming_loss": 0.0106,
        "exact_match_rate": 0.8519,
    },
]

df = pd.DataFrame(models)

# ============================================================
# RANKING
# Higher is better for F1 and Exact Match
# Lower is better for Hamming Loss
# ============================================================

df["micro_f1_rank"] = (
    df["micro_f1"]
    .rank(ascending=False, method="min")
    .astype(int)
)

df["macro_f1_rank"] = (
    df["macro_f1"]
    .rank(ascending=False, method="min")
    .astype(int)
)

df["hamming_loss_rank"] = (
    df["hamming_loss"]
    .rank(ascending=True, method="min")
    .astype(int)
)

df["exact_match_rank"] = (
    df["exact_match_rate"]
    .rank(ascending=False, method="min")
    .astype(int)
)

# ============================================================
# IMPROVEMENT RELATIVE TO STRONGEST CONVENTIONAL ML MODEL
# Random Forest
# ============================================================

rf = df[
    df["model"] == "TF-IDF + Random Forest"
].iloc[0]

phaf = df[
    df["model"] == "P-HAF-KG V2.1"
].iloc[0]

micro_improvement = (
    (phaf["micro_f1"] - rf["micro_f1"])
    / rf["micro_f1"]
) * 100

hamming_reduction = (
    (rf["hamming_loss"] - phaf["hamming_loss"])
    / rf["hamming_loss"]
) * 100

exact_improvement = (
    (phaf["exact_match_rate"] - rf["exact_match_rate"])
    / rf["exact_match_rate"]
) * 100

print("=" * 75)
print("P-HAF-KG V2.1 FINAL MODEL COMPARISON")
print("=" * 75)

print(
    df[
        [
            "model",
            "model_type",
            "micro_f1",
            "macro_f1",
            "hamming_loss",
            "exact_match_rate",
            "micro_f1_rank",
            "macro_f1_rank",
            "hamming_loss_rank",
            "exact_match_rank",
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 75)
print("P-HAF-KG V2.1 vs RANDOM FOREST")
print("=" * 75)

print(
    f"Micro F1 improvement: "
    f"{micro_improvement:.2f}%"
)

print(
    f"Hamming Loss reduction: "
    f"{hamming_reduction:.2f}%"
)

print(
    f"Exact Match improvement: "
    f"{exact_improvement:.2f}%"
)

print("\n" + "=" * 75)
print("P-HAF-KG V2.1 RESULTS")
print("=" * 75)

print(
    f"Micro F1:       {phaf['micro_f1']:.4f}"
)

print(
    f"Macro F1:       {phaf['macro_f1']:.4f}"
)

print(
    f"Hamming Loss:   {phaf['hamming_loss']:.4f}"
)

print(
    f"Exact Match:    {phaf['exact_match_rate']:.4f}"
)

# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved:")
print(OUTPUT.resolve())

print("\n" + "=" * 75)
print("FINAL COMPARISON COMPLETE")
print("=" * 75)
