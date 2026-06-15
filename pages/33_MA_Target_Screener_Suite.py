import streamlit as st
import pandas as pd
import plotly.express as px
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.frameworks import framework_banner
from lib.uploads import ColumnSchema, Col, data_input
from lib.ma_suite import TARGET_CRITERIA, demo_targets, score_targets

st.set_page_config(page_title="M&A Target Screener", page_icon="🔎", layout="wide")
page_header("🔎 M&A Target Screener",
            "Upload a target universe and rank it on a weighted scorecard — strategic fit, financials, synergy, "
            "integration risk and market position — then map the portfolio to pick where to focus.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)
framework_banner("target-screener")

schema = ColumnSchema([
    Col("target", "text", "Target name — REQUIRED to action the shortlist", "Alpha Diagnostics", required=True),
    Col("strategic_fit", "num", "Strategic fit score (0-100)", "88", required=True),
    Col("financial", "num", "Financial health (0-100)", "72", required=True),
    Col("synergy", "num", "Synergy potential (0-100)", "80", required=True),
    Col("risk", "num", "Integration risk (0-100, higher = worse)", "30", required=True),
    Col("market", "num", "Market position (0-100)", "75", required=True),
])
st.markdown("#### Load your target universe")
df_raw = data_input(schema, demo_targets(), demo_label="Use demo targets", key="targets")
if df_raw is None or df_raw.empty:
    st.stop()

P = st.session_state.setdefault("scr_params",
                                {"w_fit": 8, "w_fin": 6, "w_syn": 7, "w_risk": 5, "w_mkt": 6})

STAGES = ["① Score & Rank", "② Portfolio Map", "📋 Summary"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls adapt below)", STAGES, key="scr_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

if stage in (STAGES[0], STAGES[1]):
    st.sidebar.caption("Criteria weights (normalized to 100%).")
    P["w_fit"] = st.sidebar.slider("Strategic fit", 0, 10, P["w_fit"])
    P["w_fin"] = st.sidebar.slider("Financial health", 0, 10, P["w_fin"])
    P["w_syn"] = st.sidebar.slider("Synergy potential", 0, 10, P["w_syn"])
    P["w_risk"] = st.sidebar.slider("Integration risk (inverse)", 0, 10, P["w_risk"])
    P["w_mkt"] = st.sidebar.slider("Market position", 0, 10, P["w_mkt"])

raw = {"strategic_fit": P["w_fit"], "financial": P["w_fin"], "synergy": P["w_syn"], "risk": P["w_risk"], "market": P["w_mkt"]}
wsum = sum(raw.values()) or 1
weights = {k: v / wsum for k, v in raw.items()}
scored = score_targets(df_raw, weights)
top = scored.iloc[0]

if stage == STAGES[2]:
    locked_panel([("Top target", str(top["target"])), ("Score", f"{top['Weighted score']:.1f}"),
                  ("Screened", f"{len(scored)}")])

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v" style="font-size:1.1rem">{top["target"]}</div><div class="l">Top-ranked target</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{top["Weighted score"]:.1f}</div><div class="l">Top weighted score</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{len(scored)}</div><div class="l">Targets screened</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    show = scored.rename(columns={**TARGET_CRITERIA, "target": "Target"})
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download ranked shortlist (CSV)", show.to_csv(index=False),
                       file_name="ma_target_ranking.csv", mime="text/csv")

elif stage == STAGES[1]:
    st.caption("Bubble = target. X: strategic fit · Y: synergy potential · size: financial health · color: weighted score.")
    fig = px.scatter(scored, x="strategic_fit", y="synergy", size="financial", color="Weighted score",
                     text="target", color_continuous_scale=["#6B7393", "#8B6CFF", "#22D3EE"], size_max=40, height=440)
    fig.update_traces(textposition="top center", textfont=dict(size=10, color="#cdd6f5"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="Strategic fit →", yaxis_title="Synergy potential →", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="map")

else:
    runner = scored.iloc[1]["target"] if len(scored) > 1 else "—"
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">On the current weighting, '
          f'<b>{top["target"]}</b> ranks first ({top["Weighted score"]:.1f}/100), ahead of <b>{runner}</b>. '
          f'It leads on the criteria you weighted most heavily. Prioritize diligence on the top 2–3, and re-run '
          f'the weights to test how sensitive the ranking is — if the order flips easily, the thesis needs sharpening '
          f'before committing resources. Integration-risk scores enter inverted, so a high-fit/high-risk target '
          f'should carry an explicit integration plan before it advances.</div>')

st.caption("AI-assisted weighted-scorecard screening. Directional — scores are your inputs, not a valuation. "
           f"For deal origination & screening: {PROFILE['email']}.")
