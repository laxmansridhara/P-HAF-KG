import json
from pathlib import Path
from datetime import datetime


OUTPUT_FILE = Path(
    "data/processed/p_haf_kg_v2_1_frozen_config.json"
)


config = {
    "model_name": "P-HAF-KG",
    "version": "2.1",
    "status": "FROZEN",
    "purpose": "Final full-dataset evaluation",

    "allergen_categories": [
        "celery",
        "wheat_gluten",
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
        "sulphites",
        "tree_nut"
    ],

    "knowledge_base": (
        "data/processed/"
        "ingredient_allergen_knowledge_14.csv"
    ),

    "evidence_layer": (
        "data/processed/"
        "p_haf_kg_evidence_14_v2_1.csv"
    ),

    "development_metrics": (
        "data/processed/"
        "p_haf_kg_14_v2_1_metrics.csv"
    ),

    "baseline_metrics": (
        "data/processed/"
        "baseline_keyword_metrics.csv"
    ),

    "development_products": 27,

    "development_results": {
        "micro_f1": 0.9623,
        "macro_f1": 0.4932,
        "macro_precision": 0.4949,
        "macro_recall": 0.4921,
        "hamming_loss": 0.0106,
        "exact_match_rate": 0.8519
    },

    "frozen_at": datetime.now().isoformat(
        timespec="seconds"
    ),

    "final_evaluation_rule": (
        "No further model or knowledge-base "
        "modifications after freezing."
    )
}


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        config,
        f,
        indent=4
    )


print(
    "===== P-HAF-KG V2.1 FROZEN ====="
)

print(
    "Model version: P-HAF-KG V2.1"
)

print(
    "Status: FROZEN"
)

print(
    "Development products: 27"
)

print()
print(
    "Final evaluation configuration saved to:"
)

print(
    OUTPUT_FILE
)
