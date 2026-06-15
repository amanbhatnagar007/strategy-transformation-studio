import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.frameworks import framework_banner
from lib.synergy_logic import estimate_synergies, synergy_summary
from lib.uploads import ColumnSchema, Col, data_input
from lib.ma_suite import planned_increments, track, CURVES

st.set_page_config(page_title="Synergy & Deal Value Suite", page_icon="🔗", layout="wide")
page_header("🔗 Synergy & Deal Value Suite",
            "Size revenue and cost synergies, phase them to run-rate, test value against the purchase price, and "
            "track capture vs plan — the analysis behind $100M+ of identified synergies on real transactions.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)
framework_banner("synergy-deal")

P = st.session_state.setdefault("syn_params", {
    "acq_rev": 4000, "tgt_rev": 1200, "deal_value": 2200, "integration_cost": 120,
    "tgt_sga_pct": 24, "tgt_cogs_pct": 55, "overlap": 0.6, "cross_sell": 0.5, "pricing_power": 0.3,
    "curve": "S-curve (back-loaded)", "n_periods": 4,
})

STAGES = ["① Synergy Sizing", "② Phasing", "③ Capture Tracking", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="syn_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

s = estimate_synergies(P["acq_rev"], P["tgt_rev"], P["tgt_sga_pct"], P["tgt_cogs_pct"], P["overlap"],
                       P["cross_sell"], P["pricing_power"], P["deal_value"], P["integration_cost"])

if stage == STAGES[0]:
    P["acq_rev"] = st.sidebar.number_input("Acquirer revenue ($M)", 50, 200000, P["acq_rev"], step=50)
    P["tgt_rev"] = st.sidebar.number_input("Target revenue ($M)", 10, 100000, P["tgt_rev"], step=10)
    P["deal_value"] = st.sidebar.number_input("Deal value ($M)", 10, 300000, P["deal_value"], step=50)
    P["integration_cost"] = st.sidebar.number_input("Integration cost ($M)", 0, 50000, P["integration_cost"], step=10)
    P["tgt_sga_pct"] = st.sidebar.slider("Target SG&A (% rev)", 5, 50, P["tgt_sga_pct"])
    P["tgt_cogs_pct"] = st.sidebar.slider("Target COGS (% rev)", 20, 85, P["tgt_cogs_pct"])
    P["overlap"] = st.sidebar.slider("Business / cost overlap", 0.0, 1.0, P["overlap"], 0.05)
    P["cross_sell"] = st.sidebar.slider("Cross-sell potential", 0.0, 1.0, P["cross_sell"], 0.05)
    P["pricing_power"] = st.sidebar.slider("Pricing power", 0.0, 1.0, P["pricing_power"], 0.05)
elif stage == STAGES[1]:
    st.sidebar.caption("Phasing uses a fixed 3-year ramp to run-rate.")
    locked_panel([("Run-rate synergies", f"${s['total_runrate']}M"), ("% of deal", f"{s['pct_of_deal']}%")])
elif stage == STAGES[2]:
    P["curve"] = st.sidebar.selectbox("Planned capture curve", list(CURVES.keys()), index=list(CURVES.keys()).index(P["curve"]))
    P["n_periods"] = st.sidebar.slider("Periods (quarters)", 4, 8, P["n_periods"])
    locked_panel([("Synergy target", f"${s['total_runrate']}M")])
else:
    locked_panel([("Run-rate", f"${s['total_runrate']}M"), ("NPV", f"${s['npv']}M"), ("% of deal", f"{s['pct_of_deal']}%")])

s = estimate_synergies(P["acq_rev"], P["tgt_rev"], P["tgt_sga_pct"], P["tgt_cogs_pct"], P["overlap"],
                       P["cross_sell"], P["pricing_power"], P["deal_value"], P["integration_cost"])

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${s["total_runrate"]:,.0f}M</div><div class="l">Run-rate synergies</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{s["pct_of_deal"]}%</div><div class="l">of deal value</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${s["npv"]:,.0f}M</div><div class="l">Synergy NPV @10%</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">${s["cost_syn"]:,.0f}M</div><div class="l">Cost synergies</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    cL, cR = st.columns(2)
    with cL:
        cb = s["cost_breakdown"]
        fig = go.Figure(go.Bar(x=list(cb.values()), y=list(cb.keys()), orientation="h", marker_color="#8B6CFF",
                               text=[f"${v}M" for v in cb.values()], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=240, title="Cost synergies", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=30, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="cost")
    with cR:
        rb = s["rev_breakdown"]
        fig = go.Figure(go.Bar(x=list(rb.values()), y=list(rb.keys()), orientation="h", marker_color="#22D3EE",
                               text=[f"${v}M" for v in rb.values()], textposition="outside"))
        fig.update_layout(template="plotly_dark", height=240, title="Revenue synergies (EBITDA)", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=30, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True, key="rev")

elif stage == STAGES[1]:
    df = pd.DataFrame(s["rows"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Year"], y=df["Cost syn ($M)"], name="Cost", marker_color="#8B6CFF"))
    fig.add_trace(go.Bar(x=df["Year"], y=df["Revenue syn ($M)"], name="Revenue", marker_color="#22D3EE"))
    fig.update_layout(template="plotly_dark", height=320, barmode="stack", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Synergies realized ($M)",
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True, key="phase")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif stage == STAGES[2]:
    st.caption("Track quarterly synergy capture vs the planned curve. Upload actuals or use the demo.")
    n = P["n_periods"]
    inc = planned_increments(s["total_runrate"], P["curve"], n)
    demo = [{"period": f"Q{i+1}", "planned": inc[i], "actual": round(inc[i] * m, 1)}
            for i, m in zip(range(n), [0.85, 0.92, 0.80, 0.88, 0.9, 0.9, 0.9, 0.9])]
    schema = ColumnSchema([Col("period", "text", "Period (e.g. Q1)", "Q1"),
                           Col("planned", "num", "Planned synergy this period ($M)", "15"),
                           Col("actual", "num", "Actual synergy this period ($M)", "12")])
    df_in = data_input(schema, demo, demo_label="Use demo actuals", key="dealtrack")
    if df_in is not None and not df_in.empty:
        d, pct, projected = track(df_in, s["total_runrate"])
        a, b, c = st.columns(3)
        a.markdown(f'<div class="glass metric"><div class="v">{pct:.0f}%</div><div class="l">of target captured</div></div>', unsafe_allow_html=True)
        b.markdown(f'<div class="glass metric"><div class="v">${d["Variance ($M)"].iloc[-1]:+,.0f}M</div><div class="l">Variance to plan</div></div>', unsafe_allow_html=True)
        c.markdown(f'<div class="glass metric"><div class="v">${projected:,.0f}M</div><div class="l">Projected landing</div></div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d["period"], y=d["Planned cum"], name="Planned", line=dict(color="#8B6CFF", width=3)))
        fig.add_trace(go.Scatter(x=d["period"], y=d["Actual cum"], name="Actual", line=dict(color="#22D3EE", width=3)))
        fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          yaxis_title="Cumulative synergies ($M)", margin=dict(l=10, r=10, t=10, b=10),
                          legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True, key="track")
        st.dataframe(d, use_container_width=True, hide_index=True)

else:
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{synergy_summary(s, P["deal_value"])}</div>')
    st.download_button("⬇ Download synergy phasing (CSV)", pd.DataFrame(s["rows"]).to_csv(index=False),
                       file_name="synergy_phasing.csv", mime="text/csv")

st.caption("AI-assisted heuristic synergy & capture model for screening / diligence framing. Directional, not "
           f"investment advice. For deal support: {PROFILE['email']}.")
