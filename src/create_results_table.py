#!/usr/bin/env python3

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "p_haf_kg_final_evaluation.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "chapter4_results_table.csv"
)


def main():

    print("===== CHAPTER 4 RESULTS TABLE =====")

    rows = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            if row["evaluation_type"] != "development":
                continue

            rows.append({
                "Metric": row["metric"],
                "Keyword Baseline": row["baseline"],
                "P-HAF-KG V2.1": row["p_haf_kg"],
                "Improvement (%)": row["improvement_percent"],
            })

    fields = [
        "Metric",
        "Keyword Baseline",
        "P-HAF-KG V2.1",
        "Improvement (%)",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("===== RESULTS =====")

    for row in rows:

        print(
            f"{row['Metric']:20s} "
            f"{row['Keyword Baseline']:>8s} "
            f"{row['P-HAF-KG V2.1']:>8s} "
            f"{row['Improvement (%)']:>8s}"
        )

    print()
    print("Saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
