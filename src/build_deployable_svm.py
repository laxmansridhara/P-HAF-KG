#!/usr/bin/env python3

from pathlib import Path
import json
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC


ROOT = Path(".")
TRAIN_FILE = ROOT / "data/processed/ml/train.csv"
VALIDATION_FILE = ROOT / "data/processed/ml/validation.csv"

MODEL_DIR = ROOT / "models/svm_allergen"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

ALLERGENS = [
    "celery",
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
    "tree_nut",
    "wheat_gluten",
]


def parse_labels(value):
    if pd.isna(value):
        return set()

    return {
        x.strip()
        for x in str(value).split(";")
        if x.strip() in ALLERGENS
    }


def load_data(path):
    df = pd.read_csv(path)

    df["ingredient_text"] = (
        df["ingredient_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[df["ingredient_text"] != ""].copy()

    for allergen in ALLERGENS:
        df[allergen] = df["confirmed_allergens"].apply(
            lambda x, a=allergen: int(a in parse_labels(x))
        )

    return df


def main():

    print("=" * 70)
    print("BUILD DEPLOYABLE TF-IDF + LINEAR SVM")
    print("=" * 70)

    train_df = load_data(TRAIN_FILE)
    validation_df = load_data(VALIDATION_FILE)

    df = pd.concat(
        [train_df, validation_df],
        ignore_index=True
    )

    print(f"Training rows: {len(df):,}")

    X_text = df["ingredient_text"]

    Y = df[ALLERGENS].values

    print("Building TF-IDF...")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.98,
        sublinear_tf=True,
        max_features=100_000,
    )

    X = vectorizer.fit_transform(X_text)

    print(f"TF-IDF features: {X.shape[1]:,}")

    print("Training Linear SVM...")

    model = OneVsRestClassifier(
        LinearSVC(
            C=1.0,
            max_iter=5000
        ),
        n_jobs=1
    )

    model.fit(X, Y)

    vectorizer_path = MODEL_DIR / "tfidf_vectorizer.joblib"
    model_path = MODEL_DIR / "svm_allergen_model.joblib"
    metadata_path = MODEL_DIR / "model_metadata.json"

    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(model, model_path)

    metadata = {
        "model": "TF-IDF + One-vs-Rest Linear SVM",
        "training_data": [
            str(TRAIN_FILE),
            str(VALIDATION_FILE)
        ],
        "training_rows": int(len(df)),
        "features": int(X.shape[1]),
        "ngram_range": [1, 2],
        "min_df": 2,
        "max_df": 0.98,
        "sublinear_tf": True,
        "max_features": 100000,
        "svm_C": 1.0,
        "max_iter": 5000,
        "allergens": ALLERGENS,
        "purpose": "Reusable deployment/inference model",
        "note": "Separate from frozen 500-product gold evaluation model."
    }

    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print()
    print("MODEL SAVED")
    print("-" * 70)
    print(vectorizer_path)
    print(model_path)
    print(metadata_path)
    print()
    print("Training complete.")


if __name__ == "__main__":
    main()
