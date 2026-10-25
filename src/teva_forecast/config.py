"""Project-wide constants: paths, data source, temporal protocol and model settings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
MODELS_DIR = ROOT / "models"

SOURCE_REPO = "https://github.com/Marchev-Science/case-forecasting-pharmacutical-demand"
RAW_BASE_URL = "https://raw.githubusercontent.com/Marchev-Science/case-forecasting-pharmacutical-demand/main/data"
RAW_FILES = {
    "full": ("teva_sales.csv", "1bd2852a9a0fb410ec5ac864dc0b3d7ced0b5dfebe756868a72b2bfe2117af23"),
    "small": ("teva_sales_small.csv", "aa88d78417225c15dbb9f8d3592fa2c4c5d1b98cc536be178d53c2fa8f845ac2"),
}

FIRST_MONTH = "2019-01-01"
N_MONTHS = 60

# Annual planning protocol: a forecast is issued at the end of December
# for the 12 months of the following year (horizon h = calendar month).
VALIDATION = {"train_years": [2020, 2021], "eval_year": 2022}
TEST = {"train_years": [2020, 2021, 2022], "eval_year": 2023}

SEED = 42
N_FOLDS = 5
BOOTSTRAP_SAMPLES = 1000

# Age (months on market) is capped: SKUs already selling in 2019-01 are left-censored
# and treated as established products.
AGE_CAP = 24

CATBOOST_PARAMS = {
    "iterations": 3000,
    "learning_rate": 0.05,
    "depth": 6,
    "l2_leaf_reg": 3.0,
    "max_ctr_complexity": 1,
    "random_seed": SEED,
    "thread_count": -1,
    "allow_writing_files": False,
    "verbose": False,
}
EARLY_STOPPING_ROUNDS = 200
LOSS_CANDIDATES = ["RMSE", "Tweedie:variance_power=1.5", "MAE"]
# A loss is eligible only if its validation forecast keeps the total volume within +-50%:
# WAPE alone rewards near-constant median forecasts that under-predict new products by ~90%.
MAX_ABS_VALIDATION_BIAS = 0.5
