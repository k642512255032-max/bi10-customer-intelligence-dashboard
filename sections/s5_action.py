"""Section 5 - What to do. Dashboard grid + customer explorer."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import SUB_SEGMENTS
from data_loader import load_csv, load_metrics, split_table
from focus import BADGE_HIGHLIGHT, BADGE_WHOLE, is_active
from formatting import chart_card, grid, kpi_cards, num, pct, section_title, vnd
from strings import t

H = 320


def render(ctx) -> None:
    lang, focus, df, d = ctx["lang"], ctx["focus"], ctx["df"], ctx["df_focus"]
    m = load_metrics()
    bk = BADGE_HIGHLIGHT if is_active(focus) else BADGE_WHOLE
    section_title(t("s5.h", lang), t("s5.lead", lang))

    lv, cg = m.get("value_levers", {}), m.get("call_gains_simulation", {})
    kpi_cards([
        ("Calls freed (cut lowest-ES 30%)", num(lv.get("L1_calls_saved_cut30pct_lowES", 0))),
        ("Positives still kept", pct(cg.get("positives_kept_if_cut_30pct_lowest_ES", 0))),
        ("Healthy, maturing in 90d", num(lv.get("L2_healthy_customers_maturing_90d", 0))),
        ("PROTECT risk vs GROW", f"{lv.get('L3_protect_vs_grow_risk_ratio', 0):.2f}x"),
    ])
    st.caption(t("s5.trigger.note", lang))
    st.write("")

    mix = pd.Series(m["nba_mix"])
    mix.index = [str(i).replace("\u00b7", "-")[:40] for i in mix.index]
    c1, c2 = grid(2)
    chart_card(c1, t("s5.action.h", lang), "", ch.mix_bar(mix, {}, order=list(mix.index)),
               "One recommended action per customer. Triggers override the segment action.",
               "summary_metrics.json / nba_mix", lang, BADGE_WHOLE, H)
    chart_card(c2, t("s5.action.h", lang) + " - by segment", "",
               ch.stacked_action_bar(split_table(m, "nba_by_segment"), focus),
               "Each column is a segment split by the action its customers receive. "
               "A segment is not a single action because triggers cut across it.",
               "summary_metrics.json / nba_by_segment", lang, bk, H)

    c3, c4 = grid(2)
    chart_card(c3, t("s5.calls.h", lang), t("s5.calls.lead", lang),
               ch.calls_vs_payoff(load_csv("call_allocation_by_segment.csv")
                                  .set_index("SEGMENT"), focus),
               "Grey bars are the share of all telesales calls a segment receives. The "
               "green line is positives returned per 10,000 of those calls.",
               "call_allocation_by_segment.csv", lang, bk, H)
    chart_card(c4, t("s5.opp.h", lang), "",
               ch.segment_profile_bar(load_csv("opportunity_map.csv").set_index("SEGMENT"),
                                      "customers", focus, ",.0f", "customers"),
               "Segment size, for scale against the levers above.",
               "opportunity_map.csv", lang, bk, H)

    st.markdown(f"#### {t('s5.explorer.h', lang)}")
    st.caption(t("s5.explorer.lead", lang))
    if df.empty:
        st.info(t("ui.no_sample", lang))
        return
    pool = d
    e1, e2, e3 = st.columns([2, 2, 1])
    with e1:
        subs = [s for s in SUB_SEGMENTS if s in pool["SUB_SEGMENT"].unique()]
        pick = st.selectbox(t("sl.subsegment", lang), ["(any)"] + subs, key="exp_sub")
    with e2:
        rng = st.slider("FHS", 0, 100, (0, 100), key="exp_fhs")
    with e3:
        st.write("")
        if st.button(t("s5.explorer.btn", lang), use_container_width=True):
            st.session_state["exp_seed"] = st.session_state.get("exp_seed", 0) + 1
    sel = pool if pick == "(any)" else pool[pool["SUB_SEGMENT"] == pick]
    sel = sel[(sel["FHS"] >= rng[0]) & (sel["FHS"] <= rng[1])]
    if sel.empty:
        st.warning(t("sl.none", lang))
        return
    row = sel.sample(1, random_state=st.session_state.get("exp_seed", 0)).iloc[0]
    with st.container(border=True):
        st.markdown(f"**{row['EXPLANATION']}**")
        kpi_cards([
            ("FHS", f"{row['FHS']:.0f} ({row['FHS_TIER']})"),
            ("ES", f"{row['ES']:.0f} ({row['ES_LEVEL']})"),
            ("Segment", str(row["SEGMENT"])),
            ("Priority", str(row["NBA_PRIORITY"])),
            ("Offer", vnd(row["NBA_OFFER_VND"])),
        ])
        g1, g2 = st.columns(2)
        with g1:
            st.markdown(f"- **Action**: {row['NBA_ACTION']}\n"
                        f"- **Product**: {row['NBA_PRODUCT']}\n"
                        f"- **Channel**: {row['NBA_CHANNEL']}")
        with g2:
            st.markdown(f"- **Timing**: {row['NBA_TIMING']}\n"
                        f"- **Trigger**: {row['NBA_TRIGGER']}\n"
                        f"- **Credit ceiling**: {vnd(row['CREDIT_CEILING_VND'])}")
        st.caption(f"ES parts - R {row['ES_RECENCY']:.0f} | F {row['ES_FREQUENCY']:.0f} | "
                   f"I {row['ES_INTERACTION']:.0f} | L {row['ES_LEAD_ACTIVITY']:.0f} | "
                   f"P {row['ES_PRODUCT_INTERACTION']:.0f}")
