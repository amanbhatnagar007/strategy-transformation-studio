import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.gtm_data import MARKETS, ROUTES
from lib.gtm_logic import score_routes, prioritize_markets, business_case, exec_summary

st.set_page_config(page_title="GTM Strategy Builder", page_icon="🚀", layout="wide")
page_header("🚀 GTM & Route-to-Market Strategy Builder",
            "A CXO-grade decision tool: recommends your go-to-market route, prioritizes target countries by "
            "sector, and builds a 5-year ROI business case — all from a few inputs.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

# ===================== INPUTS =====================
with st.sidebar:
    st.header("1 · Product & market")
    product = st.text_input("Product / offering", "Next-gen CGM sensor")
    sector = st.selectbox("Sector", list(MARKETS.keys()))
    ptype = st.selectbox("Product type", ["Capital equipment", "Disposable / consumable",
                                          "Software / SaMD", "Drug / therapy", "Service"])
    model = st.selectbox("Commercial model", ["Capital / one-time", "Subscription",
                                              "Pay-per-use", "Hybrid"])
    st.header("2 · Commercial profile")
    asp = st.number_input("Avg. selling price / unit ($)", 10, 5_000_000, 1500, step=50)
    complexity = st.slider("Clinical / sales complexity (1–10)", 1, 10, 7)
    fragmentation = st.slider("Buyer fragmentation (1–10)", 1, 10, 6)
    digital = st.slider("Buyer digital maturity (1–10)", 1, 10, 6)
    presence = st.slider("Your local presence / brand (1–10)", 1, 10, 4)
    st.header("3 · Business case")
    invest = st.number_input("Upfront investment ($M)", 1, 2000, 40, step=5)
    units_y1 = st.number_input("Year-1 unit volume", 100, 5_000_000, 45000, step=500)
    vol_cagr = st.slider("Volume CAGR (%)", 0, 80, 25)
    gross_margin = st.slider("Gross margin (%)", 10, 90, 62)

# ===================== COMPUTE =====================
routes = score_routes(asp, complexity, digital, fragmentation, presence, model, units_y1)
top_route = routes[0][0]
markets = prioritize_markets(MARKETS[sector])
top_market_names = [m["country"] for m in markets[:3]]

# ===================== HEADLINE =====================
bc_top = business_case(invest, asp, units_y1, vol_cagr, gross_margin, top_route)
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v" style="font-size:1.15rem">{top_route}</div><div class="l">Recommended route</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{bc_top["roi"]}%</div><div class="l">5-yr ROI</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${bc_top["npv"]:,.0f}M</div><div class="l">NPV @12%</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{bc_top["payback"]}</div><div class="l">Payback</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🧭 Route-to-Market", "🌍 Market Prioritization",
                                  "💰 ROI Business Case", "📋 Executive Summary"])

# ---------- TAB 1: RTM ----------
with tab1:
    st.markdown("#### Recommended route-to-market (direct vs indirect vs hybrid)")
    st.caption("Scored on ASP, clinical complexity, buyer fragmentation, digital maturity, local presence and commercial model.")
    cL, cR = st.columns([1.1, 1])
    with cL:
        names = [r[0] for r in routes]
        vals = [r[1] for r in routes]
        colors = ["#22D3EE" if n == top_route else "#5B4B9E" for n in names]
        fig = go.Figure(go.Bar(x=vals, y=names, orientation="h", marker_color=colors,
                               text=[f"{v}" for v in vals], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=30, t=10, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_title="Fit score (0–100)", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        for i, (name, score, why) in enumerate(routes[:3]):
            tag = "★ Recommended" if i == 0 else f"#{i+1}"
            glass(f'<div style="display:flex;justify-content:space-between"><span style="font-weight:600;color:#fff">{name}</span>'
                  f'<span style="color:#22D3EE;font-size:.8rem">{tag} · {score}</span></div>'
                  f'<div style="color:#aab4d6;font-size:.82rem;margin-top:.25rem">{ROUTES[name]}</div>'
                  f'<div style="color:#c4b5ff;font-size:.78rem;margin-top:.35rem">Why here: {why}.</div>')

# ---------- TAB 2: MARKETS ----------
with tab2:
    st.markdown(f"#### Target-market prioritization — {sector}")
    st.caption("Bubble = market. X: ease of entry · Y: attractiveness · size: growth. Top-right enters first.")
    dfm = pd.DataFrame(markets)
    fig = px.scatter(dfm, x="ease", y="attract", size="growth", color="tier", text="country",
                     color_discrete_map={"Tier 1 — Now": "#22D3EE", "Tier 2 — Next": "#8B6CFF",
                                         "Tier 3 — Later": "#6B7393"},
                     size_max=42, height=430)
    fig.update_traces(textposition="top center", textfont=dict(size=10, color="#cdd6f5"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Ease of entry →", yaxis_title="Market attractiveness →",
                      legend_title="", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Entry sequence")
    show = dfm[["country", "region", "tier", "wave", "attract", "ease", "growth"]].rename(
        columns={"attract": "Attractiveness", "ease": "Ease", "growth": "Growth %"})
    st.dataframe(show, use_container_width=True, hide_index=True)

# ---------- TAB 3: ROI ----------
with tab3:
    st.markdown("#### 5-year business case — and direct vs indirect economics")
    st.caption("Adjust inputs in the sidebar. Indirect routes trade margin (distributor take) for lower fixed cost.")
    compare = st.multiselect("Compare routes", list(ROUTES.keys()),
                             default=[top_route, "Distributor / indirect"])
    cases = {r: business_case(invest, asp, units_y1, vol_cagr, gross_margin, r) for r in compare}

    cc = st.columns(len(cases)) if cases else [st]
    for col, (r, bc) in zip(cc, cases.items()):
        with col:
            glass(f'<div style="font-weight:600;color:#fff">{r}</div>'
                  f'<div style="color:#aab4d6;font-size:.8rem;margin:.3rem 0">ROI <b style="color:#22D3EE">{bc["roi"]}%</b> · '
                  f'NPV <b style="color:#22D3EE">${bc["npv"]}M</b> · payback {bc["payback"]}</div>'
                  f'<div style="color:#9AA6CC;font-size:.76rem">distributor take {bc["distributor_take"]}% · opex {bc["opex_pct"]}% of rev</div>')

    fig = go.Figure()
    palette = ["#22D3EE", "#8B6CFF", "#EC4899", "#F59E0B", "#34D399"]
    for (r, bc), color in zip(cases.items(), palette):
        df = pd.DataFrame(bc["rows"])
        fig.add_trace(go.Scatter(x=df["Year"], y=df["Cumulative cash ($M)"], mode="lines+markers",
                                 name=r, line=dict(width=3, color=color)))
    fig.add_hline(y=0, line_dash="dot", line_color="#888")
    fig.update_layout(template="plotly_dark", height=330, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Cumulative cash ($M)",
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("See full P&L for the recommended route"):
        st.dataframe(pd.DataFrame(business_case(invest, asp, units_y1, vol_cagr, gross_margin, top_route)["rows"]),
                     use_container_width=True, hide_index=True)

# ---------- TAB 4: SUMMARY ----------
with tab4:
    st.markdown("#### Board-ready executive summary")
    summary = exec_summary(product, sector, top_route, top_market_names, bc_top)
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{summary}</div>')
    c1, c2 = st.columns(2)
    with c1:
        glass('<div style="font-weight:600;color:#fff">Strategic options to weigh</div>'
              '<div class="bullet">Build vs. partner for Wave-1 entry speed</div>'
              '<div class="bullet">Own salesforce vs. distributor margin trade-off</div>'
              '<div class="bullet">Land-and-expand in Tier-1 before Tier-2 spend</div>'
              '<div class="bullet">Pricing model alignment to buyer economics</div>')
    with c2:
        glass('<div style="font-weight:600;color:#fff">Key risks to de-risk</div>'
              '<div class="bullet">Reimbursement / regulatory timing by market</div>'
              '<div class="bullet">Channel conflict in hybrid models</div>'
              '<div class="bullet">Ramp assumptions vs. real adoption curve</div>'
              '<div class="bullet">Competitive response & price erosion</div>')
    df = pd.DataFrame(bc_top["rows"])
    st.download_button("⬇ Download business case (CSV)", df.to_csv(index=False),
                       file_name="gtm_business_case.csv", mime="text/csv")

st.caption("AI-assisted heuristic model grounded in commercial-strategy & route-to-market frameworks. "
           f"Indices are directional planning inputs, not live market data. For a tailored engagement: {PROFILE['email']}.")
