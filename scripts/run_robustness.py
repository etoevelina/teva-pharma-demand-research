"""Robustness studies of the INN/ATC comparison (test year 2023 unless stated otherwise).

Studies (each run of the rolling cycle repeats validation, all choices on the validation year and
the test-year fits; see src/teva_forecast/protocol.py):

* model_seeds - CatBoost seeds 7, 2024, 11, 99 (seed 42 is the rolling run) with the same data and
  folds; all scenarios, the four main arms;
* fold_seeds  - five seeded random-order grouped-fold assignments (seeds 42, 7, 2024, 11, 99) with
  CatBoost seed 42; scenarios B, C, D, D1, the four main arms;
* placebo     - shuffled-peer placebo of the INN + ATC arm and of the validation-selected arm with
  permutation seeds 1-5; all scenarios except D1, where no INN/ATC peer statistics exist;
* trees       - the original study: test-year refits with 1,200 trees and seeds 42, 7, 2024, read at
  several tree counts (descriptive, nothing feeds back into model selection).

Usage:
    python scripts/run_robustness.py                         # model_seeds fold_seeds placebo (about 4 h)
    python scripts/run_robustness.py --studies placebo --scenarios A B
    python scripts/run_robustness.py --studies trees         # original tree-count curves (about 60 min)
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import config, data, experiments as E, features as F, metrics, modeling as M  # noqa: E402
from teva_forecast import protocol as PR  # noqa: E402

MAX_TREES = 1200
CHECKPOINTS = [100, 200, 300, 500, 750, 1000, 1200]
TREE_SEEDS = [42, 7, 2024]
TREES_OUT = config.TABLES_DIR / "robustness_trees_seeds.csv"
STUDIES = ["model_seeds", "fold_seeds", "placebo", "trees"]


def tree_curves(ds, scenarios):
    loss = pd.read_csv(config.TABLES_DIR / "runs.csv")["loss"].iloc[0]
    split = E.SPLITS["test"]
    rows = []
    for scenario in scenarios:
        fold, test, pool = E.scenario_units(ds, scenario)[0]
        history, launch = scenario == "A", scenario == "N"
        roles, ev_rows = E.prepare_unit(ds, scenario, split["eval_year"], test, pool)
        actual = ds.sales0[ev_rows["i"].to_numpy(), ev_rows["t"].to_numpy()]
        frames = []
        for half, targets, donors, exclude in roles:
            tr_rows = E.training_rows(ds, targets, split["train_years"], include_launches=launch)
            frames.append((
                F.build_frame(ds, tr_rows, donors, exclude, with_history=history, with_launch_age=launch),
                F.build_frame(ds, ev_rows, donors, exclude, with_history=history, with_launch_age=launch),
            ))
        for arm in E.arms_for(scenario):
            cat, num = M.feature_columns(arm, history=history, launch_age=launch)
            for seed in TREE_SEEDS:
                start = time.time()
                staged = {k: [] for k in CHECKPOINTS}
                for train, ev in frames:
                    model = M.fit(train, cat, num, loss, iterations=MAX_TREES, seed=seed)
                    for k in CHECKPOINTS:
                        staged[k].append(M.predict(model, ev, cat, num, ntree_end=k))
                for k in CHECKPOINTS:
                    pred = np.mean(staged[k], axis=0)
                    rows.append({"scenario": scenario, "fold": fold, "arm": arm, "seed": seed, "trees": k,
                                 **metrics.summarize(actual, pred)})
                print(f"{scenario} {arm} seed {seed}: {time.time() - start:.0f}s, "
                      f"WAPE@500={rows[-4]['WAPE']:.3f}", flush=True)
        pd.DataFrame(rows).to_csv(TREES_OUT, index=False)
    print("written", TREES_OUT.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--studies", nargs="+", default=["model_seeds", "fold_seeds", "placebo"], choices=STUDIES)
    parser.add_argument("--scenarios", nargs="+", default=None, choices=list(E.SCENARIOS))
    args = parser.parse_args()
    ds = data.load_processed("teva")
    year = PR.ROBUSTNESS_TEST_YEAR

    def pick(default):
        if not args.scenarios:
            return default
        dropped = [s for s in args.scenarios if s not in default]
        if dropped:
            print("not part of this study:", " ".join(dropped))
        return [s for s in default if s in args.scenarios]

    if "trees" in args.studies:
        tree_curves(ds, pick(["A", "B", "C", "N"]))
    if not set(args.studies) - {"trees"}:
        return
    loss, table = PR.cycle_loss(ds, year)
    if "model_seeds" in args.studies:
        # Seed 42 is the rolling run itself (all arms, same folds); it is run here if missing.
        for seed in PR.MODEL_SEEDS:
            stage = "rolling" if seed == config.SEED else "model_seeds"
            for scenario in pick(PR.ROBUSTNESS_SCENARIOS):
                arms = E.arms_for(scenario) if stage == "rolling" else M.ARMS
                PR.execute(ds, stage, scenario, year, loss, arms, model_seed=seed, loss_table=table)
    if "fold_seeds" in args.studies:
        for seed in PR.FOLD_SEEDS:
            for scenario in pick(PR.FOLD_SCENARIOS):
                PR.execute(ds, "fold_seeds", scenario, year, loss, M.ARMS, fold_seed=seed,
                           fold_method="random_order", loss_table=table)
    if "placebo" in args.studies:
        # The INN + ATC arm (pre-specified) and the arm(s) the rolling run selected on validation.
        for scenario in pick(PR.PLACEBO_SCENARIOS):
            rolling = PR.execute(ds, "rolling", scenario, year, loss, E.arms_for(scenario), loss_table=table)
            arms = sorted(set(rolling["selected_arm_by_fold"].values()) | {PR.PLACEBO_ARM}, key=M.ARMS.index)
            for seed in PR.PLACEBO_SEEDS:
                PR.execute(ds, "placebo", scenario, year, loss, arms, placebo_seed=seed, loss_table=table)
    PR.log("robustness studies done: " + " ".join(args.studies))


if __name__ == "__main__":
    main()
