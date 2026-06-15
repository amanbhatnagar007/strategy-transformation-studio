import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Medicare Advantage Estimator", page_icon="🏥", layout="wide")
page_header("🏥 Medicare Advantage Estimator",
            "Estimate the value upside from better risk-score (RAF) capture, care-management investment and "
            "MLR improvement in a Medicare Advantage book — current vs improved revenue and margin.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

ACCENT, ACCENT2, GREEN, RED = "#8B6CFF", "#22D3EE", "#34D399", "#EF4444"

with st.sidebar:
    st.header("Book of business")
    members = st.number_input("MA members", 1000, 5_000_000, 50_000, step=1000)
    base_pmpm = st.number_input("Base PMPM revenue at RAF 1.0 ($)", 200, 3000, 950, step=10)
    st.header("Risk capture")
    cur_raf = st.slider("Current avg RAF (risk score)", 0.50, 2.50, 1.00, 0.01)
    tgt_raf = st.slider("Target avg RAF after better capture", 0.50, 2.50, 1.12, 0.01)
    st.header("Care & cost")
    care_pmpm = st.number_input("Care-management cost PMPM ($)", 0, 300, 18, step=1)
    mlr_now = st.slider("Current medical loss ratio (MLR %)", 70, 100, 86)
    mlr_impr = st.slider("Expected MLR improvement (pts)", 0.0, 8.0, 1.5, 0.1)

if tgt_raf < cur_raf:
    st.warning("Target RAF is below current RAF — showing a downside scenario. Set target ≥ current for upside.")

mlr_new = max(mlr_now - mlr_impr, 0.0)


def annual_revenue(raf):
    return members * base_pmpm * raf * 12


rev_cur = annual_revenue(cur_raf)
rev_tgt = annual_revenue(tgt_raf)
rev_upside = rev_tgt - rev_cur

care_annual = members * care_pmpm * 12

# Margin = revenue * (1 - MLR) - care management cost
margin_cur = rev_cur * (1 - mlr_now / 100)
margin_tgt = rev_tgt * (1 - mlr_new / 100) - care_annual
margin_upside = margin_tgt - margin_cur

per_member_uplift = margin_upside / members if members else 0

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${rev_upside:,.0f}</div><div class="l">Annual revenue upside</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${margin_upside:,.0f}</div><div class="l">Annual margin upside</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${per_member_uplift:,.0f}</div><div class="l">Margin uplift / member / yr</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🌉 Value bridge", "📊 Current vs improved", "📋 Executive summary"])

with t1:
    st.markdown("#### Margin bridge: current → improved")
    # Decompose: start at current margin, add risk-capture revenue margin, subtract care mgmt, add MLR improvement
    risk_rev_margin = (rev_tgt - rev_cur) * (1 - mlr_now / 100)
    mlr_gain = rev_tgt * (mlr_now / 100 - mlr_new / 100)
    steps = [
        ("Current margin", margin_cur, "abs"),
        ("Risk capture (RAF↑)", risk_rev_margin, "rel"),
        ("Care mgmt cost", -care_annual, "rel"),
        ("MLR improvement", mlr_gain, "rel"),
        ("Improved margin", margin_tgt, "total"),
    ]
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=[s[2].replace("abs", "absolute").replace("rel", "relative") for s in steps],
        x=[s[0] for s in steps], y=[s[1] for s in steps],
        text=[f"${s[1]:,.0f}" for s in steps], textposition="outside",
        connector={"line": {"color": "#6b7394"}},
        increasing={"marker": {"color": GREEN}}, decreasing={"marker": {"color": RED}},
        totals={"marker": {"color": ACCENT}}))
    fig.update_layout(template="plotly_dark", height=400, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Annual margin ($)",
                      margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">Improved RAF lifts CMS revenue; care-management investment is '
          'a cost that funds documentation accuracy and lower utilization, which shows up as the MLR improvement. '
          'Net of the care-management spend, the program is accretive when RAF gains and MLR savings outweigh it.</div>')

with t2:
    st.markdown("#### Current vs improved")
    cmp = pd.DataFrame({
        "Scenario": ["Current", "Improved"],
        "Annual revenue ($)": [rev_cur, rev_tgt],
        "Annual margin ($)": [margin_cur, margin_tgt],
        "Avg RAF": [cur_raf, tgt_raf],
        "MLR %": [mlr_now, mlr_new],
    })
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Revenue", x=cmp["Scenario"], y=cmp["Annual revenue ($)"], marker_color=ACCENT2))
    fig.add_trace(go.Bar(name="Margin", x=cmp["Scenario"], y=cmp["Annual margin ($)"], marker_color=ACCENT))
    fig.update_layout(template="plotly_dark", height=360, barmode="group",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="$ / year", margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(cmp.round(2), use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    direction = "upside" if margin_upside >= 0 else "downside"
    txt = (f"On a <b>{members:,}</b>-member Medicare Advantage book, lifting average RAF from <b>{cur_raf:.2f}</b> to "
           f"<b>{tgt_raf:.2f}</b> grows annual revenue by <b>${rev_upside:,.0f}</b> (to ${rev_tgt:,.0f}). "
           f"Net of <b>${care_annual:,.0f}</b> in care-management investment and a <b>{mlr_impr:.1f}-pt</b> MLR "
           f"improvement (to {mlr_new:.1f}%), annual margin {direction} is <b>${margin_upside:,.0f}</b> — about "
           f"<b>${per_member_uplift:,.0f}</b> per member. "
           f"Assumptions: PMPM revenue scales linearly with RAF at ${base_pmpm}/RAF-point; margin = revenue×(1−MLR) "
           f"less care-management cost; risk capture must be supported by compliant documentation. "
           f"Figures are directional heuristics for planning, not actuarial certification.")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{txt}</div>')
    out = pd.DataFrame({
        "Metric": ["Members", "Base PMPM ($)", "Current RAF", "Target RAF", "Care mgmt PMPM ($)",
                   "Current MLR %", "Improved MLR %", "Current revenue ($)", "Improved revenue ($)",
                   "Revenue upside ($)", "Current margin ($)", "Improved margin ($)", "Margin upside ($)",
                   "Per-member uplift ($)"],
        "Value": [members, base_pmpm, cur_raf, tgt_raf, care_pmpm, mlr_now, round(mlr_new, 1),
                  round(rev_cur), round(rev_tgt), round(rev_upside), round(margin_cur), round(margin_tgt),
                  round(margin_upside), round(per_member_uplift)],
    })
    st.download_button("⬇ Download MA estimate (CSV)", out.to_csv(index=False),
                       file_name="medicare_advantage_estimate.csv", mime="text/csv")

st.caption("AI-assisted heuristic Medicare Advantage value model — directional, not actuarial or CMS bid advice. "
           f"For a tailored engagement: {PROFILE['email']}.")
