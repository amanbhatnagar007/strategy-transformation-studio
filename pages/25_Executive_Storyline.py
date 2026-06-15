import streamlit as st
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Executive Storyline", page_icon="📝", layout="wide")
page_header("📝 Executive Storyline Builder",
            "Turn your raw findings into a board-ready narrative using SCQA and the Pyramid Principle — "
            "governing message on top, grouped supporting arguments beneath. It structures your input; it doesn't invent.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Inputs (your facts)")
    situation = st.text_area("Situation (where we are)", "The business grew 4% last year, below the 8% plan.", height=80)
    complication = st.text_area("Complication (what changed)", "Digital entrants are winning the mid-market and price is eroding.", height=80)
    question = st.text_input("Question to answer", "How do we get back to double-digit growth?")
    recommendation = st.text_area("Recommendation (your answer)", "Refocus GTM on the mid-market with a digital-first model.", height=80)

st.markdown("##### Supporting arguments (3 is ideal)")
args = []
for i in range(3):
    c = st.columns([1, 2])
    head = c[0].text_input(f"Argument {i+1}", ["Sharpen where to play", "Fix how we win", "Build to enable"][i], key=f"h{i}")
    ev = c[1].text_input("Evidence / so-what", ["Mid-market is 60% of growth and under-served",
                                                "Shift to digital + inside sales lifts reach at lower cost",
                                                "Re-skill the team and instrument the funnel"][i], key=f"e{i}")
    if head.strip():
        args.append((head, ev))

st.markdown("### Your storyline")

glass(f'<div style="color:#9AA6CC;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em">Governing message</div>'
      f'<div style="font-family:Space Grotesk;font-size:1.2rem;color:#fff;font-weight:600;margin-top:.3rem">{recommendation}</div>')

cS, cC = st.columns(2)
with cS:
    glass(f'<div style="color:#c4b5ff;font-weight:600">Situation</div>'
          f'<div style="color:#dfe5fb;font-size:.9rem;margin-top:.2rem">{situation}</div>')
with cC:
    glass(f'<div style="color:#c4b5ff;font-weight:600">Complication</div>'
          f'<div style="color:#dfe5fb;font-size:.9rem;margin-top:.2rem">{complication}</div>')

glass(f'<div style="color:#c4b5ff;font-weight:600">Question</div>'
      f'<div style="color:#dfe5fb;font-size:.95rem;margin-top:.2rem">{question}</div>')

st.markdown("#### Because… (supporting pillars)")
cols = st.columns(max(1, len(args)))
for col, (head, ev) in zip(cols, args):
    with col:
        glass(f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff">{head}</div>'
              f'<div style="color:#aab4d6;font-size:.85rem;margin-top:.3rem">{ev}</div>')

# Assemble a copyable narrative from the user's own inputs
pillars = "; ".join(f"({i+1}) {h.lower()} — {e}" for i, (h, e) in enumerate(args))
narrative = (f"Situation: {situation} Complication: {complication} "
             f"Question: {question} Recommendation: {recommendation} "
             f"This holds because {pillars}.")
with st.expander("📋 Copy the assembled narrative"):
    st.code(narrative, language=None)
    st.download_button("⬇ Download storyline (TXT)", narrative, file_name="executive_storyline.txt")

st.caption("A structuring aid built entirely from your inputs (SCQA + Pyramid Principle) — it does not add facts. "
           f"For help crafting the board story: {PROFILE['email']}.")
