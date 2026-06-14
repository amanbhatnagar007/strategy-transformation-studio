import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="MedTech Market Sizer", page_icon="📏", layout="wide")
page_header("📏 MedTech Market Sizer",
            "Size TAM / SAM / SOM for a MedTech category (e.g. CGM). Walk from target population through "
            "prevalence, diagnosis, treatment penetration and achievable share to a defensible revenue opportunity.")
st.page_link("Home.py", label="← Back to Studio")

ACCENT, ACCENT2 = "#8B6CFF", "#22D3EE"

with st.sidebar:
    st.header("Population & demand")
    population = st.number_input("Target population", 10_000, 2_000_000_000, 330_000_000, step=10_000)
    prevalence = st.slider("Disease prevalence (%)", 0.1, 60.0, 11.0, 0.1)
    diagnosis = st.slider("Diagnosis rate (%)", 1.0, 100.0, 78.0, 1.0)
    treatment = st.slider("Treatment / device penetration (%)", 1.0, 100.0, 35.0, 1.0)
    st.header("Economics & ambition")
    price = st.number_input("Annual price per patient ($)", 10, 200_000, 1800, step=10)
    share = st.slider("Achievable market share (%)", 0.5, 100.0, 12.0, 0.5)

prev_pat = population * prevalence / 100
dx_pat = prev_pat * diagnosis / 100
tx_pat = dx_pat * treatment / 100
som_pat = tx_pat * share / 100

tam = prev_pat * price          # everyone with the condition, at full price
sam = tx_pat * price            # diagnosed AND treatable/penetrable
som = som_pat * price           # realistic captured share

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${tam/1e9:,.2f}B</div><div class="l">TAM</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${sam/1e9:,.2f}B</div><div class="l">SAM</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${som/1e6:,.1f}M</div><div class="l">SOM</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔻 Sizing funnel", "🎚️ Sensitivity", "📋 Executive summary"])

with t1:
    st.markdown("#### From population to obtainable revenue")
    fig = go.Figure(go.Funnel(
        y=["TAM · all prevalence", "SAM · diagnosed & treatable", "SOM · achievable share"],
        x=[tam, sam, som],
        textinfo="value+percent initial",
        marker={"color": [ACCENT, ACCENT2, "#EC4899"]},
        connector={"line": {"color": "#6b7394"}}))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    walk = pd.DataFrame({
        "Stage": ["Population", "× Prevalence", "× Diagnosis", "× Treatment penetration", "× Achievable share"],
        "Patients": [round(population), round(prev_pat), round(dx_pat), round(tx_pat), round(som_pat)],
        "Annual revenue ($)": [np.nan, round(tam), round(dx_pat * price), round(sam), round(som)],
    })
    st.dataframe(walk, use_container_width=True, hide_index=True)

with t2:
    st.markdown("#### SOM sensitivity to share % and price")
    shares = np.linspace(max(share - 10, 0.5), share + 10, 9)
    prices = np.unique(np.round(np.linspace(price * 0.6, price * 1.4, 7))).astype(int)
    z = np.outer(prices, tx_pat * shares / 100) / 1e6  # $M
    fig = go.Figure(data=go.Heatmap(
        z=z, x=[f"{s:.0f}%" for s in shares], y=[f"${p:,}" for p in prices],
        colorscale=[[0, "#0e1430"], [0.5, ACCENT], [1, ACCENT2]],
        colorbar=dict(title="SOM ($M)")))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Achievable share (%)",
                      yaxis_title="Annual price per patient ($)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">SOM scales linearly with both share and price, so the corners '
          'of this grid bracket the realistic opportunity range. Treat the base case as a point estimate inside that '
          'band — share assumptions, not price, usually carry the most execution risk.</div>')

with t3:
    st.markdown("#### Board-ready read")
    txt = (f"For a target population of <b>{population:,.0f}</b> with <b>{prevalence:.1f}%</b> prevalence, the category "
           f"TAM is <b>${tam/1e9:,.2f}B</b> ({prev_pat:,.0f} patients at ${price:,}/yr). Applying a "
           f"<b>{diagnosis:.0f}%</b> diagnosis rate and <b>{treatment:.0f}%</b> treatment/device penetration narrows "
           f"the serviceable market (SAM) to <b>${sam/1e9:,.2f}B</b> ({tx_pat:,.0f} patients). At a "
           f"<b>{share:.1f}%</b> achievable share, the obtainable opportunity (SOM) is <b>${som/1e6:,.1f}M</b> "
           f"({som_pat:,.0f} patients). "
           f"Assumptions: single annual price per patient, multiplicative funnel, and share independent of price. "
           f"Figures are directional heuristics for opportunity framing — validate prevalence, penetration and "
           f"pricing against epidemiology and payer-coverage data before committing to a plan.")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{txt}</div>')
    out = pd.DataFrame({
        "Metric": ["Population", "Prevalence %", "Diagnosis %", "Treatment penetration %", "Achievable share %",
                   "Price per patient ($)", "Prevalent patients", "Treatable patients", "Obtainable patients",
                   "TAM ($)", "SAM ($)", "SOM ($)"],
        "Value": [population, prevalence, diagnosis, treatment, share, price,
                  round(prev_pat), round(tx_pat), round(som_pat), round(tam), round(sam), round(som)],
    })
    st.download_button("⬇ Download market sizing (CSV)", out.to_csv(index=False),
                       file_name="medtech_market_sizing.csv", mime="text/csv")

st.caption("AI-assisted heuristic TAM/SAM/SOM model — directional opportunity framing, not market research. "
           f"For a tailored engagement: {PROFILE['email']}.")
