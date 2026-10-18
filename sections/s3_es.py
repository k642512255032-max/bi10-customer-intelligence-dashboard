"""Section 3 - Engagement (ES). Dashboard grid layout."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts as ch
from config import C, ES_LEVELS, LEVEL_COLOR
from data_loader import load_metrics, split_table
from focus import BADGE_FILTERED, BADGE_WHOLE
from formatting import chart_card, grid, kpi_cards, pct, section_title
from strings import t

H = 300


def render(ctx) -> None:
    lang, df, d = ctx["lang"], ctx["df"], ctx["df_focus"]
    m = load_metrics()
    sliced = len(d) < len(df) if not df.empty else False
    bk = BADGE_FILTERED if sliced else BADGE_WHOLE
    section_title(t("s3.h", lang), t("s3.lead", lang))

    mix = pd.Series(m["es_level_mix"])
    val = split_table(m, "es_validation")
    kpi_cards([
        ("Champion", pct(mix.get("Champion", 0))),
        ("Active", pct(mix.get("Active", 0))),
        ("Warm", pct(mix.get("Warm", 0))),
        ("Cooling", pct(mix.get("Cooling", 0))),
        ("Champions still high after 1 quarter", pct(m.get("es_champion_stay_high", 0))),
    ])
    st.write("")

    c1, c2 = grid(2)
    chart_card(c1, t("s3.dist.h", lang), t("s3.dist.lead", lang),
               ch.weighted_hist(d, "ES", m["es_cuts"], df if sliced else None,
                                C["blue"], "ES") if not df.empty else None,
               t("s3.dist.how", lang), "dashboard_sample.csv", lang, bk, H)
    chart_card(c2, t("s3.level.h", lang), "",
               ch.mix_bar(mix, LEVEL_COLOR, order=ES_LEVELS),
               " | ".join(f"{k} {v:.1%}" for k, v in
                         mix.reindex(ES_LEVELS).dropna().items()),
               "summary_metrics.json / es_level_mix", lang, BADGE_WHOLE, H)

    c3, c4 = grid(2)
    chart_card(c3, t("s3.dims.h", lang), t("s3.dims.lead", lang),
               ch.dimension_card(split_table(m, "es_dimension_card")),
               "Blue bars are the weight each part carries. The orange line is the share "
               "of customers who actually have a real value for it - a part with a big "
               "weight but low coverage does less work than it looks like.\n\n"
               + t("s3.dims.caveat", lang),
               "summary_metrics.json / es_dimension_card", lang, BADGE_WHOLE, 320)
    chart_card(c4, t("s3.decile.h", lang), t("s3.decile.lead", lang),
               ch.decile_lines(split_table(m, "es_decile_outcomes")),
               "Each line is one outcome, scaled so its best decile is 100%. All three "
               "climb from left to right.",
               "summary_metrics.json / es_decile_outcomes", lang, BADGE_WHOLE, 320)

    c5, c6 = grid(2)
    chart_card(c5, t("s3.monthly.h", lang), t("s3.monthly.lead", lang),
               ch.monthly_lines(split_table(m, "es_monthly_forward"), LEVEL_COLOR,
                                "positives per 100 calls"),
               "Fifteen months of calls after scoring. If the groups were noise the lines "
               "would tangle; they do not.",
               "summary_metrics.json / es_monthly_forward", lang, BADGE_WHOLE, H)
    chart_card(c6, t("s3.walk.h", lang), t("s3.walk.lead", lang),
               ch.walkforward_bar(split_table(m, "es_walkforward")),
               "The score was rebuilt from scratch at three dates. Champions beat Cooling "
               "every time.", "summary_metrics.json / es_walkforward", lang, BADGE_WHOLE, H)

    cdc = m.get("call_date_check", {})
    if cdc and not cdc.get("call_dates_reliable", True):
        st.warning(t("s3.limit.body", lang,
                     real=cdc.get("share_with_application_within_14d_real", 0),
                     shuf=cdc.get("same_share_with_shuffled_call_dates", 0)),
                   icon=":material/warning:")

    w1, w2 = grid(2)
    with w1:
        with st.container(border=True):
            st.markdown(f"**{t('s3.weights.h', lang)}**")
            st.caption(t("s3.weights.body", lang))
            if "es_weights" in m:
                st.dataframe(split_table(m, "es_weights").round(4),
                             use_container_width=True)
    with w2:
        with st.container(border=True):
            st.markdown(f"**{t('s3.limit.h', lang)}**")
            st.caption(t("s3.selection.body", lang))
            st.dataframe(split_table(m, "es_backtest_by_level").round(4),
                         use_container_width=True)

    with st.expander(t("s3.selection.h", lang)):
        st.write(t("s3.selection.body", lang))
        st.dataframe(split_table(m, "es_backtest_by_level").round(4),
                     use_container_width=True)
        st.dataframe(val.round(4), use_container_width=True)
