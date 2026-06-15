import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE

st.set_page_config(page_title="Operating Model Benchmark", page_icon="📐", layout="wide")
page_header("📐 Operating Model Benchmark",
            "Benchmark an operating model against best-practice ranges — SG&A intensity, span, layers, "
            "productivity and support ratios — and see where the structural gaps are.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

P = st.session_state.setdefault("omb_params", {
    "sga_pct": 22.0, "span": 5.0, "layers": 9, "rev_per_fte": 240, "support_ratio": 28.0})

STAGES = ["① Actual vs Benchmark", "② Scorecard", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="omb_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")


def build_dims(P):
    DIMS = [
        {"name": "SG&A % of revenue", "actual": P["sga_pct"], "best": 12.0, "limit": 28.0, "lower_better": True},
        {"name": "Span of control", "actual": P["span"], "best": 8.0, "limit": 4.0, "lower_better": False},
        {"name": "Management layers", "actual": float(P["layers"]), "best": 5.0, "limit": 9.0, "lower_better": True},
        {"name": "Revenue per FTE ($k)", "actual": float(P["rev_per_fte"]), "best": 400.0, "limit": 180.0, "lower_better": False},
        {"name": "Support-to-front ratio %", "actual": P["support_ratio"], "best": 15.0, "limit": 32.0, "lower_better": True},
    ]
    for d in DIMS:
        best, limit, a = d["best"], d["limit"], d["actual"]
        if d["lower_better"]:
            s = 100.0 if a <= best else (0.0 if a >= limit else (limit - a) / (limit - best) * 100.0)
        else:
            s = 100.0 if a >= best else (0.0 if a <= limit else (a - limit) / (best - limit) * 100.0)
        d["score"] = round(max(0.0, min(100.0, s)))
    return DIMS


if stage in (STAGES[0], STAGES[1]):
    P["sga_pct"] = st.sidebar.slider("SG&A (% of revenue)", 5.0, 45.0, P["sga_pct"], 0.5)
    P["span"] = st.sidebar.slider("Average span of control", 2.0, 12.0, P["span"], 0.5)
    P["layers"] = st.sidebar.slider("Management layers", 4, 14, P["layers"])
    P["rev_per_fte"] = st.sidebar.number_input("Revenue per FTE ($k)", 50, 2000, P["rev_per_fte"], step=10)
    P["support_ratio"] = st.sidebar.slider("Support-to-front-line ratio (%)", 5.0, 50.0, P["support_ratio"], 0.5)

DIMS = build_dims(P)
overall = round(sum(d["score"] for d in DIMS) / len(DIMS))
worst = min(DIMS, key=lambda d: d["score"])
if stage == STAGES[2]:
    locked_panel([("Overall score", f"{overall}/100"), ("Biggest gap", worst["name"].split(" (")[0])])

k1, k2 = st.columns(2)
k1.markdown(f'<div class="glass metric"><div class="v">{overall}/100</div><div class="l">Overall OM score</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v" style="font-size:1.0rem">{worst["name"].split(" (")[0]}</div><div class="l">Biggest gap</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")
names = [d["name"] for d in DIMS]

if stage == STAGES[0]:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your model", x=names, y=[d["actual"] for d in DIMS], marker_color="#8B6CFF",
                         text=[f"{d['actual']:g}" for d in DIMS], textposition="outside"))
    fig.add_trace(go.Bar(name="Best practice", x=names, y=[d["best"] for d in DIMS], marker_color="#22D3EE",
                         text=[f"{d['best']:g}" for d in DIMS], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=360, barmode="group", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-0.25), margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="bench")
    glass('<div style="color:#aab4d6;font-size:.85rem">Units differ — compare each bar to its own best-practice '
          'marker; the normalized 0–100 scorecard makes dimensions comparable. Bands are generic best-practice, not sector quartiles.</div>')

elif stage == STAGES[1]:
    scores = [d["score"] for d in DIMS]
    fig = go.Figure(go.Scatterpolar(r=scores + [scores[0]], theta=names + [names[0]], fill="toself", line_color="#8B6CFF"))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      polar=dict(radialaxis=dict(range=[0, 100], visible=True)), margin=dict(l=40, r=40, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, key="radar")
    st.dataframe(pd.DataFrame([{"Dimension": d["name"], "Your value": d["actual"], "Best practice": d["best"],
                                "Acceptable limit": d["limit"], "Score (0-100)": d["score"]} for d in DIMS]),
                 use_container_width=True, hide_index=True)

else:
    top3 = sorted(DIMS, key=lambda d: d["score"])[:3]
    areas = "; ".join(f"{d['name']} (score {d['score']})" for d in top3)
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">The operating model scores '
          f'<b>{overall}/100</b> against best-practice. The biggest improvement areas are <b>{areas}</b>. '
          'Prioritize the lowest-scoring dimensions — they typically signal an organization that is too tall and '
          'too costly. Widening spans and removing layers usually closes the SG&A and support-ratio gaps together. '
          'Calibrate the bands to your sector before setting hard targets.</div>')
    st.download_button("⬇ Download scorecard (CSV)",
                       pd.DataFrame([{"Dimension": d["name"], "Your value": d["actual"], "Score": d["score"]} for d in DIMS]
                                    + [{"Dimension": "OVERALL", "Your value": "", "Score": overall}]).to_csv(index=False),
                       file_name="om_benchmark.csv", mime="text/csv")

st.caption("AI-assisted heuristic benchmark for operating-model framing. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
