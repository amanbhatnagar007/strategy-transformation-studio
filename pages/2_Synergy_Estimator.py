import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.synergy_logic import estimate_synergies, synergy_summary

st.set_page_config(page_title="M&A Synergy Estimator", page_icon="🔗", layout="wide")
page_header("🔗 M&A Synergy Estimator",
            "Size revenue and cost synergies for a deal, phase them to run-rate, and test value creation "
            "against the purchase price — the analysis behind $100M+ of identified synergies on real transactions.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Targets")
    acq_rev = st.number_input("Acquirer revenue ($M)", 50, 200000, 4000, step=50)
    tgt_rev = st.number_input("Target revenue ($M)", 10, 100000, 1200, step=10)
    deal_value = st.number_input("Deal value ($M)", 10, 300000, 2200, step=50)
    integration_cost = st.number_input("Integration cost ($M)", 0, 50000, 120, step=10)
    st.header("Target economics")
    tgt_sga_pct = st.slider("Target SG&A (% of revenue)", 5, 50, 24)
    tgt_cogs_pct = st.slider("Target COGS (% of revenue)", 20, 85, 55)
    st.header("Synergy drivers")
    overlap = st.slider("Business / cost overlap", 0.0, 1.0, 0.6, 0.05)
    cross_sell = st.slider("Cross-sell potential", 0.0, 1.0, 0.5, 0.05)
    pricing_power = st.slider("Pricing power", 0.0, 1.0, 0.3, 0.05)

s = estimate_synergies(acq_rev, tgt_rev, tgt_sga_pct, tgt_cogs_pct, overlap,
                       cross_sell, pricing_power, deal_value, integration_cost)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${s["total_runrate"]:,.0f}M</div><div class="l">Run-rate synergies</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{s["pct_of_deal"]}%</div><div class="l">of deal value</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${s["npv"]:,.0f}M</div><div class="l">Synergy NPV @10%</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{s["payback_ratio"]}×</div><div class="l">Integration cost / run-rate</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🧱 Synergy bridge", "📅 Phasing", "📋 Executive summary"])

with t1:
    st.markdown("#### Where the value comes from")
    cL, cR = st.columns(2)
    with cL:
        cb = s["cost_breakdown"]
        fig = go.Figure(go.Bar(x=list(cb.values()), y=list(cb.keys()), orientation="h",
                               marker_color="#8B6CFF", text=[f"${v}M" for v in cb.values()], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=240, title="Cost synergies",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=30, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        rb = s["rev_breakdown"]
        fig = go.Figure(go.Bar(x=list(rb.values()), y=list(rb.keys()), orientation="h",
                               marker_color="#22D3EE", text=[f"${v}M" for v in rb.values()], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=240, title="Revenue synergies (EBITDA contribution)",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=30, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">Cost synergies (SG&A de-duplication, procurement scale, '
          'footprint) are higher-confidence and front-loaded. Revenue synergies are margin-adjusted and '
          'should be validated in commercial due diligence before crediting them to the deal model.</div>')

with t2:
    st.markdown("#### Synergy realization to run-rate")
    df = pd.DataFrame(s["rows"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Year"], y=df["Cost syn ($M)"], name="Cost", marker_color="#8B6CFF"))
    fig.add_trace(go.Bar(x=df["Year"], y=df["Revenue syn ($M)"], name="Revenue", marker_color="#22D3EE"))
    fig.update_layout(template="plotly_dark", height=320, barmode="stack",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="Synergies realized ($M)", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{synergy_summary(s, deal_value)}</div>')
    st.download_button("⬇ Download synergy phasing (CSV)", pd.DataFrame(s["rows"]).to_csv(index=False),
                       file_name="synergy_phasing.csv", mime="text/csv")

st.caption("AI-assisted heuristic synergy model for screening & diligence framing. "
           f"Directional, not investment advice. For deal support: {PROFILE['email']}.")
