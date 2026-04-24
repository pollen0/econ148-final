# Econ 148 Final Project - Intergenerational Mobility Across US Counties

**Team:** Paul Lin (data engineering), Kabir, Emily
**Track / Topic:** A-4, Intergenerational Mobility Across US Counties

## Project description

We study what interactions between Chetty's five core correlates of intergenerational
mobility (racial and income segregation, income inequality, school quality, social
capital, and family structure) a random forest is able to capture in US county-level
mobility outcomes that an OLS linear model misses. Our feature and outcome data come
from the Opportunity Insights publications "Where is the Land of Opportunity?"
(Chetty, Hendren, Kline, Saez, QJE 2014) and "The Opportunity Atlas" (Chetty,
Friedman, Hendren, Jones, Porter, 2018). The main deliverable is a comparison of OLS
and random forest fits with partial-dependence and SHAP-style interaction analyses
highlighting where the forest's nonlinear structure adds explanatory power.

## Setup

```bash
git clone <repo-url> econ148-final
cd econ148-final
pip install -r requirements.txt
jupyter lab
```

Open `notebooks/01_data_inspection.ipynb` and select "Run All". The notebook will
download the three source files into `data/raw/` on the first run (about 40 MB
total); subsequent runs use the cached copies.

## Data sources

All three files are downloaded at runtime by `src/data_loader.py`; none are
committed to the repo (see `.gitignore`).

| # | Dataset | Loader function | Primary URL |
|---|---------|-----------------|-------------|
| 1 | Chetty et al. 2014, online data tables (county and commuting-zone covariates) | `get_chetty_2014()` | `http://www.equality-of-opportunity.org/data/descriptive/table1/online_data_tables.xls` (canonical mirror; the original `opportunityinsights.org/wp-content/uploads/2018/03/online_data_tables-8.xlsx` now returns 404) |
| 2 | Opportunity Atlas tract-level outcomes (simple variant) | `get_opportunity_atlas_tract()` | `https://www2.census.gov/ces/opportunity/tract_outcomes_simple.csv` (~33 MB; the full `tract_outcomes.zip` at 958 MB is also documented in the loader but not downloaded by default) |
| 3 | Opportunity Atlas county-level outcomes rollup (day-1 outcome) | `get_county_outcomes()` | `https://www2.census.gov/ces/opportunity/county_outcomes_simple.csv` |

Each loader tries a list of URLs in order and falls back to the next when a URL
fails, so the notebook records the exact source actually used on each run.

## Directory structure

```
econ148-final/
  README.md
  requirements.txt
  .gitignore
  data/
    raw/            downloaded files land here (git-ignored)
    processed/      cleaned / merged files (git-ignored)
  notebooks/
    01_data_inspection.ipynb
  src/
    __init__.py
    data_loader.py
  report/           progress report and final writeup artifacts
```

## Code standards

Enforced across all modules and notebooks in this repo:

- No function longer than 10 lines of code.
- No emojis anywhere (source, comments, markdown, notebook cells, print output).
- Every code cell in every notebook is preceded by a markdown cell explaining the
  "what" and "why".
- Notebooks must run end-to-end with "Run All" and no manual intervention.
- Any data not pulled from a public endpoint at runtime must be committed under
  `data/` with a clear path; everything currently used is pulled at runtime.
- All code is modular (functions live in `src/`, notebooks import them) and
  reproducible (downloads are cached; seeds where used are explicit).

## AI-usage disclosure (stub)

Per Econ 148 course policy, any use of AI tools in producing this repo is
disclosed here. This section will be updated with specifics before the final
submission. Planned disclosures:

- Whether AI was used to draft code, and if so, where.
- Whether AI was used to edit prose in the report, and if so, where.
- Whether AI was used to explore alternative model specifications, and if so,
  which were considered.

No AI-generated output is used without human review and verification.
