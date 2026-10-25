"""Download, validation, cleaning and description parsing for the Teva sales data."""
import hashlib
import re
import urllib.request
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config

ATTRIBUTE_COLUMNS = {
    "Morion ID": "sku",
    "ATC Code (1)": "atc1",
    "ATC Code (2)": "atc2",
    "ATC Code (3)": "atc3",
    "ATC Code (4)": "atc4",
    "ATC Code (5)": "atc5",
    "Brand": "brand",
    "INN": "inn",
    "NFC (1)": "nfc",
    "Description": "description",
}
MONTH_PATTERN = re.compile(r"^\d{4} \d{2}$")
TWIN_KEY = ["atc5", "brand", "inn", "nfc", "description"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_raw(dataset="full", force=False):
    """Download a raw CSV from the source repository and verify its checksum."""
    name, expected = config.RAW_FILES[dataset]
    path = config.RAW_DIR / name
    if path.exists() and not force and sha256(path) == expected:
        return path
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(f"{config.RAW_BASE_URL}/{name}", path)
    digest = sha256(path)
    if digest != expected:
        raise ValueError(f"Checksum mismatch for {name}: {digest} != {expected}")
    return path


def load_wide(path):
    """Read the wide CSV, validate its schema and split it into attributes and a sales matrix."""
    raw = pd.read_csv(path)
    missing = [c for c in ATTRIBUTE_COLUMNS if c not in raw.columns]
    assert not missing, f"Missing attribute columns: {missing}"
    months = [c for c in raw.columns if MONTH_PATTERN.match(str(c))]
    assert len(months) == config.N_MONTHS, f"Expected {config.N_MONTHS} month columns, found {len(months)}"
    dates = pd.to_datetime(months, format="%Y %m")
    assert dates[0] == pd.Timestamp(config.FIRST_MONTH)
    assert (np.diff(dates.year * 12 + dates.month) == 1).all(), "Month columns are not consecutive"
    assert raw["Morion ID"].is_unique, "Morion ID must identify an SKU"
    attrs = raw[list(ATTRIBUTE_COLUMNS)].rename(columns=ATTRIBUTE_COLUMNS).reset_index(drop=True)
    sales = raw[months].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    return attrs, sales, dates


PLACEHOLDERS = {"-", ""}
CODED_COLUMNS = ["atc1", "atc2", "atc3", "atc4", "atc5", "inn", "nfc"]


def clean_attributes(attrs):
    """Strip whitespace (including non-breaking spaces) and turn placeholder codes into missing values.

    The raw file marks products without an INN with a non-breaking space followed by '-'
    (931 SKUs) and uses the same placeholder for 14 missing ATC4 codes.
    """
    attrs = attrs.copy()
    for col in CODED_COLUMNS + ["description"]:
        attrs[col] = attrs[col].astype(str).str.replace("\xa0", " ").str.strip()
    for col in CODED_COLUMNS:
        attrs[col] = attrs[col].where(~attrs[col].isin(PLACEHOLDERS))
    return attrs


# --- Description parsing -------------------------------------------------------------
# Heuristic parser for free-text product descriptions such as
# "tabs coated w/film 20 mg blister, #30" or "sol. for inj. 50 mg/2 ml amp. 2 ml, #10".

_NUM = r"(\d+(?:\.\d+)?)"
_MASS = {"mcg": 0.001, "µg": 0.001, "ug": 0.001, "mg": 1.0, "g": 1000.0}
_STRENGTH = re.compile(
    _NUM + r"\s*(mcg|µg|ug|mg|g|iu|me|units?|%)(?![a-z])"
    r"(?:\s*/\s*(?:" + _NUM + r"\s*)?(ml|dose|g|hour|h)\b)?"
)
_CONTAINER = re.compile(
    r"\b(blister|amp\.|ampoules?|flask|fl\.|bot\.|bottle|tube|cont\.|container|bag|sachet|pack|jar|"
    r"cartridge|syringe|syr\.|can\.|strip|inhaler|cylinder|vial|env\.|box|pen|applicat\.)"
)
_CONTENT = re.compile(r"(?<![/\d.])" + _NUM + r"\s*(ml|l|g)\b(?!\s*/)")
_DOSES = re.compile(r"(\d+)\s*doses\b")
_PACK = re.compile(r"#\s*(\d+)")


_CYRILLIC_UNITS = [("мкг", "mcg"), ("мг", "mg"), ("мл", "ml"), ("ае", "iu"), ("ме", "iu"), ("г", "g"), ("№", "#")]


def _normalise_text(text):
    text = str(text).lower().replace("\xa0", " ")
    for cyr, lat in _CYRILLIC_UNITS:
        text = re.sub(rf"(?<=[\d\s/+]){cyr}(?![а-яё])", lat, text)
    return re.sub(r"(?<=\d),(?=\d)", ".", text)


def parse_description(text):
    """Extract strength, package content, number of doses and pack count from a description."""
    s = _normalise_text(text)
    container = _CONTAINER.search(s)
    container_pos = container.start() if container else len(s)

    strengths = [m for m in _STRENGTH.finditer(s) if m.start() < container_pos]
    out = {
        "strength_value": np.nan,
        "strength_unit": "none",
        "multi_strength": 0,
        "content_value": np.nan,
        "content_unit": "none",
        "n_doses": np.nan,
        "pack_count": np.nan,
    }
    if strengths:
        m = strengths[0]
        value, unit, per_value, per_unit = float(m.group(1)), m.group(2), m.group(3), m.group(4)
        if unit in _MASS:
            value, base = value * _MASS[unit], "mg"
        elif unit == "%":
            base = "%"
        else:
            base = "IU"
        if per_unit:
            divisor = float(per_value) if per_value else 1.0
            per = {"ml": "ml", "g": "g", "dose": "dose", "hour": "h", "h": "h"}[per_unit]
            value, base = value / divisor, f"{base}/{per}"
        out.update(strength_value=value, strength_unit=base, multi_strength=int(len(strengths) > 1))

    used = [(m.start(), m.end()) for m in strengths]
    contents = [m for m in _CONTENT.finditer(s) if not any(a <= m.start() < b for a, b in used)]
    contents = [m for m in contents if m.start() >= container_pos] or contents
    if contents:
        m = contents[-1]
        value, unit = float(m.group(1)), m.group(2)
        if unit == "l":
            value, unit = value * 1000.0, "ml"
        out.update(content_value=value, content_unit=unit)

    doses = _DOSES.search(s)
    if doses:
        out["n_doses"] = float(doses.group(1))
    packs = _PACK.findall(s)
    if packs:
        out["pack_count"] = float(packs[-1])
    return out


# --- Cleaned dataset --------------------------------------------------------------------

@dataclass
class Dataset:
    attrs: pd.DataFrame          # one row per SKU, positional index aligned with `sales`
    sales: np.ndarray            # (n_sku, 60) packs sold; NaN before the first sale (not yet on market)
    dates: pd.DatetimeIndex

    @property
    def sales0(self):
        return np.nan_to_num(self.sales, nan=0.0)


def build_dataset(attrs, sales, dates):
    """Clean the raw matrix, derive lifecycle fields and parse product descriptions."""
    assert not np.isnan(sales).any(), "Raw data unexpectedly contain missing sales"
    assert (sales >= 0).all(), "Raw data unexpectedly contain negative sales"
    attrs = clean_attributes(attrs)
    positive = sales > 0
    has_sales = positive.any(axis=1)
    first_t = np.where(has_sales, positive.argmax(axis=1), -1)
    last_t = np.where(has_sales, sales.shape[1] - 1 - positive[:, ::-1].argmax(axis=1), -1)
    attrs["first_t"] = first_t
    attrs["last_t"] = last_t
    attrs["first_sale"] = dates[first_t]
    attrs["last_sale"] = dates[last_t]
    attrs["launch_observed"] = (first_t > 0).astype(int)
    attrs["twin_cluster"] = attrs.groupby(TWIN_KEY, sort=False, dropna=False).ngroup()
    attrs["twin_size"] = attrs.groupby("twin_cluster")["sku"].transform("size")
    attrs["inn_missing"] = attrs["inn"].isna().astype(int)
    attrs["n_ingredients"] = attrs["inn"].str.count(r"\+") + 1
    # Unit for "new INN" splits: the INN, or the twin cluster for products without an INN.
    attrs["inn_unit"] = attrs["inn"].fillna("no INN, twin " + attrs["twin_cluster"].astype(str))

    parsed = pd.DataFrame([parse_description(d) for d in attrs["description"]])
    attrs = pd.concat([attrs, parsed], axis=1)

    clean = sales.astype(float).copy()
    months = np.arange(sales.shape[1])
    clean[months[None, :] < first_t[:, None]] = np.nan
    return Dataset(attrs=attrs, sales=clean, dates=dates)


def to_long(ds):
    """Long SKU x month panel for storage and EDA."""
    n_sku, n_t = ds.sales.shape
    long = pd.DataFrame({
        "sku": np.repeat(ds.attrs["sku"].to_numpy(), n_t),
        "date": np.tile(ds.dates.to_numpy(), n_sku),
        "t": np.tile(np.arange(n_t), n_sku),
        "sales": ds.sales0.ravel(),
        "on_market": ~np.isnan(ds.sales).ravel(),
    })
    return long


def save_processed(ds, prefix="teva"):
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    attrs_path = config.PROCESSED_DIR / f"{prefix}_sku_attributes.parquet"
    panel_path = config.PROCESSED_DIR / f"{prefix}_sales_panel.parquet"
    ds.attrs.to_parquet(attrs_path, index=False)
    long = to_long(ds)
    long["sales"] = long["sales"].astype("float32")
    long.to_parquet(panel_path, index=False)
    return attrs_path, panel_path


def load_processed(prefix="teva"):
    attrs = pd.read_parquet(config.PROCESSED_DIR / f"{prefix}_sku_attributes.parquet")
    long = pd.read_parquet(config.PROCESSED_DIR / f"{prefix}_sales_panel.parquet")
    n_t = config.N_MONTHS
    order = pd.Series(np.arange(len(attrs)), index=attrs["sku"])
    long = long.assign(pos=order.loc[long["sku"]].to_numpy()).sort_values(["pos", "t"])
    sales = long["sales"].to_numpy(dtype=float).reshape(len(attrs), n_t)
    sales[~long["on_market"].to_numpy().reshape(len(attrs), n_t)] = np.nan
    dates = pd.DatetimeIndex(long["date"].iloc[:n_t].to_numpy())
    return Dataset(attrs=attrs, sales=sales, dates=dates)
