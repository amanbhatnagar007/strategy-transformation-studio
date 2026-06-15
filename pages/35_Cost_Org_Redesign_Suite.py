import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.frameworks import framework_banner
from lib.cost_logic import cost_savings, cost_summary
from lib.orgchart import delayer_org_dot

st.set_page_config(page_title="Cost & Org Redesign Suite", page_icon="🛠️", layout="wide")
page_header("🛠️ Cost & Org Redesign Suite",
            "Quantify cost takeout by lever, model the spans-and-layers de-layering, and see the before/after "
            "org — the approach behind ~$150M of identified cost improvement on a Fortune-500 client.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)
framework_banner("cost-org")

P = st.session_state.setdefault("cor_params", {
    "cost_base": 900, "headcount": 6000, "avg_cost": 95, "footprint_cost": 80,
    "procurement_addr": 300, "layers": 9, "target_span": 7, "automation_ready": 0.5,
})

STAGES = ["① Cost Takeout", "② Spans & Layers", "③ Org Chart (before/after)", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="cor_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

c = cost_savings(P["cost_base"], P["headcount"], P["avg_cost"], P["layers"], P["target_span"],
                 P["procurement_addr"], P["automation_ready"], P["footprint_cost"])
target_layers = max(4, math.ceil(math.log(max(P["headcount"], 2)) / math.log(max(P["target_span"], 1.6))))

if stage == STAGES[0]:
    P["cost_base"] = st.sidebar.number_input("Cost base ($M)", 10, 100000, P["cost_base"], step=10)
    P["procurement_addr"] = st.sidebar.number_input("Addressable 3rd-party spend ($M)", 0, 50000, P["procurement_addr"], step=10)
    P["footprint_cost"] = st.sidebar.number_input("Facilities cost ($M)", 0, 20000, P["footprint_cost"], step=5)
    P["automation_ready"] = st.sidebar.slider("Automation readiness", 0.0, 1.0, P["automation_ready"], 0.05)
elif stage in (STAGES[1], STAGES[2]):
    P["headcount"] = st.sidebar.number_input("Headcount (FTEs)", 50, 500000, P["headcount"], step=50)
    P["avg_cost"] = st.sidebar.number_input("Avg fully-loaded cost ($k/FTE)", 20, 500, P["avg_cost"], step=5)
    P["layers"] = st.sidebar.slider("Current management layers", 4, 14, P["layers"])
    P["target_span"] = st.sidebar.slider("Target span of control", 4, 12, P["target_span"])
    locked_panel([("Cost takeout", f"${c['total']}M"), ("Current span", f"{c['org']['current_span']}")])
else:
    locked_panel([("Cost takeout", f"${c['total']}M"), ("Roles removed", f"~{c['mgr_reduction']:,}"),
                  ("Layers", f"{P['layers']} → {target_layers}")])

c = cost_savings(P["cost_base"], P["headcount"], P["avg_cost"], P["layers"], P["target_span"],
                 P["procurement_addr"], P["automation_ready"], P["footprint_cost"])
target_layers = max(4, math.ceil(math.log(max(P["headcount"], 2)) / math.log(max(P["target_span"], 1.6))))

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">${c["total"]:,.0f}M</div><div class="l">Cost takeout</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{c["pct"]}%</div><div class="l">of cost base</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{c["org"]["current_span"]}</div><div class="l">Current span</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">~{c["mgr_reduction"]:,}</div><div class="l">Mgmt roles removed</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    lv = c["levers"]
    measures = ["relative"] * len(lv) + ["total"]
    fig = go.Figure(go.Waterfall(orientation="v", measure=measures, x=list(lv.keys()) + ["Total takeout"],
                                 y=list(lv.values()) + [c["total"]],
                                 text=[f"${v}M" for v in lv.values()] + [f"${c['total']}M"],
                                 connector={"line": {"color": "rgba(255,255,255,.2)"}},
                                 increasing={"marker": {"color": "#22D3EE"}}, totals={"marker": {"color": "#8B6CFF"}}))
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="Savings ($M)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="waterfall")

elif stage == STAGES[1]:
    cL, cR = st.columns(2)
    with cL:
        glass(f'<div style="font-weight:600;color:#fff">Current state</div>'
              f'<div class="bullet">{P["layers"]} management layers</div>'
              f'<div class="bullet">Avg span: {c["org"]["current_span"]}</div>'
              f'<div class="bullet">~{c["org"]["managers"]:,} managers</div>'
              f'<div class="bullet">{c["org"]["excess_layers"]} layers above best-practice (≤6)</div>')
    with cR:
        glass(f'<div style="font-weight:600;color:#fff">Target state</div>'
              f'<div class="bullet">~{target_layers} layers</div>'
              f'<div class="bullet">Span: {P["target_span"]}</div>'
              f'<div class="bullet">~{c["target_managers"]:,} managers</div>'
              f'<div class="bullet">~{c["mgr_reduction"]:,} roles removed (55% realization)</div>')
    st.dataframe(pd.DataFrame(c["rows"]), use_container_width=True, hide_index=True)

elif stage == STAGES[2]:
    st.caption(f"De-layering from {P['layers']} to ~{target_layers} layers at a {P['target_span']}× target span.")
    cL, cR = st.columns(2)
    with cL:
        st.markdown("**Before**")
        st.graphviz_chart(delayer_org_dot(P["layers"], P["headcount"], "#EC4899"), use_container_width=True)
    with cR:
        st.markdown("**After**")
        st.graphviz_chart(delayer_org_dot(target_layers, P["headcount"], "#22D3EE"), use_container_width=True)

else:
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{cost_summary(c, P["cost_base"])}</div>')
    df = pd.DataFrame([{"Lever": k, "Savings ($M)": v} for k, v in c["levers"].items()])
    st.download_button("⬇ Download savings by lever (CSV)", df.to_csv(index=False),
                       file_name="cost_takeout.csv", mime="text/csv")

st.caption("AI-assisted heuristic cost & org model. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
