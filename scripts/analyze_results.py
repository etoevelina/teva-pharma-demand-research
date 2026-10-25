"""Build result tables, ablation statistics, error analysis and figures from saved predictions.

Usage: python scripts/analyze_results.py   (run after scripts/run_experiments.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import analysis as AN, config, data, plotting as P  # noqa: E402


def write_table(df, name, floatfmt=".4f"):
    df.to_csv(config.TABLES_DIR / f"{name}.csv", index=False)
    (config.TABLES_DIR / f"{name}.md").write_text(df.to_markdown(index=False, floatfmt=floatfmt) + "\n")


def results_matrix(overall, metric):
    t = overall[overall["split"] == "test"].pivot(index="model", columns="scenario", values=metric)
    order = list(dict.fromkeys(["zero_forecast"] + AN.EXISTING_BASELINES + AN.COLD_BASELINES + ["launch_age_mean"]
                               + [f"catboost_{a}" for a in AN.ARMS + [AN.CODES_ARM]]))
    t = t.reindex([m for m in order if m in t.index])[[s for s in AN.SCENARIO_ORDER if s in t.columns]]
    t.index = [AN.MODEL_LABELS[m] for m in t.index]
    return t.reset_index(names="model")


def main():
    P.apply_style()
    preds = AN.load_predictions()
    overall = AN.overall_metrics(preds)
    write_table(overall, "metrics_overall")
    folds = AN.fold_metrics(preds)
    write_table(folds, "metrics_by_fold")
    spread = (folds[folds["split"] == "test"].groupby(["scenario", "model"])["WAPE"]
              .agg(["mean", "std", "min", "max"]).reset_index())
    write_table(spread, "wape_fold_spread")
    for metric in ("WAPE", "MAE", "RMSE", "bias", "WAPE_annual", "spearman_annual"):
        write_table(results_matrix(overall, metric), f"results_test_{metric.lower()}", floatfmt=".3f")

    ablation = AN.ablation_table(preds, overall)
    write_table(ablation, "ablation_inn_atc")
    br = AN.error_breakdowns(preds, overall)["breakdowns"]
    write_table(br, "error_breakdowns")
    for s, model in (("A", "catboost_both"), ("B", "catboost_both"), ("C", "catboost_both"), ("N", "catboost_both")):
        if (s, "test") in preds:
            write_table(AN.inn_errors(preds, s, model), f"inn_errors_{s}")

    robustness_file = config.TABLES_DIR / "robustness_trees_seeds.csv"
    curves = pd.read_csv(robustness_file) if robustness_file.exists() else None
    if curves is not None:
        write_table(AN.robustness_summary(curves), "robustness_summary")

    importance = pd.read_csv(config.TABLES_DIR / "feature_importance.csv")
    ds = data.load_processed("teva")
    figures = {
        "res_overview_wape": lambda: AN.fig_overview(overall),
        "res_ablation_inn_atc": lambda: AN.fig_ablation(ablation),
        "res_actual_vs_predicted": lambda: AN.fig_actual_vs_predicted(preds),
        "res_aggregate_test_2023": lambda: AN.fig_aggregate(preds, overall),
        "res_examples_existing": lambda: AN.fig_examples(preds, ds, "A"),
        "res_examples_new_sku": lambda: AN.fig_examples(preds, ds, "B"),
        "res_error_by_atc1": lambda: AN.fig_error_by_atc1(br),
        "res_c_known_atc_depth": lambda: AN.fig_known_depth(br),
        "res_feature_importance": lambda: AN.fig_importance(importance),
        "res_launch_age": lambda: AN.fig_launch_age(preds),
    }
    if curves is not None:
        figures["res_robustness_trees_seeds"] = lambda: AN.fig_robustness(curves)
    needs = {"res_examples_existing": "A", "res_examples_new_sku": "B", "res_c_known_atc_depth": "C",
             "res_launch_age": "N"}
    for name, make in figures.items():
        if name in needs and (needs[name], "test") not in preds:
            print("skipped", name, "(scenario not run)")
            continue
        fig = make()
        P.save(fig, name)
        plt.close(fig)
        print("figure", name)


if __name__ == "__main__":
    main()
