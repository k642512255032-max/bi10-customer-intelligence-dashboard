"""Pure Plotly figure builders. No Streamlit imports - these are testable in isolation.

Every function returns a go.Figure, or None when there is not enough data to chart.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import (C, ES_LEVELS, FHS_TIERS, LEVEL_COLOR, PLOT_LAYOUT, SEGMENT_COLOR,
                    SEGMENTS, SEQ, SUB_SEGMENTS, TIER_COLOR)
from focus import MIN_ROWS, as_segment, highlight_colors, is_active


def _style(fig: go.Figure, height: int = 360, showlegend: bool = True) -> go.Figure:
    fig.update_layout(**PLOT_LAYOUT, height=height, showlegend=showlegend)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#d6d5d0")
    fig.update_yaxes(gridcolor="#ecebe7", zeroline=False, linecolor="rgba(0,0,0,0)")
    return fig


def _enough(df: pd.DataFrame) -> bool:
    return df is not None and not df.empty and len(df) >= MIN_ROWS


# ---------------------------------------------------------------- distributions
def weighted_hist(df: pd.DataFrame, col: str, cuts: list, base: pd.DataFrame | None,
                  color: str, title_x: str) -> go.Figure | None:
    """Population-weighted histogram, optionally with the whole base as a ghost outline."""
    if not _enough(df):
        return None
    fig = go.Figure()
    if base is not None and len(base) > len(df):
        fig.add_trace(go.Histogram(
            x=base[col], y=base["W"], histfunc="sum", histnorm="percent",
            nbinsx=50, name="All customers", marker=dict(color="rgba(0,0,0,0)"),
            marker_line=dict(color=C["grey"], width=1.2), hoverinfo="skip",
        ))
    fig.add_trace(go.Histogram(
        x=df[col], y=df["W"], histfunc="sum", histnorm="percent",
        nbinsx=50, name="Selected", marker=dict(color=color),
        hovertemplate=f"{title_x} %{{x}}<br>%{{y:.2f}}% of customers<extra></extra>",
    ))
    for c in cuts:
        fig.add_vline(x=c, line_width=1, line_dash="dash", line_color=C["ink2"])
    fig.update_layout(barmode="overlay", xaxis_title=title_x, yaxis_title="% of customers")
    return _style(fig, 340, showlegend=base is not None)


def mix_bar(mix: pd.Series, color_map: dict, focus: str | None = None,
            order: list | None = None) -> go.Figure:
    """Share-per-category bar built from a population table (the truth, not the sample)."""
    s = mix.reindex([c for c in (order or list(mix.index)) if c in mix.index])
    colors = (highlight_colors(list(s.index), focus, color_map)
              if is_active(focus) and set(s.index) <= set(SEGMENTS)
              else [color_map.get(c, C["grey"]) for c in s.index])
    fig = go.Figure(go.Bar(
        x=list(s.index), y=s.values, marker_color=colors,
        text=[f"{v:.1%}" for v in s.values], textposition="outside",
        hovertemplate="%{x}<br>%{y:.2%} of customers<extra></extra>",
    ))
    fig.update_layout(yaxis_tickformat=".0%", yaxis_title="% of customers")
    fig.update_yaxes(range=[0, max(s.values) * 1.22])
    return _style(fig, 330, showlegend=False)


def hbar(s: pd.Series, color: str, value_fmt: str = ".3g", x_title: str = "") -> go.Figure:
    s = s.sort_values()
    fig = go.Figure(go.Bar(
        x=s.values, y=list(s.index), orientation="h", marker_color=color,
        text=[f"{v:{value_fmt}}" for v in s.values], textposition="auto",
        hovertemplate="%{y}<br>%{x:.3g}<extra></extra>",
    ))
    fig.update_layout(xaxis_title=x_title)
    return _style(fig, max(300, 34 * len(s)), showlegend=False)


# ---------------------------------------------------------------- FHS specific
def scorecard_chart(sc: pd.DataFrame, top_factors: int = 8) -> go.Figure:
    """Points awarded per factor band - the 'nothing is hidden' chart."""
    order = (sc.groupby("factor")["fhs_points"].apply(lambda s: s.abs().max())
             .sort_values(ascending=False).head(top_factors).index.tolist())
    d = sc[sc["factor"].isin(order)].copy()
    d["factor"] = pd.Categorical(d["factor"], categories=order[::-1], ordered=True)
    d = d.sort_values("factor")
    fig = px.bar(
        d, x="fhs_points", y="factor", color="bin", orientation="h",
        color_discrete_sequence=SEQ[1:], barmode="group",
        labels={"fhs_points": "Points added to the score", "factor": "", "bin": "Band"},
    )
    fig.add_vline(x=0, line_width=1, line_color=C["ink2"])
    fig.update_traces(hovertemplate="%{y}<br>band %{customdata[0]}<br>%{x:+.1f} points<extra></extra>",
                      customdata=d[["bin"]].values)
    return _style(fig, 34 * len(order) + 160)


def validation_bar(tbl: pd.DataFrame, value_col: str = "auc") -> go.Figure:
    """Outcome tests as 'right N times out of 100' rather than raw AUC."""
    d = tbl.dropna(subset=[value_col]).copy()
    d["pctright"] = d[value_col] * 100
    d = d.sort_values("pctright")
    fig = go.Figure(go.Bar(
        x=d["pctright"], y=[i[:62] for i in d.index], orientation="h",
        marker_color=[C["aqua"] if v >= 50 else C["red"] for v in d["pctright"]],
        text=[f"{v:.0f}/100" for v in d["pctright"]], textposition="auto",
        hovertemplate="%{y}<br>right %{x:.0f} times out of 100<extra></extra>",
    ))
    fig.add_vline(x=50, line_width=1, line_dash="dash", line_color=C["ink2"])
    fig.update_layout(xaxis_title="times right out of 100 (50 = a coin flip)")
    return _style(fig, 34 * len(d) + 150, showlegend=False)


# ---------------------------------------------------------------- ES specific
def dimension_card(tbl: pd.DataFrame) -> go.Figure:
    """Weight of each ES dimension against how much real signal it carries."""
    d = tbl.copy()
    wcol, scol = d.columns[0], d.columns[1]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(d.index), y=d[wcol], name="Weight in ES",
                         marker_color=C["blue"], yaxis="y",
                         text=[f"{v:.0%}" for v in d[wcol]], textposition="outside"))
    fig.add_trace(go.Scatter(x=list(d.index), y=d[scol], name="Share with a real signal",
                             mode="markers+lines", marker=dict(size=11, color=C["orange"]),
                             yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Weight", tickformat=".0%", range=[0, max(d[wcol]) * 1.35]),
        yaxis2=dict(title="Coverage", tickformat=".0%", overlaying="y", side="right",
                    range=[0, 1.05], showgrid=False),
    )
    return _style(fig, 380)


def decile_lines(tbl: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(tbl.columns):
        v = tbl[col]
        fig.add_trace(go.Scatter(
            x=list(tbl.index), y=v / v.max(), mode="lines+markers", name=col[:46],
            line=dict(color=[C["aqua"], C["orange"], C["violet"]][i % 3], width=2.2),
            customdata=np.c_[v.values],
            hovertemplate="decile %{x}<br>%{customdata[0]:.4g}<extra></extra>",
        ))
    fig.update_layout(xaxis_title="ES decile (1 = lowest, 10 = highest)",
                      yaxis_title="relative to the best decile", yaxis_tickformat=".0%")
    return _style(fig, 360)


def monthly_lines(tbl: pd.DataFrame, color_map: dict, y_title: str) -> go.Figure:
    fig = go.Figure()
    for lvl in [l for l in ES_LEVELS if l in tbl.index]:
        fig.add_trace(go.Scatter(
            x=list(range(1, len(tbl.columns) + 1)), y=tbl.loc[lvl].values,
            mode="lines+markers", name=lvl,
            line=dict(color=color_map.get(lvl, C["grey"]), width=2.2),
            hovertemplate=f"{lvl}<br>month %{{x}}<br>%{{y:.4g}}<extra></extra>",
        ))
    fig.update_layout(xaxis_title="months after scoring", yaxis_title=y_title)
    return _style(fig, 360)


def walkforward_bar(tbl: pd.DataFrame) -> go.Figure:
    cols = [c for c in ["Cooling", "Champion"] if c in tbl.columns]
    fig = go.Figure()
    for c in cols:
        fig.add_trace(go.Bar(x=list(tbl.index), y=tbl[c], name=c,
                             marker_color=LEVEL_COLOR.get(c, C["grey"]),
                             text=[f"{v:.1%}" for v in tbl[c]], textposition="outside",
                             hovertemplate=f"{c}<br>%{{x}}<br>%{{y:.1%}}<extra></extra>"))
    fig.update_layout(barmode="group", yaxis_tickformat=".0%",
                      yaxis_title="still self-active afterwards", xaxis_title="scoring date")
    return _style(fig, 360)


# ---------------------------------------------------------------- matrix & segments
def matrix_heatmap(m: pd.DataFrame) -> go.Figure:
    """FHS tier x ES level counts. Rows/cols forced into the canonical order (G: the
    CSV arrives alphabetical, which would make the heatmap read backwards)."""
    d = m.set_index("FHS_TIER") if "FHS_TIER" in m.columns else m
    d = d.reindex(index=[t for t in FHS_TIERS if t in d.index],
                  columns=[c for c in ES_LEVELS if c in d.columns])
    fig = px.imshow(d.values, x=list(d.columns), y=list(d.index),
                    color_continuous_scale=SEQ, aspect="auto",
                    labels=dict(x="Engagement level", y="Financial health tier", color="Customers"))
    fig.update_traces(text=[[f"{v:,.0f}" for v in row] for row in d.values],
                      texttemplate="%{text}",
                      hovertemplate="%{y} x %{x}<br>%{z:,.0f} customers<extra></extra>")
    fig.update_layout(coloraxis_showscale=False)
    return _style(fig, 380, showlegend=False)


def segment_scatter(df: pd.DataFrame, focus: str | None, n: int = 15000) -> go.Figure | None:
    """Every customer on the FHS x ES plane. Subsampled and webgl for responsiveness."""
    if not _enough(df):
        return None
    d = df.sample(min(n, len(df)), random_state=42)
    fig = go.Figure()
    seg = as_segment(focus)
    for s in [x for x in SEGMENTS if x in d["SEGMENT"].unique()]:
        sub = d[d["SEGMENT"] == s]
        dimmed = seg is not None and s != seg
        fig.add_trace(go.Scattergl(
            x=sub["ES"], y=sub["FHS"], mode="markers", name=s,
            marker=dict(size=3.5, color=C["dim"] if dimmed else SEGMENT_COLOR[s],
                        opacity=0.25 if dimmed else 0.55),
            hovertemplate=f"{s}<br>ES %{{x:.0f}} / FHS %{{y:.0f}}<extra></extra>",
        ))
    fig.update_layout(xaxis_title="Engagement (ES)", yaxis_title="Financial health (FHS)")
    return _style(fig, 430)


def segment_profile_bar(prof: pd.DataFrame, col: str, focus: str | None,
                        fmt: str = ".3g", y_title: str = "") -> go.Figure:
    d = prof.reindex([s for s in SEGMENTS if s in prof.index])
    fig = go.Figure(go.Bar(
        x=list(d.index), y=d[col],
        marker_color=highlight_colors(list(d.index), focus, SEGMENT_COLOR),
        text=[f"{v:{fmt}}" for v in d[col]], textposition="outside",
        hovertemplate="%{x}<br>%{y:.4g}<extra></extra>",
    ))
    fig.update_layout(yaxis_title=y_title)
    fig.update_yaxes(range=[0, float(d[col].max()) * 1.2])
    return _style(fig, 330, showlegend=False)


def grouped_segment_bar(d: pd.DataFrame, cols: list, labels: list, focus: str | None,
                        y_title: str, tickfmt: str | None = None) -> go.Figure:
    d = d.reindex([s for s in SEGMENTS if s in d.index])
    seg = as_segment(focus)
    fig = go.Figure()
    for i, (c, lab) in enumerate(zip(cols, labels)):
        opac = [1.0 if (seg is None or s == seg) else 0.28 for s in d.index]
        fig.add_trace(go.Bar(
            x=list(d.index), y=d[c], name=lab,
            marker=dict(color=[C["blue"], C["orange"]][i % 2], opacity=opac),
            hovertemplate=f"{lab}<br>%{{x}}<br>%{{y:.4g}}<extra></extra>",
        ))
    fig.update_layout(barmode="group", yaxis_title=y_title)
    if tickfmt:
        fig.update_layout(yaxis_tickformat=tickfmt)
    return _style(fig, 360)


def stacked_action_bar(tbl: pd.DataFrame, focus: str | None) -> go.Figure:
    d = tbl.reindex([s for s in SEGMENTS if s in tbl.index])
    seg = as_segment(focus)
    fig = go.Figure()
    for i, col in enumerate(d.columns):
        opac = [1.0 if (seg is None or s == seg) else 0.3 for s in d.index]
        fig.add_trace(go.Bar(
            x=list(d.index), y=d[col], name=col[:44],
            marker=dict(color=SEQ[i % len(SEQ)], opacity=opac),
            hovertemplate=f"{col[:44]}<br>%{{x}}<br>%{{y:.1%}}<extra></extra>",
        ))
    fig.update_layout(barmode="stack", yaxis_tickformat=".0%",
                      yaxis_title="share of the segment")
    return _style(fig, 400)


def sub_segment_bar(shares: pd.Series, focus: str | None) -> go.Figure:
    s = shares.reindex([x for x in SUB_SEGMENTS if x in shares.index])
    fig = go.Figure(go.Bar(
        x=s.values, y=list(s.index), orientation="h", marker_color=C["blue"],
        text=[f"{v:.1%}" for v in s.values], textposition="auto",
        hovertemplate="%{y}<br>%{x:.1%} of the segment<extra></extra>",
    ))
    fig.update_layout(xaxis_tickformat=".0%", xaxis_title="share of the focused segment")
    return _style(fig, max(260, 42 * len(s)), showlegend=False)


# ---------------------------------------------------------------- insights
def insight_pull_push(tbl: pd.DataFrame) -> go.Figure:
    """I1: lead volume share versus booking share, per initiator."""
    d = tbl.reindex([i for i in ["PULL", "WARM", "PUSH"] if i in tbl.index])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(d.index), y=d["lead_share"], name="Share of leads",
                         marker_color=C["grey"],
                         text=[f"{v:.1%}" for v in d["lead_share"]], textposition="outside"))
    fig.add_trace(go.Bar(x=list(d.index), y=d["bookings_share"], name="Share of bookings",
                         marker_color=C["aqua"],
                         text=[f"{v:.1%}" for v in d["bookings_share"]], textposition="outside"))
    fig.update_layout(barmode="group", yaxis_tickformat=".0%", yaxis_title="share")
    return _style(fig, 360)


def insight_credit_hunger(tbl: pd.DataFrame) -> go.Figure:
    """I2: more channels shopped before applying -> worse loan performance."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(tbl.index), y=tbl["applications"], name="Applications",
                         marker_color=SEQ[2], yaxis="y"))
    fig.add_trace(go.Scatter(x=list(tbl.index), y=tbl["bad_rate"], name="Bad rate",
                             mode="lines+markers", yaxis="y2",
                             line=dict(color=C["red"], width=2.5), marker=dict(size=9)))
    fig.update_layout(
        xaxis_title="channels shopped in the 90 days before applying",
        yaxis=dict(title="applications"),
        yaxis2=dict(title="bad rate", overlaying="y", side="right",
                    tickformat=".1%", showgrid=False),
    )
    fig.update_xaxes(type="category")
    return _style(fig, 380)


def insight_maturity(tbl: pd.DataFrame) -> go.Figure:
    """I3: preserve the JSON index order - it is a life-cycle, not a category list."""
    v = tbl["mean"]
    peak = v.idxmax()
    fig = go.Figure(go.Bar(
        x=list(tbl.index), y=v.values,
        marker_color=[C["aqua"] if i == peak else SEQ[2] for i in tbl.index],
        text=[f"{x:.0%}" for x in v.values], textposition="outside",
        customdata=np.c_[tbl["size"].values],
        hovertemplate="%{x}<br>%{y:.1%} take a new loan<br>%{customdata[0]:,.0f} customers<extra></extra>",
    ))
    fig.update_layout(yaxis_tickformat=".0%", yaxis_title="share taking a new loan",
                      xaxis_title="position in the loan life-cycle")
    fig.update_yaxes(range=[0, float(v.max()) * 1.2])
    return _style(fig, 400, showlegend=False)


def insight_ghost_calling(tbl: pd.DataFrame, max_attempt: int = 12) -> go.Figure:
    d = tbl[tbl.index <= max_attempt] if pd.api.types.is_numeric_dtype(tbl.index) else tbl.head(max_attempt)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(d.index), y=d["attempts"], name="Calls made",
                         marker_color=C["dim"], yaxis="y"))
    fig.add_trace(go.Scatter(x=list(d.index), y=d["connect_rate"], name="Someone answers",
                             mode="lines+markers", yaxis="y2",
                             line=dict(color=C["orange"], width=2.5), marker=dict(size=8)))
    fig.update_layout(
        xaxis_title="attempt number to the same customer",
        yaxis=dict(title="calls made"),
        yaxis2=dict(title="connect rate", overlaying="y", side="right",
                    tickformat=".0%", showgrid=False, rangemode="tozero"),
    )
    fig.update_xaxes(type="category")
    return _style(fig, 380)


def calls_vs_payoff(d: pd.DataFrame, focus: str | None) -> go.Figure:
    """N3: share of calls spent versus positives returned per 10k calls."""
    d = d.reindex([s for s in SEGMENTS if s in d.index])
    seg = as_segment(focus)
    opac = [1.0 if (seg is None or s == seg) else 0.3 for s in d.index]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(d.index), y=d["attempt_share"], name="Share of all calls",
                         marker=dict(color=C["grey"], opacity=opac),
                         text=[f"{v:.0%}" for v in d["attempt_share"]], textposition="outside",
                         yaxis="y"))
    fig.add_trace(go.Scatter(x=list(d.index), y=d["positives_per_10k_calls"],
                             name="Positives per 10,000 calls", mode="markers+lines",
                             marker=dict(size=13, color=C["aqua"]), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="share of all calls", tickformat=".0%", range=[0, 0.8]),
        yaxis2=dict(title="positives per 10k calls", overlaying="y", side="right",
                    showgrid=False, rangemode="tozero"),
    )
    return _style(fig, 380)
