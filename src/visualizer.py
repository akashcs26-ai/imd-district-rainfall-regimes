import matplotlib.pyplot as plt
def plot_pareto(df, save_path="reports/figures/q10_pareto.png"):
    top20 = df.groupby("district")["Heavy_Rain_Days"].sum().sort_values(ascending=False).head(20)
    cum_pct = top20.cumsum() / top20.sum() * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    # ... your ax.bar, twinx, ax2.plot, labels and title lines from explore.py ...
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()