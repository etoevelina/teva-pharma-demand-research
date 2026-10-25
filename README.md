# Teva Pharma Demand Research

Research notebook on forecasting monthly pharmaceutical sales at the SKU level, built on the public Teva Pharmaceutical sales dataset. It is a reproducible prototype for diploma research on pharmaceutical demand forecasting.

## What the notebook covers

- Loads `teva_sales_small.csv` (20 INNs, 1,730 SKUs, monthly sales 2019-01 — 2023-12) and validates its schema.
- Reshapes the data into an SKU × month panel and runs EDA: SKUs per INN, ATC structure, zero sales, seasonality.
- Extracts strength and pack size from the free-text `Description` field and checks pack comparability.
- Compares three forecasting approaches on a time-based split (**2019–2021 train, 2022 validation, 2023 test**):
  - Seasonal Naive (value from 12 months earlier);
  - ETS (Holt–Winters, one model per SKU);
  - a global CatBoost model using only leakage-free features (`lag12`, `lag24`, calendar and product attributes).
- Runs a mock cold-start experiment: 20% of SKUs per INN are fully held out from training and forecast from product attributes and peer sales only.

## Results (small dataset)

| Model | WAPE, validation 2022 | WAPE, test 2023 |
|---|---|---|
| Seasonal Naive | 59.5% | 42.2% |
| ETS | 61.1% | **40.0%** |
| CatBoost | 60.1% | 43.7% |

Mock cold-start on 347 held-out SKUs (test 2023): INN-month median baseline — 98.9% WAPE, cold-start CatBoost — 150.2% WAPE.

The notebook ends with a list of limitations and next steps. The most important one: the target is **quantity sold in packs**, not true patient demand, and zero sales can mean either no demand or no stock.

## How to run

**Google Colab:** open the notebook and choose **Runtime → Run all**. Missing dependencies are installed automatically.

**Locally:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook teva_pharma_demand_research_colab.ipynb
```

The data are downloaded from GitHub at run time. To use a local copy of the CSV, set `TEVA_DATA_PATH=/path/to/teva_sales_small.csv`. To run on the full dataset, set `DATASET = "full"` in the first code cell (the ETS step takes noticeably longer).

## Data source

[Marchev-Science / case-forecasting-pharmacutical-demand](https://github.com/Marchev-Science/case-forecasting-pharmacutical-demand), file `data/teva_sales_small.csv`, MIT license.
