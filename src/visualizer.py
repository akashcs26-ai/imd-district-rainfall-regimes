import matplotlib.pyplot as plt
import seaborn as sns
def plot_pareto(df, save_path="reports/figures/q10_pareto.png"):
    top20 = df.groupby(["state", "district"])["Heavy_Rain_Days"].sum().sort_values(ascending=False).head(20)
    cum_pct = top20.cumsum() / top20.sum() * 100
    labels = []
    for state, district in top20.index:
        labels.append(district + " (" + state + ")")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(labels, top20.values, color="steelblue")
    ax.set_ylabel("Heavy rain days")
    ax.tick_params(axis="x", rotation=90)

    ax2 = ax.twinx()
    ax2.plot(labels, cum_pct.values, color="red", marker="o")
    ax2.set_ylabel("Cumulative %")
    plt.title("Top 20 districts by heavy rain days")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
def plot_state_boxplot(df, save_path="reports/figures/q11_boxplot.png"):
    top10 = df.groupby("state")["district"].nunique().sort_values(ascending=False).head(10).index
    data = df[df["state"].isin(top10)]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=data, x="state", y="Monthly_Total", order=top10, ax=ax)
    ax.set_xlabel("State")
    ax.set_ylabel("Monthly rainfall (mm)")
    ax.tick_params(axis="x", rotation=45)
    sns.despine()
    plt.title("Monthly rainfall in the top 10 states")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
def plot_state_heatmap(df, save_path="reports/figures/q11_heatmap.png"):
    top10 = df.groupby("state")["district"].nunique().sort_values(ascending=False).head(10).index
    data = df[df["state"].isin(top10)]
    table = data.pivot_table(index="state", columns="month", values="Monthly_Total", aggfunc="median")
    table = table.loc[top10]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(table, annot=True, fmt=".0f", cmap="Blues", ax=ax)
    ax.set_xlabel("Month")
    ax.set_ylabel("State")
    plt.title("Median monthly rainfall (mm) in the top 10 states")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()