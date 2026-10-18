"""Section 4b - Segment spotlight: everything the pack knows about one segment."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import C, SEGMENTS
from data_loader import load_csv, weighted_share
from focus import BADGE_FILTERED, BADGE_HIGHLIGHT, BADGE_WHOLE, as_segment, is_active
from formatting import chart_block, kpi_row, no_sample_notice, num, pct, vnd
from strings import t


def render(ctx) -> None:
    lang, focus, df = ctx["lang"], ctx["focus"], ctx["df"]
    seg = as_segment(focus)
    prof = load_csv("segment_profile.csv").set_index("SEGMENT")
    opp = load_csv("opportunity_map.csv").set_index("SEGMENT")
    st.header(t("s4b.h", lang))

    if seg is None:
        st.info(t("s4b.pick", lang))
        show = prof[["customers", "share", "avg_FHS", "avg_ES",
                     "fwd_positive_per_100_calls", "bt_newloan_bad"]]
        st.dataframe(show.reindex(SEGMENTS).round(4), use_container_width=True)
        return

    r = prof.loc[seg]
    st.markdown(f"### :{'green' if seg == 'GROW' else 'orange'}[{seg}]")
    kpi_row([
        (t("ui.customers", lang).capitalize(), num(r["customers"])),
        (t("ui.of_base", lang).capitalize(), pct(r["share"])),
        ("Average FHS", f"{r['avg_FHS']:.1f}"),
        ("Average ES", f"{r['avg_ES']:.1f}"),
    ])

    # S2 - who is inside this segment (weighted! see G1)
    if df.empty:
        no_sample_notice(lang)
    else:
        shares = weighted_share(ctx["df_focus"], "SUB_SEGMENT")
        chart_block(t("s4b.who.h", lang), "",
                    ch.sub_segment_bar(shares, focus),
                    "Sub-segment shares, weighted back to the real population. The sample "
                    "holds 5,000 rows of each sub-segment regardless of its true size, so "
                    "unweighted these bars would all be equal and wrong.",
                    "dashboard_sample.csv + sub_segment_profile.csv", lang, BADGE_FILTERED)

        # S3 - this segment versus everyone
        f1 = ch.weighted_hist(ctx["df_focus"], "FHS", [40, 55, 70], df, C["aqua"], "FHS")
        chart_block(t("s4b.vs.h", lang) + " - FHS", t("s4b.vs.lead", lang), f1,
                    "The grey outline is all 1,000,528 customers; the solid shape is this "
                    "segment. Both are shown as a percentage so the shapes compare fairly.",
                    "dashboard_sample.csv", lang, BADGE_FILTERED)
        f2 = ch.weighted_hist(ctx["df_focus"], "ES", [25, 41, 57], df, C["blue"], "ES")
        chart_block(t("s4b.vs.h", lang) + " - ES", "", f2,
                    "Same comparison for engagement.", "dashboard_sample.csv", lang,
                    BADGE_FILTERED)

    # S4 - what it is worth
    st.subheader(t("s4b.worth.h", lang))
    o = opp.loc[seg]
    ca = load_csv("call_allocation_by_segment.csv").set_index("SEGMENT").loc[seg]
    kpi_row([
        ("Growth actions", num(o["growth_actions"])),
        ("Loans maturing in 90d", num(o["maturing_90d"])),
        ("Median offer", vnd(o["median_offer"])),
        ("Positives per 10k calls", f"{ca['positives_per_10k_calls']:.1f}"),
    ])
    chart_block(t("s5.calls.h", lang), t("s5.calls.lead", lang),
                ch.calls_vs_payoff(load_csv("call_allocation_by_segment.csv")
                                   .set_index("SEGMENT"), focus),
                "Grey bars are the share of all telesales calls this segment receives. The "
                "green line is how many positive outcomes 10,000 of those calls return.",
                "call_allocation_by_segment.csv", lang, BADGE_HIGHLIGHT)
