from pathlib import Path
import json
import subprocess
import sys


# ============================================================
# APPLICATION REGRESSION TEST RESULTS
#
# Runs the actual predictor test script and records the
# resulting pass/fail status.
#
# OCR is NOT included here because test_tesseract_ocr.py
# requires an image path and has not yet been executed.
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "application_tests"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "application_regression_test_results.json"
)


PREDICTOR_TEST = (
    PROJECT_ROOT
    / "src"
    / "test_predict_food.py"
)


# ------------------------------------------------------------
# RUN ACTUAL PREDICTOR TEST
# ------------------------------------------------------------

print("\nRunning predictor regression test...")

result = subprocess.run(
    [
        sys.executable,
        str(PREDICTOR_TEST)
    ],
    cwd=PROJECT_ROOT,
    capture_output=True,
    text=True
)


stdout = result.stdout

stderr = result.stderr


# ------------------------------------------------------------
# DETERMINE TEST RESULT
# ------------------------------------------------------------

predictor_passed = (
    result.returncode == 0
    and
    "ALL PREDICTOR TESTS PASSED" in stdout
)


# Count explicit PASS lines
pass_lines = [
    line.strip()
    for line in stdout.splitlines()
    if line.strip().startswith("PASS:")
]


predictor_checks = len(pass_lines)


# ------------------------------------------------------------
# BUILD RESULTS
# ------------------------------------------------------------

results = {
    "test_run": {
        "predictor_test": {
            "status": (
                "PASSED"
                if predictor_passed
                else "FAILED"
            ),
            "checks_passed": predictor_checks,
            "checks_expected": 3,
            "passed": predictor_passed,
            "return_code": result.returncode,
            "pass_messages": pass_lines
        },
        "ocr_test": {
            "status": "NOT_RUN",
            "reason": (
                "OCR test requires an image path and "
                "was therefore not included in this run."
            )
        }
    }
}


# ------------------------------------------------------------
# SAVE JSON
# ------------------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        results,
        file,
        indent=2
    )


# ------------------------------------------------------------
# PRINT RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)

print("APPLICATION REGRESSION TEST RESULTS")

print("=" * 70)

print(
    f"Predictor checks passed: "
    f"{predictor_checks}/3"
)

print(
    "Predictor status: "
    + results["test_run"]["predictor_test"]["status"]
)

print(
    "OCR status: "
    + results["test_run"]["ocr_test"]["status"]
)

print("\nSaved to:")

print(OUTPUT_FILE)

print(
    "\nFile exists:",
    OUTPUT_FILE.exists()
)

print("=" * 70)


# ------------------------------------------------------------
# DISPLAY STDERR IF PRESENT
# ------------------------------------------------------------

if stderr.strip():

    print("\nWarnings / stderr from predictor test:")

    print(stderr)