"""Static configuration: data location, palette and the canonical category orders."""
from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("BI10_DATA_DIR", APP_DIR / "data"))

SAMPLE_FILE = "dashboard_sample.csv"
METRICS_FILE = "summary_metrics.json"

# Aggregate tables; these carry no personal data and are safe to publish.
AGGREGATE_FILES = [
    METRICS_FILE,
    "segment_profile.csv",
    "sub_segment_profile.csv",
    "matrix_fhs_es.csv",
    "opportunity_map.csv",
    "call_allocation_by_segment.csv",
    "fhs_scorecard.csv",
    "figure_index.csv",
]

# ---- canonical orderings (never rely on alphabetical order from a CSV) ----
FHS_TIERS = ["Distressed", "Vulnerable", "Thin-file", "Stable", "Resilient"]
ES_LEVELS = ["Cooling", "Warm", "Active", "Champion"]
SEGMENTS = ["GROW", "REACTIVATE", "PROTECT", "BUILD"]
SUB_SEGMENTS = [
    "Prime Champions", "Loyal Core", "Sleeping Prime", "Cautious Growers",
    "Credit-Hungry Stressed", "Silent Risk", "New-to-Credit Explorers", "Dormant Unknowns",
]

# ---- palette, lifted from the notebook so the dashboard matches the figures ----
C = {
    "blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
    "magenta": "#e87ba4", "green": "#008300", "violet": "#6250d6", "red": "#e34948",
    "grey": "#8a8984", "ink": "#0b0b0b", "ink2": "#52514e", "surface": "#fcfcfb",
    "dim": "#d8d6cf",
}
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

SEGMENT_COLOR = {
    "GROW": C["aqua"], "REACTIVATE": C["blue"], "PROTECT": C["orange"], "BUILD": C["yellow"],
}
TIER_COLOR = {
    "Distressed": C["red"], "Vulnerable": C["orange"], "Thin-file": C["grey"],
    "Stable": C["blue"], "Resilient": C["aqua"],
}
LEVEL_COLOR = {
    "Cooling": SEQ[1], "Warm": SEQ[2], "Active": SEQ[4], "Champion": SEQ[6],
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=13, color=C["ink2"]),
    margin=dict(l=10, r=10, t=36, b=10),
    hoverlabel=dict(font_size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
)


def sample_available() -> bool:
    """The customer-level sample is git-ignored; the deployed app runs without it."""
    return (DATA_DIR / SAMPLE_FILE).exists()
