import os
import pandas as pd

OUTPUT = "data/processed/final_ml_model_comparison.csv"

# ------------------------------------------------------------
# RESULTS ALREADY VALIDATED IN THIS PROJECT
# ------------------------------------------------------------

results = [
    {
        "model": "Keyword baseline",
        "model_type": "Lexical / rule-based",
        "micro_f1": 0.6617,
        "macro_f1": 0.6079,
        "hamming_loss": 0.2381,
        "exact_match_rate": None,
    },
    {
        "model": "TF-IDF baseline",
        "model_type": "Statistical NLP",
        "micro_f1": 0.6789,
        "macro_f1": 0.6951,
        "hamming_loss": 0.1852,
        "exact_match_rate": None,
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

df = pd.DataFrame(results)

# ------------------------------------------------------------
# ADD RANKINGS
# ------------------------------------------------------------

df["micro_f1_rank"] = (
    df["micro_f1"]
    .rank(ascending=False, method="min")
    .astype("Int64")
)

df["macro_f1_rank"] = (
    df["macro_f1"]
    .rank(ascending=False, method="min")
    .astype("Int64")
)

df["hamming_loss_rank"] = (
    df["hamming_loss"]
    .rank(ascending=True, method="min")
    .astype("Int64")
)

df["exact_match_rank"] = (
    df["exact_match_rate"]
    .rank(ascending=False, method="min")
    .astype("Int64")
)

# ------------------------------------------------------------
# IMPROVEMENT OF P-HAF-KG OVER RANDOM FOREST
# ------------------------------------------------------------

rf = df[df["model"] == "TF-IDF + Random Forest"].iloc[0]
phaf = df[df["model"] == "P-HAF-KG V2.1"].iloc[0]

micro_improvement = (
    (phaf["micro_f1"] - rf["micro_f1"])
    / rf["micro_f1"]
    * 100
)

hamming_reduction = (
    (rf["hamming_loss"] - phaf["hamming_loss"])
    / rf["hamming_loss"]
    * 100
)

exact_improvement = (
    (phaf["exact_match_rate"] - rf["exact_match_rate"])
    / rf["exact_match_rate"]
    * 100
)

# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

df.to_csv(OUTPUT, index=False)

print("=" * 70)
print("FINAL ML MODEL COMPARISON")
print("=" * 70)

print(df.to_string(index=False))

print("\n" + "=" * 70)
print("P-HAF-KG V2.1 VS BEST CONVENTIONAL ML")
print("=" * 70)

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

print("\nSaved:")
print(os.path.abspath(OUTPUT))
