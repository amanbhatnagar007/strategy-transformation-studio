import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.frameworks import framework_banner
from lib.uploads import ColumnSchema, Col, data_input
from lib.payer_suite import demo_contracts, analyze_contracts, margin_tier, medicare_value

st.set_page_config(page_title="Payer & Reimbursement Suite", page_icon="💵", layout="wide")
page_header("💵 Payer & Reimbursement Suite",
            "Find where payer contracts make and lose money at the CPT level, build a renegotiation target list, "
            "and size Medicare Advantage value from better risk capture — the analysis behind +15% provider profitability.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)
framework_banner("payer-reimbursement")

STAGES = ["① Contract profitability", "② Medicare Advantage value"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Module (controls adapt below)", STAGES, key="payer_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ',1)[1]}")

P = st.session_state.setdefault("payer_params", {
    "members": 50000, "base_pmpm": 950, "raf_current": 1.05, "raf_target": 1.18,
    "care_pmpm": 22, "mlr_improve": 1.5,
})

# ============ STAGE 1: CONTRACT PROFITABILITY ============
if stage == STAGES[0]:
    schema = ColumnSchema([
        Col("contract_id", "text", "Contract/line identifier — REQUIRED to action renegotiations", "Aetna-99213", required=True),
        Col("service", "text", "CPT / DRG / service line", "99213", required=True),
        Col("encounters", "int", "Encounter / claim volume", "1200", required=True),
        Col("contracted_rate", "num", "Contracted reimbursement per unit ($)", "118", required=True),
        Col("cost_per_unit", "num", "Your cost to deliver per unit ($)", "95", required=True),
        Col("payer", "text", "Payer name", "Aetna", required=False),
        Col("denial_rate", "pct", "Denial rate %", "8", required=False),
        Col("expected_rate", "num", "Expected/allowed rate ($) for underpayment checks", "120", required=False),
    ])
    st.markdown("#### Load your payer contract lines")
    df_raw = data_input(schema, demo_contracts(), demo_label="Use demo contracts", key="payerlines")
    if df_raw is None or df_raw.empty:
        st.stop()

    res = analyze_contracts(df_raw)
    res["tier"] = res["margin_pct"].apply(margin_tier)
    total_margin = res["total_margin"].sum()
    loss_n = int((res["margin_pct"] < 0).sum())
    at_stake = -res[res["total_margin"] < 0]["total_margin"].sum()

    st.sidebar.caption("Profitability is computed per line from rate − cost × encounters.")
    locked_panel([("Lines", f"{len(res):,}"), ("Loss-making", f"{loss_n}"),
                  ("$ at stake", f"${at_stake/1e6:.1f}M")])

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="glass metric"><div class="v">${total_margin/1e6:.1f}M</div><div class="l">Total margin</div></div>', unsafe_allow_html=True)
    blended = res["margin_pct"].mean()
    k2.markdown(f'<div class="glass metric"><div class="v">{blended:.0f}%</div><div class="l">Avg margin %</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass metric"><div class="v" style="color:#F87171">{loss_n}</div><div class="l">Loss-making lines</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="glass metric"><div class="v">${at_stake/1e6:.1f}M</div><div class="l">Margin at stake</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {stage}")
    worst = res.head(15)
    fig = go.Figure(go.Bar(
        x=worst["total_margin"], y=worst["contract_id"], orientation="h",
        marker_color=["#F87171" if v < 0 else "#34D399" for v in worst["total_margin"]],
        text=[f"${v/1000:.0f}k" for v in worst["total_margin"]], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=420, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Total margin ($)",
                      yaxis=dict(autorange="reversed"), title="15 lowest-margin contract lines",
                      margin=dict(l=10, r=30, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True, key="margins")

    st.markdown("#### Renegotiation action plan")
    tier_defs = [
        {"label": "🔴 Loss-making", "accent": "#F87171",
         "action": "Renegotiate or exit. Rebase rate to at least cover cost; escalate to payer JOC with the data."},
        {"label": "🟠 Thin", "accent": "#FBBF24",
         "action": "Target in the next cycle. Benchmark vs better payers for the same CPT; pursue modest uplift."},
        {"label": "🟢 Healthy", "accent": "#34D399",
         "action": "Protect. Maintain terms; use as a benchmark for under-performing payers."},
    ]
    cols = st.columns(3)
    for c, td in zip(cols, tier_defs):
        sub = res[res["tier"] == td["label"]]
        c.markdown(f'<div class="glass metric" style="border-color:{td["accent"]}55">'
                   f'<div class="v" style="color:{td["accent"]}">{len(sub)}</div>'
                   f'<div class="l">{td["label"]}</div></div>', unsafe_allow_html=True)
    for td in tier_defs:
        sub = res[res["tier"] == td["label"]].sort_values("total_margin")
        if sub.empty:
            continue
        glass(f'<div style="border-left:3px solid {td["accent"]};padding-left:.6rem">'
              f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff">{td["label"]} '
              f'<span style="color:#9AA6CC;font-size:.8rem">· {len(sub)} lines</span></div>'
              f'<div style="color:#c4b5ff;font-size:.9rem;margin-top:.3rem"><b>Action:</b> {td["action"]}</div></div>')
        show = [c for c in ["contract_id", "payer", "service", "encounters", "contracted_rate",
                            "cost_per_unit", "margin_pct", "total_margin"] if c in sub.columns]
        with st.expander(f"View & download {td['label']} list ({len(sub)})"):
            st.dataframe(sub[show], use_container_width=True, hide_index=True, key=f"tb_{td['label']}")
            st.download_button(f"⬇ {td['label']} list (CSV)", sub[show].to_csv(index=False),
                               file_name=f"contracts_{td['label'].split()[1].lower()}.csv", mime="text/csv",
                               key=f"dl_{td['label']}")

# ============ STAGE 2: MEDICARE ADVANTAGE ============
else:
    P["members"] = st.sidebar.number_input("MA members", 1000, 5_000_000, P["members"], step=1000)
    P["base_pmpm"] = st.sidebar.number_input("Base PMPM revenue ($)", 300, 3000, P["base_pmpm"], step=10)
    P["raf_current"] = st.sidebar.slider("Current avg RAF (risk score)", 0.6, 2.0, P["raf_current"], 0.01)
    P["raf_target"] = st.sidebar.slider("Target RAF after risk capture", P["raf_current"], 2.5, max(P["raf_target"], P["raf_current"]), 0.01)
    P["care_pmpm"] = st.sidebar.number_input("Care-management cost PMPM ($)", 0, 200, P["care_pmpm"], step=1)
    P["mlr_improve"] = st.sidebar.slider("MLR improvement (pp)", 0.0, 8.0, P["mlr_improve"], 0.1)
    locked_panel([("Members", f"{P['members']:,}"), ("RAF lift", f"{P['raf_current']} → {P['raf_target']}")])

    v = medicare_value(P["members"], P["base_pmpm"], P["raf_current"], P["raf_target"],
                       P["care_pmpm"], P["mlr_improve"])
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="glass metric"><div class="v">${v["margin_upside"]/1e6:.1f}M</div><div class="l">Margin upside / yr</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="glass metric"><div class="v">${v["risk_uplift"]/1e6:.1f}M</div><div class="l">Risk-capture revenue</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass metric"><div class="v">${v["per_member"]:,.0f}</div><div class="l">Per member / yr</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {stage}")
    st.caption("Value bridge: better risk capture (RAF) + MLR improvement, net of care-management investment.")
    labels = ["Current revenue", "Risk capture", "MLR savings", "Care mgmt cost", "Net upside"]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=["absolute", "relative", "relative", "relative", "total"],
        x=labels,
        y=[v["rev_current"]/1e6, v["risk_uplift"]/1e6, v["mlr_savings"]/1e6, -v["care_cost"]/1e6, v["margin_upside"]/1e6],
        text=[f"${x/1e6:.1f}M" for x in [v["rev_current"], v["risk_uplift"], v["mlr_savings"], -v["care_cost"], v["margin_upside"]]],
        connector={"line": {"color": "rgba(255,255,255,.2)"}},
        increasing={"marker": {"color": "#34D399"}}, decreasing={"marker": {"color": "#F87171"}},
        totals={"marker": {"color": "#8B6CFF"}}))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="$M", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="ma_bridge")
    glass(f'<div style="color:#dfe5fb">Improving average RAF from {P["raf_current"]} to {P["raf_target"]} and MLR by '
          f'{P["mlr_improve"]}pp yields an estimated <b>${v["margin_upside"]/1e6:.1f}M</b> annual margin upside '
          f'(${v["per_member"]:,.0f}/member), net of ${v["care_cost"]/1e6:.1f}M care-management investment. '
          'Validate RAF assumptions against documented, compliant risk-adjustment coding.</div>')

st.caption("AI-assisted heuristic models for payer-contract and MA value framing. Directional, not coding or "
           f"actuarial advice. For a tailored engagement: {PROFILE['email']}.")
