"""Leakage-free feature construction for the annual planning protocol.

Every row is a (SKU, target month t) pair belonging to an evaluation year Y.
The forecast origin is T = December of year Y-1, so the horizon is h = month(t) in 1..12.
All features are computed from information available at T:

* history features use only the SKU's own sales up to T;
* peer-group aggregates are computed from an explicit set of *donor* SKUs. In the cold-start
  scenarios the donors are disjoint from the SKUs the model is trained on (cross-fitting, see
  experiments.py), so within one model a group's statistics are the same for every training SKU of
  the group and never depend on its own sales, exactly as for an unseen product. In scenario A,
  where a SKU's own history is a legitimate input, the SKU's own twin cluster is subtracted
  (exclude_unit) identically for training and evaluation rows;
* the seasonal lag t-12 is always <= T because h <= 12.
"""
import warnings

import numpy as np
import pandas as pd

from . import config

GROUPINGS = {
    "global": [],
    "nfc": ["nfc"],
    "inn": ["inn"],
    "inn_nfc": ["inn", "nfc"],
    "atc1": ["atc1"],
    "atc2": ["atc2"],
    "atc3": ["atc3"],
    "atc4": ["atc4"],
    "atc5": ["atc5"],
}
AGG_STATS = ["mean12", "trend6", "n_selling", "lag12", "seas"]

# `year` is kept in the frame but not used as a model input: trees cannot extrapolate to an unseen year.
CALENDAR = ["month", "quarter", "month_sin", "month_cos"]
PRODUCT_NUM = ["strength_value", "content_value", "n_doses", "pack_count", "multi_strength"]
PRODUCT_CAT = ["nfc", "strength_unit", "content_unit"]
HISTORY = [
    "last1", "mean3", "mean6", "mean12", "std12", "max12", "zero_share12",
    "trend6", "yoy12", "lag12", "lag24", "age_at_origin",
]
INN_CAT = ["inn"]
ATC_CAT = ["atc1", "atc2", "atc3", "atc4", "atc5"]


def agg_columns(grouping):
    return [f"{grouping}_{s}" for s in AGG_STATS]


def origin_index(year):
    """Index of December of year-1 in the 2019-01..2023-12 month axis."""
    return (year - 2019) * 12 - 1


def year_months(year):
    start = (year - 2019) * 12
    return np.arange(start, start + 12)


def active_at_origin(ds, year):
    """SKUs with at least one sale in the 12 months up to the origin of `year`."""
    T = origin_index(year)
    return (ds.sales0[:, max(T - 11, 0):T + 1] > 0).any(axis=1)


def launched_in(ds, year):
    months = year_months(year)
    first_t = ds.attrs["first_t"].to_numpy()
    return (first_t >= months[0]) & (first_t <= months[-1])


def make_rows(ds, sku_mask, year, from_launch=False):
    """Row index for the 12 target months of `year` for the selected SKUs.

    With from_launch=True only months on or after the SKU's first sale are kept
    (used for new launches whose planned launch month is assumed to be known).
    """
    idx = np.flatnonzero(sku_mask)
    months = year_months(year)
    rows = pd.DataFrame({
        "i": np.repeat(idx, 12),
        "t": np.tile(months, len(idx)),
    })
    rows["T"] = origin_index(year)
    if from_launch:
        first_t = ds.attrs["first_t"].to_numpy()[rows["i"]]
        rows = rows[rows["t"] >= first_t].reset_index(drop=True)
    return rows


def _window(matrix, i, end, length):
    """Gather matrix[i, end-length+1 .. end] with NaN for indices before month 0."""
    cols = end[:, None] - np.arange(length - 1, -1, -1)[None, :]
    valid = cols >= 0
    out = matrix[i[:, None], np.clip(cols, 0, None)]
    return np.where(valid, out, np.nan)


def _safe_ratio(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = a / b
    r[~np.isfinite(r)] = np.nan
    return r


def calendar_features(ds, rows):
    dates = ds.dates[rows["t"].to_numpy()]
    out = pd.DataFrame(index=rows.index)
    out["year"] = dates.year
    out["month"] = dates.month
    out["quarter"] = dates.quarter
    out["month_sin"] = np.sin(2 * np.pi * out["month"] / 12)
    out["month_cos"] = np.cos(2 * np.pi * out["month"] / 12)
    return out


def static_features(ds, rows):
    cols = PRODUCT_NUM + PRODUCT_CAT + INN_CAT + ATC_CAT + ["n_ingredients"]
    return ds.attrs.iloc[rows["i"].to_numpy()][cols].reset_index(drop=True).set_index(rows.index)


def history_features(ds, rows):
    """Own-history features of each SKU at the origin (requires the SKU to be on the market at T)."""
    pairs = rows[["i", "T"]].drop_duplicates().reset_index(drop=True)
    i, T = pairs["i"].to_numpy(), pairs["T"].to_numpy()
    W = _window(ds.sales, i, T, 24)                     # NaN before launch / before 2019-01
    last12, prev12 = W[:, 12:], W[:, :12]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        feats = pd.DataFrame({
            "i": i, "T": T,
            "last1": W[:, -1],
            "mean3": np.nanmean(W[:, -3:], axis=1),
            "mean6": np.nanmean(W[:, -6:], axis=1),
            "mean12": np.nanmean(last12, axis=1),
            "std12": np.nanstd(last12, axis=1),
            "max12": np.nanmax(last12, axis=1),
            "zero_share12": np.nanmean(np.where(np.isnan(last12), np.nan, last12 == 0), axis=1),
            "mean_prev12": np.nanmean(prev12, axis=1),
            "mean_prev6": np.nanmean(W[:, -12:-6], axis=1),
        })
    feats["trend6"] = _safe_ratio(feats["mean6"].to_numpy(), feats["mean_prev6"].to_numpy())
    feats["yoy12"] = _safe_ratio(feats["mean12"].to_numpy(), feats["mean_prev12"].to_numpy())
    first_t = ds.attrs["first_t"].to_numpy()[i]
    observed = ds.attrs["launch_observed"].to_numpy()[i] == 1
    feats["age_at_origin"] = np.where(observed, np.minimum(T - first_t + 1, config.AGE_CAP), config.AGE_CAP)
    feats = feats.drop(columns=["mean_prev12", "mean_prev6"])

    out = rows[["i", "T"]].merge(feats, on=["i", "T"], how="left").set_index(rows.index)
    t = rows["t"].to_numpy()
    ri = rows["i"].to_numpy()
    out["lag12"] = ds.sales[ri, t - 12]
    lag24_t = t - 24
    out["lag24"] = np.where(lag24_t >= 0, ds.sales[ri, np.clip(lag24_t, 0, None)], np.nan)
    return out[HISTORY]


def age_at_target(ds, rows):
    """Months since launch at the target month (for planned launches); capped, established = cap."""
    i, t = rows["i"].to_numpy(), rows["t"].to_numpy()
    first_t = ds.attrs["first_t"].to_numpy()[i]
    observed = ds.attrs["launch_observed"].to_numpy()[i] == 1
    age = np.where(observed, np.minimum(t - first_t + 1, config.AGE_CAP), config.AGE_CAP)
    return pd.Series(age, index=rows.index, name="age_at_target")


def group_codes(ds, grouping):
    """Integer group code per SKU; -1 when any key of the grouping is missing (e.g. no INN)."""
    keys = GROUPINGS[grouping]
    n = len(ds.attrs)
    if not keys:
        return np.zeros(n, dtype=int), 1
    frame = ds.attrs[keys]
    valid = frame.notna().all(axis=1).to_numpy()
    codes = np.full(n, -1, dtype=int)
    codes[valid] = frame[valid].groupby(keys, sort=False).ngroup().to_numpy()
    return codes, max(int(codes.max()) + 1, 1)


def group_aggregates(ds, rows, donor_mask, exclude_unit=None, groupings=tuple(GROUPINGS)):
    """Peer-group statistics at the origin, computed from donor SKUs only.

    For group g and month m: S[g, m] = total sales of the donors, N[g, m] = number of donors with
    positive sales; per-SKU averages are S / N ("sales per selling SKU"). With exclude_unit
    (an integer unit code per SKU that is nested in every grouping, i.e. the twin cluster) the
    row's own unit is subtracted from its group.
    """
    Y0 = ds.sales0
    selling = (Y0 > 0).astype(float)
    donors = np.asarray(donor_mask, dtype=bool)
    i, t, T = rows["i"].to_numpy(), rows["t"].to_numpy(), rows["T"].to_numpy()
    if exclude_unit is not None:
        unit = np.asarray(exclude_unit)
        US = np.zeros((unit.max() + 1, Y0.shape[1]))
        UN = np.zeros_like(US)
        np.add.at(US, unit[donors], Y0[donors])
        np.add.at(UN, unit[donors], selling[donors])
        u = unit[i]
    out = {}
    for name in groupings:
        codes, n_groups = group_codes(ds, name)
        use = donors & (codes >= 0)
        S = np.zeros((n_groups, Y0.shape[1]))
        N = np.zeros_like(S)
        np.add.at(S, codes[use], Y0[use])
        np.add.at(N, codes[use], selling[use])
        g = codes[i]
        has_group = g >= 0
        gg = np.where(has_group, g, 0)

        def window_sum(M, end, length, own=None):
            total = np.nansum(_window(M, gg, end, length), axis=1)
            if own is not None:
                total = total - np.nansum(_window(own, u, end, length), axis=1)
            return total

        own_s = US if exclude_unit is not None else None
        own_n = UN if exclude_unit is not None else None
        s12, n12 = window_sum(S, T, 12, own_s), window_sum(N, T, 12, own_n)
        s6, n6 = window_sum(S, T, 6, own_s), window_sum(N, T, 6, own_n)
        sp6, np6 = window_sum(S, T - 6, 6, own_s), window_sum(N, T - 6, 6, own_n)
        s_lag, n_lag, n_origin = S[gg, t - 12], N[gg, t - 12], N[gg, T]
        if exclude_unit is not None:
            s_lag = s_lag - US[u, t - 12]
            n_lag = n_lag - UN[u, t - 12]
            n_origin = n_origin - UN[u, T]
        mean12 = _safe_ratio(s12, n12)
        lag12 = _safe_ratio(s_lag, n_lag)
        cols = {
            "mean12": mean12,
            "trend6": _safe_ratio(_safe_ratio(s6, n6), _safe_ratio(sp6, np6)),
            "n_selling": n_origin.astype(float),
            "lag12": lag12,
            "seas": _safe_ratio(lag12, mean12),
        }
        for stat, values in cols.items():
            out[f"{name}_{stat}"] = np.where(has_group, values, np.nan)
    return pd.DataFrame(out, index=rows.index)


def build_frame(ds, rows, donor_mask, exclude_unit=None, with_history=False, with_launch_age=False):
    """Assemble the full feature frame plus target and identifiers for the given rows."""
    parts = [
        rows[["i", "t"]],
        pd.DataFrame({
            "sku": ds.attrs["sku"].to_numpy()[rows["i"]],
            "date": ds.dates[rows["t"].to_numpy()],
            "sales": ds.sales0[rows["i"].to_numpy(), rows["t"].to_numpy()],
        }, index=rows.index),
        calendar_features(ds, rows),
        static_features(ds, rows),
        group_aggregates(ds, rows, donor_mask, exclude_unit),
    ]
    if with_history:
        parts.append(history_features(ds, rows))
    if with_launch_age:
        parts.append(age_at_target(ds, rows).to_frame())
    return pd.concat(parts, axis=1)
