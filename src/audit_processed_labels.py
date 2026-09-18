import csv
from pathlib import Path
from collections import Counter


# ============================================================
# P-HAF-KG V2.1
# PROCESSED OUTPUT AUDIT
# ============================================================

INPUT_FILE = Path(
    "data/processed/scan/p_haf_kg_v2_1_large_scale_4535553.csv"
)


# ============================================================
# COUNTERS
# ============================================================

total_rows = 0

confirmed_products = 0
potential_products = 0
both_products = 0
neither_products = 0

confirmed_counts = Counter()
potential_counts = Counter()

confirmed_per_product = Counter()
potential_per_product = Counter()

missing_code = 0
missing_product_name = 0


# ============================================================
# READ PROCESSED FILE
# ============================================================

print("=" * 70)
print("P-HAF-KG V2.1 PROCESSED OUTPUT AUDIT")
print("=" * 70)

print("\nInput:")
print(INPUT_FILE)

print("\nStarting audit...\n")


with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    # --------------------------------------------------------
    # Check columns
    # --------------------------------------------------------

    required_columns = {
        "code",
        "product_name",
        "confirmed_allergens",
        "potential_allergens",
        "direct_matches",
        "precautionary_matches",
        "special_threshold_matches",
    }

    actual_columns = set(reader.fieldnames or [])

    missing_columns = required_columns - actual_columns

    if missing_columns:
        print("ERROR: Missing columns:")
        for column in sorted(missing_columns):
            print("  -", column)

        print("\nActual columns:")
        print(reader.fieldnames)

        raise SystemExit(1)

    print("Columns verified:")
    for column in reader.fieldnames:
        print("  -", column)

    print()


    # ========================================================
    # PROCESS ROWS
    # ========================================================

    for row in reader:

        total_rows += 1

        # ----------------------------------------------------
        # Basic field checks
        # ----------------------------------------------------

        code = (row.get("code") or "").strip()
        product_name = (row.get("product_name") or "").strip()

        if not code:
            missing_code += 1

        if not product_name:
            missing_product_name += 1


        # ----------------------------------------------------
        # Confirmed allergens
        # ----------------------------------------------------

        confirmed_text = (
            row.get("confirmed_allergens") or ""
        ).strip()

        potential_text = (
            row.get("potential_allergens") or ""
        ).strip()


        confirmed = set()

        if confirmed_text:
            confirmed = {
                x.strip()
                for x in confirmed_text.split(";")
                if x.strip()
            }


        potential = set()

        if potential_text:
            potential = {
                x.strip()
                for x in potential_text.split(";")
                if x.strip()
            }


        # ----------------------------------------------------
        # Product-level classification
        # ----------------------------------------------------

        if confirmed:
            confirmed_products += 1

        if potential:
            potential_products += 1

        if confirmed and potential:
            both_products += 1

        if not confirmed and not potential:
            neither_products += 1


        # ----------------------------------------------------
        # Allergen counts
        # ----------------------------------------------------

        for allergen in confirmed:
            confirmed_counts[allergen] += 1

        for allergen in potential:
            potential_counts[allergen] += 1


        # ----------------------------------------------------
        # Number of allergens per product
        # ----------------------------------------------------

        confirmed_number = len(confirmed)
        potential_number = len(potential)

        if confirmed_number == 0:
            confirmed_per_product["0"] += 1
        elif confirmed_number == 1:
            confirmed_per_product["1"] += 1
        elif confirmed_number == 2:
            confirmed_per_product["2"] += 1
        else:
            confirmed_per_product["3+"] += 1


        if potential_number == 0:
            potential_per_product["0"] += 1
        elif potential_number == 1:
            potential_per_product["1"] += 1
        elif potential_number == 2:
            potential_per_product["2"] += 1
        else:
            potential_per_product["3+"] += 1


        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if total_rows % 100_000 == 0:
            print(
                f"Audited {total_rows:,} products..."
            )


# ============================================================
# RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)


# ============================================================
# PRODUCT COUNTS
# ============================================================

print("\nPRODUCT COUNTS")
print("-" * 70)

print(
    f"Total processed products:              {total_rows:,}"
)

print(
    f"Products with confirmed allergens:      {confirmed_products:,}"
)

print(
    f"Products with potential allergens:      {potential_products:,}"
)

print(
    f"Products with BOTH:                     {both_products:,}"
)

print(
    f"Products with NEITHER:                  {neither_products:,}"
)


# ============================================================
# PERCENTAGES
# ============================================================

if total_rows > 0:

    print("\nPRODUCT PERCENTAGES")
    print("-" * 70)

    print(
        f"Confirmed:   "
        f"{confirmed_products / total_rows * 100:.2f}%"
    )

    print(
        f"Potential:   "
        f"{potential_products / total_rows * 100:.2f}%"
    )

    print(
        f"Both:        "
        f"{both_products / total_rows * 100:.2f}%"
    )

    print(
        f"Neither:     "
        f"{neither_products / total_rows * 100:.2f}%"
    )


# ============================================================
# CONFIRMED ALLERGEN COUNTS
# ============================================================

print("\n")
print("=" * 70)
print("CONFIRMED ALLERGEN COUNTS")
print("=" * 70)

for allergen, count in sorted(
    confirmed_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    percentage = (
        count / total_rows * 100
        if total_rows
        else 0
    )

    print(
        f"{allergen:25s} "
        f"{count:10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# POTENTIAL ALLERGEN COUNTS
# ============================================================

print("\n")
print("=" * 70)
print("POTENTIAL ALLERGEN COUNTS")
print("=" * 70)

for allergen, count in sorted(
    potential_counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    percentage = (
        count / total_rows * 100
        if total_rows
        else 0
    )

    print(
        f"{allergen:25s} "
        f"{count:10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# CONFIRMED ALLERGENS PER PRODUCT
# ============================================================

print("\n")
print("=" * 70)
print("CONFIRMED ALLERGENS PER PRODUCT")
print("=" * 70)

for category in ["0", "1", "2", "3+"]:

    count = confirmed_per_product[category]

    percentage = (
        count / total_rows * 100
        if total_rows
        else 0
    )

    print(
        f"{category:5s} allergen(s): "
        f"{count:10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# POTENTIAL ALLERGENS PER PRODUCT
# ============================================================

print("\n")
print("=" * 70)
print("POTENTIAL ALLERGENS PER PRODUCT")
print("=" * 70)

for category in ["0", "1", "2", "3+"]:

    count = potential_per_product[category]

    percentage = (
        count / total_rows * 100
        if total_rows
        else 0
    )

    print(
        f"{category:5s} allergen(s): "
        f"{count:10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# DATA QUALITY
# ============================================================

print("\n")
print("=" * 70)
print("DATA QUALITY")
print("=" * 70)

print(
    f"Rows with missing code:          {missing_code:,}"
)

print(
    f"Rows with missing product name:   {missing_product_name:,}"
)


# ============================================================
# SUMMARY FOR DISSERTATION
# ============================================================

print("\n")
print("=" * 70)
print("DISSERTATION SUMMARY")
print("=" * 70)

print(
    f"""
P-HAF-KG V2.1 processed-output audit:

Total products analysed: {total_rows:,}

Products containing confirmed allergens:
{confirmed_products:,}

Products containing potential allergens:
{potential_products:,}

Products containing both confirmed and potential allergens:
{both_products:,}

Products containing neither:
{neither_products:,}

Knowledge-base output fields were successfully verified.
"""
)

print("=" * 70)
print("END")
print("=" * 70)
