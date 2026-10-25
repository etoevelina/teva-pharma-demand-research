"""Result tables, ablation statistics, error analysis and result figures."""
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import config, metrics
from . import plotting as P
from .experiments import BOOTSTRAP_CLUSTER, SCENARIOS, arms_for
from .modeling import ARM_LABELS, ARMS, CODES_ARM

SCENARIO_ORDER = ["A", "B", "C", "D", "D1", "N"]
SCENARIO_SHORT = {
    "A": "A: existing drug",
    "B": "B: new SKU, known INN",
    "C": "C: new INN, known ATC",
    "D": "D: unseen ATC2 group",
    "D1": "D1: unseen ATC1 group",
    "N": "N: real 2023 launches",
}
EXISTING_BASELINES = ["naive", "seasonal_naive", "moving_average_12"]
COLD_BASELINES = ["global_mean", "form_mean", "hierarchical_mean", "hierarchical_median"]
MODEL_LABELS = {
    "naive": "Naive (last month)",
    "seasonal_naive": "Seasonal naive",
    "moving_average_12": "Moving average (12)",
    "global_mean": "Global mean",
    "form_mean": "Form mean",
    "hierarchical_mean": "Hierarchical group mean",
    "hierarchical_median": "Hierarchical group median",
    "launch_age_mean": "Launch-age mean",
    "zero_forecast": "Zero forecast (reference)",
    **{f"catboost_{a}": f"CatBoost, {label}" for a, label in ARM_LABELS.items()},
}


def baselines_for(scenario):
    if scenario == "A":
        return EXISTING_BASELINES
    return COLD_BASELINES + (["launch_age_mean"] if scenario == "N" else [])


def model_columns(scenario):
    return baselines_for(scenario) + [f"catboost_{a}" for a in arms_for(scenario)]


def load_predictions(scenarios=SCENARIO_ORDER):
    out = {}
    attrs = pd.read_parquet(config.PROCESSED_DIR / "teva_sku_attributes.parquet")
    keep = ["sku", "inn", "inn_unit", "atc1", "atc2", "nfc", "twin_cluster", "twin_size", "first_sale"]
    for s in scenarios:
        for split in ("validation", "test"):
            path = config.PREDICTIONS_DIR / f"{s}_{split}.parquet"
            if path.exists():
                d = pd.read_parquet(path).merge(attrs[keep], on="sku", how="left")
                float_cols = d.select_dtypes("float32").columns
                d[float_cols] = d[float_cols].astype(float)
                out[(s, split)] = d
    return out


def _annual_scores(d, col):
    """WAPE and Spearman correlation of the SKU-level totals over the evaluated months."""
    a = d.groupby("sku")[["sales", col]].sum()
    rho = a["sales"].corr(a[col], method="spearman") if a[col].nunique() > 1 else np.nan
    return metrics.wape(a["sales"], a[col]), rho


def overall_metrics(preds):
    """Monthly MAE / RMSE / WAPE / bias plus SKU-level annual WAPE and rank correlation.

    Cold-start scenarios also get a zero forecast as a reference: its WAPE is exactly 1, so any
    unbiased forecast of very skewed new-product sales can exceed 1 while still being more useful.
    """
    rows = []
    for (s, split), d in preds.items():
        cols = model_columns(s)
        if s != "A":
            d = d.assign(zero_forecast=0.0)
            cols = cols + ["zero_forecast"]
        for col in cols:
            wape_annual, rho = _annual_scores(d, col)
            rows.append({"scenario": s, "split": split, "model": col, **metrics.summarize(d["sales"], d[col]),
                         "WAPE_annual": wape_annual, "spearman_annual": rho, "skus": int(d["sku"].nunique())})
    return pd.DataFrame(rows)


def fold_metrics(preds):
    rows = []
    for (s, split), d in preds.items():
        for fold, g in d.groupby("fold"):
            for col in model_columns(s):
                rows.append({"scenario": s, "split": split, "fold": fold, "model": col,
                             **metrics.summarize(g["sales"], g[col])})
    return pd.DataFrame(rows)


def best_baseline(overall, scenario):
    """Baseline chosen on the validation year only, with the same rule as the CatBoost loss:
    lowest WAPE among baselines whose total-volume bias stays within the limit."""
    v = overall[(overall["scenario"] == scenario) & (overall["split"] == "validation")
                & overall["model"].isin(baselines_for(scenario))]
    ok = v[v["bias"].abs() <= config.MAX_ABS_VALIDATION_BIAS]
    return (ok if len(ok) else v).sort_values("WAPE").iloc[0]["model"]


def ablation_table(preds, overall, n_boot=config.BOOTSTRAP_SAMPLES):
    """Paired cluster-bootstrap comparison of each arm against the no-INN/ATC arm and the best baseline."""
    rows = []
    for (s, split), d in preds.items():
        if split != "test":
            continue
        cluster = BOOTSTRAP_CLUSTER[s]
        ref_base = best_baseline(overall, s)
        for arm in arms_for(s):
            col = f"catboost_{arm}"
            vs_none = metrics.bootstrap_wape_difference(d, cluster, col, "catboost_none", n_boot=n_boot)
            vs_base = metrics.bootstrap_wape_difference(d, cluster, col, ref_base, n_boot=n_boot)
            m = metrics.summarize(d["sales"], d[col])
            rows.append({
                "scenario": s, "arm": arm, "WAPE": m["WAPE"], "MAE": m["MAE"], "RMSE": m["RMSE"], "bias": m["bias"],
                "dWAPE_vs_none": vs_none["diff"], "dWAPE_vs_none_lo": vs_none["diff_lo"],
                "dWAPE_vs_none_hi": vs_none["diff_hi"],
                "rel_vs_none": vs_none["rel"], "rel_vs_none_lo": vs_none["rel_lo"], "rel_vs_none_hi": vs_none["rel_hi"],
                "p_not_better_than_none": vs_none["p_a_not_better"],
                "best_baseline": ref_base, "baseline_WAPE": vs_base["wape_b"],
                "rel_vs_baseline": vs_base["rel"], "rel_vs_baseline_lo": vs_base["rel_lo"],
                "rel_vs_baseline_hi": vs_base["rel_hi"],
                "bootstrap_cluster": cluster, "clusters": vs_none["n_clusters"],
            })
    return pd.DataFrame(rows)


def _volume_bins(d):
    tot = d.groupby("sku")["sales"].sum()
    q = pd.qcut(tot.rank(method="first"), 5, labels=["Q1 (smallest)", "Q2", "Q3", "Q4", "Q5 (largest)"])
    return d["sku"].map(q)


def error_breakdowns(preds, overall):
    """WAPE by ATC1, dosage form, SKU volume quintile and scenario-specific factors (test year)."""
    out = {}
    frames = []
    for (s, split), d in preds.items():
        if split != "test":
            continue
        base = best_baseline(overall, s)
        cols = [base, "catboost_none", "catboost_both"]
        d = d.assign(volume_quintile=_volume_bins(d))
        for by in ["atc1", "nfc", "volume_quintile"]:
            g = metrics.grouped_metrics(d, by, cols)
            g = g.rename(columns={by: "group"})
            g.insert(0, "breakdown", by)
            g.insert(0, "scenario", s)
            frames.append(g)
        if "known_atc_depth" in d:
            g = metrics.grouped_metrics(d, "known_atc_depth", cols).rename(columns={"known_atc_depth": "group"})
            g.insert(0, "breakdown", "known_atc_depth")
            g.insert(0, "scenario", s)
            frames.append(g)
        if s == "N":
            attrs = pd.read_parquet(config.PROCESSED_DIR / "teva_sku_attributes.parquet")
            earlier = attrs[(attrs["first_t"] >= 0) & (attrs["first_sale"] < "2023-01-01")]
            hist_inn, older_twins = set(earlier["inn"].dropna()), set(earlier["twin_cluster"])
            d = d.assign(
                inn_seen=np.select([d["inn"].isna(), d["inn"].isin(hist_inn)],
                                   ["no INN", "INN sold before 2023"], "new INN"),
                twin=np.where(d["twin_cluster"].isin(older_twins), "has an older identical twin", "no older twin"),
                months_since_launch=d["age_at_target"].astype(int))
            for by in ["inn_seen", "twin", "months_since_launch"]:
                g = metrics.grouped_metrics(d, by, cols).rename(columns={by: "group"})
                g.insert(0, "breakdown", by)
                g.insert(0, "scenario", s)
                frames.append(g)
    out["breakdowns"] = pd.concat(frames, ignore_index=True)
    return out


def inn_errors(preds, scenario, model, top=20):
    d = preds[(scenario, "test")]
    g = d.assign(abs_err=(d["sales"] - d[model]).abs(), inn=d["inn"].fillna("(no INN)")).groupby("inn").agg(
        skus=("sku", "nunique"), actual=("sales", "sum"), predicted=(model, "sum"), abs_error=("abs_err", "sum"))
    g["WAPE"] = g["abs_error"] / g["actual"]
    g["share_of_total_error"] = g["abs_error"] / g["abs_error"].sum()
    return g.sort_values("abs_error", ascending=False).head(top).reset_index()


# --- Figures ----------------------------------------------------------------------------

def _model_color(col):
    if col.startswith("catboost_"):
        return P.ARM_COLORS[col.split("_", 1)[1]]
    return P.AXIS


def fig_overview(overall):
    scen = [s for s in SCENARIO_ORDER if ((overall["scenario"] == s) & (overall["split"] == "test")).any()]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    for ax, s in zip(axes.ravel(), scen):
        t = overall[(overall["scenario"] == s) & (overall["split"] == "test")].set_index("model").loc[model_columns(s)]
        y = np.arange(len(t))[::-1]
        ax.barh(y, t["WAPE"], color=[_model_color(c) for c in t.index], height=0.62)
        ax.set_yticks(y, [MODEL_LABELS[c] for c in t.index], fontsize=8)
        xmax = min(t["WAPE"].max(), 3.0) * 1.22
        for yy, v in zip(y, t["WAPE"]):
            ax.text(min(v, xmax / 1.22) + xmax * 0.01, yy, f"{v:.3f}", va="center", fontsize=7.5, color=P.INK_2)
        ax.set_xlim(0, xmax)
        if s != "A":
            ax.axvline(1.0, color=P.INK_2, lw=0.8, ls=(0, (3, 2)))
            ax.set_ylim(-1.3, len(t) - 0.4)
            ax.text(1.0, -0.95, " zero forecast = 1", fontsize=7, color=P.INK_2, va="center")
        ax.set_title(SCENARIO_SHORT[s], fontsize=10)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("WAPE, test 2023 (lower is better)", fontsize=8)
    for ax in axes.ravel()[len(scen):]:
        ax.set_visible(False)
    fig.tight_layout()
    return fig


def fig_ablation(ablation):
    scen = [s for s in SCENARIO_ORDER if s in set(ablation["scenario"])]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    offsets = {"inn": -0.27, "atc": -0.09, "both": 0.09, CODES_ARM: 0.27}
    markers = {CODES_ARM: "D"}
    for arm, off in offsets.items():
        t = ablation[ablation["arm"] == arm].set_index("scenario").reindex(scen)
        x = np.arange(len(scen)) + off
        keep = t["rel_vs_none"].notna().to_numpy()
        if not keep.any():
            continue
        marker, color = markers.get(arm, "o"), P.ARM_COLORS[arm]
        ax.errorbar(x[keep], t["rel_vs_none"][keep],
                    yerr=[(t["rel_vs_none"] - t["rel_vs_none_lo"])[keep], (t["rel_vs_none_hi"] - t["rel_vs_none"])[keep]],
                    fmt=marker, color=color, ms=6, capsize=3, lw=1.4, label=ARM_LABELS[arm],
                    markeredgecolor=P.SURFACE, markeredgewidth=1.2)
    ax.axhline(0, color=P.INK_2, lw=0.9)
    ax.set_xticks(range(len(scen)), [s + ":\n" + "\n".join(textwrap.wrap(SCENARIO_SHORT[s].split(": ", 1)[1], 14))
                                     for s in scen], fontsize=8)
    ax.yaxis.set_major_formatter(P.PERCENT)
    ax.set_ylabel("relative WAPE change vs\nCatBoost without INN/ATC")
    ax.set_title("Effect of INN and ATC features (test 2023, 95% cluster-bootstrap CI)")
    ax.legend(loc="best", ncols=2, fontsize=8)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def fig_actual_vs_predicted(preds, model="catboost_both"):
    scen = [s for s in SCENARIO_ORDER if (s, "test") in preds]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.6))
    for ax, s in zip(axes.ravel(), scen):
        d = preds[(s, "test")]
        x, y = np.log10(d["sales"] + 1), np.log10(d[model] + 1)
        hb = ax.hexbin(x, y, gridsize=45, bins="log", cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list(
            "seq", P.SEQUENTIAL), mincnt=1, linewidths=0)
        lim = max(x.max(), y.max()) * 1.02
        ax.plot([0, lim], [0, lim], color=P.INK_2, lw=0.9)
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_title(SCENARIO_SHORT[s], fontsize=10)
        ax.set_xlabel("actual, log10(packs + 1)", fontsize=8)
        ax.set_ylabel("predicted, log10(packs + 1)", fontsize=8)
        ax.grid(False)
        corr = np.corrcoef(x, y)[0, 1]
        ax.text(0.03, 0.95, f"r (log) = {corr:.2f}\nWAPE = {metrics.wape(d['sales'], d[model]):.3f}",
                transform=ax.transAxes, va="top", fontsize=8, color=P.INK_2)
    for ax in axes.ravel()[len(scen):]:
        ax.set_visible(False)
    cb = fig.colorbar(hb, ax=axes.ravel().tolist(), shrink=0.6)
    cb.set_label("SKU-months (log scale)")
    cb.outline.set_visible(False)
    fig.suptitle("Actual vs predicted monthly packs, CatBoost with INN + ATC, test 2023", x=0.01, ha="left",
                 fontweight="bold", fontsize=11)
    return fig


def fig_aggregate(preds, overall):
    scen = [s for s in SCENARIO_ORDER if (s, "test") in preds]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.4), sharex=True)
    for ax, s in zip(axes.ravel(), scen):
        d = preds[(s, "test")]
        base = best_baseline(overall, s)
        g = d.groupby("date")[["sales", base, "catboost_none", "catboost_both"]].sum()
        ax.plot(g.index, g["sales"], color=P.INK, lw=2, label="actual")
        ax.plot(g.index, g[base], color=P.AXIS, lw=1.6, label=f"best baseline: {MODEL_LABELS[base]}")
        ax.plot(g.index, g["catboost_none"], color=P.ARM_COLORS["none"], lw=1.6, label="CatBoost, no INN/ATC")
        ax.plot(g.index, g["catboost_both"], color=P.ARM_COLORS["both"], lw=1.8, label="CatBoost, INN + ATC")
        ax.yaxis.set_major_formatter(P.COMPACT)
        ax.set_ylim(0, None)
        ax.set_title(f"{SCENARIO_SHORT[s]}\nbest baseline: {MODEL_LABELS[base].lower()}", fontsize=9)
        ax.tick_params(axis="x", labelrotation=45, labelsize=7)
    for ax in axes.ravel()[len(scen):]:
        ax.set_visible(False)
    handles = [plt.Line2D([], [], color=c, lw=2) for c in (P.INK, P.AXIS, P.ARM_COLORS["none"], P.ARM_COLORS["both"])]
    fig.legend(handles, ["actual", "best baseline (by validation WAPE)", "CatBoost, no INN/ATC", "CatBoost, INN + ATC"],
               loc="lower center", ncols=4, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Total monthly packs of the evaluated SKUs, test 2023", x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def fig_examples(preds, ds, scenario="A", n=6):
    d = preds[(scenario, "test")]
    top = d.groupby("sku")["sales"].sum().sort_values(ascending=False)
    # Spread the examples over the volume distribution: the largest SKU, then the top 1%, 5%, 20%, 50%, 80%.
    ranks = [0] + [int(q * len(top)) for q in (0.01, 0.05, 0.2, 0.5, 0.8)]
    picks = list(top.index[ranks])[:n]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6), sharex=True)
    sku_pos = pd.Series(np.arange(len(ds.attrs)), index=ds.attrs["sku"])
    base = "seasonal_naive" if scenario == "A" else "hierarchical_mean"
    for ax, sku in zip(axes.ravel(), picks):
        i = sku_pos[sku]
        ax.plot(ds.dates, ds.sales0[i], color=P.INK, lw=1.6, label="actual")
        g = d[d["sku"] == sku].sort_values("date")
        ax.plot(g["date"], g[base], color=P.AXIS, lw=1.6, label=MODEL_LABELS[base])
        ax.plot(g["date"], g["catboost_none"], color=P.ARM_COLORS["none"], lw=1.6, label="CatBoost, no INN/ATC")
        ax.plot(g["date"], g["catboost_both"], color=P.ARM_COLORS["both"], lw=1.8, label="CatBoost, INN + ATC")
        a = ds.attrs.iloc[i]
        rank = int(np.flatnonzero(top.index == sku)[0]) + 1
        inn = a["inn"] if isinstance(a["inn"], str) else "(no INN)"
        ax.set_title(f"{inn[:24]} | {a['nfc'][:16]}\nvolume rank {rank:,} of {len(top):,}", fontsize=8.5)
        ax.yaxis.set_major_formatter(P.COMPACT)
        ax.set_ylim(0, None)
        ax.axvline(np.datetime64("2023-01-01"), color=P.AXIS, lw=0.8)
        ax.tick_params(axis="x", labelsize=7)
    handles = [plt.Line2D([], [], color=c, lw=2) for c in (P.INK, P.AXIS, P.ARM_COLORS["none"], P.ARM_COLORS["both"])]
    fig.legend(handles, ["actual", MODEL_LABELS[base], "CatBoost, no INN/ATC", "CatBoost, INN + ATC"],
               loc="lower center", ncols=4, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"Example SKUs, scenario {SCENARIO_SHORT[scenario]} (forecast origin 2022-12)", x=0.01, ha="left",
                 fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def fig_error_by_atc1(breakdowns):
    from matplotlib.colors import LinearSegmentedColormap
    b = breakdowns[(breakdowns["breakdown"] == "atc1") & (breakdowns["model"] == "catboost_both")]
    t = b.pivot(index="group", columns="scenario", values="WAPE")
    t = t[[s for s in SCENARIO_ORDER if s in t.columns]]
    t.index = [i if len(i) <= 34 else i[:33] + "…" for i in t.index]
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    vals = t.to_numpy()
    shown = np.clip(vals, 0, 1.5)
    im = ax.imshow(shown, cmap=LinearSegmentedColormap.from_list("seq", P.SEQUENTIAL), aspect="auto", vmin=0, vmax=1.5)
    ax.set_xticks(range(t.shape[1]), [SCENARIO_SHORT[s].split(":")[0] for s in t.columns])
    ax.set_yticks(range(t.shape[0]), t.index, fontsize=8)
    ax.grid(False)
    for (r, c), v in np.ndenumerate(vals):
        if np.isfinite(v):
            ax.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                    color="white" if min(v, 1.5) > 0.8 else P.INK)
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label("WAPE (colour capped at 1.5)")
    cb.outline.set_visible(False)
    ax.set_title("WAPE by ATC level-1 group, CatBoost with INN + ATC, test 2023")
    fig.tight_layout()
    return fig


def fig_known_depth(breakdowns):
    b = breakdowns[(breakdowns["scenario"] == "C") & (breakdowns["breakdown"] == "known_atc_depth")]
    models = list(dict.fromkeys(b["model"]))
    depths = sorted(b["group"].unique())
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    w = 0.26
    for k, m in enumerate(models):
        t = b[b["model"] == m].set_index("group").reindex(depths)
        x = np.arange(len(depths)) + (k - 1) * (w + 0.02)
        ax.bar(x, t["WAPE"], width=w, color=_model_color(m), label=MODEL_LABELS[m])
    counts = b[b["model"] == models[0]].set_index("group").reindex(depths)
    ax.set_xticks(range(len(depths)), [f"deepest shared\nlevel: ATC{int(d)}\n(n = {int(n / 12):,} SKUs)"
                                       if d > 0 else "no shared level" for d, n in zip(depths, counts["n"])], fontsize=8)
    ax.set_ylabel("WAPE")
    ax.set_title("Scenario C: error vs deepest ATC level shared with training INNs")
    ax.legend(loc="best", fontsize=8)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def fig_importance(importance, scenarios=("A", "B", "N")):
    from .modeling import feature_columns  # noqa: F401
    present = [s for s in scenarios if ((importance["scenario"] == s) & (importance["arm"] == "both")).any()]
    fig, axes = plt.subplots(1, len(present), figsize=(4.4 * len(present), 4.8))
    axes = np.atleast_1d(axes)
    for ax, s in zip(axes, present):
        t = importance[(importance["scenario"] == s) & (importance["arm"] == "both") & (importance["fold"] == 0)
                       & (importance["half"] == 0)]
        t = t.sort_values("importance", ascending=False).head(15)[::-1]
        colors = []
        for f in t["feature"]:
            if f == "inn" or f.startswith("inn_") or f == "n_ingredients":
                colors.append(P.ARM_COLORS["inn"])
            elif f.startswith("atc"):
                colors.append(P.ARM_COLORS["atc"])
            else:
                colors.append(P.MUTED)
        ax.barh(range(len(t)), t["importance"], color=colors, height=0.62)
        ax.set_yticks(range(len(t)), t["feature"], fontsize=8)
        ax.set_title(SCENARIO_SHORT[s], fontsize=10)
        ax.set_xlabel("PredictionValuesChange, %", fontsize=8)
        ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (P.ARM_COLORS["inn"], P.ARM_COLORS["atc"], P.MUTED)]
    fig.legend(handles, ["INN block", "ATC block", "other"], loc="lower center", ncols=3, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Top-15 feature importances, CatBoost with INN + ATC (first fold, first cross-fitting half)", x=0.01, ha="left",
                 fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def fig_launch_age(preds):
    d = preds[("N", "test")]
    g = d.groupby("age_at_target")[["sales", "hierarchical_mean", "launch_age_mean", "catboost_none", "catboost_both"]].mean()
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.plot(g.index, g["sales"], color=P.INK, lw=2, marker="o", label="actual")
    ax.plot(g.index, g["hierarchical_mean"], color=P.AXIS, lw=1.6, label=MODEL_LABELS["hierarchical_mean"])
    ax.plot(g.index, g["launch_age_mean"], color=P.AXIS, lw=1.6, ls=(0, (4, 2)), label=MODEL_LABELS["launch_age_mean"])
    ax.plot(g.index, g["catboost_none"], color=P.ARM_COLORS["none"], lw=1.6, marker="o", label="CatBoost, no INN/ATC")
    ax.plot(g.index, g["catboost_both"], color=P.ARM_COLORS["both"], lw=1.8, marker="o", label="CatBoost, INN + ATC")
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("month since launch")
    ax.set_ylabel("mean packs per SKU")
    ax.yaxis.set_major_formatter(P.COMPACT)
    ax.set_ylim(0, None)
    ax.set_title("Real 2023 launches: average sales by month since launch")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    return fig


def robustness_summary(curves):
    """Mean and spread over seeds of the test WAPE at each tree count, per scenario and arm."""
    g = curves.groupby(["scenario", "arm", "trees"])["WAPE"]
    return g.agg(mean="mean", min="min", max="max").reset_index()


def fig_robustness(curves):
    summary = robustness_summary(curves)
    scen = [s for s in SCENARIO_ORDER if s in set(summary["scenario"])]
    fig, axes = plt.subplots(1, len(scen), figsize=(4.2 * len(scen), 3.8), squeeze=False)
    for ax, s in zip(axes.ravel(), scen):
        for arm in ARMS + [CODES_ARM]:
            t = summary[(summary["scenario"] == s) & (summary["arm"] == arm)]
            if t.empty:
                continue
            color = P.ARM_COLORS.get(arm, P.INK_2)
            ax.fill_between(t["trees"], t["min"], t["max"], color=color, alpha=0.12, lw=0)
            ax.plot(t["trees"], t["mean"], color=color, lw=1.8, marker="o" if arm != CODES_ARM else "D",
                    ms=4, label=ARM_LABELS[arm])
        ax.set_title(SCENARIO_SHORT[s], fontsize=10)
        ax.set_xlabel("number of trees", fontsize=8)
        ax.set_ylabel("WAPE, test 2023", fontsize=8)
    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncols=len(labels), bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Test WAPE vs number of trees (mean over 3 seeds, band = min-max; first fold for cold start)",
                 x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    return fig
