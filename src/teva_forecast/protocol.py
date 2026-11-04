"""Rolling, validation-selected evaluation protocol and its robustness studies.

Cycle for a test year Y (forecast origin December of Y-1):

* validation: train on the target years 2020..Y-2, early-stop every model on Y-1 and select, on
  Y-1 only, the loss, the tree counts, the primary metadata arm and the median calibration factor;
* test: retrain on 2020..Y-1 with the validation tree counts and forecast Y.

Y = 2023 is the original split (train 2020-2021, validation 2022; retrain 2020-2022, test 2023).
Y = 2022 trains its validation models on 2020 alone: 2020 is the first target year whose origin
(December 2019) has 12 months of history, so no earlier year can be added without using months
before 2019-01. Nothing from the test year enters a choice made for it: every selection function
receives validation-year predictions only, and the test models are fit after all choices are made.

Robustness studies (test year 2023): CatBoost seeds with fixed data and folds; grouped-fold seeds
with a fixed CatBoost seed; and a shuffled-peer placebo, in which the INN and ATC peer statistics
of every product are replaced by those of another group (features.placebo_permutation).
"""
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd

from . import baselines as B
from . import config, metrics
from . import experiments as E
from . import features as F

TEST_YEARS = (2022, 2023)
FIRST_TRAIN_YEAR = 2020
CONTROL_ARM = "none"
METADATA_ARMS = ["inn", "atc", "both"]
PLACEBO_ARM = "both"
MODEL_SEEDS = [42, 7, 2024, 11, 99]
FOLD_SEEDS = [42, 7, 2024, 11, 99]
PLACEBO_SEEDS = [1, 2, 3, 4, 5]
ROBUSTNESS_TEST_YEAR = 2023
ROBUSTNESS_SCENARIOS = ["A", "B", "C", "D", "D1", "N", "N0"]
FOLD_SCENARIOS = ["B", "C", "D", "D1"]
# D1 is left out of the placebo: no INN or ATC group of its training or held-out products has donors,
# so the INN/ATC peer statistics are missing in every row and shuffling them changes nothing.
PLACEBO_SCENARIOS = ["A", "B", "C", "D", "N", "N0"]
ROLLING_ORDER = ["A", "N", "N0", "B", "C", "D", "D1"]
PROTOCOL_DIR = config.RESULTS_DIR / "protocol"
LOG_FILE = PROTOCOL_DIR / "run_log.txt"
PACKAGES = ["numpy", "pandas", "catboost", "scipy", "pyarrow", "matplotlib"]


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    PROTOCOL_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as fh:
        fh.write(line + "\n")


def cycle_splits(test_year):
    """Validation and test splits of the rolling cycle that forecasts `test_year`."""
    assert test_year - 2 >= FIRST_TRAIN_YEAR, "the validation model needs at least one training year"
    return {
        "validation": {"train_years": list(range(FIRST_TRAIN_YEAR, test_year - 1)), "eval_year": test_year - 1},
        "test": {"train_years": list(range(FIRST_TRAIN_YEAR, test_year)), "eval_year": test_year},
    }


# --- Metrics and choices made on the validation year ---------------------------------------

def scores(frame, col):
    """The study's metrics: monthly MAE / RMSE / WAPE / total bias and the SKU-level annual
    WAPE and Spearman correlation (same definitions as analysis.overall_metrics)."""
    a = frame.groupby("sku")[["sales", col]].sum()
    rho = a["sales"].corr(a[col], method="spearman") if a[col].nunique() > 1 else np.nan
    return {**metrics.summarize(frame["sales"], frame[col]), "WAPE_annual": metrics.wape(a["sales"], a[col]),
            "spearman": rho, "skus": int(frame["sku"].nunique())}


def frame_years(frame):
    """Calendar years of the target months in a prediction frame (t = 0 is 2019-01)."""
    return set((2019 + frame["t"].to_numpy() // 12).tolist())


def validation_metrics(val_frame, scenario, arms, test_year):
    """Validation scores of each arm; the evaluation year is read from the rows, not from a label."""
    years = frame_years(val_frame)
    assert years == {test_year - 1}, f"validation rows must all lie in {test_year - 1}, found {sorted(years)}"
    rows = [{"scenario": scenario, "split": "validation", "eval_year": test_year - 1, "arm": arm,
             **scores(val_frame, f"catboost_{arm}")} for arm in arms]
    return pd.DataFrame(rows)


def select_metadata_arm(val_metrics, test_year, candidates=METADATA_ARMS):
    """Primary metadata arm: lowest validation WAPE among the INN / ATC arms.

    Accepts validation-year metrics only; ties go to the earlier candidate (inn, atc, both).
    """
    assert (val_metrics["split"] == "validation").all(), "selection may only see validation metrics"
    assert (val_metrics["eval_year"] < test_year).all(), "selection may only see years before the test year"
    v = val_metrics[val_metrics["arm"].isin(candidates)].set_index("arm").reindex(candidates)
    assert v["WAPE"].notna().all(), "every candidate arm needs a validation score"
    return v["WAPE"].idxmin()


def calibration_factor(val_frame, test_year, col="hierarchical_median"):
    """Ratio of actual to forecast total of the hierarchical median on the validation year."""
    years = frame_years(val_frame)
    assert years and max(years) < test_year, f"calibration may only use years before {test_year}, found {sorted(years)}"
    total = float(val_frame[col].sum())
    return float(val_frame["sales"].sum()) / total if total > 0 else 1.0


def choice_folds(fold, val_folds):
    """Validation folds whose results a test fold may use: never its own held-out SKUs.

    With validation folds 0 and 1, test fold 0 uses fold 1, fold 1 uses fold 0 and the other folds
    use both. Scenarios with a single unit (A, N, N0) use it: in A the product's own history is an
    allowed input, and in N / N0 the validation and test launch cohorts are different SKUs.
    """
    if len(val_folds) == 1:
        return list(val_folds)
    return [f for f in val_folds if f != fold] if fold in val_folds else list(val_folds)


def validation_baselines(ds, scenario, units, split):
    """Validation-year actual and hierarchical-median totals of every unit (no model is fit)."""
    rows = []
    for fold, test, pool in units:
        _, ev = E.prepare_unit(ds, scenario, split["eval_year"], test, pool)
        base = F.build_frame(ds, ev, pool, with_launch_age=scenario == "N")
        med = B.cold_start_baselines(ds, base, pool)["hierarchical_median"]
        rows.append({"fold": fold, "actual": float(base["sales"].sum()), "median": float(med.sum())})
    return pd.DataFrame(rows)


def fold_calibration(totals, fold):
    """Calibration factor for a test fold from the validation totals of all other folds."""
    t = totals if len(totals) == 1 else totals[totals["fold"] != fold]
    return float(t["actual"].sum() / t["median"].sum()) if t["median"].sum() > 0 else 1.0


def choose_loss(table):
    """Lowest mean validation WAPE among losses whose total-volume bias stays within the limit in every scenario."""
    table = table.copy()
    table["eligible"] = table["bias"].abs() <= config.MAX_ABS_VALIDATION_BIAS
    ok = table.groupby("loss")["eligible"].all()
    mean_wape = table.groupby("loss")["WAPE"].mean()
    candidates = mean_wape[ok[ok].index] if ok.any() else mean_wape
    return candidates.idxmin(), table


def select_loss(ds, test_year, seed=None):
    """Choose the CatBoost loss on the validation year of the cycle (INN + ATC arm of A and fold 0 of B)."""
    split = cycle_splits(test_year)["validation"]
    rows = []
    for scenario in ("A", "B"):
        fold, test, pool = E.scenario_units(ds, scenario)[0]
        for loss in config.LOSS_CANDIDATES:
            out, info, _, _ = E.run_unit(ds, scenario, "validation", test, pool, loss, arms=["both"], fold=fold,
                                         split=split, seed=seed)
            s = metrics.summarize(out["sales"], out["catboost_both"])
            rows.append({"scenario": scenario, "fold": fold, "loss": loss, "eval_year": split["eval_year"],
                         "iterations": "/".join(str(r["iterations"]) for r in info), **s})
            log(f"loss selection test{test_year} {scenario} {loss}: validation WAPE={s['WAPE']:.4f}")
    loss, table = choose_loss(pd.DataFrame(rows))
    return loss, table


# --- One scenario of one cycle --------------------------------------------------------------

def run_cycle(ds, scenario, test_year, loss, arms, model_seed=config.SEED, fold_seed=config.SEED,
              fold_method="balanced", placebo_seed=None):
    """Validation, choices on the validation year, then the test-year forecasts of one scenario.

    Returns (validation predictions, test predictions, fit records, choices). Every choice (tree
    counts, metadata arm, calibration factor) is made before any test model is trained, and a
    test fold only uses validation results of other folds (choice_folds), so in the cold-start
    scenarios a held-out product never tunes its own forecast.
    """
    splits = cycle_splits(test_year)
    units = E.scenario_units(ds, scenario, fold_seed=fold_seed, fold_method=fold_method)
    opts = {"arms": arms, "seed": model_seed, "placebo_seed": placebo_seed, "peer_baselines": True}
    val_parts, val_iters, fits = [], {}, []
    # CatBoost validation on the first two folds of a cold-start scenario, or on the single unit of A / N / N0.
    for fold, test, pool in units[:2]:
        val, info, _, _ = E.run_unit(ds, scenario, "validation", test, pool, loss, fold=fold,
                                     split=splits["validation"], **opts)
        val_iters[fold] = {(r["arm"], r["half"]): r["iterations"] for r in info}
        val_parts.append(val)
        fits += info
    val_frame = pd.concat(val_parts, ignore_index=True)
    val_folds = sorted(val_iters)
    vm = validation_metrics(val_frame, scenario, arms, test_year)
    select = set(METADATA_ARMS) <= set(arms)
    totals = validation_baselines(ds, scenario, units, splits["validation"])
    selected_by_fold, factor_by_fold = {}, {}
    for fold, _, _ in units:
        use = choice_folds(fold, val_folds)
        if select:
            selected_by_fold[fold] = select_metadata_arm(
                validation_metrics(val_frame[val_frame["fold"].isin(use)], scenario, arms, test_year), test_year)
        factor_by_fold[fold] = fold_calibration(totals, fold)
    pooled_check = calibration_factor(val_frame, test_year)
    for fold in val_folds:   # the baseline-only totals must match the validation runs
        v = val_frame[val_frame["fold"] == fold]
        t = totals.set_index("fold").loc[fold]
        assert np.isclose(t["actual"], v["sales"].sum()) and np.isclose(t["median"], v["hierarchical_median"].sum())
    choices = {
        "selected_arm": select_metadata_arm(vm, test_year) if select else None,
        "selected_arm_by_fold": {str(k): v for k, v in selected_by_fold.items()},
        "calibration_factor": fold_calibration(totals, -1),
        "calibration_factor_by_fold": {str(k): v for k, v in factor_by_fold.items()},
        "calibration_factor_validation_folds": pooled_check,
        "validation_baseline_totals": totals.to_dict("records"),
        "validation_metrics": vm.to_dict("records"),
        "validation_iterations": {str(k): {f"{a}|{h}": int(n) for (a, h), n in v.items()} for k, v in val_iters.items()},
    }

    test_parts = []
    for fold, test, pool in units:
        # Tree counts come from the validation run of another fold: fold 0 uses fold 1, every other fold uses fold 0.
        source = 1 if fold == 0 and 1 in val_iters else 0
        tst, info, _, _ = E.run_unit(ds, scenario, "test", test, pool, loss, iterations=val_iters[source],
                                     fold=fold, split=splits["test"], **opts)
        test_parts.append(tst)
        fits += info
    test_frame = pd.concat(test_parts, ignore_index=True)
    for frame in (val_frame, test_frame):
        frame["calibrated_median"] = frame["fold"].map(factor_by_fold) * frame["hierarchical_median"]
        if select:
            arm_of_row = frame["fold"].map(selected_by_fold)
            frame["catboost_selected"] = np.select([arm_of_row == a for a in METADATA_ARMS],
                                                   [frame[f"catboost_{a}"] for a in METADATA_ARMS])
    return val_frame, test_frame, fits, choices


# --- Run records ----------------------------------------------------------------------------

def environment():
    """Code and software versions: git commit, uncommitted changes (tracked and untracked), source hash."""
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=config.ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    status = git("status", "--porcelain", "--", "src", "scripts", "tests", "requirements.txt")
    return {"git_commit": git("rev-parse", "HEAD"), "git_dirty": bool(status) if status is not None else None,
            "source_sha256": source_hash(), "python": sys.version.split()[0], "platform": platform.platform(),
            "packages": versions}


def source_hash():
    """SHA-256 over the Python sources of the package and the scripts (identifies the code that ran)."""
    h = hashlib.sha256()
    for path in sorted(list((config.ROOT / "src").rglob("*.py")) + list((config.ROOT / "scripts").glob("*.py"))):
        h.update(str(path.relative_to(config.ROOT)).encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def dataset_signature(ds):
    h = hashlib.sha256()
    h.update(ds.attrs["sku"].to_numpy().tobytes())
    h.update(np.nan_to_num(ds.sales, nan=-1.0).tobytes())
    return {"n_skus": int(len(ds.attrs)), "sha256": h.hexdigest()}


def fingerprint(ds, loss, arms, model_seed, fold_seed, fold_method, placebo_seed):
    """Everything that determines a run besides the code; a stored run is reused only if it matches."""
    return {"loss": loss, "arms": list(arms), "catboost_params": catboost_params(model_seed),
            "early_stopping_rounds": config.EARLY_STOPPING_ROUNDS, "n_folds": config.N_FOLDS,
            "model_seed": model_seed, "fold_seed": fold_seed, "fold_method": fold_method,
            "placebo_seed": placebo_seed, "dataset": dataset_signature(ds)}


def catboost_params(model_seed):
    """CatBoost parameters as passed to the models of a run (the seed is the run's model seed)."""
    return {**{k: v for k, v in config.CATBOOST_PARAMS.items() if k != "verbose"}, "random_seed": int(model_seed)}


def run_id(stage, scenario, test_year, model_seed, fold_seed, fold_method, placebo_seed):
    fold_tag = f"fs{fold_seed}" + ("r" if fold_method == "random_order" else "")
    return f"{stage}__{scenario}__test{test_year}__ms{model_seed}__{fold_tag}__ps{placebo_seed if placebo_seed is not None else 'none'}"


def _compact(frame, scenario):
    out = frame.drop(columns=[c for c in ("date", "i", "baseline_level") if c in frame]).copy()
    float_cols = out.select_dtypes("float").columns
    out[float_cols] = out[float_cols].astype("float32")
    out["t"] = out["t"].astype("int16")
    out["fold"] = out["fold"].astype("int8")
    out.insert(0, "scenario", scenario)
    return out


def _write_json(path, obj):
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=str))
    os.replace(tmp, path)


def execute(ds, stage, scenario, test_year, loss, arms, model_seed=config.SEED, fold_seed=config.SEED,
            fold_method="balanced", placebo_seed=None, loss_table=None):
    """Run one scenario of one cycle unless a matching record exists; save predictions and the run record.

    A stored run is reused only if its fingerprint (loss, arms, CatBoost parameters, seeds, fold
    method, data) equals the requested one and both prediction files exist; otherwise it raises,
    so stale results are never mixed into the tables.
    """
    rid = run_id(stage, scenario, test_year, model_seed, fold_seed, fold_method, placebo_seed)
    out_dir = PROTOCOL_DIR / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    record_path = out_dir / f"{rid}.json"
    fp = fingerprint(ds, loss, arms, model_seed, fold_seed, fold_method, placebo_seed)
    if record_path.exists():
        record = json.loads(record_path.read_text())
        files = [out_dir / f"{rid}_{split}.parquet" for split in ("validation", "test")]
        if record.get("fingerprint") != json.loads(json.dumps(fp, default=str)) or not all(f.exists() for f in files):
            raise RuntimeError(f"{record_path} does not match the requested run; delete it to rerun")
        log(f"{rid}: already done, skipped")
        return record
    start, started = time.time(), time.strftime("%Y-%m-%dT%H:%M:%S%z")
    env = environment()
    val, tst, fits, choices = run_cycle(ds, scenario, test_year, loss, arms, model_seed=model_seed,
                                        fold_seed=fold_seed, fold_method=fold_method, placebo_seed=placebo_seed)
    _compact(val, scenario).to_parquet(out_dir / f"{rid}_validation.parquet", index=False, compression="zstd")
    _compact(tst, scenario).to_parquet(out_dir / f"{rid}_test.parquet", index=False, compression="zstd")
    splits = cycle_splits(test_year)
    record = {
        "run_id": rid, "stage": stage, "scenario": scenario, "started": started,
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "seconds": round(time.time() - start, 1),
        **env,
        "catboost_params": catboost_params(model_seed),
        "early_stopping_rounds": config.EARLY_STOPPING_ROUNDS, "loss": loss,
        "model_seed": model_seed, "fold_seed": fold_seed, "fold_method": fold_method, "placebo_seed": placebo_seed,
        "placebo_arms": arms if placebo_seed is not None else None,
        "n_folds": config.N_FOLDS, "half_seed": config.SEED + 1,
        "validation_years": splits["validation"], "test_years": splits["test"],
        "selection_year": splits["validation"]["eval_year"], "test_year": test_year, "arms": arms,
        **choices,
        "fits": fits,
        "loss_selection": loss_table.to_dict("records") if loss_table is not None else None,
        "fingerprint": fp,
    }
    _write_json(record_path, record)
    sel = f", selected {choices['selected_arm']} (by fold {choices['selected_arm_by_fold']})" if choices["selected_arm"] else ""
    log(f"{rid}: done in {record['seconds']:.0f}s{sel}, calibration factor {choices['calibration_factor']:.3f}, test WAPE "
        + ", ".join(f"{a}={metrics.wape(tst['sales'], tst[f'catboost_{a}']):.3f}" for a in arms))
    return record


def cycle_loss(ds, test_year):
    """Loss of a rolling cycle: chosen once on its validation year and stored next to the results."""
    path = PROTOCOL_DIR / f"loss_selection_test{test_year}.csv"
    if path.exists():
        table = pd.read_csv(path)
        assert set(table["eval_year"]) == {test_year - 1}, f"{path} was not chosen on {test_year - 1}"
        return choose_loss(table.drop(columns=["eligible"], errors="ignore"))[0], table
    loss, table = select_loss(ds, test_year)
    PROTOCOL_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False)
    log(f"loss for test{test_year}: {loss}")
    return loss, table
