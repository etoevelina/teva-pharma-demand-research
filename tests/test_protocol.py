"""Checks of the rolling, validation-selected protocol and its robustness studies (run with: pytest -q)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from teva_forecast import analysis as AN, baselines as B, config, data, experiments as E  # noqa: E402
from teva_forecast import features as F, metrics, modeling as M, protocol as PR  # noqa: E402

UNIT_COLUMNS = {"B": ["twin_cluster"], "C": ["twin_cluster", "inn"], "D": ["twin_cluster", "inn", "atc2"],
                "D1": ["twin_cluster", "inn", "atc1"]}


@pytest.fixture(scope="module")
def ds():
    return data.load_processed("teva_small")


def _perturbed(ds, rows_mask=None, months=None):
    sales = ds.sales.copy()
    sel = np.ones(len(ds.attrs), bool) if rows_mask is None else rows_mask
    cols = np.arange(sales.shape[1]) if months is None else np.arange(sales.shape[1])[months]
    block = sales[np.ix_(np.flatnonzero(sel), cols)]
    sales[np.ix_(np.flatnonzero(sel), cols)] = np.where(np.isnan(block), np.nan, block * 7 + 13)
    return data.Dataset(attrs=ds.attrs, sales=sales, dates=ds.dates)


# --- Grouped folds -------------------------------------------------------------------------

@pytest.mark.parametrize("scenario", list(UNIT_COLUMNS))
@pytest.mark.parametrize("seed", PR.FOLD_SEEDS)
def test_no_group_leakage_for_any_fold_seed(ds, scenario, seed):
    """A held-out group (twin cluster, INN, ATC2, ATC1) never also appears in the training pool."""
    for fold, test, pool in E.scenario_units(ds, scenario, fold_seed=seed, fold_method="random_order"):
        assert test.any() and pool.any() and not (test & pool).any()
        for col in UNIT_COLUMNS[scenario]:
            held = set(ds.attrs.loc[test, col].dropna())
            assert held.isdisjoint(ds.attrs.loc[pool, col].dropna()), (scenario, seed, fold, col)


@pytest.mark.parametrize("scenario", list(UNIT_COLUMNS))
def test_donors_are_disjoint_from_test_and_training_skus(ds, scenario):
    for seed in PR.FOLD_SEEDS[:2]:
        fold, test, pool = E.scenario_units(ds, scenario, fold_seed=seed, fold_method="random_order")[0]
        roles, ev_rows = E.prepare_unit(ds, scenario, 2023, test, pool)
        for _, targets, donors, _ in roles:
            assert not (donors & test).any() and not (donors & targets).any()
        # Perturbing every held-out SKU leaves the features of the evaluated rows unchanged.
        donors = roles[0][2]
        before = F.build_frame(ds, ev_rows, donors)
        after = F.build_frame(_perturbed(ds, rows_mask=test), ev_rows, donors)
        cols = [c for c in before.columns if c != "sales"]
        pd.testing.assert_frame_equal(before[cols], after[cols])


def test_fold_assignment_is_reproducible_and_seed_dependent(ds):
    labels = ds.attrs["atc1"].to_numpy()
    a = E.assign_folds(labels, seed=7, method="random_order")
    assert np.array_equal(a, E.assign_folds(labels, seed=7, method="random_order"))
    assert len(set(np.bincount(a))) > 0 and np.bincount(a).min() > 0
    others = [E.assign_folds(labels, seed=s, method="random_order") for s in PR.FOLD_SEEDS]
    assert len({tuple(o) for o in others}) > 1
    for o in others:  # every label stays in exactly one fold
        assert pd.Series(o).groupby(labels).nunique().max() == 1
    # The primary assignment is unchanged by the new option.
    assert np.array_equal(E.assign_folds(labels), E.assign_folds(labels, method="balanced"))


# --- Fake training runs for the orchestration tests -------------------------------------------

def _fake_run_unit(calls, val_winner="atc", test_winner="inn"):
    """Stand-in for experiments.run_unit: real rows, targets and hierarchical median, fake model forecasts.

    The arm `val_winner` (a dict fold -> arm, or one arm) is perfect on validation and `test_winner`
    on test; every other arm is poor.
    """
    def run(ds, scenario, split_name, test_mask, pool_mask, loss, arms=None, iterations=None, fold=0,
            split=None, seed=None, placebo_seed=None, peer_baselines=False, keep_models=False):
        calls.append({"split_name": split_name, "split": split, "fold": fold, "iterations": iterations})
        _, ev_rows = E.prepare_unit(ds, scenario, split["eval_year"], test_mask, pool_mask)
        sales = ds.sales0[ev_rows["i"].to_numpy(), ev_rows["t"].to_numpy()]
        base = F.build_frame(ds, ev_rows, pool_mask, with_launch_age=scenario == "N")
        out = pd.DataFrame({"fold": fold, "sku": ds.attrs["sku"].to_numpy()[ev_rows["i"]], "i": ev_rows["i"].to_numpy(),
                            "t": ev_rows["t"].to_numpy(), "sales": sales,
                            "hierarchical_median": B.cold_start_baselines(ds, base, pool_mask)["hierarchical_median"].to_numpy()})
        winner = val_winner if split_name == "validation" else test_winner
        winner = winner.get(fold, "both") if isinstance(winner, dict) else winner
        for arm in arms:
            out[f"catboost_{arm}"] = sales if arm == winner else sales * 3 + 1
        info = [{"arm": a, "half": h, "iterations": 10 + fold, "split": split_name} for a in arms for h in (0, 1)]
        return out, info, {}, []
    return run


def test_selection_only_sees_validation_metrics(ds, monkeypatch):
    calls, seen = [], []
    monkeypatch.setattr(E, "run_unit", _fake_run_unit(calls, val_winner="atc", test_winner="inn"))
    real_select = PR.select_metadata_arm

    def spy(val_metrics, test_year, *a, **k):
        seen.append(val_metrics.copy())
        assert not any(c["split_name"] == "test" for c in calls), "selection must happen before any test fit"
        return real_select(val_metrics, test_year, *a, **k)
    monkeypatch.setattr(PR, "select_metadata_arm", spy)
    real_metrics = PR.validation_metrics
    frames = []

    def metrics_spy(frame, *a, **k):
        frames.append(frame)
        return real_metrics(frame, *a, **k)
    monkeypatch.setattr(PR, "validation_metrics", metrics_spy)
    for year in PR.TEST_YEARS:
        calls.clear()
        frames.clear()
        _, tst, _, choices = PR.run_cycle(ds, "C", year, "Tweedie:variance_power=1.5", M.ARMS)
        assert choices["selected_arm"] == "atc"           # the validation winner, not the test winner
        assert set(choices["selected_arm_by_fold"].values()) == {"atc"}
        assert metrics.wape(tst["sales"], tst["catboost_inn"]) == 0
        assert frames and all(PR.frame_years(f) == {year - 1} for f in frames)   # the rows, not a label
        assert {c["split"]["eval_year"] for c in calls if c["split_name"] == "validation"} == {year - 1}
        assert max(max(c["split"]["train_years"]) for c in calls if c["split_name"] == "validation") == year - 2
        assert max(max(c["split"]["train_years"]) for c in calls if c["split_name"] == "test") == year - 1


def test_validation_guards_check_the_rows(ds, monkeypatch):
    monkeypatch.setattr(E, "run_unit", _fake_run_unit([]))
    val, tst, _, _ = PR.run_cycle(ds, "D", 2023, "Tweedie:variance_power=1.5", M.ARMS)
    with pytest.raises(AssertionError):
        PR.validation_metrics(tst, "D", M.ARMS, 2023)
    with pytest.raises(AssertionError):
        PR.calibration_factor(tst, 2023)
    assert PR.calibration_factor(val, 2023) > 0


def test_loss_is_chosen_on_the_validation_year(ds, monkeypatch, tmp_path):
    monkeypatch.setattr(PR, "LOG_FILE", tmp_path / "log.txt")
    monkeypatch.setattr(PR, "PROTOCOL_DIR", tmp_path)
    calls = []

    def run(ds, scenario, split_name, test_mask, pool_mask, loss, arms=None, fold=0, split=None, seed=None, **kw):
        calls.append({"split_name": split_name, "split": split})
        _, ev_rows = E.prepare_unit(ds, scenario, split["eval_year"], test_mask, pool_mask)
        sales = ds.sales0[ev_rows["i"].to_numpy(), ev_rows["t"].to_numpy()]
        good = loss == ("MAE" if split["eval_year"] == 2022 else "RMSE")   # RMSE would win on the test year
        out = pd.DataFrame({"sku": ds.attrs["sku"].to_numpy()[ev_rows["i"]], "t": ev_rows["t"].to_numpy(), "sales": sales,
                            "catboost_both": sales * (1.0 if good else 1.3)})
        return out, [{"iterations": 5}], {}, []
    monkeypatch.setattr(E, "run_unit", run)
    loss, table = PR.select_loss(ds, 2023)
    assert loss == "MAE" and set(table["eval_year"]) == {2022}
    assert {c["split_name"] for c in calls} == {"validation"}
    assert all(c["split"]["eval_year"] == 2022 and max(c["split"]["train_years"]) == 2021 for c in calls)


def test_stored_runs_are_reused_only_when_they_match(ds, monkeypatch, tmp_path):
    monkeypatch.setattr(PR, "PROTOCOL_DIR", tmp_path)
    monkeypatch.setattr(PR, "LOG_FILE", tmp_path / "log.txt")
    monkeypatch.setattr(E, "run_unit", _fake_run_unit([]))
    first = PR.execute(ds, "rolling", "D", 2023, "Tweedie:variance_power=1.5", M.ARMS)
    assert first["catboost_params"]["random_seed"] == config.SEED and first["fingerprint"]["dataset"]["n_skus"] == len(ds.attrs)
    assert PR.execute(ds, "rolling", "D", 2023, "Tweedie:variance_power=1.5", M.ARMS)["run_id"] == first["run_id"]
    with pytest.raises(RuntimeError):
        PR.execute(ds, "rolling", "D", 2023, "MAE", M.ARMS)
    seeded = PR.execute(ds, "model_seeds", "D", 2023, "Tweedie:variance_power=1.5", M.ARMS, model_seed=7)
    assert seeded["catboost_params"]["random_seed"] == 7


def test_selection_rejects_test_metrics():
    v = pd.DataFrame({"split": ["validation", "validation", "validation", "test"], "eval_year": [2022, 2022, 2022, 2023],
                      "arm": ["inn", "atc", "both", "atc"], "WAPE": [0.5, 0.7, 0.6, 0.1]})
    with pytest.raises(AssertionError):
        PR.select_metadata_arm(v, 2023)
    with pytest.raises(AssertionError):
        PR.select_metadata_arm(v.iloc[:3].assign(eval_year=2023), 2023)
    assert PR.select_metadata_arm(v.iloc[:3], 2023) == "inn"


def test_cold_start_choices_never_use_the_test_folds_own_validation(ds, monkeypatch):
    """Arm and calibration of test fold k come from validation folds other than k."""
    monkeypatch.setattr(E, "run_unit", _fake_run_unit([], val_winner={0: "inn", 1: "atc"}))
    val, tst, _, choices = PR.run_cycle(ds, "C", 2023, "Tweedie:variance_power=1.5", M.ARMS)
    by_fold = choices["selected_arm_by_fold"]
    assert by_fold["0"] == "atc" and by_fold["1"] == "inn"           # each from the other validation fold
    for fold in (0, 1):
        rows = tst[tst["fold"] == fold]
        assert (rows["catboost_selected"] == rows[f"catboost_{by_fold[str(fold)]}"]).all()
    # Changing the validation-year sales of fold 0's held-out SKUs leaves fold 0's calibrated forecasts unchanged.
    fold0 = E.scenario_units(ds, "C")[0][1]
    sales = ds.sales.copy()
    sales[np.ix_(np.flatnonzero(fold0), np.arange(36, 48))] *= 7      # 2022 volumes only; who sells stays the same
    perturbed = data.Dataset(attrs=ds.attrs, sales=sales, dates=ds.dates)
    _, tst_p, _, choices_p = PR.run_cycle(perturbed, "C", 2023, "Tweedie:variance_power=1.5", M.ARMS)
    a, b = tst[tst["fold"] == 0], tst_p[tst_p["fold"] == 0]
    np.testing.assert_allclose(a["calibrated_median"].to_numpy(), b["calibrated_median"].to_numpy())
    assert choices["calibration_factor_by_fold"]["0"] == pytest.approx(choices_p["calibration_factor_by_fold"]["0"])
    assert choices["calibration_factor_by_fold"]["1"] != pytest.approx(choices_p["calibration_factor_by_fold"]["1"])


def test_median_calibration_never_uses_test_targets(ds, monkeypatch):
    calls = []
    fake = _fake_run_unit(calls)

    def run_with_test_targets(scale):
        def run(*args, **kwargs):
            out, info, m, i = fake(*args, **kwargs)
            if args[2] == "test":
                out["sales"] = out["sales"] * scale + 1000
            return out, info, m, i
        return run
    results = []
    for scale in (1.0, 50.0):
        monkeypatch.setattr(E, "run_unit", run_with_test_targets(scale))
        val, tst, _, choices = PR.run_cycle(ds, "B", 2023, "Tweedie:variance_power=1.5", M.ARMS)
        assert choices["calibration_factor_validation_folds"] == pytest.approx(
            val["sales"].sum() / val["hierarchical_median"].sum())
        results.append(tst["calibrated_median"].to_numpy())
    np.testing.assert_array_equal(results[0], results[1])


def test_tree_counts_come_from_another_fold(ds, monkeypatch):
    calls = []
    monkeypatch.setattr(E, "run_unit", _fake_run_unit(calls))
    PR.run_cycle(ds, "D", 2023, "Tweedie:variance_power=1.5", M.ARMS)
    for c in calls:
        if c["split_name"] == "test":
            source = 1 if c["fold"] == 0 else 0
            assert set(c["iterations"].values()) == {10 + source}


def test_fold_predictions_are_combined_once_per_row(ds, monkeypatch):
    monkeypatch.setattr(E, "run_unit", _fake_run_unit([]))
    for scenario in ("B", "D1"):
        _, tst, _, _ = PR.run_cycle(ds, scenario, 2023, "Tweedie:variance_power=1.5", M.ARMS)
        assert not tst.duplicated(["sku", "t"]).any()
        assert tst.groupby("sku")["fold"].nunique().max() == 1
        expected = set()
        for fold, test, pool in E.scenario_units(ds, scenario):
            _, rows = E.prepare_unit(ds, scenario, 2023, test, pool)
            expected |= set(zip(ds.attrs["sku"].to_numpy()[rows["i"]], rows["t"]))
        assert set(zip(tst["sku"], tst["t"])) == expected


# --- Shuffled-peer placebo -------------------------------------------------------------------

def test_placebo_is_reproducible_and_permutes_whole_groups(ds):
    pool = np.ones(len(ds.attrs), bool)
    targets, donors = E.donor_halves(ds, "C", pool)[0]
    rows = F.make_rows(ds, targets & F.active_at_origin(ds, 2023), 2023)
    true = F.group_aggregates(ds, rows, donors)
    a = F.group_aggregates(ds, rows, donors, placebo_seed=3)
    pd.testing.assert_frame_equal(a, F.group_aggregates(ds, rows, donors, placebo_seed=3))
    b = F.group_aggregates(ds, rows, donors, placebo_seed=4)
    meta = [c for g in F.METADATA_GROUPINGS for c in F.agg_columns(g)]
    control = [c for g in ("global", "nfc") for c in F.agg_columns(g)]
    pd.testing.assert_frame_equal(a[control], true[control])        # control features are untouched
    assert not a[meta].equals(true[meta]) and not a[meta].equals(b[meta])
    frame = pd.concat([rows, a, ds.attrs.iloc[rows["i"]][["inn", "atc2"]].set_index(rows.index)], axis=1)
    for grouping, key in (("inn", "inn"), ("atc2", "atc2")):
        spread = frame.dropna(subset=[key]).groupby([key, "t"])[F.agg_columns(grouping)].nunique(dropna=False)
        assert (spread.max() <= 1).all()                              # one shuffled group per true group
    # A row has a shuffled 12-month mean exactly when it has a true one (its group is active at the origin).
    for grouping in F.METADATA_GROUPINGS:
        col = f"{grouping}_mean12"
        assert (true[col].isna() == a[col].isna()).all(), grouping


def test_placebo_permutation_is_a_derangement_of_the_active_groups():
    rng = np.random.default_rng(0)
    for grouping in F.METADATA_GROUPINGS:
        active = rng.random(50) < 0.6
        perm = F.placebo_permutation(50, active, 3, grouping)
        assert np.array_equal(np.sort(perm), np.arange(50))          # a bijection
        assert (perm[~active] == np.flatnonzero(~active)).all()      # inactive groups stay
        assert (perm[active] != np.flatnonzero(active)).all()        # no active group keeps its own statistics
        assert active[perm[active]].all()
        start = np.flatnonzero(active)[0]                            # one cycle through all active groups
        seen, g = 1, perm[start]
        while g != start:
            seen, g = seen + 1, perm[g]
        assert seen == active.sum()
        np.testing.assert_array_equal(perm, F.placebo_permutation(50, active, 3, grouping))
        assert not np.array_equal(perm, F.placebo_permutation(50, active, 4, grouping))


def test_placebo_uses_only_donor_sales_before_the_origin(ds):
    pool = np.ones(len(ds.attrs), bool)
    targets, donors = E.donor_halves(ds, "B", pool)[0]
    rows = F.make_rows(ds, targets & F.active_at_origin(ds, 2023), 2023)
    before = F.group_aggregates(ds, rows, donors, placebo_seed=2)
    pd.testing.assert_frame_equal(before, F.group_aggregates(_perturbed(ds, months=slice(48, 60)), rows, donors,
                                                             placebo_seed=2))
    pd.testing.assert_frame_equal(before, F.group_aggregates(_perturbed(ds, rows_mask=~donors), rows, donors,
                                                             placebo_seed=2))


def test_placebo_with_own_unit_exclusion_ignores_own_sales(ds):
    donors = np.ones(len(ds.attrs), bool)
    unit = ds.attrs["twin_cluster"].to_numpy()
    target = unit == unit[ds.attrs["twin_size"].to_numpy().argmax()]
    rows = F.make_rows(ds, target, 2023)
    before = F.group_aggregates(ds, rows, donors, unit, placebo_seed=5)
    after = F.group_aggregates(_perturbed(ds, rows_mask=target), rows, donors, unit, placebo_seed=5)
    pd.testing.assert_frame_equal(before, after)


# --- Scenario N0 -----------------------------------------------------------------------------

def test_n0_forecasts_every_month_without_the_launch_month(ds):
    pool = np.ones(len(ds.attrs), bool)
    roles, ev_rows = E.prepare_unit(ds, "N0", 2023, pool, pool)
    assert (ev_rows.groupby("i").size() == 12).all()
    assert set(ev_rows["i"]) == set(np.flatnonzero(F.launched_in(ds, 2023)))
    cat, num = M.feature_columns("both", market_flag=True)
    assert "age_at_target" not in cat + num and "on_market_at_origin" in num
    # Moving each launch to another month of 2023 (and changing its volumes) must not change any feature.
    launches = np.flatnonzero(F.launched_in(ds, 2023))
    sales = ds.sales.copy()
    year = np.arange(48, 60)
    sales[np.ix_(launches, year)] = np.nan
    sales[launches, 59] = 999.0
    attrs = ds.attrs.copy()
    attrs.loc[launches, "first_t"] = 59
    moved = data.Dataset(attrs=attrs, sales=sales, dates=ds.dates)
    _, ev_moved = E.prepare_unit(moved, "N0", 2023, pool, pool)
    pd.testing.assert_frame_equal(ev_rows, ev_moved)
    for _, targets, donors, exclude in roles:
        opts = {"with_market_flag": True}
        a = F.build_frame(ds, ev_rows, donors, exclude, **opts)
        b = F.build_frame(moved, ev_rows, donors, exclude, **opts)
        cols = [c for c in a.columns if c != "sales"]
        pd.testing.assert_frame_equal(a[cols], b[cols])
        train = E.training_rows(ds, targets, [2020, 2021, 2022], include_launches=True, launch_full_year=True)
        assert not F.launched_in(ds, 2023)[train["i"]][train["t"].to_numpy() >= 48].any()
    cohorts = pd.concat([F.make_rows(ds, F.launched_in(ds, y), y) for y in (2020, 2021, 2022)], ignore_index=True)
    np.testing.assert_array_equal(B.launch_cohort_baseline(ds, cohorts, ev_rows),
                                  B.launch_cohort_baseline(moved, cohorts, ev_rows))


def test_n_keeps_its_retrospective_launch_rows(ds):
    pool = np.ones(len(ds.attrs), bool)
    _, rows_n = E.prepare_unit(ds, "N", 2023, pool, pool)
    _, rows_n0 = E.prepare_unit(ds, "N0", 2023, pool, pool)
    first_t = ds.attrs["first_t"].to_numpy()
    assert (rows_n["t"].to_numpy() >= first_t[rows_n["i"]]).all()
    assert set(map(tuple, rows_n[["i", "t"]].to_numpy())) <= set(map(tuple, rows_n0[["i", "t"]].to_numpy()))


# --- Metric definitions --------------------------------------------------------------------

def test_metric_definitions_are_unchanged():
    y = np.array([0.0, 10.0, 5.0, 5.0])
    p = np.array([1.0, 8.0, 5.0, 10.0])
    assert metrics.wape(y, p) == pytest.approx(8 / 20)
    assert metrics.bias(y, p) == pytest.approx(24 / 20 - 1)
    frame = pd.DataFrame({"sku": [1, 1, 2, 2, 3, 3], "sales": [1.0, 2, 3, 4, 10, 0], "pred": [2.0, 2, 1, 1, 9, 9]})
    s = PR.scores(frame, "pred")
    assert s["spearman"] == pytest.approx(0.5)                        # SKU totals 3, 7, 10 vs 4, 2, 18
    assert s["WAPE_annual"] == pytest.approx((1 + 5 + 8) / 20)
    ref = AN.overall_metrics({("C", "test"): frame.assign(**{f"catboost_{a}": frame["pred"] for a in M.ARMS},
                                                          **{b: frame["pred"] for b in AN.COLD_BASELINES})})
    row = ref[ref["model"] == "catboost_none"].iloc[0]
    for k, v in (("WAPE", s["WAPE"]), ("bias", s["bias"]), ("spearman_annual", s["spearman"]),
                 ("WAPE_annual", s["WAPE_annual"]), ("MAE", s["MAE"]), ("RMSE", s["RMSE"])):
        assert row[k] == pytest.approx(v)


def test_cycle_splits_never_reach_the_test_year():
    for year in PR.TEST_YEARS:
        s = PR.cycle_splits(year)
        assert s["validation"]["eval_year"] == year - 1 and max(s["validation"]["train_years"]) == year - 2
        assert s["test"]["eval_year"] == year and max(s["test"]["train_years"]) == year - 1
        assert min(s["validation"]["train_years"]) == PR.FIRST_TRAIN_YEAR
    assert PR.cycle_splits(2023)["validation"] == config.VALIDATION and PR.cycle_splits(2023)["test"] == config.TEST


# --- End to end on the small sample with few trees -----------------------------------------

def test_cycle_runs_end_to_end(ds, monkeypatch):
    monkeypatch.setitem(config.CATBOOST_PARAMS, "iterations", 20)
    monkeypatch.setattr(config, "EARLY_STOPPING_ROUNDS", 5)
    val, tst, fits, choices = PR.run_cycle(ds, "N0", 2022, "Tweedie:variance_power=1.5", M.ARMS, model_seed=7)
    assert choices["selected_arm"] in PR.METADATA_ARMS
    assert {f["split"] for f in fits} == {"validation", "test"}
    assert set(tst["t"]) == set(range(36, 48)) and set(val["t"]) == set(range(24, 36))
    assert tst[[f"catboost_{a}" for a in M.ARMS] + ["calibrated_median", "launch_cohort_mean"]].notna().all().all()
    _, tst_p, _, choices_p = PR.run_cycle(ds, "B", 2023, "Tweedie:variance_power=1.5", [PR.PLACEBO_ARM], placebo_seed=1)
    assert choices_p["selected_arm"] is None and tst_p["catboost_both"].notna().all()
