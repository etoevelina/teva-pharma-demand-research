"""Figures of the WHO seasonality comparison (Figures 1-4 of the report)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from . import plotting as P
from . import who

SOURCE_NOTE = ("Sources: Teva pharmacy sales dataset (packs per month); WHO GISRS FluNet and FluID via the "
               "FluMart API (ISO weeks allocated to months by day).")
WINDOW_LABELS = {"covid_npi": "COVID-19 restrictions", "war_onset": "war onset"}


def _shade(ax, label=False):
    styles = {"covid_npi": {"facecolor": P.GRID, "alpha": 0.6, "hatch": None},
              "war_onset": {"facecolor": "none", "alpha": 1.0, "hatch": "////"}}
    for key, (start, end) in who.ANOMALY_WINDOWS.items():
        st = styles[key]
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end) + pd.offsets.MonthEnd(0), facecolor=st["facecolor"],
                   alpha=st["alpha"], hatch=st["hatch"], edgecolor=P.AXIS, lw=0,
                   label=WINDOW_LABELS[key] if label else None)


def _note(fig, text=SOURCE_NOTE, y=0.005):
    fig.text(0.01, y, text, fontsize=7, color=P.INK_2, ha="left", va="bottom")


def fig1_monthly_series(sales, indicators):
    panels = [
        ("R05 cough and cold", sales["R05 cough and cold"] / 1e6, "million packs", "R05 cough and cold preparations, sales"),
        ("N02BB+N02BE antipyretics", sales["N02BB+N02BE antipyretics"] / 1e6, "million packs", "Antipyretic analgesics (N02BB, N02BE), sales"),
        ("J01 antibacterials", sales["J01 antibacterials"] / 1e6, "million packs", "J01 antibacterials, sales"),
        ("J05AH+J05AC influenza antivirals", sales["J05AH+J05AC influenza antivirals"] / 1e3, "thousand packs", "Influenza antivirals (J05AH, J05AC), sales"),
        ("flu", indicators["flu_positivity"] * 100, "% positive", "Influenza positivity, FluNet (sum positives / sum tested)"),
        ("spec", indicators["flu_specimens"], "specimens", "Specimens tested for influenza, FluNet (log scale)"),
        ("ari", indicators["ari_per_100k"], "per 100,000", "ARI incidence, FluID (ISO weeks 40-20 reported; months used Oct-Apr)"),
        ("ili", indicators["ili_per_100k"], "per 100,000", "ILI incidence, FluID sentinel sites"),
    ]
    fig, axes = plt.subplots(len(panels), 1, figsize=(9, 13), sharex=True)
    for k, (ax, (key, series, unit, title)) in enumerate(zip(axes, panels)):
        _shade(ax, label=k == 0)
        color = P.SERIES[0] if k < 4 else P.SERIES[1]
        ax.plot(series.index, series.to_numpy(), color=color, lw=1.6, marker="o", ms=2.5)
        if key == "spec":
            ax.lines[-1].set_ydata(series.where(series > 0).to_numpy())
            ax.set_yscale("log")
        else:
            ax.set_ylim(0, None)
        ax.set_ylabel(unit, fontsize=8)
        ax.set_title(title, fontsize=9)
    axes[0].legend(loc="upper right", fontsize=7, ncols=2)
    fig.suptitle("Figure 1. Monthly pharmaceutical sales and influenza surveillance indicators, Ukraine, 2019-2023",
                 x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.02, 1, 0.98))
    _note(fig)
    return fig


def _heat(ax, table, title, span, cbar_label):
    cmap = LinearSegmentedColormap.from_list("div", P.DIVERGING)
    raw = table.to_numpy(dtype=float)
    vals = np.log2(np.clip(raw, 2.0 ** -span, None))
    vals[~np.isfinite(raw)] = np.nan
    im = ax.imshow(np.ma.masked_invalid(vals), cmap=cmap, norm=TwoSlopeNorm(0, -span, span), aspect="auto")
    ax.set_xticks(range(12), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_yticks(range(len(table)), table.index, fontsize=8)
    ax.grid(False)
    for (r, c), v in np.ndenumerate(raw):
        if np.isfinite(v):
            ax.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(vals[r, c]) > span * 0.6 else P.INK)
        else:
            ax.text(c, r, "n/a", ha="center", va="center", fontsize=6, color=P.MUTED)
    ax.set_title(title, fontsize=9.5)
    cb = plt.colorbar(im, ax=ax, shrink=0.9)
    cb.set_label(cbar_label, fontsize=8)
    cb.outline.set_visible(False)


def fig2_seasonal_profiles(profiles, groups, indicators_meta):
    sales_rows = [g for g in groups if g in profiles]
    who_rows = [k for k in indicators_meta if k in profiles]
    top = profiles[sales_rows].T
    bottom = profiles[who_rows].T
    bottom.index = [indicators_meta[k][2] for k in who_rows]
    fig, axes = plt.subplots(2, 1, figsize=(9.5, 8.5), gridspec_kw={"height_ratios": [len(top), len(bottom) + 0.6]})
    _heat(axes[0], top, "Sales: within-year seasonal index (1 = average month of the year)", 0.6,
          "log2(seasonal index)")
    _heat(axes[1], bottom, "WHO indicators: within-year seasonal index (ARI: Oct-Apr only)", 2.5,
          "log2(seasonal index)")
    fig.suptitle("Figure 2. Seasonal patterns of selected ATC groups and WHO indicators, Ukraine, 2019-2023",
                 x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    _note(fig, SOURCE_NOTE + " Index: month / mean of its calendar year, averaged over 2019-2023.")
    return fig


def fig3_correlations(res, groups, indicators_meta):
    base = res[(res["lag_months"] == 0) & (res["period"] == "full period")]
    cols = []
    for key in indicators_meta:
        for kind in ("levels", "anomalies"):
            cols.append((key, kind))
    rows = list(groups)
    rho = np.full((len(rows), len(cols)), np.nan)
    mark = np.full((len(rows), len(cols)), "", dtype=object)
    for i, g in enumerate(rows):
        for j, (key, kind) in enumerate(cols):
            r = base[(base["group"] == g) & (base["indicator"] == key) & (base["series"] == kind)]
            if len(r) and np.isfinite(r["spearman"].iloc[0]):
                rho[i, j] = r["spearman"].iloc[0]
                m = ""
                if r["p_year_permutation"].iloc[0] < 0.05:
                    m += "*"
                if "q_bh_primary" in r and r["q_bh_primary"].iloc[0] < 0.05:
                    m += "†"
                mark[i, j] = m
    fig, ax = plt.subplots(figsize=(9.5, 7))
    cmap = LinearSegmentedColormap.from_list("div", P.DIVERGING[::-1])
    im = ax.imshow(np.ma.masked_invalid(rho), cmap=cmap, vmin=-1, vmax=1, aspect="auto")
    short = {"flu_positivity": "Influenza\npositivity", "ari_per_100k": "ARI\nincidence", "ili_per_100k": "ILI incidence\n(sentinel)"}
    ax.set_xticks(range(len(cols)), [f"{short.get(k, k)}\n{kind}" for k, kind in cols], fontsize=7.5)
    labels = [f"{g}  [{groups[g][2]}]" for g in rows]
    ax.set_yticks(range(len(rows)), labels, fontsize=8)
    ax.grid(False)
    for (i, j), v in np.ndenumerate(rho):
        if np.isfinite(v):
            ax.text(j, i, f"{v:+.2f}{mark[i, j]}", ha="center", va="center", fontsize=7,
                    color="white" if abs(v) > 0.6 else P.INK)
    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label("Spearman correlation, lag 0", fontsize=8)
    cb.outline.set_visible(False)
    ax.set_title("Levels: log sales vs indicator. Anomalies: both series minus their calendar-month means.\n"
                 "* year-permutation p < 0.05;  † Benjamini-Hochberg q < 0.05 within the pre-specified primary pairs",
                 fontsize=8.5, loc="left", fontweight="normal")
    fig.suptitle("Figure 3. Correlation between pharmaceutical sales and epidemiological indicators, Ukraine, 2019-2023",
                 x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    _note(fig, SOURCE_NOTE + " n = months with both values (flu positivity 57, ARI 35, ILI 60 before lagging).")
    return fig


def fig4_lags(res, primary_pairs, indicators_meta):
    keys = [k for k in primary_pairs]
    fig, axes = plt.subplots(2, len(keys), figsize=(5.2 * len(keys), 8.2), squeeze=False)
    base = res[(res["period"] == "full period")]
    offsets = {0: -0.22, 1: 0.0, 2: 0.22}
    colors = {0: P.SERIES[0], 1: P.SERIES[1], 2: P.SERIES[2]}
    for col, key in enumerate(keys):
        groups = primary_pairs[key]
        for row, kind in enumerate(("levels", "anomalies")):
            ax = axes[row, col]
            for lag, off in offsets.items():
                t = base[(base["indicator"] == key) & (base["series"] == kind) & (base["lag_months"] == lag)].set_index("group").reindex(groups)
                y = np.arange(len(groups))[::-1] + off
                ax.errorbar(t["spearman"], y, xerr=[t["spearman"] - t["spearman_ci_lo"], t["spearman_ci_hi"] - t["spearman"]],
                            fmt="o", color=colors[lag], ms=5, capsize=2, lw=1.2, label=f"lag {lag} month{'s' if lag != 1 else ''}",
                            markeredgecolor=P.SURFACE, markeredgewidth=1)
            ax.axvline(0, color=P.INK_2, lw=0.8)
            ax.set_xlim(-1, 1)
            ax.set_xticks([-1, -0.5, 0, 0.5, 1])
            ax.set_yticks(np.arange(len(groups))[::-1], groups, fontsize=7.5)
            ax.set_title(f"{indicators_meta[key][2]}: {kind}", fontsize=9)
            ax.set_xlabel("Spearman correlation (95% block-bootstrap CI)", fontsize=8)
            ax.grid(axis="y", visible=False)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncols=3, fontsize=8, bbox_to_anchor=(0.5, 0.025))
    fig.suptitle("Figure 4. Lagged associations: sales in month t vs indicator in month t - lag, Ukraine, 2019-2023",
                 x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    _note(fig, SOURCE_NOTE + " Moving blocks of 12 calendar months, 2,000 bootstrap resamples.")
    return fig


def make_all_figures(sales, indicators, profiles, res, groups, indicators_meta, primary_pairs):
    figs = {
        "who_fig1_monthly_series": fig1_monthly_series(sales, indicators),
        "who_fig2_seasonal_profiles": fig2_seasonal_profiles(profiles, groups, indicators_meta),
        "who_fig3_correlations": fig3_correlations(res, groups, indicators_meta),
        "who_fig4_lagged_associations": fig4_lags(res, primary_pairs, indicators_meta),
    }
    for name, fig in figs.items():
        fig.savefig(P.config.FIGURES_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
        plt.close(fig)


def make_overview_figures(sales, indicators, profiles, groups=None, indicators_meta=None):
    fig = fig1_monthly_series(sales, indicators)
    fig.savefig(P.config.FIGURES_DIR / "who_fig1_monthly_series.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
