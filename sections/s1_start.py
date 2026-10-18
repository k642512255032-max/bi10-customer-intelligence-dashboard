"""Section 1 - Start here. Opens with a sentence, never a chart."""
from __future__ import annotations

import streamlit as st

from data_loader import load_metrics
from formatting import num, section_title
from strings import GLOSSARY, t


def render(ctx) -> None:
    lang = ctx["lang"]
    m = load_metrics()
    section_title(t("s1.h", lang))

    a, b = st.columns([3, 2])
    with a:
        st.write(t("s1.p1", lang))
        st.write(t("s1.p2", lang))
        st.write(t("s1.p3", lang))
    with b:
        with st.container(border=True):
            st.markdown(t("s1.fhs.card", lang))
        with st.container(border=True):
            st.markdown(t("s1.es.card", lang))

    c1, c2 = st.columns([2, 3])
    with c1:
        with st.container(border=True):
            st.markdown(f"**{t('s1.coverage.h', lang)}**")
            cov = m.get("coverage", {})
            rows = [{"table": k, "from": str(v[0])[:10], "to": str(v[1])[:10]}
                    for k, v in cov.items() if isinstance(v, (list, tuple)) and len(v) == 2]
            if rows:
                st.dataframe(rows, hide_index=True, use_container_width=True)
    with c2:
        st.info(t("s1.coverage.note", lang))
        with st.expander(t("s1.gloss.h", lang)):
            for term, desc in GLOSSARY.get(lang, GLOSSARY["en"]):
                st.markdown(f"**{term}** - {desc}")
