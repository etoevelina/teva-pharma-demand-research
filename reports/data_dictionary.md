# Data Dictionary

Source: `teva_sales.csv` from [Marchev-Science / case-forecasting-pharmacutical-demand](https://github.com/Marchev-Science/case-forecasting-pharmacutical-demand) (MIT license), SHA-256 `1bd2852a…af23`. The sampled file `teva_sales_small.csv` (20 INNs, 1,730 SKUs) is an exact subset of the full file (identical IDs and values, checked in `results/tables/source_files_check.md`) and is used by the unit tests and the prototype notebook.

## 1. Raw fields

| Raw column | Name in code | Type | Description | Checked facts |
|---|---|---|---|---|
| `Morion ID` | `sku` | integer | Product (SKU) identifier: one row per ID | 13,762 unique, no duplicates, no missing values |
| `ATC Code (1)` | `atc1` | categorical | ATC level 1, anatomical main group, e.g. `N NERVOUS SYSTEM` | 14 groups; ATC is a strict tree (no ATC2–ATC5 code has more than one parent) |
| `ATC Code (2)` | `atc2` | categorical | ATC level 2, therapeutic subgroup, e.g. `N05 PSYCHOLEPTICS` | 90 groups |
| `ATC Code (3)` | `atc3` | categorical | ATC level 3, therapeutic or pharmacological subgroup | 224 groups |
| `ATC Code (4)` | `atc4` | categorical | ATC level 4, chemical, therapeutic or pharmacological subgroup | 586 groups; 14 SKUs carry the placeholder `-` (treated as missing) |
| `ATC Code (5)` | `atc5` | categorical | ATC level 5, chemical substance, e.g. `N05A H03 Olanzapine` | 1,563 groups; 595 SKUs carry a level-4 code here (no substance-level code); 1,525 SKUs carry non-standard local codes marked `**` |
| `Brand` | `brand` | integer code | Anonymized brand code | 4,895 codes; not used as a model feature (see Methodology) |
| `INN` | `inn` | categorical | International Nonproprietary Name: the active substance or a `+`-joined combination, e.g. `COFFEINUM*+PARACETAMOLUM` | 1,776 INNs; 514 INNs have a single SKU; 931 SKUs carry the placeholder `-` preceded by a non-breaking space (no INN), treated as missing |
| `NFC (1)` | `nfc` | categorical | New Form Code level 1: dosage form or presentation, e.g. `Oral Solid Ordinary` | 16 forms |
| `Description` | `description` | free text | Presentation text with strength, container, package content and pack size, e.g. `tabs coated w/film 20 mg blister, #30` | 8,449 distinct strings after whitespace cleaning (non-breaking spaces replaced, ends trimmed); 17 SKUs (12 distinct strings) use Cyrillic units |
| `2019 01` … `2023 12` | `sales` (long format) | float ≥ 0 | **Quantity sold, number of packs**, per SKU and month (60 columns) | no missing or negative values; 99.6% of positive values are non-integer, so these are probably projected or estimated volumes rather than raw counts |

No revenue, price, stock, stock-out, promotion or tender fields exist in the dataset. **The target is therefore quantity sold in packs, not revenue and not patient demand.**

## 2. Derived SKU-level fields (`data/processed/teva_sku_attributes.parquet`)

| Field | Definition |
|---|---|
| `first_t`, `first_sale` | Index (0 = 2019-01) and date of the first month with positive sales. Treated as the launch date (proxy) |
| `last_t`, `last_sale` | Index and date of the last month with positive sales |
| `launch_observed` | 1 if the first sale is after 2019-01, i.e. the launch falls inside the observation window; 0 = left-censored, already on the market in 2019-01 |
| `twin_cluster`, `twin_size` | Cluster of SKUs with identical ATC5, brand, INN, form and description (different Morion IDs). 1,981 SKUs sit in 814 such clusters. Twins are kept together in every simulated cold-start split; in N an older twin of a launch is in the training data but excluded from the launch's peer statistics |
| `inn_missing` | 1 if the raw INN is the placeholder (no INN) |
| `inn_unit` | Grouping unit of the "new INN" split: the INN, or the twin cluster for SKUs without an INN |
| `n_ingredients` | Number of `+`-separated components of the INN (missing without an INN) |
| `strength_value`, `strength_unit` | First strength found before the container word (Cyrillic units mapped to Latin first). Mass converted to mg; units `mg`, `mg/ml`, `mg/g`, `mg/dose`, `mg/h`, `%`, `IU`, `IU/ml`, `IU/g`, `IU/dose`; `none` if absent (22.7% of SKUs) |
| `multi_strength` | 1 if more than one strength is listed (fixed-dose combinations) |
| `content_value`, `content_unit` | Package content in ml or g (e.g. `flask 100 ml`) |
| `n_doses` | Number of doses for metered products (`200 doses`) |
| `pack_count` | Number of units in the pack, from the last `#N` token (missing for 11.8% of SKUs) |

Parsing is a heuristic regex. A random sample of 60 descriptions (seed 7) was checked by hand (verdicts in `reports/description_parsing_audit.csv`): 58 were parsed correctly in every field. Both errors read the mass of a herbal or granulate package (`gran. case 10 g`, `collect. fruit 40 g pack`) as strength.

## 3. Sales panel (`data/processed/teva_sales_panel.parquet`)

| Field | Definition |
|---|---|
| `sku` | Morion ID |
| `date` | First day of the month, 2019-01-01 … 2023-12-01 |
| `t` | Month index 0 … 59 |
| `sales` | Packs sold (0 before the first sale) |
| `on_market` | `False` for months before the first sale. These structural zeros mean "not yet launched" and are excluded from training targets, history features and peer-group counts |

## 4. Model features (computed at the forecast origin T = December of the previous year)

| Block | Features | Used in |
|---|---|---|
| Calendar | `month`, `quarter`, `month_sin`, `month_cos` (`year` is computed but not a model input) | all models |
| Product presentation | `nfc`, `strength_value`, `strength_unit`, `content_value`, `content_unit`, `n_doses`, `pack_count`, `multi_strength` | all models |
| Global and form peers | `global_*`, `nfc_*` aggregates (see below) | all models |
| Own history | `last1`, `mean3`, `mean6`, `mean12`, `std12`, `max12`, `zero_share12`, `trend6` (mean of last 6 / previous 6 months), `yoy12` (last 12 / previous 12), `lag12` and `lag24` (same month 1 and 2 years before the target), `age_at_origin` (months on the market at T, counting the first-sale month as 1, capped at 24; 24 for SKUs already selling in 2019-01) | scenario A only |
| Launch age | `age_at_target` (months on the market at the target month, the launch month being 1, capped at 24) | real-launch scenario N only |
| **INN block** | `n_ingredients`, `inn_*` and `inn_nfc_*` aggregates | arms "INN only", "INN + ATC" |
| **ATC block** | `atc1_*` … `atc5_*` aggregates | arms "ATC only", "INN + ATC" |
| Category codes | `inn`, `atc1` … `atc5` as CatBoost categories | sensitivity arm "INN + ATC + category codes" (scenarios A and B) |

Peer aggregates for a grouping `G` are computed from a set of *donor* SKUs. In the cold-start scenarios (B, C, D, D1) and in N, the training pool is split into two halves (by twin cluster, INN unit, ATC2 or ATC1); a model trained on one half takes its peer statistics only from the other half, and its forecasts for evaluated SKUs use the same donors. The forecasts of the two models are averaged. In scenario A all SKUs are donors and each SKU's own twin cluster is subtracted from its group. SKUs without a group code (no INN, missing ATC4) get missing values for that grouping. See report, Section 3.4.

| Suffix | Definition |
|---|---|
| `G_mean12` | Average sales per selling SKU-month in the group over the 12 months up to T |
| `G_trend6` | Per-SKU average of the last 6 months divided by that of the previous 6 months |
| `G_n_selling` | Number of donor SKUs of the group with positive sales in month T |
| `G_lag12` | Average sales per selling SKU of the group in the same calendar month one year before the target month |
| `G_seas` | `G_lag12 / G_mean12`, a seasonal index of the target month |
