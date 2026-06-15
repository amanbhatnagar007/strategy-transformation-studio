import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input
from lib.salesforce_suite import (demo_universe, segment, target, size_force,
                                  territory_balance, ic_curve, simulate_ic)

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

st.markdown("#### Load your HCP / account universe")
df_raw = data_input(schema, demo_universe(), demo_label="Use demo universe", key="sfuniverse")
if df_raw is None or df_raw.empty:
    st.stop()

# ---------------- Persistent parameter store (survives across steps) ----------------
P = st.session_state.setdefault("sf_params", {
    "a_min": 8, "b_min": 5,
    "reach_A": 100, "freq_A": 12, "reach_B": 80, "freq_B": 8, "reach_C": 40, "freq_C": 4,
    "selling_days": 200, "calls_per_day": 6, "current_reps": 6, "bal_tol": 20,
    "threshold": 80, "target_pay": 40000, "accelerator": 1.5, "cap_pct": 200,
})

STAGES = ["① Segmentation", "② Targeting", "③ Sizing",
          "④ Structure & Alignment", "⑤ Incentive Comp", "🎯 Action plan"]

# ---------------- Sidebar: step selector ----------------
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls below adapt to this)", STAGES, key="sf_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")

# ---------------- Compute the full chain every run (so any step can show upstream) ----------------
def build_plan():
    return {"A — High": {"reach": P["reach_A"], "freq": P["freq_A"]},
            "B — Medium": {"reach": P["reach_B"], "freq": P["freq_B"]},
            "C — Low": {"reach": P["reach_C"], "freq": P["freq_C"]}}

df_seg = segment(df_raw, P["a_min"], P["b_min"])
plan = build_plan()
df_t, tgt_summary, total_calls = target(df_seg, plan)
reps_req, capacity = size_force(total_calls, P["selling_days"], P["calls_per_day"])
gap = reps_req - P["current_reps"]
sim = simulate_ic(reps_req, P["threshold"], P["target_pay"], P["accelerator"], P["cap_pct"])
tier_counts = df_seg["tier"].value_counts().to_dict()

# ---------------- Stage-specific sidebar controls + locked upstream ----------------
if stage == STAGES[0]:        # Segmentation
    P["a_min"] = st.sidebar.slider("Tier A — min decile", 6, 10, P["a_min"])
    P["b_min"] = st.sidebar.slider("Tier B — min decile", 2, P["a_min"] - 1, min(P["b_min"], P["a_min"] - 1))
    st.sidebar.caption("Decile cutoffs define the A/B/C tiers used by every later step.")

elif stage == STAGES[1]:      # Targeting
    for t, k in [("A — High", "A"), ("B — Medium", "B"), ("C — Low", "C")]:
        st.sidebar.markdown(f"**{t}**")
        P[f"reach_{k}"] = st.sidebar.slider(f"Reach % · {k}", 0, 100, P[f"reach_{k}"], key=f"r{k}")
        P[f"freq_{k}"] = st.sidebar.slider(f"Frequency · {k}", 0, 24, P[f"freq_{k}"], key=f"f{k}")
    locked_panel([("Tier A", f"decile ≥ {P['a_min']} · {tier_counts.get('A — High',0)} HCPs"),
                  ("Tier B", f"decile ≥ {P['b_min']} · {tier_counts.get('B — Medium',0)} HCPs"),
                  ("Tier C", f"rest · {tier_counts.get('C — Low',0)} HCPs")])

elif stage == STAGES[2]:      # Sizing
    P["selling_days"] = st.sidebar.slider("Selling days / year", 120, 240, P["selling_days"])
    P["calls_per_day"] = st.sidebar.slider("Calls / day", 3, 12, P["calls_per_day"])
    P["current_reps"] = st.sidebar.number_input("Current rep count", 1, 2000, P["current_reps"])
    locked_panel([("Targeted HCPs", f"{int(df_t['targeted'].sum()):,}"),
                  ("Total calls / yr", f"{total_calls:,}"),
                  ("Tier freqs", f"A {P['freq_A']} · B {P['freq_B']} · C {P['freq_C']}")])

elif stage == STAGES[3]:      # Structure & Alignment
    P["bal_tol"] = st.sidebar.slider("Balance tolerance ± %", 5, 40, P["bal_tol"])
    st.sidebar.caption("Territories beyond this band vs the mean are flagged over/under-served.")
    locked_panel([("Reps required", f"{reps_req}"),
                  ("Rep capacity", f"{capacity:,} calls/yr"),
                  ("Total calls / yr", f"{total_calls:,}")])

elif stage == STAGES[4]:      # Incentive Comp
    P["threshold"] = st.sidebar.slider("Payout threshold (% attain)", 50, 100, P["threshold"])
    P["target_pay"] = st.sidebar.number_input("Target incentive / rep ($)", 1000, 500000, P["target_pay"], step=1000)
    P["accelerator"] = st.sidebar.slider("Accelerator above 100%", 0.0, 3.0, P["accelerator"], 0.1)
    P["cap_pct"] = st.sidebar.slider("Payout cap (% of target)", 100, 300, P["cap_pct"])
    locked_panel([("Reps (plan)", f"{reps_req}"),
                  ("Incentive budget", f"${reps_req * P['target_pay']/1e6:.2f}M")])

else:                          # Action plan
    st.sidebar.caption("Review the targeted call plan. Adjust any earlier step to update it.")
    locked_panel([("Tiers", f"A≥{P['a_min']} · B≥{P['b_min']}"),
                  ("Targeted HCPs", f"{int(df_t['targeted'].sum()):,}"),
                  ("Reps required", f"{reps_req}")])

# Re-derive with any just-changed segmentation/targeting params
df_seg = segment(df_raw, P["a_min"], P["b_min"])
plan = build_plan()
df_t, tgt_summary, total_calls = target(df_seg, plan)
reps_req, capacity = size_force(total_calls, P["selling_days"], P["calls_per_day"])
gap = reps_req - P["current_reps"]
gap_color = "#22D3EE" if gap <= 0 else "#EC4899"

# ---------------- Persistent headline KPIs ----------------
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{int(df_t["targeted"].sum()):,}</div><div class="l">HCPs targeted</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{total_calls:,}</div><div class="l">Calls / year</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{reps_req}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v" style="color:{gap_color}">{gap:+d}</div><div class="l">vs current reps</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

# ==================== STAGE CONTENT ====================
if stage == STAGES[0]:
    st.caption(f"Decile from your column if provided, else derived from potential. "
               f"Tiers: A (decile ≥ {P['a_min']}), B (≥ {P['b_min']}), C (rest).")
    cL, cR = st.columns(2)
    with cL:
        d = df_seg.groupby("decile").size().reset_index(name="HCPs")
        fig = go.Figure(go.Bar(x=d["decile"], y=d["HCPs"], marker_color="#8B6CFF"))
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Decile", yaxis_title="HCPs",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        t = df_seg.groupby("tier").agg(HCPs=("hcp_id", "size"), Potential=("potential", "sum")).reset_index()
        fig = go.Figure(go.Bar(x=t["tier"], y=t["Potential"], marker_color="#22D3EE",
                               text=t["HCPs"], texttemplate="%{text} HCPs", textposition="outside"))
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Total potential", title="Potential by tier",
                          margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

elif stage == STAGES[1]:
    st.caption("Reach = % of each tier to cover; Frequency = calls/HCP/year. Adjust in the sidebar.")
    st.dataframe(tgt_summary, use_container_width=True, hide_index=True)
    fig = go.Figure(go.Bar(x=tgt_summary["Tier"], y=tgt_summary["Calls demanded"],
                           marker_color="#8B6CFF", text=tgt_summary["Calls demanded"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Calls / year", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

elif stage == STAGES[2]:
    st.caption(f"Rep capacity = {P['selling_days']} selling days × {P['calls_per_day']} calls/day = "
               f"**{capacity:,} calls/year**. Reps required = total calls ÷ capacity.")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="glass metric"><div class="v">{capacity:,}</div><div class="l">Calls / rep / yr</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass metric"><div class="v">{reps_req}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass metric"><div class="v">{P["current_reps"]}</div><div class="l">Current reps</div></div>', unsafe_allow_html=True)
    verdict = ("You are under-resourced — add capacity or tighten targeting." if gap > 0
               else "You have headroom — reinvest capacity into higher frequency or coverage.")
    glass(f'<div style="color:#dfe5fb">Gap: <b style="color:{gap_color}">{gap:+d} reps</b>. {verdict}</div>')

elif stage == STAGES[3]:
    bal = territory_balance(df_t, capacity)
    avg = bal["reps_needed"].mean() if len(bal) else 0
    tol = P["bal_tol"] / 100
    bal["balance"] = np.where(bal["reps_needed"] > avg * (1 + tol), "Over-served",
                              np.where(bal["reps_needed"] < avg * (1 - tol), "Under-served", "Balanced"))
    colors = {"Over-served": "#EC4899", "Under-served": "#F59E0B", "Balanced": "#22D3EE"}
    fig = go.Figure(go.Bar(x=bal["geo"], y=bal["reps_needed"],
                           marker_color=[colors[b] for b in bal["balance"]],
                           text=bal["balance"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Reps needed", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(bal, use_container_width=True, hide_index=True)

elif stage == STAGES[4]:
    sim = simulate_ic(reps_req, P["threshold"], P["target_pay"], P["accelerator"], P["cap_pct"])
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="glass metric"><div class="v">${sim["total_payout"]/1e6:.2f}M</div><div class="l">Total payout</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass metric"><div class="v">{sim["vs_budget"]:+.0f}%</div><div class="l">vs target budget</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass metric"><div class="v">{sim["pct_above_target"]:.0f}%</div><div class="l">reps above target</div></div>', unsafe_allow_html=True)
    cL, cR = st.columns(2)
    with cL:
        xs = np.arange(P["threshold"] - 10, 176)
        ys = ic_curve(xs, P["threshold"], P["target_pay"], P["accelerator"], P["cap_pct"])
        fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#22D3EE", width=3)))
        fig.add_vline(x=100, line_dash="dot", line_color="#888")
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Attainment %", yaxis_title="Payout $",
                          title="Payout curve", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with cR:
        fig = go.Figure(go.Histogram(x=sim["attain"], nbinsx=24, marker_color="#8B6CFF"))
        fig.add_vline(x=P["threshold"], line_dash="dot", line_color="#F59E0B")
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Rep attainment %", yaxis_title="Reps",
                          title="Attainment distribution", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    if sim["vs_budget"] > 8:
        glass('<div style="color:#dfe5fb">⚠ Payout is running over budget — the accelerator/cap may be too rich. '
              'Flatten the curve above 100% or lower the cap to protect cost of sales.</div>')

else:  # Action plan
    st.caption("Each tier gets a recommended cadence and channel mix. Download the targeted list — it includes the HCP identifier so the field team can act.")
    targeted = df_t[df_t["targeted"]].copy()
    targeted["decile"] = targeted["decile"].astype(int)
    tier_defs = [
        {"label": "A — High", "accent": "#22D3EE", "icon": "★",
         "action": f"Highest priority. {P['freq_A']} calls/yr + digital + KAM for top accounts. Defend share, deepen relationship."},
        {"label": "B — Medium", "accent": "#8B6CFF", "icon": "◆",
         "action": f"Selective coverage. {P['freq_B']} calls/yr + email/webinar nurture. Grow adopters, convert spreaders."},
        {"label": "C — Low", "accent": "#6B7393", "icon": "○",
         "action": f"Low-cost reach. {P['freq_C']} calls/yr or fully digital/inside-sales. Maintain, don't over-invest."},
    ]
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
              f'<span style="color:#9AA6CC;font-size:.8rem">· {len(sub)} HCPs · {sub["planned_calls"].iloc[0]} calls/yr each</span></div>'
              f'<div style="color:#c4b5ff;font-size:.9rem;margin-top:.3rem"><b>Action:</b> {td["action"]}</div></div>')
        show = [c for c in ["hcp_id", "specialty", "geo", "decile", "potential", "planned_calls"] if c in sub.columns]
        with st.expander(f"View & download {td['label']} call list ({len(sub)} HCPs)"):
            st.dataframe(sub[show], use_container_width=True, hide_index=True)
            st.download_button(f"⬇ {td['label']} call list (CSV)", sub[show].to_csv(index=False),
                               file_name=f"call_list_{td['label'][0]}.csv", mime="text/csv", key=f"dl_{td['label']}")

st.caption("AI-assisted SFE model (decile segmentation · workload build-up sizing · goal-attainment IC curve). "
           f"Directional planning tool. For a tailored sales-force & IC engagement: {PROFILE['email']}.")
