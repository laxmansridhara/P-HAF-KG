import os
import pandas as pd


TEST_FILE = "data/processed/test.csv"

KEYWORD_PREDICTIONS = (
    "data/processed/baseline_keyword_predictions.csv"
)

TFIDF_PREDICTIONS = (
    "data/processed/baseline_tfidf_predictions.csv"
)

OUTPUT_FILE = (
    "data/processed/baseline_exact_match_metrics.csv"
)


def parse_labels(value):
    if pd.isna(value):
        return set()

    value = str(value).strip()

    if not value:
        return set()

    return {
        x.strip().lower()
        for x in value.split(";")
        if x.strip()
    }


def find_prediction_column(df):
    candidates = [
        "predicted_allergens",
        "prediction",
        "predictions",
        "predicted_labels",
        "labels"
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        "Could not find prediction column. "
        f"Available columns: {df.columns.tolist()}"
    )


def calculate_exact_match(
    true_file,
    prediction_file,
    model_name
):

    true_df = pd.read_csv(true_file)
    pred_df = pd.read_csv(prediction_file)

    if len(true_df) != len(pred_df):
        raise ValueError(
            f"{model_name}: row count mismatch. "
            f"True={len(true_df)}, "
            f"Predictions={len(pred_df)}"
        )

    true_column = "confirmed_allergens"

    if true_column not in true_df.columns:
        raise ValueError(
            f"Missing '{true_column}' in test file."
        )

    pred_column = find_prediction_column(pred_df)

    true_labels = (
        true_df[true_column]
        .apply(parse_labels)
        .tolist()
    )

    predicted_labels = (
        pred_df[pred_column]
        .apply(parse_labels)
        .tolist()
    )

    exact_matches = [
        true_set == pred_set
        for true_set, pred_set
        in zip(true_labels, predicted_labels)
    ]

    exact_match_rate = (
        sum(exact_matches)
        / len(exact_matches)
    )

    return {
        "model": model_name,
        "test_products": len(true_labels),
        "exact_matches": sum(exact_matches),
        "exact_match_rate": exact_match_rate,
        "prediction_file": prediction_file
    }


print("=" * 70)
print("BASELINE EXACT MATCH CALCULATION")
print("=" * 70)

results = []


# ------------------------------------------------------------
# KEYWORD
# ------------------------------------------------------------

if os.path.exists(KEYWORD_PREDICTIONS):

    results.append(
        calculate_exact_match(
            TEST_FILE,
            KEYWORD_PREDICTIONS,
            "Keyword baseline"
        )
    )

else:

    print(
        "\nWARNING: Keyword prediction file not found:"
    )

    print(KEYWORD_PREDICTIONS)


# ------------------------------------------------------------
# TF-IDF
# ------------------------------------------------------------

if os.path.exists(TFIDF_PREDICTIONS):

    results.append(
        calculate_exact_match(
            TEST_FILE,
            TFIDF_PREDICTIONS,
            "TF-IDF baseline"
        )
    )

else:

    print(
        "\nWARNING: TF-IDF prediction file not found:"
    )

    print(TFIDF_PREDICTIONS)


# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------

result_df = pd.DataFrame(results)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

if len(result_df) > 0:

    print(
        result_df.to_string(
            index=False
        )
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nSaved:")
    print(os.path.abspath(OUTPUT_FILE))

else:

    print(
        "No prediction files were found."
    )

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)
