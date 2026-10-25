"""Write the dataset description tables and EDA figures to results/.

Usage: python scripts/make_eda.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import config, data, eda, plotting as P  # noqa: E402


def write_table(df, name):
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.TABLES_DIR / f"{name}.csv", index=False)
    (config.TABLES_DIR / f"{name}.md").write_text(df.to_markdown(index=False, floatfmt=".3f") + "\n")


def main():
    P.apply_style()
    raw_path = data.download_raw("full")
    attrs, raw_sales, dates = data.load_wide(raw_path)
    raw_shape = pd.read_csv(raw_path, nrows=0).shape[1]
    ds = data.load_processed("teva")

    write_table(eda.dataset_characteristics(ds, (len(attrs), raw_shape)), "dataset_characteristics")
    write_table(eda.hierarchy_table(ds), "hierarchy_levels")
    write_table(eda.quality_report(ds, raw_sales), "data_quality")
    write_table(eda.parse_coverage(ds), "description_parsing_coverage")
    write_table(eda.hierarchy_checks(ds), "hierarchy_checks")
    write_table(eda.launch_composition(ds), "launch_composition")
    write_table(eda.key_numbers(ds), "eda_key_numbers")
    write_table(eda.atc1_composition(ds), "atc1_composition")
    write_table(eda.source_files_check(raw_path, data.download_raw("small")), "source_files_check")
    audit = eda.parsing_audit_sample(ds)
    verdicts = config.ROOT / "reports" / "description_parsing_audit.csv"
    if verdicts.exists():
        audit = audit.merge(pd.read_csv(verdicts)[["sku", "manual_check"]], on="sku", how="left")
    write_table(audit, "description_parsing_audit_sample")
    write_table(eda.group_informativeness(ds), "group_informativeness")
    write_table(eda.seasonal_index(ds, "atc1").reset_index(names="atc1"), "seasonal_index_atc1")
    ac = eda.lag12_autocorrelation(ds)
    write_table(ac.describe().rename("value").rename_axis("statistic").reset_index(), "lag12_autocorrelation_summary")
    curve, n = eda.launch_curve(ds)
    write_table(curve.assign(n_skus=n), "launch_curve")

    figures = {
        "eda_monthly_total": eda.fig_monthly_total,
        "eda_sku_distribution": eda.fig_sku_distribution,
        "eda_hierarchy": eda.fig_hierarchy,
        "eda_atc1_composition": eda.fig_atc1_composition,
        "eda_seasonality_atc1": eda.fig_seasonality,
        "eda_lifecycle": eda.fig_lifecycle,
        "eda_dosage_forms": eda.fig_forms,
        "eda_launch_curve": eda.fig_launch_curve,
        "eda_group_informativeness": eda.fig_group_informativeness,
    }
    for name, fn in figures.items():
        fig = fn(ds)
        P.save(fig, name)
        plt.close(fig)
        print("figure", name)


if __name__ == "__main__":
    main()
