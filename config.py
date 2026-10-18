"""Static configuration: data location, palette and the canonical category orders."""
from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("BI10_DATA_DIR", APP_DIR / "data"))

SAMPLE_FILE = "dashboard_sample.csv"
SAMPLE_FILE_GZ = "dashboard_sample.csv.gz"
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
    # GROW
    "Prime Champions", "Loyal Core", "Cautious Growers",
    # REACTIVATE
    "Sleeping Prime",
    # PROTECT
    "Silent Risk", "Credit-Hungry Stressed", "Credit-Hungry Newcomers", "Stretched Seekers",
    # BUILD
    "Dormant Unknowns", "New-to-Credit Explorers",
]

# ---- palette, lifted from the notebook so the dashboard matches the figures ----
C = {
    "blue": "#1668d6", "blue_lt": "#5aa0f0", "navy": "#12315c",
    "orange": "#eb6834", "aqua": "#12a37a", "yellow": "#e8a317",
    "magenta": "#e87ba4", "green": "#0d8a4f", "violet": "#6250d6", "red": "#d94141",
    "grey": "#97a4b8", "ink": "#13233d", "ink2": "#6a7a92", "surface": "#ffffff",
    "dim": "#dbe4f0",
}
SEQ = ["#d7e6fa", "#aecdf5", "#84b3ef", "#5aa0f0", "#2f7fe0", "#1668d6", "#0f4a9c"]

SEGMENT_COLOR = {
    "GROW": C["blue"], "REACTIVATE": C["blue_lt"],
    "PROTECT": C["orange"], "BUILD": C["yellow"],
}
TIER_COLOR = {
    "Distressed": C["red"], "Vulnerable": C["orange"], "Thin-file": C["grey"],
    "Stable": C["blue_lt"], "Resilient": C["blue"],
}
LEVEL_COLOR = {
    "Cooling": SEQ[1], "Warm": SEQ[3], "Active": SEQ[5], "Champion": C["navy"],
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=12, color=C["ink2"], family="Segoe UI, Inter, sans-serif"),
    margin=dict(l=6, r=6, t=14, b=6),
    hoverlabel=dict(font_size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                font=dict(size=11)),
)


def sample_path():
    """Prefer the committed gzipped sample; fall back to a local uncompressed one."""
    gz = DATA_DIR / SAMPLE_FILE_GZ
    return gz if gz.exists() else DATA_DIR / SAMPLE_FILE


def sample_available() -> bool:
    return sample_path().exists()
