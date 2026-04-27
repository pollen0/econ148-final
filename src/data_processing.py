"""Cleaning and merging utilities for the Econ 148 final.

The functions here turn the three raw downloads from `src.data_loader` into a
single county-level frame suitable for downstream OLS and random-forest fits.
Each function stays under the 10-line course budget and is intended to be
re-used from notebooks, scripts, and tests without any hidden state.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

CHETTY_TABLE8_TEXT_COLS = ("CZ Name", "State")


def load_chetty_table8(chetty_path: Path) -> pd.DataFrame:
    """Read Online Data Table 8 (CZ-level covariates) from the 2014 workbook."""
    df = pd.read_excel(chetty_path, sheet_name="Online Data Table 8", skiprows=6, header=0)
    df = df.iloc[1:].reset_index(drop=True)
    for c in df.columns:
        if c not in CHETTY_TABLE8_TEXT_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def add_county_fips(county_df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of county_df with a 5-digit county_fips = state*1000 + county."""
    out = county_df.copy()
    out["county_fips"] = out["state"] * 1000 + out["county"]
    return out


def merge_cz_covariates(county_df: pd.DataFrame, crosswalk_df: pd.DataFrame, cz_cov_df: pd.DataFrame) -> pd.DataFrame:
    """Attach Chetty Table 8 CZ covariates onto the county frame via the crosswalk."""
    cw = crosswalk_df[["cty", "cz"]].rename(columns={"cty": "county_fips", "cz": "cz_id"})
    step = county_df.merge(cw, on="county_fips", how="left")
    return step.merge(cz_cov_df.rename(columns={"CZ": "cz_id"}), on="cz_id", how="left")


def drop_unmatched_counties(merged: pd.DataFrame, marker: str = "Racial Segregation") -> pd.DataFrame:
    """Drop the 89 counties (PR, AK reorgs, post-2014 renamings) with no CZ covariates."""
    before = len(merged)
    out = merged.dropna(subset=[marker]).reset_index(drop=True)
    print(f"  dropped {before - len(out)} unmatched counties (kept {len(out)} of {before}).")
    return out


def save_features_parquet(df: pd.DataFrame, out_path: Path) -> Path:
    """Write df to out_path as parquet, creating the parent directory if needed."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    return out_path
