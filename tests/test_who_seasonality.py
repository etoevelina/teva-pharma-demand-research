"""Checks of the WHO data processing used in the seasonality comparison (run with: pytest -q)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from teva_forecast import who  # noqa: E402


def test_weekly_to_monthly_conserves_totals_and_splits_boundary_weeks():
    weeks = pd.DataFrame({"start": ["2023-01-23", "2023-01-30", "2023-02-06"], "cases": [70.0, 70.0, 70.0]})
    m = who.weekly_to_monthly(weeks, "start", ["cases"])
    assert m["cases"].sum() == pytest.approx(210.0)
    # The week starting Monday 2023-01-30 has 2 days in January and 5 in February.
    assert m.loc["2023-01-01", "cases"] == pytest.approx(70 + 20)
    assert m.loc["2023-02-01", "cases"] == pytest.approx(50 + 70)


def test_iso_week_53_is_allocated():
    weeks = pd.DataFrame({"start": ["2020-12-28"], "cases": [7.0]})   # ISO week 53 of 2020
    m = who.weekly_to_monthly(weeks, "start", ["cases"])
    assert m.loc["2020-12-01", "cases"] == pytest.approx(4.0)
    assert m.loc["2021-01-01", "cases"] == pytest.approx(3.0)


def test_coverage_reflects_reported_days():
    weeks = pd.DataFrame({"start": ["2023-03-06", "2023-03-13"], "cases": [1.0, 1.0]})
    m = who.weekly_to_monthly(weeks, "start", ["cases"])
    assert m.loc["2023-03-01", "coverage"] == pytest.approx(14 / 31)


def _flunet(rows):
    base = {"RSV_PROCESSED": 0, "RSV": 0}
    return pd.DataFrame([{**base, **r} for r in rows])


def test_positivity_is_ratio_of_sums_and_sources_are_added():
    raw = _flunet([
        {"ISO_WEEKSTARTDATE": "2023-01-02", "ORIGIN_SOURCE": "SENTINEL", "SPEC_PROCESSED_NB": 10, "INF_ALL": 5},
        {"ISO_WEEKSTARTDATE": "2023-01-02", "ORIGIN_SOURCE": "NONSENTINEL", "SPEC_PROCESSED_NB": 90, "INF_ALL": 9},
        {"ISO_WEEKSTARTDATE": "2023-01-09", "ORIGIN_SOURCE": "SENTINEL", "SPEC_PROCESSED_NB": 10, "INF_ALL": 5},
        {"ISO_WEEKSTARTDATE": "2023-01-16", "ORIGIN_SOURCE": "SENTINEL", "SPEC_PROCESSED_NB": 100, "INF_ALL": 50},
        {"ISO_WEEKSTARTDATE": "2023-01-23", "ORIGIN_SOURCE": "SENTINEL", "SPEC_PROCESSED_NB": 100, "INF_ALL": 50},
    ])
    m = who.flunet_monthly(raw)
    jan = m.loc["2023-01-01"]
    # Weeks 1-4 lie fully in January; the week of 23 January ends on the 29th.
    assert jan["flu_specimens"] == pytest.approx(310)
    assert jan["flu_positivity"] == pytest.approx(119 / 310)
    weekly_mean = np.mean([14 / 100, 0.5, 0.5, 0.5])
    assert abs(jan["flu_positivity"] - weekly_mean) > 0.02


def test_rsv_detections_without_rsv_specimens_are_dropped():
    raw = _flunet([
        {"ISO_WEEKSTARTDATE": d, "ORIGIN_SOURCE": src, "SPEC_PROCESSED_NB": 10, "INF_ALL": 1,
         "RSV_PROCESSED": tested, "RSV": pos}
        for d in ["2021-02-01", "2021-02-08", "2021-02-15", "2021-02-22"]
        for src, tested, pos in [("SENTINEL", 10, 2), ("NONSENTINEL", 0, 5)]
    ])
    assert who.flunet_monthly(raw).loc["2021-02-01", "rsv_positivity"] == pytest.approx(0.2)


def test_zero_specimens_give_missing_positivity():
    raw = _flunet([{"ISO_WEEKSTARTDATE": d, "ORIGIN_SOURCE": "SENTINEL", "SPEC_PROCESSED_NB": 0, "INF_ALL": 0}
                   for d in ["2023-07-03", "2023-07-10", "2023-07-17", "2023-07-24"]])
    assert np.isnan(who.flunet_monthly(raw).loc["2023-07-01", "flu_positivity"])


def _fluid_row(week, age, ari, pop=1_000_000, ili=1.0, ili_pop=1000.0):
    return {"ISO_WEEKSTARTDATE": week, "AGEGROUP_CODE": age, "ARI_CASE": ari, "ARI_POP_COV": pop,
            "ILI_CASE": ili, "ILI_POP_COV": ili_pop, "SARI_CASE": np.nan, "SARI_INPATIENTS": np.nan}


def test_fluid_prefers_all_ages_row_and_falls_back_to_age_groups():
    rows = [_fluid_row("2023-01-02", "All", 400)]
    rows += [_fluid_row("2023-01-02", a, 100) for a in who.STANDARD_AGE_GROUPS]
    rows += [_fluid_row("2023-01-09", a, 50, pop=250_000) for a in who.STANDARD_AGE_GROUPS]
    weekly = who.fluid_all_ages(pd.DataFrame(rows)).set_index("ISO_WEEKSTARTDATE")
    assert weekly.loc["2023-01-02", "ARI_CASE"] == 400        # all-ages row, no double counting
    assert weekly.loc["2023-01-09", "ARI_CASE"] == 200        # sum of the four age groups
    assert weekly.loc["2023-01-09", "ARI_POP_COV"] == 1_000_000


def test_fluid_zero_all_ages_value_falls_back_to_age_groups():
    rows = [_fluid_row("2023-01-02", "ALL", 0)] + [_fluid_row("2023-01-02", a, 100) for a in who.STANDARD_AGE_GROUPS]
    weekly = who.fluid_all_ages(pd.DataFrame(rows)).set_index("ISO_WEEKSTARTDATE")
    assert weekly.loc["2023-01-02", "ARI_CASE"] == 400
    assert weekly.loc["2023-01-02", "ari_source"] == "sum of age groups"


def test_fluid_zero_ari_is_treated_as_not_reported():
    rows = [_fluid_row("2023-07-03", "ALL", 0)]
    weekly = who.fluid_all_ages(pd.DataFrame(rows)).set_index("ISO_WEEKSTARTDATE")
    assert np.isnan(weekly.loc["2023-07-03", "ARI_CASE"])
    assert weekly.loc["2023-07-03", "ILI_CASE"] == 1.0     # ILI of the same week is kept


def test_ari_rate_per_100k():
    rows = [_fluid_row(d, "ALL", 700, pop=1_000_000) for d in pd.date_range("2023-01-02", periods=4, freq="7D").strftime("%Y-%m-%d")]
    m = who.fluid_monthly(pd.DataFrame(rows))
    # 28 reported days of 31 -> scaled to the full month.
    assert m.loc["2023-01-01", "ari_per_100k"] == pytest.approx(2800 * 31 / 28 / 1_000_000 * 1e5)


def test_lag_alignment():
    idx = pd.date_range("2019-01-01", periods=36, freq="MS")
    epi = pd.Series(np.sin(np.arange(36) / 2.0), index=idx)
    sales = epi.shift(2)
    r = who.correlate(sales, epi, lag=2, n_boot=50)
    assert r["n"] == 34
    assert r["spearman"] == pytest.approx(1.0)


def test_lag_masks_both_the_sales_month_and_the_indicator_month():
    idx = pd.date_range("2019-01-01", periods=60, freq="MS")
    epi = pd.Series(np.arange(60.0), index=idx)
    epi["2021"] = 1e6                       # inside the excluded window; must never be paired
    sales = pd.Series(np.arange(60.0), index=idx).shift(1)
    keep = who.exclude_windows(idx, [("2021-01-01", "2021-12-01")])
    r = who.correlate(sales, epi, lag=1, keep=keep, n_boot=50)
    # Months 1..59 minus sales months in 2021 (24..35) and the month after it (36, indicator in 2021).
    assert r["n"] == 59 - 13
    assert r["spearman"] == pytest.approx(1.0)


def test_anomalies_have_zero_calendar_month_means():
    idx = pd.date_range("2019-01-01", periods=60, freq="MS")
    s = pd.Series(np.exp(np.random.default_rng(0).normal(size=60)) * (2 + np.cos(np.arange(60) / 12 * 2 * np.pi)), index=idx)
    a = who.anomalies(s, log=True)
    assert np.allclose(a.groupby(a.index.month).mean(), 0)


def test_year_permutation_ignores_shared_seasonality():
    idx = pd.date_range("2019-01-01", periods=60, freq="MS")
    season = np.tile(np.cos(np.arange(12) / 12 * 2 * np.pi), 5)
    rng = np.random.default_rng(1)
    x = pd.Series(season + rng.normal(0, 0.1, 60), index=idx)
    y = pd.Series(season + rng.normal(0, 0.1, 60), index=idx)
    p, n = who.year_permutation_p(x, y)
    assert n == 120
    assert p > 0.05           # same seasonal shape only: alignment of years adds nothing
    yearly = np.repeat(rng.normal(0, 1, 5), 12)
    p2, _ = who.year_permutation_p(x + yearly, y + yearly)
    assert p2 <= 0.05         # shared year-to-year variation is detected


def test_year_permutation_with_excluded_months_keeps_all_permutations():
    idx = pd.date_range("2019-01-01", periods=60, freq="MS")
    season = np.tile(np.cos(np.arange(12) / 12 * 2 * np.pi), 5)
    x = pd.Series(season + np.repeat([0.0, 1.0, -1.0, 2.0, -2.0], 12), index=idx)
    keep = who.exclude_windows(idx, [("2020-03-01", "2021-12-01")])
    p, n = who.year_permutation_p(x, x.copy(), keep=keep)
    assert n == 120
    assert p == pytest.approx(1 / 120)     # only the true alignment reproduces rho = 1


def test_autocorrelation_uses_adjacent_calendar_months_only():
    x = np.tile([0.0, 1.0, np.nan, 1.0, 0.0, np.nan], 10)
    assert who.lag1_autocorr(x) == pytest.approx(-1.0)


def test_bootstrap_ci_is_missing_for_short_series():
    lo, hi, _ = who.block_bootstrap_ci(np.arange(20.0), np.arange(20.0))
    assert np.isnan(lo) and np.isnan(hi)


def test_effective_n_is_smaller_for_autocorrelated_series():
    rng = np.random.default_rng(2)
    white = rng.normal(size=200)
    ar = np.convolve(rng.normal(size=220), np.ones(20) / 20, mode="valid")[:200]
    assert who.effective_n(ar, ar) < who.effective_n(white, rng.normal(size=200))


def test_benjamini_hochberg():
    q = who.benjamini_hochberg([0.01, 0.04, 0.03, 0.5])
    assert np.allclose(q, [0.04, 0.16 / 3, 0.16 / 3, 0.5])
