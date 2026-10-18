"""Display helpers: number formatting, KPI rows, and the standard chart block."""
from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from focus import BADGE_FILTERED, BADGE_HIGHLIGHT, BADGE_WHOLE, MIN_ROWS
from strings import t


def _missing(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x)) or pd.isna(x)


def vnd(x) -> str:
    """VND are large; always render in millions."""
    if _missing(x) or x == 0:
        return "-"
    return f"{x / 1e6:,.1f}M VND"


def pct(x, d: int = 1) -> str:
    return "-" if _missing(x) else f"{100 * x:.{d}f}%"


def num(x, d: int = 0) -> str:
    return "-" if _missing(x) else f"{x:,.{d}f}"


def auc_plain(a, lang: str) -> str:
    """Turn an AUC into a sentence a beginner understands."""
    return "-" if _missing(a) else t("ui.auc_plain", lang, n=round(100 * a))


def kpi_row(items: list[tuple[str, str]], help_texts: list[str] | None = None) -> None:
    cols = st.columns(len(items))
    for i, (label, value) in enumerate(items):
        with cols[i]:
            st.metric(label, value, help=(help_texts[i] if help_texts else None))


BADGE_STYLE = {
    BADGE_FILTERED: ("#1baf7a", "#e8f6f1"),
    BADGE_HIGHLIGHT: ("#eb6834", "#fdefe9"),
    BADGE_WHOLE: ("#52514e", "#f1efe8"),
}


def badge(kind: str, lang: str) -> None:
    """Tell the reader exactly what the chart below is showing."""
    fg, bg = BADGE_STYLE.get(kind, BADGE_STYLE[BADGE_WHOLE])
    label = t(f"ui.badge.{kind}", lang)
    st.markdown(
        f"<div style='display:inline-block;padding:2px 10px;border-radius:10px;"
        f"background:{bg};color:{fg};font-size:12px;margin-bottom:6px'>{label}</div>",
        unsafe_allow_html=True,
    )


def chart_block(title: str, lead: str, fig, how_to_read: str, source: str,
                lang: str, badge_kind: str = BADGE_WHOLE) -> None:
    """One sentence first, chart second, technical detail last and collapsed."""
    st.subheader(title)
    st.caption(lead)
    badge(badge_kind, lang)
    if fig is None:
        st.info(t("ui.too_few", lang, n=MIN_ROWS))
        return
    st.plotly_chart(fig, use_container_width=True)
    with st.expander(t("ui.how_to_read", lang)):
        st.markdown(how_to_read)
        st.caption(f"{t('ui.source', lang)}: {source}")


def no_sample_notice(lang: str) -> None:
    st.info(t("ui.no_sample", lang))


# ---------------------------------------------------------------- dashboard layout
KPI_CSS = """
<style>
div[data-testid="stMetric"] {background: #ffffff; border: 1px solid #e6e4dc;
  border-radius: 10px; padding: 12px 14px 10px 14px;}
div[data-testid="stMetricLabel"] p {font-size: 0.78rem; color: #6b6a65;
  text-transform: uppercase; letter-spacing: .03em;}
div[data-testid="stMetricValue"] {font-size: 1.55rem; font-weight: 600;}
div[data-testid="stVerticalBlockBorderWrapper"] {background: #ffffff;}
.block-container {padding-top: 2.2rem; padding-bottom: 1rem;}
h1 {font-size: 1.75rem !important; margin-bottom: .2rem;}
</style>
"""


def kpi_cards(items: list[tuple[str, str]], helps: list[str] | None = None) -> None:
    """A row of Power-BI style KPI tiles."""
    cols = st.columns(len(items))
    for i, (label, value) in enumerate(items):
        with cols[i]:
            st.metric(label, value, help=(helps[i] if helps else None))


def grid(n: int = 2):
    """n equal columns for a dashboard-style chart grid."""
    return st.columns(n, gap="medium")


def chart_card(col, title: str, lead: str, fig, how_to_read: str, source: str,
               lang: str, badge_kind: str = BADGE_WHOLE, height: int | None = None) -> None:
    """One chart inside a bordered card, sized for a grid cell."""
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            if lead:
                st.caption(lead)
            badge(badge_kind, lang)
            if fig is None:
                st.info(t("ui.too_few", lang, n=MIN_ROWS))
                return
            if height:
                fig.update_layout(height=height)
            st.plotly_chart(fig, use_container_width=True)
            with st.expander(t("ui.how_to_read", lang)):
                st.markdown(how_to_read)
                st.caption(f"{t('ui.source', lang)}: {source}")


def section_title(title: str, lead: str = "") -> None:
    st.markdown(f"#### {title}")
    if lead:
        st.caption(lead)


# ---------------------------------------------------------------- KPI with sparkline
def _spark(values, color: str, fill: str):
    """Tiny area chart for a KPI tile - no axes, no hover chrome."""
    import plotly.graph_objects as go
    f = go.Figure(go.Scatter(y=list(values), mode="lines", line=dict(color=color, width=1.8),
                             fill="tozeroy", fillcolor=fill, hoverinfo="skip"))
    f.update_layout(height=44, margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    xaxis=dict(visible=False, fixedrange=True),
                    yaxis=dict(visible=False, fixedrange=True))
    return f


def kpi_spark_row(items: list[dict]) -> None:
    """A row of KPI tiles, each optionally carrying a small distribution sparkline.

    item = {label, value, spark (iterable|None), color, fill, help}
    """
    cols = st.columns(len(items))
    for col, it in zip(cols, items):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='font-size:.72rem;color:#6a7a92;text-transform:uppercase;"
                    f"letter-spacing:.055em;font-weight:600'>{it['label']}</div>"
                    f"<div style='font-size:1.6rem;font-weight:700;color:#13233d;"
                    f"line-height:1.2;white-space:nowrap;overflow:hidden;"
                    f"text-overflow:ellipsis'>{it['value']}</div>",
                    unsafe_allow_html=True)
                sp = it.get("spark")
                if sp is not None and len(sp):
                    st.plotly_chart(
                        _spark(sp, it.get("color", "#1668d6"),
                               it.get("fill", "rgba(22,104,214,.16)")),
                        use_container_width=True,
                        config={"displayModeBar": False, "staticPlot": True},
                        key=it.get("key"))


def hist_spark(series, bins: int = 28, weights=None):
    """Binned density of a column, for use as a KPI sparkline."""
    import numpy as np
    s = np.asarray(series, dtype=float)
    ok = ~np.isnan(s)
    if ok.sum() < 10:
        return None
    w = None if weights is None else np.asarray(weights, dtype=float)[ok]
    h, _ = np.histogram(s[ok], bins=bins, weights=w)
    return h
