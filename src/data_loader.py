"""Downloaders for the three Opportunity Insights datasets used in the Econ 148 final.

Each public function returns a pathlib.Path to a file in data/raw/. Files are cached,
so re-runs are fast. If a URL 404s, the loader falls through a list of fallbacks and
records each attempt on stdout so notebook readers see the trail.

Dataset references:
- Chetty, Hendren, Kline, Saez (2014) "Where is the Land of Opportunity?" QJE 129(4).
- Chetty, Friedman, Hendren, Jones, Porter (2018) "The Opportunity Atlas".
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import requests

USER_AGENT = "econ148-final/0.1 (academic research; paul@getpasal.com)"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Chetty et al. 2014 online data tables. The .xlsx links in the 2018/03/ tree that
# the project brief originally pointed at now return 404; the live copy is the .xls
# version in 2018/04/, and the equality-of-opportunity.org mirror is the canonical
# academic source.
CHETTY_2014_URLS: tuple[str, ...] = (
    "https://opportunityinsights.org/wp-content/uploads/2018/03/online_data_tables-8.xlsx",
    "https://opportunityinsights.org/wp-content/uploads/2018/03/online_data_tables-5.xlsx",
    "https://opportunityinsights.org/wp-content/uploads/2018/04/online_data_tables-8.xls",
    "http://www.equality-of-opportunity.org/data/descriptive/table1/online_data_tables.xls",
)

# Opportunity Atlas tract-level outcomes. The full tract_outcomes.zip at census.gov
# is 958 MB, which is too large to pull during a typical notebook 'Run All'. The
# _simple variant preserves the pooled outcome columns we need for day-1 at ~33 MB.
ATLAS_TRACT_URLS: tuple[str, ...] = (
    "https://www2.census.gov/ces/opportunity/tract_outcomes_simple.csv",
    "https://opportunityinsights.org/wp-content/uploads/2018/10/tract_outcomes_simple.csv",
)

# Opportunity Atlas county-level rollup (used as the day-1 outcome variable).
COUNTY_OUTCOMES_URLS: tuple[str, ...] = (
    "https://opportunityinsights.org/wp-content/uploads/2018/10/county_outcomes.csv",
    "https://www2.census.gov/ces/opportunity/county_outcomes_simple.csv",
)


def ensure_raw_dir() -> Path:
    """Create data/raw if needed and return its path."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    return RAW_DIR


def _report(path: Path) -> Path:
    """Print a '(size MB)' line for a file and return the path."""
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  saved: {path.name}  ({size_mb:.2f} MB)")
    return path


def _download(url: str, path: Path) -> bool:
    """Stream url to path; delete any partial file on failure. Return success bool."""
    try:
        with requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=300) as r, open(path, "wb") as f:
            r.raise_for_status()
            for chunk in r.iter_content(65536):
                f.write(chunk)
        return True
    except (requests.RequestException, OSError) as exc:
        print(f"  fail:  {url} ({exc})")
        path.unlink(missing_ok=True)
        return False


def _fetch_one(urls: Iterable[str], filename: str) -> Path:
    """Cache-or-download: return data/raw/filename, trying each url until one works."""
    ensure_raw_dir()
    path = RAW_DIR / filename
    if path.exists():
        return _report(path)
    for url in urls:
        print(f"  try:   {url}")
        if _download(url, path):
            return _report(path)
    raise RuntimeError(f"All {len(tuple(urls))} URLs failed for {filename}")


def get_chetty_2014(filename: str = "chetty2014_online_data_tables.xls") -> Path:
    """Download Chetty et al. 2014 online data tables (multi-sheet Excel)."""
    print("[1/3] Chetty 2014 descriptive tables:")
    return _fetch_one(CHETTY_2014_URLS, filename)


def get_opportunity_atlas_tract(filename: str = "tract_outcomes_simple.csv") -> Path:
    """Download Opportunity Atlas tract-level outcomes (simple CSV, ~33 MB)."""
    print("[2/3] Opportunity Atlas tract outcomes:")
    return _fetch_one(ATLAS_TRACT_URLS, filename)


def get_county_outcomes(filename: str = "county_outcomes_simple.csv") -> Path:
    """Download the Opportunity Atlas county-level rollup (day-1 outcome file)."""
    print("[3/3] Atlas county-level outcomes:")
    return _fetch_one(COUNTY_OUTCOMES_URLS, filename)
