"""Sprint 1/2 — Dataset finalization & preprocessing (10/8/26 – 22/8/26).
Cleans raw samples: drops duplicates, removes negative readings, fills missing
values with the column median, and adds HPI/NPI reference labels for ML training.
Run from repo root:  python ml/preprocess.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from hpi import STANDARDS, calculate  # noqa: E402

METALS = list(STANDARDS)


def preprocess(df):
    df = df.drop_duplicates().copy()
    df[METALS] = df[METALS].apply(pd.to_numeric, errors="coerce")
    df[METALS] = df[METALS].mask(df[METALS] < 0)          # negative = sensor error
    df[METALS] = df[METALS].fillna(df[METALS].median())
    labels = df[METALS].apply(lambda r: pd.Series(calculate(r.to_dict())), axis=1)
    return pd.concat([df, labels], axis=1)


if __name__ == "__main__":
    raw = pd.read_csv(ROOT / "data" / "sample_water_samples.csv")
    clean = preprocess(raw)
    assert clean[METALS].isna().sum().sum() == 0 and (clean[METALS] >= 0).all().all()
    clean.to_csv(ROOT / "data" / "processed_samples.csv", index=False)
    print(f"{len(raw)} raw rows -> {len(clean)} clean rows")
    print(clean[["location", "hpi", "npi", "hpi_class"]].to_string(index=False))
