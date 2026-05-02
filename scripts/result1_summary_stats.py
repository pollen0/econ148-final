"""Result 1 builder: produce data/processed/features.parquet and print the
summary-statistics table for the six named predictors plus the
kfr_pooled_pooled_p25 outcome.

The 89 counties without Chetty 2014 CZ covariates (Puerto Rico, Alaska
reorganisations, and a few post-2014 county renamings) are dropped here per
the team decision documented in report/progress_report_blockers.md.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd

ROOT = Path("/Users/paullin/Desktop/econ148-final")
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from src.data_loader import (
    download_cz_crosswalk,
    get_chetty_2014,
    get_county_outcomes,
)
from src.data_processing import (
    add_county_fips,
    drop_unmatched_counties,
    load_chetty_table8,
    merge_cz_covariates,
    save_features_parquet,
)


PREDICTORS = (
    ("Segregation (racial)", "Racial Segregation"),
    ("Income inequality (Gini)", "Gini"),
    ("School quality (test score, inc-adj)", "Test Score Percentile (Income Adjusted"),
    ("Social capital", "Social Capital Index"),
    ("Family structure (single mothers)", "Fraction of Children with Single Mothers"),
    ("Commuting (frac < 15 min)", "Frac. with Commute < 15 Mins"),
)
OUTCOME = ("Outcome (kfr_pooled_pooled_p25)", "kfr_pooled_pooled_p25")
PARQUET_OUT = ROOT / "data" / "processed" / "features.parquet"


def _load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Download (or reuse cached) raw inputs and return county / crosswalk / CZ-cov frames."""
    county = add_county_fips(pd.read_csv(get_county_outcomes()))
    crosswalk = pd.read_csv(download_cz_crosswalk())
    cz_cov = load_chetty_table8(get_chetty_2014())
    return county, crosswalk, cz_cov


def _row_for(label: str, col: str, df: pd.DataFrame) -> dict:
    """Compute summary statistics (n, mean, sd, min, max) for one column."""
    s = pd.to_numeric(df[col], errors="coerce")
    return {"variable": label, "column_name": col, "n": int(s.count()),
            "mean": s.mean(), "sd": s.std(), "min": s.min(), "max": s.max()}


def _summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Build the summary-statistics table for the six predictors plus outcome."""
    rows = [_row_for(label, col, df) for label, col in (*PREDICTORS, OUTCOME)]
    return pd.DataFrame(rows)


def main() -> None:
    """End-to-end Result 1 pipeline: build features.parquet and print stats."""
    print("=" * 78 + "\nResult 1 - features.parquet builder + summary stats\n" + "=" * 78)
    county, crosswalk, cz_cov = _load_inputs()
    cleaned = drop_unmatched_counties(merge_cz_covariates(county, crosswalk, cz_cov))
    out = save_features_parquet(cleaned, PARQUET_OUT)
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"\nSaved features.parquet to: {out}  (shape={cleaned.shape}, size={size_mb:.2f} MB)")
    print("\nResult 1 - summary statistics:")
    print(_summary_stats(cleaned).to_string(index=False, float_format="%.4f"))


if __name__ == "__main__":
    main()
