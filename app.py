"""BI10 Customer Intelligence dashboard.

Layout: a horizontal category bar across the top picks which family of figures to
show; the left sidebar is a slicer panel that narrows the customer-level charts.

Every number comes from the exported RESULTS_PACK of the BI10 Round-02 Colab
notebook. Nothing is recomputed from raw data.

Run:  streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import streamlit as st

from config import (DATA_DIR, ES_LEVELS, FHS_TIERS, SEGMENTS, SUB_SEGMENTS,
                    sample_available)
from data_loader import load_csv, load_sample
from focus import ALL, SEGMENT_SUBS, apply_focus, as_segment, is_active
from formatting import KPI_CSS, chart_card, grid, kpi_cards, num, pct
from sections import (s1_start, s2_fhs, s3_es, s4_matrix, s4b_segment, s5_action,
                      s6_insights)
from strings import LANGS, t

st.set_page_config(page_title="BI10 Customer Intelligence",
                   page_icon="chart_with_upwards_trend",
                   layout="wide", initial_sidebar_state="expanded")

SECTIONS = [
    ("nav.1", "navs.1", s1_start.render), ("nav.2", "navs.2", s2_fhs.render),
    ("nav.3", "navs.3", s3_es.render), ("nav.4", "navs.4", s4_matrix.render),
    ("nav.4b", "navs.4b", s4b_segment.render), ("nav.5", "navs.5", s5_action.render),
    ("nav.6", "navs.6", s6_insights.render),
]

CSS = """
<style>
div[data-testid="stSidebar"] div[role="radiogroup"] label p {font-size: 0.86rem;}
div[data-testid="stSidebarUserContent"] {padding-top: 1rem;}
section.main div[role="radiogroup"] {gap: 0.15rem;}
</style>
"""


def guard_data() -> bool:
    missing = [f for f in ["summary_metrics.json", "segment_profile.csv",
                           "sub_segment_profile.csv", "matrix_fhs_es.csv"]
               if not (DATA_DIR / f).exists()]
    if missing:
        st.error(
            f"Data files not found in `{DATA_DIR}`.\n\nMissing: {', '.join(missing)}\n\n"
            "Extract the RESULTS_PACK into that folder, or set the `BI10_DATA_DIR` "
            "environment variable to point at it."
        )
        return False
    return True


def top_bar(lang: str) -> int:
    """Horizontal category bar. Renders only the chosen section, so it stays fast."""
    labels = [t(short, lang) for _, short, _ in SECTIONS]
    picker = getattr(st, "segmented_control", None)
    if picker is not None:
        choice = picker("", labels, default=labels[st.session_state.get("sec_i", 0)],
                        key="sec_bar", label_visibility="collapsed")
        idx = labels.index(choice) if choice in labels else 0
    else:
        idx = st.radio("", range(len(labels)), format_func=lambda i: labels[i],
                       horizontal=True, key="sec_bar_r", label_visibility="collapsed")
    st.session_state["sec_i"] = idx
    return idx


def slicer_panel(lang: str, df: pd.DataFrame) -> dict:
    """Left vertical slicer panel. Returns the chosen values."""
    ANY = t("ui.filter.any", lang)
    s = {}
    with st.sidebar:
        st.markdown(f"### {t('sl.h', lang)}")
        s["lang"] = st.radio(t("ui.language", "en"), list(LANGS),
                             format_func=lambda k: LANGS[k], horizontal=True, key="lang")
        st.divider()

        st.markdown(f"**{t('sl.who', lang)}**")
        s["focus"] = st.selectbox(
            t("ui.focus", lang), [ALL] + SEGMENTS,
            format_func=lambda x: t("ui.focus.all", lang) if x == ALL else x, key="f_seg")
        s["sub"] = st.selectbox(t("sl.subsegment", lang), [ANY] + SUB_SEGMENTS, key="f_sub")
        s["tier"] = st.selectbox(t("ui.filter.tier", lang), [ANY] + FHS_TIERS, key="f_tier")
        s["level"] = st.selectbox(t("ui.filter.level", lang), [ANY] + ES_LEVELS, key="f_lvl")

        st.markdown(f"**{t('sl.scores', lang)}**")
        s["fhs"] = st.slider(t("sl.fhs_range", lang), 0, 100, (0, 100), key="f_fhs")
        s["es"] = st.slider(t("sl.es_range", lang), 0, 100, (0, 100), key="f_es")

        if not df.empty:
            st.markdown(f"**{t('sl.action', lang)}**")
            s["prio"] = st.selectbox(t("sl.priority", lang),
                                     [ANY] + ["High", "Medium", "Low"], key="f_prio")
            s["trig"] = st.selectbox(
                t("sl.trigger", lang),
                [ANY] + sorted(df["NBA_TRIGGER"].dropna().unique().tolist()), key="f_trig")
            st.markdown(f"**{t('sl.where', lang)}**")
            s["fam"] = st.selectbox(
                t("sl.family", lang),
                [ANY] + sorted(df["PREF_FAMILY"].dropna().unique().tolist()), key="f_fam")
            prov = df["PROVINCE"].value_counts().head(25).index.tolist()
            s["prov"] = st.selectbox(t("ui.filter.province", lang), [ANY] + sorted(prov),
                                     key="f_prov")
            st.markdown(f"**{t('sl.flags', lang)}**")
            s["stress"] = st.checkbox(t("sl.stress", lang), key="f_stress")
            s["mature"] = st.checkbox(t("sl.maturing", lang), key="f_mature")
            s["gma"] = st.checkbox(t("sl.gma", lang), key="f_gma")
        s["ANY"] = ANY
    return s


def apply_slicers(df: pd.DataFrame, s: dict) -> pd.DataFrame:
    """Slicers narrow the customer-level sample only. Weights survive filtering."""
    if df.empty:
        return df
    d = apply_focus(df, s.get("focus"))
    ANY = s["ANY"]
    for key, col in [("sub", "SUB_SEGMENT"), ("tier", "FHS_TIER"), ("level", "ES_LEVEL"),
                     ("prio", "NBA_PRIORITY"), ("trig", "NBA_TRIGGER"),
                     ("fam", "PREF_FAMILY"), ("prov", "PROVINCE")]:
        v = s.get(key)
        if v and v != ANY:
            d = d[d[col] == v]
    lo, hi = s.get("fhs", (0, 100))
    d = d[(d["FHS"] >= lo) & (d["FHS"] <= hi)]
    lo, hi = s.get("es", (0, 100))
    d = d[(d["ES"] >= lo) & (d["ES"] <= hi)]
    if s.get("stress"):
        d = d[d["LIVE_STRESS_FLAG"] == 1]
    if s.get("mature"):
        d = d[d["MATURING_90D"] == 1]
    if s.get("gma"):
        d = d[d["GMA_SESSIONS"] > 0]
    return d


def slicers_active(s: dict) -> bool:
    ANY = s["ANY"]
    return (is_active(s.get("focus"))
            or any(s.get(k, ANY) not in (ANY, None)
                   for k in ["sub", "tier", "level", "prio", "trig", "fam", "prov"])
            or s.get("fhs", (0, 100)) != (0, 100)
            or s.get("es", (0, 100)) != (0, 100)
            or any(s.get(k) for k in ["stress", "mature", "gma"]))


def header_kpis(lang: str, d: pd.DataFrame, s: dict) -> None:
    """KPI strip that reacts to the slicers (weighted back to the population)."""
    from data_loader import load_metrics, weighted_mean
    m = load_metrics()
    if d.empty:
        kpi_cards([(t("s1.kpi.customers", lang), num(m["customers_total"])),
                   ("Avg FHS", "-"), ("Avg ES", "-"), ("Segments", str(len(SEGMENTS)))])
        return
    people = float(d["W"].sum())
    kpi_cards([
        (t("s1.kpi.customers", lang), num(people)),
        (f"{t('ui.of_base', lang)}", pct(people / m["customers_total"])),
        ("Avg FHS", f"{weighted_mean(d, 'FHS'):.1f}"),
        ("Avg ES", f"{weighted_mean(d, 'ES'):.1f}"),
        ("GROW share", pct((d.loc[d.SEGMENT == "GROW", "W"].sum() / people) if people else 0)),
    ])


def main() -> None:
    if not guard_data():
        return
    st.markdown(CSS + KPI_CSS, unsafe_allow_html=True)

    df = load_sample()
    s = slicer_panel(st.session_state.get("lang", "vi"), df)
    lang = s["lang"]
    d = apply_slicers(df, s)

    head = st.columns([3, 2])
    with head[0]:
        st.title(t("app.title", lang))
        st.caption(t("app.subtitle", lang))
    with head[1]:
        if not df.empty:
            st.caption(t("sl.matching", lang, n=len(d), tot=len(df)))
            st.progress(min(1.0, len(d) / max(len(df), 1)))

    idx = top_bar(lang)

    if slicers_active(s):
        st.info(t("sl.mixed", lang), icon=":material/filter_alt:")
    if not sample_available():
        st.warning(t("ui.no_sample", lang))

    header_kpis(lang, d, s)
    st.write("")

    if not df.empty and d.empty:
        st.warning(t("sl.none", lang))
        return

    ctx = dict(lang=lang, focus=s["focus"], df=df, df_focus=d, slicers=s)
    SECTIONS[idx][2](ctx)

    st.divider()
    from data_loader import load_metrics
    tot = load_metrics()["customers_total"]
    st.caption(
        f"Source: BI10 Round-02 notebook export (v5 pack, 4 segments + 3 triggers). "
        f"Population figures come from the exported aggregate tables; customer-level "
        f"charts use a {len(df):,}-row stratified sample reweighted to the full base of "
        f"{tot:,}."
    )


if __name__ == "__main__":
    main()
