import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv("data/processed/cleaned_data.csv", sep=";")
print(df.head())
print(df.columns)
print(df.shape)
day_cols = df.columns[3:]
df["Monthly_Total"] = df[day_cols].sum(axis=1)
df["Heavy_Rain_Days"] = (df[day_cols] >= 64.5).sum(axis=1)
print(df[["district", "month", "Monthly_Total", "Heavy_Rain_Days"]].head(10))
from src.visualizer import plot_pareto
plot_pareto(df)



