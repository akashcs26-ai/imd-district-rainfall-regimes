import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

file_path = project_folder / "data" / "raw" / "Indian Rainfall Dataset District-wise Daily Measurements.csv"

df = pd.read_csv(file_path, sep=";")

print("First five records:")
print(df.head())

print("\nDataset information:")
print(df.info())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())