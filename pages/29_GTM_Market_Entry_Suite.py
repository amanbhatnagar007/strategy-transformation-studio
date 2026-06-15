import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.frameworks import framework_banner
from lib.gtm_data import MARKETS, ROUTES
from lib.gtm_logic import score_routes, prioritize_markets, business_case, exec_summary

st.set_page_config(page_title="GTM & Market-Entry", page_icon="🚀", layout="wide")
page_header("🚀 GTM & Market-Entry Strategy",
            "Recommend the route-to-market, prioritize target countries by sector, and build the 5-year ROI "
            "business case — the questions a CXO asks before committing to a launch.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)
framework_banner("gtm-market-entry")

P = st.session_state.setdefault("gtm_params", {
    "product": "Next-gen CGM sensor", "sector": list(MARKETS.keys())[0], "model": "Capital / one-time",
    "asp": 1500, "complexity": 7, "fragmentation": 6, "digital": 6, "presence": 4,
    "invest": 40, "units_y1": 45000, "vol_cagr": 25, "gross_margin": 62,
})

STAGES = ["① Route-to-Market", "② Market Prioritization", "③ ROI Business Case", "📋 Executive Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="gtm_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

# compute chain
routes = score_routes(P["asp"], P["complexity"], P["digital"], P["fragmentation"], P["presence"], P["model"], P["units_y1"])
top_route = routes[0][0]
markets = prioritize_markets(MARKETS[P["sector"]])
top_names = [m["country"] for m in markets[:3]]
bc = business_case(P["invest"], P["asp"], P["units_y1"], P["vol_cagr"], P["gross_margin"], top_route)

if stage == STAGES[0]:
    P["product"] = st.sidebar.text_input("Product / offering", P["product"])
    P["sector"] = st.sidebar.selectbox("Sector", list(MARKETS.keys()), index=list(MARKETS.keys()).index(P["sector"]))
    P["model"] = st.sidebar.selectbox("Commercial model", ["Capital / one-time", "Subscription", "Pay-per-use", "Hybrid"],
                                      index=["Capital / one-time", "Subscription", "Pay-per-use", "Hybrid"].index(P["model"]))
    P["asp"] = st.sidebar.number_input("Avg selling price / unit ($)", 10, 5_000_000, P["asp"], step=50)
    P["complexity"] = st.sidebar.slider("Clinical / sales complexity", 1, 10, P["complexity"])
    P["fragmentation"] = st.sidebar.slider("Buyer fragmentation", 1, 10, P["fragmentation"])
    P["digital"] = st.sidebar.slider("Buyer digital maturity", 1, 10, P["digital"])
    P["presence"] = st.sidebar.slider("Local presence / brand", 1, 10, P["presence"])
elif stage == STAGES[1]:
    st.sidebar.caption(f"Markets prioritized for **{P['sector']}** (set on step 1).")
    locked_panel([("Sector", P["sector"]), ("Recommended route", top_route)])
elif stage == STAGES[2]:
    P["invest"] = st.sidebar.number_input("Upfront investment ($M)", 1, 2000, P["invest"], step=5)
    P["units_y1"] = st.sidebar.number_input("Year-1 unit volume", 100, 5_000_000, P["units_y1"], step=500)
    P["vol_cagr"] = st.sidebar.slider("Volume CAGR (%)", 0, 80, P["vol_cagr"])
    P["gross_margin"] = st.sidebar.slider("Gross margin (%)", 10, 90, P["gross_margin"])
    locked_panel([("Route", top_route), ("Top markets", ", ".join(top_names))])
else:
    locked_panel([("Product", P["product"]), ("Sector", P["sector"]), ("Route", top_route),
                  ("5-yr ROI", f"{bc['roi']}%")])

# recompute after edits
routes = score_routes(P["asp"], P["complexity"], P["digital"], P["fragmentation"], P["presence"], P["model"], P["units_y1"])
top_route = routes[0][0]
markets = prioritize_markets(MARKETS[P["sector"]])
top_names = [m["country"] for m in markets[:3]]
bc = business_case(P["invest"], P["asp"], P["units_y1"], P["vol_cagr"], P["gross_margin"], top_route)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v" style="font-size:1.1rem">{top_route}</div><div class="l">Recommended route</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{bc["roi"]}%</div><div class="l">5-yr ROI</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${bc["npv"]:,.0f}M</div><div class="l">NPV @12%</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{bc["payback"]}</div><div class="l">Payback</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    cL, cR = st.columns([1.1, 1])
    with cL:
        names = [r[0] for r in routes]
        vals = [r[1] for r in routes]
        colors = ["#22D3EE" if n == top_route else "#5B4B9E" for n in names]
        fig = go.Figure(go.Bar(x=vals, y=names, orientation="h", marker_color=colors,
                               text=vals, textposition="outside"))
        fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Fit score", yaxis=dict(autorange="reversed"),
                          margin=dict(l=10, r=30, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, key="routes")
    with cR:
        for i, (name, score, why) in enumerate(routes[:3]):
            tag = "★ Recommended" if i == 0 else f"#{i+1}"
            glass(f'<div style="display:flex;justify-content:space-between"><span style="font-weight:600;color:#fff">{name}</span>'
                  f'<span style="color:#22D3EE;font-size:.8rem">{tag} · {score}</span></div>'
                  f'<div style="color:#aab4d6;font-size:.8rem;margin-top:.25rem">{ROUTES[name]}</div>')

elif stage == STAGES[1]:
    st.caption("Bubble = market. X: ease of entry · Y: attractiveness · size: growth. Top-right enters first.")
    dfm = pd.DataFrame(markets)
    fig = px.scatter(dfm, x="ease", y="attract", size="growth", color="tier", text="country",
                     color_discrete_map={"Tier 1 — Now": "#22D3EE", "Tier 2 — Next": "#8B6CFF", "Tier 3 — Later": "#6B7393"},
                     size_max=42, height=430)
    fig.update_traces(textposition="top center", textfont=dict(size=10, color="#cdd6f5"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Ease of entry →", yaxis_title="Attractiveness →", legend_title="",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="markets")
    st.dataframe(dfm[["country", "region", "tier", "wave", "attract", "ease", "growth"]],
                 use_container_width=True, hide_index=True)

elif stage == STAGES[2]:
    st.caption("5-year business case for the recommended route — and a direct-vs-indirect comparison.")
    compare = st.multiselect("Compare routes", list(ROUTES.keys()), default=[top_route, "Distributor / indirect"])
    cases = {r: business_case(P["invest"], P["asp"], P["units_y1"], P["vol_cagr"], P["gross_margin"], r) for r in compare}
    fig = go.Figure()
    palette = ["#22D3EE", "#8B6CFF", "#EC4899", "#F59E0B", "#34D399"]
    for (r, b), color in zip(cases.items(), palette):
        df = pd.DataFrame(b["rows"])
        fig.add_trace(go.Scatter(x=df["Year"], y=df["Cumulative cash ($M)"], mode="lines+markers", name=r,
                                 line=dict(width=3, color=color)))
    fig.add_hline(y=0, line_dash="dot", line_color="#888")
    fig.update_layout(template="plotly_dark", height=330, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="Cumulative cash ($M)", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True, key="roi")
    st.dataframe(pd.DataFrame(bc["rows"]), use_container_width=True, hide_index=True)

else:
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{exec_summary(P["product"], P["sector"], top_route, top_names, bc)}</div>')
    st.download_button("⬇ Download business case (CSV)", pd.DataFrame(bc["rows"]).to_csv(index=False),
                       file_name="gtm_business_case.csv", mime="text/csv")

st.caption("AI-assisted heuristic GTM model (route scoring · market prioritization · 5-yr business case). "
           f"Directional, not investment advice. For a tailored engagement: {PROFILE['email']}.")
