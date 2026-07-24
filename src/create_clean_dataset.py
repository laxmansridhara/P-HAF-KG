import pandas as pd

# Load only required columns
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

df = pd.read_csv(
    "data/en.openfoodfacts.org.products (1).csv",
    sep="\t",
    usecols=columns,
    low_memory=False
)

print(df.head())

# Save cleaned dataset
df.to_csv(
    "results/clean_food_dataset.csv",
    index=False
)

print("\nDataset saved successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))