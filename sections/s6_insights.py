"""Section 6 - the four signature insights. Dashboard grid layout."""
from __future__ import annotations

import streamlit as st

import charts as ch
from data_loader import load_metrics, split_table
from focus import BADGE_WHOLE
from formatting import chart_card, grid, kpi_cards, num, pct, section_title
from strings import t

H = 300


def render(ctx) -> None:
    lang = ctx["lang"]
    m = load_metrics()
    section_title(t("s6.h", lang), t("s6.lead", lang))

    g = m.get("I4_ghost", {})
    i1 = split_table(m, "I1_by_initiator")
    kpi_cards([
        ("Pull leads -> booked in 30d", pct(i1.loc["PULL", "book_30d"]) if "PULL" in i1.index else "-"),
        ("Push leads -> booked in 30d", pct(i1.loc["PUSH", "book_30d"]) if "PUSH" in i1.index else "-"),
        ("Calls to never-answering customers", pct(g.get("share_attempts_to_never_connected_customers", 0))),
        ("Connect rate, attempt 1", pct(g.get("connect_rate_attempt1", 0))),
    ])
    st.write("")

    c1, c2 = grid(2)
    chart_card(c1, t("s6.i1.h", lang), t("s6.i1.lead", lang),
               ch.insight_pull_push(i1),
               "PULL = the customer came to us. PUSH = we generated the lead. A taller "
               "green bar than grey means that channel punches above its weight.\n\n"
               "**So what:** spend less on pushed volume, more on making it easy to come "
               "to you.", "summary_metrics.json / I1_by_initiator", lang, BADGE_WHOLE, H)
    chart_card(c2, t("s6.i2.h", lang), t("s6.i2.lead", lang),
               ch.insight_credit_hunger(split_table(m, "I2_by_channels")),
               "Bars are applications from customers who shopped that many channels first. "
               "The red line is how often those loans went bad.\n\n**So what:** shopping "
               "many channels fast is a risk signal, not an engagement signal.",
               "summary_metrics.json / I2_by_channels", lang, BADGE_WHOLE, H)

    c3, c4 = grid(2)
    chart_card(c3, t("s6.i3.h", lang), t("s6.i3.lead", lang),
               ch.insight_maturity(split_table(m, "I3_maturity_window")),
               "Customers lined up by where they sit in the loan life-cycle. The green bar "
               "is the peak.\n\n**So what:** time the re-loan offer to the maturity window "
               "instead of blanketing the base.",
               "summary_metrics.json / I3_maturity_window", lang, BADGE_WHOLE, H)
    chart_card(c4, t("s6.i4.h", lang), t("s6.i4.lead", lang),
               ch.insight_ghost_calling(split_table(m, "I4_by_attempt")),
               "Grey bars are calls made at each attempt number; the orange line is how "
               "often someone answered.\n\n**So what:** after a few unanswered attempts "
               "the next call is close to worthless - switch channel.",
               "summary_metrics.json / I4_by_attempt", lang, BADGE_WHOLE, H)
