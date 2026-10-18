"""Section 6 - the four signature insights."""
from __future__ import annotations

import streamlit as st

import charts as ch
from data_loader import load_metrics, split_table
from focus import BADGE_WHOLE
from formatting import chart_block, kpi_row, num, pct
from strings import t


def render(ctx) -> None:
    lang = ctx["lang"]
    m = load_metrics()
    st.header(t("s6.h", lang))
    st.write(t("s6.lead", lang))
    st.caption(t("ui.badge.whole", lang))

    # I1 - customers pull, we push
    i1 = split_table(m, "I1_by_initiator")
    chart_block(t("s6.i1.h", lang), t("s6.i1.lead", lang),
                ch.insight_pull_push(i1),
                "PULL = the customer came to us (app, landing page, in-store). PUSH = we "
                "generated the lead. If the green bar is taller than the grey one, that "
                "channel punches above its weight.\n\n**So what:** spend less on pushed "
                "volume and more on making it easy for customers to come to you.",
                "summary_metrics.json / I1_by_initiator", lang, BADGE_WHOLE)

    # I2 - credit hunger
    chart_block(t("s6.i2.h", lang), t("s6.i2.lead", lang),
                ch.insight_credit_hunger(split_table(m, "I2_by_channels")),
                "Bars are how many applications came from customers who had shopped that "
                "many channels first. The red line is how often those loans went bad.\n\n"
                "**So what:** shopping many channels in a short window is a risk signal, "
                "not an engagement signal.",
                "summary_metrics.json / I2_by_channels", lang, BADGE_WHOLE)

    # I3 - the maturity window
    chart_block(t("s6.i3.h", lang), t("s6.i3.lead", lang),
                ch.insight_maturity(split_table(m, "I3_maturity_window")),
                "Customers are lined up by where they sit in their loan life-cycle, from "
                "long finished on the left to far from maturity on the right. The green bar "
                "is the peak.\n\n**So what:** time the re-loan offer to the maturity window "
                "instead of blanketing the base.",
                "summary_metrics.json / I3_maturity_window", lang, BADGE_WHOLE)

    # I4 - ghost calling
    ghost = m.get("I4_ghost", {})
    chart_block(t("s6.i4.h", lang), t("s6.i4.lead", lang),
                ch.insight_ghost_calling(split_table(m, "I4_by_attempt")),
                "Grey bars are how many calls were made at each attempt number. The orange "
                "line is how often someone actually answered.\n\n**So what:** after a few "
                "unanswered attempts the next call is close to worthless - switch channel "
                "instead of dialling again.",
                "summary_metrics.json / I4_by_attempt", lang, BADGE_WHOLE)
    if ghost:
        kpi_row([(k.replace("_", " ").capitalize()[:34],
                  pct(v) if isinstance(v, float) and v <= 1 else num(v))
                 for k, v in list(ghost.items())[:4]])
