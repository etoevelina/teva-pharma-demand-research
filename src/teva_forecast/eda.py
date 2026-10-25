"""Dataset description tables and EDA figures."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import plotting as P

LEVELS = ["atc1", "atc2", "atc3", "atc4", "atc5", "inn"]
LEVEL_LABELS = {"nfc": "Form (NFC)", "atc1": "ATC1", "atc2": "ATC2", "atc3": "ATC3", "atc4": "ATC4",
                "atc5": "ATC5", "inn": "INN", "inn_nfc": "INN x form"}


def _short(label, n=28):
    return label if len(label) <= n else label[: n - 1] + "…"


def sku_summary(ds):
    a = ds.attrs.copy()
    on = ~np.isnan(ds.sales)
    with np.errstate(invalid="ignore"):
        a["mean_sales"] = np.nansum(ds.sales, axis=1) / on.sum(axis=1)
        a["zero_share"] = np.nansum(ds.sales == 0, axis=1) / on.sum(axis=1)
    a["total_sales"] = ds.sales0.sum(axis=1)
    a["on_market_months"] = on.sum(axis=1)
    return a


def dataset_characteristics(ds, raw_shape):
    a = ds.attrs
    on = ~np.isnan(ds.sales)
    rows = [
        ("Source file", "teva_sales.csv (full dataset)"),
        ("Raw shape (rows x columns)", f"{raw_shape[0]:,} x {raw_shape[1]}"),
        ("Unit of observation", "SKU (Morion ID) x calendar month"),
        ("Period", f"{ds.dates[0]:%Y-%m} to {ds.dates[-1]:%Y-%m} ({len(ds.dates)} months)"),
        ("Target variable", "quantity sold, number of packs per SKU per month"),
        ("SKUs (Morion ID)", f"{a['sku'].nunique():,}"),
        ("INNs (active substances or combinations)", f"{a['inn'].nunique():,}"),
        ("ATC level 1 / 2 / 3 / 4 / 5 groups", " / ".join(f"{a[f'atc{lvl}'].nunique():,}" for lvl in range(1, 6))),
        ("Brands (anonymised codes)", f"{a['brand'].nunique():,}"),
        ("Dosage forms (NFC1)", f"{a['nfc'].nunique()}"),
        ("Distinct descriptions", f"{a['description'].nunique():,}"),
        ("SKU-month cells", f"{ds.sales.size:,}"),
        ("SKU-months on the market (after first sale)", f"{int(on.sum()):,} ({on.mean():.1%})"),
        ("Zero sales among on-market SKU-months", f"{(ds.sales[on] == 0).mean():.1%}"),
        ("Total volume 2019-2023", f"{ds.sales0.sum() / 1e9:.2f} billion packs"),
        ("SKUs selling in 2019-01 (launch date unobserved)", f"{int((a['first_t'] == 0).sum()):,}"),
        ("SKUs first sold 2019-02 .. 2023-12 (observed launches)", f"{int((a['first_t'] > 0).sum()):,}"),
        ("Revenue / price / stock columns", "not available"),
    ]
    return pd.DataFrame(rows, columns=["characteristic", "value"])


def hierarchy_table(ds):
    a = ds.attrs
    rows = []
    for lvl in ["atc1", "atc2", "atc3", "atc4", "atc5", "inn", "nfc"]:
        sku_per = a.groupby(lvl)["sku"].nunique()
        inn_per = a.groupby(lvl)["inn"].nunique()
        rows.append({
            "level": LEVEL_LABELS.get(lvl, lvl), "groups": a[lvl].nunique(),
            "SKUs per group (median)": float(sku_per.median()), "SKUs per group (max)": int(sku_per.max()),
            "INNs per group (median)": float(inn_per.median()),
            "groups with >= 2 INNs": int((inn_per >= 2).sum()),
            "single-SKU groups": int((sku_per == 1).sum()),
        })
    return pd.DataFrame(rows)


def hierarchy_checks(ds):
    """Facts about the INN / ATC hierarchy cited in the report, computed from the cleaned attributes."""
    a = ds.attrs
    rows = [("SKUs without an INN (placeholder '-' in the raw file)", int(a["inn_missing"].sum())),
            ("SKUs with a missing ATC4 code (placeholder '-')", int(a["atc4"].isna().sum())),
            ("INNs (excluding the placeholder)", int(a["inn"].nunique()))]
    for level in range(2, 6):
        parents = a.dropna(subset=[f"atc{level}", f"atc{level - 1}"]).groupby(f"atc{level}")[f"atc{level - 1}"].nunique()
        rows.append((f"ATC{level} codes with more than one ATC{level - 1} parent", int((parents > 1).sum())))
    known = a.dropna(subset=["inn"])
    rows += [
        ("ATC5 codes containing more than one INN", int((known.groupby("atc5")["inn"].nunique() > 1).sum())),
        ("INNs appearing under more than one ATC5 code", int((known.groupby("inn")["atc5"].nunique() > 1).sum())),
        ("INNs appearing under more than one ATC2 group", int((known.groupby("inn")["atc2"].nunique() > 1).sum())),
    ]
    tw = a[a["twin_size"] > 1]
    span = tw.groupby("twin_cluster").agg(latest_first=("first_t", "max"), earliest_last=("last_t", "min"))
    rows += [
        ("Twin groups (identical ATC5, brand, INN, form, description)", int(tw["twin_cluster"].nunique())),
        ("  of which all members are on sale together at some point",
         int((span["latest_first"] <= span["earliest_last"]).sum())),
    ]
    total = ds.sales0.sum(axis=1)
    order = np.sort(total)[::-1]
    rows += [
        ("Share of volume of the top 1% of SKUs", round(order[: len(order) // 100].sum() / order.sum(), 3)),
        ("Share of volume of the top 10% of SKUs", round(order[: len(order) // 10].sum() / order.sum(), 3)),
    ]
    return pd.DataFrame(rows, columns=["check", "value"])


def key_numbers(ds):
    """Scalar facts quoted in the report that are not part of another table."""
    s = sku_summary(ds)
    m = s["mean_sales"].dropna()
    total = pd.Series(ds.sales0.sum(axis=0), index=ds.dates)
    selling = (ds.sales0 > 0).sum(axis=0)
    annual = total.groupby(total.index.year).sum()
    a = ds.attrs
    entries = a.loc[a["first_t"] > 0, "first_sale"].dt.year.value_counts().sort_index()
    rows = [
        ("Mean monthly packs per SKU (on-market months): median", round(m.median(), 1)),
        ("Mean monthly packs per SKU: 90th percentile", round(m.quantile(0.9), 1)),
        ("Mean monthly packs per SKU: maximum", round(m.max(), 1)),
        ("Total packs, 2020-03 (million)", round(total["2020-03"].iloc[0] / 1e6, 1)),
        ("Total packs, 2020-04 (million)", round(total["2020-04"].iloc[0] / 1e6, 1)),
        ("Total packs, 2022-02 (million)", round(total["2022-02"].iloc[0] / 1e6, 1)),
        ("Total packs, 2022-04 (million)", round(total["2022-04"].iloc[0] / 1e6, 1)),
        *[(f"Total packs, {y} (million)", round(v / 1e6, 1)) for y, v in annual.items()],
        ("Change of annual volume 2022 vs 2021", round(annual[2022] / annual[2021] - 1, 3)),
        ("SKUs with positive sales per month: minimum", int(selling.min())),
        ("SKUs with positive sales per month: maximum", int(selling.max())),
        *[(f"SKUs first sold in {y} (excluding 2019-01)", int(v)) for y, v in entries.items()],
    ]
    return pd.DataFrame(rows, columns=["fact", "value"])


def atc1_composition(ds):
    a = ds.attrs.assign(total=ds.sales0.sum(axis=1))
    g = a.groupby("atc1").agg(skus=("sku", "size"), packs=("total", "sum"))
    out = g.div(g.sum()).round(4).rename(columns={"skus": "share of SKUs", "packs": "share of packs"})
    return out.reset_index()


def source_files_check(full_path, small_path):
    """Confirm that the sampled file is an exact subset of the full file."""
    full, small = pd.read_csv(full_path), pd.read_csv(small_path)
    common = small["Morion ID"].isin(full["Morion ID"])
    f = full.set_index("Morion ID").loc[small["Morion ID"]]
    s_ = small.set_index("Morion ID")
    identical = bool(f.reset_index().equals(s_.loc[f.index].reset_index()))
    return pd.DataFrame([
        ("teva_sales.csv rows", len(full)),
        ("teva_sales_small.csv rows", len(small)),
        ("small-file IDs present in the full file", int(common.sum())),
        ("small-file rows identical to the full file (all columns)", identical),
        ("INNs in the small file", int(small["INN"].nunique())),
    ], columns=["check", "value"])


def launch_composition(ds):
    """SKUs first sold in 2022 and 2023 and how much is known about them at the launch."""
    a = ds.attrs
    rows = []
    for year in (2022, 2023):
        start = (year - 2019) * 12
        new = a[(a["first_t"] >= start) & (a["first_t"] < start + 12)]
        before = a[(a["first_t"] >= 0) & (a["first_t"] < start)]
        seen = set(before["inn"].dropna())
        older_twins = set(before["twin_cluster"])
        rows.append({
            "launch year": year, "SKUs": len(new),
            "INN sold before": int(new["inn"].isin(seen).sum()),
            "new INN": int((new["inn"].notna() & ~new["inn"].isin(seen)).sum()),
            "no INN": int(new["inn"].isna().sum()),
            "with an older identical twin": int(new["twin_cluster"].isin(older_twins).sum()),
        })
    return pd.DataFrame(rows)


def parsing_audit_sample(ds, n=60, seed=7):
    """The random sample of descriptions used for the manual parsing check."""
    cols = ["sku", "description", "strength_value", "strength_unit", "multi_strength",
            "content_value", "content_unit", "n_doses", "pack_count"]
    return ds.attrs.sample(n, random_state=seed)[cols].reset_index(drop=True)


def quality_report(ds, raw_sales):
    a = ds.attrs
    T = ds.sales.shape[1]
    t = np.arange(T)[None, :]
    first, last = a["first_t"].to_numpy()[:, None], a["last_t"].to_numpy()[:, None]
    zero = raw_sales == 0
    interior = zero & (t > first) & (t < last)
    pre = zero & (t < first)
    post = zero & (t > last)
    runs3 = 0
    for row in interior:
        run = best = 0
        for v in row:
            run = run + 1 if v else 0
            best = max(best, run)
        runs3 += best >= 3
    on = ~np.isnan(ds.sales)
    pos = raw_sales > 0
    logs = np.where(pos, np.log1p(raw_sales), np.nan)
    med = np.nanmedian(logs, axis=1, keepdims=True)
    mad = np.nanmedian(np.abs(logs - med), axis=1, keepdims=True) * 1.4826
    with np.errstate(invalid="ignore", divide="ignore"):
        rz = np.abs(logs - med) / mad
    outliers = np.nansum(rz > 3.5)
    atc5_is_atc4 = (a["atc5"] == a["atc4"]).sum()
    nonstandard = a["atc5"].str.contains(r"\*\*", regex=True).sum()
    rows = [
        ("Missing attribute values in the raw file", 0, "but see the placeholders below"),
        ("Placeholder '-' in INN (product without an INN), treated as missing", int(a["inn"].isna().sum()), ""),
        ("Placeholder '-' in ATC4, treated as missing", int(a["atc4"].isna().sum()), ""),
        ("Missing monthly sales values", int(np.isnan(raw_sales).sum()), ""),
        ("Negative sales values", int((raw_sales < 0).sum()), ""),
        ("Duplicate Morion IDs", int(a["sku"].duplicated().sum()), ""),
        ("SKUs with an identical twin (same ATC5, brand, INN, form, description)",
         int((a["twin_size"] > 1).sum()), f"{a.loc[a['twin_size'] > 1, 'twin_cluster'].nunique()} twin groups"),
        ("SKUs without any sale in 60 months", int((a["first_t"] < 0).sum()), ""),
        ("Zero SKU-months, total", int(zero.sum()), f"{zero.mean():.1%} of all cells"),
        ("  before the first sale (not yet on market)", int(pre.sum()), f"{pre.mean():.1%} of all cells"),
        ("  between first and last sale (gaps, possible stock-outs)", int(interior.sum()),
         f"{interior.sum() / max(int(((t >= first) & (t <= last)).sum()), 1):.1%} of active span"),
        ("  after the last sale (discontinued or right-censored)", int(post.sum()), f"{post.mean():.1%} of all cells"),
        ("SKUs with at least one interior gap", int(interior.any(axis=1).sum()), ""),
        ("SKUs with an interior gap of >= 3 consecutive months", int(runs3), ""),
        ("Non-integer sales values (positive cells)", int((pos & (raw_sales % 1 != 0)).sum()),
         f"{(raw_sales[pos] % 1 != 0).mean():.1%} of positive cells"),
        ("Outlying months (robust z > 3.5 on log sales within SKU)", int(outliers),
         f"{outliers / pos.sum():.2%} of positive cells; kept, not removed"),
        ("ATC5 field holding a level-4 code (no substance-level code)", int(atc5_is_atc4), ""),
        ("Non-standard ATC5 codes marked with '**'", int(nonstandard), ""),
        ("On-market SKU-months", int(on.sum()), f"{on.mean():.1%} of all cells"),
    ]
    return pd.DataFrame(rows, columns=["check", "count", "note"])


def parse_coverage(ds):
    a = ds.attrs
    rows = [
        ("strength parsed", a["strength_unit"].ne("none").mean()),
        ("  of which mass per unit (mg)", a["strength_unit"].eq("mg").mean()),
        ("  of which concentration (mg/ml, mg/g, %, IU/ml, ...)", a["strength_unit"].isin(["mg/ml", "mg/g", "%", "IU/ml", "IU/g"]).mean()),
        ("multiple strengths (combination product)", a["multi_strength"].mean()),
        ("package content parsed (ml or g)", a["content_unit"].ne("none").mean()),
        ("number of doses parsed", a["n_doses"].notna().mean()),
        ("pack count parsed (#N)", a["pack_count"].notna().mean()),
    ]
    return pd.DataFrame(rows, columns=["field", "share of SKUs"])


def seasonal_index(ds, by="atc1"):
    """Within-year seasonal index: month share of the annual total x 12, averaged over 2019-2023."""
    a = ds.attrs
    out = {}
    years = ds.dates.year.to_numpy()
    for g, idx in a.groupby(by).indices.items():
        s = ds.sales0[idx].sum(axis=0)
        frame = pd.DataFrame({"year": years, "month": ds.dates.month, "s": s})
        frame["idx"] = frame["s"] / frame.groupby("year")["s"].transform("mean")
        out[g] = frame.groupby("month")["idx"].mean()
    return pd.DataFrame(out).T


def lag12_autocorrelation(ds, min_months=36):
    on = ~np.isnan(ds.sales)
    res = []
    for i in np.flatnonzero(on.sum(axis=1) >= min_months):
        y = ds.sales[i]
        x0, x1 = y[12:], y[:-12]
        ok = ~np.isnan(x0) & ~np.isnan(x1)
        if ok.sum() >= 24 and np.std(x0[ok]) > 0 and np.std(x1[ok]) > 0:
            res.append(np.corrcoef(x0[ok], x1[ok])[0, 1])
    return pd.Series(res, name="lag12_corr")


def group_informativeness(ds):
    """Leave-one-out R^2 of predicting a SKU's log mean sales by the mean of the *other* SKUs in its group.

    This measures how much a group label tells about the sales level of an unseen product.
    """
    s = sku_summary(ds)
    s = s[s["on_market_months"] > 0].copy()
    y = np.log1p(s["mean_sales"].to_numpy())
    s["y"] = y
    s["inn_nfc"] = s["inn"] + " | " + s["nfc"]
    total = ((y - y.mean()) ** 2).sum()
    rows = []
    for g in ["nfc", "atc1", "atc2", "atc3", "atc4", "atc5", "inn", "inn_nfc"]:
        grp = s.groupby(g)["y"]
        tot, cnt = grp.transform("sum").to_numpy(), grp.transform("count").to_numpy()
        loo = np.where(cnt > 1, (tot - y) / np.maximum(cnt - 1, 1), np.nan)
        coverage = np.mean(cnt > 1)
        pred = np.where(np.isnan(loo), y.mean(), loo)
        rows.append({"grouping": LEVEL_LABELS[g], "groups": s[g].nunique(),
                     "SKUs with a peer in group": coverage,
                     "LOO R2 (log mean sales)": 1 - ((y - pred) ** 2).sum() / total})
    return pd.DataFrame(rows)


def launch_curve(ds):
    """Sales by month since launch for SKUs first sold 2020-01..2022-12, relative to months 7-12."""
    a = ds.attrs
    sel = np.flatnonzero((a["first_t"] >= 12) & (a["first_t"] <= 47))
    curves = []
    for i in sel:
        f = a["first_t"].iat[i]
        y = ds.sales0[i, f:f + 12]
        ref = y[6:12].mean()
        if len(y) == 12 and ref > 0:
            curves.append(y / ref)
    c = np.array(curves)
    return pd.DataFrame({
        "month_since_launch": np.arange(1, 13),
        "median": np.median(c, axis=0),
        "q25": np.quantile(c, 0.25, axis=0),
        "q75": np.quantile(c, 0.75, axis=0),
    }), len(c)


# --- Figures ----------------------------------------------------------------------------

def fig_monthly_total(ds):
    total = ds.sales0.sum(axis=0)
    selling = (ds.sales0 > 0).sum(axis=0)
    fig, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    axes[0].plot(ds.dates, total, color=P.SERIES[0], lw=1.8)
    axes[0].yaxis.set_major_formatter(P.COMPACT)
    axes[0].set_title("Total packs sold per month")
    axes[0].set_ylim(0, total.max() * 1.1)
    axes[1].plot(ds.dates, selling, color=P.SERIES[0], lw=1.8)
    axes[1].yaxis.set_major_formatter(P.COMPACT)
    axes[1].set_title("SKUs with positive sales")
    axes[1].set_ylim(0, selling.max() * 1.15)
    for ax in axes:
        ax.axvspan(np.datetime64("2022-01-01"), np.datetime64("2022-12-31"), color=P.GRID, alpha=0.5, lw=0)
    axes[0].text(np.datetime64("2022-01-15"), total.max() * 1.02, "validation year", color=P.INK_2, fontsize=8)
    fig.tight_layout()
    return fig


def fig_sku_distribution(ds):
    s = sku_summary(ds)
    s = s[s["on_market_months"] > 0]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    axes[0].hist(np.log10(s["mean_sales"] + 1), bins=40, color=P.SERIES[0], edgecolor=P.SURFACE, linewidth=0.6)
    axes[0].set_title("Mean monthly packs per SKU")
    axes[0].set_xlabel("log10(mean packs + 1)")
    axes[0].set_ylabel("SKUs")
    axes[1].hist(s["zero_share"], bins=20, color=P.SERIES[0], edgecolor=P.SURFACE, linewidth=0.6)
    axes[1].set_title("Share of zero months while on market")
    axes[1].xaxis.set_major_formatter(P.PERCENT)
    axes[1].set_ylabel("SKUs")
    fig.tight_layout()
    return fig


def fig_hierarchy(ds):
    a = ds.attrs
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    counts = [a[c].nunique() for c in ["atc1", "atc2", "atc3", "atc4", "atc5", "inn", "sku"]]
    labels = ["ATC1", "ATC2", "ATC3", "ATC4", "ATC5", "INN", "SKU"]
    bars = axes[0].bar(labels, counts, color=P.SERIES[0], width=0.6)
    axes[0].set_yscale("log")
    axes[0].set_title("Distinct values per level")
    for b, v in zip(bars, counts):
        axes[0].text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:,}", ha="center", fontsize=8, color=P.INK_2)
    axes[0].set_ylim(1, max(counts) * 4)
    per_inn = a.groupby("inn")["sku"].nunique()
    bins = np.unique(np.logspace(0, np.log10(per_inn.max() + 1), 25).astype(int))
    axes[1].hist(per_inn, bins=bins, color=P.SERIES[0], edgecolor=P.SURFACE, linewidth=0.6)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("SKUs per INN")
    axes[1].set_xlabel("SKUs in the INN")
    axes[1].set_ylabel("INNs")
    fig.tight_layout()
    return fig


def fig_atc1_composition(ds):
    a = ds.attrs.assign(total=ds.sales0.sum(axis=1))
    g = a.groupby("atc1").agg(skus=("sku", "size"), sales=("total", "sum"))
    g = g.div(g.sum()).sort_values("sales")
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(g))
    h = 0.38
    ax.barh(y + h / 2 + 0.02, g["skus"], height=h, color=P.SERIES[0], label="share of SKUs")
    ax.barh(y - h / 2 - 0.02, g["sales"], height=h, color=P.SERIES[1], label="share of packs sold")
    ax.set_yticks(y, [_short(i, 40) for i in g.index])
    ax.xaxis.set_major_formatter(P.PERCENT)
    ax.set_title("ATC level-1 groups: assortment vs volume")
    ax.legend(loc="lower right")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def fig_seasonality(ds):
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    idx = seasonal_index(ds, "atc1")
    idx.index = [_short(i, 34) for i in idx.index]
    cmap = LinearSegmentedColormap.from_list("div", P.DIVERGING)
    fig, ax = plt.subplots(figsize=(9, 5))
    span = float(np.nanmax(np.abs(idx.to_numpy() - 1)))
    im = ax.imshow(idx.to_numpy(), cmap=cmap, norm=TwoSlopeNorm(1.0, 1 - span, 1 + span), aspect="auto")
    ax.set_xticks(range(12), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_yticks(range(len(idx)), idx.index)
    ax.grid(False)
    for (r, c), v in np.ndenumerate(idx.to_numpy()):
        ax.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                color="white" if abs(v - 1) > span * 0.6 else P.INK)
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label("seasonal index (1 = average month)")
    cb.outline.set_visible(False)
    ax.set_title("Within-year seasonal index by ATC level-1 group, 2019-2023")
    fig.tight_layout()
    return fig


def fig_lifecycle(ds):
    a = ds.attrs
    first = a.loc[a["first_t"] > 0, "first_sale"].dt.year.value_counts().sort_index()
    last = a.loc[(a["last_t"] >= 0) & (a["last_t"] < len(ds.dates) - 12), "last_sale"].dt.year.value_counts().sort_index()
    years = np.arange(2019, 2024)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    w = 0.36
    ax.bar(years - w / 2 - 0.02, first.reindex(years, fill_value=0), width=w, color=P.SERIES[0], label="first sale (launch)")
    ax.bar(years + w / 2 + 0.02, last.reindex(years, fill_value=0), width=w, color=P.SERIES[1], label="last sale (exit)")
    ax.set_xticks(years)
    ax.set_title("SKU entries and exits per year")
    ax.set_ylabel("SKUs")
    ax.legend(loc="upper right")
    ax.text(2023 + w / 2, 30, "censored", rotation=90, ha="center", fontsize=8, color=P.INK_2)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def fig_forms(ds):
    c = ds.attrs["nfc"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(range(len(c)), c.to_numpy(), color=P.SERIES[0], height=0.6)
    ax.set_yticks(range(len(c)), [_short(i, 40) for i in c.index])
    for k, v in enumerate(c.to_numpy()):
        ax.text(v + c.max() * 0.01, k, f"{v:,}", va="center", fontsize=8, color=P.INK_2)
    ax.set_title("SKUs by dosage form (NFC1)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, c.max() * 1.12)
    fig.tight_layout()
    return fig


def fig_launch_curve(ds):
    curve, n = launch_curve(ds)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.fill_between(curve["month_since_launch"], curve["q25"], curve["q75"], color=P.SERIES[0], alpha=0.12, lw=0,
                    label="interquartile range")
    ax.plot(curve["month_since_launch"], curve["median"], color=P.SERIES[0], marker="o", label="median")
    ax.axhline(1, color=P.AXIS, lw=0.8)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("month since first sale")
    ax.set_ylabel("sales / mean of months 7-12")
    ax.set_title(f"Ramp-up of new SKUs launched 2020-2022 (n = {n:,})")
    ax.legend(loc="lower right")
    fig.tight_layout()
    return fig


def fig_group_informativeness(ds):
    t = group_informativeness(ds)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    colors = [P.MUTED if g == "Form (NFC)" else (P.ARM_COLORS["atc"] if g.startswith("ATC") else P.ARM_COLORS["inn"])
              for g in t["grouping"]]
    bars = ax.bar(t["grouping"], t["LOO R2 (log mean sales)"], color=colors, width=0.6)
    for b, v in zip(bars, t["LOO R2 (log mean sales)"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center", fontsize=8, color=P.INK_2)
    ax.set_ylabel("leave-one-out R²")
    ax.set_title("How well the peer group predicts an unseen SKU's sales level")
    ax.set_ylim(0, max(0.05, t["LOO R2 (log mean sales)"].max() * 1.2))
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig
