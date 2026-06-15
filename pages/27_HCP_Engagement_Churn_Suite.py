import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.frameworks import framework_banner
from lib.uploads import ColumnSchema, Col, data_input
from lib.churn_model import train, FEATURES, LABELS
from lib.hcp_suite import (demo_panel, score_panel, risk_tier, optimize_mix, DEFAULT_CHANNELS)

st.set_page_config(page_title="HCP Engagement & Churn Suite", page_icon="🩺", layout="wide")
page_header("🩺 HCP Engagement & Churn Suite",
            "Predict which prescribers (by NPI) are at risk of reducing volume, turn the scores into an action "
            "plan by risk tier, and optimize the omni-channel mix that re-engages them.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)
framework_banner("hcp-engagement")

@st.cache_resource(show_spinner="Training the churn model…")
def get_model():
    return train()
model, _train_df, auc, importances = get_model()

# ---------------- Upload: prescriber panel (NPI required) ----------------
schema = ColumnSchema([
    Col("hcp_id", "text", "NPI or HCP identifier — REQUIRED so at-risk HCPs can be actioned by name", "1234567890", required=True),
    Col("rx_trend", "num", "Rx volume trend % (needs ≥2 periods; declining = risk)", "-8", required=True),
    Col("current_volume", "num", "Current Rx volume (TRx/NRx)", "70", required=True),
    Col("specialty", "text", "Specialty", "Endocrinology", required=False),
    Col("geo", "text", "Territory / region", "North", required=False),
    Col("calls_per_qtr", "int", "Rep calls last quarter", "2", required=False),
    Col("email_engagement", "int", "Email engagement 0–100", "30", required=False),
    Col("samples_used", "int", "Samples used / quarter", "5", required=False),
    Col("tenure_months", "int", "Months on therapy/brand", "36", required=False),
    Col("competitor_share", "pct", "Competitor share of scripts %", "45", required=False),
    Col("tickets_open", "int", "Open service tickets", "2", required=False),
    Col("payer_friction", "int", "Payer friction 0–10", "6", required=False),
])

st.markdown("#### Load your prescriber panel")
df_raw = data_input(schema, demo_panel(), demo_label="Use demo panel", key="hcppanel")
if df_raw is None or df_raw.empty:
    st.stop()

# ---------------- Persistent params ----------------
P = st.session_state.setdefault("hcp_params", {
    "hi": 60, "mid": 30, "budget": 500000,
})

STAGES = ["① Churn risk (ML)", "② Action plan by risk", "③ Omni-channel mix"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Module (controls adapt below)", STAGES, key="hcp_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ',1)[1]}")

# Score once (used by stages 1 & 2)
scored, used_feats, imputed_feats = score_panel(model, df_raw)
scored["risk_tier"] = scored["churn_risk"].apply(lambda v: risk_tier(v, P["hi"], P["mid"]))

if stage == STAGES[0]:
    P["hi"] = st.sidebar.slider("High-risk cutoff (%)", 50, 90, P["hi"])
    P["mid"] = st.sidebar.slider("Medium-risk cutoff (%)", 10, P["hi"] - 5, min(P["mid"], P["hi"] - 5))
    locked_panel([("Model AUC", f"{auc}"), ("HCPs scored", f"{len(scored):,}"),
                  ("Features used", f"{len(used_feats)}/{len(FEATURES)}")])
elif stage == STAGES[1]:
    st.sidebar.caption("Risk cutoffs are set on the Churn-risk step.")
    locked_panel([("High cutoff", f"≥ {P['hi']}%"), ("Medium cutoff", f"≥ {P['mid']}%"),
                  ("HCPs scored", f"{len(scored):,}")])
else:
    P["budget"] = st.sidebar.number_input("Promo budget ($)", 50000, 50_000_000, P["budget"], step=50000)
    st.sidebar.caption("Allocated by marginal return across channels.")
    locked_panel([("High-risk HCPs", f"{int((scored['churn_risk']>=P['hi']).sum()):,}")])

# Re-tier after any cutoff change
scored["risk_tier"] = scored["churn_risk"].apply(lambda v: risk_tier(v, P["hi"], P["mid"]))

# ---------------- KPIs ----------------
hi_n = int((scored["churn_risk"] >= P["hi"]).sum())
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{auc}</div><div class="l">Model AUC</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{len(scored):,}</div><div class="l">HCPs scored</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v" style="color:#F87171">{hi_n:,}</div><div class="l">High risk</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{scored["churn_risk"].mean():.0f}%</div><div class="l">Avg risk</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

if stage == STAGES[0]:
    if imputed_feats:
        st.caption("Optional features not in your file were filled with training medians: "
                   + ", ".join(LABELS[f] for f in imputed_feats))
    cL, cR = st.columns([3, 2])
    with cL:
        fig = go.Figure(go.Histogram(x=scored["churn_risk"], nbinsx=25, marker_color="#8B6CFF"))
        fig.add_vline(x=P["hi"], line_dash="dot", line_color="#F87171", annotation_text="High")
        fig.add_vline(x=P["mid"], line_dash="dot", line_color="#FBBF24", annotation_text="Med")
        fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Churn risk %", yaxis_title="HCPs",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, key="hist")
    with cR:
        names = [LABELS[f] for f, _ in importances]
        vals = [round(v, 3) for _, v in importances]
        fig = go.Figure(go.Bar(x=vals, y=names, orientation="h", marker_color="#22D3EE"))
        fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(autorange="reversed"),
                          xaxis_title="Importance", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, key="imp")
    st.dataframe(scored.sort_values("churn_risk", ascending=False).head(15)[
        ["hcp_id", "churn_risk", "risk_tier"] + [f for f in ["specialty", "geo", "rx_trend"] if f in scored.columns]],
        use_container_width=True, hide_index=True)

elif stage == STAGES[1]:
    st.caption("Each risk tier gets a play. Download the targeted list — it includes the NPI so the field team can act on named HCPs.")
    tier_defs = [
        {"label": "🔴 High", "accent": "#F87171",
         "action": "Senior-rep save play this week: resolve payer friction & open tickets, re-establish call cadence, reinforce value vs competitor."},
        {"label": "🟠 Medium", "accent": "#FBBF24",
         "action": "Proactive nurture: refresh samples, lift digital engagement, monitor Rx trend monthly."},
        {"label": "🟢 Low", "accent": "#34D399",
         "action": "Maintain cadence via low-cost digital channels; protect the relationship."},
    ]
    cols = st.columns(3)
    for c, td in zip(cols, tier_defs):
        sub = scored[scored["risk_tier"] == td["label"]]
        c.markdown(f'<div class="glass metric" style="border-color:{td["accent"]}55">'
                   f'<div class="v" style="color:{td["accent"]}">{len(sub)}</div>'
                   f'<div class="l">{td["label"]}</div></div>', unsafe_allow_html=True)
    for td in tier_defs:
        sub = scored[scored["risk_tier"] == td["label"]].sort_values("churn_risk", ascending=False)
        if sub.empty:
            continue
        glass(f'<div style="border-left:3px solid {td["accent"]};padding-left:.6rem">'
              f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff">{td["label"]} '
              f'<span style="color:#9AA6CC;font-size:.8rem">· {len(sub)} HCPs</span></div>'
              f'<div style="color:#c4b5ff;font-size:.9rem;margin-top:.3rem"><b>Action:</b> {td["action"]}</div></div>')
        show = [c for c in ["hcp_id", "churn_risk", "specialty", "geo", "rx_trend", "current_volume"] if c in sub.columns]
        with st.expander(f"View & download {td['label']} list ({len(sub)} HCPs)"):
            st.dataframe(sub[show], use_container_width=True, hide_index=True, key=f"tb_{td['label']}")
            st.download_button(f"⬇ {td['label']} HCP list (CSV)", sub[show].to_csv(index=False),
                               file_name=f"hcp_{td['label'].split()[1].lower()}_risk.csv", mime="text/csv",
                               key=f"dl_{td['label']}")

else:
    st.caption("Marginal-return allocation across channels for the budget — where the next dollar buys the most engagement.")
    alloc, conv = optimize_mix(P["budget"], DEFAULT_CHANNELS)
    total_conv = sum(conv.values())
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="glass metric"><div class="v">{total_conv:,.0f}</div><div class="l">Est. engagements</div></div>', unsafe_allow_html=True)
    cpc = P["budget"] / total_conv if total_conv else 0
    c2.markdown(f'<div class="glass metric"><div class="v">${cpc:,.0f}</div><div class="l">Cost / engagement</div></div>', unsafe_allow_html=True)
    fig = go.Figure(go.Bar(x=list(alloc.keys()), y=list(alloc.values()), marker_color="#8B6CFF",
                           text=[f"${v/1000:.0f}k" for v in alloc.values()], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Recommended spend ($)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="mix")
    mix_df = pd.DataFrame({"Channel": alloc.keys(),
                           "Spend ($)": [round(v) for v in alloc.values()],
                           "Est. engagements": [round(conv[c]) for c in alloc]})
    st.dataframe(mix_df, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download recommended mix (CSV)", mix_df.to_csv(index=False),
                       file_name="omnichannel_mix.csv", mime="text/csv")

st.caption("Real RandomForest churn model (AUC on held-out data) + marginal-return channel allocation. "
           f"Synthetic demo data; bring your own NPI-keyed panel. For a production build: {PROFILE['email']}.")
