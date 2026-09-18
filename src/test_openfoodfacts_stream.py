import csv
import time
from pathlib import Path

INPUT_FILE = Path(
    "data/en.openfoodfacts.org.products (1).csv"
)

MAX_ROWS = 10_000

print("=" * 70)
print("OPEN FOOD FACTS STREAMING TEST")
print("=" * 70)

print(f"Input: {INPUT_FILE}")
print(f"Test rows: {MAX_ROWS}")

start_time = time.time()

rows_read = 0
rows_with_ingredients = 0
rows_with_allergens = 0
food_candidates = 0

# ------------------------------------------------------------
# Open file
# ------------------------------------------------------------

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    reader = csv.DictReader(
        f,
        delimiter="\t"
    )

    # --------------------------------------------------------
    # Check columns
    # --------------------------------------------------------

    columns = reader.fieldnames

    print("\nColumns detected:", len(columns))

    required_columns = [
        "code",
        "product_name",
        "ingredients_text",
        "allergens",
        "categories",
        "countries"
    ]

    print("\nRequired columns:")

    for column in required_columns:

        if column in columns:
            print(f"  [OK] {column}")
        else:
            print(f"  [MISSING] {column}")

    # --------------------------------------------------------
    # Process rows
    # --------------------------------------------------------

    for row in reader:

        rows_read += 1

        ingredients = (
            row.get("ingredients_text") or ""
        ).strip()

        allergens = (
            row.get("allergens") or ""
        ).strip()

        categories = (
            row.get("categories") or ""
        ).strip()

        if ingredients:
            rows_with_ingredients += 1

        if allergens:
            rows_with_allergens += 1

        # Basic food candidate filter
        text = (
            ingredients + " " + categories
        ).lower()

        if ingredients and (
            "food" in text
            or "beverage" in text
            or "snack" in text
            or "chocolate" in text
            or "milk" in text
            or "bread" in text
            or "cereal" in text
        ):
            food_candidates += 1

        # Stop after MAX_ROWS
        if rows_read >= MAX_ROWS:
            break


elapsed = time.time() - start_time


# ------------------------------------------------------------
# Results
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("STREAMING TEST RESULTS")
print("=" * 70)

print(
    f"Rows read:              {rows_read:,}"
)

print(
    f"Rows with ingredients:  "
    f"{rows_with_ingredients:,}"
)

print(
    f"Rows with allergens:    "
    f"{rows_with_allergens:,}"
)

print(
    f"Food candidates:        "
    f"{food_candidates:,}"
)

print(
    f"Processing time:        "
    f"{elapsed:.2f} seconds"
)

if elapsed > 0:

    print(
        f"Rows/second:            "
        f"{rows_read / elapsed:,.0f}"
    )


# ------------------------------------------------------------
# First-row example
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DATA SAMPLE")
print("=" * 70)

with INPUT_FILE.open(
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as f:

    reader = csv.DictReader(
        f,
        delimiter="\t"
    )

    sample = next(reader)

    print(
        "\nProduct:"
    )

    print(
        sample.get(
            "product_name",
            ""
        )
    )

    print(
        "\nCode:"
    )

    print(
        sample.get(
            "code",
            ""
        )
    )

    print(
        "\nIngredients:"
    )

    print(
        (sample.get(
            "ingredients_text",
            ""
        ) or "")[:1000]
    )

    print(
        "\nOpen Food Facts allergens:"
    )

    print(
        sample.get(
            "allergens",
            ""
        )
    )

    print(
        "\nCategories:"
    )

    print(
        (sample.get(
            "categories",
            ""
        ) or "")[:500]
    )


print("\n" + "=" * 70)
print("STREAMING TEST COMPLETE")
print("=" * 70)
