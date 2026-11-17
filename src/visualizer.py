import numpy as np
import pandas as pd
from pathlib import Path
from typing import List
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


class RainfallVisualizer:
    """
    Generates static publication-grade Matplotlib/Seaborn figures and
    an interactive Plotly HTML dashboard for IMD district rainfall regimes.
    """

    REGIME_ORDER: List[str] = [
        "Arid (<500 mm)",
        "Semi-Arid (500-1000 mm)",
        "Sub-Humid (1000-2000 mm)",
        "Humid (2000-3000 mm)",
        "Per-Humid (>3000 mm)",
    ]

    def __init__(self, df: pd.DataFrame, reports_dir: str | Path = "reports") -> None:
        self.df = df.copy()
        self.reports_dir = Path(reports_dir)
        self.figures_dir = self.reports_dir / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        sns.set_theme(style="whitegrid", context="notebook", palette="viridis")

    def plot_primary_envelope(self) -> Path:
        """
        Generates reports/figures/primary_envelope.png:
        Confidence envelope & linear/polynomial regression overlay comparing
        Southwest Monsoon (JJAS) vs. Annual Rainfall across districts.
        """
        out_path = self.figures_dir / "primary_envelope.png"
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        x_col = "JJAS" if "JJAS" in self.df.columns else "SEASONALITY_CV"
        y_col = "ANNUAL"

        plot_df = self.df[[x_col, y_col, "RAINFALL_REGIME"]].dropna().sort_values(by=x_col)
        x = plot_df[x_col].to_numpy(dtype=float)
        y = plot_df[y_col].to_numpy(dtype=float)

        # Scatter points colored by regime
        sns.scatterplot(
            data=plot_df,
            x=x_col,
            y=y_col,
            hue="RAINFALL_REGIME",
            hue_order=[r for r in self.REGIME_ORDER if r in plot_df["RAINFALL_REGIME"].unique()],
            alpha=0.75,
            s=45,
            ax=ax,
        )

        # Linear regression fit + 95% confidence/prediction envelope
        if len(x) > 2:
            coeffs = np.polyfit(x, y, deg=1)
            poly_fn = np.poly1d(coeffs)
            x_grid = np.linspace(x.min(), x.max(), 200)
            y_pred = poly_fn(x_grid)

            residuals = y - poly_fn(x)
            std_err = np.std(residuals)

            ax.plot(x_grid, y_pred, color="#111111", linewidth=2, label=f"OLS Fit (y = {coeffs[0]:.2f}x + {coeffs[1]:.1f})")
            ax.fill_between(
                x_grid,
                np.maximum(0, y_pred - 1.96 * std_err),
                y_pred + 1.96 * std_err,
                color="#4C72B0",
                alpha=0.18,
                label="95% Confidence Envelope (±1.96σ)",
            )

        ax.set_title("IMD District Rainfall: Monsoon-to-Annual Regression & Confidence Envelope", fontsize=13, fontweight="bold")
        ax.set_xlabel("Southwest Monsoon Rainfall JJAS (mm)" if x_col == "JJAS" else x_col, fontsize=11)
        ax.set_ylabel("Total Annual Rainfall (mm)", fontsize=11)
        ax.legend(title="Climate Regime / Fit", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)

        plt.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_correlation_heatmap(self) -> Path:
        """
        Generates reports/figures/correlation_heatmap.png:
        Seaborn annotated correlation matrix across monthly, seasonal, and derived metrics.
        """
        out_path = self.figures_dir / "correlation_heatmap.png"
        candidate_cols = [
            "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
            "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
            "JF", "MAM", "JJAS", "OND", "ANNUAL", "MONSOON_SHARE_PCT", "SEASONALITY_CV"
        ]
        num_cols = [c for c in candidate_cols if c in self.df.columns]
        corr = self.df[num_cols].corr()

        fig, ax = plt.subplots(figsize=(12, 9), dpi=300)
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

        sns.heatmap(
            corr,
            mask=mask,
            annot=True,
            fmt=".2f",
            cmap="YlGnBu",
            vmin=-1.0,
            vmax=1.0,
            linewidths=0.5,
            annot_kws={"size": 7.5},
            cbar_kws={"shrink": 0.8, "label": "Pearson Correlation (r)"},
            ax=ax,
        )

        ax.set_title("Annotated Correlation Matrix of IMD Monthly & Seasonal Rainfall Features", fontsize=13, fontweight="bold")
        plt.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_distribution_regimes(self) -> Path:
        """
        Generates reports/figures/distribution_regimes.png:
        Multi-panel Seaborn categorical distribution (boxplot + stripplot & count breakdown)
        across climate regime tiers.
        """
        out_path = self.figures_dir / "distribution_regimes.png"
        present_order = [r for r in self.REGIME_ORDER if r in self.df["RAINFALL_REGIME"].unique()]

        fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

        # Panel A: Annual Rainfall distribution by regime
        sns.boxplot(
            data=self.df,
            x="RAINFALL_REGIME",
            y="ANNUAL",
            order=present_order,
            palette="viridis",
            ax=axes[0],
        )
        sns.stripplot(
            data=self.df,
            x="RAINFALL_REGIME",
            y="ANNUAL",
            order=present_order,
            color="#222222",
            size=3.5,
            alpha=0.5,
            ax=axes[0],
        )
        axes[0].set_title("Annual Rainfall Spread by Climate Regime", fontsize=12, fontweight="bold")
        axes[0].set_xlabel("")
        axes[0].set_ylabel("Annual Rainfall (mm)")
        axes[0].tick_params(axis="x", rotation=25)

        # Panel B: District counts per regime
        sns.countplot(
            data=self.df,
            x="RAINFALL_REGIME",
            order=present_order,
            palette="viridis",
            ax=axes[1],
        )
        for container in axes[1].containers:
            axes[1].bar_label(container, padding=3, fontsize=9)

        axes[1].set_title("District Frequency Across Climate Tiers", fontsize=12, fontweight="bold")
        axes[1].set_xlabel("")
        axes[1].set_ylabel("Number of Districts")
        axes[1].tick_params(axis="x", rotation=25)

        plt.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def export_interactive_dashboard(self) -> Path:
        """
        Generates reports/interactive_dashboard.html:
        Standalone interactive Plotly HTML dashboard with dropdown regime filter
        and hover tooltips for district-level inspection.
        """
        out_path = self.reports_dir / "interactive_dashboard.html"

        district_col = next((c for c in ["DISTRICT", "DIST_NAME", "NAME"] if c in self.df.columns), None)
        state_col = next((c for c in ["STATE", "STATE_UT_NAME", "SUBDIVISION"] if c in self.df.columns), None)

        hover_cols = [c for c in [state_col, "ANNUAL", "JJAS", "MONSOON_SHARE_PCT", "SEASONALITY_CV"] if c and c in self.df.columns]

        fig = px.scatter(
            self.df,
            x="JJAS" if "JJAS" in self.df.columns else "ANNUAL",
            y="ANNUAL",
            color="RAINFALL_REGIME",
            category_orders={"RAINFALL_REGIME": self.REGIME_ORDER},
            hover_name=district_col if district_col else None,
            hover_data=hover_cols,
            size="MONSOON_SHARE_PCT" if "MONSOON_SHARE_PCT" in self.df.columns else None,
            title="IMD District Rainfall Regimes — Interactive Explorer",
            labels={
                "JJAS": "Southwest Monsoon JJAS (mm)",
                "ANNUAL": "Annual Rainfall (mm)",
                "RAINFALL_REGIME": "Climate Regime",
                "MONSOON_SHARE_PCT": "Monsoon Share (%)",
            },
            template="plotly_white",
        )

        # Add interactive dropdown filter buttons by Climate Regime
        regimes = ["All Regimes"] + [r for r in self.REGIME_ORDER if r in self.df["RAINFALL_REGIME"].unique()]
        buttons = []
        for regime in regimes:
            if regime == "All Regimes":
                visibility = [True] * len(fig.data)
            else:
                visibility = [trace.name == regime for trace in fig.data]
            buttons.append(
                dict(
                    label=regime,
                    method="update",
                    args=[{"visible": visibility}, {"title": f"IMD District Rainfall Regimes — {regime}"}],
                )
            )

        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    buttons=buttons,
                    x=1.02,
                    y=1.12,
                    xanchor="right",
                    yanchor="top",
                )
            ],
            height=680,
            legend_title_text="Climate Regime",
        )

        fig.write_html(str(out_path), include_plotlyjs="cdn")
        return out_path

    def generate_all(self) -> dict[str, Path]:
        """Runs all visualizations and returns paths to generated files."""
        return {
            "primary_envelope": self.plot_primary_envelope(),
            "correlation_heatmap": self.plot_correlation_heatmap(),
            "distribution_regimes": self.plot_distribution_regimes(),
            "interactive_dashboard": self.export_interactive_dashboard(),
        }


if __name__ == "__main__":
    from src.analyzer import ClimateRegimeClassifier

    classifier = ClimateRegimeClassifier()
    enriched_df, _ = classifier.run_analysis()
    viz = RainfallVisualizer(enriched_df)
    outputs = viz.generate_all()
    for name, path in outputs.items():
        print(f"Generated {name}: {path}")