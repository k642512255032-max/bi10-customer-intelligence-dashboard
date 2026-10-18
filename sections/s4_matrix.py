"""Section 4 - FHS x ES grouping. Dashboard grid layout."""
from __future__ import annotations

import streamlit as st

import charts as ch
from data_loader import load_csv
from focus import BADGE_HIGHLIGHT, BADGE_WHOLE, is_active
from formatting import chart_card, grid, kpi_cards, num, pct, section_title
from strings import t

H = 330


def render(ctx) -> None:
    lang, focus, df, d = ctx["lang"], ctx["focus"], ctx["df"], ctx["df_focus"]
    prof = load_csv("segment_profile.csv").set_index("SEGMENT")
    bk = BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE
    section_title(t("s4.h", lang), t("s4.lead", lang))

    kpi_cards([(s, f"{pct(prof.loc[s, 'share'])}  ({num(prof.loc[s, 'customers'])})")
               for s in prof.index.tolist()])
    st.write("")

    c1, c2 = grid(2)
    chart_card(c1, t("s4.matrix.h", lang), t("s4.matrix.lead", lang),
               ch.matrix_heatmap(load_csv("matrix_fhs_es.csv")),
               "Rows are financial health, safest at the top. Columns are engagement, most "
               "engaged on the right. Each cell is a customer count.",
               "matrix_fhs_es.csv", lang, BADGE_WHOLE, H)
    chart_card(c2, t("s4.scatter.h", lang), t("s4.scatter.lead", lang),
               ch.segment_scatter(d, focus) if not df.empty else None,
               "A sample of customers, one dot each. Colour is the assigned segment.",
               "dashboard_sample.csv", lang, bk, H)

    c3, c4 = grid(2)
    chart_card(c3, t("s4.seg.h", lang), "",
               ch.segment_profile_bar(prof, "share", focus, ".1%", "share of base"),
               t("s4.rule", lang), "segment_profile.csv", lang, bk, H)
    chart_card(c4, "FHS vs ES", "",
               ch.grouped_segment_bar(prof, ["avg_FHS", "avg_ES"],
                                      ["Average FHS", "Average ES"], focus, "score"),
               "GROW and REACTIVATE are both financially healthy; engagement separates "
               "them. PROTECT and BUILD are the stretched and the unknown.",
               "segment_profile.csv", lang, bk, H)

    with st.expander(t("s4.seg.h", lang) + " - " + t("ui.how_to_read", lang)):
        cols = [c for c in ["customers", "avg_FHS", "avg_ES", "share", "holds_product",
                            "fwd_positive_per_100_calls", "bt_newloan_bad"]
                if c in prof.columns]
        st.dataframe(prof[cols].round(4), use_container_width=True)
