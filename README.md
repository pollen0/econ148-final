# Econ 148 Final Project - Intergenerational Mobility Across US Counties

**Team:** Paul Lin (data engineering), Kabir (econometrics), Emily (machine learning)
**Track / Topic:** A-4, Intergenerational Mobility Across US Counties

## Project description

We study what interactions between Chetty's five core correlates of intergenerational
mobility (racial and income segregation, income inequality, school quality, social
capital, and family structure) plus a commuting variable a random forest is able to
capture in US county-level mobility outcomes that an OLS linear model misses. Our
feature and outcome data come from the Opportunity Insights publications "Where is
the Land of Opportunity?" (Chetty, Hendren, Kline, Saez, QJE 2014) and "The
Opportunity Atlas" (Chetty, Friedman, Hendren, Jones, Porter, 2018). The main
deliverable is a comparison of OLS and random forest fits with feature-importance and
partial-dependence analyses highlighting where the forest's nonlinear structure adds
explanatory power.

## Replication

The repo is self-contained: the four raw source files (~37 MB) and the cleaned
`data/processed/features.parquet` (~1.8 MB) are checked in, so a fresh clone or zip
extract can be reproduced offline.

### 1. Install dependencies

Local (Python 3.10+):

```bash
git clone https://github.com/pollen0/econ148-final.git
cd econ148-final
pip install -r requirements.txt
```

Google Colab:

```python
!git clone https://github.com/pollen0/econ148-final.git
%cd econ148-final
!pip install -r requirements.txt
```

The pinned floors in `requirements.txt` (numpy 2.x, matplotlib 3.9.3+,
numexpr 2.10+, bottleneck 1.4+, scikit-learn 1.6+, pyarrow 15.0+) are
chosen to avoid the C-extension ABI mismatches that the older
conda-default builds raise on a numpy 2.x runtime. Colab's default kernel
already runs numpy 2.x and pip resolves the floors automatically.

### 2. Run the pipeline

Notebooks are run in numeric order. Each notebook is independent (uses
`data/processed/features.parquet`) but they tell a single story end-to-end.

| Order | Notebook / script | Owner | Produces |
|------:|-------------------|-------|----------|
| 1 | `notebooks/01_data_inspection.ipynb` | Paul | downloads cached, FIPS diagnostics, three-way intersection, summary-for-Leo cell |
| 2 | `scripts/result1_summary_stats.py` | Paul | rebuilds `data/processed/features.parquet` and prints the Result 1 summary-stats table for the six predictors plus the outcome |
| 3 | `notebooks/02_ols_baseline.ipynb` | Kabir | OLS fit with HC3 standard errors and the regression table (Result 2) |
| 4 | `scripts/result3_rf_importance.py` and `notebooks/03_random_forest.ipynb` | Emily | RF fit (R^2, RMSE) and the ranked feature-importance bar chart (Result 3, saved to `report/result3_feature_importance.png`) |

To regenerate everything from scratch:

```bash
jupyter nbconvert --to notebook --execute notebooks/01_data_inspection.ipynb \
  --output 01_data_inspection_executed.ipynb
python3 scripts/result1_summary_stats.py
python3 scripts/result3_rf_importance.py
```

### 3. Expected outputs

Running the steps above (re)produces the following artefacts:

- `data/raw/chetty2014_online_data_tables.xls` (2.75 MB)
- `data/raw/county_outcomes_simple.csv` (1.65 MB)
- `data/raw/tract_outcomes_simple.csv` (32.81 MB)
- `data/raw/cty_cz_st_crosswalk.csv` (0.13 MB)
- `data/processed/features.parquet` (3,130 rows by 106 columns, 1.78 MB)
- `notebooks/01_data_inspection_executed.ipynb` (with embedded outputs)
- `report/result3_feature_importance.png` (Result 3 chart)
- Console output from the two scripts: Result 1 summary-stats table and Result 3
  test R^2 / RMSE / top-10 feature ranking

The `01_data_inspection_executed.ipynb` summary-for-Leo cell reports
`(3141, 25)` for Chetty 2014, `(73278, 66)` for the tract file, and
`(3219, 65)` for the Atlas county file, intersecting on 3,133 counties.
After dropping the 89 unmatched counties (78 Puerto Rico municipios, 8
Alaska borough reorganisations, 3 post-2014 county renamings) the
analytic frame is 3,130 counties. Result 3's RF run reports test
R^2 = 0.642 and RMSE = 0.039 with `random_state=148`.

## Data sources

All four files are also pulled at runtime by `src/data_loader.py` if missing. The
loader tries each canonical URL in order and falls back to the next on 404/403.

| # | Dataset | Loader function | Working URL (2026-05) |
|---|---------|-----------------|------------------------|
| 1 | Chetty et al. 2014, online data tables (county and CZ covariates) | `get_chetty_2014()` | `http://www.equality-of-opportunity.org/data/descriptive/table1/online_data_tables.xls` |
| 2 | Opportunity Atlas tract-level outcomes (simple variant, 33 MB) | `get_opportunity_atlas_tract()` | `https://www2.census.gov/ces/opportunity/tract_outcomes_simple.csv` |
| 3 | Opportunity Atlas county-level outcomes rollup (day-1 outcome) | `get_county_outcomes()` | `https://www2.census.gov/ces/opportunity/county_outcomes_simple.csv` |
| 4 | County-to-CZ crosswalk | `download_cz_crosswalk()` | `http://www.equality-of-opportunity.org/data/health/cty_cz_st_crosswalk.csv` |

The original `opportunityinsights.org/wp-content/uploads/2018/03/...` URLs in the
project brief now return 404/403; the loader fallback chain handles this transparently.

## Directory structure

```
econ148-final/
  README.md
  requirements.txt
  .gitignore
  data/
    raw/                                          37 MB of source files
      chetty2014_online_data_tables.xls
      county_outcomes_simple.csv
      tract_outcomes_simple.csv
      cty_cz_st_crosswalk.csv
    processed/
      features.parquet                            cleaned merged frame for OLS / RF
  notebooks/
    01_data_inspection.ipynb                      Paul, source notebook
    01_data_inspection_executed.ipynb             with embedded outputs (GitHub-renderable)
  scripts/
    result1_summary_stats.py                      builds features.parquet and Result 1 stats
    result3_rf_importance.py                      runs the RF and saves Result 3 chart
  src/
    __init__.py
    data_loader.py                                URL fallback downloaders
    data_processing.py                            merge + drop-unmatched + parquet save
  report/
    progress_report_blockers.md                   blockers organised by role
    result3_feature_importance.png                Result 3 chart
```

## Code standards

Enforced across every module and notebook in this repo:

- No function longer than 10 lines of code.
- No emojis anywhere (source, comments, markdown, notebook cells, print output).
- Every code cell in every notebook is preceded by a markdown cell explaining the
  "what" and "why".
- Notebooks must run end-to-end with "Run All" and no manual intervention.
- All code is modular (functions live in `src/`, notebooks and scripts import them)
  and reproducible (downloads are cached; seeds are explicit, default `random_state=148`).

## AI-usage disclosure (stub)

Per Econ 148 course policy, any use of AI tools in producing this repo is
disclosed here. This section will be updated with specifics before the final
submission. Planned disclosures:

- Whether AI was used to draft code, and if so, where.
- Whether AI was used to edit prose in the report, and if so, where.
- Whether AI was used to explore alternative model specifications, and if so,
  which were considered.

No AI-generated output is used without human review and verification.
