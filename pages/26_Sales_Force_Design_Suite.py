import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input
from lib.actions import render_tiered_actions
from lib.salesforce_suite import (demo_universe, segment, target, size_force,
                                  territory_balance, ic_curve, simulate_ic, DEFAULT_PLAN)

st.set_page_config(page_title="Sales Force Design & IC Suite", page_icon="🧭", layout="wide")
page_header("🧭 Sales Force Design & IC Suite",
            "End-to-end commercial design from one upload: segment the HCP universe, set targeting, size the force "
            "(workload build-up), align territories, and design the incentive plan — with an actionable target list by tier.")
st.page_link("Home.py", label="← Back to Studio")

# ---------------- Upload (required NPI + universe) ----------------
schema = ColumnSchema([
    Col("hcp_id", "text", "HCP identifier — NPI or internal ID (so the output is actionable per HCP)", "1234567890", required=True),
    Col("specialty", "text", "Primary specialty", "Endocrinology", required=True),
    Col("geo", "text", "Territory / region / ZIP", "North", required=True),
    Col("potential", "num", "Rx or market potential (units or $)", "180", required=True),
    Col("current_volume", "num", "Current volume (TRx/NRx or sales)", "70", required=True),
    Col("decile", "int", "Decile 1–10 (else derived from potential)", "9", required=False),
    Col("access", "text", "Rep access: High/Medium/Low/No-see", "High", required=False),
    Col("competitor_share", "pct", "Competitor share of HCP's scripts (%)", "40", required=False),
    Col("behavior_segment", "text", "Behavioral segment (loyalist/spreader/adopter)", "spreader", required=False),
])

st.markdown("#### 1 · Load your HCP / account universe")
df_raw = data_input(schema, demo_universe(), demo_label="Use demo universe", key="sfuniverse")
if df_raw is None or df_raw.empty:
    st.stop()

df = segment(df_raw)

# ---------------- Targeting controls (sidebar) ----------------
with st.sidebar:
    st.header("Targeting plan")
    plan = {}
    for tier, d in DEFAULT_PLAN.items():
        st.markdown(f"**{tier}**")
        reach = st.slider(f"Reach % · {tier}", 0, 100, d["reach"], key=f"r{tier}")
        freq = st.slider(f"Frequency (calls/yr) · {tier}", 0, 24, d["freq"], key=f"f{tier}")
        plan[tier] = {"reach": reach, "freq": freq}
    st.header("Rep capacity")
    selling_days = st.slider("Selling days / year", 120, 240, 200)
    calls_per_day = st.slider("Calls / day", 3, 12, 6)
    current_reps = st.number_input("Current rep count", 1, 2000, 6)
    st.header("Incentive plan")
    threshold = st.slider("Payout threshold (% attainment)", 50, 100, 80)
    target_pay = st.number_input("Target incentive / rep ($)", 1000, 500000, 40000, step=1000)
    accelerator = st.slider("Accelerator above 100%", 0.0, 3.0, 1.5, 0.1)
    cap_pct = st.slider("Payout cap (% of target)", 100, 300, 200)

df_t, tgt_summary, total_calls = target(df, plan)
reps_req, capacity = size_force(total_calls, selling_days, calls_per_day)
gap = reps_req - current_reps

# ---------------- Headline KPIs ----------------
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{int(df_t["targeted"].sum()):,}</div><div class="l">HCPs targeted</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{total_calls:,}</div><div class="l">Calls / year</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{reps_req}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
gap_color = "#22D3EE" if gap <= 0 else "#EC4899"
k4.markdown(f'<div class="glass metric"><div class="v" style="color:{gap_color}">{gap:+d}</div><div class="l">vs current reps</div></div>', unsafe_allow_html=True)

tSeg, tTgt, tSize, tStruct, tIC, tAction = st.tabs(
    ["① Segmentation", "② Targeting", "③ Sizing", "④ Structure & Alignment", "⑤ Incentive Comp", "🎯 Action plan"])

with tSeg:
    st.markdown("#### Segment the universe by decile → tier")
    st.caption("Decile from your column if provided, else derived from potential. Tiers: A (8–10), B (5–7), C (1–4).")
    cL, cR = st.columns(2)
    with cL:
        d = df.groupby("decile").size().reset_index(name="HCPs")
        fig = go.Figure(go.Bar(x=d["decile"], y=d["HCPs"], marker_color="#8B6CFF"))
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Decile", yaxis_title="HCPs",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        t = df.groupby("tier").agg(HCPs=("hcp_id", "size"), Potential=("potential", "sum")).reset_index()
        fig = go.Figure(go.Bar(x=t["tier"], y=t["Potential"], marker_color="#22D3EE",
                               text=t["HCPs"], texttemplate="%{text} HCPs", textposition="outside"))
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Total potential", title="Potential by tier",
                          margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df.groupby(["tier", "specialty"]).size().reset_index(name="HCPs"),
                 use_container_width=True, hide_index=True)

with tTgt:
    st.markdown("#### Targeting — reach & frequency by tier (adjust in the sidebar)")
    st.dataframe(tgt_summary, use_container_width=True, hide_index=True)
    fig = go.Figure(go.Bar(x=tgt_summary["Tier"], y=tgt_summary["Calls demanded"],
                           marker_color="#8B6CFF", text=tgt_summary["Calls demanded"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Calls / year", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with tSize:
    st.markdown("#### Sizing — workload build-up")
    st.caption(f"Rep capacity = {selling_days} selling days × {calls_per_day} calls/day = **{capacity:,} calls/year**. "
               f"Reps required = total calls ÷ capacity.")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="glass metric"><div class="v">{capacity:,}</div><div class="l">Calls / rep / yr</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass metric"><div class="v">{reps_req}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass metric"><div class="v">{current_reps}</div><div class="l">Current reps</div></div>', unsafe_allow_html=True)
    verdict = ("You are under-resourced — add capacity or tighten targeting." if gap > 0
               else "You have headroom — reinvest capacity into higher frequency or coverage.")
    glass(f'<div style="color:#dfe5fb">Gap: <b style="color:{gap_color}">{gap:+d} reps</b>. {verdict}</div>')

with tStruct:
    st.markdown("#### Structure & alignment — workload balance by territory")
    bal = territory_balance(df_t, capacity)
    colors = {"Over-served": "#EC4899", "Under-served": "#F59E0B", "Balanced": "#22D3EE"}
    fig = go.Figure(go.Bar(x=bal["geo"], y=bal["reps_needed"],
                           marker_color=[colors[b] for b in bal["balance"]],
                           text=bal["balance"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Reps needed", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(bal, use_container_width=True, hide_index=True)

with tIC:
    st.markdown("#### Incentive compensation — payout curve & cost")
    sim = simulate_ic(reps_req, threshold, target_pay, accelerator, cap_pct)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="glass metric"><div class="v">${sim["total_payout"]/1e6:.2f}M</div><div class="l">Total payout</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass metric"><div class="v">{sim["vs_budget"]:+.0f}%</div><div class="l">vs target budget</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass metric"><div class="v">{sim["pct_above_target"]:.0f}%</div><div class="l">reps above target</div></div>', unsafe_allow_html=True)
    cL, cR = st.columns(2)
    with cL:
        xs = np.arange(threshold - 10, 176)
        ys = ic_curve(xs, threshold, target_pay, accelerator, cap_pct)
        fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#22D3EE", width=3)))
        fig.add_vline(x=100, line_dash="dot", line_color="#888")
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Attainment %", yaxis_title="Payout $",
                          title="Payout curve", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        fig = go.Figure(go.Histogram(x=sim["attain"], nbinsx=24, marker_color="#8B6CFF"))
        fig.add_vline(x=threshold, line_dash="dot", line_color="#F59E0B")
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Rep attainment %", yaxis_title="Reps",
                          title="Attainment distribution", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    if sim["vs_budget"] > 8:
        glass('<div style="color:#dfe5fb">⚠ Payout is running over budget — the accelerator/cap may be too rich. '
              'Flatten the curve above 100% or lower the cap to protect cost of sales.</div>')

with tAction:
    st.markdown("#### Actionable call plan by target tier")
    st.caption("Each tier gets a recommended cadence and channel mix. Download the targeted list — it includes the HCP identifier so the field team can act.")
    targeted = df_t[df_t["targeted"]].copy()
    targeted["decile"] = targeted["decile"].astype(int)
    tier_defs = [
        {"label": "A — High", "min": 0, "max": 99, "accent": "#22D3EE", "icon": "★",
         "action": f"Highest priority. {plan['A — High']['freq']} calls/yr + digital + KAM for top accounts. Defend share, deepen relationship."},
        {"label": "B — Medium", "min": 0, "max": 99, "accent": "#8B6CFF", "icon": "◆",
         "action": f"Selective coverage. {plan['B — Medium']['freq']} calls/yr + email/webinar nurture. Grow adopters, convert spreaders."},
        {"label": "C — Low", "min": 0, "max": 99, "accent": "#6B7393", "icon": "○",
         "action": f"Low-cost reach. {plan['C — Low']['freq']} calls/yr or fully digital/inside-sales. Maintain, don't over-invest."},
    ]
    # tier the targeted set by its own 'tier' label (use a numeric proxy so render works on label)
    targeted["__tval"] = targeted["tier"].map({"A — High": 1, "B — Medium": 2, "C — Low": 3})
    # Build per-tier cards manually (tiers are categorical, not ranges)
    cols = st.columns(3)
    for c, td in zip(cols, tier_defs):
        sub = targeted[targeted["tier"] == td["label"]]
        c.markdown(f'<div class="glass metric" style="border-color:{td["accent"]}55">'
                   f'<div class="v" style="color:{td["accent"]}">{len(sub)}</div>'
                   f'<div class="l">{td["icon"]} {td["label"]} targeted</div></div>', unsafe_allow_html=True)
    for td in tier_defs:
        sub = targeted[targeted["tier"] == td["label"]].sort_values("potential", ascending=False)
        if sub.empty:
            continue
        glass(f'<div style="border-left:3px solid {td["accent"]};padding-left:.6rem">'
              f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff">{td["icon"]} {td["label"]} '
              f'<span style="color:#9AA6CC;font-size:.8rem">· {len(sub)} HCPs · {plan[td["label"]]["freq"]} calls/yr each</span></div>'
              f'<div style="color:#c4b5ff;font-size:.9rem;margin-top:.3rem"><b>Action:</b> {td["action"]}</div></div>')
        show = ["hcp_id", "specialty", "geo", "decile", "potential", "planned_calls"]
        show = [c for c in show if c in sub.columns]
        with st.expander(f"View & download {td['label']} call list ({len(sub)} HCPs)"):
            st.dataframe(sub[show], use_container_width=True, hide_index=True)
            st.download_button(f"⬇ {td['label']} call list (CSV)", sub[show].to_csv(index=False),
                               file_name=f"call_list_{td['label'][0]}.csv", mime="text/csv",
                               key=f"dl_{td['label']}")

st.caption("AI-assisted SFE model (decile segmentation · workload build-up sizing · goal-attainment IC curve). "
           f"Directional planning tool. For a tailored sales-force & IC engagement: {PROFILE['email']}.")
