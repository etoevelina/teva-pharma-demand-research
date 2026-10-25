"""CatBoost feature sets for the INN/ATC ablation and thin training/prediction wrappers."""
import numpy as np
from catboost import CatBoostRegressor, Pool

from . import config
from .features import (
    ATC_CAT, CALENDAR, HISTORY, INN_CAT, PRODUCT_CAT, PRODUCT_NUM, agg_columns,
)

ARMS = ["none", "inn", "atc", "both"]
# Sensitivity arm: INN + ATC peer statistics plus the raw INN and ATC codes as CatBoost categories.
CODES_ARM = "both_codes"
ARM_LABELS = {"none": "no INN/ATC", "inn": "INN only", "atc": "ATC only", "both": "INN + ATC",
              CODES_ARM: "INN + ATC + category codes"}


def feature_columns(arm, history=False, launch_age=False):
    """Categorical and numeric columns for an ablation arm.

    Control features shared by every arm: calendar, parsed product presentation (form, strength,
    content, doses, pack size) and global / dosage-form peer aggregates.
    INN block: number of ingredients and the INN and INN x form peer aggregates.
    ATC block: the peer aggregates of ATC levels 1-5.
    INN and ATC enter the main arms only through peer statistics computed from donor products.
    Raw codes are not used there: for an unseen INN or ATC group the code carries nothing at
    prediction time, while in training CatBoost's target statistics for it are in-sample.
    The sensitivity arm adds the codes as categories to measure what they contribute beyond that.
    """
    cat = list(PRODUCT_CAT)
    num = CALENDAR + PRODUCT_NUM + agg_columns("global") + agg_columns("nfc")
    if history:
        num = num + HISTORY
    if launch_age:
        num = num + ["age_at_target"]
    if arm in ("inn", "both", CODES_ARM):
        num = num + ["n_ingredients"] + agg_columns("inn") + agg_columns("inn_nfc")
    if arm in ("atc", "both", CODES_ARM):
        num = num + [c for level in range(1, 6) for c in agg_columns(f"atc{level}")]
    if arm == CODES_ARM:
        cat = cat + INN_CAT + ATC_CAT
    return cat, num


def make_pool(frame, cat, num, with_label=True, offset=None):
    X = frame[cat + num].copy()
    for c in cat:
        X[c] = X[c].fillna("MISSING").astype(str)
    label = frame["sales"].to_numpy() if with_label else None
    baseline = np.full(len(frame), offset) if offset is not None else None
    return Pool(X, label=label, cat_features=cat, baseline=baseline)


def _log_link(loss):
    return loss.startswith(("Tweedie", "Poisson"))


def _prediction_type(loss):
    return "Exponent" if _log_link(loss) else "RawFormulaVal"


def fit(train, cat, num, loss, eval_frame=None, iterations=None, seed=None):
    """Fit CatBoost; with eval_frame use early stopping, otherwise train a fixed number of trees.

    Log-link losses (Tweedie) start from log(mean training target) instead of 0, so the trees model
    deviations from the average level rather than spending the first iterations on the scale.
    The offset is stored in the model as its bias, so saved models predict on their own.
    """
    params = dict(config.CATBOOST_PARAMS, loss_function=loss)
    if iterations is not None:
        params["iterations"] = int(iterations)
    if seed is not None:
        params["random_seed"] = int(seed)
    model = CatBoostRegressor(**params)
    offset = float(np.log(max(train["sales"].mean(), 1e-9))) if _log_link(loss) else None
    train_pool = make_pool(train, cat, num, offset=offset)
    if eval_frame is not None:
        model.fit(train_pool, eval_set=make_pool(eval_frame, cat, num, offset=offset),
                  early_stopping_rounds=config.EARLY_STOPPING_ROUNDS, use_best_model=True)
    else:
        model.fit(train_pool)
    if offset is not None:
        scale, bias = model.get_scale_and_bias()
        model.set_scale_and_bias(scale, bias + offset)
    return model


def predict(model, frame, cat, num, ntree_end=0):
    loss = model.get_params()["loss_function"]
    pred = model.predict(make_pool(frame, cat, num, with_label=False), prediction_type=_prediction_type(loss),
                         ntree_end=ntree_end)
    return np.clip(pred, 0, None)


def best_iterations(model):
    best = model.get_best_iteration()
    return int(best) + 1 if best is not None else int(model.tree_count_)
