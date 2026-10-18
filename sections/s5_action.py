"""Section 5 - What to do: the NBA engine, opportunity sizing, customer explorer."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import SEGMENTS, SUB_SEGMENTS
from data_loader import load_csv, load_metrics, split_table
from focus import BADGE_FILTERED, BADGE_HIGHLIGHT, BADGE_WHOLE, apply_focus, is_active
from formatting import chart_block, kpi_row, no_sample_notice, num, pct, vnd
from strings import t


def render(ctx) -> None:
    lang, focus, df = ctx["lang"], ctx["focus"], ctx["df"]
    m = load_metrics()
    st.header(t("s5.h", lang))
    st.write(t("s5.lead", lang))
    st.info(t("s5.trigger.note", lang))

    # N1 - action mix
    mix = pd.Series(m["nba_mix"])
    mix.index = [str(i).replace("\u00b7", "-")[:46] for i in mix.index]
    chart_block(t("s5.action.h", lang), "",
                ch.mix_bar(mix, {}, order=list(mix.index)),
                "One recommended action per customer. Triggers override the segment action.",
                "summary_metrics.json / nba_mix", lang, BADGE_WHOLE)

    # N2 - action by segment
    chart_block(t("s5.action.h", lang) + " - by segment", "",
                ch.stacked_action_bar(split_table(m, "nba_by_segment"), focus),
                "Each column is a segment, split by the action its customers receive. A "
                "segment is not one single action because the timing triggers cut across it.",
                "summary_metrics.json / nba_by_segment", lang,
                BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE)

    # N3 - calls vs payoff
    chart_block(t("s5.calls.h", lang), t("s5.calls.lead", lang),
                ch.calls_vs_payoff(load_csv("call_allocation_by_segment.csv")
                                   .set_index("SEGMENT"), focus),
                "GROW takes 61.6% of all calls. REACTIVATE takes 8.2% and returns the "
                "fewest positives per call.",
                "call_allocation_by_segment.csv", lang,
                BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE)

    # N4 - opportunity sizing
    st.subheader(t("s5.opp.h", lang))
    lv = m.get("value_levers", {})
    cg = m.get("call_gains_simulation", {})
    kpi_row([
        ("Calls freed by dropping the lowest-ES 30%", num(lv.get("L1_calls_saved_cut30pct_lowES", 0))),
        ("Positive outcomes still kept", pct(cg.get("positives_kept_if_cut_30pct_lowest_ES", 0))),
        ("Healthy customers maturing in 90d", num(lv.get("L2_healthy_customers_maturing_90d", 0))),
        ("PROTECT risk vs GROW", f"{lv.get('L3_protect_vs_grow_risk_ratio', 0):.2f}x"),
    ])
    chart_block("", "",
                ch.segment_profile_bar(load_csv("opportunity_map.csv").set_index("SEGMENT"),
                                       "customers", focus, ",.0f", "customers"),
                "Segment size, for scale against the levers above.",
                "opportunity_map.csv", lang,
                BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE)

    # N5 - the customer explorer
    st.divider()
    st.subheader(t("s5.explorer.h", lang))
    st.caption(t("s5.explorer.lead", lang))
    if df.empty:
        no_sample_notice(lang)
        return
    pool = ctx["df_focus"]
    c1, c2 = st.columns([1, 1])
    with c1:
        subs = [s for s in SUB_SEGMENTS if s in pool["SUB_SEGMENT"].unique()]
        pick = st.selectbox("Sub-segment", ["(any)"] + subs, key="explorer_sub")
    with c2:
        fhs_rng = st.slider("FHS", 0, 100, (0, 100), key="explorer_fhs")
    sel = pool if pick == "(any)" else pool[pool["SUB_SEGMENT"] == pick]
    sel = sel[(sel["FHS"] >= fhs_rng[0]) & (sel["FHS"] <= fhs_rng[1])]
    if sel.empty:
        st.warning("No customer matches that combination.")
        return
    if st.button(t("s5.explorer.btn", lang)):
        st.session_state["explorer_seed"] = st.session_state.get("explorer_seed", 0) + 1
    row = sel.sample(1, random_state=st.session_state.get("explorer_seed", 0)).iloc[0]
    with st.container(border=True):
        st.markdown(f"**{row['EXPLANATION']}**")
        kpi_row([
            ("FHS", f"{row['FHS']:.0f} ({row['FHS_TIER']})"),
            ("ES", f"{row['ES']:.0f} ({row['ES_LEVEL']})"),
            ("Segment", f"{row['SEGMENT']}"),
            ("Priority", f"{row['NBA_PRIORITY']}"),
        ])
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(
                f"- **Action**: {row['NBA_ACTION']}\n"
                f"- **Product**: {row['NBA_PRODUCT']}\n"
                f"- **Channel**: {row['NBA_CHANNEL']}\n"
                f"- **Timing**: {row['NBA_TIMING']}")
        with d2:
            st.markdown(
                f"- **Offer**: {vnd(row['NBA_OFFER_VND'])}\n"
                f"- **Credit ceiling**: {vnd(row['CREDIT_CEILING_VND'])}\n"
                f"- **Trigger**: {row['NBA_TRIGGER']}\n"
                f"- **Preferred product**: {row['PREF_FAMILY']}")
        st.caption("ES parts - "
                   f"Recency {row['ES_RECENCY']:.0f} | Frequency {row['ES_FREQUENCY']:.0f} | "
                   f"Interaction {row['ES_INTERACTION']:.0f} | Lead {row['ES_LEAD_ACTIVITY']:.0f} | "
                   f"Product {row['ES_PRODUCT_INTERACTION']:.0f}")
