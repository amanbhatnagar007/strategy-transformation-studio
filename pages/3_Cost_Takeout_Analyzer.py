import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.cost_logic import cost_savings, cost_summary

st.set_page_config(page_title="Cost Takeout Analyzer", page_icon="🛠️", layout="wide")
page_header("🛠️ Cost Takeout & Org Redesign Analyzer",
            "Quantify a cost-transformation: savings by lever, the org de-layering opportunity, and a "
            "phased EBITDA bridge — the approach behind ~$150M of identified cost improvement on a Fortune-500 client.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Cost base")
    cost_base = st.number_input("Total addressable cost base ($M)", 10, 100000, 900, step=10)
    headcount = st.number_input("Headcount (FTEs)", 50, 500000, 6000, step=50)
    avg_cost = st.number_input("Avg. fully-loaded cost ($k / FTE)", 20, 500, 95, step=5)
    footprint_cost = st.number_input("Facilities / footprint cost ($M)", 0, 20000, 80, step=5)
    procurement_addr = st.number_input("Addressable 3rd-party spend ($M)", 0, 50000, 300, step=10)
    st.header("Org structure")
    layers = st.slider("Management layers (CEO → front line)", 4, 14, 9)
    target_span = st.slider("Target span of control", 4, 12, 7)
    automation_ready = st.slider("Process automation readiness", 0.0, 1.0, 0.5, 0.05)

c = cost_savings(cost_base, headcount, avg_cost, layers, target_span,
                 procurement_addr, automation_ready, footprint_cost)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${c["total"]:,.0f}M</div><div class="l">Cost takeout</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{c["pct"]}%</div><div class="l">of cost base</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{c["org"]["current_span"]}</div><div class="l">Current avg span</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">~{c["mgr_reduction"]:,}</div><div class="l">Mgmt roles removed</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🧱 Savings bridge", "🪜 Org & spans", "📋 Executive summary"])

with t1:
    st.markdown("#### Savings by lever (waterfall to EBITDA)")
    lv = c["levers"]
    measures = ["relative"] * len(lv) + ["total"]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=measures,
        x=list(lv.keys()) + ["Total takeout"],
        y=list(lv.values()) + [c["total"]],
        text=[f"${v}M" for v in lv.values()] + [f"${c['total']}M"],
        connector={"line": {"color": "rgba(255,255,255,.2)"}},
        increasing={"marker": {"color": "#22D3EE"}},
        totals={"marker": {"color": "#8B6CFF"}}))
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Savings ($M)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.markdown("#### Organization de-layering opportunity")
    cL, cR = st.columns(2)
    with cL:
        glass(f'<div style="font-weight:600;color:#fff">Current state</div>'
              f'<div class="bullet">{layers} management layers</div>'
              f'<div class="bullet">Avg span of control: {c["org"]["current_span"]}</div>'
              f'<div class="bullet">~{c["org"]["managers"]:,} managers</div>'
              f'<div class="bullet">{c["org"]["excess_layers"]} layers above best-practice (≤6)</div>')
    with cR:
        glass(f'<div style="font-weight:600;color:#fff">Target state</div>'
              f'<div class="bullet">Span of control: {target_span}</div>'
              f'<div class="bullet">~{c["target_managers"]:,} managers</div>'
              f'<div class="bullet">~{c["mgr_reduction"]:,} management roles removed</div>'
              f'<div class="bullet">Flatter, faster decision-making</div>')
    st.markdown("#### Phasing")
    st.dataframe(pd.DataFrame(c["rows"]), use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{cost_summary(c, cost_base)}</div>')
    df = pd.DataFrame([{"Lever": k, "Savings ($M)": v} for k, v in c["levers"].items()])
    st.download_button("⬇ Download savings by lever (CSV)", df.to_csv(index=False),
                       file_name="cost_takeout.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for cost-transformation framing. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
