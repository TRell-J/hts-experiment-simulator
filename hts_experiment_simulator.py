import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go

st.set_page_config(
    page_title="HTS Media | A/B Experiment Simulator",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #FF6B35 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #888 !important;
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    section[data-testid="stSidebar"] {
        background: #111318 !important;
        border-right: 1px solid #2a2d35;
    }

    h1 { font-size: 2rem !important; font-weight: 700 !important; letter-spacing: -0.02em; }
    h2 { font-size: 1.1rem !important; font-weight: 600 !important; letter-spacing: -0.01em; }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
        margin-top: 8px;
    }
    .section-icon {
        font-size: 1.5rem;
        line-height: 1;
    }
    .metric-row [data-testid="metric-container"] {
        background: #1a1d24;
        border: 1px solid #2a2d35;
        border-radius: 12px;
        padding: 20px 24px;
    }
    div[data-testid="stHorizontalBlock"] > div {
        gap: 16px;
    }
    .stSlider > label { font-size: 0.85rem !important; font-weight: 500 !important; color: #ccc !important; }
    .stSelectSlider > label { font-size: 0.85rem !important; font-weight: 500 !important; color: #ccc !important; }
    .stNumberInput > label { font-size: 0.85rem !important; font-weight: 500 !important; color: #ccc !important; }

    hr { border-color: #2a2d35 !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## ✈️ &nbsp; HTS Media · A/B Experiment Simulator")
st.markdown("<p style='color:#888; font-size:0.9rem; margin-top:-12px;'>Design lightweight experiments to validate monetization and growth hypotheses — without roadmap drag.</p>", unsafe_allow_html=True)
st.divider()

# ── Presets ────────────────────────────────────────────────────────────────────
PRESETS = {
    "Custom": dict(baseline=0.30, mde=0.05, daily_traffic=5000, avg_revenue=18.50, confidence=0.95, power=0.80),
    "Cancel for Any Reason — Attach Rate Lift": dict(baseline=0.30, mde=0.05, daily_traffic=5000, avg_revenue=18.50, confidence=0.95, power=0.80),
    "Disruption Assistance — Upsell Trigger":   dict(baseline=0.12, mde=0.03, daily_traffic=3000, avg_revenue=22.00, confidence=0.95, power=0.80),
    "Ad Relevance Score — CTR Improvement":     dict(baseline=0.045, mde=0.008, daily_traffic=50000, avg_revenue=2.20, confidence=0.95, power=0.80),
    "Fintech Attach — Checkout Placement Test": dict(baseline=0.28, mde=0.04, daily_traffic=8000, avg_revenue=15.00, confidence=0.95, power=0.80),
}

CHART_BG    = "#16181f"
GRID_COLOR  = "#2a2d35"
FONT_COLOR  = "#e0e0e0"
ACCENT      = "#FF6B35"
ACCENT_SOFT = "rgba(255,107,53,0.15)"
BLUE        = "#4B8BFF"
GRAY_LINE   = "#555c6b"

with st.sidebar:
    st.markdown("<div style='font-size:1rem; font-weight:700; color:#fff; margin-bottom:4px;'>📋 &nbsp; Scenario Presets</div>", unsafe_allow_html=True)
    scenario = st.selectbox("Load a preset", list(PRESETS.keys()), label_visibility="collapsed")
    p = PRESETS[scenario]
    st.divider()
    st.markdown("<div style='font-size:0.8rem; font-weight:600; color:#aaa; text-transform:uppercase; letter-spacing:0.05em;'>About this tool</div>", unsafe_allow_html=True)
    st.caption("Built to size HTS Media experiments before committing engineering resources. Outputs: sample size, test duration, and revenue impact.")
    st.caption("Built by **Terrell Johnson** — Strategy & Operations")

# ── Inputs ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="section-header"><span class="section-icon">🎯</span> Experiment Parameters</div>', unsafe_allow_html=True)
    baseline_rate = st.slider("Baseline Conversion / Attach Rate", 0.01, 0.80, float(p["baseline"]), 0.01, format="%.2f")
    mde           = st.slider("Minimum Detectable Effect (MDE)",   0.005, 0.20, float(p["mde"]),      0.005, format="%.3f")
    confidence    = st.select_slider("Confidence Level",  options=[0.90, 0.95, 0.99], value=p["confidence"])
    power         = st.select_slider("Statistical Power", options=[0.70, 0.80, 0.90], value=p["power"])

with col2:
    st.markdown('<div class="section-header"><span class="section-icon">📊</span> Traffic & Revenue Context</div>', unsafe_allow_html=True)
    daily_traffic = st.number_input("Daily Users Eligible for Test",      100, 500_000, int(p["daily_traffic"]), 500)
    avg_rev       = st.number_input("Avg Revenue per Conversion ($)",     0.50, 500.0,  float(p["avg_revenue"]), 0.50)
    test_split    = st.slider("Traffic Split — Control / Variant",        0.3, 0.7, 0.5, 0.05)

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
st.divider()
st.markdown('<div class="section-header"><span class="section-icon">📈</span> Experiment Readout</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Sample Size (per variant)", f"{n_per:,}")
m2.metric("Total Sample Needed",       f"{total:,}")
m3.metric("Estimated Test Duration",   f"{dur} days")
m4.metric("Est. Annual Revenue Lift",  f"${annual_lift:,.0f}", delta=f"+${daily_lift:,.0f}/day")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
LAYOUT_BASE = dict(
    plot_bgcolor=CHART_BG,
    paper_bgcolor=CHART_BG,
    font=dict(family="Inter, sans-serif", size=12, color=FONT_COLOR),
    margin=dict(l=12, r=12, t=36, b=12),
    height=360,
)

v1, v2 = st.columns(2, gap="large")

with v1:
    st.markdown('<div class="section-header"><span class="section-icon">📉</span> Power Curve — Duration vs. MDE</div>', unsafe_allow_html=True)
    mde_range = np.linspace(max(0.005, mde * 0.2), mde * 3, 80)
    dur_range = [int(np.ceil(calc_n(baseline_rate, m, confidence, power) * 2 / daily_traffic)) for m in mde_range]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=[m * 100 for m in mde_range], y=dur_range,
        mode="lines", fill="tozeroy",
        line=dict(color=ACCENT, width=2.5),
        fillcolor=ACCENT_SOFT,
        hovertemplate="MDE: %{x:.1f}%<br>Duration: %{y} days<extra></extra>"
    ))
    fig1.add_vline(
        x=mde * 100, line_dash="dot", line_color=BLUE, line_width=2,
        annotation_text=f"  Your MDE: {mde*100:.1f}%",
        annotation_font=dict(color=BLUE, size=12),
        annotation_position="top right"
    )
    fig1.update_layout(**LAYOUT_BASE)
    fig1.update_xaxes(title_text="Min. Detectable Effect (%)", gridcolor=GRID_COLOR, zeroline=False, title_font=dict(size=11))
    fig1.update_yaxes(title_text="Test Duration (days)",       gridcolor=GRID_COLOR, zeroline=False, title_font=dict(size=11))
    st.plotly_chart(fig1, use_container_width=True)

with v2:
    st.markdown('<div class="section-header"><span class="section-icon">💰</span> Cumulative Revenue — Control vs. Variant</div>', unsafe_allow_html=True)
    days   = list(range(1, min(dur * 2, 90) + 1))
    ctrl_r = [daily_traffic * test_split       * baseline_rate * avg_rev * d for d in days]
    var_r  = [daily_traffic * (1 - test_split) * v_rate        * avg_rev * d for d in days]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=days, y=ctrl_r, name="Control",
        line=dict(color=GRAY_LINE, width=2, dash="dot"),
        hovertemplate="Day %{x}<br>Control: $%{y:,.0f}<extra></extra>"
    ))
    fig2.add_trace(go.Scatter(
        x=days, y=var_r, name="Variant",
        line=dict(color=ACCENT, width=3),
        fill="tonexty", fillcolor="rgba(255,107,53,0.07)",
        hovertemplate="Day %{x}<br>Variant: $%{y:,.0f}<extra></extra>"
    ))
    fig2.add_vline(
        x=dur, line_dash="dot", line_color=BLUE, line_width=2,
        annotation_text="  Significance reached",
        annotation_font=dict(color=BLUE, size=12),
        annotation_position="top left"
    )
    fig2.update_layout(
        **LAYOUT_BASE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)")
    )
    fig2.update_xaxes(title_text="Days",                   gridcolor=GRID_COLOR, zeroline=False, title_font=dict(size=11))
    fig2.update_yaxes(title_text="Cumulative Revenue ($)", gridcolor=GRID_COLOR, zeroline=False, title_font=dict(size=11))
    st.plotly_chart(fig2, use_container_width=True)

# ── Recommendation ─────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-header"><span class="section-icon">🧠</span> Experiment Recommendation</div>', unsafe_allow_html=True)

if dur <= 7:
    st.success(f"✅ **Green light.** Reaches statistical significance in {dur} day(s). Minimal business risk — run it immediately.")
elif dur <= 21:
    st.info(f"⚡ **Feasible.** {dur} days is reasonable. Consider increasing traffic allocation or widening the MDE to compress the timeline.")
elif dur <= 60:
    st.warning(f"⚠️ **Caution.** {dur} days introduces seasonality risk. Try a higher MDE threshold, a larger traffic split, or targeting a higher-intent cohort.")
else:
    st.error(f"🔴 **Too long.** {dur} days is not a lightweight experiment. Increase daily traffic eligibility, raise the MDE, or redesign as a holdout test on a targeted segment.")

# ── Hypothesis Builder ─────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-header"><span class="section-icon">📝</span> Hypothesis Builder</div>', unsafe_allow_html=True)

with st.expander("Generate your experiment hypothesis statement"):
    metric_name = st.text_input("Metric being tested",              value="fintech attach rate")
    treatment   = st.text_input("What you're changing (treatment)", value="surfacing Cancel for Any Reason earlier in checkout")
    segment     = st.text_input("User segment",                     value="mobile users booking flights > $200")

    if metric_name and treatment and segment:
        st.markdown(f"""
> **H1:** Changing *{treatment}* for *{segment}* will increase *{metric_name}*
> by at least **{mde*100:.1f}%** (from {baseline_rate*100:.1f}% → {v_rate*100:.1f}%)
> at **{int(confidence*100)}% confidence** within **{dur} days**,
> generating an estimated **${annual_lift:,.0f} in annualized revenue lift**.
        """)
        st.caption("Copy this into your experiment brief or stakeholder doc.")

st.divider()
st.markdown("<p style='color:#444; font-size:0.78rem;'>HTS Media · Experiment Design Framework · Built by Terrell Johnson — Strategy & Operations</p>", unsafe_allow_html=True)
