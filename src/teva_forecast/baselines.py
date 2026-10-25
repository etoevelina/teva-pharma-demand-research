"""Reference forecasts: naive models for existing SKUs, peer-group means for cold start."""
import numpy as np
import pandas as pd

from . import config
from .features import age_at_target, group_codes

HIERARCHY = ["inn_nfc", "inn", "atc5", "atc4", "atc3", "atc2", "atc1", "nfc", "global"]
MIN_PEERS = 3


def existing_drug_baselines(frame):
    """Naive (last observed month), seasonal naive (t-12, falls back to the 12-month mean), MA(12)."""
    return pd.DataFrame({
        "naive": frame["last1"],
        "seasonal_naive": frame["lag12"].fillna(frame["mean12"]),
        "moving_average_12": frame["mean12"],
    }, index=frame.index).fillna(0.0)


def _group_lag12_median(ds, rows, pool_mask, grouping):
    """Median sales per selling pool SKU of the row's group in month t-12."""
    codes, _ = group_codes(ds, grouping)
    pool_idx = np.flatnonzero(np.asarray(pool_mask) & (codes >= 0))
    months = np.unique(rows["t"].to_numpy() - 12)
    vals = ds.sales0[np.ix_(pool_idx, months)]
    long = pd.DataFrame({
        "g": np.repeat(codes[pool_idx], len(months)),
        "k": np.tile(months, len(pool_idx)),
        "v": vals.ravel(),
    })
    med = long[long["v"] > 0].groupby(["g", "k"])["v"].median()
    key = pd.MultiIndex.from_arrays([codes[rows["i"].to_numpy()], rows["t"].to_numpy() - 12])
    return med.reindex(key).to_numpy()


def cold_start_baselines(ds, frame, pool_mask):
    """Peer-group baselines that never use the target SKU's own sales.

    global_mean     - average sales per selling SKU, same month last year, all pool SKUs
    form_mean       - the same within the dosage form (NFC), falling back to global
    hierarchical_*  - most specific peer group with at least MIN_PEERS selling SKUs at the origin:
                      INN x form -> INN -> ATC5 -> ATC4 -> ATC3 -> ATC2 -> ATC1 -> form -> global
    """
    level = pd.Series(pd.NA, index=frame.index, dtype="object")
    mean = pd.Series(np.nan, index=frame.index)
    for g in HIERARCHY:
        ok = level.isna() & frame[f"{g}_lag12"].notna() & (frame[f"{g}_n_selling"] >= MIN_PEERS)
        level[ok] = g
        mean[ok] = frame.loc[ok, f"{g}_lag12"]
    median = pd.Series(np.nan, index=frame.index)
    rows = frame[["i", "t"]]
    for g in HIERARCHY:
        sel = (level == g).to_numpy()
        if sel.any():
            median[sel] = _group_lag12_median(ds, rows[sel], pool_mask, g)
    out = pd.DataFrame({
        "global_mean": frame["global_lag12"],
        "form_mean": frame["nfc_lag12"].fillna(frame["global_lag12"]),
        "hierarchical_mean": mean,
        "hierarchical_median": median.fillna(mean),
    }, index=frame.index).fillna(0.0)
    out["baseline_level"] = level.fillna("none")
    return out


def launch_age_baseline(ds, train_rows, eval_rows):
    """Average sales of past launches (training years) at the same number of months since launch."""
    age = age_at_target(ds, train_rows).to_numpy()
    sales = ds.sales0[train_rows["i"].to_numpy(), train_rows["t"].to_numpy()]
    launch = age < config.AGE_CAP
    curve = pd.Series(sales[launch]).groupby(age[launch]).mean()
    target_age = age_at_target(ds, eval_rows)
    fallback = curve.iloc[-1] if len(curve) else 0.0
    return target_age.map(curve).fillna(fallback).to_numpy()
