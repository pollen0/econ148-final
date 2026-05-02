"""Result 3 builder: train RandomForestRegressor on data/processed/features.parquet
with an 80/20 split, save the ranked feature-importance bar chart for all 38
CZ-level covariates, and print Emily's 2-3 sentence Progress Report blurb.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path("/Users/paullin/Desktop/econ148-final")
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

PARQUET = ROOT / "data" / "processed" / "features.parquet"
CHART_OUT = ROOT / "report" / "result3_feature_importance.png"
SEED = 148

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
OUTCOME = "kfr_pooled_pooled_p25"


def _load_xy() -> tuple[pd.DataFrame, pd.Series]:
    """Read parquet, keep rows with non-null outcome, mean-impute features."""
    df = pd.read_parquet(PARQUET).dropna(subset=[OUTCOME])
    X_raw, y = df[list(CZ_COVARIATES)], df[OUTCOME]
    imp = SimpleImputer(strategy="mean")
    X = pd.DataFrame(imp.fit_transform(X_raw), columns=list(CZ_COVARIATES))
    return X, y


def _fit_rf(X: pd.DataFrame, y: pd.Series):
    """Split 80/20 and fit RandomForestRegressor; return (rf, X_te, y_te)."""
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=SEED)
    rf = RandomForestRegressor(n_estimators=300, random_state=SEED, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    return rf, X_te, y_te


def _evaluate(rf, X_te, y_te) -> tuple[float, float]:
    """Return (R^2, RMSE) on the held-out test set."""
    pred = rf.predict(X_te)
    return r2_score(y_te, pred), float(np.sqrt(mean_squared_error(y_te, pred)))


def _save_chart(importances: pd.Series, r2: float) -> Path:
    """Render the horizontal ranked bar chart of all 38 features and save as PNG."""
    asc = importances.sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, 11))
    ax.barh(asc.index, asc.values, color="steelblue")
    ax.set(xlabel="Mean decrease in impurity", title=f"Result 3: RF feature importance (test R^2 = {r2:.3f})\n38 CZ-level covariates predicting kfr_pooled_pooled_p25")
    fig.tight_layout()
    CHART_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHART_OUT, dpi=144, bbox_inches="tight")
    plt.close(fig)
    return CHART_OUT


def _print_top10(importances: pd.Series) -> None:
    """Print the top 10 features by mean decrease in impurity to stdout."""
    print("\nTop 10 features by mean decrease in impurity:")
    for i, (name, val) in enumerate(importances.sort_values(ascending=False).head(10).items(), 1):
        print(f"  {i:2d}. {val:.4f}  {'#' * int(round(val * 200)):<22}  {name}")


def _print_leo_update(r2: float, rmse: float, importances: pd.Series) -> None:
    """Print Emily's 2-3 sentence Progress Report blurb."""
    top3 = ", ".join(importances.sort_values(ascending=False).head(3).index.tolist())
    print("\n[Progress Report sentences for Leo]\n")
    print(f"Hi Leo - I pulled Paul's data/processed/features.parquet, ran an 80/20 split (random_state=148), and fit RandomForestRegressor(n_estimators=300) on the 38 CZ-level covariates, getting a test R^2 of {r2:.3f} and RMSE of {rmse:.3f}. Result 3 is the ranked horizontal bar chart of all 38 covariates by mean decrease in impurity, saved to report/result3_feature_importance.png; the top three predictors are {top3}. No active blockers - I will switch to permutation importance and partial-dependence plots once Kabir's OLS spec is locked so the OLS-vs-RF comparison runs on identical features.")


def main() -> None:
    """End-to-end Result 3 pipeline."""
    print("=" * 78 + "\nResult 3 - RF feature importance\n" + "=" * 78)
    X, y = _load_xy()
    rf, X_te, y_te = _fit_rf(X, y)
    r2, rmse = _evaluate(rf, X_te, y_te)
    print(f"\nLoaded features: {X.shape}; test R^2 = {r2:.4f}, RMSE = {rmse:.4f}")
    importances = pd.Series(rf.feature_importances_, index=list(CZ_COVARIATES))
    print(f"Saved bar chart to: {_save_chart(importances, r2)}")
    _print_top10(importances)
    _print_leo_update(r2, rmse, importances)


if __name__ == "__main__":
    main()
