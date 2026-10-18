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
