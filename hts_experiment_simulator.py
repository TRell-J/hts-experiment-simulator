import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go

st.set_page_config(
    page_title="HTS Media · Experiment Simulator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens ──────────────────────────────────────────────────────────────
BG          = "#0B0E14"   # canvas
SURFACE     = "#11151F"   # card
SURFACE_2   = "#161B27"   # elevated card
BORDER      = "#1F2533"   # hairline
BORDER_HI   = "#2A3142"   # hover / focus
TEXT        = "#E6E8EF"
TEXT_DIM    = "#8A93A6"
TEXT_MUTED  = "#5B6478"

ACCENT      = "#22D3EE"            # cyan — data primary
ACCENT_SOFT = "rgba(34,211,238,0.12)"
ACCENT_LINE = "rgba(34,211,238,0.45)"
WARM        = "#F97316"            # burnt orange — emphasis / variant
WARM_SOFT   = "rgba(249,115,22,0.10)"
SUCCESS     = "#34D399"
CAUTION     = "#FBBF24"
DANGER      = "#F87171"

CHART_BG    = SURFACE
GRID_COLOR  = "#1B2231"
AXIS_COLOR  = "#3A4356"
FONT_COLOR  = TEXT

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Base */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: {BG};
        color: {TEXT};
        -webkit-font-smoothing: antialiased;
    }}

    /* Hide the default Streamlit chrome a bit — scoped narrowly to avoid
       hiding any future <footer> element that may wrap app content. */
    #MainMenu {{ visibility: hidden; }}
    footer[class*="viewerBadge"], div[class*="viewerBadge"] {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}
    .block-container {{
        padding-top: 1.4rem !important;
        padding-bottom: 7rem !important;
        max-width: 1400px;
    }}

    /* Typography */
    h1, h2, h3, h4 {{
        font-family: 'Inter', sans-serif;
        color: {TEXT};
        letter-spacing: -0.018em;
    }}
    p, span, label, div {{ color: {TEXT}; }}

    /* Hero ─────────────────────────────────────────────────────── */
    .hero {{
        position: relative;
        padding: 28px 32px 26px 32px;
        margin: 0 0 26px 0;
        background:
            radial-gradient(900px 220px at 0% 0%, rgba(34,211,238,0.07), transparent 60%),
            radial-gradient(700px 200px at 100% 0%, rgba(249,115,22,0.06), transparent 60%),
            linear-gradient(180deg, {SURFACE_2} 0%, {SURFACE} 100%);
        border: 1px solid {BORDER};
        border-radius: 16px;
        overflow: hidden;
    }}
    .hero::before {{
        content: "";
        position: absolute; top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, {ACCENT_LINE}, transparent);
    }}
    .hero-row {{
        display: flex; align-items: center; justify-content: space-between;
        gap: 24px; flex-wrap: wrap;
    }}
    .brand {{
        display: flex; align-items: center; gap: 14px;
    }}
    .brand-mark {{
        width: 38px; height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, {ACCENT} 0%, #0EA5B7 100%);
        display: flex; align-items: center; justify-content: center;
        color: #06222A; font-weight: 800; font-size: 1.15rem;
        box-shadow: 0 8px 22px -8px rgba(34,211,238,0.55), inset 0 1px 0 rgba(255,255,255,0.25);
    }}
    .brand-title {{
        font-size: 1.45rem; font-weight: 700; letter-spacing: -0.02em;
        color: {TEXT}; line-height: 1.1;
    }}
    .brand-sub {{
        font-size: 0.82rem; color: {TEXT_DIM};
        font-weight: 500; margin-top: 2px;
    }}
    .pill {{
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 12px; border-radius: 999px;
        background: rgba(52,211,153,0.10);
        border: 1px solid rgba(52,211,153,0.25);
        color: {SUCCESS}; font-size: 0.72rem; font-weight: 600;
        letter-spacing: 0.04em; text-transform: uppercase;
    }}
    .pill-dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: {SUCCESS};
        box-shadow: 0 0 0 0 rgba(52,211,153,0.6);
        animation: pulse 2.2s infinite;
    }}
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0.5); }}
        70% {{ box-shadow: 0 0 0 8px rgba(52,211,153,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0); }}
    }}
    .tagline {{
        margin-top: 14px;
        color: {TEXT_DIM};
        font-size: 0.95rem;
        max-width: 760px;
        line-height: 1.55;
    }}

    /* Section header ──────────────────────────────────────────── */
    .section-header {{
        display: flex; align-items: center; justify-content: space-between;
        margin: 4px 0 14px 0;
    }}
    .section-title {{
        display: flex; align-items: center; gap: 10px;
        font-size: 0.78rem; font-weight: 700;
        color: {TEXT}; letter-spacing: 0.12em; text-transform: uppercase;
    }}
    .section-title::before {{
        content: ""; width: 3px; height: 14px; border-radius: 2px;
        background: linear-gradient(180deg, {ACCENT}, #0EA5B7);
    }}
    .section-eyebrow {{
        font-size: 0.72rem; color: {TEXT_MUTED};
        font-weight: 500; letter-spacing: 0.04em;
    }}

    /* Card surface ────────────────────────────────────────────── */
    .card {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 22px 24px;
        transition: border-color 160ms ease, transform 160ms ease;
    }}
    .card:hover {{ border-color: {BORDER_HI}; }}

    /* Input group head (no surrounding card — heading + sub above inputs) */
    .group-head {{
        margin: 4px 0 14px 0;
    }}
    .group-title {{
        font-size: 0.98rem;
        font-weight: 700;
        color: {TEXT};
        letter-spacing: -0.01em;
    }}
    .group-sub {{
        font-size: 0.8rem;
        color: {TEXT_MUTED};
        margin-top: 3px;
    }}

    /* Chart head (above each plotly chart) */
    .chart-head {{ margin: 2px 0 10px 0; }}
    .chart-head-row {{
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 12px;
    }}
    .chart-title {{
        font-size: 0.98rem;
        font-weight: 700;
        color: {TEXT};
        letter-spacing: -0.01em;
    }}
    .chart-eyebrow {{
        font-size: 0.7rem;
        color: {TEXT_MUTED};
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 600;
    }}
    .chart-sub {{
        font-size: 0.8rem;
        color: {TEXT_MUTED};
        margin-top: 3px;
    }}

    /* KPI metric containers ───────────────────────────────────── */
    div[data-testid="stMetric"] {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 20px 16px 20px;
        position: relative;
        overflow: hidden;
        transition: border-color 200ms ease, transform 200ms ease;
    }}
    div[data-testid="stMetric"]::before {{
        content: ""; position: absolute; top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, {ACCENT}, rgba(34,211,238,0));
        opacity: 0.6;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {BORDER_HI};
        transform: translateY(-1px);
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: {TEXT} !important;
        line-height: 1.1 !important;
        font-feature-settings: "tnum";
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: {TEXT_MUTED} !important;
        margin-bottom: 6px !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: {TEXT_MUTED} !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: {SUCCESS} !important;
    }}
    [data-testid="stMetricDelta"] svg {{ display: none; }}

    /* Sidebar ──────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: {SURFACE} !important;
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.8rem !important;
    }}
    .sidebar-section {{
        font-size: 0.7rem;
        font-weight: 700;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 18px 0 10px 0;
    }}
    .sidebar-brand {{
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 6px;
    }}
    .sidebar-brand-mark {{
        width: 28px; height: 28px; border-radius: 8px;
        background: linear-gradient(135deg, {ACCENT} 0%, #0EA5B7 100%);
        display: flex; align-items: center; justify-content: center;
        color: #06222A; font-weight: 800; font-size: 0.85rem;
    }}
    .sidebar-brand-text {{
        font-size: 0.95rem; font-weight: 700; color: {TEXT};
        letter-spacing: -0.01em;
    }}

    /* Form controls ───────────────────────────────────────────── */
    .stSlider > label, .stSelectSlider > label, .stNumberInput > label,
    .stSelectbox > label, .stTextInput > label {{
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        color: {TEXT_DIM} !important;
        letter-spacing: 0.01em;
    }}

    /* Slider track recolor */
    .stSlider [data-baseweb="slider"] > div > div {{
        background: {BORDER} !important;
    }}
    .stSlider [data-baseweb="slider"] [role="slider"] {{
        background: {ACCENT} !important;
        border: 2px solid {BG} !important;
        box-shadow: 0 0 0 3px rgba(34,211,238,0.18) !important;
    }}

    /* Number / text input */
    .stNumberInput input, .stTextInput input {{
        background: {SURFACE_2} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        color: {TEXT} !important;
        font-feature-settings: "tnum";
    }}
    .stNumberInput input:focus, .stTextInput input:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 3px rgba(34,211,238,0.12) !important;
    }}
    .stSelectbox > div > div {{
        background: {SURFACE_2} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
    }}

    /* Expander */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {{
        background: {SURFACE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: {TEXT} !important;
        padding: 14px 18px !important;
    }}
    [data-testid="stExpander"] {{
        border: none !important;
    }}
    [data-testid="stExpander"] details {{
        background: transparent !important;
        border: 1px solid {BORDER};
        border-radius: 12px;
        overflow: hidden;
    }}
    [data-testid="stExpander"] details[open] summary {{
        border-bottom: 1px solid {BORDER} !important;
        border-radius: 12px 12px 0 0 !important;
    }}

    /* Dividers */
    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, {BORDER}, transparent) !important;
        margin: 28px 0 !important;
    }}

    /* Recommendation chips replace default st.alert */
    .rec {{
        display: flex; align-items: flex-start; gap: 14px;
        padding: 18px 22px;
        border-radius: 14px;
        border: 1px solid {BORDER};
        background: {SURFACE};
        position: relative;
        overflow: hidden;
    }}
    .rec::before {{
        content: ""; position: absolute; left: 0; top: 0; bottom: 0;
        width: 3px;
    }}
    .rec.rec-success::before {{ background: {SUCCESS}; }}
    .rec.rec-info::before    {{ background: {ACCENT}; }}
    .rec.rec-warn::before    {{ background: {CAUTION}; }}
    .rec.rec-danger::before  {{ background: {DANGER}; }}
    .rec-icon {{
        width: 36px; height: 36px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem; flex-shrink: 0;
    }}
    .rec-success .rec-icon {{ background: rgba(52,211,153,0.12); color: {SUCCESS}; }}
    .rec-info    .rec-icon {{ background: rgba(34,211,238,0.12); color: {ACCENT}; }}
    .rec-warn    .rec-icon {{ background: rgba(251,191,36,0.12); color: {CAUTION}; }}
    .rec-danger  .rec-icon {{ background: rgba(248,113,113,0.12); color: {DANGER}; }}
    .rec-title {{
        font-weight: 700; font-size: 0.95rem; color: {TEXT};
        margin: 1px 0 4px 0;
    }}
    .rec-body {{
        color: {TEXT_DIM}; font-size: 0.88rem; line-height: 1.5;
    }}

    /* Hypothesis output */
    .hypo-card {{
        background: linear-gradient(180deg, {SURFACE_2} 0%, {SURFACE} 100%);
        border: 1px solid {BORDER};
        border-left: 3px solid {ACCENT};
        border-radius: 12px;
        padding: 20px 22px;
        font-size: 0.95rem;
        line-height: 1.65;
        color: {TEXT};
    }}
    .hypo-card strong {{ color: {ACCENT}; font-weight: 700; }}
    .hypo-card em {{
        font-style: normal;
        color: {WARM};
        background: {WARM_SOFT};
        padding: 1px 6px; border-radius: 4px;
        font-weight: 500;
    }}

    /* Footer */
    .footer {{
        margin-top: 36px;
        padding-top: 18px;
        border-top: 1px solid {BORDER};
        display: flex; align-items: center; justify-content: space-between;
        flex-wrap: wrap; gap: 12px;
        color: {TEXT_MUTED}; font-size: 0.78rem;
    }}
    .footer-mono {{ font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: {TEXT_MUTED}; }}

    /* Plotly modebar — keep but tone down */
    .modebar {{ opacity: 0.25 !important; transition: opacity 200ms ease; }}
    .modebar:hover {{ opacity: 0.9 !important; }}

    /* Caption color refinement */
    [data-testid="stCaptionContainer"], .stCaption, small {{
        color: {TEXT_MUTED} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-row">
    <div class="brand">
      <div class="brand-mark">HJ</div>
      <div>
        <div class="brand-title">HTS Media · Experiment Simulator</div>
        <div class="brand-sub">A/B test sizing &nbsp;·&nbsp; revenue impact &nbsp;·&nbsp; hypothesis design</div>
      </div>
    </div>
    <div class="pill"><span class="pill-dot"></span>Live · v1.2</div>
  </div>
  <div class="tagline">
    Design lightweight experiments to validate monetization and growth hypotheses —
    without roadmap drag. Built to size HTS Media experiments before committing engineering resources.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Presets ────────────────────────────────────────────────────────────────────
PRESETS = {
    "Custom": dict(baseline=0.30, mde=0.05, daily_traffic=5000, avg_revenue=18.50, confidence=0.95, power=0.80),
    "Cancel for Any Reason — Attach Rate Lift": dict(baseline=0.30, mde=0.05, daily_traffic=5000, avg_revenue=18.50, confidence=0.95, power=0.80),
    "Disruption Assistance — Upsell Trigger":   dict(baseline=0.12, mde=0.03, daily_traffic=3000, avg_revenue=22.00, confidence=0.95, power=0.80),
    "Ad Relevance Score — CTR Improvement":     dict(baseline=0.045, mde=0.008, daily_traffic=50000, avg_revenue=2.20, confidence=0.95, power=0.80),
    "Fintech Attach — Checkout Placement Test": dict(baseline=0.28, mde=0.04, daily_traffic=8000, avg_revenue=15.00, confidence=0.95, power=0.80),
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
      <div class="sidebar-brand-mark">HJ</div>
      <div class="sidebar-brand-text">HTS Media</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Strategy & Operations · Experiment Design")

    st.markdown('<div class="sidebar-section">Scenario presets</div>', unsafe_allow_html=True)
    scenario = st.selectbox("Load a preset", list(PRESETS.keys()), label_visibility="collapsed")
    p = PRESETS[scenario]

    st.markdown('<div class="sidebar-section">About</div>', unsafe_allow_html=True)
    st.caption(
        "Size A/B experiments before committing engineering resources. "
        "Inputs flow through power calculation to estimate sample size, "
        "test duration, and projected revenue impact."
    )

    st.markdown('<div class="sidebar-section">Methodology</div>', unsafe_allow_html=True)
    st.caption(
        "Two-proportion z-test with pooled variance. "
        "Defaults to 95% confidence and 80% power — adjust to match your team's risk tolerance."
    )

    st.markdown('<div class="sidebar-section">Author</div>', unsafe_allow_html=True)
    st.caption("**Terrell Johnson** — Strategy & Operations")

# ── Inputs ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><div class="section-title">Inputs</div><div class="section-eyebrow">Adjust to model your experiment</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(f"""
    <div class="group-head">
      <div class="group-title">Experiment parameters</div>
      <div class="group-sub">Statistical setup for the test</div>
    </div>
    """, unsafe_allow_html=True)
    baseline_rate = st.slider("Baseline conversion / attach rate", 0.01, 0.80, float(p["baseline"]), 0.01, format="%.2f")
    mde           = st.slider("Minimum detectable effect (MDE)",   0.005, 0.20, float(p["mde"]),      0.005, format="%.3f")
    confidence    = st.select_slider("Confidence level",  options=[0.90, 0.95, 0.99], value=p["confidence"])
    power         = st.select_slider("Statistical power", options=[0.70, 0.80, 0.90], value=p["power"])

with col2:
    st.markdown(f"""
    <div class="group-head">
      <div class="group-title">Traffic &amp; revenue context</div>
      <div class="group-sub">Volume and unit economics</div>
    </div>
    """, unsafe_allow_html=True)
    daily_traffic = st.number_input("Daily users eligible for test",      100, 500_000, int(p["daily_traffic"]), 500)
    avg_rev       = st.number_input("Avg revenue per conversion ($)",     0.50, 500.0,  float(p["avg_revenue"]), 0.50)
    test_split    = st.slider("Traffic split — control / variant",        0.3, 0.7, 0.5, 0.05)

# ── Calculations ───────────────────────────────────────────────────────────────
def calc_n(base, effect, conf, pwr):
    z_a  = stats.norm.ppf(1 - (1 - conf) / 2)
    z_b  = stats.norm.ppf(pwr)
    pool = (base + base + effect) / 2
    return int(np.ceil(2 * pool * (1 - pool) * (z_a + z_b)**2 / effect**2))

n_per       = calc_n(baseline_rate, mde, confidence, power)
total       = n_per * 2
dur         = int(np.ceil(total / daily_traffic))
v_rate      = baseline_rate + mde
daily_lift  = daily_traffic * mde * avg_rev
annual_lift = daily_lift * 365

# ── Readout ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><div class="section-title">Readout</div><div class="section-eyebrow">Key metrics from your setup</div></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Sample size · per variant", f"{n_per:,}")
m2.metric("Total sample needed",       f"{total:,}")
m3.metric("Estimated test duration",   f"{dur} days")
m4.metric("Est. annual revenue lift",  f"${annual_lift:,.0f}", delta=f"+${daily_lift:,.0f}/day")

# ── Charts ─────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><div class="section-title">Diagnostics</div><div class="section-eyebrow">How your inputs interact</div></div>', unsafe_allow_html=True)

LAYOUT_BASE = dict(
    plot_bgcolor=CHART_BG,
    paper_bgcolor=CHART_BG,
    font=dict(family="Inter, sans-serif", size=12, color=FONT_COLOR),
    margin=dict(l=8, r=8, t=12, b=8),
    height=340,
    hoverlabel=dict(
        bgcolor=SURFACE_2,
        bordercolor=BORDER_HI,
        font=dict(family="Inter, sans-serif", size=12, color=TEXT),
    ),
)

AXIS_STYLE = dict(
    gridcolor=GRID_COLOR,
    zeroline=False,
    showline=True,
    linecolor=AXIS_COLOR,
    linewidth=1,
    tickfont=dict(color=TEXT_DIM, size=11),
    title_font=dict(size=11, color=TEXT_DIM),
)

PLOTLY_CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

v1, v2 = st.columns(2, gap="large")

with v1:
    st.markdown(f"""
    <div class="chart-head">
      <div class="chart-head-row">
        <div class="chart-title">Power curve</div>
        <div class="chart-eyebrow">Duration vs. MDE</div>
      </div>
      <div class="chart-sub">Smaller effects need more samples — see where your MDE lands.</div>
    </div>
    """, unsafe_allow_html=True)

    mde_range = np.linspace(max(0.005, mde * 0.2), mde * 3, 80)
    dur_range = [int(np.ceil(calc_n(baseline_rate, m, confidence, power) * 2 / daily_traffic)) for m in mde_range]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=[m * 100 for m in mde_range], y=dur_range,
        mode="lines", fill="tozeroy",
        line=dict(color=ACCENT, width=2.5, shape="spline", smoothing=0.6),
        fillcolor=ACCENT_SOFT,
        hovertemplate="<b>MDE</b> %{x:.2f}%<br><b>Duration</b> %{y} days<extra></extra>"
    ))
    fig1.add_vline(
        x=mde * 100,
        line=dict(color=WARM, width=2, dash="dot"),
        annotation_text=f" Your MDE · {mde*100:.1f}%",
        annotation_font=dict(color=WARM, size=11, family="Inter"),
        annotation_position="top right",
        annotation_bgcolor="rgba(11,14,20,0.85)",
        annotation_bordercolor=WARM,
        annotation_borderwidth=1,
    )
    fig1.update_layout(**LAYOUT_BASE)
    fig1.update_xaxes(title_text="Minimum detectable effect (%)", **AXIS_STYLE)
    fig1.update_yaxes(title_text="Test duration (days)", **AXIS_STYLE)
    st.plotly_chart(fig1, use_container_width=True, config=PLOTLY_CONFIG)

with v2:
    st.markdown(f"""
    <div class="chart-head">
      <div class="chart-head-row">
        <div class="chart-title">Cumulative revenue</div>
        <div class="chart-eyebrow">Control vs. variant</div>
      </div>
      <div class="chart-sub">Projected revenue paths over the test window.</div>
    </div>
    """, unsafe_allow_html=True)

    days   = list(range(1, min(dur * 2, 90) + 1))
    ctrl_r = [daily_traffic * test_split       * baseline_rate * avg_rev * d for d in days]
    var_r  = [daily_traffic * (1 - test_split) * v_rate        * avg_rev * d for d in days]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=days, y=ctrl_r, name="Control",
        line=dict(color=TEXT_MUTED, width=2, dash="dot"),
        hovertemplate="<b>Day %{x}</b><br>Control · $%{y:,.0f}<extra></extra>"
    ))
    fig2.add_trace(go.Scatter(
        x=days, y=var_r, name="Variant",
        line=dict(color=ACCENT, width=2.6, shape="spline", smoothing=0.4),
        fill="tonexty", fillcolor=ACCENT_SOFT,
        hovertemplate="<b>Day %{x}</b><br>Variant · $%{y:,.0f}<extra></extra>"
    ))
    fig2.add_vline(
        x=dur,
        line=dict(color=WARM, width=2, dash="dot"),
        annotation_text=" Significance reached",
        annotation_font=dict(color=WARM, size=11, family="Inter"),
        annotation_position="top left",
        annotation_bgcolor="rgba(11,14,20,0.85)",
        annotation_bordercolor=WARM,
        annotation_borderwidth=1,
    )
    fig2.update_layout(
        **LAYOUT_BASE,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11, color=TEXT_DIM),
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
            itemsizing="constant",
        )
    )
    fig2.update_xaxes(title_text="Days", **AXIS_STYLE)
    fig2.update_yaxes(title_text="Cumulative revenue ($)", **AXIS_STYLE)
    st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

# ── Recommendation ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><div class="section-title">Recommendation</div><div class="section-eyebrow">Go / no-go signal</div></div>', unsafe_allow_html=True)

if dur <= 7:
    rec_cls, rec_icon, rec_title = "rec-success", "✓", "Green light"
    rec_body = f"Reaches statistical significance in <strong>{dur} day{'s' if dur != 1 else ''}</strong>. Minimal business risk — run it immediately."
elif dur <= 21:
    rec_cls, rec_icon, rec_title = "rec-info", "→", "Feasible"
    rec_body = f"<strong>{dur} days</strong> is a reasonable test window. Consider increasing traffic allocation or widening the MDE to compress the timeline."
elif dur <= 60:
    rec_cls, rec_icon, rec_title = "rec-warn", "!", "Caution"
    rec_body = f"<strong>{dur} days</strong> introduces seasonality risk. Try a higher MDE threshold, a larger traffic split, or targeting a higher-intent cohort."
else:
    rec_cls, rec_icon, rec_title = "rec-danger", "✕", "Too long"
    rec_body = f"<strong>{dur} days</strong> is not a lightweight experiment. Increase daily traffic eligibility, raise the MDE, or redesign as a holdout test on a targeted segment."

st.markdown(f"""
<div class="rec {rec_cls}">
  <div class="rec-icon">{rec_icon}</div>
  <div>
    <div class="rec-title">{rec_title}</div>
    <div class="rec-body">{rec_body}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hypothesis Builder ─────────────────────────────────────────────────────────
st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><div class="section-title">Hypothesis builder</div><div class="section-eyebrow">Drop into your brief</div></div>', unsafe_allow_html=True)

with st.expander("Generate your experiment hypothesis statement", expanded=False):
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        metric_name = st.text_input("Metric being tested",              value="fintech attach rate")
    with hcol2:
        treatment   = st.text_input("Treatment (what you're changing)", value="surfacing Cancel for Any Reason earlier in checkout")
    with hcol3:
        segment     = st.text_input("User segment",                     value="mobile users booking flights > $200")

    if metric_name and treatment and segment:
        st.markdown(f"""
<div class="hypo-card">
<strong>H1.</strong> Changing <em>{treatment}</em> for <em>{segment}</em>
will increase <em>{metric_name}</em> by at least
<strong>{mde*100:.1f}%</strong> (from {baseline_rate*100:.1f}% → {v_rate*100:.1f}%)
at <strong>{int(confidence*100)}%</strong> confidence within
<strong>{dur} days</strong>, generating an estimated
<strong>${annual_lift:,.0f}</strong> in annualized revenue lift.
</div>
        """, unsafe_allow_html=True)
        st.caption("Copy this into your experiment brief or stakeholder doc.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  <div>HTS Media · Experiment Design Framework</div>
  <div class="footer-mono">built by terrell johnson · strategy &amp; operations</div>
</div>
""", unsafe_allow_html=True)
