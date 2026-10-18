"""Section 2 - Financial health (FHS). Dashboard grid layout."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import C, FHS_TIERS, TIER_COLOR
from data_loader import load_csv, load_metrics, split_table, weighted_share
from focus import BADGE_FILTERED, BADGE_WHOLE
from formatting import chart_card, grid, kpi_cards, num, pct, section_title
from strings import t

H = 300


def render(ctx) -> None:
    lang, focus, df, d = ctx["lang"], ctx["focus"], ctx["df"], ctx["df_focus"]
    m = load_metrics()
    sliced = len(d) < len(df) if not df.empty else False
    bk = BADGE_FILTERED if sliced else BADGE_WHOLE
    section_title(t("s2.h", lang), t("s2.lead", lang))

    mix = pd.Series(m["fhs_tier_mix"])
    kpi_cards([
        ("Resilient", pct(mix.get("Resilient", 0))),
        ("Stable", pct(mix.get("Stable", 0))),
        ("Vulnerable", pct(mix.get("Vulnerable", 0))),
        ("Thin-file", pct(mix.get("Thin-file", 0))),
        ("Distressed", pct(mix.get("Distressed", 0))),
        ("Scored customers", num(m["fhs_stats_filed"]["count"])),
    ])
    st.write("")

    c1, c2 = grid(2)
    chart_card(c1, t("s2.dist.h", lang), t("s2.dist.lead", lang),
               ch.weighted_hist(d, "FHS", m["fhs_tier_cuts"], df if sliced else None,
                                C["aqua"], "FHS") if not df.empty else None,
               t("s2.dist.how", lang), "dashboard_sample.csv", lang, bk, H)
    chart_card(c2, t("s2.tier.h", lang), t("s2.tier.lead", lang),
               ch.mix_bar(mix, TIER_COLOR, order=FHS_TIERS),
               " | ".join(f"{k} {v:.1%}" for k, v in
                         mix.reindex(FHS_TIERS[::-1]).dropna().items()),
               "summary_metrics.json / fhs_tier_mix", lang, BADGE_WHOLE, H)

    c3, c4 = grid(2)
    chart_card(c3, t("s2.factors.h", lang), t("s2.factors.lead", lang),
               ch.hbar(pd.Series(m["factor_weights_effective"]), C["blue"],
                       x_title="effective weight"),
               "Longer bar = that factor shifts the score more.",
               "summary_metrics.json / factor_weights_effective", lang, BADGE_WHOLE, 320)
    chart_card(c4, t("s2.valid.h", lang), t("s2.valid.lead", lang),
               ch.validation_bar(split_table(m, "fhs_validation")),
               "Each bar is one test. 50 out of 100 is a coin flip; above that the score "
               "adds real information.", "summary_metrics.json / fhs_validation", lang,
               BADGE_WHOLE, 320)

    c5, _ = grid([3, 1]) if False else (st.container(), None)
    with c5:
        with st.container(border=True):
            st.markdown(f"**{t('s2.scorecard.h', lang)}**")
            st.caption(t("s2.scorecard.lead", lang))
            st.plotly_chart(ch.scorecard_chart(load_csv("fhs_scorecard.csv")),
                            use_container_width=True)
            with st.expander(t("ui.how_to_read", lang)):
                st.markdown("Bars to the right add points (safer), bars to the left "
                            "subtract. Every customer's score is the sum of their bands.")
                st.caption(t("s2.note.filed", lang, n=int(m["fhs_stats_filed"]["count"])))
