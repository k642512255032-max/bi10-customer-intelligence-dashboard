"""Section 4 - FHS x ES, the grouping."""
from __future__ import annotations

import streamlit as st

import charts as ch
from config import SEGMENTS
from data_loader import load_csv, load_metrics, split_table
from focus import BADGE_HIGHLIGHT, BADGE_WHOLE, is_active
from formatting import chart_block, no_sample_notice, pct
from strings import t


def render(ctx) -> None:
    lang, focus, df = ctx["lang"], ctx["focus"], ctx["df"]
    m = load_metrics()
    st.header(t("s4.h", lang))
    st.write(t("s4.lead", lang))

    # M1 - the crosstab
    chart_block(t("s4.matrix.h", lang), t("s4.matrix.lead", lang),
                ch.matrix_heatmap(load_csv("matrix_fhs_es.csv")),
                "Rows are financial health, safest at the top. Columns are engagement, "
                "most engaged on the right. The number in each cell is how many customers "
                "sit there.",
                "matrix_fhs_es.csv", lang, BADGE_WHOLE)

    # M2 - the map
    if df.empty:
        no_sample_notice(lang)
    else:
        chart_block(t("s4.scatter.h", lang), t("s4.scatter.lead", lang),
                    ch.segment_scatter(df, focus),
                    "A sample of 15,000 customers, one dot each. Colour is the segment they "
                    "were assigned to.",
                    "dashboard_sample.csv (15,000 of 40,000 rows)", lang,
                    BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE)

    st.info(t("s4.rule", lang))

    # M3 / M4 - segment sizes and profiles
    prof = load_csv("segment_profile.csv").set_index("SEGMENT")
    chart_block(t("s4.seg.h", lang), "",
                ch.segment_profile_bar(prof, "share", focus, ".1%", "share of all customers"),
                "GROW 38.8% | PROTECT 29.1% | BUILD 18.2% | REACTIVATE 13.9%",
                "segment_profile.csv", lang,
                BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE)

    chart_block("FHS vs ES " + t("s4.seg.h", lang), "",
                ch.grouped_segment_bar(prof, ["avg_FHS", "avg_ES"],
                                       ["Average FHS", "Average ES"], focus, "score (0-100)"),
                "GROW and REACTIVATE are both financially healthy; what separates them is "
                "engagement. PROTECT and BUILD are the stretched and the unknown.",
                "segment_profile.csv", lang,
                BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE)

    with st.expander(t("s4.seg.h", lang) + " - " + t("ui.how_to_read", lang)):
        show = prof[["customers", "avg_FHS", "avg_ES", "share", "holds_product",
                     "fwd_positive_per_100_calls", "bt_newloan_bad"]].copy()
        st.dataframe(show.round(4), use_container_width=True)
