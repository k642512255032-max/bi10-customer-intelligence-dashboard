"""BI10 Customer Intelligence dashboard.

Every number shown here comes from the exported RESULTS_PACK of the BI10 Round-02
Colab notebook. Nothing is recomputed from raw data.

Run:  streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from config import DATA_DIR, ES_LEVELS, FHS_TIERS, SEGMENTS, SUB_SEGMENTS, sample_available
from data_loader import load_sample
from focus import ALL, SEGMENT_SUBS, apply_focus, as_segment, is_active
from formatting import num, pct
from sections import (s1_start, s2_fhs, s3_es, s4_matrix, s4b_segment, s5_action,
                      s6_insights)
from strings import LANGS, t

st.set_page_config(page_title="BI10 Customer Intelligence", page_icon="chart_with_upwards_trend",
                   layout="wide", initial_sidebar_state="expanded")

SECTIONS = [
    ("nav.1", s1_start.render), ("nav.2", s2_fhs.render), ("nav.3", s3_es.render),
    ("nav.4", s4_matrix.render), ("nav.4b", s4b_segment.render),
    ("nav.5", s5_action.render), ("nav.6", s6_insights.render),
]


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


def sidebar() -> dict:
    with st.sidebar:
        st.markdown(f"### {t('app.title', 'en')}")
        lang = st.radio(t("ui.language", "en"), list(LANGS),
                        format_func=lambda k: LANGS[k], horizontal=True, key="lang")
        st.caption(t("app.subtitle", lang))
        st.divider()

        idx = st.radio(t("ui.sections", lang), range(len(SECTIONS)),
                       format_func=lambda i: t(SECTIONS[i][0], lang), key="section")
        st.divider()

        st.markdown(f"**{t('ui.focus', lang)}**")
        drill = st.checkbox(t("ui.focus.drill", lang), key="drill")
        options = [ALL] + (SUB_SEGMENTS if drill else SEGMENTS)
        focus = st.radio("", options, label_visibility="collapsed",
                         format_func=lambda s: t("ui.focus.all", lang) if s == ALL else s,
                         key="focus_choice")
        st.divider()

        st.markdown(f"**{t('ui.filters', lang)}**")
        any_label = t("ui.filter.any", lang)
        tier = st.selectbox(t("ui.filter.tier", lang), [any_label] + FHS_TIERS, key="f_tier")
        level = st.selectbox(t("ui.filter.level", lang), [any_label] + ES_LEVELS, key="f_level")
        return dict(lang=lang, idx=idx, focus=focus, tier=tier, level=level, any_label=any_label)


def main() -> None:
    if not guard_data():
        return
    s = sidebar()
    lang = s["lang"]

    df = load_sample()
    df_focus = apply_focus(df, s["focus"]) if not df.empty else df
    if not df_focus.empty:
        if s["tier"] != s["any_label"]:
            df_focus = df_focus[df_focus["FHS_TIER"] == s["tier"]]
        if s["level"] != s["any_label"]:
            df_focus = df_focus[df_focus["ES_LEVEL"] == s["level"]]

    st.title(t("app.title", lang))

    # Persistent focus banner, built from the population table (not the sample).
    if is_active(s["focus"]):
        from data_loader import load_csv
        seg = as_segment(s["focus"])
        prof = load_csv("segment_profile.csv").set_index("SEGMENT")
        if seg in prof.index:
            r = prof.loc[seg]
            label = s["focus"] if s["focus"] in SEGMENT_SUBS else f"{s['focus']} ({seg})"
            st.success(
                f"**{label}** - {num(r['customers'])} {t('ui.customers', lang)}, "
                f"{pct(r['share'])} {t('ui.of_base', lang)} | "
                f"avg FHS {r['avg_FHS']:.1f} | avg ES {r['avg_ES']:.1f} | "
                f"{r['fwd_positive_per_100_calls']:.2f} positives / 100 calls"
            )
    if not sample_available():
        st.warning(t("ui.no_sample", lang))

    ctx = dict(lang=lang, focus=s["focus"], df=df, df_focus=df_focus)
    SECTIONS[s["idx"]][1](ctx)

    st.divider()
    st.caption(
        "Source: BI10 Round-02 notebook export (RESULTS_PACK_v3, 2026-10-17). "
        "Population figures come from the exported aggregate tables; distribution charts "
        "use a 40,000-row stratified sample reweighted to the full base of 1,000,528."
    )


if __name__ == "__main__":
    main()
