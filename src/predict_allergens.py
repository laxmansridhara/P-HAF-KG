#!/usr/bin/env python3

from pathlib import Path
import sys
import joblib


MODEL_DIR = Path("models/svm_allergen")

VECTORIZER_FILE = MODEL_DIR / "tfidf_vectorizer.joblib"
MODEL_FILE = MODEL_DIR / "svm_allergen_model.joblib"

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


def main():
    if len(sys.argv) < 2:
        print(
            'Usage:\n'
            'python src/predict_allergens.py '
            '"wheat flour, milk powder, soy lecithin"'
        )
        sys.exit(1)

    ingredient_text = " ".join(sys.argv[1:]).strip()

    if not ingredient_text:
        print("ERROR: Ingredient text is empty.")
        sys.exit(1)

    if not VECTORIZER_FILE.exists():
        print(f"ERROR: Missing vectorizer: {VECTORIZER_FILE}")
        sys.exit(1)

    if not MODEL_FILE.exists():
        print(f"ERROR: Missing model: {MODEL_FILE}")
        sys.exit(1)

    vectorizer = joblib.load(VECTORIZER_FILE)
    model = joblib.load(MODEL_FILE)

    X = vectorizer.transform([ingredient_text])

    prediction = model.predict(X)[0]

    print()
    print("=" * 70)
    print("P-HAF / SVM ALLERGEN PREDICTION")
    print("=" * 70)
    print()
    print("Ingredient text:")
    print(ingredient_text)
    print()

    detected = [
        allergen
        for allergen, value in zip(ALLERGENS, prediction)
        if int(value) == 1
    ]

    if detected:
        print("Predicted allergens:")
        for allergen in detected:
            print(f"  ✓ {allergen}")
    else:
        print("Predicted allergens:")
        print("  None")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
