"""A named framework + logical 'thread' for each suite, so the subsections read as a
deliberate consulting sequence (not random tabs). Rendered as a banner under the header."""
import streamlit as st

# keyed by nav url
FRAMEWORKS = {
    "sales-force": {
        "name": "The SFE value chain",
        "thesis": "Coverage follows value — you can't size or pay a force until you know who's worth calling on.",
        "thread": ["Segment by value", "Target reach × frequency", "Size by workload", "Structure & align", "Incentivize on attainment", "Act on the call plan"]},
    "gtm-market-entry": {
        "name": "Where-to-play · How-to-win · Prove-it",
        "thesis": "Choose the route and the markets before you model the money.",
        "thread": ["Route-to-market", "Prioritize markets", "Prove the ROI", "Tell the story"]},
    "pricing-model": {
        "name": "Value-based pricing → model economics",
        "thesis": "Price to the value you create, then pick the model that monetizes it best.",
        "thread": ["Set the price corridor", "Compare business models", "Recommend"]},
    "synergy-deal": {
        "name": "Cost vs revenue synergies → capture",
        "thesis": "Credit cost synergies with confidence and revenue synergies with caution, then track capture vs plan.",
        "thread": ["Size synergies", "Phase to run-rate", "Track capture", "Decide"]},
    "target-screener": {
        "name": "Weighted-scorecard screening",
        "thesis": "Rank targets on what matters to the thesis, then test how easily the order flips.",
        "thread": ["Score & rank", "Map the portfolio", "Shortlist"]},
    "integration-separation": {
        "name": "Day-1 readiness → clean separation",
        "thesis": "Be market-ready on Day 1, then exit stranded cost and TSAs deliberately.",
        "thread": ["Day-1 readiness", "Carve-out & stranded cost", "Separation org", "Plan"]},
    "cost-org": {
        "name": "Spans-and-layers, then spend",
        "thesis": "Structural cost is the most durable pool — fix the org shape first, then the spend.",
        "thread": ["Cost takeout", "Spans & layers", "Redesign the org", "Summarize"]},
    "om-benchmark": {
        "name": "Operating-model diagnostic",
        "thesis": "Benchmark the structure to find where the org is too tall and too costly to run.",
        "thread": ["Actual vs benchmark", "Normalized scorecard", "Prioritize the gaps"]},
    "value-creation": {
        "name": "EBITDA bridge → initiative roadmap",
        "thesis": "Set the EBITDA target lever by lever, then sequence the initiatives that deliver it.",
        "thread": ["Build the EBITDA bridge", "Prioritize initiatives", "Sequence"]},
    "hcp-engagement": {
        "name": "Predict → prioritize → engage",
        "thesis": "Score churn risk by NPI, turn it into a tiered save play, then fund the channels that re-engage.",
        "thread": ["Predict churn (ML)", "Action by risk tier", "Optimize channel mix"]},
    "payer-reimbursement": {
        "name": "Contribution-margin lens",
        "thesis": "Follow the margin per CPT and per member to see where to renegotiate and where to invest.",
        "thread": ["Contract profitability", "Medicare Advantage value"]},
    "market-access": {
        "name": "TAM / SAM / SOM → forecast",
        "thesis": "Size top-down with explicit filters, then forecast the ramp under low/base/high scenarios.",
        "thread": ["Size the market", "Forecast adoption", "Summarize"]},
    "ai-agent": {
        "name": "Grounded retrieval (no hallucination)",
        "thesis": "Every answer is grounded only in Aman's real frameworks and engagements.",
        "thread": ["Ask", "Retrieve from the knowledge base", "Answer in frameworks"]},
    "strategy-toolkit": {
        "name": "Structure → stress-test → story",
        "thesis": "Frame the problem (MECE), pressure-test the case (sensitivity), then tell the story (SCQA).",
        "thread": ["Issue tree", "Scenario & sensitivity", "Executive storyline"]},
    "medtech-trends": {
        "name": "Trend → implication",
        "thesis": "Each trend is paired with the commercial implication a CXO has to act on.",
        "thread": ["Explore trends", "Read the implications"]},
}


def framework_banner(key):
    fw = FRAMEWORKS.get(key)
    if not fw:
        return
    thread = '  <span style="color:#6f7aa0">→</span>  '.join(
        f'<span style="color:#9beaf6">{s}</span>' for s in fw["thread"])
    st.markdown(
        f'<div class="glass" style="margin:.4rem 0 .9rem;border-left:3px solid #8B6CFF;padding:.8rem 1rem">'
        f'<span style="color:#8B6CFF;font-size:.7rem;font-weight:600;letter-spacing:.09em">FRAMEWORK · {fw["name"].upper()}</span>'
        f'<div style="color:#dfe5fb;font-size:.92rem;margin:.3rem 0 .45rem;line-height:1.5">{fw["thesis"]}</div>'
        f'<div style="font-family:Space Grotesk;font-size:.82rem">{thread}</div></div>',
        unsafe_allow_html=True)
