import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Operating Model Benchmark", page_icon="📐", layout="wide")
page_header("📐 Operating Model Benchmark",
            "Benchmark an operating model against best-practice ranges — SG&A intensity, span of control, "
            "layers, productivity and support ratios — and see where the structural gaps are.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Your operating model")
    sga_pct = st.slider("SG&A (% of revenue)", 5.0, 45.0, 22.0, 0.5)
    span = st.slider("Average span of control", 2.0, 12.0, 5.0, 0.5)
    layers = st.slider("Management layers (CEO → front line)", 4, 14, 9)
    rev_per_fte = st.number_input("Revenue per FTE ($k)", 50, 2000, 240, step=10)
    support_ratio = st.slider("Support-to-front-line ratio (%)", 5.0, 50.0, 28.0, 0.5,
                              help="Support/overhead FTEs as a % of front-line FTEs. Lower is leaner.")

# Benchmark ranges (best, acceptable_limit) — direction-aware.
# For "higher is better" dims (span, rev/fte) best is high; for "lower is better" best is low.
DIMS = [
    {"name": "SG&A % of revenue", "actual": sga_pct, "best": 12.0, "limit": 28.0,
     "lower_better": True, "unit": "%"},
    {"name": "Span of control", "actual": span, "best": 8.0, "limit": 4.0,
     "lower_better": False, "unit": "×"},
    {"name": "Management layers", "actual": float(layers), "best": 5.0, "limit": 9.0,
     "lower_better": True, "unit": ""},
    {"name": "Revenue per FTE ($k)", "actual": float(rev_per_fte), "best": 400.0, "limit": 180.0,
     "lower_better": False, "unit": "k"},
    {"name": "Support-to-front ratio %", "actual": support_ratio, "best": 15.0, "limit": 32.0,
     "lower_better": True, "unit": "%"},
]

def score_dim(d):
    """0-100: 100 = at/beyond best practice, 0 = at/worse than acceptable limit."""
    best, limit, a = d["best"], d["limit"], d["actual"]
    if d["lower_better"]:
        if a <= best:
            s = 100.0
        elif a >= limit:
            s = 0.0
        else:
            s = (limit - a) / (limit - best) * 100.0
    else:
        if a >= best:
            s = 100.0
        elif a <= limit:
            s = 0.0
        else:
            s = (a - limit) / (best - limit) * 100.0
    return round(max(0.0, min(100.0, s)))

for d in DIMS:
    d["score"] = score_dim(d)
    # gap toward best practice (signed, in native units)
    d["gap"] = round(d["actual"] - d["best"], 1)

overall = round(sum(d["score"] for d in DIMS) / len(DIMS))
worst = min(DIMS, key=lambda d: d["score"])

k1, k2 = st.columns(2)
k1.markdown(f'<div class="glass metric"><div class="v">{overall}/100</div><div class="l">Overall OM score</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{worst["name"].split(" (")[0]}</div><div class="l">Biggest gap</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📊 Actual vs benchmark", "🕸️ Scorecard", "📋 Executive summary"])

with t1:
    st.markdown("#### Each dimension vs best-practice")
    names = [d["name"] for d in DIMS]
    actuals = [d["actual"] for d in DIMS]
    bests = [d["best"] for d in DIMS]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Your model", x=names, y=actuals, marker_color="#8B6CFF",
                         text=[f"{v:g}" for v in actuals], textposition="outside"))
    fig.add_trace(go.Bar(name="Best practice", x=names, y=bests, marker_color="#22D3EE",
                         text=[f"{v:g}" for v in bests], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=360, barmode="group",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", y=-0.25), margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">Raw values use different units, so compare each bar to its '
          'own best-practice marker. The normalized 0–100 score in the Scorecard tab makes dimensions comparable. '
          'Benchmark ranges are directional, generic best-practice bands — not industry-specific quartiles.</div>')

with t2:
    st.markdown("#### Normalized scorecard (0–100, higher is better)")
    scores = [d["score"] for d in DIMS]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=scores + [scores[0]], theta=names + [names[0]],
                                  fill="toself", line_color="#8B6CFF", name="Score"))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      polar=dict(radialaxis=dict(range=[0, 100], visible=True)),
                      margin=dict(l=40, r=40, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
    df = pd.DataFrame([{"Dimension": d["name"], "Your value": d["actual"],
                        "Best practice": d["best"], "Acceptable limit": d["limit"],
                        "Score (0-100)": d["score"]} for d in DIMS])
    st.dataframe(df, use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    ranked = sorted(DIMS, key=lambda d: d["score"])
    top3 = ranked[:3]
    areas = "; ".join(f"{d['name']} (score {d['score']})" for d in top3)
    summary = (
        f"The operating model scores <b>{overall}/100</b> against best-practice benchmarks. "
        f"The biggest improvement areas are: <b>{areas}</b>. "
        f"Prioritize the lowest-scoring dimensions first — these typically signal an organization that is "
        f"too tall and too costly to run. Structural moves (widening spans, removing layers) usually unlock "
        f"the SG&A and support-ratio gaps simultaneously. These scores are directional heuristics based on "
        f"generic best-practice bands; calibrate the ranges to your sector before setting hard targets."
    )
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{summary}</div>')
    csv = pd.DataFrame([{"Dimension": d["name"], "Your value": d["actual"],
                         "Best practice": d["best"], "Acceptable limit": d["limit"],
                         "Score (0-100)": d["score"]} for d in DIMS] +
                       [{"Dimension": "OVERALL", "Your value": "", "Best practice": "",
                         "Acceptable limit": "", "Score (0-100)": overall}])
    st.download_button("⬇ Download benchmark scorecard (CSV)", csv.to_csv(index=False),
                       file_name="operating_model_benchmark.csv", mime="text/csv")

st.caption("AI-assisted heuristic benchmark for operating-model framing. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
