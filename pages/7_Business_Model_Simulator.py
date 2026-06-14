import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.bizmodel_logic import simulate, recommend, bm_summary, MODELS

st.set_page_config(page_title="Business Model Simulator", page_icon="📊", layout="wide")
page_header("📊 Business Model Simulator",
            "Compare capital, subscription, pay-per-use and hybrid commercial models on revenue ramp, "
            "lifetime value and durability — the analysis behind pay-per-use models now ~10% of a top-20 MedTech's revenue.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Demand")
    new_y1 = st.number_input("New customers in Year 1", 1, 1000000, 500, step=10)
    growth = st.slider("Annual new-customer growth (%)", -20, 100, 15)
    st.header("Price points")
    capital_price = st.number_input("Capital / one-time price ($)", 0, 5000000, 40000, step=1000)
    sub_price = st.number_input("Subscription price ($ / yr)", 0, 1000000, 12000, step=500)
    ppu_price = st.number_input("Pay-per-use revenue ($ / customer / yr)", 0, 1000000, 9000, step=500)
    st.header("Hybrid")
    hyb_upfront = st.number_input("Hybrid upfront ($)", 0, 5000000, 10000, step=500)
    hyb_price = st.number_input("Hybrid recurring ($ / yr)", 0, 1000000, 7000, step=500)
    st.header("Economics")
    retention = st.slider("Annual retention (%)", 50, 99, 88)
    gross_margin = st.slider("Gross margin (%)", 10, 95, 65)
    years = st.slider("Time horizon (years)", 3, 7, 5)

out = simulate(new_y1, growth, capital_price, sub_price, ppu_price,
               hyb_upfront, hyb_price, retention, gross_margin, years)
rec, scored = recommend(out, gross_margin)
rec_d = out[rec]

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{rec}</div><div class="l">Recommended model</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${rec_d["cum_rev"]/1e6:,.1f}M</div><div class="l">{years}-yr cumulative revenue</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${rec_d["ltv"]:,.0f}</div><div class="l">Customer LTV</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{retention}%</div><div class="l">Assumed retention</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📈 Revenue ramp", "💎 LTV & cumulative", "📋 Executive summary"])

COLORS = {"Capital / one-time": "#8B6CFF", "Subscription": "#22D3EE",
          "Pay-per-use": "#EC4899", "Hybrid": "#F5A623"}

with t1:
    st.markdown("#### Annual revenue by model")
    fig = go.Figure()
    for m in MODELS:
        rows = out[m]["rows"]
        fig.add_trace(go.Scatter(x=[r["Year"] for r in rows], y=[r["Revenue ($)"] for r in rows],
                                 mode="lines+markers", name=m, line=dict(color=COLORS[m], width=3)))
    fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Revenue ($)",
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div style="color:#aab4d6;font-size:.85rem">Recurring models (subscription, pay-per-use, hybrid) '
          f'compound an installed base retained at {retention}%/yr; the capital model re-wins every customer '
          f'each year. Horizon: {years} years.</div>')

with t2:
    st.markdown("#### Lifetime value & cumulative revenue")
    cL, cR = st.columns(2)
    with cL:
        fig = go.Figure(go.Bar(x=MODELS, y=[out[m]["ltv"] for m in MODELS],
                               marker_color=[COLORS[m] for m in MODELS],
                               text=[f"${out[m]['ltv']:,.0f}" for m in MODELS], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=300, title="Customer LTV",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        fig = go.Figure(go.Bar(x=MODELS, y=[out[m]["cum_rev"] for m in MODELS],
                               marker_color=[COLORS[m] for m in MODELS],
                               text=[f"${out[m]['cum_rev']/1e6:,.1f}M" for m in MODELS], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=300, title=f"{years}-yr cumulative revenue",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pd.DataFrame(rec_d["rows"]), use_container_width=True, hide_index=True)
    st.caption(f"Table shows the recommended model: {rec}.")

with t3:
    st.markdown("#### Board-ready read")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{bm_summary(out, rec, gross_margin, years)}</div>')
    comp = pd.DataFrame([{"Model": m, "Cumulative revenue ($)": round(out[m]["cum_rev"]),
                          "Customer LTV ($)": round(out[m]["ltv"]),
                          "Recurring": out[m]["recurring"]} for m in MODELS])
    st.download_button("⬇ Download model comparison (CSV)", comp.to_csv(index=False),
                       file_name="business_model_comparison.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for commercial-model framing. Directional estimates, not a forecast. "
           f"For a tailored engagement: {PROFILE['email']}.")
