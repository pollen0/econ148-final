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


def main() -> None:
    print("=" * 78)
    print("Result 1 - features.parquet builder + summary stats")
    print("=" * 78)
    chetty_path = get_chetty_2014()
    county_path = get_county_outcomes()
    crosswalk_path = download_cz_crosswalk()

    county_df = add_county_fips(pd.read_csv(county_path))
    crosswalk_df = pd.read_csv(crosswalk_path)
    cz_cov_df = load_chetty_table8(chetty_path)

    print(f"\nMerging {county_df.shape} county outcomes with {cz_cov_df.shape} CZ covariates "
          f"via {len(crosswalk_df)}-row crosswalk ...")
    merged = merge_cz_covariates(county_df, crosswalk_df, cz_cov_df)
    cleaned = drop_unmatched_counties(merged)

    out = save_features_parquet(cleaned, PARQUET_OUT)
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"\nSaved features.parquet to:  {out}")
    print(f"  shape: {cleaned.shape}   size: {size_mb:.2f} MB")

    rows = []
    for label, col in (*PREDICTORS, OUTCOME):
        s = pd.to_numeric(cleaned[col], errors="coerce")
        rows.append({"variable": label, "column_name": col, "n": int(s.count()),
                     "mean": s.mean(), "sd": s.std(), "min": s.min(), "max": s.max()})
    stats = pd.DataFrame(rows)

    print("\nResult 1 - summary statistics (six predictors + outcome):")
    print(stats.to_string(index=False, float_format="%.4f"))


if __name__ == "__main__":
    main()
