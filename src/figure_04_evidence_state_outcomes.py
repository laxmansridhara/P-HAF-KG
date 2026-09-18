from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.4
# P-HAF-KG Evidence-State Outcomes
#
# REAL SOURCE:
# data/processed/ml/gold_test/
# p_haf_kg_gold_confirmed_outcomes_500.csv
#
# The CSV contains:
# gold_id
# allergen
# gold_confirmed
# kg_confirmed
# kg_potential
# error_type
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------
# 2. INPUT FILE
# ------------------------------------------------------------

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ml"
    / "gold_test"
    / "p_haf_kg_gold_confirmed_outcomes_500.csv"
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
    / "figure_5_4_evidence_state_outcomes.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT FILE
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL CSV
# ------------------------------------------------------------

print("\nLoading evidence-state evaluation CSV...")

df = pd.read_csv(INPUT_FILE)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. SHOW COLUMNS
# ------------------------------------------------------------

print("\nColumns found:")

for column in df.columns:
    print(f"  - {column}")


print(
    f"\nRows: {len(df)}"
)


# ------------------------------------------------------------
# 7. SHOW ERROR TYPES
# ------------------------------------------------------------

print("\nActual error_type values found:")

error_counts = (
    df["error_type"]
    .value_counts(dropna=False)
)

print(
    error_counts.to_string()
)


# ------------------------------------------------------------
# 8. VERIFY EXPECTED COLUMN
# ------------------------------------------------------------

if "error_type" not in df.columns:
    raise ValueError(
        "The CSV does not contain the required 'error_type' column."
    )


# ------------------------------------------------------------
# 9. MAP REAL ERROR TYPES TO EVIDENCE STATES
# ------------------------------------------------------------

def classify_error(error_type):

    value = str(error_type).strip().lower()

    if value == "correct_confirmed":
        return "Confirmed"

    if value == "detected_potential":
        return "Potential"

    if value == "completely_missed":
        return "Missed"

    return "Other"


df["evidence_state"] = (
    df["error_type"]
    .apply(classify_error)
)


# ------------------------------------------------------------
# 10. COUNT STATES
# ------------------------------------------------------------

state_counts = (
    df["evidence_state"]
    .value_counts()
)


confirmed_count = int(
    state_counts.get(
        "Confirmed",
        0
    )
)


potential_count = int(
    state_counts.get(
        "Potential",
        0
    )
)


missed_count = int(
    state_counts.get(
        "Missed",
        0
    )
)


other_count = int(
    state_counts.get(
        "Other",
        0
    )
)


# ------------------------------------------------------------
# 11. PRINT REAL COUNTS
# ------------------------------------------------------------

print("\nREAL EVIDENCE-STATE COUNTS")
print("=" * 70)

print(
    f"Confirmed : {confirmed_count}"
)

print(
    f"Potential : {potential_count}"
)

print(
    f"Missed    : {missed_count}"
)

print(
    f"Other     : {other_count}"
)

print("=" * 70)


# ------------------------------------------------------------
# 12. PRIMARY THREE STATES
# ------------------------------------------------------------

labels = [
    "Confirmed",
    "Potential",
    "Missed"
]


values = [
    confirmed_count,
    potential_count,
    missed_count
]


total = sum(values)


if total == 0:
    raise ValueError(
        "No recognised evidence-state records were found."
    )


# ------------------------------------------------------------
# 13. CALCULATE PERCENTAGES
# ------------------------------------------------------------

percentages = [
    (value / total) * 100
    for value in values
]


print("\nPERCENTAGES")
print("=" * 70)

for label, value, percentage in zip(
    labels,
    values,
    percentages
):

    print(
        f"{label}: "
        f"{value} "
        f"({percentage:.2f}%)"
    )

print("=" * 70)


# ------------------------------------------------------------
# 14. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(10, 6)
)


x = list(
    range(len(labels))
)


bars = ax.bar(
    x,
    values
)


# ------------------------------------------------------------
# 15. TITLE
# ------------------------------------------------------------

ax.set_title(
    "P-HAF-KG Evidence-State Outcomes on the 500-Product Gold Set",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 16. AXIS LABELS
# ------------------------------------------------------------

ax.set_ylabel(
    "Gold-Confirmed Allergen Instances",
    fontsize=11
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    labels,
    fontsize=10
)


# ------------------------------------------------------------
# 17. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 18. LABEL BARS
# ------------------------------------------------------------

for bar, value, percentage in zip(
    bars,
    values,
    percentages
):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        bar.get_height()
        + total * 0.015,

        f"{value}\n({percentage:.2f}%)",

        ha="center",
        va="bottom",

        fontsize=10
    )


# ------------------------------------------------------------
# 19. SAVE
# ------------------------------------------------------------

fig.tight_layout()


fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)


plt.close(fig)


# ------------------------------------------------------------
# 20. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 70)

print(
    "Figure 5.4 generated from the actual CSV."
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