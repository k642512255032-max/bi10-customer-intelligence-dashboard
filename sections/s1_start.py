"""Section 1 - Start here. Opens with a sentence, never a chart."""
from __future__ import annotations

import streamlit as st

from data_loader import load_metrics
from formatting import kpi_row, num
from strings import GLOSSARY, t


def render(ctx) -> None:
    lang = ctx["lang"]
    m = load_metrics()
    st.header(t("s1.h", lang))
    st.write(t("s1.p1", lang))
    st.write(t("s1.p2", lang))
    st.write(t("s1.p3", lang))

    kpi_row([
        (t("s1.kpi.customers", lang), num(m.get("customers_total", 0))),
        (t("s1.kpi.tables", lang), str(len(m.get("raw_shapes", {})))),
        (t("s1.kpi.snapshot", lang), "2025-06-05"),
        (t("s1.kpi.runtime", lang), f"{m.get('runtime_minutes', 0):.0f} min"),
    ])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("s1.fhs.card", lang))
    with c2:
        st.markdown(t("s1.es.card", lang))

    st.divider()
    st.subheader(t("s1.coverage.h", lang))
    cov = m.get("coverage", {})
    if cov:
        rows = [{"table": table, "from": str(span[0])[:10], "to": str(span[1])[:10]}
                for table, span in cov.items() if isinstance(span, (list, tuple)) and len(span) == 2]
        if rows:
            st.dataframe(rows, hide_index=True, use_container_width=True)
    st.info(t("s1.coverage.note", lang))

    with st.expander(t("s1.gloss.h", lang)):
        for term, desc in GLOSSARY.get(lang, GLOSSARY["en"]):
            st.markdown(f"**{term}** - {desc}")
