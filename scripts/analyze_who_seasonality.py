"""Compare the seasonality of Teva pharmacy sales with WHO influenza and respiratory surveillance.

The confirmatory plan (groups, indicators, primary pairs, lags 0-2, sensitivity windows) is the
"pre-specified analysis plan" block below; its timing relative to the results is not independently
documented. Analyses added after the first results are labelled post hoc or exploratory and are
written to separate tables. The script reads the processed sales panel and WHO data only, and
writes results/tables/who_*.csv and results/figures/who_*.png.

Usage:
    python scripts/analyze_who_seasonality.py            # downloads WHO data if missing
    python scripts/analyze_who_seasonality.py --refresh  # re-download WHO data
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import config, data, plotting as P, who  # noqa: E402
from teva_forecast import who_figures as WF  # noqa: E402

# --- Pre-specified analysis plan ------------------------------------------------------------

# Country of the sales data and the evidence behind it: see reports/who_seasonality_comparison.md,
# Section 2. Formal correlations are only computed when status is not "not_established".
GEOGRAPHY = {"country": "UKR", "status": "supported_not_explicit"}

GROUPS = {
    # name: (ATC column, code prefixes, role, medical rationale)
    "R respiratory system": ("atc1", ("R ",), "primary", "requested ATC1 group"),
    "J anti-infectives (systemic)": ("atc1", ("J ",), "primary", "requested ATC1 group"),
    "R05 cough and cold": ("atc2", ("R05",), "primary", "symptomatic treatment of acute respiratory infections"),
    "R01 nasal preparations": ("atc2", ("R01",), "primary", "decongestants for upper respiratory infections"),
    "R02 throat preparations": ("atc2", ("R02",), "primary", "sore throat in upper respiratory infections"),
    "N02BB+N02BE antipyretics": ("atc4", ("N02B B", "N02B E"), "primary", "metamizole and paracetamol: fever and pain"),
    "J01 antibacterials": ("atc2", ("J01",), "primary", "respiratory infections are a main driver of outpatient antibiotic use"),
    "J05AH+J05AC influenza antivirals": ("atc4", ("J05A H", "J05A C"), "primary", "oseltamivir and rimantadine: influenza-specific"),
    "J05AX other antivirals": ("atc4", ("J05A X",), "primary", "mainly inosine pranobex, tilorone, enisamium, a Calamagrostis/Deschampsia preparation and umifenovir: marketed for acute respiratory viral infections"),
    "R06 antihistamines": ("atc2", ("R06",), "control", "seasonal but non-infectious (pollen allergy)"),
    "J05AB herpes antivirals": ("atc4", ("J05A B",), "control", "anti-infective without a respiratory link"),
    "C09 renin-angiotensin agents": ("atc2", ("C09",), "control", "chronic treatment, no expected epidemic link"),
    "A10 antidiabetics": ("atc2", ("A10",), "control", "chronic treatment, no expected epidemic link"),
}
INDICATORS = {
    # name: (column, log for anomalies, label, unit)
    "flu_positivity": ("flu_positivity", False, "Influenza positivity (FluNet)", "share of specimens positive"),
    "ari_per_100k": ("ari_per_100k", True, "ARI incidence (FluID)", "cases per 100,000 per month"),
    "ili_per_100k": ("ili_per_100k", True, "ILI incidence, sentinel (FluID)", "cases per 100,000 per month"),
}
PRIMARY_PAIRS = {
    "ari_per_100k": ["R respiratory system", "J anti-infectives (systemic)", "R05 cough and cold", "R01 nasal preparations",
                     "R02 throat preparations", "N02BB+N02BE antipyretics", "J01 antibacterials", "J05AX other antivirals"],
    "flu_positivity": ["R respiratory system", "J anti-infectives (systemic)", "R05 cough and cold", "N02BB+N02BE antipyretics",
                       "J05AH+J05AC influenza antivirals", "J05AX other antivirals"],
}
LAGS = [0, 1, 2]   # indicator in month t - lag against sales in month t; lag 0 is the a-priori expectation
SENSITIVITY = {
    "full period": [],
    "without COVID restrictions (2020-03..2021-12)": [who.ANOMALY_WINDOWS["covid_npi"]],
    "without war onset (2022-02..2022-12)": [who.ANOMALY_WINDOWS["war_onset"]],
    "without both": [who.ANOMALY_WINDOWS["covid_npi"], who.ANOMALY_WINDOWS["war_onset"]],
}

# --- Exploratory additions (not part of the pre-specified plan) ----------------------------------

LEADING_LAGS = [-2, -1]           # sales in month t vs indicator in month t + 2 / t + 1
COMMON_MONTH_LAGS = [-2, -1, 0, 1, 2]
# Dispensing of antibiotics by electronic prescription began on 1 August 2022 (paper prescriptions
# remained allowed until the end of 2022).
ANTIBIOTIC_RX_WINDOW = ("2022-08-01", "2023-12-01")


def write(df, name):
    df.to_csv(config.TABLES_DIR / f"{name}.csv", index=False)


def load_who(refresh):
    country = GEOGRAPHY["country"]
    if refresh or not (who.WHO_RAW_DIR / f"flunet_{country}.csv").exists():
        who.download_who(country)
    flunet = pd.read_csv(who.WHO_RAW_DIR / f"flunet_{country}.csv", low_memory=False)
    fluid = pd.read_csv(who.WHO_RAW_DIR / f"fluid_{country}.csv", low_memory=False)
    provenance = json.loads((who.WHO_RAW_DIR / "provenance.json").read_text())
    return flunet, fluid, provenance


def window(df):
    return df.loc[who.PERIOD[0]:who.PERIOD[1]]


def indicator_series(indicators, key):
    """Indicator on the analysis scale: log for incidence rates, as is for positivity."""
    col, log_epi = INDICATORS[key][0], INDICATORS[key][1]
    series = indicators[col]
    return np.log(series.where(series > 0)) if log_epi else series


def summary_table(res, rel):
    """One row per group: the lag-0 full-period results used in the paper, plus the robustness checks."""
    def pick(df, name, key, kind, period="full period"):
        r = df[(df["group"] == name) & (df["indicator"] == key) & (df["series"] == kind)
               & (df["lag_months"] == 0) & (df["period"] == period)]
        return r.iloc[0] if len(r) else None

    out = []
    for name, (_c, _p, role, _r) in GROUPS.items():
        row = {"group": name, "role": role}
        for key in ("ari_per_100k", "flu_positivity"):
            row[f"{key}_primary_pair"] = name in PRIMARY_PAIRS[key]
            for kind in ("levels", "anomalies"):
                r = pick(res, name, key, kind)
                tag = f"{key}_{kind}"
                row[f"{tag}_rho"] = r["spearman"]
                row[f"{tag}_ci"] = f"[{r['spearman_ci_lo']:.2f}, {r['spearman_ci_hi']:.2f}]"
                row[f"{tag}_p_perm"] = r["p_year_permutation"]
                rr = pick(rel, name, key, kind)
                row[f"{key}_relative_{kind}_rho"] = rr["spearman"] if rr is not None else np.nan
                row[f"{key}_relative_{kind}_p_perm"] = rr["p_year_permutation"] if rr is not None else np.nan
        for period, tag in (("without war onset (2022-02..2022-12)", "without_war_onset"), ("without both", "without_both_windows")):
            r = pick(res, name, "ari_per_100k", "levels", period)
            row[f"ari_levels_rho_{tag}"], row[f"ari_levels_p_perm_{tag}"] = r["spearman"], r["p_year_permutation"]
            rr = pick(rel, name, "ari_per_100k", "levels", period)
            row[f"ari_relative_levels_rho_{tag}"] = rr["spearman"] if rr is not None else np.nan
            row[f"ari_relative_levels_p_perm_{tag}"] = rr["p_year_permutation"] if rr is not None else np.nan
        row["ari_n"] = int(pick(res, name, "ari_per_100k", "levels")["n"])
        row["flu_n"] = int(pick(res, name, "flu_positivity", "levels")["n"])
        out.append(row)
    return pd.DataFrame(out)


def exploratory(sales, indicators):
    """Analyses added after the first results: sales-leading lags, lags on common months, antibiotic rule."""
    rows = []
    for key in INDICATORS:
        y_avail = indicators[INDICATORS[key][0]].notna()
        common = np.logical_and.reduce([y_avail.shift(lag, fill_value=False).to_numpy() for lag in COMMON_MONTH_LAGS])
        for name, (_c, _p, role, _r) in GROUPS.items():
            x, y = np.log(sales[name]), indicator_series(indicators, key)
            for kind in ("levels", "anomalies"):
                for lag in LEADING_LAGS:
                    rows.append({"analysis": "sales leading the indicator (negative lags)", "indicator": key, "group": name,
                                 "role": role, "lag_months": lag, "period": "full period", "series": kind,
                                 **who.correlate(x, y, lag, anomaly=kind == "anomalies")})
                for lag in COMMON_MONTH_LAGS:
                    rows.append({"analysis": "lags -2..2 on the months where the indicator exists at every lag",
                                 "indicator": key, "group": name, "role": role, "lag_months": lag, "period": "common months",
                                 "series": kind, **who.correlate(x.where(common), y, lag, anomaly=kind == "anomalies")})
                if name in ("J01 antibacterials", "J anti-infectives (systemic)"):
                    keep = who.exclude_windows(sales.index, [ANTIBIOTIC_RX_WINDOW])
                    rows.append({"analysis": "antibiotics: without the e-prescription period", "indicator": key,
                                 "group": name, "role": role, "lag_months": 0,
                                 "period": "without e-prescription period (2022-08..2023-12)", "series": kind,
                                 **who.correlate(x, y, 0, keep, anomaly=kind == "anomalies")})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--figures-only", action="store_true", help="redraw figures from the saved tables")
    args = parser.parse_args()
    P.apply_style()
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    if args.figures_only:
        monthly = pd.read_csv(config.TABLES_DIR / "who_monthly_series.csv", parse_dates=["month"]).set_index("month")
        sales = monthly[[c for c in monthly if c.startswith("sales: ")]].rename(columns=lambda c: c[len("sales: "):])
        indicators = monthly[[c for c in monthly if not c.startswith("sales: ")]]
        profiles = pd.read_csv(config.TABLES_DIR / "who_seasonal_profiles.csv").set_index("month")
        res = pd.read_csv(config.TABLES_DIR / "who_correlations.csv")
        WF.make_all_figures(sales, indicators, profiles, res, GROUPS, INDICATORS, PRIMARY_PAIRS)
        rel = pd.read_csv(config.TABLES_DIR / "who_correlations_relative_to_chronic.csv")
        write(summary_table(res, rel), "who_summary_table")
        print("figures and summary table redrawn")
        return

    ds = data.load_processed("teva")
    sales = window(who.sales_by_group(ds, {k: v[:2] for k, v in GROUPS.items()}))
    flunet, fluid, provenance = load_who(args.refresh)
    write(pd.DataFrame(provenance), "who_provenance")

    flu = window(who.flunet_monthly(flunet))
    flu_sentinel = window(who.flunet_monthly(flunet, source="SENTINEL"))
    epi = window(who.fluid_monthly(fluid))
    indicators = pd.concat([flu[["flu_specimens", "flu_positives", "flu_positivity", "rsv_specimens", "rsv_positivity"]],
                            flu_sentinel[["flu_positivity"]].rename(columns={"flu_positivity": "flu_positivity_sentinel"}),
                            epi[["ari_per_100k", "ili_per_100k", "sari_per_100_inpatients", "ARI_POP_COV", "ILI_POP_COV"]]],
                           axis=1).reindex(sales.index)
    monthly = pd.concat([sales.add_prefix("sales: "), indicators], axis=1).reset_index()
    write(monthly, "who_monthly_series")
    write(who.indicator_availability(indicators), "who_indicator_availability")

    # 1. Seasonality of the sales data (robustness of the EDA finding).
    write(who.atc1_seasonality_stability(ds), "who_atc1_seasonality_stability")
    profiles = pd.DataFrame({name: who.seasonal_index(sales[name]) for name in GROUPS})
    profiles["C09+A10 chronic basket"] = who.seasonal_index(sales["C09 renin-angiotensin agents"] + sales["A10 antidiabetics"])
    for key, (col, _log, _label, _unit) in INDICATORS.items():
        profiles[key] = who.seasonal_index(indicators[col])
    write(profiles.rename_axis("month").reset_index(), "who_seasonal_profiles")
    write(pd.DataFrame([{"group": k, "atc_column": v[0], "codes": " / ".join(v[1]).strip(), "role": v[2],
                         "rationale": v[3]} for k, v in GROUPS.items()]), "who_atc_indicator_mapping_groups")

    if GEOGRAPHY["status"] == "not_established":
        print("geography not established: formal correlations skipped")
        WF.make_overview_figures(sales, indicators, profiles)
        return

    # 2-6. Correlations, lags, sensitivity windows, common seasonality.
    rows = []
    for key in INDICATORS:
        for name, (_c, _p, role, _r) in GROUPS.items():
            primary = name in PRIMARY_PAIRS.get(key, [])
            x, y = np.log(sales[name]), indicator_series(indicators, key)
            for lag in LAGS:
                for period, windows in SENSITIVITY.items():
                    keep = who.exclude_windows(sales.index, windows)
                    for kind in ("levels", "anomalies"):
                        stats = who.correlate(x, y, lag, keep, anomaly=kind == "anomalies")
                        rows.append({"indicator": key, "group": name, "role": role, "primary_pair": primary,
                                     "lag_months": lag, "period": period, "series": kind, **stats})
    res = pd.DataFrame(rows)
    family = (res["primary_pair"] & (res["lag_months"] == 0) & (res["period"] == "full period"))
    for kind in ("levels", "anomalies"):
        sel = family & (res["series"] == kind) & res["p_spearman_neff"].notna()
        res.loc[sel, "q_bh_primary"] = who.benjamini_hochberg(res.loc[sel, "p_spearman_neff"])
    write(res, "who_correlations")

    # Post hoc (not pre-specified): demand relative to a chronic-treatment basket. Added after the
    # control groups were seen to correlate with ARI, to ask whether the association survives
    # dividing by the sales of drugs without an expected epidemic link (C09 + A10). The basket has
    # its own seasonality and its own reaction to the shocks, so the ratio does not isolate
    # infection-driven demand.
    basket = sales["C09 renin-angiotensin agents"] + sales["A10 antidiabetics"]
    rel_rows = []
    for key in PRIMARY_PAIRS:
        y = indicator_series(indicators, key)
        for name in GROUPS:
            if GROUPS[name][2] != "primary" and name not in ("R06 antihistamines", "J05AB herpes antivirals"):
                continue
            x = np.log(sales[name] / basket)
            for period, windows in SENSITIVITY.items():
                keep = who.exclude_windows(sales.index, windows)
                for kind in ("levels", "anomalies"):
                    rel_rows.append({"indicator": key, "group": name, "role": GROUPS[name][2], "lag_months": 0,
                                     "period": period, "series": kind, "analysis": "post hoc: sales / (C09 + A10)",
                                     **who.correlate(x, y, 0, keep, anomaly=kind == "anomalies")})
    rel = pd.DataFrame(rel_rows)
    write(rel, "who_correlations_relative_to_chronic")
    write(exploratory(sales, indicators), "who_correlations_exploratory")
    write(summary_table(res, rel), "who_summary_table")
    WF.make_all_figures(sales, indicators, profiles, res, GROUPS, INDICATORS, PRIMARY_PAIRS)
    print("done:", len(res), "correlation rows")


if __name__ == "__main__":
    main()
