import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.pricing_logic import price_corridor, demand_curve, estimate_at, entry_mode, pricing_summary
from lib.bizmodel_logic import simulate, recommend, bm_summary, MODELS

st.set_page_config(page_title="Pricing & Business Model Lab", page_icon="🏷️", layout="wide")
page_header("🏷️ Pricing & Business Model Lab",
            "Find the viable price corridor and entry mode, then compare commercial models — capital vs "
            "subscription vs pay-per-use vs hybrid — on revenue and lifetime value.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

P = st.session_state.setdefault("pml_params", {
    "unit_cost": 400, "target_margin": 60, "competitor_price": 1200, "value_to_customer": 1800,
    "elasticity": -1.4, "base_volume": 10000, "presence": 4,
    "new_customers_y1": 5000, "growth": 20, "capital_price": 1500, "sub_price_yr": 600,
    "ppu_price_yr": 500, "hybrid_upfront": 400, "hybrid_price_yr": 350, "retention": 85, "gross_margin": 62,
})

STAGES = ["① Pricing Corridor", "② Business Model Simulator", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="pml_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

corr = price_corridor(P["unit_cost"], P["target_margin"], P["competitor_price"], P["value_to_customer"])
est = estimate_at(corr["recommended"], P["unit_cost"], P["competitor_price"], P["elasticity"], P["base_volume"])
mode, why = entry_mode(P["presence"], est["margin"], P["value_to_customer"], P["competitor_price"])
out = simulate(P["new_customers_y1"], P["growth"], P["capital_price"], P["sub_price_yr"], P["ppu_price_yr"],
               P["hybrid_upfront"], P["hybrid_price_yr"], P["retention"], P["gross_margin"])
rec_model, scored = recommend(out, P["gross_margin"])

if stage == STAGES[0]:
    P["unit_cost"] = st.sidebar.number_input("Unit cost ($)", 1, 1_000_000, P["unit_cost"], step=10)
    P["target_margin"] = st.sidebar.slider("Target margin (%)", 10, 90, P["target_margin"])
    P["competitor_price"] = st.sidebar.number_input("Competitor price ($)", 1, 1_000_000, P["competitor_price"], step=10)
    P["value_to_customer"] = st.sidebar.number_input("Value to customer ($)", 1, 5_000_000, P["value_to_customer"], step=10)
    P["elasticity"] = st.sidebar.slider("Demand elasticity", -3.0, -0.2, P["elasticity"], 0.1)
    P["base_volume"] = st.sidebar.number_input("Base volume @ competitor price", 100, 10_000_000, P["base_volume"], step=100)
    P["presence"] = st.sidebar.slider("Local presence (entry mode)", 0, 10, P["presence"])
elif stage == STAGES[1]:
    P["new_customers_y1"] = st.sidebar.number_input("New customers Y1", 100, 5_000_000, P["new_customers_y1"], step=100)
    P["growth"] = st.sidebar.slider("Customer growth (%/yr)", 0, 60, P["growth"])
    P["capital_price"] = st.sidebar.number_input("Capital price ($)", 1, 5_000_000, P["capital_price"], step=10)
    P["sub_price_yr"] = st.sidebar.number_input("Subscription $/yr", 1, 1_000_000, P["sub_price_yr"], step=10)
    P["ppu_price_yr"] = st.sidebar.number_input("Pay-per-use $/yr", 1, 1_000_000, P["ppu_price_yr"], step=10)
    P["hybrid_upfront"] = st.sidebar.number_input("Hybrid upfront ($)", 0, 1_000_000, P["hybrid_upfront"], step=10)
    P["hybrid_price_yr"] = st.sidebar.number_input("Hybrid $/yr", 0, 1_000_000, P["hybrid_price_yr"], step=10)
    P["retention"] = st.sidebar.slider("Annual retention (%)", 50, 99, P["retention"])
    P["gross_margin"] = st.sidebar.slider("Gross margin (%)", 10, 90, P["gross_margin"])
    locked_panel([("Recommended price", f"${corr['recommended']:,.0f}"), ("Entry mode", mode)])
else:
    locked_panel([("Rec. price", f"${corr['recommended']:,.0f}"), ("Entry mode", mode), ("Rec. model", rec_model)])

# recompute
corr = price_corridor(P["unit_cost"], P["target_margin"], P["competitor_price"], P["value_to_customer"])
est = estimate_at(corr["recommended"], P["unit_cost"], P["competitor_price"], P["elasticity"], P["base_volume"])
mode, why = entry_mode(P["presence"], est["margin"], P["value_to_customer"], P["competitor_price"])
out = simulate(P["new_customers_y1"], P["growth"], P["capital_price"], P["sub_price_yr"], P["ppu_price_yr"],
               P["hybrid_upfront"], P["hybrid_price_yr"], P["retention"], P["gross_margin"])
rec_model, scored = recommend(out, P["gross_margin"])

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${corr["recommended"]:,.0f}</div><div class="l">Rec. price</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{est["margin"]:.0f}%</div><div class="l">Unit margin</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v" style="font-size:1.0rem">{mode}</div><div class="l">Entry mode</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v" style="font-size:1.0rem">{rec_model}</div><div class="l">Rec. model</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    prices, vols, revenue, profit = demand_curve(corr, P["unit_cost"], P["competitor_price"], P["elasticity"], P["base_volume"])
    cL, cR = st.columns(2)
    with cL:
        for lbl, key, col in [("Floor (cost-plus)", "floor", "#EC4899"), ("Reference (competitor)", "reference", "#8B6CFF"),
                              ("Recommended", "recommended", "#22D3EE"), ("Ceiling (value)", "ceiling", "#34D399")]:
            glass(f'<div style="display:flex;justify-content:space-between"><span style="color:#cdd6f5">{lbl}</span>'
                  f'<span style="color:{col};font-weight:600">${corr[key]:,.2f}</span></div>')
    with cR:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices, y=revenue, name="Revenue", line=dict(color="#22D3EE", width=3)))
        fig.add_trace(go.Scatter(x=prices, y=profit, name="Profit", line=dict(color="#8B6CFF", width=3)))
        fig.add_vline(x=corr["recommended"], line_dash="dot", line_color="#fff")
        fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_title="Price ($)", yaxis_title="$", margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig, use_container_width=True, key="demand")
    glass(f'<div style="color:#dfe5fb"><b>Entry mode: {mode}.</b> {why}.</div>')

elif stage == STAGES[1]:
    fig = go.Figure()
    palette = {"Capital / one-time": "#EC4899", "Subscription": "#22D3EE", "Pay-per-use": "#8B6CFF", "Hybrid": "#34D399"}
    for m in MODELS:
        df = pd.DataFrame(out[m]["rows"])
        fig.add_trace(go.Scatter(x=df["Year"], y=df["Cumulative ($)"], name=m, line=dict(width=3, color=palette[m])))
    fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="Cumulative revenue ($)", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, use_container_width=True, key="bm")
    comp = pd.DataFrame([{"Model": m, "5-yr revenue ($)": round(out[m]["cum_rev"]),
                          "Customer LTV ($)": round(out[m]["ltv"]), "Recommended": "★" if m == rec_model else ""}
                         for m in MODELS]).sort_values("5-yr revenue ($)", ascending=False)
    st.dataframe(comp, use_container_width=True, hide_index=True)

else:
    glass(f'<div style="font-size:.97rem;line-height:1.7;color:#dfe5fb">{pricing_summary(corr, est, mode, why, P["target_margin"])}</div>')
    glass(f'<div style="font-size:.97rem;line-height:1.7;color:#dfe5fb;margin-top:.6rem">{bm_summary(out, rec_model, P["gross_margin"])}</div>')

st.caption("AI-assisted heuristic pricing & business-model models. Directional — validate value-to-customer, "
           f"elasticity and retention with primary research. For a tailored engagement: {PROFILE['email']}.")
