import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Strategy Toolkit", page_icon="💡", layout="wide")
page_header("💡 Strategy Toolkit",
            "Three consultant's tools in one: structure a problem into a MECE issue tree, stress-test a business "
            "case with scenario & sensitivity analysis, and assemble a board-ready storyline. It structures your "
            "thinking — it does not invent facts.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

TREES = {
    "Grow revenue": {
        "Where to play": ["Which segments/geographies have the most attractive, winnable growth?",
                          "Are we under-penetrated in existing accounts (share of wallet)?",
                          "Which adjacencies extend the core credibly?"],
        "How to win": ["Is the value proposition differentiated and priced to value?",
                       "Is the route-to-market right for each segment?",
                       "Do sales coverage, capacity and incentives match the opportunity?"],
        "How to enable": ["Do we have the data, talent and ops to execute?",
                          "What is the investment case and payback by initiative?"]},
    "Reduce cost": {
        "Structural": ["Are spans and layers at best practice; where is the de-layering opportunity?",
                      "Is the operating model fit-for-purpose (centralize vs decentralize)?"],
        "Spend": ["Where is third-party/procurement spend addressable?",
                 "Which processes can be automated or simplified?"],
        "Footprint": ["Is the facilities/network footprint right-sized?",
                     "What is the phasing and one-time cost to capture savings?"]},
    "Enter a new market": {
        "Is it attractive?": ["How large, growing and profitable is the market?",
                             "What are regulatory, reimbursement and access barriers?"],
        "Can we win?": ["What is our right-to-win vs incumbents?",
                       "What entry mode fits (organic, partner, distributor, M&A)?"],
        "What does it take?": ["What is the go-to-market and investment plan?",
                              "What are the key risks and how do we de-risk entry?"]},
    "Evaluate an acquisition": {
        "Strategic rationale": ["Does the target strengthen where-to-play / how-to-win?",
                               "Is this the best use of capital vs alternatives?"],
        "Value": ["Is the standalone plan credible?",
                 "What are the cost and revenue synergies, net of integration cost and risk?"],
        "Deliverability": ["What are integration and culture risks?",
                          "What must be true on Day 1 for value capture?"]},
}

STAGES = ["① Issue Tree", "② Scenario & Sensitivity", "③ Executive Storyline"]
st.sidebar.header("Toolkit")
stage = st.sidebar.radio("Tool (controls adapt below)", STAGES, key="tk_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

# ---------------- TOOL 1: ISSUE TREE ----------------
if stage == STAGES[0]:
    archetype = st.sidebar.selectbox("Problem type", list(TREES.keys()))
    subject = st.sidebar.text_input("Company / business unit", "a global MedTech business")
    context = st.sidebar.text_area("Context (optional)", "Hardware-led, facing margin pressure and digital entrants.", height=90)
    st.markdown("### ① Issue Tree")
    glass(f'<div style="color:#9AA6CC;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em">Governing question</div>'
          f'<div style="font-family:Space Grotesk;font-size:1.15rem;color:#fff;margin-top:.3rem">How should {subject} {archetype.lower()}?</div>'
          + (f'<div style="color:#9AA6CC;font-size:.85rem;margin-top:.4rem">Context: {context}</div>' if context.strip() else ""))
    tree = TREES[archetype]
    cols = st.columns(len(tree))
    flat = []
    for col, (branch, qs) in zip(cols, tree.items()):
        with col:
            bullets = "".join(f'<div class="bullet">{x}</div>' for x in qs)
            glass(f'<div style="font-family:Space Grotesk;font-weight:600;color:#c4b5ff;margin-bottom:.3rem">{branch}</div>{bullets}')
            flat += [{"Branch": branch, "Hypothesis / question": x} for x in qs]
    st.download_button("⬇ Download issue tree (CSV)", pd.DataFrame(flat).to_csv(index=False),
                       file_name="issue_tree.csv", mime="text/csv")

# ---------------- TOOL 2: SCENARIO ----------------
elif stage == STAGES[1]:
    base = st.sidebar.number_input("Base outcome (e.g. EBITDA $M)", 1.0, 1_000_000.0, 100.0, step=5.0)
    n = st.sidebar.slider("Number of drivers", 2, 6, 4)
    st.markdown("### ② Scenario & Sensitivity")
    st.caption("Outcome = Base × ∏(1 + weight × swing). Set each driver's low/high % swing and weight.")
    defaults = [("Volume", -15, 20, 1.0), ("Price", -8, 10, 1.0), ("Cost inflation", -12, 6, 0.8),
                ("Mix", -6, 8, 0.6), ("FX", -5, 5, 0.4), ("Churn", -10, 5, 0.7)]
    drivers = []
    for i in range(n):
        nm0, lo0, hi0, w0 = defaults[i]
        with st.expander(f"Driver {i+1}: {nm0}", expanded=i < 2):
            c = st.columns(4)
            drivers.append({"name": c[0].text_input("Name", nm0, key=f"n{i}"),
                            "lo": c[1].number_input("Low %", -90, 0, lo0, key=f"lo{i}"),
                            "hi": c[2].number_input("High %", 0, 200, hi0, key=f"hi{i}"),
                            "w": c[3].slider("Weight", 0.0, 1.0, w0, key=f"w{i}")})
    downside = base * np.prod([1 + d["w"] * d["lo"] / 100 for d in drivers])
    upside = base * np.prod([1 + d["w"] * d["hi"] / 100 for d in drivers])
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="glass metric"><div class="v">${downside:,.0f}</div><div class="l">Downside</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="glass metric"><div class="v">${base:,.0f}</div><div class="l">Base</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass metric"><div class="v">${upside:,.0f}</div><div class="l">Upside</div></div>', unsafe_allow_html=True)
    rows = [{"name": d["name"], "low": base * (1 + d["w"] * d["lo"] / 100) - base,
             "high": base * (1 + d["w"] * d["hi"] / 100) - base} for d in drivers]
    rows.sort(key=lambda r: abs(r["high"] - r["low"]))
    fig = go.Figure()
    fig.add_trace(go.Bar(y=[r["name"] for r in rows], x=[r["low"] for r in rows], orientation="h", name="Low", marker_color="#EC4899"))
    fig.add_trace(go.Bar(y=[r["name"] for r in rows], x=[r["high"] for r in rows], orientation="h", name="High", marker_color="#22D3EE"))
    fig.update_layout(template="plotly_dark", height=320, barmode="overlay", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Δ outcome vs base", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True, key="tornado")
    top = max(rows, key=lambda r: abs(r["high"] - r["low"]))
    glass(f'<div style="color:#dfe5fb"><b>{top["name"]}</b> swings the outcome most — it deserves the tightest '
          'estimate and clearest mitigation.</div>')

# ---------------- TOOL 3: STORYLINE ----------------
else:
    sit = st.sidebar.text_area("Situation", "Grew 4% last year, below the 8% plan.", height=70)
    comp = st.sidebar.text_area("Complication", "Digital entrants are winning the mid-market; price is eroding.", height=70)
    ques = st.sidebar.text_input("Question", "How do we get back to double-digit growth?")
    rec = st.sidebar.text_area("Recommendation", "Refocus GTM on the mid-market with a digital-first model.", height=70)
    st.markdown("### ③ Executive Storyline")
    args = [("Sharpen where to play", "Mid-market is 60% of growth and under-served"),
            ("Fix how we win", "Shift to digital + inside sales lifts reach at lower cost"),
            ("Build to enable", "Re-skill the team and instrument the funnel")]
    glass(f'<div style="color:#9AA6CC;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em">Governing message</div>'
          f'<div style="font-family:Space Grotesk;font-size:1.2rem;color:#fff;font-weight:600;margin-top:.3rem">{rec}</div>')
    cS, cC = st.columns(2)
    with cS:
        glass(f'<div style="color:#c4b5ff;font-weight:600">Situation</div><div style="color:#dfe5fb;font-size:.9rem;margin-top:.2rem">{sit}</div>')
    with cC:
        glass(f'<div style="color:#c4b5ff;font-weight:600">Complication</div><div style="color:#dfe5fb;font-size:.9rem;margin-top:.2rem">{comp}</div>')
    glass(f'<div style="color:#c4b5ff;font-weight:600">Question</div><div style="color:#dfe5fb;font-size:.95rem;margin-top:.2rem">{ques}</div>')
    st.markdown("#### Because… (supporting pillars)")
    cols = st.columns(3)
    for col, (h, e) in zip(cols, args):
        with col:
            glass(f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff">{h}</div>'
                  f'<div style="color:#aab4d6;font-size:.85rem;margin-top:.3rem">{e}</div>')
    narrative = (f"Situation: {sit} Complication: {comp} Question: {ques} Recommendation: {rec} "
                 f"This holds because " + "; ".join(f"({i+1}) {h.lower()} — {e}" for i, (h, e) in enumerate(args)) + ".")
    with st.expander("📋 Copy the assembled narrative"):
        st.code(narrative, language=None)
        st.download_button("⬇ Download storyline (TXT)", narrative, file_name="executive_storyline.txt")

st.caption("Structuring tools built from your inputs (MECE issue tree · sensitivity model · SCQA/Pyramid). "
           f"They organize thinking; they do not assert facts. For a facilitated session: {PROFILE['email']}.")
