"""Leakage and consistency checks for the feature pipeline (run with: pytest -q)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from teva_forecast import data, experiments as E, features as F  # noqa: E402


@pytest.fixture(scope="module")
def ds():
    return data.load_processed("teva_small")


def _perturbed(ds, rows_mask=None, months=None):
    sales = ds.sales.copy()
    sel = np.ones(len(ds.attrs), bool) if rows_mask is None else rows_mask
    cols = slice(None) if months is None else months
    block = sales[sel][:, cols]
    sales[np.ix_(np.flatnonzero(sel), np.arange(sales.shape[1])[cols])] = np.where(np.isnan(block), np.nan, block * 7 + 13)
    return data.Dataset(attrs=ds.attrs, sales=sales, dates=ds.dates)


def test_history_features_ignore_sales_after_origin(ds):
    rows = F.make_rows(ds, F.active_at_origin(ds, 2023), 2023)
    before = F.history_features(ds, rows)
    after = F.history_features(_perturbed(ds, months=slice(48, 60)), rows)
    pd.testing.assert_frame_equal(before, after)


def test_group_aggregates_ignore_sales_after_origin(ds):
    rows = F.make_rows(ds, F.active_at_origin(ds, 2023), 2023)
    donors = np.ones(len(ds.attrs), bool)
    unit = ds.attrs["twin_cluster"].to_numpy()
    before = F.group_aggregates(ds, rows, donors, unit)
    after = F.group_aggregates(_perturbed(ds, months=slice(48, 60)), rows, donors, unit)
    pd.testing.assert_frame_equal(before, after)


def test_cold_start_features_ignore_held_out_sales(ds):
    folds = E.assign_folds(ds.attrs["twin_cluster"].to_numpy())
    test, pool = E.cold_start_masks(ds, "B", folds, 0)
    rows = F.make_rows(ds, test & F.active_at_origin(ds, 2023), 2023)
    before = F.build_frame(ds, rows, pool)
    after = F.build_frame(_perturbed(ds, rows_mask=~pool), rows, pool)
    cols = [c for c in before.columns if c != "sales"]
    pd.testing.assert_frame_equal(before[cols], after[cols])


@pytest.mark.parametrize("scenario", ["B", "C", "D", "D1", "N"])
def test_cross_fit_training_features_ignore_own_sales(ds, scenario):
    """Within a cross-fitted model, the peer statistics of training SKUs never use their own sales."""
    if scenario == "N":
        pool = np.ones(len(ds.attrs), bool)
    else:
        folds = E.assign_folds(ds.attrs[E.COLD_START_FOLD_LABEL[scenario]].to_numpy())
        _, pool = E.cold_start_masks(ds, scenario, folds, 0)
    for targets, donors in E.donor_halves(ds, scenario, pool):
        assert not (targets & donors).any()
        rows = E.training_rows(ds, targets, [2020, 2021, 2022], include_launches=scenario == "N")
        before = F.group_aggregates(ds, rows, donors)
        after = F.group_aggregates(_perturbed(ds, rows_mask=targets), rows, donors)
        pd.testing.assert_frame_equal(before, after)
        if scenario in ("C", "D", "D1"):
            assert set(ds.attrs.loc[targets, "inn"].dropna()).isdisjoint(ds.attrs.loc[donors, "inn"].dropna())


def test_training_and_evaluation_rows_share_peer_statistics(ds):
    """Training and evaluated SKUs of the same group, origin and month get identical peer statistics."""
    folds = E.assign_folds(ds.attrs["twin_cluster"].to_numpy())
    test, pool = E.cold_start_masks(ds, "B", folds, 0)
    targets, donors = E.donor_halves(ds, "B", pool)[0]
    tr = F.build_frame(ds, F.make_rows(ds, targets & F.active_at_origin(ds, 2023), 2023), donors)
    ev = F.build_frame(ds, F.make_rows(ds, test & F.active_at_origin(ds, 2023), 2023), donors)
    both = pd.concat([tr.assign(role="train"), ev.assign(role="eval")])
    for grouping, keys in F.GROUPINGS.items():
        cols = F.agg_columns(grouping)
        spread = both.groupby(keys + ["t"], dropna=True)[cols].nunique(dropna=False)
        assert (spread.max() <= 1).all(), grouping


def test_b_halves_put_each_multi_cluster_inn_in_both_halves(ds):
    folds = E.assign_folds(ds.attrs["twin_cluster"].to_numpy())
    _, pool = E.cold_start_masks(ds, "B", folds, 0)
    (t0, d0), (t1, d1) = E.donor_halves(ds, "B", pool)
    a = ds.attrs[pool]
    multi = a.groupby("inn")["twin_cluster"].nunique()
    multi = set(multi[multi >= 2].index)
    assert multi <= set(ds.attrs.loc[d0, "inn"]) and multi <= set(ds.attrs.loc[d1, "inn"])


def test_n_launch_features_ignore_own_older_twin(ds):
    pool = np.ones(len(ds.attrs), bool)
    a = ds.attrs
    launches = F.launched_in(ds, 2023)
    twins = a["twin_cluster"].to_numpy()
    candidates = (a["first_t"].to_numpy() < 48) & pd.Series(twins).isin(twins[launches]).to_numpy() & ~launches
    if not candidates.any():
        pytest.skip("no launch with an older twin in the sample")
    cluster = twins[np.flatnonzero(candidates)[0]]
    older = candidates & (twins == cluster)
    rows = F.make_rows(ds, launches & (twins == cluster), 2023, from_launch=True)
    for _, donors in E.donor_halves(ds, "N", pool):
        before = F.group_aggregates(ds, rows, donors, twins)
        after = F.group_aggregates(_perturbed(ds, rows_mask=older), rows, donors, twins)
        pd.testing.assert_frame_equal(before, after)


def test_scenario_a_excludes_own_twin_cluster(ds):
    donors = np.ones(len(ds.attrs), bool)
    unit = ds.attrs["twin_cluster"].to_numpy()
    target = unit == unit[ds.attrs["twin_size"].to_numpy().argmax()]
    rows = F.make_rows(ds, target, 2023)
    before = F.group_aggregates(ds, rows, donors, unit)
    after = F.group_aggregates(_perturbed(ds, rows_mask=target), rows, donors, unit)
    pd.testing.assert_frame_equal(before, after)


def test_placeholder_codes_become_missing():
    attrs = pd.DataFrame({"atc1": ["A x"], "atc2": ["A01 x"], "atc3": ["A01A x"], "atc4": ["\xa0-"],
                          "atc5": ["A01A A01 x"], "inn": ["\xa0-"], "nfc": ["Oral"], "description": [" tabs, #10"]})
    clean = data.clean_attributes(attrs)
    assert clean["inn"].isna().all() and clean["atc4"].isna().all()
    assert clean["description"].iloc[0] == "tabs, #10"


@pytest.mark.parametrize("scenario", ["B", "C", "D", "D1"])
def test_cold_start_splits_are_disjoint(ds, scenario):
    folds = E.assign_folds(ds.attrs[E.COLD_START_FOLD_LABEL[scenario]].to_numpy())
    for k in range(folds.max() + 1):
        test, pool = E.cold_start_masks(ds, scenario, folds, k)
        a = ds.attrs
        assert not (test & pool).any()
        assert set(a.loc[test, "twin_cluster"]).isdisjoint(a.loc[pool, "twin_cluster"])
        if scenario == "B":
            known = E.known_inn(ds, pool, 2023)
            assert set(a.loc[test & known, "inn"]) <= set(a.loc[pool, "inn"])
        if scenario in ("C", "D", "D1"):
            assert set(a.loc[test, "inn"].dropna()).isdisjoint(a.loc[pool, "inn"].dropna())
        if scenario == "D":
            assert set(a.loc[test, "atc2"]).isdisjoint(a.loc[pool, "atc2"])
        if scenario == "D1":
            assert set(a.loc[test, "atc1"]).isdisjoint(a.loc[pool, "atc1"])


@pytest.mark.parametrize("text,expected", [
    ("tabs coated w/film 20 mg blister, #30", {"strength_value": 20.0, "strength_unit": "mg", "pack_count": 30.0}),
    ("sol.  for inj. 50 mg/2 ml amp. 2 ml, #10", {"strength_value": 25.0, "strength_unit": "mg/ml",
                                                 "content_value": 2.0, "pack_count": 10.0}),
    ("ointment tube 30 g", {"strength_unit": "none", "content_value": 30.0, "content_unit": "g"}),
    ("tablets sublingual 0,0005 g cont., #40", {"strength_value": 0.5, "strength_unit": "mg"}),
    ("tabs 5 mg + 25 mg blister, #30", {"strength_value": 5.0, "multi_strength": 1}),
    (" sol.  for inj. 1600 мг/13,4 мл flask, #1", {"strength_unit": "mg/ml", "pack_count": 1.0}),
])
def test_parse_description(text, expected):
    parsed = data.parse_description(text)
    for key, value in expected.items():
        assert parsed[key] == pytest.approx(value) if isinstance(value, float) else parsed[key] == value
