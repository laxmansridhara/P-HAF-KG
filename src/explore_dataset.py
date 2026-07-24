import os
import pandas as pd

DATA_DIR = "data"

csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

if not csv_files:
    raise FileNotFoundError("Copy your OpenFoodFacts CSV into the data folder.")

file_path = os.path.join(DATA_DIR, csv_files[0])

print("Reading:", file_path)

df = pd.read_csv(file_path, sep="\t", nrows=5, low_memory=False)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst five rows:")
print(df.head())
