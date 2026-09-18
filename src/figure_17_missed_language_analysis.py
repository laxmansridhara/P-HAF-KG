from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.16
# Language Signals in Completely Missed Allergen Instances
#
# REAL SOURCE:
# data/processed/ml/gold_test/
# p_haf_kg_111_missed_language_analysis.csv
#
# The language_signal field may contain multiple comma-
# separated language signals for one missed instance.
# Therefore the plotted language counts are signal occurrences,
# not mutually exclusive product counts.
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
    / "p_haf_kg_111_missed_language_analysis.csv"
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
    / "figure_5_16_missed_language_analysis.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. LOAD REAL CSV
# ------------------------------------------------------------

print("\nLoading missed-language analysis CSV...")

df = pd.read_csv(
    INPUT_FILE
)

print("CSV loaded successfully.")


# ------------------------------------------------------------
# 6. VERIFY COLUMNS
# ------------------------------------------------------------

required_columns = [
    "gold_id",
    "allergen",
    "gold_confirmed",
    "kg_confirmed",
    "kg_potential",
    "error_type",
    "language_signal"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )


# ------------------------------------------------------------
# 7. VERIFY ERROR TYPE
# ------------------------------------------------------------

error_types = (
    df["error_type"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

unexpected_types = sorted(
    set(error_types)
    - {"completely_missed"}
    - {""}
)

if unexpected_types:

    print(
        "\nWarning: unexpected error types found:"
    )

    for value in unexpected_types:
        print(
            f"  - {value}"
        )


# ------------------------------------------------------------
# 8. KEEP COMPLETELY MISSED INSTANCES
# ------------------------------------------------------------

missed_df = df[
    error_types == "completely_missed"
].copy()


if missed_df.empty:

    raise ValueError(
        "No completely_missed records were found."
    )


print(
    f"\nCompletely missed allergen instances: "
    f"{len(missed_df)}"
)


# ------------------------------------------------------------
# 9. EXTRACT LANGUAGE SIGNALS
# ------------------------------------------------------------

language_counts = {}


for value in missed_df["language_signal"]:

    if pd.isna(value):
        continue

    text = str(value).strip()

    if not text:
        continue

    signals = [
        item.strip().lower()
        for item in text.split(",")
        if item.strip()
    ]

    for signal in signals:

        language_counts[signal] = (
            language_counts.get(
                signal,
                0
            )
            + 1
        )


# ------------------------------------------------------------
# 10. CREATE DATAFRAME
# ------------------------------------------------------------

language_df = pd.DataFrame(
    [
        {
            "language_signal": signal,
            "count": count
        }
        for signal, count in language_counts.items()
    ]
)


if language_df.empty:

    raise ValueError(
        "No language signals were found."
    )


# ------------------------------------------------------------
# 11. SORT
# ------------------------------------------------------------

language_df = language_df.sort_values(
    "count",
    ascending=True
).reset_index(
    drop=True
)


# ------------------------------------------------------------
# 12. PRINT REAL RESULTS
# ------------------------------------------------------------

print("\nREAL LANGUAGE-SIGNAL COUNTS")
print("=" * 75)

for _, row in language_df.iterrows():

    print(
        f"{row['language_signal']}: "
        f"{int(row['count'])}"
    )

print("=" * 75)


# ------------------------------------------------------------
# 13. CREATE DISPLAY LABELS
# ------------------------------------------------------------

display_labels = []

for signal in language_df["language_signal"]:

    if signal == "english_or_unknown":

        label = "English / Unknown"

    else:

        label = signal.replace(
            "_",
            " "
        ).title()

    display_labels.append(
        label
    )


# ------------------------------------------------------------
# 14. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(11, 7)
)


y = list(
    range(len(language_df))
)


bars = ax.barh(
    y,
    language_df["count"]
)


# ------------------------------------------------------------
# 15. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Language Signals in Completely Missed Allergen Instances",
    fontsize=14,
    pad=15
)


# ------------------------------------------------------------
# 16. AXES
# ------------------------------------------------------------

ax.set_xlabel(
    "Missed Allergen Instances with Language Signal",
    fontsize=11
)

ax.set_ylabel(
    "Language Signal",
    fontsize=11
)


ax.set_yticks(
    y
)


ax.set_yticklabels(
    display_labels,
    fontsize=9
)


# ------------------------------------------------------------
# 17. GRID
# ------------------------------------------------------------

ax.grid(
    axis="x",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 18. BAR LABELS
# ------------------------------------------------------------

maximum = language_df["count"].max()


for bar in bars:

    value = int(
        bar.get_width()
    )

    ax.text(
        bar.get_width()
        + maximum * 0.02,

        bar.get_y()
        + bar.get_height() / 2,

        str(value),

        va="center",

        fontsize=9
    )


# ------------------------------------------------------------
# 19. NOTE ABOUT OVERLAP
# ------------------------------------------------------------

ax.text(
    0.5,
    -0.12,

    "Note: one missed instance may contain multiple language signals; "
    "counts are therefore not mutually exclusive.",

    transform=ax.transAxes,

    ha="center",

    fontsize=9
)


# ------------------------------------------------------------
# 20. SAVE
# ------------------------------------------------------------

fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


# ------------------------------------------------------------
# 21. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.16 generated from the actual "
    "missed-language analysis CSV."
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

print("=" * 75)