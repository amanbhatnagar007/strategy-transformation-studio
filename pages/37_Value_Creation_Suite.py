import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="Value Creation Planning", page_icon="🗺️", layout="wide")
page_header("🗺️ Value Creation Planning",
            "Walk EBITDA from today to a target lever by lever, then prioritize and sequence the initiatives "
            "that deliver it — impact vs effort, with cumulative value over time.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

P = st.session_state.setdefault("vcp_params", {
    "rev": 1200, "margin_pct": 14, "price_up": 2.0, "vol_growth": 4.0, "cogs_red": 3.0, "sga_red": 2.5, "mix_up": 1.0})

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

STAGES = ["① EBITDA Bridge", "② Initiative Roadmap", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="vcp_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")


def ebitda():
    start = P["rev"] * P["margin_pct"] / 100.0
    levers = {"Price uplift": round(P["rev"] * P["price_up"] / 100, 1),
              "Volume growth": round(P["rev"] * P["vol_growth"] / 100 * P["margin_pct"] / 100, 1),
              "COGS reduction": round(P["rev"] * P["cogs_red"] / 100, 1),
              "SG&A reduction": round(P["rev"] * P["sga_red"] / 100, 1),
              "Mix improvement": round(P["rev"] * P["mix_up"] / 100, 1)}
    total = round(sum(levers.values()), 1)
    target = round(start + total, 1)
    new_rev = P["rev"] * (1 + P["vol_growth"] / 100) + P["rev"] * P["price_up"] / 100
    new_margin = target / new_rev * 100 if new_rev else 0
    return start, levers, total, target, new_margin

start, levers, total, target, new_margin = ebitda()

if stage == STAGES[0]:
    P["rev"] = st.sidebar.number_input("Starting revenue ($M)", 10, 200000, P["rev"], step=10)
    P["margin_pct"] = st.sidebar.slider("Starting EBITDA margin (%)", 1, 60, P["margin_pct"])
    P["price_up"] = st.sidebar.slider("Price uplift (%)", 0.0, 15.0, P["price_up"], 0.5)
    P["vol_growth"] = st.sidebar.slider("Volume growth (%)", 0.0, 25.0, P["vol_growth"], 0.5)
    P["cogs_red"] = st.sidebar.slider("COGS reduction (%)", 0.0, 15.0, P["cogs_red"], 0.5)
    P["sga_red"] = st.sidebar.slider("SG&A reduction (%)", 0.0, 15.0, P["sga_red"], 0.5)
    P["mix_up"] = st.sidebar.slider("Mix improvement (%)", 0.0, 8.0, P["mix_up"], 0.5)
else:
    locked_panel([("Start EBITDA", f"${start:,.0f}M"), ("Target EBITDA", f"${target:,.0f}M")])

start, levers, total, target, new_margin = ebitda()
margin_delta = round((new_margin - P["margin_pct"]) * 100)

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${start:,.0f}M</div><div class="l">Start EBITDA</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${target:,.0f}M</div><div class="l">Target EBITDA</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">+{margin_delta:,} bps</div><div class="l">Margin delta</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    measures = ["absolute"] + ["relative"] * len(levers) + ["total"]
    fig = go.Figure(go.Waterfall(orientation="v", measure=measures,
                                 x=["Start EBITDA"] + list(levers.keys()) + ["Target EBITDA"],
                                 y=[round(start, 1)] + list(levers.values()) + [target],
                                 text=[f"${round(start,1)}M"] + [f"+${v}M" for v in levers.values()] + [f"${target}M"],
                                 textposition="outside", connector={"line": {"color": "rgba(255,255,255,.2)"}},
                                 increasing={"marker": {"color": "#22D3EE"}}, totals={"marker": {"color": "#8B6CFF"}}))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="EBITDA ($M)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="bridge")
    glass(f'<div style="color:#aab4d6;font-size:.85rem">Margin moves from <b style="color:#fff">{P["margin_pct"]}%</b> '
          f'to <b style="color:#fff">{new_margin:.1f}%</b>. Price & cost levers drop ~fully to EBITDA; volume is '
          'credited at current margin; mix is a directional assumption — validate each before committing.</div>')

elif stage == STAGES[1]:
    st.caption("Upload your initiative list (or use the demo) to prioritize on impact vs effort.")
    schema = ColumnSchema([Col("initiative", "text", "Initiative name", "Procurement renegotiation", required=True),
                           Col("value_m", "num", "Annual value at run-rate ($M)", "18", required=True),
                           Col("effort", "int", "Effort 1 (easy) – 10 (hard)", "3", required=True),
                           Col("months_to_impact", "int", "Months until value lands", "4", required=True)])
    df = data_input(schema, DEMO, demo_label="Use demo initiatives", key="vcr")
    if df is not None and not df.empty:
        df = df.copy()
        vm, em = df["value_m"].median(), df["effort"].median()
        df["quadrant"] = df.apply(lambda r: ("Quick wins" if r["value_m"] >= vm and r["effort"] < em else
                                             "Big bets" if r["value_m"] >= vm else
                                             "Fill-ins" if r["effort"] < em else "Hard slogs"), axis=1)
        QC = {"Quick wins": "#22D3EE", "Big bets": "#8B6CFF", "Fill-ins": "#9AA6CC", "Hard slogs": "#EC4899"}
        a, b, cc = st.columns(3)
        a.markdown(f'<div class="glass metric"><div class="v">${df["value_m"].sum():,.0f}M</div><div class="l">Total value</div></div>', unsafe_allow_html=True)
        b.markdown(f'<div class="glass metric"><div class="v">{int((df["quadrant"]=="Quick wins").sum())}</div><div class="l">Quick wins</div></div>', unsafe_allow_html=True)
        cc.markdown(f'<div class="glass metric"><div class="v">${df.loc[df["months_to_impact"]<=12,"value_m"].sum():,.0f}M</div><div class="l">Value ≤12 mo</div></div>', unsafe_allow_html=True)
        fig = go.Figure()
        for q, col in QC.items():
            sub = df[df["quadrant"] == q]
            if sub.empty:
                continue
            fig.add_trace(go.Scatter(x=sub["effort"], y=sub["value_m"], mode="markers+text", name=q,
                                     text=sub["initiative"], textposition="top center",
                                     marker=dict(size=sub["value_m"] / df["value_m"].max() * 45 + 12, color=col,
                                                 opacity=.85, line=dict(color="white", width=1))))
        fig.add_vline(x=em, line_dash="dash", line_color="rgba(255,255,255,.25)")
        fig.add_hline(y=vm, line_dash="dash", line_color="rgba(255,255,255,.25)")
        fig.update_layout(template="plotly_dark", height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_title="Effort →", yaxis_title="Value ($M) →", legend=dict(orientation="h", y=-0.2),
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, key="matrix")
        cum = df.sort_values("months_to_impact").copy()
        cum["cum"] = cum["value_m"].cumsum().round(1)
        st.dataframe(df[["initiative", "value_m", "effort", "months_to_impact", "quadrant"]],
                     use_container_width=True, hide_index=True)
        st.session_state["_vcp_df"] = df

else:
    top = max(levers, key=levers.get)
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">The plan lifts EBITDA from '
          f'<b>${start:,.0f}M</b> to <b>${target:,.0f}M</b> (+${total:,.0f}M, ~{margin_delta:,} bps), led by '
          f'<b>{top}</b> (${levers[top]}M). Cost levers are higher-confidence and front-loadable; price and mix '
          'need commercial proof; volume must be underwritten against real demand. Sequence the quick-win initiatives '
          'first to self-fund the program, then the big bets that carry the structural upside.</div>')
    csv = pd.DataFrame([{"Item": "Start EBITDA ($M)", "Value": round(start, 1)}]
                       + [{"Item": k, "Value": v} for k, v in levers.items()]
                       + [{"Item": "Target EBITDA ($M)", "Value": target}])
    st.download_button("⬇ Download EBITDA bridge (CSV)", csv.to_csv(index=False),
                       file_name="value_creation.csv", mime="text/csv")

st.caption("AI-assisted heuristic value-creation model. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
