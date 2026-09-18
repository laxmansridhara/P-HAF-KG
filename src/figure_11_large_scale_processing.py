from pathlib import Path
import csv
import matplotlib.pyplot as plt


# ============================================================
# FIGURE 5.10
# Large-Scale P-HAF-KG Dataset Processing
#
# REAL SOURCE:
# data/processed/scan/
# p_haf_kg_v2_1_large_scale_4535553.csv
#
# The script reads the actual processed CSV and counts:
#   - processed products
#   - products with confirmed allergens
#   - products with potential allergens
#
# No result counts are manually entered.
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
    / "scan"
    / "p_haf_kg_v2_1_large_scale_4535553.csv"
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
    / "figure_5_10_large_scale_dataset_processing.png"
)


# ------------------------------------------------------------
# 4. CHECK INPUT
# ------------------------------------------------------------

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}"
    )


# ------------------------------------------------------------
# 5. STREAM THROUGH THE REAL CSV
# ------------------------------------------------------------

print("\nReading large-scale P-HAF-KG output...")

processed_products = 0

confirmed_products = 0

potential_products = 0

confirmed_and_potential = 0


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as file:

    reader = csv.DictReader(file)


    # --------------------------------------------------------
    # 6. VERIFY COLUMNS
    # --------------------------------------------------------

    expected_columns = [
        "code",
        "product_name",
        "confirmed_allergens",
        "potential_allergens",
        "direct_matches",
        "precautionary_matches",
        "special_threshold_matches"
    ]


    missing_columns = [
        column
        for column in expected_columns
        if column not in reader.fieldnames
    ]


    if missing_columns:

        raise ValueError(
            "Missing expected columns: "
            + ", ".join(missing_columns)
        )


    # --------------------------------------------------------
    # 7. COUNT RECORDS
    # --------------------------------------------------------

    for row in reader:

        processed_products += 1


        confirmed = (
            str(
                row["confirmed_allergens"]
            ).strip()
        )


        potential = (
            str(
                row["potential_allergens"]
            ).strip()
        )


        has_confirmed = bool(
            confirmed
        )


        has_potential = bool(
            potential
        )


        if has_confirmed:

            confirmed_products += 1


        if has_potential:

            potential_products += 1


        if (
            has_confirmed
            and has_potential
        ):

            confirmed_and_potential += 1


# ------------------------------------------------------------
# 8. PRINT REAL RESULTS
# ------------------------------------------------------------

print("\nREAL LARGE-SCALE RESULTS")
print("=" * 75)

print(
    f"Processed product records : "
    f"{processed_products:,}"
)

print(
    f"Products with confirmed allergens : "
    f"{confirmed_products:,}"
)

print(
    f"Products with potential allergens : "
    f"{potential_products:,}"
)

print(
    f"Products with both confirmed and potential evidence : "
    f"{confirmed_and_potential:,}"
)

print("=" * 75)


# ------------------------------------------------------------
# 9. CALCULATE PERCENTAGES
# ------------------------------------------------------------

confirmed_percentage = (
    confirmed_products
    / processed_products
    * 100
)


potential_percentage = (
    potential_products
    / processed_products
    * 100
)


print("\nPERCENTAGES OF PROCESSED PRODUCTS")
print("=" * 75)

print(
    f"Confirmed allergen evidence : "
    f"{confirmed_percentage:.2f}%"
)

print(
    f"Potential allergen evidence : "
    f"{potential_percentage:.2f}%"
)

print("=" * 75)


# ------------------------------------------------------------
# 10. PREPARE PLOT
# ------------------------------------------------------------

labels = [
    "Processed products",
    "Confirmed-allergen products",
    "Potential-allergen products"
]


values = [
    processed_products,
    confirmed_products,
    potential_products
]


# ------------------------------------------------------------
# 11. CREATE FIGURE
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(11, 7)
)


x = list(
    range(
        len(labels)
    )
)


bars = ax.bar(
    x,
    values
)


# ------------------------------------------------------------
# 12. TITLE
# ------------------------------------------------------------

ax.set_title(
    "Large-Scale P-HAF-KG Dataset Processing",
    fontsize=15,
    pad=15
)


# ------------------------------------------------------------
# 13. AXES
# ------------------------------------------------------------

ax.set_ylabel(
    "Number of Product Records",
    fontsize=11
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    labels,
    rotation=15,
    ha="right",
    fontsize=10
)


# ------------------------------------------------------------
# 14. GRID
# ------------------------------------------------------------

ax.grid(
    axis="y",
    alpha=0.25
)

ax.set_axisbelow(True)


# ------------------------------------------------------------
# 15. VALUE LABELS
# ------------------------------------------------------------

maximum = max(
    values
)


for bar, value in zip(
    bars,
    values
):

    ax.text(
        bar.get_x()
        + bar.get_width() / 2,

        bar.get_height()
        + maximum * 0.02,

        f"{value:,}",

        ha="center",
        va="bottom",

        fontsize=10
    )


# ------------------------------------------------------------
# 16. SAVE
# ------------------------------------------------------------

fig.tight_layout()


fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)


plt.close(fig)


# ------------------------------------------------------------
# 17. VERIFY
# ------------------------------------------------------------

print("\nSUCCESS")
print("=" * 75)

print(
    "Figure 5.10 generated from the actual large-scale CSV."
)

print("\nSaved to:")

print(
    OUTPUT_FILE
)

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