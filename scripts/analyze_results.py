"""Build result tables, ablation statistics, error analysis and figures from saved predictions.

Part 1 uses the original single split (results/predictions/, from scripts/run_experiments.py).
Part 2 uses the rolling, validation-selected protocol and the robustness studies
(results/protocol/, from scripts/run_rolling.py and scripts/run_robustness.py) and is skipped
when those runs are missing.

Usage: python scripts/analyze_results.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from teva_forecast import analysis as AN, config, data, plotting as P  # noqa: E402
from teva_forecast import protocol_analysis as PA  # noqa: E402

RESULTS_REPORT = config.ROOT / "reports" / "evaluation_protocol_results.md"


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


def save_figure(fig, name):
    P.save(fig, name)
    plt.close(fig)
    print("figure", name)


def protocol_results():
    """Tables and figures of the rolling validation-selected protocol and the robustness studies."""
    rolling = PA.load_records("rolling")
    if not rolling:
        print("skipped the rolling protocol (no runs in results/protocol/rolling)")
        return
    attrs = PA.load_attrs()
    long, selected, calibrated = PA.rolling_tables(rolling, attrs)
    write_table(long, "rolling_year_results")
    write_table(selected, "validation_selected_models")
    write_table(calibrated, "calibrated_baselines")
    nn0 = PA.n_vs_n0(rolling, attrs)
    if len(nn0):
        write_table(nn0, "scenario_n_vs_n0")
    empty = pd.DataFrame()
    model_runs, model_summary = (PA.model_seed_tables(rolling, PA.load_records("model_seeds"))
                                 if PA.load_records("model_seeds") else (empty, empty))
    fold_runs, fold_summary = (PA.fold_seed_tables(rolling, PA.load_records("fold_seeds"))
                               if PA.load_records("fold_seeds") else (empty, empty))
    placebo_runs, placebo_summary = (PA.placebo_tables(rolling, PA.load_records("placebo"), attrs)
                                     if PA.load_records("placebo") else (empty, empty))
    for name, table in (("model_seed_robustness", model_runs), ("model_seed_robustness_summary", model_summary),
                        ("fold_seed_robustness", fold_runs), ("fold_seed_robustness_summary", fold_summary),
                        ("shuffled_peer_placebo", placebo_runs), ("shuffled_peer_placebo_summary", placebo_summary)):
        if len(table):
            write_table(table, name)
    variability = PA.variability_summary(model_summary, fold_summary, placebo_summary)
    if len(variability):
        write_table(variability, "variability_summary")
    write_table(PA.paper_table(selected, calibrated, model_summary, fold_summary, placebo_summary),
                "paper_results_table", floatfmt=".3f")
    RESULTS_REPORT.write_text(PA.results_markdown(
        selected, calibrated, model_summary, fold_summary, placebo_summary, nn0, "scripts/analyze_results.py"))
    save_figure(PA.fig_selected_vs_calibrated(calibrated), "res_selected_vs_calibrated_median")
    if len(model_runs) or len(fold_runs):
        save_figure(PA.fig_variability(model_runs, fold_runs), "res_wape_variability")
    if len(placebo_runs):
        save_figure(PA.fig_placebo(placebo_runs), "res_placebo_true_vs_shuffled")


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
        save_figure(make(), name)
    protocol_results()


if __name__ == "__main__":
    main()
