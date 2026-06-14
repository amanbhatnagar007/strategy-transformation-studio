import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="Value-Creation Roadmap", page_icon="🗺️", layout="wide")
page_header("🗺️ Value-Creation Roadmap",
            "Prioritize and sequence transformation initiatives on an impact-vs-effort matrix, then phase "
            "them into a roadmap with cumulative value over time.")
st.page_link("Home.py", label="← Back to Studio")

DEMO = [
    {"initiative": "Procurement renegotiation", "value_m": 18, "effort": 3, "months_to_impact": 4},
    {"initiative": "Spans & layers de-layering", "value_m": 32, "effort": 6, "months_to_impact": 9},
    {"initiative": "Footprint consolidation", "value_m": 14, "effort": 7, "months_to_impact": 14},
    {"initiative": "SG&A shared services", "value_m": 26, "effort": 8, "months_to_impact": 12},
    {"initiative": "Pricing optimization", "value_m": 22, "effort": 4, "months_to_impact": 6},
    {"initiative": "Process automation", "value_m": 16, "effort": 5, "months_to_impact": 8},
    {"initiative": "Working-capital release", "value_m": 12, "effort": 3, "months_to_impact": 5},
    {"initiative": "Portfolio rationalization", "value_m": 28, "effort": 9, "months_to_impact": 18},
]

schema = ColumnSchema([
    Col("initiative", "text", "Name of the initiative", "Procurement renegotiation"),
    Col("value_m", "num", "Annual value at run-rate ($M)", "18"),
    Col("effort", "int", "Effort / difficulty (1 = easy, 10 = hard)", "3"),
    Col("months_to_impact", "int", "Months until value lands", "4"),
])

st.markdown("#### Initiatives")
df = data_input(schema, DEMO, demo_label="Use demo initiatives", key="vcr")

if df is None or df.empty:
    st.stop()

df = df.copy()
val_mid = df["value_m"].median()
eff_mid = df["effort"].median()

def quadrant(r):
    hi_val = r["value_m"] >= val_mid
    lo_eff = r["effort"] < eff_mid
    if hi_val and lo_eff:
        return "Quick wins"
    if hi_val and not lo_eff:
        return "Big bets"
    if not hi_val and lo_eff:
        return "Fill-ins"
    return "Hard slogs"

df["quadrant"] = df.apply(quadrant, axis=1)

total_value = round(df["value_m"].sum(), 1)
n_quick = int((df["quadrant"] == "Quick wins").sum())
year1_value = round(df.loc[df["months_to_impact"] <= 12, "value_m"].sum(), 1)

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${total_value:,.0f}M</div><div class="l">Total value at run-rate</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{n_quick}</div><div class="l">Quick wins</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${year1_value:,.0f}M</div><div class="l">Value landing ≤ 12 mo</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🎯 Impact vs effort", "📅 Sequenced roadmap", "📋 Executive summary"])

QCOLOR = {"Quick wins": "#22D3EE", "Big bets": "#8B6CFF", "Fill-ins": "#9AA6CC", "Hard slogs": "#EC4899"}

with t1:
    st.markdown("#### Prioritization matrix")
    fig = go.Figure()
    for q in ["Quick wins", "Big bets", "Fill-ins", "Hard slogs"]:
        sub = df[df["quadrant"] == q]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["effort"], y=sub["value_m"], mode="markers+text", name=q,
            text=sub["initiative"], textposition="top center",
            marker=dict(size=(sub["value_m"] / df["value_m"].max() * 50 + 12),
                        color=QCOLOR[q], opacity=0.85, line=dict(color="white", width=1))))
    fig.add_vline(x=eff_mid, line_dash="dash", line_color="rgba(255,255,255,.25)")
    fig.add_hline(y=val_mid, line_dash="dash", line_color="rgba(255,255,255,.25)")
    fig.update_layout(template="plotly_dark", height=440, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Effort / difficulty →",
                      yaxis_title="Value ($M) →", legend=dict(orientation="h", y=-0.2),
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">Quadrants split at the median value and effort of '
          '<b>your</b> initiatives. <b style="color:#22D3EE">Quick wins</b> (high value, low effort) self-fund '
          'the program; <b style="color:#8B6CFF">Big bets</b> need investment but carry the upside; '
          '<b>Fill-ins</b> are opportunistic; <b style="color:#EC4899">Hard slogs</b> warrant a hard look at '
          'whether the prize justifies the effort.</div>')

with t2:
    st.markdown("#### Sequenced by time-to-impact")
    # Order: quick wins first, then by months_to_impact, then by value desc
    qrank = {"Quick wins": 0, "Fill-ins": 1, "Big bets": 2, "Hard slogs": 3}
    seq = df.assign(_q=df["quadrant"].map(qrank)).sort_values(
        ["_q", "months_to_impact", "value_m"], ascending=[True, True, False]).reset_index(drop=True)
    seq.insert(0, "Seq", range(1, len(seq) + 1))

    # Cumulative value over time
    cum = df.sort_values("months_to_impact").copy()
    cum["cumulative_value_m"] = cum["value_m"].cumsum().round(1)
    fig = go.Figure(go.Scatter(
        x=cum["months_to_impact"], y=cum["cumulative_value_m"], mode="lines+markers",
        line=dict(color="#8B6CFF", width=3), marker=dict(color="#22D3EE", size=9),
        text=cum["initiative"], hovertemplate="%{text}<br>Month %{x}: $%{y}M cum<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Months to impact",
                      yaxis_title="Cumulative value ($M)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(seq[["Seq", "initiative", "value_m", "effort", "months_to_impact", "quadrant"]],
                 use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    qw = df[df["quadrant"] == "Quick wins"].sort_values("value_m", ascending=False)
    qw_names = ", ".join(qw["initiative"].tolist()) if not qw.empty else "none at the current thresholds"
    bb = df[df["quadrant"] == "Big bets"].sort_values("value_m", ascending=False)
    bb_names = ", ".join(bb["initiative"].head(3).tolist()) if not bb.empty else "none"
    summary = (
        f"Across <b>{len(df)} initiatives</b>, the portfolio carries <b>${total_value:,.0f}M</b> of "
        f"run-rate value, with <b>${year1_value:,.0f}M</b> landing within 12 months. "
        f"Lead with the <b>{n_quick} quick win(s)</b> ({qw_names}) to build momentum and self-fund the "
        f"program, then sequence the big bets ({bb_names}) that carry the structural upside. "
        f"Re-prioritize as effort and value estimates firm up — these reflect only the initiatives you "
        f"entered and are directional planning inputs, not committed targets."
    )
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{summary}</div>')
    out = df[["initiative", "value_m", "effort", "months_to_impact", "quadrant"]]
    st.download_button("⬇ Download roadmap (CSV)", out.to_csv(index=False),
                       file_name="value_creation_roadmap.csv", mime="text/csv")

st.caption("AI-assisted heuristic prioritization for value-creation framing. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
