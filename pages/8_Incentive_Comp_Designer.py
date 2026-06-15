import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.incentive_logic import payout_curve, simulate_population, ic_summary

st.set_page_config(page_title="Incentive Comp Designer", page_icon="🎯", layout="wide")
page_header("🎯 Incentive Comp Designer",
            "Design a sales incentive plan — threshold, accelerator and cap — then simulate a rep population "
            "to see total payout cost and cost of sales before you roll it out. EY-certified SFE approach.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Plan design")
    target_total = st.number_input("Target total earnings ($)", 10000, 1000000, 120000, step=5000)
    base_pct = st.slider("Base (% of target)", 30, 90, 60)
    threshold = st.slider("Threshold (% quota to start paying)", 0, 90, 40)
    accelerator = st.slider("Accelerator above 100% (×)", 1.0, 4.0, 2.0, 0.1)
    cap = st.slider("Cap (% of target variable)", 100, 400, 250, step=10)
    st.header("Rep population")
    n_reps = st.number_input("Number of reps", 10, 10000, 200, step=10)
    mean_att = st.slider("Mean attainment (%)", 60, 130, 98)
    std_att = st.slider("Attainment spread (std %)", 5, 50, 22)
    avg_quota = st.number_input("Avg quota / rep ($ revenue)", 100000, 50000000, 1500000, step=50000)

xs, ys = payout_curve(target_total, base_pct, threshold, accelerator, cap)
sim = simulate_population(n_reps, mean_att, std_att, target_total, base_pct,
                          threshold, accelerator, cap, avg_quota)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${sim["avg_payout"]:,.0f}</div><div class="l">Avg payout / rep</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{sim["cost_of_sales"]}%</div><div class="l">Cost of sales</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{sim["pct_above_target"]}%</div><div class="l">Reps above target</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">${sim["total_payout"]/1e6:,.2f}M</div><div class="l">Total payout cost</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📈 Payout curve", "📊 Population", "📋 Executive summary"])

with t1:
    st.markdown("#### Earnings vs % quota attainment")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#8B6CFF", width=3),
                             name="Total earnings"))
    fig.add_hline(y=target_total, line_dash="dot", line_color="#22D3EE",
                  annotation_text="Target earnings", annotation_position="top left")
    fig.add_vline(x=100, line_dash="dot", line_color="rgba(255,255,255,.3)")
    fig.add_vline(x=threshold, line_dash="dot", line_color="rgba(245,166,35,.6)",
                  annotation_text="Threshold", annotation_position="top")
    fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="% quota attainment",
                      yaxis_title="Total earnings ($)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div style="color:#aab4d6;font-size:.85rem">No variable below {threshold}% attainment; linear to '
          f'target at 100%; {accelerator:.1f}× marginal rate above quota, capped at {cap}% of target variable. '
          f'Base/variable split: {base_pct}/{100-base_pct}.</div>')

with t2:
    st.markdown("#### Payout distribution across the rep population")
    fig = go.Figure(go.Histogram(x=sim["payouts"], nbinsx=30, marker_color="#22D3EE"))
    fig.add_vline(x=target_total, line_dash="dot", line_color="#8B6CFF",
                  annotation_text="Target", annotation_position="top")
    fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Payout per rep ($)",
                      yaxis_title="Reps", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div class="bullet">Simulated mean attainment: {sim["avg_attainment"]}% '
          f'({n_reps} reps, normal spread)</div>'
          f'<div class="bullet">{sim["pct_below_threshold"]}% of reps fall below threshold (zero variable)</div>'
          f'<div class="bullet">Estimated revenue generated: ${sim["revenue"]/1e6:,.1f}M</div>')

with t3:
    st.markdown("#### Board-ready read")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">'
          f'{ic_summary(sim, target_total, base_pct, threshold, accelerator, cap)}</div>')
    curve_df = pd.DataFrame({"Attainment %": np.round(xs, 1), "Total earnings ($)": np.round(ys)})
    st.download_button("⬇ Download payout curve (CSV)", curve_df.to_csv(index=False),
                       file_name="incentive_payout_curve.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for incentive-plan framing. Directional; simulated population, not "
           f"actual reps. For a tailored engagement: {PROFILE['email']}.")
