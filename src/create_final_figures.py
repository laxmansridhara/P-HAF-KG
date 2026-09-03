#!/usr/bin/env python3

import csv
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "p_haf_kg_final_evaluation.csv"
)

FIGURES_DIR = (
    BASE_DIR
    / "data"
    / "figures"
)

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_metrics():

    metrics = {}

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["evaluation_type"] != "development":
                continue

            metric = row["metric"]

            metrics[metric] = {
                "baseline": float(row["baseline"]),
                "p_haf_kg": float(row["p_haf_kg"]),
            }

    return metrics


def create_comparison_figure(
    metric,
    baseline,
    p_haf,
    filename,
    ylabel,
    title
):

    labels = [
        "Keyword Baseline",
        "P-HAF-KG V2.1"
    ]

    values = [
        baseline,
        p_haf
    ]

    plt.figure(figsize=(8, 6))

    bars = plt.bar(
        labels,
        values
    )

    plt.ylabel(ylabel)
    plt.title(title)

    for bar, value in zip(
        bars,
        values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.4f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    output = FIGURES_DIR / filename

    plt.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output}"
    )


def main():

    print(
        "===== P-HAF-KG V2.1 FINAL FIGURES ====="
    )

    metrics = load_metrics()

    required = [
        "Micro F1",
        "Macro F1",
        "Hamming Loss",
        "Exact Match Rate"
    ]

    for metric in required:

        if metric not in metrics:

            raise RuntimeError(
                f"Missing metric: {metric}"
            )

    # --------------------------------------------------------
    # Micro F1
    # --------------------------------------------------------

    create_comparison_figure(
        "Micro F1",
        metrics["Micro F1"]["baseline"],
        metrics["Micro F1"]["p_haf_kg"],
        "fig_micro_f1_comparison.png",
        "Micro F1",
        "Micro F1: Keyword Baseline vs P-HAF-KG V2.1"
    )

    # --------------------------------------------------------
    # Macro F1
    # --------------------------------------------------------

    create_comparison_figure(
        "Macro F1",
        metrics["Macro F1"]["baseline"],
        metrics["Macro F1"]["p_haf_kg"],
        "fig_macro_f1_comparison.png",
        "Macro F1",
        "Macro F1: Keyword Baseline vs P-HAF-KG V2.1"
    )

    # --------------------------------------------------------
    # Hamming Loss
    # --------------------------------------------------------

    create_comparison_figure(
        "Hamming Loss",
        metrics["Hamming Loss"]["baseline"],
        metrics["Hamming Loss"]["p_haf_kg"],
        "fig_hamming_loss_comparison.png",
        "Hamming Loss",
        "Hamming Loss: Keyword Baseline vs P-HAF-KG V2.1"
    )

    # --------------------------------------------------------
    # Exact Match Rate
    # --------------------------------------------------------

    create_comparison_figure(
        "Exact Match Rate",
        metrics["Exact Match Rate"]["baseline"],
        metrics["Exact Match Rate"]["p_haf_kg"],
        "fig_exact_match_comparison.png",
        "Exact Match Rate",
        "Exact Match Rate: Keyword Baseline vs P-HAF-KG V2.1"
    )

    # --------------------------------------------------------
    # Combined figure
    # --------------------------------------------------------

    labels = [
        "Micro F1",
        "Macro F1",
        "Exact Match Rate"
    ]

    baseline_values = [
        metrics["Micro F1"]["baseline"],
        metrics["Macro F1"]["baseline"],
        metrics["Exact Match Rate"]["baseline"]
    ]

    phaf_values = [
        metrics["Micro F1"]["p_haf_kg"],
        metrics["Macro F1"]["p_haf_kg"],
        metrics["Exact Match Rate"]["p_haf_kg"]
    ]

    x = range(len(labels))

    width = 0.35

    plt.figure(figsize=(10, 6))

    baseline_bars = plt.bar(
        [i - width / 2 for i in x],
        baseline_values,
        width,
        label="Keyword Baseline"
    )

    phaf_bars = plt.bar(
        [i + width / 2 for i in x],
        phaf_values,
        width,
        label="P-HAF-KG V2.1"
    )

    plt.xticks(
        list(x),
        labels
    )

    plt.ylabel("Score")
    plt.title(
        "Overall Development Performance Comparison"
    )

    plt.legend()

    for bar, value in zip(
        baseline_bars,
        baseline_values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f}",
            ha="center",
            va="bottom"
        )

    for bar, value in zip(
        phaf_bars,
        phaf_values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    combined_output = (
        FIGURES_DIR
        / "fig_overall_performance_comparison.png"
    )

    plt.savefig(
        combined_output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {combined_output}"
    )

    print()
    print(
        "===== FIGURE GENERATION COMPLETE ====="
    )


if __name__ == "__main__":
    main()
