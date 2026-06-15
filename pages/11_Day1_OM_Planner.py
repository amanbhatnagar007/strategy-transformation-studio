import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Day-1 OM Planner", page_icon="🗂️", layout="wide")
page_header("🗂️ Day-1 Commercial Operating Model Planner",
            "Track Day-1 readiness across the commercial operating model — workstream by workstream — with "
            "RAG status, a weighted readiness score and a go-live confidence call. The discipline behind a "
            "$3B business separation that went market-ready in 9 months.")
st.page_link("Home.py", label="← Back to Studio")

# workstream -> (default completion %, relative weight)
WORKSTREAMS = {
    "Sales": 6,
    "Marketing": 4,
    "Customer service": 4,
    "Pricing / contracts": 7,
    "IT / CRM": 7,
    "Supply": 6,
    "People / org": 5,
    "Legal / compliance": 6,
}
DEFAULTS = {"Sales": 75, "Marketing": 60, "Customer service": 55, "Pricing / contracts": 45,
            "IT / CRM": 40, "Supply": 70, "People / org": 80, "Legal / compliance": 65}

with st.sidebar:
    st.header("Workstream completion %")
    st.caption("Where each workstream stands against its Day-1 checklist.")
    completion = {}
    for ws in WORKSTREAMS:
        completion[ws] = st.slider(ws, 0, 100, DEFAULTS[ws], key=f"ws_{ws}")
    st.header("Go-live")
    target_days = st.number_input("Days to planned Day-1", 1, 365, 90, step=5)


def rag(pct):
    if pct < 50:
        return "🔴 Red"
    if pct < 80:
        return "🟠 Amber"
    return "🟢 Green"


RAG_COLOR = {"🔴 Red": "#F87171", "🟠 Amber": "#FBBF24", "🟢 Green": "#34D399"}

wsum = sum(WORKSTREAMS.values())
rows = []
for ws, w in WORKSTREAMS.items():
    pct = completion[ws]
    rows.append({"Workstream": ws, "Completion %": pct, "Weight %": round(w / wsum * 100, 1),
                 "RAG": rag(pct)})
df = pd.DataFrame(rows)

overall = round(sum(completion[ws] * w for ws, w in WORKSTREAMS.items()) / wsum, 1)
n_red = int((df["RAG"] == "🔴 Red").sum())
n_amber = int((df["RAG"] == "🟠 Amber").sum())
# crude days-to-ready: scale the remaining gap, penalize red workstreams
gap = 100 - overall
days_to_ready = round(target_days * (gap / 100) * (1 + 0.25 * n_red))

if overall >= 80 and n_red == 0:
    confidence = "High"
elif overall >= 65 and n_red <= 1:
    confidence = "Moderate"
else:
    confidence = "Low"

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{overall:.0f}%</div><div class="l">Overall readiness</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{n_red}</div><div class="l">Red workstreams</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">~{days_to_ready}</div><div class="l">Days to ready (est.)</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{confidence}</div><div class="l">Go-live confidence</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["📊 Readiness by workstream", "🚧 Gaps", "📋 Executive summary"])

with t1:
    st.markdown("#### Day-1 readiness by workstream (RAG)")
    fig = go.Figure(go.Bar(
        x=df["Completion %"], y=df["Workstream"], orientation="h",
        marker_color=[RAG_COLOR[r] for r in df["RAG"]],
        text=[f"{p}%" for p in df["Completion %"]], textposition="outside"))
    fig.add_vline(x=50, line_dash="dot", line_color="#F87171", opacity=.5)
    fig.add_vline(x=80, line_dash="dot", line_color="#34D399", opacity=.5)
    fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Completion %",
                      xaxis_range=[0, 110], yaxis=dict(autorange="reversed"),
                      margin=dict(l=10, r=30, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

with t2:
    st.markdown("#### Workstreams needing attention before Day-1")
    gaps = df[df["RAG"] != "🟢 Green"].sort_values("Completion %")
    if gaps.empty:
        glass('<div style="color:#34D399;font-weight:600">All workstreams green — operating model is Day-1 ready on current inputs.</div>')
    else:
        bullets = "".join(
            f'<div class="bullet"><b>{r["Workstream"]}</b> — {r["RAG"].split()[1]} at {r["Completion %"]}% '
            f'(weight {r["Weight %"]}%). {"Critical path — escalate." if r["RAG"]=="🔴 Red" else "Monitor and close remaining items."}</div>'
            for _, r in gaps.iterrows())
        glass(f'<div style="font-weight:600;color:#fff;margin-bottom:.3rem">{len(gaps)} workstream(s) below green</div>{bullets}')

with t3:
    st.markdown("#### Board-ready read")
    reds = ", ".join(df[df["RAG"] == "🔴 Red"]["Workstream"]) or "none"
    summary = (
        f"The commercial operating model is <b>{overall:.0f}% Day-1 ready</b> on a weighted basis, with "
        f"<b>{n_red} red</b> and {n_amber} amber workstream(s) against a planned Day-1 in {target_days} days. "
        f"Go-live confidence is <b>{confidence}</b>. "
        f"{'Critical-path workstreams (' + reds + ') are below 50% and must be escalated now.' if n_red else 'No workstream is in the red zone.'} "
        f"On current burn-down, an estimated <b>~{days_to_ready} days</b> of focused effort remain to reach a "
        "green operating model. Readiness percentages are directional self-assessments — pair them with a "
        "checklist audit before committing to a Day-1 go-live date."
    )
    glass(f"<div style='font-size:.98rem;line-height:1.7;color:#dfe5fb'>{summary}</div>")
    st.download_button("⬇ Download readiness tracker (CSV)", df.to_csv(index=False),
                       file_name="day1_readiness.csv", mime="text/csv")

st.caption("AI-assisted heuristic readiness model for separation / Day-1 planning. Directional, not "
           f"investment advice. For deal support: {PROFILE['email']}.")
