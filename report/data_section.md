# Data section (Paul's contribution to the final report)

## Sources and download

Our analysis combines three publicly archived datasets from the Opportunity
Insights research group plus a county-to-commuting-zone crosswalk. The first is
the Chetty, Hendren, Kline, and Saez (2014) "Where is the Land of Opportunity?"
online data tables (`online_data_tables.xls`). We use Online Data Table 8,
which records 38 commuting-zone-level covariates for 741 commuting zones,
including the racial- and income-segregation indices, the Gini coefficient and
top-percentile income shares, the income-adjusted test-score and
high-school-dropout indices, the Social Capital Index, and the family-structure
variables (fraction of children with single mothers, fraction of adults married
or divorced) that constitute the "famous five" plus a commuting variable
(fraction with commute under 15 minutes). The second is the Opportunity Atlas
(Chetty, Friedman, Hendren, Jones, and Porter, 2018) distributed by the U.S.
Census Bureau's Center for Economic Studies as the county-level rollup file
`county_outcomes_simple.csv`; this provides our outcome variable
`kfr_pooled_pooled_p25`, the mean income rank of children whose parents were
at the 25th percentile of the national family-income distribution, for 3,219
US counties. The third is the corresponding tract-level outcomes file used as
a robustness reference. The crosswalk file `cty_cz_st_crosswalk.csv` maps the
five-digit county FIPS to commuting-zone identifiers for 3,138 counties. All
four files are pulled at runtime by `src/data_loader.py`, which tries each
canonical URL in order and falls back automatically when an upstream path has
been reorganised. The
`opportunityinsights.org/wp-content/uploads/2018/03/...` URLs originally cited
in the project brief now return 404 or 403 status codes; the loader
transparently falls through to the live mirrors at
`equality-of-opportunity.org` and `www2.census.gov/ces/opportunity`. Each
download is cached under `data/raw/`, and the four files are checked into the
repository so a fresh clone reproduces the analysis without network access.

## FIPS merge and the 89 unmatched counties

We construct the analytic frame by merging the Chetty 2014 commuting-zone
covariates onto the county-level Atlas outcome via the crosswalk. The merge
key is a five-digit county FIPS code computed as `state * 1000 + county`,
which exactly matches the integer-packed FIPS representation used both by
Chetty 2014's Online Data Table 3 and by the crosswalk's `cty` column; we
verified the encoding by spot-checking against the county names in each
source. Of the 3,219 county rows in the Atlas outcome file, 89 (2.77 percent)
have no covariate match: 78 are Puerto Rico municipios, which lie outside the
50-state-plus-DC scope of Chetty et al. (2014); 8 are Alaska boroughs whose
FIPS codes were reorganised after the 2014 crosswalk was published; and 3 are
post-2014 county renamings (Broomfield County, Colorado, which incorporated
in 2001; Miami-Dade County, Florida, which the older crosswalk lists under
the legacy name "Dade"; and Oglala Lakota County, South Dakota, which was
renamed from Shannon County in 2015). We chose to drop these 89 rows rather
than impute their covariates because each unmatched FIPS lacks a
meaningful 2014-era commuting-zone assignment, and imputing covariates from
neighbouring CZ averages would invent CZ identities for places that
genuinely have none in the source paper. The cleaned analytic frame
contains 3,130 counties and is saved as `data/processed/features.parquet`
(106 columns, 1.78 MB) for the OLS and RF notebooks to read directly.

## Missingness and Result 1 summary statistics

Within the cleaned 3,130-row frame the residual missingness is small. The
outcome `kfr_pooled_pooled_p25` is missing for 4 of 3,130 counties (0.13
percent), the income-adjusted test-score percentile (school quality) is
missing for 44 counties (1.41 percent), and the Social Capital Index is
missing for 25 counties (0.80 percent); the other four predictors have no
missing values at the county level after the merge. The OLS specification
will use list-wise deletion on the six predictors and the outcome (yielding
3,063 effective observations, 97.9 percent of the cleaned frame); the RF specification mean-imputes the
predictors before fitting because tree models are sensitive to the small
deletions list-wise would imply at every split. Table 1 reports the means,
standard deviations, and ranges for the six predictors plus the outcome,
which together motivate our analysis.

| Variable | n | Mean | SD | Min | Max |
|----------|--:|----:|---:|----:|----:|
| Segregation (Racial Segregation index) | 3130 | 0.1543 | 0.1008 | 0.0000 | 0.5537 |
| Income inequality (Gini) | 3130 | 0.4208 | 0.0777 | 0.2018 | 0.8473 |
| School quality (Test Score Pct, income adjusted) | 3086 | -0.3035 | 7.3142 | -32.7852 | 20.0705 |
| Social capital (Social Capital Index) | 3105 | 0.0284 | 1.1600 | -3.1990 | 7.3054 |
| Family structure (Fraction of Children with Single Mothers) | 3130 | 0.2088 | 0.0499 | 0.0818 | 0.4337 |
| Commuting (Frac. with Commute < 15 Mins) | 3130 | 0.4095 | 0.1303 | 0.1561 | 0.9451 |
| **Outcome** (`kfr_pooled_pooled_p25`) | 3126 | 0.4302 | 0.0620 | 0.2423 | 0.6883 |

Two features of these descriptive moments motivate the modelling that
follows. First, the outcome `kfr_pooled_pooled_p25` itself spans nearly
half the income distribution (the 0.242-0.688 range corresponds to an
expected adult income rank from the 24th to the 69th percentile for the
same starting parental percentile of 25), confirming that there is
substantial county-level variation to be explained. Second, the
predictors are heterogeneously scaled: the segregation index and the
single-mother fraction are bounded shares with standard deviations near
0.05-0.10, while the income-adjusted school-quality and social-capital
indices are residuals from national regressions and so are centred near
zero with much wider unstandardised variance (SD = 7.3 and 1.2
respectively). The OLS model will therefore report standardised-coefficient
versions to make the magnitudes comparable across predictors, and the
random forest is unaffected by scale and uses the raw values directly.
