"""Scenario definitions (existing drug, simulated and real cold start) and the experiment runner.

Peer statistics and leakage
---------------------------
INN and ATC information reaches the models through peer-group statistics (features.group_aggregates).
If those statistics were computed from a pool that also contains the training SKU, a tree model could
compare a group's statistic across its members and recover each member's own sales; for a product
without history that signal does not exist, so the model would be trained on a leak.

The cold-start scenarios and N therefore use cross-fitting: the training pool is split into two
halves by the scenario's grouping unit; model m is trained on the SKUs of half m with peer
statistics computed from the other half only (the donors), and every evaluated SKU is forecast by
both models with the corresponding donors, the two forecasts being averaged. Inside one model the
statistics of a group are identical for all of its training SKUs, as for an unseen product.
Scenario A (own history available) uses one model on all SKUs and removes each SKU's own twin
cluster from its peer group, identically for training and evaluation rows.
"""
import time

import numpy as np
import pandas as pd

from . import baselines as B
from . import config
from . import features as F
from . import modeling as M

SPLITS = {"validation": config.VALIDATION, "test": config.TEST}

SCENARIOS = {
    "A": "Existing drug: own sales history available",
    "B": "New product, known INN: SKU (and identical twins) held out",
    "C": "New INN, known ATC: all SKUs of the INN held out",
    "D": "Unseen ATC group: ATC level-2 group and its INNs held out (only ATC1 known)",
    "D1": "Unseen ATC group, strict: ATC level-1 group and its INNs held out",
    "N": "Real new launches: SKUs first sold in the evaluation year (retrospective; launch month known)",
    "N0": "Launch cohort of the evaluation year, all 12 months, launch month unknown at the origin",
}
LAUNCH_SCENARIOS = ("N", "N0")
COLD_START_FOLD_LABEL = {"B": "twin_cluster", "C": "inn_unit", "D": "atc2", "D1": "atc1"}
HALF_LABEL = {"N": "twin_cluster", "N0": "twin_cluster", **COLD_START_FOLD_LABEL}
BOOTSTRAP_CLUSTER = {"A": "sku", "B": "twin_cluster", "C": "inn_unit", "D": "atc2", "D1": "atc1", "N": "sku", "N0": "sku"}
SCENARIO_ARMS = {"A": M.ARMS + [M.CODES_ARM], "B": M.ARMS + [M.CODES_ARM]}


def arms_for(scenario):
    return SCENARIO_ARMS.get(scenario, M.ARMS)


def assign_folds(labels, n_folds=config.N_FOLDS, seed=config.SEED, method="balanced"):
    """Group k-fold: every label goes to exactly one fold; folds are balanced by number of SKUs.

    method="balanced" (the primary assignment) places labels from the largest to the smallest on
    the least-loaded fold, so the seed only breaks ties between labels of equal size; with few large
    groups (ATC1, ATC2) the folds are then almost the same for every seed. method="random_order"
    places the labels in a seeded random order on the least-loaded fold, which gives a different
    balanced assignment for every seed and is used for the fold-assignment robustness study.
    """
    uniq, inverse, counts = np.unique(np.asarray(labels).astype(str), return_inverse=True, return_counts=True)
    order = np.random.default_rng(seed).permutation(len(uniq))
    if method == "balanced":
        order = order[np.argsort(-counts[order], kind="stable")]
    elif method != "random_order":
        raise ValueError(f"unknown fold assignment method: {method}")
    load = np.zeros(n_folds)
    fold_of_label = np.empty(len(uniq), dtype=int)
    for g in order:
        f = int(np.argmin(load))
        fold_of_label[g] = f
        load[f] += counts[g]
    return fold_of_label[inverse]


def cold_start_masks(ds, scenario, folds, k):
    """Held-out SKUs and the training pool for one fold of a simulated cold-start scenario."""
    attrs = ds.attrs
    test = folds == k
    pool = ~test
    if scenario in ("D", "D1"):
        # An INN can belong to several ATC groups; drop it from the pool so the test INNs are unseen too.
        test_inns = attrs.loc[test, "inn"].dropna()
        pool &= ~attrs["inn"].isin(test_inns).to_numpy()
    return test, pool


def known_inn(ds, pool, year):
    """SKUs whose INN is sold by at least one SKU of `pool` in the 12 months before the origin of `year`."""
    attrs = ds.attrs
    on_market = attrs.loc[pool & F.active_at_origin(ds, year), "inn"].dropna()
    return attrs["inn"].isin(on_market).to_numpy()


def stratified_halves(units, strata, seed):
    """Split units into two halves, alternating the units of each stratum between the halves.

    Used in scenario B so that an INN with two or more twin clusters is present in both halves and
    therefore known to both cross-fitted models; units without a stratum are split by size.
    """
    rng = np.random.default_rng(seed)
    table = pd.DataFrame({"unit": units, "stratum": strata}).drop_duplicates("unit")
    half_of_unit = {}
    with_stratum = table.dropna(subset=["stratum"])
    for k, (_, g) in enumerate(with_stratum.groupby("stratum", sort=True)):
        order = rng.permutation(g["unit"].to_numpy())
        start = int(rng.integers(2))
        for j, u in enumerate(order):
            half_of_unit[u] = (start + j) % 2
    rest = table[table["stratum"].isna()]["unit"].to_numpy()
    if len(rest):
        for u, h in zip(rest, assign_folds(rest, n_folds=2, seed=seed)):
            half_of_unit[u] = int(h)
    return np.array([half_of_unit[u] for u in units])


def donor_halves(ds, scenario, pool, seed=config.SEED + 1):
    """[(targets, donors), (targets, donors)]: the two cross-fitting roles of the pool."""
    attrs = ds.attrs
    labels = attrs[HALF_LABEL[scenario]].to_numpy()
    half = np.full(len(attrs), -1)
    if scenario == "B":
        half[pool] = stratified_halves(labels[pool], attrs["inn"].to_numpy()[pool], seed)
    else:
        half[pool] = assign_folds(labels[pool], n_folds=2, seed=seed)
    roles = []
    for m in (0, 1):
        targets = pool & (half == m)
        donors = pool & (half == 1 - m)
        if scenario in ("D", "D1"):
            donors &= ~attrs["inn"].isin(attrs.loc[targets, "inn"].dropna()).to_numpy()
        roles.append((targets, donors))
    return roles


def known_atc_depth(ds, test_idx, donor_sets):
    """Deepest ATC level of each test SKU that occurs among the donors of every model (0 = none)."""
    depth = np.zeros(len(test_idx), dtype=int)
    for level in range(1, 6):
        col = f"atc{level}"
        has = ds.attrs[col].to_numpy()[test_idx]
        known = np.ones(len(test_idx), dtype=bool)
        for donors in donor_sets:
            known &= np.isin(has, list(set(ds.attrs.loc[donors, col].dropna())))
        depth = np.where(known, level, depth)
    return depth


def training_rows(ds, skus, years, include_launches=False, launch_full_year=False):
    """Rows of SKUs on the market at each origin, plus (optionally) the launches of each training year.

    Launches enter from their first sale (scenario N) or with all 12 months of the launch year
    (launch_full_year, scenario N0).
    """
    parts = [F.make_rows(ds, skus & F.active_at_origin(ds, y), y) for y in years]
    if include_launches:
        parts += [F.make_rows(ds, skus & F.launched_in(ds, y), y, from_launch=not launch_full_year) for y in years]
    return pd.concat(parts, ignore_index=True)


def evaluation_rows(ds, scenario, test_mask, year):
    if scenario == "N":
        return F.make_rows(ds, test_mask & F.launched_in(ds, year), year, from_launch=True)
    if scenario == "N0":
        # Same retrospective cohort as N, but every month of the year is forecast from the origin.
        return F.make_rows(ds, test_mask & F.launched_in(ds, year), year)
    return F.make_rows(ds, test_mask & F.active_at_origin(ds, year), year)


def prepare_unit(ds, scenario, year, test_mask, pool_mask):
    """Cross-fitting roles [(half, targets, donors, exclude_unit)] and evaluation rows for one unit."""
    twins = ds.attrs["twin_cluster"].to_numpy()
    if scenario == "A":
        roles = [(0, pool_mask, pool_mask, twins)]
    else:
        # In N an evaluated launch may have an older identical twin among the donors of one model;
        # removing the own twin cluster keeps evaluation rows like training rows (a no-op for those).
        exclude = twins if scenario in LAUNCH_SCENARIOS else None
        roles = [(m, t, d, exclude) for m, (t, d) in enumerate(donor_halves(ds, scenario, pool_mask))]
    if scenario == "B":
        # "Known INN": sold in the 12 months before the origin by donors of both cross-fitted models.
        for _, _, donors, _ in roles:
            test_mask = test_mask & known_inn(ds, donors, year)
    return roles, evaluation_rows(ds, scenario, test_mask, year)


def run_unit(ds, scenario, split_name, test_mask, pool_mask, loss, arms=None,
             iterations=None, fold=0, keep_models=False, split=None, seed=None, placebo_seed=None,
             peer_baselines=False):
    """Train every ablation arm for one (scenario, fold, split) and return predictions + run info.

    On the validation split each model is early-stopped on the evaluation year; on the test split
    it is retrained on all training years with the number of trees found on validation
    (`iterations` maps (arm, half) to a tree count). `split` overrides the years of SPLITS[split_name]
    (rolling protocol), `seed` the CatBoost seed, and `placebo_seed` replaces the INN/ATC peer
    statistics by those of permuted groups (shuffled-peer placebo). With peer_baselines, scenario A
    also gets the peer-group reference forecasts of the cold-start scenarios.
    """
    arms = arms or arms_for(scenario)
    split = split or SPLITS[split_name]
    history, launch, launch_n0 = scenario == "A", scenario == "N", scenario == "N0"
    roles, ev_rows = prepare_unit(ds, scenario, split["eval_year"], test_mask, pool_mask)
    frame_opts = {"with_history": history, "with_launch_age": launch, "with_market_flag": launch_n0}

    out = pd.DataFrame({
        "fold": fold,
        "sku": ds.attrs["sku"].to_numpy()[ev_rows["i"]],
        "date": ds.dates[ev_rows["t"].to_numpy()],
        "i": ev_rows["i"].to_numpy(),
        "t": ev_rows["t"].to_numpy(),
        "sales": ds.sales0[ev_rows["i"].to_numpy(), ev_rows["t"].to_numpy()],
    })
    if not history or peer_baselines:
        # Reference forecasts use the whole training pool (they are not trained, so nothing can leak).
        base = F.build_frame(ds, ev_rows, pool_mask, with_launch_age=launch)
        out = out.join(B.cold_start_baselines(ds, base, pool_mask))
        if launch:
            out["launch_age_mean"] = B.launch_age_baseline(ds, training_rows(
                ds, pool_mask, split["train_years"], include_launches=True), ev_rows)
            out["age_at_target"] = base["age_at_target"].to_numpy()
        if launch_n0:
            cohorts = pd.concat([F.make_rows(ds, pool_mask & F.launched_in(ds, y), y) for y in split["train_years"]],
                                ignore_index=True)
            out["launch_cohort_mean"] = B.launch_cohort_baseline(ds, cohorts, ev_rows)
        if scenario in ("C", "D", "D1"):
            out["known_atc_depth"] = known_atc_depth(ds, out["i"].to_numpy(), [r[2] for r in roles])

    preds = {arm: [] for arm in arms}
    info, models, importances = [], {}, []
    for half, targets, donors, exclude in roles:
        tr_rows = training_rows(ds, targets, split["train_years"], include_launches=launch or launch_n0,
                                launch_full_year=launch_n0)
        train = F.build_frame(ds, tr_rows, donors, exclude, placebo_seed=placebo_seed, **frame_opts)
        ev = F.build_frame(ds, ev_rows, donors, exclude, placebo_seed=placebo_seed, **frame_opts)
        diagnostics = None
        if placebo_seed is not None:
            diagnostics = {name: F.placebo_diagnostics(F.group_aggregates(ds, rows, donors, exclude), frame)
                           for name, rows, frame in (("train", tr_rows, train), ("eval", ev_rows, ev))}
        if history and half == 0:
            out = out.join(B.existing_drug_baselines(ev))
        for arm in arms:
            cat, num = M.feature_columns(arm, history=history, launch_age=launch, market_flag=launch_n0)
            start = time.time()
            if split_name == "validation":
                model = M.fit(train, cat, num, loss, eval_frame=ev, seed=seed)
                n_iter = M.best_iterations(model)
            else:
                n_iter = iterations[(arm, half)]
                model = M.fit(train, cat, num, loss, iterations=n_iter, seed=seed)
            preds[arm].append(M.predict(model, ev, cat, num))
            info.append({
                "scenario": scenario, "split": split_name, "fold": fold, "arm": arm, "half": half,
                "loss": loss, "iterations": n_iter, "n_features": len(cat) + len(num),
                "train_rows": len(train), "train_skus": int(train["sku"].nunique()),
                "donor_skus": int(np.asarray(donors).sum()),
                "eval_rows": len(ev), "eval_skus": int(ev["sku"].nunique()),
                "fit_seconds": round(time.time() - start, 1),
                **({"placebo_diagnostics": diagnostics} if diagnostics else {}),
            })
            if keep_models:
                models[(arm, half)] = model
                imp = model.get_feature_importance(type="PredictionValuesChange")
                importances.append(pd.DataFrame({
                    "scenario": scenario, "fold": fold, "arm": arm, "half": half,
                    "feature": cat + num, "importance": imp,
                }))
    for arm in arms:
        out[f"catboost_{arm}"] = np.mean(preds[arm], axis=0)
    return out, info, models, importances


def scenario_units(ds, scenario, fold_seed=config.SEED, fold_method="balanced"):
    """(fold, test_mask, pool_mask) triples for a scenario."""
    n = len(ds.attrs)
    if scenario in ("A",) + LAUNCH_SCENARIOS:
        return [(0, np.ones(n, dtype=bool), np.ones(n, dtype=bool))]
    folds = assign_folds(ds.attrs[COLD_START_FOLD_LABEL[scenario]].to_numpy(), seed=fold_seed, method=fold_method)
    return [(k, *cold_start_masks(ds, scenario, folds, k)) for k in range(config.N_FOLDS)]
