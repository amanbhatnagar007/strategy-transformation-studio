import streamlit as st
import pandas as pd
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Hypothesis Generator", page_icon="💡", layout="wide")
page_header("💡 Strategy Hypothesis Generator",
            "Turn a fuzzy business question into a MECE issue tree — the structured hypotheses an MBB team would "
            "test first. Pick the problem type and tailor it to your situation.")
st.page_link("Home.py", label="← Back to Studio")

# Deterministic issue-tree templates by problem archetype (no fabricated facts —
# these are the analytical questions to investigate).
TREES = {
    "Grow revenue": {
        "Where to play": ["Which segments/geographies have the most attractive, winnable growth?",
                          "Are we under-penetrated in existing accounts (share of wallet)?",
                          "Which adjacencies extend the core credibly?"],
        "How to win": ["Is the value proposition differentiated and priced to value?",
                       "Is the route-to-market (direct/indirect/digital) right for each segment?",
                       "Do sales coverage, capacity and incentives match the opportunity?"],
        "How to enable": ["Do we have the data, talent and ops to execute?",
                          "What is the investment case and payback by initiative?"],
    },
    "Reduce cost": {
        "Structural": ["Are spans and layers at best practice; where is the de-layering opportunity?",
                      "Is the operating model fit-for-purpose (centralize vs decentralize)?"],
        "Spend": ["Where is third-party/procurement spend addressable?",
                 "Which processes can be automated or simplified?"],
        "Footprint": ["Is the facilities/network footprint right-sized?",
                     "What is the phasing and one-time cost to capture savings?"],
    },
    "Enter a new market": {
        "Is it attractive?": ["How large, growing and profitable is the market?",
                             "What are regulatory, reimbursement and access barriers?"],
        "Can we win?": ["What is our right-to-win vs incumbents?",
                       "What entry mode fits (organic, partner, distributor, M&A)?"],
        "What does it take?": ["What is the go-to-market and investment plan?",
                              "What are the key risks and how do we de-risk entry?"],
    },
    "Evaluate an acquisition": {
        "Strategic rationale": ["Does the target strengthen where-to-play / how-to-win?",
                               "Is this the best use of capital vs alternatives?"],
        "Value": ["Is the standalone plan credible (market, share, margins)?",
                 "What are the cost and revenue synergies, net of integration cost and risk?"],
        "Deliverability": ["What are integration and culture risks?",
                          "What must be true on Day 1 for value capture?"],
    },
    "Improve pricing": {
        "Willingness to pay": ["What value do we create and for whom?",
                              "How price-sensitive is demand by segment?"],
        "Price architecture": ["Are model and metric right (capital vs subscription vs pay-per-use)?",
                              "Is there value leakage in discounts and terms?"],
        "Execution": ["Do reps have the tools and incentives to hold price?",
                     "How will competitors and customers respond?"],
    },
}

with st.sidebar:
    st.header("Frame the problem")
    archetype = st.selectbox("Problem type", list(TREES.keys()))
    subject = st.text_input("Company / business unit", "a global MedTech business")
    context = st.text_area("Context (optional)", "Hardware-led, facing margin pressure and new digital entrants.",
                           height=100)

q = f"How should {subject} {archetype.lower()}?"
st.markdown(f'#### Governing question')
glass(f'<div style="font-size:1.05rem;color:#fff;font-family:Space Grotesk">{q}</div>'
      + (f'<div style="color:#9AA6CC;font-size:.85rem;margin-top:.4rem">Context: {context}</div>' if context.strip() else ""))

st.markdown("#### MECE issue tree — hypotheses to test")
tree = TREES[archetype]
cols = st.columns(len(tree))
flat = []
for col, (branch, qs) in zip(cols, tree.items()):
    with col:
        bullets = "".join(f'<div class="bullet">{x}</div>' for x in qs)
        glass(f'<div style="font-family:Space Grotesk;font-weight:600;color:#c4b5ff;margin-bottom:.3rem">{branch}</div>{bullets}')
        for x in qs:
            flat.append({"Branch": branch, "Hypothesis / question to test": x})

st.markdown("#### Suggested next steps")
glass('<div class="bullet">Prioritize 2–3 branches by likely value and feasibility.</div>'
      '<div class="bullet">For each, state the hypothesis as a testable statement and the data needed.</div>'
      '<div class="bullet">Run a quick fact-base to confirm/kill, then deep-dive the survivors.</div>')

st.download_button("⬇ Download issue tree (CSV)", pd.DataFrame(flat).to_csv(index=False),
                   file_name="issue_tree.csv", mime="text/csv")
st.caption("A structuring tool — it organizes the questions to investigate; it does not assert answers. "
           f"For a facilitated problem-structuring session: {PROFILE['email']}.")
