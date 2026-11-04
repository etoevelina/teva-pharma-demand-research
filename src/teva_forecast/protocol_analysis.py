"""Tables and figures of the rolling, validation-selected protocol and its robustness studies.

Everything is computed from the saved predictions and run records in results/protocol/:
the selected arm and the calibration factor are read from the run record, which stores the
choices made on the validation year before the test models were fit.
"""
import json
import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config, metrics
from . import plotting as P
from .analysis import SCENARIO_SHORT
from .experiments import BOOTSTRAP_CLUSTER
from .modeling import ARM_LABELS, ARMS
from .protocol import CONTROL_ARM, PLACEBO_ARM, PROTOCOL_DIR, ROBUSTNESS_TEST_YEAR, scores

SCENARIOS = ["A", "B", "C", "D", "D1", "N", "N0"]
SHORT = {**SCENARIO_SHORT, "N": "N: launches, launch month known (retrospective)",
         "N0": "N0: launch cohort, launch month unknown"}
BASELINES = {
    "A": ["naive", "seasonal_naive", "moving_average_12", "hierarchical_median", "calibrated_median"],
    "N": ["hierarchical_median", "calibrated_median", "launch_age_mean"],
    "N0": ["hierarchical_median", "calibrated_median", "launch_cohort_mean"],
}
COLD_BASELINES = ["global_mean", "form_mean", "hierarchical_mean", "hierarchical_median", "calibrated_median"]
MODEL_LABELS = {
    "naive": "Naive (last month)", "seasonal_naive": "Seasonal naive", "moving_average_12": "Moving average (12)",
    "global_mean": "Global mean", "form_mean": "Form mean", "hierarchical_mean": "Hierarchical group mean",
    "hierarchical_median": "Hierarchical group median", "calibrated_median": "Calibrated hierarchical median",
    "launch_age_mean": "Launch-age mean", "launch_cohort_mean": "Launch-cohort mean", "zero_forecast": "Zero forecast",
    **{f"catboost_{a}": f"CatBoost, {label}" for a, label in ARM_LABELS.items()},
}


def baselines_for(scenario):
    return BASELINES.get(scenario, COLD_BASELINES)


# --- Loading --------------------------------------------------------------------------------

def load_records(stage):
    folder = PROTOCOL_DIR / stage
    return [json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))] if folder.exists() else []


def load_frame(record, split):
    d = pd.read_parquet(PROTOCOL_DIR / record["stage"] / f"{record['run_id']}_{split}.parquet")
    float_cols = d.select_dtypes("float32").columns
    d[float_cols] = d[float_cols].astype(float)
    return d.assign(zero_forecast=0.0)


def load_attrs():
    return pd.read_parquet(config.PROCESSED_DIR / "teva_sku_attributes.parquet")[
        ["sku", "inn_unit", "atc1", "atc2", "twin_cluster", "first_t"]]


def _cluster_frame(frame, scenario, attrs):
    cluster = BOOTSTRAP_CLUSTER[scenario]
    return frame if cluster in frame else frame.merge(attrs[["sku", cluster]], on="sku", how="left")


def _compare(frame, scenario, attrs, pred_a, pred_b, n_boot=config.BOOTSTRAP_SAMPLES):
    """Paired cluster bootstrap of the relative WAPE change of pred_a against pred_b."""
    b = metrics.bootstrap_wape_difference(_cluster_frame(frame, scenario, attrs), BOOTSTRAP_CLUSTER[scenario],
                                          pred_a, pred_b, n_boot=n_boot)
    return {"rel": b["rel"], "rel_lo": b["rel_lo"], "rel_hi": b["rel_hi"], "p_not_better": b["p_a_not_better"]}


def _metric_row(frame, col):
    s = scores(frame, col)
    return {"WAPE": s["WAPE"], "bias": s["bias"], "spearman": s["spearman"], "MAE": s["MAE"], "RMSE": s["RMSE"],
            "WAPE_annual": s["WAPE_annual"], "n": s["n"], "skus": s["skus"]}


# --- Rolling protocol -----------------------------------------------------------------------

SELECTED = "catboost_selected"   # per fold, the metadata arm chosen on the validation results of other folds


def _by_fold(choice):
    return " ".join(f"{k}:{v}" for k, v in sorted(choice.items()))


def _selected_label(r):
    arms = sorted(set(r["selected_arm_by_fold"].values()))
    return arms[0] if len(arms) == 1 else "mixed (" + _by_fold(r["selected_arm_by_fold"]) + ")"


def rolling_tables(records, attrs):
    """rolling_year_results (every model and split), validation_selected_models, calibrated_baselines."""
    long, selected, calibrated = [], [], []
    for r in records:
        s, year, arm = r["scenario"], r["test_year"], r["selected_arm"]
        frames = {split: load_frame(r, split) for split in ("validation", "test")}
        models = baselines_for(s) + ["zero_forecast"] + [f"catboost_{a}" for a in r["arms"]] + [SELECTED]
        for split, d in frames.items():
            for col in models:
                a = col.removeprefix("catboost_")
                role = ("primary: control" if a == CONTROL_ARM else "primary: validation-selected metadata arm"
                        if col == SELECTED else "exploratory arm" if col.startswith("catboost_") else "baseline")
                long.append({"scenario": s, "test_year": year, "selection_year": r["selection_year"], "split": split,
                             "eval_year": r["selection_year"] if split == "validation" else year, "model": col,
                             "role": role, **_metric_row(d, col)})
        val, tst = frames["validation"], frames["test"]
        ctl = f"catboost_{CONTROL_ARM}"
        cmp = _compare(tst, s, attrs, SELECTED, ctl)
        vm = pd.DataFrame(r["validation_metrics"]).set_index("arm")["WAPE"]
        test_wape = {a: metrics.wape(tst["sales"], tst[f"catboost_{a}"]) for a in r["arms"] if a != CONTROL_ARM}
        selected.append({
            "scenario": s, "selection_year": r["selection_year"], "test_year": year,
            "selected_arm": _selected_label(r), "selected_arm_pooled_validation": arm,
            "selected_arm_by_fold": _by_fold(r["selected_arm_by_fold"]),
            "validation_WAPE": vm[arm], "test_WAPE": metrics.wape(tst["sales"], tst[SELECTED]),
            "bias": metrics.bias(tst["sales"], tst[SELECTED]), "spearman": scores(tst, SELECTED)["spearman"],
            "control_validation_WAPE": vm[CONTROL_ARM],
            "control_test_WAPE": metrics.wape(tst["sales"], tst[ctl]), "control_bias": metrics.bias(tst["sales"], tst[ctl]),
            "control_spearman": scores(tst, ctl)["spearman"],
            "rel_change_vs_control": cmp["rel"], "rel_change_lo": cmp["rel_lo"], "rel_change_hi": cmp["rel_hi"],
            "p_not_better_than_control": cmp["p_not_better"],
            "selected_beats_control_on_validation": bool(vm[arm] < vm[CONTROL_ARM]),
            "test_best_arm_exploratory": min(test_wape, key=test_wape.get),
            "loss": r["loss"], "calibration_factor_by_fold": _by_fold({k: round(v, 4) for k, v in r["calibration_factor_by_fold"].items()}),
            "run_id": r["run_id"],
        })
        for col in [ctl, SELECTED] + baselines_for(s) + ["zero_forecast"]:
            row = {"scenario": s, "test_year": year, "calibration_year": r["selection_year"], "model": col,
                   "label": "CatBoost control (no INN/ATC)" if col == ctl else
                   f"CatBoost, validation-selected ({_selected_label(r)})" if col == SELECTED else MODEL_LABELS[col],
                   **_metric_row(tst, col),
                   "calibration_factor_by_fold": _by_fold({k: round(v, 4) for k, v in r["calibration_factor_by_fold"].items()})}
            if col not in ("zero_forecast", "calibrated_median"):
                c = _compare(tst, s, attrs, col, "calibrated_median")
                row.update({"rel_vs_calibrated_median": c["rel"], "rel_lo": c["rel_lo"], "rel_hi": c["rel_hi"]})
            calibrated.append(row)
    return pd.DataFrame(long), pd.DataFrame(selected), pd.DataFrame(calibrated)


# --- Robustness -----------------------------------------------------------------------------

def _seed_runs(records, seed_key, primary):
    """One row per run, scenario and arm, plus the arm re-selected on each run's own validation year."""
    rows = []
    for r in records:
        if r["test_year"] != ROBUSTNESS_TEST_YEAR:
            continue
        tst = load_frame(r, "test")
        ctl = metrics.wape(tst["sales"], tst[f"catboost_{CONTROL_ARM}"])
        arms = [a for a in ARMS if a in r["arms"]]
        for arm in arms + ["validation_selected"]:
            col = SELECTED if arm == "validation_selected" else f"catboost_{arm}"
            w = metrics.wape(tst["sales"], tst[col])
            rows.append({"scenario": r["scenario"], seed_key: r[seed_key], "arm": arm,
                         "selected_arm_this_run": _selected_label(r),
                         "primary_selected_arm": primary.get(r["scenario"]),
                         "WAPE": w, "bias": metrics.bias(tst["sales"], tst[col]), "spearman": scores(tst, col)["spearman"],
                         "control_WAPE": ctl, "diff_vs_control": w - ctl, "rel_vs_control": w / ctl - 1,
                         "fold_method": r["fold_method"], "run_id": r["run_id"]})
    return pd.DataFrame(rows)


def summarize_runs(runs, seed_key):
    g = runs.groupby(["scenario", "arm"], sort=False)
    out = g.agg(n_runs=(seed_key, "nunique"), WAPE_mean=("WAPE", "mean"), WAPE_std=("WAPE", "std"),
                WAPE_min=("WAPE", "min"), WAPE_max=("WAPE", "max"), bias_mean=("bias", "mean"),
                spearman_mean=("spearman", "mean"), diff_vs_control_mean=("diff_vs_control", "mean"),
                diff_vs_control_std=("diff_vs_control", "std"), rel_vs_control_mean=("rel_vs_control", "mean"),
                rel_vs_control_min=("rel_vs_control", "min"), rel_vs_control_max=("rel_vs_control", "max"),
                ).reset_index()
    better = runs.assign(better=runs["diff_vs_control"] < 0).groupby(["scenario", "arm"], sort=False)["better"].sum()
    out["n_runs_better_than_control"] = better.to_numpy().astype(float)
    out.loc[out["arm"] == CONTROL_ARM, "n_runs_better_than_control"] = np.nan
    prim = runs.drop_duplicates("scenario").set_index("scenario")["primary_selected_arm"]
    out["is_primary_selected_arm"] = out["arm"] == out["scenario"].map(prim)
    sel = runs[runs["arm"] == "validation_selected"].groupby("scenario")["selected_arm_this_run"].agg(
        lambda x: "; ".join(f"{a} x{int((x == a).sum())}" for a in sorted(set(x))))
    out["selections"] = np.where(out["arm"] == "validation_selected", out["scenario"].map(sel), "")
    return out


def _primary(rolling):
    return {r["scenario"]: _selected_label(r) for r in rolling if r["test_year"] == ROBUSTNESS_TEST_YEAR}


def model_seed_tables(rolling, seeds):
    base = [r for r in rolling if r["test_year"] == ROBUSTNESS_TEST_YEAR and r["model_seed"] == config.SEED]
    runs = _seed_runs(base + seeds, "model_seed", _primary(rolling))
    return runs, summarize_runs(runs, "model_seed")


def fold_seed_tables(rolling, folds):
    runs = _seed_runs(folds, "fold_seed", _primary(rolling))
    summary = summarize_runs(runs, "fold_seed")
    reference = _seed_runs([r for r in rolling if r["test_year"] == ROBUSTNESS_TEST_YEAR
                            and r["scenario"] in set(runs["scenario"])], "fold_seed", _primary(rolling))
    ref = reference.set_index(["scenario", "arm"])["WAPE"] if len(reference) else pd.Series(dtype=float)
    summary["primary_assignment_WAPE"] = [ref.get((s, a), np.nan) for s, a in zip(summary["scenario"], summary["arm"])]
    return runs, summary


def placebo_tables(rolling, placebo, attrs):
    """Control, true peers and shuffled peers on the same rows, folds and CatBoost seed.

    Two metadata configurations are compared: the INN + ATC arm (pre-specified) and the
    validation-selected arm of the rolling run, whose shuffled version uses the same per-fold
    arm choice applied to the shuffled forecasts.
    """
    true = {r["scenario"]: r for r in rolling if r["test_year"] == ROBUSTNESS_TEST_YEAR and r["model_seed"] == config.SEED}
    missing = sorted({r["scenario"] for r in placebo} - set(true))
    if missing:
        print("placebo runs without a rolling test-2023 reference, skipped:", " ".join(missing))
    rows = []
    for r in [r for r in placebo if r["scenario"] in true]:
        s, ref_record = r["scenario"], true[r["scenario"]]
        ref, shuffled = load_frame(ref_record, "test"), load_frame(r, "test")
        arms_of_fold = {int(k): v for k, v in ref_record["selected_arm_by_fold"].items()}
        shuffled_cols = {f"catboost_{a}": f"shuffled_{a}" for a in r["arms"]}
        m = ref.merge(shuffled[["sku", "t"] + list(shuffled_cols)].rename(columns=shuffled_cols), on=["sku", "t"],
                      validate="one_to_one")
        assert len(m) == len(ref) == len(shuffled), "placebo and true runs must forecast the same rows"
        arm_of_row = m["fold"].map(arms_of_fold)
        m["shuffled_selected"] = np.select([arm_of_row == a for a in arms_of_fold.values()],
                                           [m[f"shuffled_{a}"] for a in arms_of_fold.values()])
        diag = [f["placebo_diagnostics"]["eval"] for f in r["fits"] if f["split"] == "test" and "placebo_diagnostics" in f]
        for config_name, true_col, shuf_col in (("INN + ATC", f"catboost_{PLACEBO_ARM}", f"shuffled_{PLACEBO_ARM}"),
                                                ("validation-selected", SELECTED, "shuffled_selected")):
            for label, col in (("control", f"catboost_{CONTROL_ARM}"), ("true peers", true_col), ("shuffled peers", shuf_col)):
                row = {"scenario": s, "placebo_seed": r["placebo_seed"], "configuration": config_name,
                       "selected_arm": _selected_label(ref_record) if config_name == "validation-selected" else PLACEBO_ARM,
                       "model": label, **_metric_row(m, col)}
                if label != "control":
                    c = _compare(m, s, attrs, col, f"catboost_{CONTROL_ARM}")
                    row.update({"rel_vs_control": c["rel"], "rel_lo": c["rel_lo"], "rel_hi": c["rel_hi"]})
                rows.append(row)
            c = _compare(m, s, attrs, true_col, shuf_col)
            rows.append({"scenario": s, "placebo_seed": r["placebo_seed"], "configuration": config_name,
                         "model": "true vs shuffled", "rel_true_vs_shuffled": c["rel"], "rel_lo": c["rel_lo"],
                         "rel_hi": c["rel_hi"], "p_true_not_better_than_shuffled": c["p_not_better"]})
        if diag:
            for g in diag[0]:
                rows.append({"scenario": s, "placebo_seed": r["placebo_seed"], "configuration": "diagnostics",
                             "model": f"feature check: {g}", **{k: float(np.mean([d[g][k] for d in diag])) for k in diag[0][g]}})
    runs = pd.DataFrame(rows)
    if not len(runs):
        return runs, runs
    per = runs[runs["model"].isin(["control", "true peers", "shuffled peers"])]
    out = []
    for (s, conf), d in per.groupby(["scenario", "configuration"], sort=False):
        w = d.pivot_table(index="placebo_seed", columns="model", values="WAPE")
        sh, tr = d[d["model"] == "shuffled peers"], d[d["model"] == "true peers"]
        out.append({"scenario": s, "configuration": conf, "arm": tr["selected_arm"].iloc[0],
                    "control_WAPE": w["control"].iloc[0], "true_WAPE": w["true peers"].iloc[0],
                    "shuffled_WAPE_mean": w["shuffled peers"].mean(), "shuffled_WAPE_std": w["shuffled peers"].std(),
                    "shuffled_WAPE_min": w["shuffled peers"].min(), "shuffled_WAPE_max": w["shuffled peers"].max(),
                    "n_seeds": len(w), "n_seeds_true_better_than_shuffled": int((w["true peers"] < w["shuffled peers"]).sum()),
                    "n_seeds_shuffled_better_than_control": int((w["shuffled peers"] < w["control"]).sum()),
                    "true_bias": tr["bias"].iloc[0], "shuffled_bias_mean": sh["bias"].mean(),
                    "true_spearman": tr["spearman"].iloc[0], "shuffled_spearman_mean": sh["spearman"].mean(),
                    "true_rel_vs_control": w["true peers"].iloc[0] / w["control"].iloc[0] - 1,
                    "shuffled_rel_vs_control_mean": w["shuffled peers"].mean() / w["control"].iloc[0] - 1})
    return runs, pd.DataFrame(out)


def n_vs_n0(rolling, attrs):
    """The same launch cohort with (N) and without (N0) knowledge of the launch month."""
    rows = []
    by = {(r["scenario"], r["test_year"]): r for r in rolling}
    first_t = attrs.set_index("sku")["first_t"]
    for year in sorted({r["test_year"] for r in rolling}):
        if ("N", year) not in by or ("N0", year) not in by:
            continue
        n, n0 = load_frame(by[("N", year)], "test"), load_frame(by[("N0", year)], "test")
        post = n0[n0["t"].to_numpy() >= n0["sku"].map(first_t).to_numpy()]
        assert set(n["sku"]) == set(n0["sku"]), "N and N0 must evaluate the same cohort"
        for scen, label, d, rec in (("N", "N: months from launch, launch month and age known", n, by[("N", year)]),
                                    ("N0", "N0: all 12 months, launch month unknown", n0, by[("N0", year)]),
                                    ("N0", "N0 forecasts scored on N's months (from launch)", post, by[("N0", year)])):
            for col in [f"catboost_{CONTROL_ARM}", SELECTED, "catboost_both"] + baselines_for(scen) + ["zero_forecast"]:
                rows.append({"test_year": year, "scenario": scen, "evaluation": label, "model": col,
                             "selected_arm": _selected_label(rec) if col == SELECTED else "",
                             "actual_total": float(d["sales"].sum()), **_metric_row(d, col)})
    return pd.DataFrame(rows)


def variability_summary(model_seed_summary, fold_seed_summary, placebo_summary):
    parts = []
    for name, t in (("model seeds", model_seed_summary), ("fold seeds", fold_seed_summary)):
        if len(t):
            parts.append(t.assign(source=name)[["source", "scenario", "arm", "n_runs", "WAPE_mean", "WAPE_std",
                                                "WAPE_min", "WAPE_max", "bias_mean", "spearman_mean",
                                                "rel_vs_control_mean", "rel_vs_control_min", "rel_vs_control_max",
                                                "n_runs_better_than_control"]])
    if len(placebo_summary):
        p = placebo_summary
        parts.append(pd.DataFrame({
            "source": "placebo seeds", "scenario": p["scenario"], "arm": "shuffled " + p["configuration"] + " (" + p["arm"] + ")",
            "n_runs": p["n_seeds"],
            "WAPE_mean": p["shuffled_WAPE_mean"], "WAPE_std": p["shuffled_WAPE_std"], "WAPE_min": p["shuffled_WAPE_min"],
            "WAPE_max": p["shuffled_WAPE_max"], "bias_mean": p["shuffled_bias_mean"],
            "spearman_mean": p["shuffled_spearman_mean"], "rel_vs_control_mean": p["shuffled_rel_vs_control_mean"],
            "n_runs_better_than_control": p["n_seeds_shuffled_better_than_control"]}))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def paper_table(selected, calibrated, model_seed_summary, fold_seed_summary, placebo_summary):
    """One row per scenario and test year: control, validation-selected arm, calibrated median, variability."""
    rows = []
    for _, r in selected.iterrows():
        s, year = r["scenario"], r["test_year"]
        cal = calibrated[(calibrated["scenario"] == s) & (calibrated["test_year"] == year)
                         & (calibrated["model"] == "calibrated_median")].iloc[0]
        row = {"scenario": s, "test_year": year, "selected_arm": r["selected_arm"],
               "control_WAPE": r["control_test_WAPE"], "control_bias": r["control_bias"], "control_spearman": r["control_spearman"],
               "selected_WAPE": r["test_WAPE"], "selected_bias": r["bias"], "selected_spearman": r["spearman"],
               "rel_change_vs_control": r["rel_change_vs_control"], "rel_change_lo": r["rel_change_lo"],
               "rel_change_hi": r["rel_change_hi"],
               "calibrated_median_WAPE": cal["WAPE"], "calibrated_median_bias": cal["bias"],
               "calibrated_median_spearman": cal["spearman"]}
        if year == ROBUSTNESS_TEST_YEAR:
            for name, t in (("model_seed", model_seed_summary), ("fold_seed", fold_seed_summary)):
                v = t[(t["scenario"] == s) & (t["arm"] == "validation_selected")] if len(t) else t
                if len(v):
                    row[f"{name}_selected_rel_mean"] = v["rel_vs_control_mean"].iloc[0]
                    row[f"{name}_selected_rel_min"] = v["rel_vs_control_min"].iloc[0]
                    row[f"{name}_selected_rel_max"] = v["rel_vs_control_max"].iloc[0]
                    row[f"{name}_runs_better"] = f"{int(v['n_runs_better_than_control'].iloc[0])}/{int(v['n_runs'].iloc[0])}"
            p = (placebo_summary[(placebo_summary["scenario"] == s) & (placebo_summary["configuration"] == "validation-selected")]
                 if len(placebo_summary) else placebo_summary)
            if len(p):
                row["placebo_true_rel"] = p["true_rel_vs_control"].iloc[0]
                row["placebo_shuffled_rel_mean"] = p["shuffled_rel_vs_control_mean"].iloc[0]
                row["placebo_true_better"] = f"{int(p['n_seeds_true_better_than_shuffled'].iloc[0])}/{int(p['n_seeds'].iloc[0])}"
        rows.append(row)
    return pd.DataFrame(rows)


# --- Figures --------------------------------------------------------------------------------

def _xticks(ax, scen):
    ax.set_xticks(range(len(scen)), [s + ":\n" + "\n".join(textwrap.wrap(SHORT[s].split(": ", 1)[1], 15)) for s in scen],
                  fontsize=7.5)


def fig_variability(model_runs, fold_runs):
    """Relative WAPE change of each metadata arm vs the control of the same run, per seed."""
    scen = [s for s in SCENARIOS if s in set(model_runs["scenario"])]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    offsets = {"inn": -0.27, "atc": -0.09, "both": 0.09, "validation_selected": 0.27}
    colors = {**P.ARM_COLORS, "validation_selected": P.INK}
    labels = {**ARM_LABELS, "validation_selected": "validation-selected arm"}
    for arm, off in offsets.items():
        for runs, marker, study in ((model_runs, "o", "model seeds"), (fold_runs, "^", "fold seeds")):
            t = runs[runs["arm"] == arm] if len(runs) else runs
            if not len(t):
                continue
            x = t["scenario"].map({s: i for i, s in enumerate(scen)}).to_numpy() + off + (-0.035 if marker == "o" else 0.035)
            ax.scatter(x, t["rel_vs_control"], s=16, marker=marker, color=colors[arm], alpha=0.8, linewidths=0,
                       label=f"{labels[arm]} ({study})")
    ax.axhline(0, color=P.INK_2, lw=0.9)
    _xticks(ax, scen)
    ax.yaxis.set_major_formatter(P.PERCENT)
    ax.set_ylabel("relative WAPE change vs CatBoost\ncontrol of the same run")
    ax.set_title(f"Variability over 5 CatBoost seeds (circles) and 5 fold assignments (triangles), test {ROBUSTNESS_TEST_YEAR}")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=7.5)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def fig_placebo(placebo_runs):
    per = placebo_runs[placebo_runs["model"].isin(["true peers", "shuffled peers"])]
    scen = [s for s in SCENARIOS if s in set(per["scenario"])]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
    for ax, conf in zip(axes, ("INN + ATC", "validation-selected")):
        c = per[per["configuration"] == conf]
        for label, off, color, marker in (("true peers", -0.12, P.ARM_COLORS["both"], "D"), ("shuffled peers", 0.12, P.MUTED, "o")):
            t = c[c["model"] == label].drop_duplicates(["scenario"] if label == "true peers" else ["scenario", "placebo_seed"])
            x = t["scenario"].map({s: i for i, s in enumerate(scen)}).to_numpy() + off
            ax.scatter(x, t["rel_vs_control"], s=26 if label == "true peers" else 16, marker=marker, color=color,
                       label=label + (" (5 permutation seeds)" if label == "shuffled peers" else ""), zorder=3)
        ax.axhline(0, color=P.INK_2, lw=0.9)
        _xticks(ax, scen)
        ax.yaxis.set_major_formatter(P.PERCENT)
        ax.set_title(f"{conf} arm")
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("relative WAPE change vs\nCatBoost control (no INN/ATC)")
    axes[1].legend(loc="best", fontsize=8)
    fig.suptitle(f"True versus shuffled INN/ATC peer statistics (test {ROBUSTNESS_TEST_YEAR})", x=0.01, ha="left",
                 fontweight="bold", fontsize=11)
    fig.tight_layout()
    return fig


def fig_selected_vs_calibrated(calibrated):
    years = sorted(set(calibrated["test_year"]))
    fig, axes = plt.subplots(1, len(years), figsize=(5.2 * len(years), 4.4), sharey=True, squeeze=False)
    kinds = [("control", "CatBoost control", P.MUTED, "o"), ("selected", "CatBoost, validation-selected arm", P.INK, "D"),
             ("hierarchical_median", "hierarchical median", P.SERIES[1], "s"),
             ("calibrated_median", "calibrated hierarchical median", P.SERIES[0], "^")]
    for ax, year in zip(axes[0], years):
        t = calibrated[calibrated["test_year"] == year]
        scen = [s for s in SCENARIOS if s in set(t["scenario"])]
        for k, (kind, label, color, marker) in enumerate(kinds):
            if kind == "control":
                v = t[t["model"] == f"catboost_{CONTROL_ARM}"]
            elif kind == "selected":
                v = t[t["label"].str.startswith("CatBoost, validation-selected")]
            else:
                v = t[t["model"] == kind]
            x = v["scenario"].map({s: i for i, s in enumerate(scen)}).to_numpy() + (k - 1.5) * 0.15
            ax.scatter(x, v["WAPE"], marker=marker, color=color, s=24, label=label, zorder=3)
        ax.set_xticks(range(len(scen)), scen)
        ax.set_title(f"Test {year} (choices made on {year - 1})")
        ax.set_ylabel("WAPE (monthly)")
        ax.grid(axis="x", visible=False)
    axes[0][-1].legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
    fig.tight_layout()
    return fig


# --- Generated results summary ----------------------------------------------------------------

def _md(df, floatfmt=".3f"):
    return df.to_markdown(index=False, floatfmt=floatfmt)


def _pct(x):
    return "n/a" if pd.isna(x) else f"{x:+.1%}"


def results_markdown(selected, calibrated, model_summary, fold_summary, placebo_summary, nn0, generated_by):
    """Markdown summary of the protocol results; every number is read from the tables passed in."""
    lines = ["# Validation-selected rolling protocol: results",
             "",
             f"*Generated by `{generated_by}` from `results/protocol/`; do not edit by hand. "
             "Method: [evaluation_protocol.md](evaluation_protocol.md).*",
             ""]
    sel = selected.copy()
    sel["CI"] = [f"[{_pct(lo)}, {_pct(hi)}]" for lo, hi in zip(sel["rel_change_lo"], sel["rel_change_hi"])]
    better = sel["rel_change_hi"] < 0
    worse = sel["rel_change_lo"] > 0
    lines += ["## 1. Primary result: validation-selected metadata arm against the control", "",
              f"Scenario-years: {len(sel)}. The selected arm has a lower test WAPE than the control in "
              f"{int((sel['rel_change_vs_control'] < 0).sum())}; the 95% cluster-bootstrap interval of the relative "
              f"change lies entirely below zero in {int(better.sum())} and entirely above zero in {int(worse.sum())}. "
              f"The selected arm equals the arm that would have been best on the test year in "
              f"{int((sel['selected_arm'] == sel['test_best_arm_exploratory']).sum())} of {len(sel)}.", "",
              _md(sel[["scenario", "selection_year", "test_year", "selected_arm", "selected_arm_by_fold", "validation_WAPE",
                       "control_validation_WAPE",
                       "test_WAPE", "control_test_WAPE", "rel_change_vs_control", "CI", "bias", "spearman",
                       "test_best_arm_exploratory"]]), ""]
    cal = calibrated[["scenario", "test_year", "label", "WAPE", "bias", "spearman", "calibration_factor_by_fold"]]
    lines += ["## 2. Calibrated hierarchical median and other baselines (test years)", "", _md(cal), ""]
    if len(model_summary):
        lines += ["## 3. CatBoost seeds (5 seeds, test 2023)", "",
                  _md(model_summary[["scenario", "arm", "n_runs", "WAPE_mean", "WAPE_std", "WAPE_min", "WAPE_max",
                                     "bias_mean", "spearman_mean", "rel_vs_control_mean", "rel_vs_control_min",
                                     "rel_vs_control_max", "n_runs_better_than_control", "selections"]], ".4f"), ""]
    if len(fold_summary):
        lines += ["## 4. Grouped-fold seeds (5 random-order assignments, test 2023)", "",
                  _md(fold_summary[["scenario", "arm", "n_runs", "WAPE_mean", "WAPE_std", "WAPE_min", "WAPE_max",
                                    "bias_mean", "spearman_mean", "rel_vs_control_mean", "rel_vs_control_min",
                                    "rel_vs_control_max", "n_runs_better_than_control", "selections",
                                    "primary_assignment_WAPE"]], ".4f"), ""]
    if len(placebo_summary):
        lines += ["## 5. Shuffled-peer placebo (5 permutation seeds, test 2023; D1 not applicable)", "",
                  _md(placebo_summary, ".4f"), ""]
    if len(nn0):
        cols = ["test_year", "evaluation", "model", "selected_arm", "WAPE", "bias", "spearman", "WAPE_annual", "n", "skus"]
        lines += ["## 6. Launch month known (N) versus unknown (N0)", "", _md(nn0[cols]), ""]
    return "\n".join(lines) + "\n"
