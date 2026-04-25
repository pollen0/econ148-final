# Progress Report - Blockers and Open Issues

Compiled 2026-04-24 from the day-1 data-engineering pass. Items below are
organised by the team-member role they affect; items that surfaced through
Paul's work but block Kabir or Emily downstream are listed under the role they
will land on.

## Paul (Data Engineer)

Resolved before Progress Report submission:

- Three of the brief's primary download URLs returned 404 or 403 in 2026:
  the Chetty 2014 `.xlsx` paths under `/wp-content/uploads/2018/03/`, and the
  Atlas `county_outcomes.csv` on opportunityinsights.org. The loader now
  falls through to the live mirrors (the 2018/04 `.xls`,
  `equality-of-opportunity.org`, and `www2.census.gov/ces/opportunity/`)
  and prints every attempt to the notebook on each run.
- The full Opportunity Atlas `tract_outcomes.zip` is 958 MB and would blow
  through any reasonable notebook Run All budget. We substitute the
  `tract_outcomes_simple.csv` variant (~33 MB), which preserves
  `kfr_pooled_pooled_p25` plus the race and gender disaggregations.

Open items that need a team decision:

- Merge edge cases: 89 of 3,219 Atlas counties have no Chetty 2014
  covariates after the county-FIPS join (Puerto Rico, Guam, USVI, Northern
  Marianas, plus a handful of counties whose FIPS were reorganised after
  2014). The same gap propagates to the CZ-covariate merge - 97.24% match
  rate. Drop these rows or impute the covariates from CZ averages?
- Sheet selection: the brief named Chetty Online Data Table 5 as the
  source of the "famous five" covariates, but in the 2014 workbook Table 5
  carries CZ-level mobility *estimates* while the covariates live in
  Table 8. The notebook's CZ merge preview now uses Table 8; Kabir needs to
  confirm before this lands in the Progress Report wording.

## Kabir (Econometrics)

Heads-up Paul has loaded for him:

- Online Data Table 8 carries 38 CZ-level covariate columns. Candidate
  mappings to Kabir's five-variable spec, for him to confirm in his
  Progress Report sentences:
    - Segregation: `Racial Segregation`, `Income Segregation`,
      `Segregation of Poverty (<p25)`, `Segregation of Affluence (>p75)`
    - Income inequality: `Gini`, `Top 1% Income Share`, `Gini Bottom 99%`
    - School quality: `Test Score Percentile (Income Adjusted)`,
      `High School Dropout Rate (Income Adjusted)`,
      `School Expenditure per Student`, `Teacher Student Ratio`
    - Social capital: `Social Capital Index`, `Fraction Religious`,
      `Violent Crime Rate`
    - Family structure: `Fraction of Children with Single Mothers`,
      `Fraction of Adults Married`, `Fraction of Adults Divorced`
    - Commuting (the fifth in the brief): `Frac. with Commute < 15 Mins`

Open items that need a team decision:

- The features are at the CZ level (741 CZs); the outcome
  `kfr_pooled_pooled_p25` is on the county frame (3,219 counties). Run the
  OLS at the county level with CZ features broadcast (current default in
  the merge preview), or aggregate the outcome up to CZ for a 741-row
  regression?
- The five-correlate brief mentions both "school quality" and "social
  capital", but the brief sentence in the role description only lists four
  of the five named correlates ("segregation, school quality, family
  structure, income inequality, commuting" - social capital is missing).
  Kabir to clarify whether his OLS spec includes social capital.

## Emily (ML Engineer)

Environment blocker that will bite as soon as Emily imports sklearn next to
matplotlib in the same notebook:

- Paul's anaconda env shipped numpy 2.4.3 paired with C-extension packages
  built against the numpy 1.x ABI: matplotlib 3.9.2, numexpr 2.8.7, and
  bottleneck 1.3.7. The notebook's imports cell ran successfully on the
  surface but raised captured `_ARRAY_API not found` ImportErrors that made
  `nbconvert --execute` flag a clean Run All as failed. Fix is now pinned
  in `requirements.txt`: matplotlib >= 3.9.3, numexpr >= 2.10,
  bottleneck >= 1.4, numpy >= 2.0,<3.0. Action for Emily: install with
  `pip install -r requirements.txt` rather than conda for these specific
  packages, then sanity-check with
  `python -c "import sklearn, matplotlib, pandas, numpy; print('ok')"`.
- If Emily uses Google Colab the pinned floors apply automatically on a
  fresh kernel; the runtime there ships numpy 2.x already, so a vanilla
  `!pip install -r requirements.txt` at the top of her notebook is enough.
  sklearn 1.5.1 imports cleanly post-upgrade and
  `from sklearn.ensemble import RandomForestRegressor` is available.

Heads-up Paul has loaded for her:

- The merged feature matrix from notebook section 4 is roughly (3,130, 38)
  for the OLS spec, with the same shape suitable as the RF input. Once the
  team agrees on impute-or-drop for the 89 unmerged counties, Paul will
  save a cleaned `features.parquet` under `data/processed/` that Emily's
  RF pipeline can read directly without re-running the merge.

## Cross-cutting note for Leo's eyes

The day-1 inspection notebook
(`notebooks/01_data_inspection_executed.ipynb`, viewable on GitHub with
embedded outputs) is the reference document behind every blocker above.
Cell-level numbers (FIPS overlap counts, match rate, missingness) regenerate
on every Run All from live data, so figures cited here will move slightly
if Opportunity Insights revises any source file.
