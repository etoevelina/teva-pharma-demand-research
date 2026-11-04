# Validation-selected rolling protocol and robustness studies

This document describes the evaluation protocol of the INN/ATC study as revised for review:
- the primary configuration is chosen only on the previous year;
- results are reported for two test years;
- variability is measured over CatBoost seeds and fold assignments;
- a shuffled-peer placebo, a calibrated median baseline and a launch scenario without knowledge of the launch month are added.

The original single-split analysis ([report.md](report.md)) is kept unchanged. All numbers of the new protocol are generated from saved predictions and run records by `scripts/analyze_results.py`:
- the generated tables are in `results/tables/`;
- the results summary is generated into [evaluation_protocol_results.md](evaluation_protocol_results.md).

No number in this document or in the generated summary is typed by hand.

## 1. Rolling cycles

A forecast is issued in December of year Y−1 for the 12 months of year Y. For each test year Y, the cycle has two steps:
* **Validation.** CatBoost models are trained on the target years 2020 … Y−2 and early-stopped on year Y−1. All choices are made on Y−1 (Section 2).
* **Test.** The models are retrained on 2020 … Y−1 with the validation tree counts and forecast Y.

| Test year | Validation models: train → evaluate | Test models: train → evaluate |
|---|---|---|
| 2022 | 2020 → 2021 | 2020–2021 → 2022 |
| 2023 | 2020–2021 → 2022 | 2020–2022 → 2023 (the original split) |

**First cycle (test 2022).** Its validation models are trained on a single year, 2020. An earlier training year is not possible without months before the data start. Year 2020 is the first target year whose origin (December 2019) has the 12 months of history that the features use; a 2019 target year would need an origin in December 2018. The test-2022 cycle also selects its own loss function on 2021, with the same rule and candidates as the original study (Tweedie, RMSE, MAE; lowest validation WAPE among losses whose validation total bias stays within ±50%). No 2022 target is used before the 2022 forecasts are made.

Peer statistics, history features and baselines are computed at the origin of each row's year from months up to that origin (features.py). The tests listed in Section 8 perturb sales after the origin and check that nothing changes.

## 2. Choices made on the validation year

`protocol.run_cycle` computes every choice before any test model is trained:

| Choice | Rule | Data used |
|---|---|---|
| Loss function | as in the original study (above) | validation year of the cycle, scenarios A and B fold 0, INN + ATC arm |
| Tree counts | early stopping (200 rounds) of each arm and cross-fitting half | validation year. Test fold 0 uses the counts of validation fold 1, every other fold those of validation fold 0 |
| Primary metadata arm | lowest validation WAPE among `inn`, `atc`, `both`; ties to the earlier one | validation-year CatBoost predictions of folds 0–1 (cold-start scenarios) or of the single unit (A, N, N0). Test fold 0 uses the choice made on validation fold 1, test fold 1 the one made on fold 0, and folds 2–4 the one made on folds 0 and 1 together |
| Median calibration factor | Σ actual / Σ hierarchical median on the validation year | validation-year baselines of all five folds (no model is fit). Test fold k uses the factor of the other four folds. A, N and N0 use their single unit |

**No held-out product tunes its own forecast.** In the cold-start scenarios the validation folds are the same products one year earlier. Every choice for test fold k is therefore made on validation folds other than k (`protocol.choice_folds`), exactly as for the tree counts:
- A held-out product's earlier sales never set the arm, the trees or the calibration of its own forecast.
- In A, the product's own history is an allowed input.
- In N and N0, the validation and test cohorts are different products.

The primary forecast `catboost_selected` uses, for each fold, the arm chosen for that fold. `validation_selected_models.csv` reports the arm chosen on all validation folds together (which applies to folds 2–4) and the choice for every fold.

The control arm (`none`, no INN/ATC information) is always reported. The primary comparison of each scenario and test year is the **validation-selected metadata arm against the control**. The other arms, including `both_codes` (raw codes as categories in A and B), are exploratory. `validation_selected_models.csv` also lists the arm that would have been best on the test year (`test_best_arm_exploratory`), only to show how often validation and test agree. It is never used for a conclusion.

`validation_metrics` and `calibration_factor` read the year of the rows they receive and refuse anything other than the validation year; `select_metadata_arm` only accepts those validation metrics. The tests check the following:
- With a fake trainer whose validation and test winners differ, the cycle picks the validation winner before any test fit.
- The arm and calibration of a test fold come from the other validation folds.
- Changing the test targets, or the validation-year sales of a fold's own products, leaves its calibrated forecasts unchanged.
- The loss is chosen on the validation year.

## 3. Calibrated hierarchical median

`calibrated_median = factor × hierarchical_median`. The factor is the validation-year ratio of the actual to the forecast total of the hierarchical median of the same scenario:
- for test 2022 it comes from 2021;
- for test 2023 it comes from 2022.

In B, C, D and D1, test fold k uses the ratio over the other four folds (Section 2).

The hierarchical median is the original baseline: the median t−12 sales of the selling pool SKUs in the most specific peer group with at least three selling SKUs (INN × form → INN → ATC5 … ATC1 → form → global). In scenario A it is computed the same way from the whole pool. It can then include the product's own sales of month t−12, which is legitimate because the product's own history is known in A.

`calibrated_baselines.csv` compares, on the test year:
- the CatBoost control;
- the validation-selected CatBoost arm;
- the hierarchical median and the calibrated median;
- the zero forecast;
- in A, the naive (last month), seasonal naive and MA(12) forecasts;
- in N, the launch-age mean;
- in N0, the launch-cohort mean.

## 4. CatBoost-seed robustness

The whole 2023 cycle is repeated with CatBoost seeds 42 (the rolling run), 7, 2024, 11 and 99. The data, folds, cross-fitting halves and loss are the same in every run. Each run repeats:
- validation with early stopping under its own seed;
- the arm selection;
- the test fits.

The study covers all scenarios A, B, C, D, D1, N and N0 and the four main arms. For every scenario and arm, `model_seed_robustness_summary.csv` reports:
- mean, standard deviation, minimum and maximum WAPE;
- mean bias and mean Spearman correlation;
- the WAPE difference to the control of the same run;
- the number of runs in which the arm beats the control.

The row `validation_selected` uses, in each run, the arm selected on that run's own validation year, and `selections` counts how often each arm was chosen.

## 5. Fold-assignment robustness

The primary grouped folds place groups from the largest to the smallest on the least-loaded fold, with the seed breaking ties only. For ATC1 (14 groups) the folds are identical for every seed, and for ATC2 only 2–15% of the SKUs move. The study therefore uses `assign_folds(method="random_order")`: the groups are taken in a seeded random order and placed on the least-loaded fold.

The 2023 cycle is repeated for fold seeds 42, 7, 2024, 11 and 99, with CatBoost seed 42, in the cold-start scenarios B (twin cluster), C (INN), D (ATC2) and D1 (ATC1). A and N/N0 have no folds. The assignment keeps the grouping of every scenario: a twin cluster, INN, ATC2 or ATC1 group is entirely in one fold. In D and D1 the INNs of the held-out group are also removed from the training pool. Peer statistics come only from donor SKUs of the training pool, never from a held-out SKU.

`fold_seed_robustness_summary.csv` has the same columns as the CatBoost-seed summary, plus the WAPE of the primary assignment as a reference. The model-seed and fold-seed studies change one source of randomness each, so their spreads can be compared directly.

## 6. Shuffled-peer placebo

**Question.** Do the true INN and ATC peer statistics help more than features of exactly the same form that do not belong to the product?

**What is permuted.** For each INN or ATC grouping (INN, INN × form, ATC1–ATC5), each model and each forecast origin T:
- A group is *active* at T if at least one of the model's donor SKUs sold in the 12 months up to T.
- `features.placebo_permutation` draws one random cyclic order of all groups per placebo seed and grouping, and maps every active group to the next active group in that order. This is a single cycle, so no active group keeps its own statistics unless it is the only active one.
- Inactive groups map to themselves.

Every row then reads the peer statistics of the group π_T(g) instead of its own group g. The permutation applies identically to the training and evaluation rows of a model with the same origin, so the model sees a consistent but wrong taxonomy.

**What is kept:**
- The statistics are the real donor statistics of some group, with the same time windows (all ending at T).
- The control features (global and dosage-form statistics, presentation, calendar, history) and the number of ingredients are unchanged.
- A row has statistics in the shuffled arm exactly when its group is active at T, so the group-level missingness at the origin is preserved.
- In A, N and N0 the own twin cluster is subtracted only where the permutation leaves the group in place, because elsewhere the product is not a member of the group it reads. A row whose own group is active only through its own twin cluster therefore has missing true statistics but shuffled ones.

Each run records, per grouping and for training and evaluation rows, the missing rates of the true and shuffled statistics and how often they agree (`placebo_diagnostics` in the run record; rows `feature check` in `shuffled_peer_placebo.csv`).

**Why it cannot leak:**
- Targets are never permuted.
- The permutation depends only on the seed, the grouping and which groups are active at the origin, never on sales values or anything after T.
- The statistics are computed from the same donor SKUs and the same months as the true features.
- Held-out SKUs are still never donors.

The tests check reproducibility by seed, the single-cycle bijection of the active groups, the preserved missingness, unchanged control features, invariance to sales after the origin and to non-donor sales, and correct own-unit handling.

**Where it applies.** In D1 no INN or ATC group of a training or held-out product has donors: the halves are split by ATC1, and the INNs of the targets are removed from the donors. The INN/ATC peer statistics are therefore missing in every row, the shuffled arm would be identical to the true arm, and D1 is left out of the placebo. In D only the ATC1 statistics exist, so only they are shuffled. In D1 the INN and INN + ATC arms differ from the control only by the number of ingredients and by the feature layout.

**Design.** Five permutation seeds (1–5), test 2023, CatBoost seed 42, the primary folds; scenarios A, B, C, D, N and N0.
- Two configurations are shuffled: the INN + ATC arm (`both`, pre-specified) and the validation-selected arm of the rolling run, with the same per-fold arm choice.
- The shuffled arms get their own validation early stopping, like every other arm.
- They are compared with the control and the true arms of the rolling run on exactly the same rows.

Results: `shuffled_peer_placebo.csv` (per seed) and `shuffled_peer_placebo_summary.csv`.

## 7. Launch scenarios N and N0

**N** (unchanged) is kept as a **retrospective exploratory cohort**. It contains the SKUs whose first positive sale falls in the test year, evaluated from their first sale month. It uses `age_at_target`, the months since that first sale. The launch month is not known at the forecast origin, so N describes the value of knowing it.

**N0** uses the same retrospective cohort, but at the origin:
- every month of the test year is forecast, so months before the launch count with actual sales 0;
- neither the launch month nor `launch_age` is used;
- the only lifecycle feature is `on_market_at_origin`, whether the SKU sold in the 12 months before the origin. It is known at the origin and is 0 for every evaluated SKU;
- training uses the products on the market at each training origin, plus all 12 months of the launch year of the products launched in each training year (past cohorts, fully observed at the origin);
- baselines are the hierarchical median, its calibrated version, the zero forecast and the **launch-cohort mean**. The launch-cohort mean is the average sales of past launch cohorts by calendar month of their launch year, and does not use the product's launch month.

The cohort is still selected by an outcome, a first sale in the test year, so N0 is not a prospective launch experiment. It removes the launch-month information from the forecast, not from the cohort definition. `scenario_n_vs_n0.csv` compares N and N0 on the same cohort and also scores the N0 forecasts on N's months (from launch), which isolates the effect of knowing the launch month.

## 8. Remaining limitations of the protocol

* The grouped folds and the cross-fitting halves are drawn once over the whole SKU catalogue of the dataset, including products that first sell after the origin. The assignment uses no sales values, but which products exist later affects how folds are balanced; this keeps the 2023 cycle identical to the original split.
* The arm selection uses two validation folds (40% of the products) in the cold-start scenarios, and a single unit in A, N and N0.
* The robustness studies use test year 2023 only.
* The 2022 cycle trains its validation models on a single year.
* N0's cohort is still defined by a first sale in the test year (Section 7).

## 9. Tests

`pytest -q` runs the original leakage tests (`tests/test_pipeline.py`), the WHO module tests and `tests/test_protocol.py`. The new tests cover:
- no group leakage for every fold seed and scenario;
- donors disjoint from test and training SKUs;
- reproducible and seed-dependent folds;
- selection that sees validation metrics only and happens before any test fit;
- choices of a test fold made on other folds;
- rejection of test-year rows by the validation guards;
- loss selection on the validation year;
- calibration that is invariant to test targets and to the fold's own validation-year sales;
- stored runs reused only when their fingerprint matches;
- tree counts taken from another fold;
- fold predictions combined exactly once per row;
- placebo reproducibility, the group-level bijection and its temporal and donor invariance;
- N0 invariance to the launch month;
- N's retrospective rows;
- unchanged metric definitions;
- a short end-to-end cycle on the small sample.

## 10. Outputs and run records

| Path | Content |
|---|---|
| `results/protocol/<stage>/<run_id>_{validation,test}.parquet` | predictions of every run (stages `rolling`, `model_seeds`, `fold_seeds`, `placebo`) |
| `results/protocol/<stage>/<run_id>.json` | run record: start and end time, run time, git commit and dirty flag, source hash, Python, platform and package versions, CatBoost parameters as used (with the run's seed), loss, model / fold / permutation seeds, fold method, validation and test years, arms, selected arm (pooled and per fold), calibration factors per fold, validation metrics, tree counts, every fit (iterations, rows, seconds, placebo feature checks), loss-selection table, and a fingerprint. A stored run is reused only if the fingerprint matches |
| `results/protocol/loss_selection_test{2022,2023}.csv` | loss selection of each cycle |
| `results/protocol/run_log.txt` | timestamped log of all runs |
| `results/tables/validation_selected_models.csv` | scenario, selection year, test year, selected arm, validation and test WAPE, bias, Spearman, control, relative change with 95% cluster-bootstrap CI |
| `results/tables/rolling_year_results.csv` | every model, split and year of the rolling runs |
| `results/tables/calibrated_baselines.csv` | baselines, calibrated median and CatBoost (test years) |
| `results/tables/model_seed_robustness{,_summary}.csv` | one row per run and arm; summary per scenario and arm |
| `results/tables/fold_seed_robustness{,_summary}.csv` | the same for fold seeds |
| `results/tables/shuffled_peer_placebo{,_summary}.csv` | placebo per seed; summary |
| `results/tables/scenario_n_vs_n0.csv` | N versus N0 |
| `results/tables/variability_summary.csv` | mean / std / min / max over model seeds, fold seeds and placebo seeds |
| `results/tables/paper_results_table.{csv,md}` | WAPE, bias and Spearman for the paper |
| `results/figures/res_wape_variability.png`, `res_placebo_true_vs_shuffled.png`, `res_selected_vs_calibrated_median.png` | figures |
| `results/regression/` | snapshot of the committed single-split metrics and file checksums taken before the changes, and the comparison with the rebuilt 2023 cycle |

Metrics keep the original definitions:
- WAPE, MAE, RMSE and total bias over the evaluated SKU-months;
- SKU-level annual WAPE;
- the Spearman correlation of the SKU-level totals over the evaluated months.

Bootstrap intervals resample the scenario's grouping unit (SKU, twin cluster, INN, ATC2 or ATC1).
