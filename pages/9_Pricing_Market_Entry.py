import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.pricing_logic import (price_corridor, demand_curve, estimate_at,
                               entry_mode, pricing_summary)

st.set_page_config(page_title="Pricing & Market-Entry Planner", page_icon="🏷️", layout="wide")
page_header("🏷️ Pricing & Market-Entry Planner",
            "Set a defensible price corridor — cost-plus floor, value ceiling, competitor reference — and "
            "pick the right entry mode for a new market, with elasticity-based volume and revenue.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Cost & margin")
    unit_cost = st.number_input("Unit cost ($)", 1, 1000000, 600, step=10)
    target_margin = st.slider("Target margin (%)", 5, 90, 45)
    st.header("Market references")
    competitor_price = st.number_input("Competitor price ($)", 1, 2000000, 1200, step=10)
    value_to_customer = st.number_input("Estimated value to customer ($)", 1, 2000000, 1800, step=10)
    st.header("Demand & presence")
    elasticity = st.slider("Demand elasticity", -4.0, -0.2, -1.4, 0.1)
    base_volume = st.number_input("Base annual volume @ competitor price (units)", 100, 10000000, 20000, step=100)
    presence = st.slider("Local presence / infrastructure (0–10)", 0, 10, 3)

corr = price_corridor(unit_cost, target_margin, competitor_price, value_to_customer)
est = estimate_at(corr["recommended"], unit_cost, competitor_price, elasticity, base_volume)
mode, why = entry_mode(presence, est["margin"], value_to_customer, competitor_price)

warn = corr["floor"] > corr["ceiling"]

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${corr["recommended"]:,.0f}</div><div class="l">Recommended price</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{est["margin"]}%</div><div class="l">Unit margin</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${est["revenue"]/1e6:,.1f}M</div><div class="l">Est. annual revenue</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{mode.split(" /")[0]}</div><div class="l">Entry mode</div></div>', unsafe_allow_html=True)

if warn:
    st.warning("Cost-plus floor exceeds the value ceiling — the target margin isn't supportable at this "
               "value-to-customer. Lower cost, reduce target margin, or revisit the value estimate.")

t1, t2, t3 = st.tabs(["🎚️ Price corridor", "📈 Revenue vs price", "📋 Executive summary"])

with t1:
    st.markdown("#### Price corridor")
    labels = ["Cost-plus floor", "Recommended", "Competitor reference", "Value ceiling"]
    vals = [corr["floor"], corr["recommended"], corr["reference"], corr["ceiling"]]
    colors = ["#F5A623", "#8B6CFF", "#22D3EE", "#EC4899"]
    fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h", marker_color=colors,
                           text=[f"${v:,.0f}" for v in vals], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Price ($)",
                      margin=dict(l=10, r=40, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div class="bullet">Floor protects the {target_margin}% target margin at ${unit_cost:,.0f} cost</div>'
          f'<div class="bullet">Ceiling = estimated value to customer (${value_to_customer:,.0f})</div>'
          f'<div class="bullet">Recommended price anchors on the competitor, nudged toward value</div>')

with t2:
    st.markdown("#### Revenue & profit vs price (elasticity-based)")
    prices, vols, revenue, profit = demand_curve(corr, unit_cost, competitor_price, elasticity, base_volume)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=revenue, mode="lines", name="Revenue",
                             line=dict(color="#22D3EE", width=3)))
    fig.add_trace(go.Scatter(x=prices, y=profit, mode="lines", name="Profit",
                             line=dict(color="#8B6CFF", width=3)))
    fig.add_vline(x=corr["recommended"], line_dash="dot", line_color="rgba(255,255,255,.4)",
                  annotation_text="Recommended", annotation_position="top")
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Price ($)", yaxis_title="$",
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div style="color:#aab4d6;font-size:.85rem">At elasticity {elasticity:.1f}, the recommended price '
          f'yields ~{est["volume"]:,.0f} units → ${est["revenue"]:,.0f} revenue, ${est["profit"]:,.0f} gross '
          f'profit. Elasticity is the most sensitive assumption here.</div>')

with t3:
    st.markdown("#### Board-ready read")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">'
          f'{pricing_summary(corr, est, mode, why, target_margin)}</div>')
    out = pd.DataFrame([
        {"Metric": "Cost-plus floor ($)", "Value": corr["floor"]},
        {"Metric": "Value ceiling ($)", "Value": corr["ceiling"]},
        {"Metric": "Competitor reference ($)", "Value": corr["reference"]},
        {"Metric": "Recommended price ($)", "Value": corr["recommended"]},
        {"Metric": "Est. volume (units)", "Value": round(est["volume"])},
        {"Metric": "Est. revenue ($)", "Value": round(est["revenue"])},
        {"Metric": "Unit margin (%)", "Value": est["margin"]},
        {"Metric": "Entry mode", "Value": mode},
    ])
    st.download_button("⬇ Download pricing & entry plan (CSV)", out.to_csv(index=False),
                       file_name="pricing_market_entry.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for pricing & market-entry framing. Directional; elasticity and value "
           f"estimates should be validated with research. For a tailored engagement: {PROFILE['email']}.")
