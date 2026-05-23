# HTS Experiment Simulator

A lightweight, decision-support prototype for sizing A/B experiments and estimating monetization upside in travel commerce contexts — fintech attach, disruption assistance, ad relevance, and checkout placement.

**Live demo:** [trell-j-hts-experiment-simulato-hts-experiment-simulator-u00skg.streamlit.app](https://trell-j-hts-experiment-simulato-hts-experiment-simulator-u00skg.streamlit.app/)

> Illustrative portfolio project by Terrell Johnson, built to accompany an application for a Senior Strategy & Operations Manager role at HTS Media / Hopper. This is **not** an official Hopper or HTS Media product and is **not affiliated with** Hopper, Inc. No proprietary branding, data, or systems are used.

---

## Overview

Growth and monetization teams routinely need a quick, defensible answer to three questions before they put an experiment in front of engineering:

1. How many users do we need per variant to detect the effect we care about?
2. How long will the test run given our traffic?
3. If the lift holds, how much annualized revenue is on the table?

This simulator answers those three questions in a single screen. It is designed for strategy & operations work — pre-engineering sizing, prioritization conversations, and hypothesis framing — not for replacing a production experimentation platform.

## Live Demo

[https://trell-j-hts-experiment-simulato-hts-experiment-simulator-u00skg.streamlit.app/](https://trell-j-hts-experiment-simulato-hts-experiment-simulator-u00skg.streamlit.app/)

## Key Features

- **Sample size calculator** — two-proportion z-test with pooled variance, configurable confidence (90 / 95 / 99%) and power (70 / 80 / 90%).
- **Test duration estimate** — derived from required sample size and configurable daily eligible traffic.
- **Annualized revenue lift estimate** — projects daily and annual revenue impact from MDE, traffic, and average revenue per conversion.
- **Scenario presets** — preloaded travel-commerce experiments (cancel-for-any-reason attach, disruption assistance upsell, ad relevance CTR, fintech checkout placement).
- **Diagnostics charts** — duration vs. MDE sensitivity, and cumulative control-vs-variant revenue trajectory over the test window.
- **Hypothesis & readout framing** — auto-generated strategy readout in PM/strategy language (metric, treatment, segment, projected lift).
- **Polished dark SaaS UI** — Inter typography, custom paper-plane mark, KPI cards, and a Streamlit dark theme configured for portfolio-grade presentation.

## Business Context

Travel commerce platforms monetize across multiple, often-overlapping surfaces: fintech attach (e.g., flexibility / cancel-for-any-reason / price-freeze style products), disruption assistance, ad inventory, and merchandising placements. Each surface has its own baseline conversion rate, audience size, and unit economics — and every team competes for the same engineering capacity.

The simulator helps a Strategy & Operations partner:

- **Pre-screen experiment ideas** before they enter the backlog.
- **Quantify the prize** in a consistent, comparable way across teams.
- **De-risk go/no-go conversations** by making statistical assumptions explicit (MDE, power, confidence, split).
- **Frame hypotheses** in a structured, reviewable format that pairs with PRDs and roadmap reviews.

## How It Works

1. Pick a **scenario preset** (or "Custom") in the sidebar.
2. Tune **experiment parameters** — baseline conversion / attach rate, minimum detectable effect (MDE), confidence, and power.
3. Tune **traffic & revenue context** — daily eligible users, average revenue per conversion, and the control/variant split.
4. Read the **KPI cards**: per-variant sample size, total sample, estimated test duration, and projected annual revenue lift.
5. Inspect the **diagnostics charts** to see how MDE choice trades off against test duration and to visualize cumulative control vs. variant revenue.
6. Fill in the **hypothesis builder** (metric, treatment, segment) to get a one-paragraph strategy readout you can paste into a doc.

## Methodology & Statistical Assumptions

- **Test type:** two-sided two-proportion z-test with pooled variance.
- **Sample size formula:**
  `n_per_variant = ⌈ 2 · p̄(1 − p̄) · (z_{1−α/2} + z_{1−β})² / Δ² ⌉`
  where `p̄ = (p_control + p_variant) / 2` and `Δ = MDE`.
- **Defaults:** 95% confidence, 80% power, 50/50 traffic split.
- **Duration:** `⌈ total_sample / daily_eligible_traffic ⌉` (rounded up to whole days; assumes constant daily eligibility).
- **Revenue lift:** `daily_eligible_traffic · MDE · avg_revenue_per_conversion`, annualized by × 365.

The model intentionally assumes a single proportion-based primary metric, no novelty/seasonality decay, no peeking correction, and no segmentation effects. It is meant to be a fast sizing aid — not a replacement for a full experimentation platform.

## Tech Stack

- **Python 3.9+**
- **Streamlit** — UI and app shell
- **SciPy** — z-test critical values
- **NumPy** — calculations
- **Plotly** — diagnostics charts
- Custom CSS / dark theme via `.streamlit/config.toml`

## Example Use Cases / Scenarios

The app ships with four preset scenarios that reflect real travel-commerce experimentation patterns:

| Scenario | Baseline | MDE | Daily Eligible | Avg Revenue |
|---|---|---|---|---|
| Cancel for Any Reason — attach rate lift | 30% | 5pp | 5,000 | $18.50 |
| Disruption Assistance — upsell trigger | 12% | 3pp | 3,000 | $22.00 |
| Ad Relevance Score — CTR improvement | 4.5% | 0.8pp | 50,000 | $2.20 |
| Fintech Attach — checkout placement test | 28% | 4pp | 8,000 | $15.00 |

A "Custom" preset is also available for ad-hoc sizing.

## Local Setup

Requires Python 3.9+.

```bash
# Clone
git clone https://github.com/TRell-J/hts-experiment-simulator.git
cd hts-experiment-simulator

# (Optional) virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install
pip install -r requirements.txt

# Run
streamlit run hts_experiment_simulator.py
```

The app opens at `http://localhost:8501`. The dark theme is configured in `.streamlit/config.toml` and applies automatically.

## Limitations

- **Illustrative, not production.** This is a decision-support prototype — not a replacement for an experimentation platform (Statsig, Eppo, Optimizely, in-house, etc.).
- **Proportion metrics only.** No support for continuous metrics, ratio metrics, CUPED, or variance reduction.
- **No segmentation / heterogeneity.** Treats the eligible audience as homogeneous.
- **No peeking, sequential testing, or multiple-comparison correction.** Assumes a single fixed-horizon test on one primary metric.
- **Static traffic and revenue.** No seasonality, novelty effects, or cannibalization modeling.
- **Revenue numbers are illustrative.** Inputs are user-supplied; the tool does not pull or assume any real Hopper / HTS Media data.

## Roadmap / Future Enhancements

- Continuous metric support (t-test sizing, Welch's correction).
- Sequential / always-valid inference option (e.g., mSPRT-style bounds).
- Variance reduction (CUPED) sensitivity inputs.
- Segment-level sizing (mobile vs. desktop, new vs. returning, route value bands).
- Multi-metric guardrail framing (primary + counter-metrics).
- Export-to-doc: one-click PRD-ready hypothesis & sizing brief.
- Saved scenario history with shareable links.

## Author

**Terrell Johnson** — Strategy & Operations
Built as a portfolio supplement for a Senior Strategy & Operations Manager application to HTS Media / Hopper.

For questions or feedback, please open an issue on this repository.

---

*Disclaimer: This project is an independent portfolio prototype. It is not affiliated with, endorsed by, or sponsored by Hopper, Inc. or HTS Media. All scenario presets, numbers, and copy are illustrative.*
