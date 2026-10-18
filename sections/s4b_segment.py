"""Section 4b - Segment spotlight. Dashboard grid layout."""
from __future__ import annotations

import streamlit as st

import charts as ch
from config import C, SEGMENTS
from data_loader import load_csv, weighted_share
from focus import BADGE_FILTERED, BADGE_HIGHLIGHT, as_segment
from formatting import chart_card, grid, kpi_cards, num, pct, section_title, vnd
from strings import t

H = 300


def render(ctx) -> None:
    lang, focus, df, d = ctx["lang"], ctx["focus"], ctx["df"], ctx["df_focus"]
    seg = as_segment(focus)
    prof = load_csv("segment_profile.csv").set_index("SEGMENT")
    opp = load_csv("opportunity_map.csv").set_index("SEGMENT")
    ca = load_csv("call_allocation_by_segment.csv").set_index("SEGMENT")
    section_title(t("s4b.h", lang))

    if seg is None:
        st.info(t("s4b.pick", lang))
        cols = [c for c in ["customers", "share", "avg_FHS", "avg_ES",
                            "fwd_positive_per_100_calls", "bt_newloan_bad"]
                if c in prof.columns]
        st.dataframe(prof[cols].reindex([s for s in SEGMENTS if s in prof.index]).round(4),
                     use_container_width=True)
        c1, c2 = grid(2)
        chart_card(c1, t("s4.seg.h", lang), "",
                   ch.segment_profile_bar(prof, "share", None, ".1%", "share of base"),
                   "All four segments, unfocused.", "segment_profile.csv", lang,
                   BADGE_HIGHLIGHT, H)
        chart_card(c2, t("s5.calls.h", lang), t("s5.calls.lead", lang),
                   ch.calls_vs_payoff(ca, None),
                   "Share of calls versus positives returned.",
                   "call_allocation_by_segment.csv", lang, BADGE_HIGHLIGHT, H)
        return

    r, o, k = prof.loc[seg], opp.loc[seg], ca.loc[seg]
    kpi_cards([
        (t("ui.customers", lang).capitalize(), num(r["customers"])),
        (t("ui.of_base", lang).capitalize(), pct(r["share"])),
        ("Avg FHS", f"{r['avg_FHS']:.1f}"),
        ("Avg ES", f"{r['avg_ES']:.1f}"),
        ("Positives / 10k calls", f"{k['positives_per_10k_calls']:.1f}"),
        ("Median offer", vnd(o["median_offer"])),
    ])
    st.write("")

    c1, c2 = grid(2)
    chart_card(c1, t("s4b.who.h", lang), "",
               ch.sub_segment_bar(weighted_share(d, "SUB_SEGMENT"), focus)
               if not d.empty else None,
               "Sub-segment shares weighted back to the real population. The sample holds "
               "5,000 rows of each sub-segment whatever its true size, so unweighted these "
               "bars would all be equal and wrong.",
               "dashboard_sample.csv + sub_segment_profile.csv", lang, BADGE_FILTERED, H)
    chart_card(c2, t("s4b.vs.h", lang) + " - FHS", t("s4b.vs.lead", lang),
               ch.weighted_hist(d, "FHS", [40, 55, 70], df, C["aqua"], "FHS")
               if not df.empty else None,
               "The grey outline is all 1,000,528 customers; the solid shape is this "
               "segment. Both are percentages so the shapes compare fairly.",
               "dashboard_sample.csv", lang, BADGE_FILTERED, H)

    c3, c4 = grid(2)
    chart_card(c3, t("s4b.vs.h", lang) + " - ES", "",
               ch.weighted_hist(d, "ES", [25, 41, 57], df, C["blue"], "ES")
               if not df.empty else None,
               "Same comparison for engagement.", "dashboard_sample.csv", lang,
               BADGE_FILTERED, H)
    chart_card(c4, t("s4b.worth.h", lang), t("s5.calls.lead", lang),
               ch.calls_vs_payoff(ca, focus),
               "Grey bars are the share of all calls this segment receives; the green line "
               "is positives per 10,000 calls.",
               "call_allocation_by_segment.csv", lang, BADGE_HIGHLIGHT, H)
