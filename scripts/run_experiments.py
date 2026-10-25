"""Run the loss selection and all scenario experiments; write predictions, run logs and models.

Usage:
    python scripts/run_experiments.py                    # everything (about 1.5 h on 8 free CPU cores)
    python scripts/run_experiments.py --scenarios A B    # a subset
    python scripts/run_experiments.py --loss "Tweedie:variance_power=1.5"   # skip loss selection
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import config, data, experiments as E, metrics  # noqa: E402

LOSS_FILE = config.TABLES_DIR / "loss_selection.csv"
RUNS_FILE = config.TABLES_DIR / "runs.csv"
IMPORTANCE_FILE = config.TABLES_DIR / "feature_importance.csv"
LOG_FILE = config.RESULTS_DIR / "run_log.txt"
DEFAULT_ORDER = ["A", "N", "B", "C", "D", "D1"]


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as fh:
        fh.write(line + "\n")


def choose_loss(table):
    """Lowest mean validation WAPE among losses whose total-volume bias stays within the limit in every scenario."""
    table = table.copy()
    table["eligible"] = table["bias"].abs() <= config.MAX_ABS_VALIDATION_BIAS
    ok = table.groupby("loss")["eligible"].all()
    mean_wape = table.groupby("loss")["WAPE"].mean()
    candidates = mean_wape[ok[ok].index] if ok.any() else mean_wape
    return candidates.idxmin(), table


def select_loss(ds):
    """Choose the CatBoost loss on the validation year (2022) only, using the INN + ATC arm of A and B."""
    rows = []
    for scenario in ("A", "B"):
        fold, test, pool = E.scenario_units(ds, scenario)[0]
        for loss in config.LOSS_CANDIDATES:
            out, info, _, _ = E.run_unit(ds, scenario, "validation", test, pool, loss, arms=["both"], fold=fold)
            s = metrics.summarize(out["sales"], out["catboost_both"])
            rows.append({"scenario": scenario, "fold": fold, "loss": loss,
                         "iterations": "/".join(str(r["iterations"]) for r in info), **s})
            log(f"loss selection {scenario} {loss}: WAPE={s['WAPE']:.4f}")
    loss, table = choose_loss(pd.DataFrame(rows))
    table.to_csv(LOSS_FILE, index=False)
    return loss


def merge_table(path, new, scenarios):
    if path.exists():
        old = pd.read_csv(path)
        old = old[~old["scenario"].isin(scenarios)]
        new = pd.concat([old, new], ignore_index=True)
    new.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", nargs="+", default=DEFAULT_ORDER, choices=list(E.SCENARIOS))
    parser.add_argument("--loss", default=None)
    args = parser.parse_args()

    for d in (config.TABLES_DIR, config.PREDICTIONS_DIR, config.MODELS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    ds = data.load_processed("teva")
    loss = args.loss or select_loss(ds)
    log(f"loss function: {loss}")

    all_info, all_imp = [], []
    for scenario in args.scenarios:
        units = E.scenario_units(ds, scenario)
        preds = {"validation": [], "test": []}
        # Validation (2022) on the first two folds of a cold-start scenario, or on the single unit of A and N.
        val_iters = {}
        for fold, test, pool in units[:2]:
            val, info_v, _, _ = E.run_unit(ds, scenario, "validation", test, pool, loss, fold=fold)
            val_iters[fold] = {(r["arm"], r["half"]): r["iterations"] for r in info_v}
            preds["validation"].append(val)
            all_info += info_v
            log(f"{scenario} fold {fold}: validation WAPE " + ", ".join(
                f"{a}={metrics.wape(val['sales'], val[f'catboost_{a}']):.3f}" for a in E.arms_for(scenario)))
        for fold, test, pool in units:
            # Tree counts come from the validation run of another fold, so held-out SKUs never tune
            # their own models: fold 0 uses fold 1, every other fold uses fold 0.
            source = 1 if fold == 0 and 1 in val_iters else 0
            keep = scenario in ("A", "N") or fold == 0
            tst, info_t, models, imps = E.run_unit(ds, scenario, "test", test, pool, loss,
                                                   iterations=val_iters[source], fold=fold, keep_models=keep)
            preds["test"].append(tst)
            all_info += info_t
            all_imp += imps
            for (arm, half), model in models.items():
                model.save_model(str(config.MODELS_DIR / f"{scenario}_fold{fold}_{arm}_half{half}.cbm"))
            log(f"{scenario} fold {fold}: test WAPE " + ", ".join(
                f"{a}={metrics.wape(tst['sales'], tst[f'catboost_{a}']):.3f}" for a in E.arms_for(scenario)))
        for split, parts in preds.items():
            frame = pd.concat(parts, ignore_index=True)
            float_cols = frame.select_dtypes("float").columns
            frame[float_cols] = frame[float_cols].astype("float32")
            frame.insert(0, "scenario", scenario)
            frame.to_parquet(config.PREDICTIONS_DIR / f"{scenario}_{split}.parquet", index=False)
        merge_table(RUNS_FILE, pd.DataFrame([r for r in all_info if r["scenario"] == scenario]), [scenario])
        imp = [x for x in all_imp if x["scenario"].iloc[0] == scenario]
        if imp:
            merge_table(IMPORTANCE_FILE, pd.concat(imp, ignore_index=True), [scenario])

    runs = pd.read_csv(RUNS_FILE)
    params = {
        "catboost": {k: v for k, v in config.CATBOOST_PARAMS.items() if k != "verbose"},
        "loss_function": sorted(runs["loss"].unique().tolist()),
        "early_stopping_rounds": config.EARLY_STOPPING_ROUNDS,
        "protocol": {"validation": config.VALIDATION, "test": config.TEST},
        "test_iterations": runs[runs["split"] == "test"]
        .set_index(runs.loc[runs["split"] == "test", ["scenario", "fold", "arm", "half"]].astype(str).agg("_".join, axis=1))
        ["iterations"].astype(int).to_dict(),
    }
    (config.MODELS_DIR / "training_parameters.json").write_text(json.dumps(params, indent=2, default=str))
    log("done")


if __name__ == "__main__":
    main()
