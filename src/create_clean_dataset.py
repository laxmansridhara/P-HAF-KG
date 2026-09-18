import pandas as pd

columns = [
    "code",
    "product_name",
    "ingredients_text",
    "allergens",
    "categories",
    "labels",
    "brands",
    "nutriscore_grade",
    "nova_group"
]

input_file = "data/en.openfoodfacts.org.products (1).csv"
output_file = "results/clean_food_dataset.csv"

first_chunk = True
total_rows = 0

for chunk in pd.read_csv(
    input_file,
    sep="\t",
    usecols=columns,
    chunksize=50000,
    low_memory=False,
):
    chunk.to_csv(
        output_file,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False,
    )

    total_rows += len(chunk)
    print(f"Processed {total_rows:,} rows...")

    first_chunk = False

print("\nDone!")
print(f"Saved cleaned dataset to: {output_file}")