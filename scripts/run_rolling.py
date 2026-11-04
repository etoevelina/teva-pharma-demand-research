"""Rolling, validation-selected protocol: for each test year, choose everything on the previous year.

For test 2022 the loss, tree counts, primary metadata arm and median calibration are chosen on 2021
(validation models trained on 2020); for test 2023 on 2022 (trained on 2020-2021). All ablation arms
are kept as exploratory results; the primary result is the arm selected on validation.
Writes results/protocol/rolling/ (predictions and one JSON record per run) and results/protocol/run_log.txt.

Usage:
    python scripts/run_rolling.py                          # both cycles, all scenarios (about 46 min on an Apple M2)
    python scripts/run_rolling.py --test-years 2023 --scenarios A B
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from teva_forecast import data, experiments as E, protocol as PR  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-years", nargs="+", type=int, default=list(PR.TEST_YEARS))
    parser.add_argument("--scenarios", nargs="+", default=PR.ROLLING_ORDER, choices=list(E.SCENARIOS))
    args = parser.parse_args()
    ds = data.load_processed("teva")
    for year in args.test_years:
        loss, table = PR.cycle_loss(ds, year)
        for scenario in args.scenarios:
            PR.execute(ds, "rolling", scenario, year, loss, E.arms_for(scenario), loss_table=table)
    PR.log("rolling protocol done")


if __name__ == "__main__":
    main()
