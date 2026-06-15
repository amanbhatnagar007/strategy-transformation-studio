import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="Payer Contract Analyzer", page_icon="💵", layout="wide")
page_header("💵 Payer Contract Analyzer",
            "Analyze provider profitability across payer contracts. Margin per contract, loss-makers, and "
            "renegotiation targets — the encounter-and-reimbursement lens behind smarter payer decisions.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

ACCENT, ACCENT2, RED = "#8B6CFF", "#22D3EE", "#EF4444"

DEMO_ROWS = [
    {"contract": "BlueCross PPO", "encounters": 12000, "reimbursement_per": 210, "cost_per": 165, "patient_mix": "Commercial"},
    {"contract": "Aetna HMO", "encounters": 8200, "reimbursement_per": 158, "cost_per": 172, "patient_mix": "Commercial"},
    {"contract": "Medicare FFS", "encounters": 15600, "reimbursement_per": 132, "cost_per": 140, "patient_mix": "Medicare"},
    {"contract": "Medicaid MCO", "encounters": 9400, "reimbursement_per": 98, "cost_per": 119, "patient_mix": "Medicaid"},
    {"contract": "UnitedHealth PPO", "encounters": 11100, "reimbursement_per": 224, "cost_per": 170, "patient_mix": "Commercial"},
    {"contract": "Cigna HMO", "encounters": 6700, "reimbursement_per": 188, "cost_per": 161, "patient_mix": "Commercial"},
    {"contract": "Humana MA", "encounters": 7800, "reimbursement_per": 176, "cost_per": 158, "patient_mix": "Medicare Adv"},
]


def analyze(df):
    out = df.copy()
    out["Margin per encounter ($)"] = out["reimbursement_per"] - out["cost_per"]
    out["Total margin ($)"] = out["encounters"] * out["Margin per encounter ($)"]
    out["Revenue ($)"] = out["encounters"] * out["reimbursement_per"]
    out["Margin %"] = (out["Margin per encounter ($)"] / out["reimbursement_per"].replace(0, pd.NA) * 100)
    return out.sort_values("Total margin ($)", ascending=False).reset_index(drop=True)


with st.sidebar:
    st.header("About this app")
    st.caption("Provide your payer contract lines on the upload tab, or explore the demo book. "
               "Margin per contract = encounters × (reimbursement − cost). Nothing is fabricated.")

t1, t2, t3 = st.tabs(["📤 Upload your data", "📊 Margin analysis", "📋 Executive summary"])

schema = ColumnSchema([
    Col("contract", "text", "Payer / contract name", "BlueCross PPO"),
    Col("encounters", "int", "Annual encounters / claims", "12000"),
    Col("reimbursement_per", "num", "Reimbursement per encounter ($)", "210"),
    Col("cost_per", "num", "Fully-loaded cost per encounter ($)", "165"),
    Col("patient_mix", "text", "Patient mix / segment label", "Commercial"),
])

with t1:
    st.markdown("#### Upload your payer contract book")
    st.caption("The analysis runs only on the contract lines you provide.")
    df = data_input(schema, DEMO_ROWS, key="payer")
    st.session_state["_payer_df"] = df

df = st.session_state.get("_payer_df")

with t2:
    st.markdown("#### Profitability across contracts")
    if df is None or df.empty:
        st.info("Add contract lines on the upload tab to see the analysis.")
    else:
        a = analyze(df)
        total_margin = a["Total margin ($)"].sum()
        total_rev = a["Revenue ($)"].sum()
        margin_pct = (total_margin / total_rev * 100) if total_rev else 0
        loss_n = int((a["Total margin ($)"] < 0).sum())
        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="glass metric"><div class="v">${total_margin:,.0f}</div><div class="l">Total annual margin</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="glass metric"><div class="v">{margin_pct:.1f}%</div><div class="l">Blended margin %</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="glass metric"><div class="v">{loss_n}</div><div class="l">Loss-making contracts</div></div>', unsafe_allow_html=True)

        cL, cR = st.columns(2)
        with cL:
            colors = [RED if v < 0 else ACCENT for v in a["Total margin ($)"]]
            fig = go.Figure(go.Bar(x=a["Total margin ($)"], y=a["contract"], orientation="h",
                                   marker_color=colors,
                                   text=[f"${v:,.0f}" for v in a["Total margin ($)"]], textposition="outside"))
            fig.update_layout(template="plotly_dark", height=360, title="Total margin by contract",
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              yaxis=dict(autorange="reversed"), margin=dict(l=10, r=40, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with cR:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=a["cost_per"], y=a["reimbursement_per"], mode="markers+text",
                                     text=a["contract"], textposition="top center",
                                     marker=dict(size=a["encounters"] / a["encounters"].max() * 38 + 8,
                                                 color=a["Total margin ($)"], colorscale=[[0, RED], [0.5, "#9AA6CC"], [1, ACCENT2]],
                                                 showscale=False, line=dict(color="#fff", width=1))))
            lo = min(a["cost_per"].min(), a["reimbursement_per"].min())
            hi = max(a["cost_per"].max(), a["reimbursement_per"].max())
            fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Break-even",
                                     line=dict(color="#9AA6CC", dash="dash"), showlegend=False))
            fig.update_layout(template="plotly_dark", height=360, title="Reimbursement vs cost (bubble = volume)",
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              xaxis_title="Cost / encounter ($)", yaxis_title="Reimbursement / encounter ($)",
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)
        glass('<div style="color:#aab4d6;font-size:.85rem">Points below the dashed break-even line lose money on '
              'every encounter. Large red bubbles are the most urgent renegotiation targets — high volume amplifies '
              'a negative per-encounter margin.</div>')
        st.dataframe(a[["contract", "patient_mix", "encounters", "reimbursement_per", "cost_per",
                        "Margin per encounter ($)", "Margin %", "Total margin ($)"]].round(1),
                     use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    if df is None or df.empty:
        st.info("Add contract lines on the upload tab to generate the summary.")
    else:
        a = analyze(df)
        total_margin = a["Total margin ($)"].sum()
        total_rev = a["Revenue ($)"].sum()
        margin_pct = (total_margin / total_rev * 100) if total_rev else 0
        best = a.iloc[0]
        worst = a.iloc[-1]
        losers = a[a["Total margin ($)"] < 0]
        loss_names = ", ".join(losers["contract"].tolist()) if not losers.empty else "none"
        loss_drag = losers["Total margin ($)"].sum() if not losers.empty else 0
        txt = (f"Across <b>{len(a)}</b> payer contracts the book generates <b>${total_margin:,.0f}</b> in annual margin "
               f"at a blended <b>{margin_pct:.1f}%</b>. <b>{best['contract']}</b> is the strongest contributor "
               f"(${best['Total margin ($)']:,.0f}), while <b>{worst['contract']}</b> is the weakest "
               f"(${worst['Total margin ($)']:,.0f}). "
               f"Renegotiation priority: <b>{loss_names}</b>"
               + (f" — together a <b>${loss_drag:,.0f}</b> drag." if not losers.empty else " (all contracts are margin-positive; focus on the thinnest margins).")
               + " Recommendation: pursue rate increases or cost-to-serve reduction on the loss-makers, and protect "
               "the high-volume positive contracts in any rebid. Figures are directional heuristics from the encounter, "
               "reimbursement and cost lines you provided — validate against the actual contract schedules before negotiating.")
        glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{txt}</div>')
        st.download_button("⬇ Download contract analysis (CSV)",
                           a[["contract", "patient_mix", "encounters", "reimbursement_per", "cost_per",
                              "Margin per encounter ($)", "Margin %", "Total margin ($)"]].to_csv(index=False),
                           file_name="payer_contract_analysis.csv", mime="text/csv")

st.caption("AI-assisted heuristic contract-margin model — directional, not a substitute for actuarial or contract review. "
           f"For a tailored engagement: {PROFILE['email']}.")
