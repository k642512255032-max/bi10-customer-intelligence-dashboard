"""Section 2 - Financial health (FHS)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import C, FHS_TIERS, TIER_COLOR
from data_loader import load_csv, load_metrics, split_table
from focus import BADGE_FILTERED, BADGE_WHOLE, is_active
from formatting import chart_block, no_sample_notice, num
from strings import t


def render(ctx) -> None:
    lang, focus, df = ctx["lang"], ctx["focus"], ctx["df"]
    m = load_metrics()
    st.header(t("s2.h", lang))
    st.write(t("s2.lead", lang))
    st.caption(t("s2.note.filed", lang, n=int(m["fhs_stats_filed"]["count"])))

    # F1 - distribution (sample driven, filtered by focus, ghost = whole base)
    if df.empty:
        no_sample_notice(lang)
    else:
        fig = ch.weighted_hist(ctx["df_focus"], "FHS", m["fhs_tier_cuts"],
                               df if is_active(focus) else None,
                               ch.C["aqua"], "FHS")
        chart_block(t("s2.dist.h", lang), t("s2.dist.lead", lang), fig,
                    t("s2.dist.how", lang), "dashboard_sample.csv", lang,
                    BADGE_FILTERED if is_active(focus) else BADGE_WHOLE)

    # F2 - tier mix (population truth)
    chart_block(t("s2.tier.h", lang), t("s2.tier.lead", lang),
                ch.mix_bar(pd.Series(m["fhs_tier_mix"]), TIER_COLOR, order=FHS_TIERS),
                "Resilient 32.1% | Vulnerable 22.9% | Stable 20.6% | Thin-file 18.2% | Distressed 6.2%",
                "summary_metrics.json / fhs_tier_mix", lang, BADGE_WHOLE)

    # F3 - what moves the score
    chart_block(t("s2.factors.h", lang), t("s2.factors.lead", lang),
                ch.hbar(pd.Series(m["factor_weights_effective"]), C["blue"],
                        x_title="effective weight in the scorecard"),
                "Longer bar = that factor shifts the score more.",
                "summary_metrics.json / factor_weights_effective", lang, BADGE_WHOLE)

    # F4 - the scorecard
    chart_block(t("s2.scorecard.h", lang), t("s2.scorecard.lead", lang),
                ch.scorecard_chart(load_csv("fhs_scorecard.csv")),
                "Bars to the right add points (safer), bars to the left subtract.",
                "fhs_scorecard.csv", lang, BADGE_WHOLE)

    # F5 - does it work
    chart_block(t("s2.valid.h", lang), t("s2.valid.lead", lang),
                ch.validation_bar(split_table(m, "fhs_validation")),
                "Each bar is one test. 50 out of 100 would be a coin flip; above that the "
                "score is adding real information.",
                "summary_metrics.json / fhs_validation", lang, BADGE_WHOLE)
    with st.expander("AUC / Gini / KS"):
        st.dataframe(split_table(m, "fhs_validation").round(4), use_container_width=True)
