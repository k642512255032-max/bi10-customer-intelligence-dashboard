"""Cached loaders for the RESULTS_PACK, plus the population reweighting.

G1 - THE MOST IMPORTANT THING IN THIS FILE
dashboard_sample.csv is STRATIFIED: exactly 5,000 rows per SUB_SEGMENT regardless of
how big that sub-segment really is. Raw shares from it are wrong. Unweighted it claims
14.2% of customers are Distressed; the truth is 6.2%. Every share, mean or count must
go through the W column produced by add_weights().
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from config import DATA_DIR, METRICS_FILE, SAMPLE_FILE


@st.cache_data(show_spinner=False)
def load_metrics(data_dir: str = str(DATA_DIR)) -> dict:
    with open(Path(data_dir) / METRICS_FILE, encoding="utf-8") as fh:
        return json.load(fh)


@st.cache_data(show_spinner=False)
def load_csv(name: str, data_dir: str = str(DATA_DIR)) -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / name, encoding="utf-8")


@st.cache_data(show_spinner="Loading the customer sample...")
def load_sample(data_dir: str = str(DATA_DIR)) -> pd.DataFrame:
    """Row-level sample, already reweighted to the population. May be absent."""
    path = Path(data_dir) / SAMPLE_FILE
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        path,
        encoding="utf-8",
        low_memory=False,
        dtype={"SKP_CLIENT": "int64", "LIVE_STRESS_FLAG": "int8", "MATURING_90D": "int8"},
    )
    df["NBA_TRIGGER"] = df["NBA_TRIGGER"].fillna("None")          # G4: 81% null
    df["PROVINCE"] = df["PROVINCE"].fillna("Unknown")             # G5: 19.5% null
    sub = load_csv("sub_segment_profile.csv", data_dir)
    return add_weights(df, sub)


def add_weights(df: pd.DataFrame, sub_profile: pd.DataFrame) -> pd.DataFrame:
    """Weight each sampled row back to the population. See G1."""
    counts = df["SUB_SEGMENT"].value_counts()
    weights = sub_profile.set_index("SUB_SEGMENT")["customers"] / counts
    out = df.copy()
    out["W"] = out["SUB_SEGMENT"].map(weights).astype("float64")
    return out


def split_table(metrics: dict, key: str) -> pd.DataFrame:
    """Rehydrate a pandas split-orient table written by the notebook's log() helper."""
    blob = metrics[key]
    return pd.DataFrame(blob["data"], index=blob["index"], columns=blob["columns"])


def weighted_share(df: pd.DataFrame, col: str) -> pd.Series:
    """Population share per category. NEVER use value_counts(normalize=True) here."""
    if df.empty:
        return pd.Series(dtype="float64")
    return df.groupby(col, observed=True)["W"].sum() / df["W"].sum()


def weighted_mean(df: pd.DataFrame, col: str) -> float:
    if df.empty or df["W"].sum() == 0:
        return float("nan")
    return float((df[col] * df["W"]).sum() / df["W"].sum())


def ordered(s: pd.Series, order: list) -> pd.Series:
    """Reindex to a canonical order, dropping categories that are absent."""
    return s.reindex([c for c in order if c in s.index])
