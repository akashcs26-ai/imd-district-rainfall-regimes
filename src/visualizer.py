import matplotlib.pyplot as plt
def plot_pareto(df, save_path="reports/figures/q10_pareto.png"):
    top20 = df.groupby("district")["Heavy_Rain_Days"].sum().sort_values(ascending=False).head(20)
    cum_pct = top20.cumsum() / top20.sum() * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(top20.index, top20.values, color="steelblue")
    ax.set_ylabel("Heavy rain days")
    ax.tick_params(axis="x", rotation=90)

    ax2 = ax.twinx()
    ax2.plot(top20.index, cum_pct.values, color="red", marker="o")
    ax2.set_ylabel("Cumulative %")

    plt.title("Top 20 districts by heavy rain days")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()