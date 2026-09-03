#!/usr/bin/env python3

"""
P-HAF-KG V2.1
END-TO-END IMAGE ANALYSIS PIPELINE

Image
  -> OCR
  -> P-HAF-KG allergen detection
  -> User allergy profile
  -> Personalised decision
  -> Explanation
  -> JSON
  -> Clean CSV

This script intentionally reuses the existing tested components.
It does not modify the frozen P-HAF-KG V2.1 model.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OCR_SCRIPT = BASE_DIR / "src" / "scan_and_analyse_label.py"

EXPORT_SCRIPT = BASE_DIR / "src" / "export_image_analysis_csv.py"

RESULT_JSON = (
    BASE_DIR
    / "data"
    / "processed"
    / "p_haf_kg_image_analysis_result.json"
)

RESULT_CSV = (
    BASE_DIR
    / "data"
    / "processed"
    / "p_haf_kg_image_analysis_result.csv"
)


# ============================================================
# RUN COMMAND
# ============================================================

def run_command(command, description):

    print()
    print("=" * 70)
    print(description)
    print("=" * 70)
    print()

    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"\n{description} failed "
            f"with exit code {result.returncode}."
        )


# ============================================================
# CHECK INPUT
# ============================================================

def check_image(image_path):

    image = Path(image_path)

    if not image.is_absolute():
        image = BASE_DIR / image

    if not image.exists():

        raise FileNotFoundError(
            f"Image not found:\n{image}"
        )

    return image.resolve()


# ============================================================
# LOAD FINAL JSON
# ============================================================

def load_result():

    if not RESULT_JSON.exists():

        raise FileNotFoundError(
            "Expected analysis JSON was not created:\n"
            f"{RESULT_JSON}"
        )

    with open(
        RESULT_JSON,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# SUMMARY
# ============================================================

def print_summary(data):

    print()
    print("=" * 70)
    print("P-HAF-KG V2.1 FINAL IMAGE ANALYSIS")
    print("=" * 70)
    print()

    print(
        "Decision:",
        data.get("decision", "")
    )

    print(
        "Risk:",
        data.get("risk", "")
    )

    print(
        "Matched user allergens:",
        data.get(
            "matched_user_allergens",
            ""
        )
    )

    print()

    print(
        "JSON:",
        RESULT_JSON
    )

    print(
        "CSV:",
        RESULT_CSV
    )

    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "===== P-HAF-KG V2.1 "
        "END-TO-END IMAGE PIPELINE ====="
    )

    print()

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python3 "
            "src/p_haf_kg_image_pipeline.py "
            "data/raw/food_label.jpg"
        )

        sys.exit(1)

    image = check_image(
        sys.argv[1]
    )

    print(
        "Input image:"
    )

    print(
        image
    )

    print()

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    run_command(
        [
            sys.executable,
            str(OCR_SCRIPT),
            str(image)
        ],
        "STEP 1: IMAGE -> OCR -> P-HAF-KG ANALYSIS"
    )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    run_command(
        [
            sys.executable,
            str(EXPORT_SCRIPT)
        ],
        "STEP 2: ANALYSIS JSON -> CLEAN CSV"
    )

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    data = load_result()

    print_summary(
        data
    )


if __name__ == "__main__":

    main()
