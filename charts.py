"""
charts.py — plotly layer
Svaki grafikon je zasebna funkcija koja prima DataFrame i vraća plotly Figure.
Nema pandas logike ovde — samo vizualizacija.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Paleta boja ────────────────────────────────────────────────────────────
BG       = "#0d0f14"
SURFACE  = "#13161e"
SURFACE2 = "#1a1e28"
BORDER   = "#252936"
ACCENT   = "#e8ff47"
ACCENT2  = "#ff6b47"
ACCENT3  = "#47c4ff"
TEXT     = "#f0f2f8"
MUTED    = "#6b7280"
DANGER   = "#ff4757"
SUCCESS  = "#2ed573"
PURPLE   = "#a78bfa"

REASON_COLORS = {
    "Features":   ACCENT,
    "Budget":     ACCENT3,
    "Support":    ACCENT2,
    "Unknown":    PURPLE,
    "Competitor": DANGER,
    "Pricing":    SUCCESS,
}

LAYOUT_BASE = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="monospace", color=TEXT, size=11),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(showgrid=False, zeroline=False, color=MUTED,
               linecolor=BORDER, tickcolor=BORDER),
    yaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False,
               color=MUTED, linecolor=BORDER, tickcolor=BORDER),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**LAYOUT_BASE, title=dict(
        text=title, font=dict(size=11, color=MUTED),
        x=0, xanchor="left", pad=dict(l=4)
    ))
    return fig


# ── 1. Monthly churn bar chart ─────────────────────────────────────────────
def monthly_bar(df_monthly: pd.DataFrame) -> go.Figure:
    colors = [
        DANGER if row["churns"] >= 100
        else ACCENT2 if row["churns"] >= 50
        else ACCENT
        for _, row in df_monthly.iterrows()
    ]
    fig = go.Figure(go.Bar(
        x=df_monthly["year_month_dt"],
        y=df_monthly["churns"],
        marker_color=colors,
        marker_opacity=0.85,
        hovertemplate="<b>%{x|%b %Y}</b><br>Churns: %{y}<extra></extra>",
    ))
    _apply_base(fig, "MONTHLY CHURN VOLUME")
    fig.update_layout(
        bargap=0.15,
        xaxis=dict(showgrid=False, zeroline=False, color=MUTED,
                   linecolor=BORDER, tickcolor=BORDER,
                   tickformat="%b '%y"),
    )
    return fig


# ── 2. Reason donut ────────────────────────────────────────────────────────
def reason_donut(df_reasons: pd.DataFrame) -> go.Figure:
    colors = [REASON_COLORS.get(r, MUTED) for r in df_reasons["reason"]]
    fig = go.Figure(go.Pie(
        labels=df_reasons["reason"],
        values=df_reasons["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=SURFACE, width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} churns (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text="<b>600</b>", x=0.5, y=0.5,
        font=dict(size=22, color=TEXT, family="monospace"),
        showarrow=False,
    )
    _apply_base(fig, "CHURN BY REASON")
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(color=TEXT, size=10),
                    bgcolor="rgba(0,0,0,0)", x=1, y=0.5),
        margin=dict(l=16, r=100, t=36, b=16),
    )
    return fig


# ── 3. Feedback horizontal bars ────────────────────────────────────────────
def feedback_bars(df_feedback: pd.DataFrame) -> go.Figure:
    palette = [DANGER, ACCENT2, ACCENT3, MUTED]
    colors = [palette[i] if i < len(palette) else MUTED
              for i in range(len(df_feedback))]

    fig = go.Figure(go.Bar(
        x=df_feedback["count"],
        y=df_feedback["feedback"],
        orientation="h",
        marker_color=colors,
        marker_opacity=0.85,
        text=df_feedback["count"],
        textposition="outside",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="<b>%{y}</b><br>%{x} responses<extra></extra>",
    ))
    _apply_base(fig, "FEEDBACK TEXT")
    fig.update_layout(
        yaxis=dict(autorange="reversed", showgrid=False,
                   zeroline=False, color=TEXT,
                   linecolor=BORDER, tickcolor=BORDER),
        xaxis=dict(showgrid=True, gridcolor=BORDER,
                   zeroline=False, color=MUTED),
        bargap=0.35,
    )
    return fig


# ── 4. Pre-churn signals — horizontal bar ─────────────────────────────────
def signal_bars(df_signals: pd.DataFrame) -> go.Figure:
    sig_colors = {
        "Preceded by Upgrade":   SUCCESS,
        "Preceded by Downgrade": ACCENT2,
        "Reactivations":         ACCENT3,
        "No Prior Signal":       MUTED,
    }
    colors = [sig_colors.get(s, MUTED) for s in df_signals["signal"]]

    fig = go.Figure(go.Bar(
        x=df_signals["count"],
        y=df_signals["signal"],
        orientation="h",
        marker_color=colors,
        marker_opacity=0.85,
        text=[f"{c}  ({p:.1f}%)" for c, p in
              zip(df_signals["count"], df_signals["pct"])],
        textposition="outside",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="<b>%{y}</b><br>%{x} events<extra></extra>",
    ))
    _apply_base(fig, "PRE-CHURN SIGNALS")
    fig.update_layout(
        yaxis=dict(autorange="reversed", showgrid=False,
                   zeroline=False, color=TEXT,
                   linecolor=BORDER, tickcolor=BORDER),
        xaxis=dict(showgrid=True, gridcolor=BORDER,
                   zeroline=False, color=MUTED),
        bargap=0.35,
    )
    return fig


# ── 5. Refund rate by reason ───────────────────────────────────────────────
def refund_rate_bars(df_refund: pd.DataFrame) -> go.Figure:
    colors = [REASON_COLORS.get(r, MUTED) for r in df_refund["reason_code"]]

    fig = go.Figure(go.Bar(
        x=df_refund["refund_rate_pct"],
        y=df_refund["reason_code"],
        orientation="h",
        marker_color=colors,
        marker_opacity=0.85,
        text=[f"{v:.0f}%" for v in df_refund["refund_rate_pct"]],
        textposition="outside",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="<b>%{y}</b><br>Refund rate: %{x:.1f}%<extra></extra>",
    ))
    _apply_base(fig, "REFUND RATE BY REASON")
    fig.update_layout(
        yaxis=dict(autorange="reversed", showgrid=False,
                   zeroline=False, color=TEXT,
                   linecolor=BORDER, tickcolor=BORDER),
        xaxis=dict(showgrid=True, gridcolor=BORDER,
                   zeroline=False, color=MUTED,
                   ticksuffix="%"),
        bargap=0.35,
    )
    return fig


# ── 6. Heatmap: reason × feedback ─────────────────────────────────────────
def reason_feedback_heatmap(pivot: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[c.replace("(", "").replace(")", "").strip().title()
           for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[[0, SURFACE2], [1, ACCENT]],
        showscale=False,
        text=pivot.values.astype(int),
        texttemplate="%{text}",
        textfont=dict(size=12, color=TEXT, family="monospace"),
        hovertemplate="<b>%{y} × %{x}</b><br>%{z} events<extra></extra>",
    ))
    _apply_base(fig, "REASON × FEEDBACK HEATMAP")
    fig.update_layout(
        xaxis=dict(showgrid=False, color=MUTED, side="top"),
        yaxis=dict(showgrid=False, color=TEXT, autorange="reversed"),
        margin=dict(l=90, r=16, t=60, b=16),
    )
    return fig


# ── 7. Quarterly trend — bar + line overlay ───────────────────────────────
def quarterly_trend(df_qtly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_qtly["quarter_str"],
        y=df_qtly["events"],
        marker_color=ACCENT,
        marker_opacity=0.7,
        name="Events",
        hovertemplate="<b>%{x}</b><br>%{y} events<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_qtly["quarter_str"],
        y=df_qtly["events"],
        mode="lines+markers",
        line=dict(color=DANGER, width=2),
        marker=dict(color=DANGER, size=6),
        name="Trend",
        hoverinfo="skip",
    ))

    _apply_base(fig, "QUARTERLY TREND")
    fig.update_layout(
        showlegend=False,
        bargap=0.3,
        xaxis=dict(showgrid=False, color=MUTED,
                   linecolor=BORDER, tickcolor=BORDER),
    )
    return fig
