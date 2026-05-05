"""Modeling helpers for the random-forest baseline (notebooks/03_random_forest).

Each function is under the 10-line course budget. The CZ_COVARIATES tuple is
the canonical 38-feature set drawn from Chetty 2014 Online Data Table 8;
OLS_PREDICTORS is the six-variable subset used by Kabir's OLS specification
(used to align the OLS-vs-RF comparison on identical features).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

CZ_COVARIATES: tuple[str, ...] = (
    "Census 2000 population", "Urban Areas", "Frac. Black", "Racial Segregation",
    "Income Segregation", "Segregation of Poverty (<p25)",
    "Segregation of Affluence (>p75)", "Frac. with Commute < 15 Mins",
    "Household Income per capita", "Gini", "Top 1% Income Share",
    "Gini Bottom 99%", "Frac. Between p25 and p75", "Local Tax Rate",
    "Local Government Expenditures Per Capita", "State Income Tax Progressivity",
    "State EITC Exposure", "School Expenditure per Student",
    "Teacher Student Ratio", "Test Score Percentile (Income Adjusted",
    "High School Dropout Rate (Income Adjusted)", "Number of Colleges per Capita",
    "College Tuition", "College Graduation Rate (Income Adjusted)",
    "Labor Force Participation Rate", "Manufacturing Employment Share",
    "Growth in Chinese Imports 1990-2000",
    "Teenage Labor Force Participation Rate", "Migration Inflow Rate",
    "Migration Outlflow Rate", "Frac. Foreign Born", "Social Capital Index",
    "Fraction Religious", "Violent Crime Rate",
    "Fraction of Children with Single Mothers", "Fraction of Adults Divorced",
    "Fraction of Adults Married", "Income Growth 2000-2006/10",
)
OLS_PREDICTORS: tuple[str, ...] = (
    "Racial Segregation", "Gini", "Test Score Percentile (Income Adjusted",
    "Social Capital Index", "Fraction of Children with Single Mothers",
    "Frac. with Commute < 15 Mins",
)
OUTCOME = "kfr_pooled_pooled_p25"


def prepare_xy(parquet_path: Path, feature_cols, outcome_col: str = OUTCOME):
    """Load the parquet, drop missing-outcome rows, mean-impute features."""
    df = pd.read_parquet(parquet_path).dropna(subset=[outcome_col])
    X_raw = df[list(feature_cols)]
    imp = SimpleImputer(strategy="mean")
    X = pd.DataFrame(imp.fit_transform(X_raw), columns=list(feature_cols))
    return X, df[outcome_col].reset_index(drop=True)


def split_and_fit(X: pd.DataFrame, y: pd.Series, seed: int = 148, test_size: float = 0.2):
    """Run an 80/20 split and fit a RandomForestRegressor with n_estimators=300."""
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=seed)
    rf = RandomForestRegressor(n_estimators=300, random_state=seed, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    return rf, X_tr, X_te, y_tr, y_te


def evaluate(rf, X_te, y_te) -> tuple[float, float]:
    """Return (test R^2, test RMSE)."""
    pred = rf.predict(X_te)
    return r2_score(y_te, pred), float(np.sqrt(mean_squared_error(y_te, pred)))


def importance_series(rf, columns) -> pd.Series:
    """Return rf.feature_importances_ as a descending pd.Series."""
    return pd.Series(rf.feature_importances_, index=list(columns)).sort_values(ascending=False)


def perm_importance_series(rf, X_te: pd.DataFrame, y_te: pd.Series, seed: int = 148, n_repeats: int = 20) -> pd.Series:
    """Permutation importance means as a descending pd.Series."""
    pi = permutation_importance(rf, X_te, y_te, n_repeats=n_repeats, random_state=seed, n_jobs=-1)
    return pd.Series(pi.importances_mean, index=list(X_te.columns)).sort_values(ascending=False)


def save_horizontal_bars(series: pd.Series, out_path: Path, title: str, xlabel: str) -> Path:
    """Save a sorted horizontal bar chart of `series` to `out_path` (PNG)."""
    asc = series.sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, max(4.0, 0.3 * len(asc))))
    ax.barh(asc.index, asc.values, color="steelblue")
    ax.set(xlabel=xlabel, title=title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=144, bbox_inches="tight")
    plt.close(fig)
    return out_path


def save_pdp_panel(rf, X: pd.DataFrame, features, out_path: Path) -> Path:
    """Save a 2x2 partial-dependence panel for the first up-to-4 features in `features`."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    PartialDependenceDisplay.from_estimator(rf, X, features=list(features)[:4], ax=axes.ravel())
    fig.suptitle("Partial dependence: top RF predictors of kfr_pooled_pooled_p25")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=144, bbox_inches="tight")
    plt.close(fig)
    return out_path
