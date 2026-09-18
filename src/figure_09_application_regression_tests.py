from pathlib import Path
import json
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.9
# Application Regression Testing
#
# REAL SOURCE:
# data/processed/application_tests/
# application_regression_test_results.json
#
# The figure uses the actual recorded regression-test result.
# OCR is shown separately as not tested in this run.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. INPUT JSON
# ------------------------------------------------------------

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "application_tests"
    / "application_regression_test_results.json"
)


# ------------------------------------------------------------
# 3. OUTPUT FOLDER
# ------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "figure_5_9_application_regression_tests.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nTest results file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL RESULTS
# ------------------------------------------------------------

print("\nLoading application regression-test results...")

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


predictor = data["test_run"]["predictor_test"]

ocr = data["test_run"]["ocr_test"]


# ------------------------------------------------------------
# 6. EXTRACT ACTUAL VALUES
# ------------------------------------------------------------

checks_passed = predictor["checks_passed"]

checks_expected = predictor["checks_expected"]

predictor_status = predictor["status"]

ocr_status = ocr["status"]


# ------------------------------------------------------------
# 7. PRINT REAL RESULTS
# ------------------------------------------------------------

print("\nREAL APPLICATION TEST RESULTS")
print("=" * 70)

print(
    f"Predictor checks : "
    f"{checks_passed}/{checks_expected}"
)

print(
    f"Predictor status : "
    f"{predictor_status}"
)

print(
    f"OCR status       : "
    f"{ocr_status}"
)

print("=" * 70)


# ------------------------------------------------------------
# 8. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(10, 6)
)


labels = [
    "Predictor checks passed"
]


values = [
    checks_passed
]


bars = ax.bar(
    labels,
    values
)


# ------------------------------------------------------------
# 9. AXES
# ------------------------------------------------------------

ax.set_ylim(
    0,
    max(checks_expected, checks_passed) + 1
)


ax.set_ylabel(
    "Number of Passed Checks",
    fontsize=11
)


ax.set_title(
    "Application Predictor Regression Testing",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 10. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 11. BAR LABEL
# ------------------------------------------------------------

for bar in bars:

    value = int(
        bar.get_height()
    )

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        bar.get_height()
        + 0.08,

        f"{value}/{checks_expected}",

        ha="center",
        va="bottom",

        fontsize=12
    )


# ------------------------------------------------------------
# 12. OCR NOTE
# ------------------------------------------------------------

ax.text(
    0.5,
    0.08,

    f"OCR test status: {ocr_status}",

    transform=ax.transAxes,

    ha="center",

    fontsize=10
)


# ------------------------------------------------------------
# 13. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 14. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 70)

print(
    "Figure 5.9 generated from the actual "
    "application regression-test JSON."
)

print("\nSaved to:")
print(OUTPUT_FILE)

print(
    "\nFile exists:",
    OUTPUT_FILE.exists()
)

if OUTPUT_FILE.exists():

    print(
        "File size:",
        OUTPUT_FILE.stat().st_size,
        "bytes"
    )

print("=" * 70)