# RF section (Emily's contribution to the final report)

The three written contributions Leo asked for are below: Model section
(RF half), Results section (RF half), and one Discussion paragraph on
RF limitations. All numbers are taken from
`notebooks/03_random_forest_executed.ipynb` and are reproducible by
re-running that notebook (or `scripts/result3_rf_importance.py` for the
all-38 chart alone) with `random_state=148`.

## Model section - RF half

We complement the OLS specification with a random-forest regressor
(`sklearn.ensemble.RandomForestRegressor` from scikit-learn 1.8). The
random forest is well-suited to this exercise because the research
question is, by construction, about what the OLS spec misses: each
decision tree learns piecewise-constant splits on the feature space, and
averaging across 300 trees produces a smooth nonparametric estimate of
the conditional mean `E[kfr_pooled_pooled_p25 | X]` that can represent
threshold effects, plateau regions, and pairwise interactions that a
linear no-interaction OLS cannot.

We hold the hyperparameters fixed at standard defaults: `n_estimators =
300` (large enough for stable feature-importance estimates, beyond which
returns diminish), `max_depth` unconstrained (we let trees grow fully and
rely on averaging across the 300 trees to control variance), the
default `min_samples_split = 2` and `min_samples_leaf = 1`, and the same
80/20 train-test split used in the OLS evaluation. `random_state = 148`
seeds both the train-test split and the bootstrapping inside each tree
so that all numbers in the report are bit-for-bit reproducible.

We report two complementary feature-importance measures because each
captures a different facet of "what the forest uses". *Mean decrease in
impurity* (MDI) is accumulated during training: at every split, the
forest records the reduction in mean-squared error attributable to the
splitting feature, and the totals are normalised so they sum to one
across the 38 covariates. MDI is fast and exact for the fitted forest
but is biased toward high-cardinality features, because continuous
variables can produce more candidate split points than discrete ones,
which inflates their accumulated impurity reduction. *Permutation
importance* shuffles one column at a time on the held-out test set and
records the resulting drop in test R^2; with `n_repeats = 20` the
resulting means are stable. Permutation importance is model-agnostic,
scale-free, and unbiased toward cardinality, which makes it the more
reliable measure for comparing the RF ranking against the OLS
coefficient ranking on identical features. We accordingly report MDI on
the all-38 covariate model (Result 3 chart, intended as exploratory) and
permutation importance on the six-variable OLS-aligned model (Result 3b
chart, intended as the head-to-head comparison with OLS).

## Results section - RF half

The all-38-covariate random forest reaches test R^2 = 0.642 and
RMSE = 0.0386 on the held-out 626-county test set, comparable to the OLS
R^2 reported by Kabir on the same six-predictor subset and only 0.004
points below the RF refit on the same six predictors (RF six-predictor
test R^2 = 0.638). The MDI ranking (Result 3, Figure
`report/result3_feature_importance.png`) concentrates importance on
three predictors: Social Capital Index (0.356), Fraction with Commute
under 15 Minutes (0.163), and Fraction Black (0.126). Together those
three account for 64.4 percent of the total impurity reduction across
all 300 trees; the remaining 35 covariates each contribute less than
four percent. The headline pattern - that social-capital and
short-commute density carry the most predictive weight - matches Chetty
et al. (2014)'s univariate-correlation finding that social capital is
the strongest single county-level correlate of intergenerational
mobility.

Permutation importance on the six OLS-aligned predictors (Result 3b,
Figure `report/result3b_permutation_importance.png`) is the cleanest
direct comparison to Kabir's OLS coefficient table. It ranks Social
Capital Index first (mean drop in held-out R^2 of +0.261), Fraction of
Children with Single Mothers second (+0.222), and Fraction with Commute
under 15 Minutes third (+0.162). Two predictors that the OLS reports as
statistically significant - Racial Segregation and the income-adjusted
Test Score Percentile - have permutation importance indistinguishable
from zero (mean drops of -0.003 and -0.005, respectively, where the
small negative sign is sampling noise from the 20 random-shuffle
repeats). The substantive reading is that those two predictors carry
in-sample explanatory power that does not survive a held-out test, once
the other four predictors are in the model. This is the first piece of
evidence the random forest surfaces that the OLS misses: significance
in-sample does not imply predictive content out-of-sample, and the gap
matters more for the policy interpretation than for the test R^2.

The second piece of evidence comes from the partial-dependence panel
(Result 3c, Figure `report/result3c_partial_dependence.png`). The
marginal effect of each top-MDI predictor on `kfr_pooled_pooled_p25` is
visibly nonlinear for three of the top four. Social Capital Index is
nearly flat below the value 0.7, then jumps approximately 0.08 (about
1.3 standard deviations of the outcome) over a narrow range from 0.7 to
1.1, then plateaus near 0.49. Fraction with Commute under 15 Minutes
shows a similar threshold near 0.5. Fraction Black shows a step-down
around 0.21: counties below that threshold cluster at predicted ranks of
0.44, while those above drop to about 0.40. These threshold structures
are precisely what the OLS spec assumes away by entering all covariates
linearly with no interactions or splines, and they are part of the
explanation for why the RF's six-predictor R^2 (0.638) is comparable to
the OLS R^2 even though OLS gets to weight each predictor optimally for
in-sample fit. In other words, the RF and the OLS land in similar
neighbourhoods on aggregate fit but for very different reasons: the OLS
distributes explanatory load relatively evenly across the six
predictors, while the RF concentrates roughly ninety percent of its
out-of-sample predictive content in three of them and learns sharp
threshold structure within each.

## Discussion - RF limitations

Three limitations of the random-forest analysis warrant flagging.
First, the RF estimates conditional means, not causal effects: the
partial-dependence plots show how predicted county mobility varies with
each covariate when the other covariates are held at their averages,
but they cannot be read as the counterfactual change in mobility we
would expect from policy intervention on, say, Social Capital Index,
because the underlying covariates are jointly determined and almost
certainly correlated with omitted confounders at the commuting-zone
level. Second, mean-decrease-in-impurity is structurally biased toward
high-cardinality continuous features; in our setting that includes
Census 2000 population and several percentage-share variables. We
mitigate the bias for the head-to-head OLS comparison by reporting
permutation importance on the six-variable subset, but the all-38 MDI
ranking should still be read with this bias in mind, particularly the
relative position of any binary or low-cardinality flag among the
covariates. Third, every predictor in the model is a CZ-level variable
broadcast onto the county frame via the crosswalk Paul built (Data
section); within-CZ variation in `kfr_pooled_pooled_p25` must therefore
be explained by variables that do not vary within a CZ, which
mechanically caps the RF's R^2 at the share of between-CZ variance in
the outcome. The 0.642 figure should be interpreted as how well
CZ-level structural correlates explain *between-CZ* differences in
county-level outcomes, not as a forecast of mobility for any individual
county within a commuting zone.
