import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.ma_suite import (WORKSTREAMS, WS_DEFAULTS, day1_readiness, carveout, separation_org_dot)

st.set_page_config(page_title="Integration & Separation Suite", page_icon="🗂️", layout="wide")
page_header("🗂️ Integration & Separation Suite",
            "Plan Day-1 commercial readiness, size carve-out stranded cost and TSAs, and map the separation org — "
            "the discipline behind a $3B business separation that went market-ready in 9 months.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

P = st.session_state.setdefault("intsep_params", dict(
    {f"ws_{ws}": WS_DEFAULTS[ws] for ws in WORKSTREAMS},
    target_days=90, tgt_rev=800, shared_pct=14, entanglement=6, n_tsa=12, tsa_months=12))

STAGES = ["① Day-1 Readiness", "② Carve-out & Stranded Cost", "③ Separation Org", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="intsep_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

completion = {ws: P[f"ws_{ws}"] for ws in WORKSTREAMS}
day1_df, overall, n_red, days_to_ready, confidence = day1_readiness(completion, P["target_days"])
co = carveout(P["tgt_rev"], P["shared_pct"], P["entanglement"], P["n_tsa"], P["tsa_months"])

if stage == STAGES[0]:
    st.sidebar.caption("Completion % per Day-1 workstream.")
    for ws in WORKSTREAMS:
        P[f"ws_{ws}"] = st.sidebar.slider(ws, 0, 100, P[f"ws_{ws}"], key=f"s_{ws}")
    P["target_days"] = st.sidebar.number_input("Days to planned Day-1", 1, 365, P["target_days"], step=5)
elif stage in (STAGES[1], STAGES[2]):
    P["tgt_rev"] = st.sidebar.number_input("Carve-out revenue ($M)", 10, 100000, P["tgt_rev"], step=10)
    P["shared_pct"] = st.sidebar.slider("Shared-services (% rev)", 1, 40, P["shared_pct"])
    P["entanglement"] = st.sidebar.slider("Entanglement complexity", 1, 10, P["entanglement"])
    P["n_tsa"] = st.sidebar.number_input("# TSAs needed", 0, 60, P["n_tsa"], step=1)
    P["tsa_months"] = st.sidebar.slider("TSA duration (months)", 1, 36, P["tsa_months"])
    locked_panel([("Day-1 readiness", f"{overall:.0f}%"), ("Stranded cost", f"${co['stranded_cost']}M")])
else:
    locked_panel([("Readiness", f"{overall:.0f}%"), ("Stranded", f"${co['stranded_cost']}M"),
                  ("Months to standalone", f"{co['months_to_standalone']}")])

# recompute
completion = {ws: P[f"ws_{ws}"] for ws in WORKSTREAMS}
day1_df, overall, n_red, days_to_ready, confidence = day1_readiness(completion, P["target_days"])
co = carveout(P["tgt_rev"], P["shared_pct"], P["entanglement"], P["n_tsa"], P["tsa_months"])

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{overall:.0f}%</div><div class="l">Day-1 readiness</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v" style="color:#F87171">{n_red}</div><div class="l">Red workstreams</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${co["stranded_cost"]:,.0f}M</div><div class="l">Stranded cost</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">~{co["months_to_standalone"]}</div><div class="l">Months to standalone</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")
RAG_COLOR = {"🔴 Red": "#F87171", "🟠 Amber": "#FBBF24", "🟢 Green": "#34D399"}

if stage == STAGES[0]:
    st.caption(f"Go-live confidence: **{confidence}** · ~{days_to_ready} days of focused effort to green.")
    fig = go.Figure(go.Bar(x=day1_df["Completion %"], y=day1_df["Workstream"], orientation="h",
                           marker_color=[RAG_COLOR[r] for r in day1_df["RAG"]],
                           text=[f"{p}%" for p in day1_df["Completion %"]], textposition="outside"))
    fig.add_vline(x=50, line_dash="dot", line_color="#F87171", opacity=.5)
    fig.add_vline(x=80, line_dash="dot", line_color="#34D399", opacity=.5)
    fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Completion %", xaxis_range=[0, 110], yaxis=dict(autorange="reversed"),
                      margin=dict(l=10, r=30, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="day1")
    st.dataframe(day1_df, use_container_width=True, hide_index=True)

elif stage == STAGES[1]:
    st.caption(f"Separation complexity: **{co['complexity']}**. One-time separation cost ${co['separation_cost']}M.")
    cL, cR = st.columns([1, 1])
    with cL:
        fig = go.Figure(go.Waterfall(orientation="v", measure=["absolute", "relative", "total"],
                                     x=["Shared-services", "Cleanly exited", "Stranded cost"],
                                     y=[co["shared_cost"], -(co["shared_cost"] - co["stranded_cost"]), co["stranded_cost"]],
                                     text=[f"${co['shared_cost']:.0f}M", f"-${co['shared_cost']-co['stranded_cost']:.0f}M", f"${co['stranded_cost']:.0f}M"],
                                     connector={"line": {"color": "rgba(255,255,255,.2)"}},
                                     decreasing={"marker": {"color": "#22D3EE"}}, totals={"marker": {"color": "#8B6CFF"}}))
        fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          yaxis_title="$M", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, key="bridge")
    with cR:
        fig = go.Figure(go.Bar(x=co["tsa_df"]["Exit month"], y=co["tsa_df"]["Function"], orientation="h",
                               marker_color="#8B6CFF",
                               text=[f"{m} mo · {c} TSA" for m, c in zip(co["tsa_df"]["Exit month"], co["tsa_df"]["TSAs"])],
                               textposition="outside"))
        fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_title="TSA exit month", yaxis=dict(autorange="reversed"), title="TSA exit by function",
                          margin=dict(l=10, r=30, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True, key="tsa")

elif stage == STAGES[2]:
    st.caption("Separation org: RemainCo provides transition services (TSAs) to the standalone DivestCo until exit.")
    st.graphviz_chart(separation_org_dot(co["tsa_df"]), use_container_width=True)
    st.dataframe(co["tsa_df"], use_container_width=True, hide_index=True)

else:
    reds = ", ".join(day1_df[day1_df["RAG"] == "🔴 Red"]["Workstream"]) or "none"
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">The commercial operating model is '
          f'<b>{overall:.0f}% Day-1 ready</b> with <b>{n_red} red</b> workstream(s) ({reds}); go-live confidence is '
          f'<b>{confidence}</b>, ~{days_to_ready} days from green. On the carve-out, expect <b>${co["stranded_cost"]}M</b> '
          f'of stranded cost ({co["stranded_pct"]}% of revenue) and <b>${co["separation_cost"]}M</b> one-time separation '
          f'cost, reaching standalone in ~<b>{co["months_to_standalone"]} months</b> at <b>{co["complexity"]}</b> complexity. '
          'Stand up a dedicated stranded-cost program and a TSA-exit office, and close the red workstreams before '
          'committing to a Day-1 date.</div>')
    st.download_button("⬇ Download Day-1 tracker (CSV)", day1_df.to_csv(index=False),
                       file_name="day1_readiness.csv", mime="text/csv")

st.caption("AI-assisted heuristic readiness & carve-out model. Directional, not investment advice. "
           f"For separation / integration support: {PROFILE['email']}.")
