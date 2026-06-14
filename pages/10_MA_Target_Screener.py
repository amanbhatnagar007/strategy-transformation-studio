import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="M&A Target Screener", page_icon="🔎", layout="wide")
page_header("🔎 M&A Target Screener",
            "Rank acquisition targets on a weighted scorecard — strategic fit, financial health, synergy "
            "potential, integration risk and market position — to focus diligence on the deals that matter.")
st.page_link("Home.py", label="← Back to Studio")

CRITERIA = {
    "strategic_fit": "Strategic fit",
    "financial": "Financial health",
    "synergy": "Synergy potential",
    "risk": "Cultural / integration risk",
    "market": "Market position",
}
# risk is scored 0-100 where high = more risk; it enters the score INVERTED.

with st.sidebar:
    st.header("Criteria weights")
    st.caption("Relative importance — normalized to 100%.")
    w_fit = st.slider("Strategic fit", 0, 10, 8)
    w_fin = st.slider("Financial health", 0, 10, 6)
    w_syn = st.slider("Synergy potential", 0, 10, 7)
    w_risk = st.slider("Integration risk (inverse)", 0, 10, 5)
    w_mkt = st.slider("Market position", 0, 10, 6)

raw_weights = {"strategic_fit": w_fit, "financial": w_fin, "synergy": w_syn,
               "risk": w_risk, "market": w_mkt}
wsum = sum(raw_weights.values()) or 1
weights = {k: v / wsum for k, v in raw_weights.items()}

demo_rows = [
    {"target": "Alpha Diagnostics", "strategic_fit": 88, "financial": 72, "synergy": 80, "risk": 30, "market": 75},
    {"target": "Beta Therapeutics", "strategic_fit": 70, "financial": 85, "synergy": 60, "risk": 45, "market": 82},
    {"target": "Gamma Devices",     "strategic_fit": 92, "financial": 55, "synergy": 88, "risk": 60, "market": 50},
    {"target": "Delta Health IT",   "strategic_fit": 65, "financial": 78, "synergy": 72, "risk": 25, "market": 68},
    {"target": "Epsilon Care",      "strategic_fit": 80, "financial": 60, "synergy": 55, "risk": 70, "market": 45},
    {"target": "Zeta Pharma Svcs",  "strategic_fit": 58, "financial": 90, "synergy": 65, "risk": 35, "market": 88},
]

schema = ColumnSchema([
    Col("target", "text", "Target name", "Alpha Diagnostics"),
    Col("strategic_fit", "num", "Strategic fit score (0-100)", "88"),
    Col("financial", "num", "Financial health score (0-100)", "72"),
    Col("synergy", "num", "Synergy potential score (0-100)", "80"),
    Col("risk", "num", "Cultural/integration risk (0-100, higher = worse)", "30"),
    Col("market", "num", "Market position score (0-100)", "75"),
])


def score_targets(df):
    d = df.copy()
    for c in CRITERIA:
        d[c] = d[c].clip(0, 100)
    d["Weighted score"] = (
        d["strategic_fit"] * weights["strategic_fit"]
        + d["financial"] * weights["financial"]
        + d["synergy"] * weights["synergy"]
        + (100 - d["risk"]) * weights["risk"]
        + d["market"] * weights["market"]
    ).round(1)
    d = d.sort_values("Weighted score", ascending=False).reset_index(drop=True)
    d.insert(0, "Rank", range(1, len(d) + 1))
    return d


t1, tU, t2 = st.tabs(["🏆 Ranking", "📤 Upload your data", "📋 Executive summary"])


def render(df, src):
    scored = score_targets(df)
    top = scored.iloc[0]
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="glass metric"><div class="v">{top["target"]}</div><div class="l">Top-ranked target</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="glass metric"><div class="v">{top["Weighted score"]:.1f}</div><div class="l">Top weighted score</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass metric"><div class="v">{len(scored)}</div><div class="l">Targets screened</div></div>', unsafe_allow_html=True)

    fig = go.Figure(go.Scatter(
        x=scored["strategic_fit"], y=scored["synergy"], mode="markers+text",
        text=scored["target"], textposition="top center",
        marker=dict(size=scored["financial"] / 2 + 8, color=scored["Weighted score"],
                    colorscale=[[0, "#22D3EE"], [1, "#8B6CFF"]], showscale=True,
                    colorbar=dict(title="Score"), line=dict(width=1, color="rgba(255,255,255,.3)")),
        hovertemplate="%{text}<br>Fit %{x} · Synergy %{y}<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=420, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Strategic fit",
                      yaxis_title="Synergy potential", margin=dict(l=10, r=10, t=30, b=10),
                      title="Bubble size = financial health · color = weighted score")
    st.plotly_chart(fig, use_container_width=True)

    show = scored.rename(columns={**CRITERIA, "target": "Target"})
    st.dataframe(show, use_container_width=True, hide_index=True)
    return scored


with t1:
    st.markdown("#### Weighted scorecard ranking")
    wtxt = " · ".join(f"{CRITERIA[k]} {v*100:.0f}%" for k, v in weights.items())
    glass(f'<div style="color:#aab4d6;font-size:.85rem">Active weights: {wtxt}</div>')
    scored_demo = render(pd.DataFrame(demo_rows), "demo")

with tU:
    st.markdown("#### Screen your own pipeline")
    st.caption("Each criterion is 0-100. Integration risk is scored where higher means worse — it is "
               "inverted in the weighted score. Only the rows you provide are analyzed.")
    user_df = data_input(schema, demo_rows, key="targets")
    if user_df is not None and not user_df.empty:
        render(user_df, "user")

with t2:
    st.markdown("#### Board-ready read")
    s = scored_demo
    top, second = s.iloc[0], s.iloc[1] if len(s) > 1 else s.iloc[0]
    lead = round(top["Weighted score"] - second["Weighted score"], 1)
    verdict = ("a clear front-runner" if lead > 8 else "narrowly ahead" if lead > 2 else "effectively tied with the field")
    summary = (
        f"On the active weighting (top criterion: <b>{CRITERIA[max(weights, key=weights.get)]}</b>), "
        f"<b>{top['target']}</b> ranks #1 with a weighted score of <b>{top['Weighted score']:.1f}</b>, "
        f"{verdict} versus {second['target']} ({second['Weighted score']:.1f}, a {lead}-point gap). "
        f"Its profile: fit {int(top['strategic_fit'])}, synergy {int(top['synergy'])}, financial "
        f"{int(top['financial'])}, market {int(top['market'])}, integration risk {int(top['risk'])}/100. "
        "Scores are directional inputs to focus diligence — reweight the criteria in the sidebar to "
        "stress-test the ranking against the investment thesis before committing diligence spend."
    )
    glass(f"<div style='font-size:.98rem;line-height:1.7;color:#dfe5fb'>{summary}</div>")
    st.download_button("⬇ Download ranked scorecard (CSV)",
                       s.rename(columns={**CRITERIA, "target": "Target"}).to_csv(index=False),
                       file_name="ma_target_scorecard.csv", mime="text/csv")

st.caption("AI-assisted heuristic scorecard for target screening. Directional, not investment advice. "
           f"For deal support: {PROFILE['email']}.")
