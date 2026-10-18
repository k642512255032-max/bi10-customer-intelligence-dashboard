"""Section 3 - Engagement (ES)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import C, ES_LEVELS, LEVEL_COLOR
from data_loader import load_metrics, split_table
from focus import BADGE_FILTERED, BADGE_WHOLE, is_active
from formatting import chart_block, no_sample_notice
from strings import t


def render(ctx) -> None:
    lang, focus, df = ctx["lang"], ctx["focus"], ctx["df"]
    m = load_metrics()
    st.header(t("s3.h", lang))
    st.write(t("s3.lead", lang))

    # E1 - distribution
    if df.empty:
        no_sample_notice(lang)
    else:
        fig = ch.weighted_hist(ctx["df_focus"], "ES", m["es_cuts"],
                               df if is_active(focus) else None, C["blue"], "ES")
        chart_block(t("s3.dist.h", lang), t("s3.dist.lead", lang), fig,
                    t("s3.dist.how", lang), "dashboard_sample.csv", lang,
                    BADGE_FILTERED if is_active(focus) else BADGE_WHOLE)

    # E2 - level mix
    chart_block(t("s3.level.h", lang), "",
                ch.mix_bar(pd.Series(m["es_level_mix"]), LEVEL_COLOR, order=ES_LEVELS),
                "Cooling 39.2% | Warm 30.2% | Active 20.3% | Champion 10.3%",
                "summary_metrics.json / es_level_mix", lang, BADGE_WHOLE)

    # E3 - the five dimensions
    card = split_table(m, "es_dimension_card")
    chart_block(t("s3.dims.h", lang), t("s3.dims.lead", lang),
                ch.dimension_card(card),
                "Blue bars are the weight each part carries in the final score. The orange "
                "line is the share of customers who actually have a real value for it - a "
                "part with a big weight but low coverage does less work than it looks like.",
                "summary_metrics.json / es_dimension_card", lang, BADGE_WHOLE)
    st.warning(t("s3.dims.caveat", lang))
    with st.expander(t("s3.dims.h", lang) + " - " + t("ui.how_to_read", lang)):
        st.dataframe(card.round(4), use_container_width=True)

    # E4 - deciles
    chart_block(t("s3.decile.h", lang), t("s3.decile.lead", lang),
                ch.decile_lines(split_table(m, "es_decile_outcomes")),
                "Each line is one outcome, scaled so its best decile is 100%. All three "
                "climb from left to right, which is what we want to see.",
                "summary_metrics.json / es_decile_outcomes", lang, BADGE_WHOLE)

    # E5 - monthly
    chart_block(t("s3.monthly.h", lang), t("s3.monthly.lead", lang),
                ch.monthly_lines(split_table(m, "es_monthly_forward"), LEVEL_COLOR,
                                 "positive outcomes per 100 sales calls"),
                "Fifteen months of calls after the scoring date. If the groups were noise "
                "the lines would tangle; they do not.",
                "summary_metrics.json / es_monthly_forward", lang, BADGE_WHOLE)

    # E6 - walk-forward
    wf = split_table(m, "es_walkforward")
    chart_block(t("s3.walk.h", lang), t("s3.walk.lead", lang),
                ch.walkforward_bar(wf),
                "The score was rebuilt from scratch at three different dates. Champions beat "
                "Cooling every time.",
                "summary_metrics.json / es_walkforward", lang, BADGE_WHOLE)
    with st.expander(t("s3.walk.h", lang) + " - " + t("ui.how_to_read", lang)):
        st.dataframe(wf.round(4), use_container_width=True)

    # G2 - the selection artefact, quarantined as a diagnostic, never as evidence
    st.divider()
    with st.expander(t("s3.selection.h", lang)):
        st.write(t("s3.selection.body", lang))
        bt = split_table(m, "es_backtest_by_level")
        st.dataframe(bt.round(4), use_container_width=True)
