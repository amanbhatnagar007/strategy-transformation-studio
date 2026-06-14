import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.churn_model import train, predict_one, at_risk_table, FEATURES, LABELS

st.set_page_config(page_title="HCP Churn Predictor", page_icon="🩺", layout="wide")
page_header("🩺 HCP Churn Predictor",
            "A real machine-learning model that predicts which healthcare professionals are likely to reduce "
            "prescribing — so commercial teams can intervene early. Trained live on a synthetic dataset.")
st.page_link("Home.py", label="← Back to Studio")

@st.cache_resource(show_spinner="Training the model…")
def get_model():
    return train()

model, df, auc, importances = get_model()

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">{auc}</div><div class="l">Model AUC (held-out)</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{len(df):,}</div><div class="l">HCPs in dataset</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{df.churned.mean()*100:.0f}%</div><div class="l">Base churn rate</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🎛️ Score an HCP", "📊 What drives churn", "🚨 At-risk list"])

with t1:
    st.markdown("#### Enter an HCP's profile to get a churn probability")
    c = st.columns(2)
    vals = {}
    defaults = {"rx_trend": -8.0, "calls_per_qtr": 2, "email_engagement": 30, "samples_used": 5,
                "tenure_months": 36, "competitor_share": 45, "tickets_open": 2, "payer_friction": 6}
    ranges = {"rx_trend": (-40.0, 40.0), "calls_per_qtr": (0, 12), "email_engagement": (0, 100),
              "samples_used": (0, 40), "tenure_months": (1, 120), "competitor_share": (0, 80),
              "tickets_open": (0, 6), "payer_friction": (0, 10)}
    for i, f in enumerate(FEATURES):
        with c[i % 2]:
            lo, hi = ranges[f]
            if isinstance(lo, float):
                vals[f] = st.slider(LABELS[f], lo, hi, defaults[f])
            else:
                vals[f] = st.slider(LABELS[f], lo, hi, defaults[f])
    prob, tier, action = predict_one(model, vals)
    st.markdown(f'<div class="glass" style="text-align:center;margin-top:.5rem">'
                f'<div style="font-family:Space Grotesk;font-size:2.4rem;font-weight:700;color:#fff">{prob}%</div>'
                f'<div style="color:#9AA6CC">churn probability · risk tier {tier}</div>'
                f'<div style="color:#c4b5ff;margin-top:.5rem;font-size:.9rem">Recommended action: {action}</div></div>',
                unsafe_allow_html=True)

with t2:
    st.markdown("#### Feature importance — what the model weights most")
    names = [LABELS[f] for f, _ in importances]
    vals_i = [round(v, 3) for _, v in importances]
    fig = go.Figure(go.Bar(x=vals_i, y=names, orientation="h", marker_color="#22D3EE",
                           text=vals_i, textposition="outside"))
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=30, t=10, b=10),
                      yaxis=dict(autorange="reversed"), xaxis_title="Importance")
    st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">Declining Rx trend, payer friction, open service tickets '
          'and competitor share are the strongest churn signals — the levers a field team can actually act on.</div>')

with t3:
    st.markdown("#### Highest-risk HCPs to prioritize this quarter")
    tbl = at_risk_table(model, df).rename(columns=LABELS)
    st.dataframe(tbl, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download at-risk list (CSV)", tbl.to_csv(index=False),
                       file_name="hcp_at_risk.csv", mime="text/csv")

st.caption("Real RandomForest model trained on synthetic data illustrating a predictive-churn workflow. "
           f"For a production model on your data: {PROFILE['email']}.")
