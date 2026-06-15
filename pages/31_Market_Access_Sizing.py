import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE

st.set_page_config(page_title="Market Access & Sizing", page_icon="📏", layout="wide")
page_header("📏 Market Access & Sizing",
            "Size the opportunity top-down (TAM / SAM / SOM) and forecast the revenue ramp under "
            "low / base / high adoption — with every assumption explicit.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

P = st.session_state.setdefault("mas_params", {
    "population": 38_000_000, "prevalence": 11.0, "diagnosis": 70.0, "treatment": 45.0,
    "price": 1200, "share": 8.0, "years": 5, "peak_year": 4,
})


def size_market(p):
    tam = p["population"] * p["prevalence"] / 100 * p["price"]
    sam = tam * p["diagnosis"] / 100 * p["treatment"] / 100
    som = sam * p["share"] / 100
    return tam, sam, som


def forecast(som, years, peak_year, share_mult=1.0):
    # S-curve ramp to peak share by peak_year, then flat
    ys = []
    for y in range(1, years + 1):
        f = 1 / (1 + np.exp(-( (y - peak_year/2) ) * (4/peak_year)))
        ys.append(round(som * share_mult * f))
    return ys


STAGES = ["① Market Sizing", "② Forecast & Scenario", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="mas_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

tam, sam, som = size_market(P)

if stage == STAGES[0]:
    P["population"] = st.sidebar.number_input("Target population", 10_000, 2_000_000_000, P["population"], step=100_000)
    P["prevalence"] = st.sidebar.slider("Prevalence (%)", 0.1, 60.0, P["prevalence"], 0.1)
    P["diagnosis"] = st.sidebar.slider("Diagnosed (%)", 1.0, 100.0, P["diagnosis"], 1.0)
    P["treatment"] = st.sidebar.slider("Treated / addressable (%)", 1.0, 100.0, P["treatment"], 1.0)
    P["price"] = st.sidebar.number_input("Annual price / patient ($)", 1, 1_000_000, P["price"], step=50)
    P["share"] = st.sidebar.slider("Achievable share (%)", 0.1, 60.0, P["share"], 0.1)
elif stage == STAGES[1]:
    P["years"] = st.sidebar.slider("Forecast horizon (years)", 3, 10, P["years"])
    P["peak_year"] = st.sidebar.slider("Year to reach peak share", 2, P["years"], min(P["peak_year"], P["years"]))
    locked_panel([("SOM (peak)", f"${som/1e6:,.0f}M"), ("Share", f"{P['share']}%")])
else:
    locked_panel([("TAM", f"${tam/1e6:,.0f}M"), ("SAM", f"${sam/1e6:,.0f}M"), ("SOM", f"${som/1e6:,.0f}M")])

tam, sam, som = size_market(P)

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${tam/1e6:,.0f}M</div><div class="l">TAM</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${sam/1e6:,.0f}M</div><div class="l">SAM</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${som/1e6:,.0f}M</div><div class="l">SOM (peak)</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    fig = go.Figure(go.Funnel(y=["TAM", "SAM", "SOM"], x=[tam, sam, som],
                              marker={"color": ["#8B6CFF", "#6C7BE0", "#22D3EE"]},
                              textinfo="value+percent initial"))
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="funnel")
    glass(f'<div style="color:#dfe5fb">TAM = population × prevalence × price. SAM applies diagnosis ({P["diagnosis"]:.0f}%) '
          f'and treatment ({P["treatment"]:.0f}%). SOM applies achievable share ({P["share"]:.1f}%).</div>')

elif stage == STAGES[1]:
    yrs = [f"Y{i+1}" for i in range(P["years"])]
    base = forecast(som, P["years"], P["peak_year"], 1.0)
    low = forecast(som, P["years"], P["peak_year"], 0.6)
    high = forecast(som, P["years"], P["peak_year"], 1.4)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yrs, y=high, name="High", line=dict(color="#34D399", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=yrs, y=base, name="Base", line=dict(color="#22D3EE", width=3), fill="tonexty"))
    fig.add_trace(go.Scatter(x=yrs, y=low, name="Low", line=dict(color="#EC4899", width=2, dash="dot"), fill="tonexty"))
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="Revenue ($)", margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True, key="fc")
    dff = pd.DataFrame({"Year": yrs, "Low ($M)": [round(x/1e6, 1) for x in low],
                        "Base ($M)": [round(x/1e6, 1) for x in base], "High ($M)": [round(x/1e6, 1) for x in high]})
    st.dataframe(dff, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download forecast (CSV)", dff.to_csv(index=False), file_name="market_forecast.csv", mime="text/csv")

else:
    base = forecast(som, P["years"], P["peak_year"], 1.0)
    glass(f'<div style="font-size:.97rem;line-height:1.7;color:#dfe5fb">The total addressable market is '
          f'<b>${tam/1e6:,.0f}M</b>; after diagnosis and treatment filters the serviceable market is '
          f'<b>${sam/1e6:,.0f}M</b>, and at a <b>{P["share"]:.1f}%</b> achievable share the obtainable market is '
          f'<b>${som/1e6:,.0f}M</b>. On a base adoption curve reaching peak share by Y{P["peak_year"]}, revenue ramps '
          f'to <b>${base[-1]/1e6:,.0f}M</b> by Y{P["years"]} (range ${forecast(som,P["years"],P["peak_year"],0.6)[-1]/1e6:,.0f}M–'
          f'${forecast(som,P["years"],P["peak_year"],1.4)[-1]/1e6:,.0f}M low–high). Validate prevalence, diagnosis and '
          'share assumptions against epidemiology and competitive intensity before planning capacity.</div>')

st.caption("AI-assisted heuristic market-sizing model. Directional — pressure-test every assumption. "
           f"For a tailored sizing & access engagement: {PROFILE['email']}.")
