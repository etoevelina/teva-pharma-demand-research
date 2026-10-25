# INN and ATC Features for Drug Sales Forecasting and Cold Start: Experimental Report

## 1. Research question and hypothesis

**Research question.** How much do the INN (International Nonproprietary Name, the active substance) and the ATC (Anatomical Therapeutic Chemical) classification improve the accuracy of drug sales forecasts, especially in a cold start, when a new product has no sales history of its own?

**Hypothesis.** Pharmaceutical attributes place a product among related products (same substance, same therapeutic group). Sales of these peers carry information about the level and seasonality of a new product, so a model that knows INN and ATC should forecast products without their own history better than a model that knows only the dosage form, strength and pack size.

Every result in this report comes from the final code in this repository and can be reproduced with the commands in the README; the source of each number is given as a path under `results/`. A few diagnostic numbers from development runs (Section 3.4, the `max_ctr_complexity` speed check and the loss-selection note in Section 4) are marked as such: they describe pipeline versions or checks that are not reproduced by the final code.

## 2. Dataset description

### 2.1 Source and structure

The data come from the public repository *Marchev-Science / case-forecasting-pharmacutical-demand* (MIT license), prepared in partnership with Teva. It contains two files with the same structure:

| File | Rows (SKUs) | INNs | Role in this study |
|---|---|---|---|
| `teva_sales.csv` | 13,762 | 1,776 (+ 931 SKUs without an INN) | all experiments |
| `teva_sales_small.csv` | 1,730 | 20 | exact subset of the full file (identical IDs and values, `source_files_check.md`); unit tests and the prototype notebook |

The repository also contains a README with column definitions, an example of the ATC tree and a general company presentation on machine learning at Teva; neither adds data.

Each row is one SKU (`Morion ID`) with 10 attribute columns and 60 monthly columns (`2019 01` … `2023 12`). The monthly values are **quantities sold, in packs**. There are no revenue, price, stock, stock-out, promotion or tender columns. The target variable is therefore *packs sold per SKU per month*. This is sales, not true patient demand: when a product is out of stock, sales are zero even if there is demand.

Main characteristics (`results/tables/dataset_characteristics.md`, `hierarchy_levels.md`, `hierarchy_checks.md`):

| Characteristic | Value |
|---|---|
| Unit of observation | SKU × calendar month |
| Period | 2019-01 … 2023-12 (60 months) |
| SKUs / INNs | 13,762 / 1,776; 931 SKUs (6.8%) have no INN |
| ATC level 1 / 2 / 3 / 4 / 5 groups | 14 / 90 / 224 / 586 / 1,563 |
| Brands (anonymized) / dosage forms (NFC1) | 4,895 / 16 |
| SKU-month cells / on the market after the first sale | 825,720 / 725,045 (87.8%) |
| Zero sales among on-market SKU-months | 22.1% |
| Total volume | 4.93 billion packs |
| SKUs already selling in 2019-01 (launch unobserved) | 9,712 |
| SKUs with an observed first sale (2019-02 … 2023-12) | 4,050 |

**INN and ATC availability was checked, not assumed.** All five ATC levels are filled for every SKU, except 14 placeholder ATC4 codes. ATC is a strict tree: no ATC2–ATC5 code has more than one parent. INN is a real value for 12,831 SKUs. The other **931 SKUs carry a placeholder** in the raw file (a non-breaking space followed by `-`). These are products without an INN: herbal products, cold preparations, local combinations. If the placeholder were read as a value, it would be the largest "INN" in the data. It is treated as missing: such SKUs belong to no INN group and never count as having a "known INN". In the INN split each of them forms a unit together with its identical twins (931 SKUs, 856 units).

ATC5 is almost one-to-one with INN: 155 of 1,563 ATC5 codes contain more than one INN, and 188 of 1,776 INNs appear under more than one ATC5. ATC1–ATC4 group several INNs (median 132.5, 16, 5 and 2 INNs per group), which is what makes transfer to an unseen INN possible. 137 INNs appear in more than one ATC2 group (for example, a substance with both systemic and topical forms). Further irregularities: 595 SKUs carry a level-4 code in the ATC5 field, and 1,525 SKUs carry non-standard local ATC5 codes marked `**`.

### 2.2 Data quality

`results/tables/data_quality.md` lists every check. Apart from the placeholders above, there are no missing attribute values, no missing or negative sales and no duplicated IDs. The main findings:

* **Zeros have three different meanings.** Of 261,130 zero cells (31.6%):
  * 100,675 come before the SKU's first sale: the product is not yet on the market;
  * 26,538 are gaps between the first and the last sale (4.5% of the active span), meaning no demand or a stock-out, which cannot be told apart without stock data;
  * 133,917 come after the last sale: discontinued, or right-censored at 2023-12.

  Pre-launch zeros are treated as "not on the market": they are excluded from training targets and own-history features. Gaps and post-exit zeros are kept as real zeros in targets and history features. Peer-group statistics are averages per *selling* SKU, so they ignore zero months of any kind.
* **Non-integer volumes.** 99.6% of positive values are non-integer. The volumes are probably projected or estimated from a panel, not raw counts.
* **Identical twins.** 1,981 SKUs form 814 groups with identical ATC5, brand, INN, form and description but different IDs. In 699 of these groups all members are on sale together at some point. In the simulated cold-start splits twins are always kept on the same side; in the real-launch scenario an older twin of a launch is part of the training data (it was on the market before) but is excluded from the launch's peer statistics.
* **Outliers.** 3.77% of positive months deviate by more than 3.5 robust standard deviations from the SKU's own log level. They are kept: heavy tails are genuine for pharmacy sales, and removing them would bias the evaluation.

**Description parsing.** Strength, package content, number of doses and pack size are extracted from the free-text `Description` with a regex heuristic (`src/teva_forecast/data.py`). Cyrillic units (мг, мкг, мл, г, АЕ) occur in the descriptions of 17 SKUs (12 distinct strings) and are mapped to Latin units first; the sign № is mapped to #. Coverage (`description_parsing_coverage.md`): strength 77.3% of SKUs, pack count 88.2%, package content 40.4%. A random sample of 60 SKUs (seed 7; 59 distinct descriptions) was checked by hand. The verdicts are in `reports/description_parsing_audit.csv` and the sample is in `results/tables/description_parsing_audit_sample.md`. The descriptions of 58 SKUs were parsed fully correctly. Both errors read the gram mass of a herbal or granulate package as strength.

### 2.3 Exploratory analysis

Figures are in `results/figures/eda_*.png`, tables in `results/tables/`.

* **Extreme skew.** The mean monthly volume per SKU (on-market months) has a median of 706 packs, a 90th percentile of 13,373 and a maximum of 2.04 million. The top 1% of SKUs account for 31.4% of the volume, the top 10% for 74.5% (`eda_key_numbers.md`, `hierarchy_checks.md`, `eda_sku_distribution.png`).
* **Structural breaks.** Total monthly volume spikes in March 2020 (118.8 M packs) and collapses in April (66.3 M). It falls again from 109.0 M in February 2022 to 54.0 M in April 2022, and annual volume in 2022–2023 stays about 21% below 2021 (845 M and 849 M against 1,068 M packs). The number of selling SKUs per month stays between 9,215 and 9,712 (`eda_key_numbers.md`, `eda_monthly_total.png`). The 2022 break falls in the validation year, which therefore is harder than the test year.
* **Seasonality.** Anti-infectives (J), respiratory products (R) and immunomodulators (L) peak in winter (seasonal index 1.28–1.33 in January) and reach their lowest values in summer (0.58–0.68 in June or July). Cardiovascular and alimentary products are flatter (`eda_seasonality_atc1.png`, `seasonal_index_atc1.md`). The median lag-12 autocorrelation is 0.27, computed for the 10,323 SKUs with at least 36 months on the market and at least 24 valid month pairs with non-zero variance (`lag12_autocorrelation_summary.md`).
* **Group composition.** ATC groups differ strongly in assortment size vs volume. For example, antineoplastic agents (L) are 5.6% of SKUs but 0.3% of packs, while the nervous system (N) is 14.3% of SKUs and 18.3% of packs (`atc1_composition.md`, `eda_atc1_composition.png`).
* **Launches.** 617–797 SKUs enter per year in 2020–2023 (`eda_key_numbers.md`, `eda_lifecycle.png`). A new SKU sells a median of 5% of its later level in its first month, 68% by month 6 and 111% by month 12, relative to its mean of months 7–12. The curve uses the 1,915 SKUs first sold 2020-01 … 2022-12 with positive sales in months 7–12 (`launch_curve.md`).
* **How informative is the group?** Predicting a SKU's log mean volume by the mean of the *other* SKUs of its group explains only 6% of the variance for the dosage form, 10–16% for ATC levels 1–5 and 13.5% for INN (leave-one-out R²; SKUs without a peer are predicted by the overall mean; `group_informativeness.md`). Within one INN, volume varies by orders of magnitude with strength, pack size and brand. This already suggests that INN and ATC can give a new product a better starting level, but cannot replace its own history.

## 3. Methodology

### 3.1 Forecasting task

Forecasts are monthly SKU-level volumes, 12 months ahead, issued once a year at the end of December for the 12 months of the following year (annual planning). Every row of a model's data is a pair (SKU, target month t) with origin T = December of the previous year and horizon h = month(t) ∈ 1…12. Every feature is computed from data up to T. The one exception is the launch month of a new product in scenario N, which is treated as known in advance (a planned launch date). The dataset README recommends this 12-month horizon.

### 3.2 Preprocessing pipeline

`scripts/prepare_data.py` downloads the raw CSV, verifies its SHA-256 checksum and validates the schema (10 attribute columns, 60 consecutive month columns, unique IDs, no missing or negative sales). It then cleans the attributes (whitespace, non-breaking spaces, placeholders), derives lifecycle fields (first and last sale, launch observed or left-censored, twin clusters, INN units, number of INN components) and parses descriptions. Months before the first sale are marked as "not on the market". The results are a SKU attribute table and a long SKU × month panel in `data/processed/`. The monthly granularity of the source is kept: weekly or daily data do not exist, and monthly buckets match the 12-month planning horizon.

### 3.3 Features

The full list is in `reports/data_dictionary.md`. Groups:

* **Calendar:** month, quarter, sin/cos of the month. The year is computed but not used as a model input, because tree models cannot extrapolate to the unseen test year. Trends enter through origin-time features instead.
* **Product presentation (control features, every model):** dosage form (NFC1, categorical), strength and its unit, package content and its unit, number of doses, pack size, combination flag.
* **Own history (scenario A only):**
  * last value, 3/6/12-month means, 12-month std and max, share of zero months;
  * 6-month trend and year-over-year ratio;
  * the values 12 and 24 months before the target month (both ≤ T because h ≤ 12);
  * months on the market.

  Lags 1–11 relative to the target and rolling windows ending after T are never used: they would need actual sales from inside the forecast horizon.
* **Launch age (scenario N only):** months since the planned launch at the target month. A launch date is known to the business before launch.
* **Peer-group statistics** for the global market, the dosage form, the INN, INN × form and each ATC level: average sales per selling SKU over the last 12 months, 6-month trend, number of selling SKUs at T, average sales per selling SKU in the same month one year earlier, and the implied seasonal index.
* **INN block:** number of INN components, INN and INN × form peer statistics.
* **ATC block:** peer statistics of ATC levels 1–5.

In the main models INN and ATC enter **only through peer statistics**, not as raw category codes. For an unseen INN or ATC group the code carries no information at prediction time. In training, however, CatBoost's target statistics for the code are computed from the same SKUs' targets. A model would therefore learn to rely on the code and then lose it exactly in the cold-start case. A sensitivity arm in scenarios A and B adds the codes (INN, ATC1–ATC5) as CatBoost categories to measure what they contribute beyond the peer statistics.

The brand code is not used. It identifies the product family almost uniquely, so it would act as a SKU identifier and blur the question about INN and ATC.

### 3.4 Leakage control

1. **Temporal.** All features come from months ≤ T, apart from the planned launch month in N. The test year 2023 is never used for any choice. The validation year 2022 is used only for the loss function, the number of trees and the choice of the best baseline, plus one development speed check (`max_ctr_complexity`, Section 4).
2. **Cold-start isolation.** Held-out products are removed from training rows and from every peer statistic. Their own sales never enter any feature (tested in `tests/test_pipeline.py`).
3. **Peer statistics by cross-fitting.** This point took three iterations, documented here because it decides whether the INN/ATC comparison is valid.
   1. Leave-one-out group means for training rows leaked. Together with the group identity (the group's selling-SKU count drops by one exactly when the SKU itself sold), a tree model can recover the SKU's own past sales. In a diagnostic run training WAPE fell to 0.27, while forecasts for new products collapsed toward zero (total bias −92%).
   2. 5-fold out-of-fold statistics still reduce to leave-one-out whenever a SKU is the only member of its group in its inner fold, and that is frequent for small INNs and ATC4 groups. An independent read-only audit of the code found this and reproduced it on the 20-INN sample.
   3. The final design separates the SKUs a model learns from and the SKUs that supply its peer statistics. The training pool is split into two halves by the scenario's grouping unit (twin cluster in B and N, INN unit in C, ATC2 in D, ATC1 in D1; in D and D1 the donor half also drops every INN present in the training half). Model *m* is trained on half *m* with peer statistics computed only from the other half (the donors). Each evaluated SKU is forecast by both models with their donors, and the two forecasts are averaged. In N, an evaluated launch's own twin cluster is also removed from its donors, so that an older identical twin never enters its peer statistics; training rows never have their twin among the donors either.

   Inside one model, the statistics of a group are identical for all of its training SKUs and for any evaluated SKU of that group, except in N, where an evaluated launch additionally loses its own twin cluster from its donors. They never depend on the SKU's own sales, which is what an unseen product sees. Scenario A, where a SKU's own history is a legitimate input, uses one model on all SKUs and removes each SKU's own twin cluster from its peer group, identically for training and evaluation rows. Tests check that perturbing every training SKU's sales leaves its peer statistics unchanged, that training and evaluated SKUs of the same group get identical statistics, that every multi-cluster INN of B is present in both halves, and that a launch's statistics do not depend on its older twin. A second independent read-only audit of the rewritten code found no remaining leakage. It did find the B and N measurement issues fixed above, so that "known INN" now means known to both models, and the twin handling in N.
4. **Twins** stay on the same side of every simulated cold-start split; in N see point 3.

### 3.5 Models

* **Baselines for existing products:** naive (last observed month), seasonal naive (same month last year; for a target month whose value 12 months earlier precedes the first sale, the mean of the available months up to the origin), and the 12-month moving average over the months on the market.
* **Baselines for cold start:** global mean, dosage-form mean, and a **hierarchical group mean / median**. The hierarchical baselines use the most specific peer group with at least 3 selling SKUs, in the order INN × form → INN → ATC5 → ATC4 → ATC3 → ATC2 → ATC1 → form → global, and take the same calendar month one year earlier, computed from the whole training pool. For real launches, also a **launch-age mean**: the average volume of past launches at the same month since launch.
* **CatBoostRegressor** with four arms that share every control feature:

| Arm | INN block | ATC block |
|---|---|---|
| no INN/ATC | – | – |
| INN only | ✓ | – |
| ATC only | – | ✓ |
| INN + ATC | ✓ | ✓ |
| INN + ATC + category codes (A and B only, sensitivity) | ✓ + INN code | ✓ + ATC1–5 codes |

In scenario A all arms also receive the own-history block. The arm "no INN/ATC" with history is the "CatBoost with historical features" model, and the other arms measure what pharmaceutical attributes add on top of history. A separate model is trained for every scenario, fold, arm and cross-fitting half.

### 3.6 Scenarios

| Scenario | Question | Split | Evaluated products |
|---|---|---|---|
| **A** Existing drug | value of INN/ATC when history exists | temporal only | SKUs with ≥ 1 sale in the 12 months before the origin |
| **B** New product, known INN | new SKU of a substance already on the market | 5-fold group split by twin cluster; cross-fitting halves alternate the twin clusters of each INN, so that an INN with two or more clusters is present in both halves | held-out SKUs with ≥ 1 sale in the 12 months before the origin, whose INN is sold in those 12 months by donor SKUs of **both** cross-fitted models |
| **C** New INN, known ATC | new substance, known therapeutic group | 5-fold group split by INN unit (SKUs without an INN are grouped with their identical twins) | held-out SKUs with ≥ 1 sale in the 12 months before the origin |
| **D** Unseen ATC group | new therapeutic subgroup; only ATC1 is known | 5-fold group split by ATC2; INNs of the held-out groups also removed from training | as in C |
| **D1** Unseen ATC1 group (strict) | nothing pharmaceutical is known | 5-fold group split by ATC1 (14 groups); INNs of the held-out groups also removed | as in C |
| **N** Real launches | products whose first sale falls in the evaluation year | launch-date split | SKUs first sold in the evaluation year, months from launch on |

B, C, D and D1 are **simulated cold starts**: the "new" products are established SKUs, and selecting those that sold before the origin conditions on their being on the market. Their history is hidden from the model, but their market situation is that of an established product. Scenario N uses the real launches. In 2023 there were 617 of them: 555 with an INN already sold before 2023, 20 with a new INN, 42 without an INN, and 124 with an identical twin sold earlier (`launch_composition.md`). The first sale serves as the launch date, so N is a launch-date split in the sense of the task. Because the first sale is only a proxy (and makes the first evaluated month positive by construction), N evaluates first sales observed in the data, not documented launch events.

## 4. Experimental setup

* **Temporal protocol.**
  * Validation: training targets 2020–2021 (origins 2019-12 and 2020-12), evaluation 2022 (origin 2021-12).
  * Test: training targets 2020–2022, evaluation 2023 (origin 2022-12).
  * Training rows are SKUs with at least one sale in the 12 months before their origin. In N, the launch-year rows of SKUs launched in each training year are added.
* **Cross-validation for cold start.** 5 group folds per scenario, balanced by number of SKUs, seed 42. Each held-out product is evaluated exactly once, and test metrics are pooled over folds.
* **CatBoost settings.**
  * Depth 6, learning rate 0.05, L2 3, `max_ctr_complexity` 1, up to 3,000 trees, early stopping after 200 rounds without improvement on the validation year, seed 42, all CPU threads.
  * For log-link losses the model starts from log(mean target), stored as the model bias.
  * `max_ctr_complexity = 1` was chosen in a development timing check on scenario A validation: it gave the same WAPE (0.440) as `max_ctr_complexity = 2` in 29 s instead of 76 s.
* **Number of trees.** Set on the validation year separately for every arm and cross-fitting half. For B–D1, validation runs on the first two folds, and the tree counts of one fold are applied to the others (fold 0 uses fold 1, folds 1–4 use fold 0), so held-out SKUs never tune their own models. The model is then retrained on 2020–2022 with that number of trees for the test.
* **Loss function.**
  * Selected on validation 2022 only, using the INN + ATC arm of A and of the first fold of B, among RMSE, Tweedie (variance power 1.5) and MAE.
  * The rule is the lowest mean WAPE among losses whose forecast keeps the total volume within ±50% in both scenarios.
  * Final selection (`results/tables/loss_selection.csv`): MAE has the lowest mean WAPE (A 0.465, B 0.943), but on B it under-predicts total volume by 67% after 50–60 trees, a near-constant median forecast. RMSE over-predicts B by 54% and has the highest WAPE (A 0.631, B 1.570). Only Tweedie satisfies the rule (A 0.449, B 1.262; bias +15% and +20%). **Tweedie is used for every CatBoost model.**
  * Why the bias condition is needed: WAPE, like MAE, is minimized by the median, which for skewed new-product sales is close to zero. The condition was introduced after an early development run (with the replaced leave-one-out features), in which MAE won on mean WAPE although on B it stopped after 4 trees and under-predicted total volume by 86%.
* **Best baseline.** The same rule (lowest validation WAPE among baselines with |bias| ≤ 50%), applied to the pooled validation predictions (first two folds for B–D1), never to the test year. The saved validation CatBoost predictions come from models early-stopped on those same rows, so CatBoost validation errors are slightly optimistic; they are used only for these choices, and every reported comparison is on the test year.
* **Metrics.**
  * On SKU-months: MAE, RMSE and WAPE = Σ|y − ŷ| / Σy (main metric).
  * Also reported: total bias Σŷ / Σy − 1, WAPE of the SKU totals over the evaluated months (12 months; months since launch in N), and the Spearman rank correlation of those totals (does the model rank new products correctly?).
  * For cold start a zero forecast is shown as a reference. Its WAPE is exactly 1, so an unbiased forecast of very skewed new-product volumes can exceed 1 while still being more useful than predicting nothing.
* **Known ATC depth (scenario C).** For each evaluated SKU, the deepest ATC level that occurs among the donors of both cross-fitted models.
* **Statistical comparison.**
  * For each scenario and arm, a paired cluster bootstrap with 1,000 resamples gives the 95% interval of the WAPE difference to the no-INN/ATC arm and to the best baseline.
  * Resampled clusters: SKUs in A and N, twin clusters in B, INN units in C, ATC2 groups in D, ATC1 groups in D1.
  * With only 14 clusters, the D1 intervals are rough.
  * Volume quintiles in the error analysis are formed from the realized evaluation-year volume. They describe where the errors occur and are not available at forecast time.
* **Software and hardware.** Python 3.12.10; numpy 2.5.4, pandas 2.2.3, catboost 1.2.8, pyarrow 26.0.0, matplotlib 3.11.2. Apple M2 (8 cores), 8 GB RAM, macOS. Exact package versions are in `requirements.txt`; trained models and parameters are in `models/`.

## 5. Results (test year 2023)

All numbers are for the test year 2023, forecast from the December 2022 origin. In the cold-start scenarios the five folds are pooled, so every held-out product is evaluated exactly once. Sources: `results/tables/results_test_*.md` (all metrics), `ablation_inn_atc.md` (bootstrap intervals), `error_breakdowns.csv`, and figures `results/figures/res_*.png`.

### 5.1 Overview

**WAPE** (lower is better; `results_test_wape.md`). Evaluated SKUs: A 10,381; B 8,182 held-out SKUs whose INN is known to both models (7,565 twin clusters); C, D and D1 all 10,381 active SKUs, each held out once (2,211 INN units, 90 ATC2 groups and 14 ATC1 groups respectively); N 617 launches.

| Model | A | B | C | D | D1 | N |
|---|---|---|---|---|---|---|
| Zero forecast (reference) | – | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Naive (last month) | **0.298** | – | – | – | – | – |
| Seasonal naive | 0.397 | – | – | – | – | – |
| Moving average (12) | 0.324 | – | – | – | – | – |
| Global mean | – | 1.325 | 1.387 | 1.383 | 1.380 | 2.620 |
| Form mean | – | 1.303 | 1.351 | 1.346 | 1.337 | 2.501 |
| Hierarchical group mean | – | 1.313 | 1.277 | 1.340 | 1.336 | 2.999 |
| Hierarchical group median | – | 1.001 | 0.994 | 0.967 | 0.967 | 1.474 |
| Launch-age mean | – | – | – | – | – | 1.169 |
| CatBoost, no INN/ATC | 0.339 | 1.119 | 1.211 | 1.220 | 1.251 | 0.960 |
| CatBoost, INN only | 0.314 | 1.068 | 1.198 | 1.198 | 1.272 | **0.927** |
| CatBoost, ATC only | 0.333 | 1.033 | 1.089 | 1.211 | 1.264 | **0.927** |
| CatBoost, INN + ATC | 0.302 | 1.053 | 1.069 | 1.200 | 1.246 | 0.933 |
| CatBoost, INN + ATC + category codes | 0.330 | 1.132 | – | – | – | – |

**CatBoost without vs with INN + ATC on the other metrics** (`results_test_rmse.md`, `results_test_mae.md`, `results_test_bias.md`, `results_test_wape_annual.md`, `results_test_spearman_annual.md`):

| Scenario | MAE | RMSE | Total bias | WAPE of SKU totals | Spearman of SKU totals |
|---|---|---|---|---|---|
| A | 2,280 → 2,027 | 13,020 → 12,359 | −5.8% → −4.7% | 0.288 → 0.257 | 0.957 → 0.961 |
| B | 8,252 → 7,762 | 32,525 → 31,827 | −27.0% → −29.9% | 1.104 → 1.037 | 0.268 → 0.392 |
| C | 8,140 → 7,186 | 29,203 → 29,125 | −13.0% → −34.2% | 1.197 → 1.055 | 0.190 → 0.334 |
| D | 8,198 → 8,065 | 29,276 → 29,255 | −12.4% → −14.8% | 1.206 → 1.185 | 0.161 → 0.216 |
| D1 | 8,404 → 8,376 | 29,455 → 29,423 | −11.6% → −11.1% | 1.236 → 1.232 | 0.096 → 0.122 |
| N | 2,539 → 2,468 | 8,351 → 8,171 | −63.8% → −62.7% | 0.922 → 0.895 | 0.599 → 0.667 |

### 5.2 Effect of INN and ATC (ablation)

Relative WAPE change against CatBoost without INN/ATC, with 95% paired cluster-bootstrap intervals (`ablation_inn_atc.md`, `res_ablation_inn_atc.png`). Negative = better.

| Scenario | INN only | ATC only | INN + ATC | + category codes |
|---|---|---|---|---|
| A existing drug | −7.4% [−11.7, −1.5] | −1.8% [−11.2, +10.8] | −11.1% [−16.3, −5.2] | −2.8% [−10.9, +7.5] |
| B new SKU, known INN | −4.6% [−6.7, −2.7] | **−7.7% [−9.1, −6.4]** | −5.9% [−7.6, −4.4] | +1.1% [−0.7, +3.1] |
| C new INN, known ATC | −1.1% [−1.8, −0.4] | −10.1% [−12.2, −8.2] | **−11.7% [−14.3, −9.1]** | – |
| D unseen ATC2 group | −1.8% [−3.2, −0.5] | −0.8% [−2.4, +0.8] | −1.6% [−3.0, −0.1] | – |
| D1 unseen ATC1 group | +1.7% [+0.8, +2.8] | +1.0% [−0.1, +2.4] | −0.3% [−1.8, +1.1] | – |
| N real launches 2023 | −3.4% [−5.7, −1.1] | −3.5% [−5.7, −1.3] | −2.8% [−5.3, −0.3] | – |

### 5.3 Scenario findings

**C — new INN, known ATC: the clearest gain.** A model that knows nothing pharmaceutical about a new substance reaches WAPE 1.211. Adding ATC peer statistics cuts this to 1.089, and INN + ATC to 1.069 (−11.7%). The rank correlation of SKU totals almost doubles (0.190 → 0.334), MAE drops by 12% (8,140 → 7,186), and the result beats the best baseline (hierarchical group mean, 1.277) by 16%. "INN only" changes little (−1.1%) because, for an unseen INN, the INN block reduces to the number of ingredients. The gain holds at every depth of shared ATC information (`res_c_known_atc_depth.png`): WAPE 1.645 → 1.107 when only ATC1 is shared with training INNs (168 SKUs), and 1.12–1.28 → 0.99–1.08 at ATC2–ATC5. **Trade-off:** total bias moves from −13% to −34%. The pharmaceutical information sharpens how volume is distributed across products, but in total it forecasts less of the volume (`res_aggregate_test_2023.png`).

**B — new SKU of a known INN.** All three INN/ATC arms are significantly better than the arm without them. ATC alone is the best (−7.7%), INN + ATC −5.9%, INN alone −4.6%. The ATC block contains ATC5, which is almost the INN, plus the broader levels, so it already carries the INN information. The rank correlation of SKU totals rises from 0.268 to 0.392 and RMSE falls by 2%. Adding the raw INN/ATC codes as categories removes the gain (+1.1% vs no INN/ATC, 1.132 vs 1.053 for INN + ATC). The codes encourage the model to memorize groups in training, which does not transfer to a new product. The hierarchical median baseline has a lower WAPE (1.001) only because it under-forecasts total volume by 57%, the shrink-to-zero effect of Section 4.

**N — real launches.** CatBoost is the only approach below the zero-forecast WAPE: 0.927–0.960, against 1.169 for the launch-age mean and 1.47–3.00 for the group baselines. INN and ATC add a significant 3% (INN −3.4%, ATC −3.5%, INN + ATC −2.8%), and the rank correlation rises from 0.599 to 0.667. The gain is concentrated where the launch is least like known products. For launches with a new INN (113 SKU-months) WAPE goes from 1.088 to 0.963, and for launches without an INN (299 SKU-months) from 1.450 to 1.078. For launches of an INN already on the market (3,847 SKU-months) the gain is small (0.949 → 0.930). All CatBoost arms under-forecast the total volume of launches by 60–65%: the models are trained mostly on established products and only partly capture the ramp-up (`res_launch_age.png`).

**D and D1 — unseen ATC groups.** When the ATC2 group is new and only ATC1 is known, INN + ATC give −1.6%, at the edge of significance. When even ATC1 is unknown, there is no effect (−0.3%, interval −1.8% … +1.1%), and INN-only is slightly worse (+1.7%). This is the expected boundary: INN and ATC help only through peers, and with no peer group there is nothing to transfer.

**A — existing drugs.** With its own history, CatBoost without INN/ATC reaches WAPE 0.339, which is worse than the naive last-month forecast (0.298). Adding INN + ATC peer statistics brings it to 0.302 (−11.1%). This gain survives every tree count and seed in the robustness study (Section 5.4), but it does not make CatBoost better than the naive baseline: the difference to naive is +1.4%, with interval −4.2% … +7.6%. The WAPE of annual SKU totals is the same (0.257 against 0.256), and the 12-month moving average has the lowest RMSE (9,351 against 12,359). No INN or ATC feature is among the 15 most important features of the fitted model, which is dominated by the last observed value. The arm without INN/ATC is also the least stable across seeds (WAPE 0.35–0.44 at 100 trees, against 0.31–0.32 for INN + ATC). The peer statistics therefore seem to stabilize a model that tends to over-fit the history of the shock years, rather than to add much new signal. For established products with full history, INN and ATC are of secondary importance, and a well-chosen naive forecast is as good as the global model in this annual-planning setting.

### 5.4 Robustness to the number of trees and the random seed

For scenarios A, B, C and N, the test models of every arm were refitted with 1,200 trees and three seeds (42, 7, 2024), and the test WAPE was read at 100–1,200 trees (`robustness_summary.md`, `res_robustness_trees_seeds.png`). Cold-start scenarios use their first fold (index 0) and both cross-fitting halves. D and D1 were not refitted. Mean test WAPE over the seeds:

| Scenario | Arm | 100 | 300 | 500 | 1,000 | 1,200 |
|---|---|---|---|---|---|---|
| A | no INN/ATC | 0.396 | 0.403 | 0.368 | 0.351 | 0.356 |
| A | INN + ATC | 0.315 | 0.304 | 0.307 | 0.320 | 0.324 |
| B (first fold) | no INN/ATC | 1.197 | 1.149 | 1.128 | 1.098 | 1.094 |
| B (first fold) | ATC only | 1.139 | 1.065 | 1.042 | 1.012 | 1.004 |
| B (first fold) | INN + ATC | 1.179 | 1.103 | 1.078 | 1.039 | 1.030 |
| B (first fold) | + category codes | 1.242 | 1.183 | 1.155 | 1.115 | 1.104 |
| C (first fold) | no INN/ATC | 1.228 | 1.167 | 1.144 | 1.133 | 1.130 |
| C (first fold) | INN + ATC | 1.116 | 1.049 | 1.029 | 1.007 | 0.999 |
| N | no INN/ATC | 1.093 | 0.982 | 0.959 | 0.937 | 0.933 |
| N | INN + ATC | 1.088 | 0.960 | 0.939 | 0.924 | 0.922 |

* **The direction of the INN/ATC effect does not depend on the tree count or the seed.** In A, the worst seed of INN + ATC beats the best seed without INN/ATC at every tree count. In B and C the ATC and INN + ATC arms stay below the arm without INN/ATC across the whole range. In N all three INN/ATC arms stay below it at every tree count.
* **INN alone is fold-dependent.** In the first fold of B and C it is slightly worse than no INN/ATC at every tree count (B: 1.108 against 1.094 at 1,200), while pooled over all five folds it is better (Section 5.2). ATC is the robust part of the pharmaceutical information.
* **Category codes hurt at every tree count** in B (1.104 against 1.094 without INN/ATC at 1,200 trees), which supports the decision to pass INN and ATC as peer statistics.
* **Cold-start models are under-fitted at the validation-chosen tree counts.** In B, C and N the test error keeps falling up to 1,200 trees. The 2022 break makes early stopping on the validation year conservative. The main results are therefore slightly pessimistic for the cold-start arms, and the relative INN/ATC effects are similar at 1,200 trees (C, first fold: −11.6% at 1,200 trees; pooled main run: −11.7%).

### 5.5 Error analysis

* **Volume.** Errors are dominated by the largest products. In all cold-start scenarios the top quintile of SKUs (by realized 2023 volume) has WAPE 0.79–0.85. The bottom quintile has relative errors in the hundreds, and the second quintile in the tens: a few packs of actual sales against forecasts of typical peer volumes. INN/ATC help mostly in the small and middle quintiles. In C, quintile 2 goes from 23.3 to 15.6 and quintile 3 from 4.24 to 2.87, while quintile 5 gets slightly worse (0.790 → 0.821). The forecast of a blockbuster cannot be inferred from its peers: in B the five largest held-out SKUs sell 0.56–1.54 million packs a month on average and are forecast at 8–57 thousand (`results/predictions/B_test.parquet`; the largest one is shown in `res_examples_new_sku.png`).
* **Therapeutic groups** (`res_error_by_atc1.png`). For new SKUs (B) and new INNs (C) the errors are highest for antineoplastic and immunomodulating agents (L: WAPE 1.21 and 1.75) and anti-infectives (J: 1.15 and 1.19), and in C also for "various" (V: 1.34). These groups are either small in volume or strongly seasonal. They are lowest for antiparasitics (P: 0.85 and 0.90), and also for genito-urinary products (G: 0.97) in B and systemic hormones (H: 0.95) in C. Among the large groups, cardiovascular (C) and alimentary (A) products sit at 1.02–1.04.
* **Largest INN-level errors** (`inn_errors_*.md`). In B and C the largest absolute errors come from a few mass-market over-the-counter substances: acetylsalicylic acid and its combinations, xylometazoline, sodium chloride, ascorbic acid, metamizole. Their individual SKUs sell far above their peer groups, so they are under-forecast by 38–91%; the one exception is xylometazoline in C, over-forecast by 10%. In N the biggest misses are local-anaesthetic combinations, nimesulide, paracetamol and nasal decongestants (oxymetazoline, xylometazoline).
* **Feature importance** (`res_feature_importance.png`, first fold, first half). In A the own-history features dominate (the last value alone has 51% of the PredictionValuesChange importance), and no INN or ATC feature is among the top 15. In B the top features are the ATC3 and INN × form peer means, followed by strength and pack size. In N the months since launch, pack size and strength lead, followed by ATC5, INN × form and ATC3 peer means. Product presentation (strength, pack, content) is the second pillar of every cold-start model, in line with the Level-2 question of the dataset README.

## 6. Answer to the research question

**INN and ATC improve forecasts of drug sales mainly when a product has no history of its own, and the improvement grows with how much the classification says about the new product.**

1. **Cold start with a known therapeutic group: clear, significant gains.**
   * New INN with a known ATC group: −11.7% WAPE (95% CI −14.3% … −9.1%), −12% MAE. The rank correlation of product volumes rises from 0.19 to 0.33.
   * New SKU of a known INN: −5.9% (CI −7.6% … −4.4%); ATC alone gives −7.7%.
   * Real launches of 2023: −2.8% to −3.5% overall, and −11% for launches of a new INN.
2. **No peer group, no gain.** With an unseen ATC2 group the effect shrinks to −1.6% (borderline), and with an unseen ATC1 group it disappears.
3. **Existing products: secondary role.** With own history, INN and ATC make CatBoost more stable and 11% more accurate, but not better than a naive forecast. Own history dominates.
4. **How the information is supplied matters.** The gains come from peer-group statistics of the INN and ATC levels computed on other products. Raw INN/ATC codes as categorical features do not help a new product (+1.1% in B). The leakage audit showed that a careless implementation of these statistics produces strongly misleading results.
5. **The gain is not uniform.** It sits in small and medium products and in the ranking of products. Blockbusters cannot be predicted from their peers. With pharmaceutical information the total volume of new products is under-forecast more strongly (−30% in B and −34% in C, against −27% and −13% without it).

In absolute terms, cold-start forecasting at SKU level remains hard. Every unbiased forecast of held-out products has a monthly WAPE close to or above 1, the level of a zero forecast. INN and ATC narrow this gap but do not close it. The practical value lies in ranking new products and in the level for small and medium products, not in the precise volume of a single new blockbuster.

## 7. Limitations

1. **Sales are not demand.** The target is packs sold. Zero sales mix no demand and stock-outs, and the 2022 collapse of the market is an external shock that no feature describes. Without stock, price, promotion and tender data, the results describe how well *sales* can be forecast, not patient demand.
2. **Simulated cold start.** In B, C, D and D1 the "new" products are established SKUs with their history hidden. They are selected among SKUs that sold in the year before the origin, and their market position is that of a mature product. Real launches (N) behave differently: they ramp up during the forecast year, and every CatBoost arm under-forecasts them (total bias −60% to −65%).
3. **Launch date is a proxy.** In N the first month with positive sales is taken as the launch month. This makes the first evaluated month positive by construction and cannot separate a true launch from a relisting under a new ID (124 of the 617 launches of 2023 have an older identical twin).
4. **One test year and one origin.** All conclusions rest on the 12 months of 2023 forecast from December 2022. The validation year 2022 contains a structural break, which makes the choice of the number of trees noisy (Section 5.4). A rolling-origin evaluation with several origins would make the estimates more stable.
5. **Skewed target and metric choice.** WAPE, MAE and RMSE answer different questions on such skewed data. WAPE and MAE reward forecasts that shrink toward zero for uncertain products (the zero forecast has WAPE 1, and the hierarchical median almost the same at −57% to −80% bias). RMSE is dominated by a handful of blockbusters. The conclusions are therefore stated with all three metrics, the total bias and the rank correlation, and not with WAPE alone.
6. **Few clusters at the top of the hierarchy.** Scenario D has 90 ATC2 clusters and D1 only 14 ATC1 clusters, so their bootstrap intervals are rough and fold-to-fold variation is large (WAPE spread 1.08–1.62 across D1 folds).
7. **Heuristic text parsing.** Strength and pack size come from a regex. A manual check found 2 errors in 60 descriptions, both packages without a unit dose. Pack size is missing for 11.8% of SKUs.
8. **Anonymized and incomplete product identity.** Brand codes were deliberately not used, and 931 SKUs have no INN. Products of the same molecule from different manufacturers cannot be linked beyond INN, ATC and the description.
9. **Validation predictions are optimistic.** Validation metrics come from models early-stopped on the validation rows themselves. They are used only to choose the loss, the number of trees and the best baseline, never to compare arms.

## 8. What was not done, and why

| Item from the task | Status | Reason / alternative |
|---|---|---|
| Revenue as a target | not applicable | the dataset has no prices or revenue; quantity sold in packs is the only target (as preferred by the task) |
| INN / ATC availability | done | both present; 931 placeholder INNs found and treated as missing (Section 2.1); no external lookup was needed |
| Lag and rolling features for existing products | done, restricted | only lags ≥ 12 months relative to the target and windows ending at the origin are used, because the forecast covers 12 months from a single origin; 1–11-month lags would require sales from inside the horizon |
| Scenario D, unseen ATC group | done at two levels | ATC2 (90 groups) and ATC1 (14 groups); with 14 ATC1 groups the D1 estimate is uncertain |
| Cold start split by real launch dates | done as a proxy | true launch dates are not in the data; the first month with positive sales is used (scenario N) and labelled as a proxy |
| Raw INN / ATC categories in the main models | replaced by peer statistics | for unseen INNs and ATC groups a raw code carries no information at prediction time but is learned in-sample during training; its effect is measured separately in a sensitivity arm (A, B) |
| Rolling-origin backtesting, several test years | not done | the data contain five years; with annual origins only 2022 and 2023 can be evaluated after two training years, and 2022 is used for validation. Proposed as future work |
| Hierarchical reconciliation (SKU → INN → ATC) and graph models | not done | outside the research question; suggested by the dataset README as further tasks |
| Price, stock-out, promotion features | not possible | not in the data |

## 9. Reproducibility and delivered materials

| Material | Location |
|---|---|
| Working code (package, scripts, tests) | `src/teva_forecast/`, `scripts/`, `tests/` (23 tests: leakage, splits, parsing) |
| Notebooks | `notebooks/01_dataset_description_eda.ipynb`, `notebooks/02_experiments_and_results.ipynb` (executed, with outputs) |
| Cleaned and prepared data | `data/processed/teva_sku_attributes.parquet`, `data/processed/teva_sales_panel.parquet` (derived from the MIT-licensed source; the raw CSV is downloaded and checksum-verified by `scripts/prepare_data.py`) |
| Dataset characteristics and data dictionary | `results/tables/dataset_characteristics.md`, `hierarchy_levels.md`, `hierarchy_checks.md`, `data_quality.md`; `reports/data_dictionary.md` |
| EDA and seasonality figures | `results/figures/eda_*.png` |
| Trained models and training parameters | `models/*.cbm` (final test models of A and N, and of the first fold of B–D1, both cross-fitting halves), `models/training_parameters.json`, `results/tables/runs.csv` (each of the 264 models of the main experiment: rows, SKUs, donors, trees, time; the loss-selection fits are in `loss_selection.csv`, the robustness refits in `robustness_trees_seeds.csv`) |
| Comparison of all experiments | `results/tables/results_test_*.md`, `metrics_overall.csv`, `metrics_by_fold.csv`, `ablation_inn_atc.md` |
| Error and forecast figures | `results/figures/res_*.png` |
| Predictions of every model | `results/predictions/{scenario}_{validation,test}.parquet` |
| Robustness to trees and seeds | `results/tables/robustness_trees_seeds.csv`, `robustness_summary.md`, `results/figures/res_robustness_trees_seeds.png` |
| Run log | `results/run_log.txt` |

The full pipeline runs with the commands in the README. On an Apple M2 with 8 GB RAM the experiments (264 CatBoost models plus 9 for the loss selection) took about 40 minutes (`results/run_log.txt`: 23:07–23:44), and the robustness study about 60 minutes (from the end of that run to the last write of `robustness_trees_seeds.csv` at 00:43).

