import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv("data/processed/cleaned_data.csv", sep=";")
print(df.head())
print(df.columns)
print(df.shape)
day_cols = df.columns[3:]
df["Monthly_Total"] = df[day_cols].sum(axis=1)
df["Heavy_Rain_Days"] = (df[day_cols] >= 64.5).sum(axis=1)
df["Rainy_Days"] = (df[day_cols] >= 2.5).sum(axis=1)
df["Max_Daily_Rain"] = df[day_cols].max(axis=1)
print(df[["district", "month", "Monthly_Total", "Heavy_Rain_Days"]].head(10))
from src.visualizer import plot_pareto, plot_state_boxplot, plot_state_heatmap, make_dashboard, plot_correlation_heatmap, plot_violin_tiers, plot_envelope
plot_pareto(df)
plot_state_boxplot(df)
plot_state_heatmap(df)
make_dashboard(df)
plot_correlation_heatmap(df)
plot_violin_tiers(df)
plot_envelope(df)