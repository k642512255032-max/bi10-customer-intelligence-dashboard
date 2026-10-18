"""Segment focus: one source of truth for which segment is being featured.

Verified against sub_segment_profile.csv of RESULTS_PACK_v3:
    GROW        387,780 = Prime Champions (210,021) + Loyal Core (177,759)
    REACTIVATE  139,184 = Sleeping Prime (139,184)
    PROTECT     291,144 = Cautious Growers (124,676) + Credit-Hungry Stressed (44,822)
                          + Silent Risk (121,646)
    BUILD       182,420 = New-to-Credit Explorers (50,767) + Dormant Unknowns (131,653)
"""
from __future__ import annotations

import pandas as pd

from config import C, SEGMENT_COLOR

ALL = "All"

SEGMENT_SUBS = {
    "GROW": ["Prime Champions", "Loyal Core"],
    "REACTIVATE": ["Sleeping Prime"],
    "PROTECT": ["Cautious Growers", "Credit-Hungry Stressed", "Silent Risk"],
    "BUILD": ["New-to-Credit Explorers", "Dormant Unknowns"],
}
SUB_TO_SEGMENT = {s: seg for seg, subs in SEGMENT_SUBS.items() for s in subs}

# Only these metric tables are indexed by segment, so only these can be re-framed
# per segment with real population numbers. Verified against summary_metrics.json.
SEGMENT_INDEXED = {
    "segment_profile", "nba_by_segment", "opportunity_map", "call_allocation_forward",
}
SUBSEGMENT_INDEXED = {"sub_segment_profile", "call_allocation_forward_sub"}

# Below this many sample rows a chart is noise, not evidence.
MIN_ROWS = 200

# Badge kinds shown on every chart so the reader always knows what they are looking at.
BADGE_FILTERED = "filtered"
BADGE_HIGHLIGHT = "highlighted"
BADGE_WHOLE = "whole"


def is_active(focus: str | None) -> bool:
    return bool(focus) and focus != ALL


def as_segment(focus: str | None) -> str | None:
    """Map a focus value (segment OR sub-segment) to its parent segment."""
    if not is_active(focus):
        return None
    return focus if focus in SEGMENT_SUBS else SUB_TO_SEGMENT.get(focus)


def apply_focus(df: pd.DataFrame, focus: str | None) -> pd.DataFrame:
    """Filter the row-level sample. Weights survive filtering - keep using W."""
    if not is_active(focus):
        return df
    col = "SEGMENT" if focus in SEGMENT_SUBS else "SUB_SEGMENT"
    return df[df[col] == focus]


def highlight_colors(categories, focus: str | None, base: dict, dim: str = None) -> list:
    """Population tables: dim everything except the focused segment, never delete it."""
    dim = dim or C["dim"]
    seg = as_segment(focus)
    if seg is None:
        return [base.get(c, C["grey"]) for c in categories]
    return [base.get(c, C["grey"]) if c == seg else dim for c in categories]


def focus_color(focus: str | None) -> str:
    seg = as_segment(focus)
    return SEGMENT_COLOR.get(seg, C["blue"]) if seg else C["blue"]
