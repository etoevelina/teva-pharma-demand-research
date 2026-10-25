"""Download the raw Teva CSV, validate and clean it, and write the processed parquet files.

Usage: python scripts/prepare_data.py [--dataset full|small]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from teva_forecast import data  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["full", "small"], default="full")
    args = parser.parse_args()

    path = data.download_raw(args.dataset)
    attrs, sales, dates = data.load_wide(path)
    ds = data.build_dataset(attrs, sales, dates)
    prefix = "teva" if args.dataset == "full" else "teva_small"
    attrs_path, panel_path = data.save_processed(ds, prefix=prefix)

    a = ds.attrs
    print(f"raw file:        {path}")
    print(f"SKUs:            {len(a):,}")
    print(f"INNs:            {a['inn'].nunique():,}")
    print(f"months:          {dates[0]:%Y-%m} .. {dates[-1]:%Y-%m}")
    print(f"on-market cells: {int((~__import__('numpy').isnan(ds.sales)).sum()):,}")
    print(f"strength parsed: {a['strength_unit'].ne('none').mean():.1%}")
    print(f"pack parsed:     {a['pack_count'].notna().mean():.1%}")
    print(f"written:         {attrs_path.name}, {panel_path.name}")


if __name__ == "__main__":
    main()
