"""Comparison of pharmaceutical sales seasonality with WHO influenza / respiratory surveillance.

This module is independent of the forecasting experiments: it reads the processed sales panel and
WHO surveillance data (FluNet and FluID, downloaded from the WHO FluMart OData API) and never
touches models, predictions or result tables of the main study.

Conventions
-----------
* Weekly WHO data are ISO weeks (Monday-Sunday). They are converted to calendar months by day
  allocation: every week contributes 1/7 of each count to each of its seven days, and the days are
  summed by month. A week crossing a month boundary is therefore split proportionally.
* Influenza positivity of a month is sum(positives) / sum(specimens tested) over the allocated
  days, never the mean of weekly percentages.
* Incidence rates (ARI, ILI) are cases per 100,000 population covered per month: allocated cases
  divided by the day-weighted mean population covered, scaled to the full month when some days
  are not reported. Months with less than MIN_COVERAGE of their days reported are set to missing.
"""
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from . import config

FLUMART = "https://xmart-api-public.who.int/FLUMART"
WHO_VIEWS = {
    "flunet": "VIW_FNT",        # virological surveillance (FluNet)
    "fluid": "VIW_FID_EPI",     # epidemiological surveillance (FluID): ILI, ARI, SARI
    "metadata": "VIW_FLU_METADATA",
}
WHO_PORTALS = {
    "flunet": "https://www.who.int/tools/flunet",
    "fluid": "https://www.who.int/teams/global-influenza-programme/surveillance-and-monitoring/influenza-surveillance-outputs",
}
WHO_RAW_DIR = config.RAW_DIR / "who"
PERIOD = ("2019-01-01", "2023-12-01")
MIN_COVERAGE = 0.75
STANDARD_AGE_GROUPS = ["0TO4", "5TO14", "15TO64", "65TO"]

# Pre-specified sensitivity windows (inclusive month ranges).
ANOMALY_WINDOWS = {
    "covid_npi": ("2020-03-01", "2021-12-01"),   # pandemic restrictions; influenza almost absent
    "war_onset": ("2022-02-01", "2022-12-01"),   # full-scale invasion; market and surveillance disruption
}


# --- Download with provenance ----------------------------------------------------------

def flumart_url(view, country=None):
    query = {"$format": "csv"}
    if country:
        query["$filter"] = f"COUNTRY_CODE eq '{country}'"
    return f"{FLUMART}/{view}?" + urllib.parse.urlencode(query, quote_via=urllib.parse.quote)


def download_who(country, out_dir=WHO_RAW_DIR):
    """Download FluNet, FluID and field metadata; return a provenance record per file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, view in WHO_VIEWS.items():
        url = flumart_url(view, None if name == "metadata" else country)
        path = out_dir / f"{name}_{country if name != 'metadata' else 'all'}.csv"
        urllib.request.urlretrieve(url, path)
        raw = path.read_bytes()
        records.append({
            "file": path.name, "source": "WHO FluMart OData API", "view": view, "url": url,
            "portal": WHO_PORTALS.get(name, FLUMART),
            "accessed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sha256": hashlib.sha256(raw).hexdigest(), "rows": raw.count(b"\n") - 1,
        })
    (out_dir / "provenance.json").write_text(json.dumps(records, indent=2))
    return records


# --- Weekly to monthly -----------------------------------------------------------------

def allocate_days(weekly, start_col, value_cols):
    """Spread each weekly value evenly over the seven days of its ISO week."""
    w = weekly[[start_col] + value_cols].copy()
    w[start_col] = pd.to_datetime(w[start_col])
    days = w.loc[w.index.repeat(7)].copy()
    days["day"] = days[start_col] + pd.to_timedelta(np.tile(np.arange(7), len(w)), unit="D")
    days[value_cols] = days[value_cols] / 7.0
    return days


def weekly_to_monthly(weekly, start_col, sum_cols, mean_cols=()):
    """Monthly sums of day-allocated counts, day-weighted means of level columns and coverage."""
    mean_cols = list(mean_cols)
    days = allocate_days(weekly, start_col, list(sum_cols) + mean_cols)
    for c in mean_cols:
        days[c] = days[c] * 7.0  # levels (e.g. population covered) are not divided over days
    days["month"] = days["day"].dt.to_period("M").dt.to_timestamp()
    agg = {c: "sum" for c in sum_cols}
    agg.update({c: "mean" for c in mean_cols})
    monthly = days.groupby("month").agg(agg)
    reported = days.groupby("month")["day"].nunique()
    monthly["coverage"] = reported / monthly.index.days_in_month
    return monthly


# --- FluNet ------------------------------------------------------------------------------

def flunet_weekly(raw):
    """One row per ISO week: specimens, influenza positives and RSV, summed over surveillance sources.

    Detections reported in a row whose processed count is missing, zero or smaller than the
    detections are dropped, so that every positive in a sum has its specimen in the denominator.
    """
    cols = ["SPEC_PROCESSED_NB", "INF_ALL", "RSV_PROCESSED", "RSV"]
    df = raw.copy()
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for pos, tested in (("INF_ALL", "SPEC_PROCESSED_NB"), ("RSV", "RSV_PROCESSED")):
        df[pos] = df[pos].where(df[tested].gt(0) & (df[pos] <= df[tested]))
    weekly = df.groupby("ISO_WEEKSTARTDATE", as_index=False)[cols].sum(min_count=1)
    by_source = df.pivot_table(index="ISO_WEEKSTARTDATE", columns="ORIGIN_SOURCE",
                               values="SPEC_PROCESSED_NB", aggfunc="sum")
    by_source.columns = [f"spec_{c.lower()}" for c in by_source.columns]
    return weekly.merge(by_source.reset_index(), on="ISO_WEEKSTARTDATE", how="left")


def flunet_monthly(raw, source=None):
    """Monthly influenza positivity (ratio of sums) and RSV positivity; source restricts to one site type."""
    df = raw if source is None else raw[raw["ORIGIN_SOURCE"] == source]
    weekly = flunet_weekly(df)
    m = weekly_to_monthly(weekly, "ISO_WEEKSTARTDATE", ["SPEC_PROCESSED_NB", "INF_ALL", "RSV_PROCESSED", "RSV"])
    m["flu_positivity"] = np.where(m["SPEC_PROCESSED_NB"] > 0, m["INF_ALL"] / m["SPEC_PROCESSED_NB"], np.nan)
    m["rsv_positivity"] = np.where(m["RSV_PROCESSED"] > 0, m["RSV"] / m["RSV_PROCESSED"], np.nan)
    m.loc[m["coverage"] < MIN_COVERAGE, ["flu_positivity", "rsv_positivity"]] = np.nan
    return m.rename(columns={"SPEC_PROCESSED_NB": "flu_specimens", "INF_ALL": "flu_positives",
                             "RSV_PROCESSED": "rsv_specimens", "RSV": "rsv_positives"})


# --- FluID -------------------------------------------------------------------------------

FLUID_COLS = ["ILI_CASE", "ILI_POP_COV", "ARI_CASE", "ARI_POP_COV", "SARI_CASE", "SARI_INPATIENTS"]


def fluid_all_ages(raw):
    """All-ages weekly FluID values, built column by column.

    FluID labels the all-ages row inconsistently ('ALL' or 'All'). For each week and column the
    all-ages value is used when present; otherwise the four standard age groups are summed if all
    four are reported; otherwise the value is missing. Ukraine reports ARI only during the influenza
    season and fills weeks 21-39 with zeros: weekly ARI counts of 0 (in a population of ~38 million)
    are treated as not reported. Population covered of 0 is likewise treated as missing.
    """
    df = raw.copy()
    for c in FLUID_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["age"] = df["AGEGROUP_CODE"].astype(str).str.upper()
    total = df[df["age"] == "ALL"].groupby("ISO_WEEKSTARTDATE")[FLUID_COLS].max()
    parts = df[df["age"].isin(STANDARD_AGE_GROUPS)]
    complete = parts.groupby("ISO_WEEKSTARTDATE")["age"].nunique() == len(STANDARD_AGE_GROUPS)
    summed = parts.groupby("ISO_WEEKSTARTDATE")[FLUID_COLS].sum(min_count=len(STANDARD_AGE_GROUPS))
    summed = summed[complete.reindex(summed.index, fill_value=False)]
    # Zeros are treated as not reported before choosing between the all-ages row and the age groups,
    # so a zero all-ages value falls back to the age-group sum.
    for c in ["ARI_CASE", "ARI_POP_COV", "ILI_POP_COV"]:
        total[c] = total[c].where(total[c] > 0)
        summed[c] = summed[c].where(summed[c] > 0)
    weeks = sorted(set(df["ISO_WEEKSTARTDATE"]))
    out = total.reindex(weeks).combine_first(summed.reindex(weeks))
    out["ari_source"] = np.where(total.reindex(weeks)["ARI_CASE"].notna(), "all-ages row",
                                 np.where(out["ARI_CASE"].notna(), "sum of age groups", "missing"))
    return out.rename_axis("ISO_WEEKSTARTDATE").reset_index()


def _monthly_rate(weekly, case_col, pop_col):
    w = weekly[weekly[case_col].notna() & weekly[pop_col].notna()]
    m = weekly_to_monthly(w, "ISO_WEEKSTARTDATE", [case_col], mean_cols=[pop_col])
    rate = m[case_col] / m["coverage"] / m[pop_col] * 1e5
    return rate.where(m["coverage"] >= MIN_COVERAGE), m["coverage"], m[pop_col]


def fluid_monthly(raw):
    """Monthly ARI and ILI incidence per 100,000 and SARI cases per 100 inpatients, with coverage."""
    weekly = fluid_all_ages(raw)
    ari, ari_cov, ari_pop = _monthly_rate(weekly, "ARI_CASE", "ARI_POP_COV")
    ili, ili_cov, ili_pop = _monthly_rate(weekly, "ILI_CASE", "ILI_POP_COV")
    w = weekly[weekly["SARI_CASE"].notna() & weekly["SARI_INPATIENTS"].gt(0)]
    sm = weekly_to_monthly(w, "ISO_WEEKSTARTDATE", ["SARI_CASE", "SARI_INPATIENTS"])
    sari = (sm["SARI_CASE"] / sm["SARI_INPATIENTS"] * 100).where(sm["coverage"] >= MIN_COVERAGE)
    return pd.DataFrame({
        "ari_per_100k": ari, "ari_coverage": ari_cov, "ARI_POP_COV": ari_pop,
        "ili_per_100k": ili, "ili_coverage": ili_cov, "ILI_POP_COV": ili_pop,
        "sari_per_100_inpatients": sari,
    })


# --- Sales groups ------------------------------------------------------------------------

def sales_by_group(ds, groups):
    """Monthly packs per group; `groups` maps a name to (ATC column, tuple of code prefixes)."""
    out = {}
    for name, (col, prefixes) in groups.items():
        codes = ds.attrs[col].fillna("")
        mask = codes.str.startswith(tuple(prefixes)).to_numpy()
        out[name] = ds.sales0[mask].sum(axis=0)
    return pd.DataFrame(out, index=pd.DatetimeIndex(ds.dates, name="month"))


# --- Seasonality and anomalies -------------------------------------------------------------

def seasonal_index(series):
    """Within-year index: value / mean of its calendar year, averaged by calendar month.

    Same definition as eda.seasonal_index, applied here to one series with missing months.
    """
    s = series.dropna()
    ratio = s / s.groupby(s.index.year).transform("mean")
    return ratio.groupby(ratio.index.month).mean()


def seasonal_index_by_year(series):
    s = series.dropna()
    ratio = s / s.groupby(s.index.year).transform("mean")
    return ratio.groupby([ratio.index.year, ratio.index.month]).mean().unstack()


def anomalies(series, log=True):
    """Deviation from the calendar-month mean (log scale for multiplicative series)."""
    s = np.log(series.where(series > 0)) if log else series.astype(float)
    return s - s.groupby(s.index.month).transform("mean")


# --- Correlation under autocorrelation ----------------------------------------------------
#
# All functions below work on monthly arrays laid out on the calendar (complete calendar years,
# NaN for months without a value), so that "adjacent" always means adjacent calendar months.

def lag1_autocorr(x):
    """Lag-1 autocorrelation from pairs of adjacent calendar months that both have a value."""
    x = np.asarray(x, float)
    d = x - np.nanmean(x)
    pairs = np.isfinite(d[1:]) & np.isfinite(d[:-1])
    valid = np.isfinite(d)
    if pairs.sum() < 3 or np.sum(d[valid] ** 2) == 0:
        return np.nan
    return float(np.mean(d[1:][pairs] * d[:-1][pairs]) / np.mean(d[valid] ** 2))


def effective_n(x, y):
    """Bretherton et al. (1999) effective sample size from lag-1 autocorrelations (NaN = missing month)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    n = int(ok.sum())
    rx, ry = lag1_autocorr(np.where(ok, x, np.nan)), lag1_autocorr(np.where(ok, y, np.nan))
    if not (np.isfinite(rx) and np.isfinite(ry)):
        return np.nan
    return float(np.clip(n * (1 - rx * ry) / (1 + rx * ry), 3, n))


def t_test_p(r, n_eff):
    from scipy import stats
    if not np.isfinite(n_eff):
        return np.nan
    df = n_eff - 2
    t = r * np.sqrt(df / max(1e-12, 1 - r * r))
    return float(2 * stats.t.sf(abs(t), df))


def _spearman(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 8:
        return np.nan
    ra, rb = rankdata(a[ok]), rankdata(b[ok])
    if ra.std() == 0 or rb.std() == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def _month_demean(a, n_years):
    """Subtract the calendar-month mean over the available values (array of complete calendar years)."""
    m = a.reshape(n_years, 12)
    counts = np.isfinite(m).sum(axis=0)
    means = np.where(counts > 0, np.nansum(m, axis=0) / np.maximum(counts, 1), np.nan)
    return (m - means).ravel()


def _shift(a, lag):
    out = np.full_like(a, np.nan)
    if lag == 0:
        out[:] = a
    elif lag > 0:
        out[lag:] = a[:-lag]
    else:
        out[:lag] = a[-lag:]
    return out


def block_bootstrap_ci(x, y, block=12, n_boot=2000, seed=config.SEED, method="spearman", min_pairs=8):
    """95% CI of the correlation from a moving-block bootstrap of calendar months.

    x and y are on the calendar (NaN = no pair). Blocks are 12 consecutive calendar months, so gaps
    are resampled with their neighbours. Resamples with fewer than `min_pairs` pairs are skipped;
    returns (lo, hi, share of valid resamples), with NaN bounds when fewer than 80% are valid.
    """
    rng = np.random.default_rng(seed)
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 2 * block:
        return np.nan, np.nan, 0.0
    starts = np.arange(n - block + 1)
    vals = []
    for _ in range(n_boot):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.choice(starts, int(np.ceil(n / block)))])[:n]
        a, b = x[idx], y[idx]
        ok = np.isfinite(a) & np.isfinite(b)
        if ok.sum() < min_pairs:
            continue
        a, b = a[ok], b[ok]
        if method == "spearman":
            a, b = rankdata(a), rankdata(b)
        if np.std(a) > 0 and np.std(b) > 0:
            vals.append(np.corrcoef(a, b)[0, 1])
    share = len(vals) / n_boot
    if share < 0.8:
        return np.nan, np.nan, share
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975)), share


def year_permutation_p(x, y, lag=0, keep=None, anomaly=False):
    """Exact permutation p-value of the Spearman correlation, permuting whole calendar years of y.

    x (sales, month t) and y (indicator, month t - lag) cover the same complete calendar years.
    Each permutation moves every year of y to another year with its months kept in place; the
    excluded months (`keep` False, applied to t for x and to t - lag for y) and the lag stay at fixed
    calendar positions and are applied after permuting, as are calendar-month means when
    `anomaly` is True. The within-year seasonal shape of both series is preserved and only their
    year-to-year alignment is broken, so any shared year-level variation, epidemic or not, counts
    against the null. Returns the share of the k! permutations (identity included) with |rho| at
    least the observed one, and the number of permutations with a defined correlation.
    """
    from itertools import permutations
    xa, ya = np.asarray(x, float), np.asarray(y, float)
    n_years = len(xa) // 12
    assert len(xa) == len(ya) == n_years * 12, "series must cover complete calendar years"
    keep = np.ones(len(xa), bool) if keep is None else np.asarray(keep, bool)
    xk = np.where(keep, xa, np.nan)
    if anomaly:
        xk = _month_demean(xk, n_years)

    def stat(yv):
        yk = np.where(keep, yv, np.nan)
        if anomaly:
            yk = _month_demean(yk, n_years)
        return _spearman(xk, _shift(yk, lag))

    years = ya.reshape(n_years, 12)
    observed = stat(ya)
    null = np.array([stat(years[list(perm)].ravel()) for perm in permutations(range(n_years))])
    null = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(null) == 0:
        return np.nan, 0
    return float(np.mean(np.abs(null) >= abs(observed) - 1e-12)), int(len(null))


def correlate(x, y, lag=0, keep=None, anomaly=False, n_boot=2000):
    """Correlation of sales x in month t with indicator y in month t - lag on the kept months.

    x and y are monthly pd.Series on the same index of complete calendar years, already on the
    analysis scale (log where needed). A month enters only if it is kept at t (for x) and at t - lag
    (for y). With `anomaly`, both series are first expressed as deviations from their calendar-month
    means computed over the kept months.
    """
    n_years = len(x) // 12
    keep = np.ones(len(x), bool) if keep is None else np.asarray(keep, bool)
    xk = np.where(keep, x.to_numpy(float), np.nan)
    yk = np.where(keep, y.to_numpy(float), np.nan)
    if anomaly:
        xk, yk = _month_demean(xk, n_years), _month_demean(yk, n_years)
    yl = _shift(yk, lag)
    ok = np.isfinite(xk) & np.isfinite(yl)
    n = int(ok.sum())
    if n < 8:
        return {"n": n}
    xp, yp = np.where(ok, xk, np.nan), np.where(ok, yl, np.nan)
    rx, ry = np.full(len(x), np.nan), np.full(len(x), np.nan)
    rx[ok], ry[ok] = rankdata(xp[ok]), rankdata(yp[ok])
    rho = float(np.corrcoef(rx[ok], ry[ok])[0, 1])
    n_eff = effective_n(rx, ry)
    lo, hi, boot_valid = block_bootstrap_ci(xp, yp, n_boot=n_boot)
    p_perm, n_perm = year_permutation_p(x, y, lag=lag, keep=keep, anomaly=anomaly)
    return {"n": n, "n_eff": round(n_eff, 1) if np.isfinite(n_eff) else np.nan,
            "pearson": float(np.corrcoef(xp[ok], yp[ok])[0, 1]), "spearman": rho,
            "spearman_ci_lo": lo, "spearman_ci_hi": hi, "bootstrap_valid_share": boot_valid,
            "p_spearman_neff": t_test_p(rho, n_eff), "p_year_permutation": p_perm, "n_permutations": n_perm}


def exclude_windows(index, windows):
    keep = np.ones(len(index), dtype=bool)
    for start, end in windows:
        keep &= ~((index >= pd.Timestamp(start)) & (index <= pd.Timestamp(end)))
    return keep


def benjamini_hochberg(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / (np.arange(len(p)) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.minimum(q, 1.0)
    return out


def indicator_availability(indicators):
    """Months with a value per indicator and year (2019-2023)."""
    avail = indicators.notna().groupby(indicators.index.year).sum().T
    avail.columns = [str(c) for c in avail.columns]
    avail["total"] = avail.sum(axis=1)
    return avail.reset_index(names="indicator")


def atc1_seasonality_stability(ds):
    """Year-by-year seasonal indices of the ATC1 groups and how stable the winter-summer contrast is."""
    rows = []
    for g, idx in ds.attrs.groupby("atc1").indices.items():
        s = pd.Series(ds.sales0[idx].sum(axis=0), index=pd.DatetimeIndex(ds.dates))
        by_year = seasonal_index_by_year(s)
        winter = by_year[[12, 1, 2]].mean(axis=1)
        summer = by_year[[6, 7, 8]].mean(axis=1)
        contrast = winter / summer
        rows.append({
            "atc1": g, "peak_month_mean_profile": int(seasonal_index(s).idxmax()),
            "peak_months_by_year": " ".join(str(int(m)) for m in by_year.idxmax(axis=1)),
            "winter_summer_ratio_mean": float(contrast.mean()), "winter_summer_ratio_min": float(contrast.min()),
            "winter_summer_ratio_max": float(contrast.max()), "years_winter_above_summer": int((contrast > 1).sum()),
            "max_abs_index_dev_mean": float((seasonal_index(s) - 1).abs().max()),
        })
    return pd.DataFrame(rows).sort_values("winter_summer_ratio_mean", ascending=False)
