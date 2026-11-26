from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class ClimateRegimeClassifier:
    """
    Analyzes cleaned IMD daily/monthly district rainfall data using NumPy vectorization
    and Pandas aggregations to classify districts into hydrological/climate regimes.
    """

    SEASONAL_COLS: List[str] = ["JF", "MAM", "JJAS", "OND"]
    MONTHLY_COLS: List[str] = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
    ]
    MONTH_NUM_MAP: Dict[int, str] = {
        1: "JAN", 2: "FEB", 3: "MAR", 4: "APR",
        5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG",
        9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC",
    }

    def __init__(self, data_path: str | Path = "data/processed/cleaned_data.csv") -> None:
        self.data_path = Path(data_path)
        self.df: pd.DataFrame = pd.DataFrame()
        self.summary_stats: Dict[str, float] = {}

    def load_data(self) -> pd.DataFrame:
        """Loads semicolon- or comma-delimited cleaned dataset and pivots daily records to district-level monthly/annual totals."""
        if not self.data_path.exists():
            fallback = Path("data/processed/clean_imd_rainfall_districts.csv")
            if fallback.exists():
                self.data_path = fallback
            else:
                raise FileNotFoundError(f"Cleaned dataset not found at {self.data_path}")

        # Auto-detect separator (handles ';' used in cleaned_data.csv as well as ',')
        raw_df = pd.read_csv(self.data_path, sep=None, engine="python")
        raw_df.columns = [c.strip().upper() for c in raw_df.columns]

        # Handle daily format: STATE;DISTRICT;MONTH;1ST;2ND;...;31ST
        if "MONTH" in raw_df.columns and any(c.endswith(("ST", "ND", "RD", "TH")) for c in raw_df.columns):
            day_cols = [
                c for c in raw_df.columns
                if c not in {"STATE", "DISTRICT", "MONTH", "YEAR"}
            ]
            # Convert daily columns to numeric and sum across days using NumPy vectorization
            daily_matrix = raw_df[day_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
            raw_df["MONTHLY_TOTAL"] = np.sum(daily_matrix, axis=1)

            # Map numeric month (1..12) to standard 3-letter month code
            raw_df["MONTH_CODE"] = pd.to_numeric(raw_df["MONTH"], errors="coerce").map(self.MONTH_NUM_MAP)
            raw_df = raw_df.dropna(subset=["MONTH_CODE"])

            group_keys = [c for c in ["STATE", "DISTRICT"] if c in raw_df.columns]
            # Average across years if multiple years exist per district-month, then pivot
            monthly_agg = (
                raw_df.groupby(group_keys + ["MONTH_CODE"], as_index=False)["MONTHLY_TOTAL"]
                .mean()
            )
            pivoted = monthly_agg.pivot(index=group_keys, columns="MONTH_CODE", values="MONTHLY_TOTAL").reset_index()
            pivoted.columns.name = None

            # Ensure all 12 month columns exist in chronological order
            for m_col in self.MONTHLY_COLS:
                if m_col not in pivoted.columns:
                    pivoted[m_col] = 0.0
                else:
                    pivoted[m_col] = pivoted[m_col].fillna(0.0)

            self.df = pivoted
        else:
            self.df = raw_df

        return self.df

    def compute_vectorized_metrics(self) -> pd.DataFrame:
        """
        Uses NumPy vectorization to compute:
        - Seasonal totals (JF, MAM, JJAS, OND)
        - Annual rainfall (ANNUAL)
        - Monsoon concentration index (JJAS share of annual rainfall)
        - Coefficient of Variation (CV) across months (seasonality index)
        - Z-score anomaly relative to national district mean
        """
        if self.df.empty:
            self.load_data()

        df = self.df.copy()

        avail_months = [c for c in self.MONTHLY_COLS if c in df.columns]

        # Compute IMD standard seasonal totals via NumPy vectorization
        if all(m in df.columns for m in ["JAN", "FEB"]):
            df["JF"] = np.sum(df[["JAN", "FEB"]].to_numpy(dtype=float), axis=1)
        if all(m in df.columns for m in ["MAR", "APR", "MAY"]):
            df["MAM"] = np.sum(df[["MAR", "APR", "MAY"]].to_numpy(dtype=float), axis=1)
        if all(m in df.columns for m in ["JUN", "JUL", "AUG", "SEP"]):
            df["JJAS"] = np.sum(df[["JUN", "JUL", "AUG", "SEP"]].to_numpy(dtype=float), axis=1)
        if all(m in df.columns for m in ["OCT", "NOV", "DEC"]):
            df["OND"] = np.sum(df[["OCT", "NOV", "DEC"]].to_numpy(dtype=float), axis=1)

        avail_seasons = [c for c in self.SEASONAL_COLS if c in df.columns]

        # Compute ANNUAL column
        if "ANNUAL" not in df.columns:
            if avail_months:
                df["ANNUAL"] = np.sum(df[avail_months].to_numpy(dtype=float), axis=1)
            elif avail_seasons:
                df["ANNUAL"] = np.sum(df[avail_seasons].to_numpy(dtype=float), axis=1)
            else:
                raise ValueError("Dataset lacks ANNUAL, monthly, or seasonal rainfall columns.")

        annual_arr = df["ANNUAL"].to_numpy(dtype=float)

        # 1. Monsoon Dominance Ratio (%) via NumPy safe division
        if "JJAS" in df.columns:
            jjas_arr = df["JJAS"].to_numpy(dtype=float)
            df["MONSOON_SHARE_PCT"] = np.where(
                annual_arr > 0, (jjas_arr / annual_arr) * 100.0, 0.0
            )
        else:
            df["MONSOON_SHARE_PCT"] = np.nan

        # 2. Monthly Seasonality Index (Coefficient of Variation across 12 months)
        if len(avail_months) == 12:
            month_matrix = df[avail_months].to_numpy(dtype=float)
            row_means = np.mean(month_matrix, axis=1)
            row_stds = np.std(month_matrix, axis=1)
            df["SEASONALITY_CV"] = np.where(row_means > 0, row_stds / row_means, 0.0)
        else:
            df["SEASONALITY_CV"] = np.nan

        # 3. National Z-score
        mean_ann = float(np.mean(annual_arr))
        std_ann = float(np.std(annual_arr))
        df["ANNUAL_ZSCORE"] = (annual_arr - mean_ann) / std_ann if std_ann > 0 else 0.0

        self.df = df
        return self.df

    def classify_regimes(self) -> pd.DataFrame:
        """
        Vectorized classification of districts into IMD-aligned rainfall regimes
        using np.select based on annual precipitation thresholds (mm).
        """
        if "ANNUAL" not in self.df.columns:
            self.compute_vectorized_metrics()

        annual = self.df["ANNUAL"].to_numpy(dtype=float)

        conditions = [
            annual < 500.0,
            (annual >= 500.0) & (annual < 1000.0),
            (annual >= 1000.0) & (annual < 2000.0),
            (annual >= 2000.0) & (annual < 3000.0),
            annual >= 3000.0,
        ]
        choices = [
            "Arid (<500 mm)",
            "Semi-Arid (500-1000 mm)",
            "Sub-Humid (1000-2000 mm)",
            "Humid (2000-3000 mm)",
            "Per-Humid (>3000 mm)",
        ]

        self.df["RAINFALL_REGIME"] = np.select(conditions, choices, default="Unclassified")

        if "MONSOON_SHARE_PCT" in self.df.columns and not self.df["MONSOON_SHARE_PCT"].isna().all():
            share = self.df["MONSOON_SHARE_PCT"].to_numpy(dtype=float)
            s_cond = [share >= 75.0, (share >= 50.0) & (share < 75.0), share < 50.0]
            s_choices = ["Hyper-Monsoonal (>=75%)", "Monsoonal (50-75%)", "Bimodal / Non-Monsoonal (<50%)"]
            self.df["MONSOON_TIER"] = np.select(s_cond, s_choices, default="Unknown")

        return self.df

    def get_regime_summary(self) -> pd.DataFrame:
        """Aggregates statistics per rainfall regime using Pandas groupby."""
        if "RAINFALL_REGIME" not in self.df.columns:
            self.classify_regimes()

        agg_dict = {"ANNUAL": ["count", "mean", "std", "min", "max"]}
        if "MONSOON_SHARE_PCT" in self.df.columns:
            agg_dict["MONSOON_SHARE_PCT"] = ["mean"]
        if "SEASONALITY_CV" in self.df.columns:
            agg_dict["SEASONALITY_CV"] = ["mean"]

        summary = self.df.groupby("RAINFALL_REGIME", observed=False).agg(agg_dict)
        summary.columns = ["_".join(col).strip() for col in summary.columns.values]
        return summary.reset_index().sort_values(by="ANNUAL_mean", ascending=True)

    def get_state_summary(self) -> Optional[pd.DataFrame]:
        """Returns state-level aggregated rainfall metrics if a state column exists."""
        state_col = next((c for c in ["STATE", "STATE_UT_NAME", "SUBDIVISION"] if c in self.df.columns), None)
        if not state_col:
            return None

        return (
            self.df.groupby(state_col, as_index=False)
            .agg(
                DISTRICTS=("ANNUAL", "count"),
                MEAN_ANNUAL_MM=("ANNUAL", "mean"),
                MEDIAN_ANNUAL_MM=("ANNUAL", "median"),
                MEAN_MONSOON_PCT=("MONSOON_SHARE_PCT", "mean"),
            )
            .sort_values(by="MEAN_ANNUAL_MM", ascending=False)
        )

    def run_analysis(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Executes the full analytical pipeline and returns (enriched_df, regime_summary)."""
        self.load_data()
        self.compute_vectorized_metrics()
        self.classify_regimes()
        summary = self.get_regime_summary()
        return self.df, summary


if __name__ == "__main__":
    classifier = ClimateRegimeClassifier()
    enriched_df, regime_table = classifier.run_analysis()
    print("=== Rainfall Regime Summary ===")
    print(regime_table.to_string(index=False))