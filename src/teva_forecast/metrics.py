"""Error metrics and a cluster bootstrap for paired model comparisons."""
import numpy as np
import pandas as pd


def mae(y, p):
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(p))))


def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(p)) ** 2)))


def wape(y, p):
    y, p = np.asarray(y), np.asarray(p)
    den = np.abs(y).sum()
    return float(np.abs(y - p).sum() / den) if den > 0 else np.nan


def bias(y, p):
    """Relative error of the total: sum(pred) / sum(actual) - 1."""
    y, p = np.asarray(y), np.asarray(p)
    return float(p.sum() / y.sum() - 1) if y.sum() > 0 else np.nan


def summarize(y, p):
    return {"n": int(len(y)), "MAE": mae(y, p), "RMSE": rmse(y, p), "WAPE": wape(y, p), "bias": bias(y, p)}


def bootstrap_wape_difference(frame, cluster, pred_a, pred_b, actual="sales", n_boot=1000, seed=42):
    """Paired cluster bootstrap of WAPE(pred_a) - WAPE(pred_b).

    Clusters (SKUs, INNs or ATC groups) are resampled with replacement so that the
    within-cluster dependence of monthly errors is preserved.
    """
    g = frame.groupby(cluster)
    abs_a = g.apply(lambda d: np.abs(d[actual] - d[pred_a]).sum(), include_groups=False).to_numpy()
    abs_b = g.apply(lambda d: np.abs(d[actual] - d[pred_b]).sum(), include_groups=False).to_numpy()
    tot = g[actual].sum().to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(tot), size=(n_boot, len(tot)))
    den = tot[idx].sum(axis=1)
    wa, wb = abs_a[idx].sum(axis=1) / den, abs_b[idx].sum(axis=1) / den
    diff = wa - wb
    rel = diff / wb
    point_a, point_b = abs_a.sum() / tot.sum(), abs_b.sum() / tot.sum()
    return {
        "wape_a": point_a, "wape_b": point_b,
        "diff": point_a - point_b,
        "diff_lo": float(np.quantile(diff, 0.025)), "diff_hi": float(np.quantile(diff, 0.975)),
        "rel": (point_a - point_b) / point_b,
        "rel_lo": float(np.quantile(rel, 0.025)), "rel_hi": float(np.quantile(rel, 0.975)),
        "p_a_not_better": float(np.mean(diff >= 0)),
        "n_clusters": int(len(tot)),
    }


def grouped_metrics(frame, by, pred_cols, actual="sales"):
    rows = []
    for key, d in frame.groupby(by, observed=True):
        for col in pred_cols:
            rows.append({**dict(zip([by] if isinstance(by, str) else by, [key] if isinstance(by, str) else key)),
                         "model": col, **summarize(d[actual], d[col]), "actual_total": float(d[actual].sum())})
    return pd.DataFrame(rows)
