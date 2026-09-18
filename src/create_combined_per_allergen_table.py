import os
import pandas as pd

SVM_RF_FILE = (
    "data/processed/per_allergen_model_analysis.csv"
)

PHAF_FILE = (
    "data/processed/p_haf_kg_per_allergen_metrics.csv"
)

OUTPUT_FILE = (
    "data/processed/combined_per_allergen_comparison.csv"
)

print("=" * 70)
print("COMBINED PER-ALLERGEN MODEL COMPARISON")
print("=" * 70)

# ------------------------------------------------------------
# LOAD RESULTS
# ------------------------------------------------------------

ml_df = pd.read_csv(SVM_RF_FILE)

phaf_df = pd.read_csv(PHAF_FILE)

print("\nSVM/RF rows:", len(ml_df))
print("P-HAF-KG rows:", len(phaf_df))


# ------------------------------------------------------------
# COMBINE
# ------------------------------------------------------------

combined = pd.concat(
    [
        ml_df,
        phaf_df
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# REMOVE CLASSES WITH ZERO SUPPORT
# FROM DIRECT PERFORMANCE COMPARISON
# ------------------------------------------------------------

combined = combined[
    combined["support"] > 0
].copy()


# ------------------------------------------------------------
# ORDER MODELS
# ------------------------------------------------------------

model_order = [
    "TF-IDF + Linear SVM",
    "TF-IDF + Random Forest",
    "P-HAF-KG V2.1"
]

combined["model"] = pd.Categorical(
    combined["model"],
    categories=model_order,
    ordered=True
)

combined = combined.sort_values(
    ["allergen", "model"]
)


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

combined.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("COMBINED RESULTS")
print("=" * 70)

print(
    combined.to_string(
        index=False
    )
)

print("\nSaved:")
print(
    os.path.abspath(
        OUTPUT_FILE
    )
)

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)
