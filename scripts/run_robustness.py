"""Robustness of the INN/ATC comparison to the number of trees and to the CatBoost random seed.

For every arm the test-year model (train 2020-2022, forecast 2023) is refit with a fixed, large number
of trees and three seeds, and the test error is read at several tree counts. This shows whether the
ordering of the arms depends on the tree count chosen on the (shock) validation year. Cold-start
scenarios use their first fold and both cross-fitting halves. The results are descriptive: nothing
here feeds back into model selection.

Usage: python scripts/run_robustness.py [--scenarios A B C N]
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import config, data, experiments as E, features as F, metrics, modeling as M  # noqa: E402

MAX_TREES = 1200
CHECKPOINTS = [100, 200, 300, 500, 750, 1000, 1200]
SEEDS = [42, 7, 2024]
OUT = config.TABLES_DIR / "robustness_trees_seeds.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", nargs="+", default=["A", "B", "C", "N"])
    args = parser.parse_args()
    ds = data.load_processed("teva")
    loss = pd.read_csv(config.TABLES_DIR / "runs.csv")["loss"].iloc[0]
    split = E.SPLITS["test"]
    rows = []
    for scenario in args.scenarios:
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
            for seed in SEEDS:
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
        pd.DataFrame(rows).to_csv(OUT, index=False)
    print("written", OUT.name)


if __name__ == "__main__":
    main()
