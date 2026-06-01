"""
app.py — streamlit layout layer
Ovde živu samo st.* pozivi i raspored komponenti.
Nema pandas transformacija ni plotly figure logike.
"""

import streamlit as st
from data import (
    load_data, get_kpis, get_monthly_volume, get_reason_breakdown,
    get_feedback_breakdown, get_signals, get_refund_by_reason,
    get_heatmap, get_quarterly_trend,
)
from charts import (
    monthly_bar, reason_donut, feedback_bars, signal_bars,
    refund_rate_bars, reason_feedback_heatmap, quarterly_trend,
)

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RavenStack — Churn Intelligence",
    page_icon="△",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark background for entire app */
  .stApp { background-color: #0d0f14; }

  /* Hide default Streamlit header/footer */
  #MainMenu, footer, header { visibility: hidden; }

  /* Metric card overrides */
  [data-testid="metric-container"] {
    background: #13161e;
    border: 1px solid #252936;
    border-top: 2px solid;
    padding: 16px 20px 12px;
  }

  [data-testid="stMetricLabel"] {
    font-family: monospace;
    font-size: 10px !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7280 !important;
  }

  [data-testid="stMetricValue"] {
    font-family: monospace;
    font-size: 28px !important;
    font-weight: 700;
    color: #f0f2f8 !important;
  }

  [data-testid="stMetricDelta"] {
    font-family: monospace;
    font-size: 11px !important;
    color: #6b7280 !important;
  }

  /* Section divider */
  hr { border-color: #252936; margin: 8px 0; }

  /* Chart containers */
  [data-testid="stPlotlyChart"] {
    border: 1px solid #252936;
  }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data
def load():
    return load_data("ravenstack_churn_events.csv")

df = load()
kpis = get_kpis(df)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:24px; 
            padding-bottom:16px; border-bottom:1px solid #252936;">
  <div style="width:32px; height:32px; background:#e8ff47;
              clip-path:polygon(50% 0%, 100% 100%, 0% 100%);"></div>
  <div>
    <div style="font-family:monospace; font-size:18px; font-weight:700;
                color:#f0f2f8; letter-spacing:-0.5px;">
      Raven<span style="color:#e8ff47;">Stack</span>
    </div>
    <div style="font-family:monospace; font-size:10px; color:#6b7280;
                letter-spacing:0.1em;">
      CHURN INTELLIGENCE · JAN 2023 – DEC 2024
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ROW 1 — KPI STRIP
# ══════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("Total Churns", f"{kpis['total_churns']:,}",
              f"↑ {kpis['dec_2024_churns']} in Dec 2024 alone")

with c2:
    st.metric("Refunds Issued", f"${kpis['total_refunds_usd']:,.2f}",
              f"{kpis['refund_event_count']} events · avg ${kpis['avg_refund_usd']:.2f}")

with c3:
    st.metric("Reactivations", f"{int(kpis['reactivations'])}",
              f"{kpis['reactivation_pct']:.1f}% of all churns")

with c4:
    st.metric("Top Reason", kpis["top_reason"],
              f"{kpis['top_reason_count']} events · {kpis['top_reason_pct']:.1f}%")

with c5:
    st.metric("Pre-Upgrade Churns", f"{int(kpis['pre_upgrade_churns'])}",
              f"{kpis['pre_upgrade_pct']:.1f}% had upgrade before")

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ROW 2 — BAR CHART + DONUT
# ══════════════════════════════════════════════════════════════════════════
left, right = st.columns([3, 2])

with left:
    df_monthly = get_monthly_volume(df)
    st.plotly_chart(monthly_bar(df_monthly),
                    use_container_width=True, config={"displayModeBar": False})

with right:
    df_reasons = get_reason_breakdown(df)
    st.plotly_chart(reason_donut(df_reasons),
                    use_container_width=True, config={"displayModeBar": False})

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ROW 3 — FEEDBACK + SIGNALS + REFUNDS
# ══════════════════════════════════════════════════════════════════════════
col1, col2, col3 = st.columns(3)

with col1:
    df_feedback = get_feedback_breakdown(df)
    st.plotly_chart(feedback_bars(df_feedback),
                    use_container_width=True, config={"displayModeBar": False})

with col2:
    df_signals = get_signals(df)
    st.plotly_chart(signal_bars(df_signals),
                    use_container_width=True, config={"displayModeBar": False})

with col3:
    # Refund summary numbers
    r1, r2 = st.columns(2)
    with r1:
        st.metric("Total Issued", f"${kpis['total_refunds_usd']:,.0f}")
    with r2:
        st.metric("Avg (when issued)", f"${kpis['avg_refund_usd']:.2f}")

    df_refund = get_refund_by_reason(df)
    st.plotly_chart(refund_rate_bars(df_refund),
                    use_container_width=True, config={"displayModeBar": False})

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ROW 4 — HEATMAP + QUARTERLY TREND
# ══════════════════════════════════════════════════════════════════════════
left2, right2 = st.columns([2, 3])

with left2:
    pivot = get_heatmap(df)
    st.plotly_chart(reason_feedback_heatmap(pivot),
                    use_container_width=True, config={"displayModeBar": False})

with right2:
    df_qtly = get_quarterly_trend(df)
    st.plotly_chart(quarterly_trend(df_qtly),
                    use_container_width=True, config={"displayModeBar": False})
