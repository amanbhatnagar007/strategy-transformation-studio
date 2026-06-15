import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from lib.theme import page_header, glass, locked_panel
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input
from lib.orgchart import field_org_dot, org_counts
from lib.salesforce_suite import (demo_universe, segment, assign_teams, target, size_force,
                                  ic_curve, simulate_ic, SEG_SCHEMES, TEAM_MODES)

st.set_page_config(page_title="Sales Force Design & IC Suite", page_icon="🧭", layout="wide")
page_header("🧭 Sales Force Design & IC Suite",
            "End-to-end commercial design from one upload: segment the universe (compare schemes), set targeting, "
            "size one or more sales teams, see the org chart, design incentives, and export an actionable call plan.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

# ---------------- Upload ----------------
schema = ColumnSchema([
    Col("hcp_id", "text", "NPI or internal ID (so the output is actionable per HCP)", "1234567890", required=True),
    Col("specialty", "text", "Primary specialty (used for specialty teams)", "Endocrinology", required=True),
    Col("geo", "text", "Territory / region / ZIP (used for regional teams)", "North", required=True),
    Col("potential", "num", "Rx or market potential (units or $)", "180", required=True),
    Col("current_volume", "num", "Current volume (TRx/NRx or sales)", "70", required=True),
    Col("decile", "int", "Decile 1–10 (else derived from potential)", "9", required=False),
    Col("access", "text", "Rep access: High/Medium/Low/No-see (used by access-adjusted scheme)", "High", required=False),
    Col("competitor_share", "pct", "Competitor share of HCP's scripts (%)", "40", required=False),
])
st.markdown("#### Load your HCP / account universe")
df_raw = data_input(schema, demo_universe(), demo_label="Use demo universe", key="sfuniverse")
if df_raw is None or df_raw.empty:
    st.stop()

P = st.session_state.setdefault("sf_params", {
    "a_min": 8, "b_min": 5, "scheme": SEG_SCHEMES[0], "compare": False,
    "reach_A": 100, "freq_A": 12, "reach_B": 80, "freq_B": 8, "reach_C": 40, "freq_C": 4,
    "team_mode": TEAM_MODES[0], "selling_days": 200, "calls_per_day": 6, "current_reps": 6,
    "span_dm": 8, "dm_per_rm": 5,
    "threshold": 80, "target_pay": 40000, "accelerator": 1.5, "cap_pct": 200,
})

STAGES = ["① Segmentation", "② Targeting", "③ Sizing & Teams",
          "④ Org structure", "⑤ Incentive Comp", "🎯 Action plan"]
st.sidebar.header("Workflow")
stage = st.sidebar.radio("Step (controls below adapt)", STAGES, key="sf_stage")
st.sidebar.divider()
st.sidebar.subheader(f"Controls · {stage.split(' ', 1)[1]}")


def build_plan():
    return {"A — High": {"reach": P["reach_A"], "freq": P["freq_A"]},
            "B — Medium": {"reach": P["reach_B"], "freq": P["freq_B"]},
            "C — Low": {"reach": P["reach_C"], "freq": P["freq_C"]}}


def team_metrics(df_t, capacity):
    g = (df_t[df_t["targeted"]].groupby("team")["planned_calls"].sum().reset_index(name="calls"))
    g["reps"] = np.ceil(g["calls"] / max(capacity, 1)).astype(int)
    return g


# ----- full chain (recomputed each run so any step shows upstream) -----
def compute():
    df_seg = segment(df_raw, P["a_min"], P["b_min"], P["scheme"])
    df_seg["team"] = assign_teams(df_seg, P["team_mode"])
    df_t, tgt_summary, total_calls = target(df_seg, build_plan())
    _, capacity = size_force(total_calls, P["selling_days"], P["calls_per_day"])
    tm = team_metrics(df_t, capacity)
    total_reps = int(tm["reps"].sum()) if len(tm) else 0
    return df_seg, df_t, tgt_summary, total_calls, capacity, tm, total_reps

df_seg, df_t, tgt_summary, total_calls, capacity, tm, total_reps = compute()
tier_counts = df_seg["tier"].value_counts().to_dict()

# ---------------- Stage sidebar controls + locked ----------------
if stage == STAGES[0]:
    P["scheme"] = st.sidebar.selectbox("Segmentation scheme", SEG_SCHEMES, index=SEG_SCHEMES.index(P["scheme"]))
    P["compare"] = st.sidebar.toggle("Compare with the other scheme", P["compare"])
    P["a_min"] = st.sidebar.slider("Tier A — min decile", 6, 10, P["a_min"])
    P["b_min"] = st.sidebar.slider("Tier B — min decile", 2, P["a_min"] - 1, min(P["b_min"], P["a_min"] - 1))
elif stage == STAGES[1]:
    for t, k in [("A — High", "A"), ("B — Medium", "B"), ("C — Low", "C")]:
        st.sidebar.markdown(f"**{t}**")
        P[f"reach_{k}"] = st.sidebar.slider(f"Reach % · {k}", 0, 100, P[f"reach_{k}"], key=f"r{k}")
        P[f"freq_{k}"] = st.sidebar.slider(f"Frequency · {k}", 0, 24, P[f"freq_{k}"], key=f"f{k}")
    locked_panel([("Scheme", P["scheme"]),
                  ("Tier A/B/C", f"{tier_counts.get('A — High',0)}/{tier_counts.get('B — Medium',0)}/{tier_counts.get('C — Low',0)}")])
elif stage == STAGES[2]:
    P["team_mode"] = st.sidebar.selectbox("Team structure", TEAM_MODES, index=TEAM_MODES.index(P["team_mode"]))
    P["selling_days"] = st.sidebar.slider("Selling days / year", 120, 240, P["selling_days"])
    P["calls_per_day"] = st.sidebar.slider("Calls / day", 3, 12, P["calls_per_day"])
    P["current_reps"] = st.sidebar.number_input("Current rep count", 1, 5000, P["current_reps"])
    locked_panel([("Targeted HCPs", f"{int(df_t['targeted'].sum()):,}"),
                  ("Total calls / yr", f"{total_calls:,}")])
elif stage == STAGES[3]:
    P["span_dm"] = st.sidebar.slider("Reps per District Manager", 4, 12, P["span_dm"])
    P["dm_per_rm"] = st.sidebar.slider("Districts per Regional Manager", 3, 8, P["dm_per_rm"])
    locked_panel([("Teams", f"{len(tm)}"), ("Total reps", f"{total_reps}"),
                  ("Mode", P["team_mode"].split(" (")[0])])
elif stage == STAGES[4]:
    P["threshold"] = st.sidebar.slider("Payout threshold (% attain)", 50, 100, P["threshold"])
    P["target_pay"] = st.sidebar.number_input("Target incentive / rep ($)", 1000, 500000, P["target_pay"], step=1000)
    P["accelerator"] = st.sidebar.slider("Accelerator above 100%", 0.0, 3.0, P["accelerator"], 0.1)
    P["cap_pct"] = st.sidebar.slider("Payout cap (% of target)", 100, 300, P["cap_pct"])
    locked_panel([("Reps (plan)", f"{total_reps}"), ("Incentive budget", f"${total_reps*P['target_pay']/1e6:.2f}M")])
else:
    st.sidebar.caption("Review the targeted call plan; adjust any earlier step to update it.")
    locked_panel([("Scheme", P["scheme"]), ("Teams", f"{len(tm)}"), ("Reps", f"{total_reps}")])

# recompute after edits
df_seg, df_t, tgt_summary, total_calls, capacity, tm, total_reps = compute()
gap = total_reps - P["current_reps"]
gap_color = "#22D3EE" if gap <= 0 else "#EC4899"

# ---------------- KPIs ----------------
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{int(df_t["targeted"].sum()):,}</div><div class="l">HCPs targeted</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{len(tm)}</div><div class="l">Teams</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{total_reps}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v" style="color:{gap_color}">{gap:+d}</div><div class="l">vs current reps</div></div>', unsafe_allow_html=True)

st.markdown(f"### {stage}")

# ==================== STAGE CONTENT ====================
if stage == STAGES[0]:
    st.caption(f"Scheme: **{P['scheme']}**. Tiers: A (decile ≥ {P['a_min']}), B (≥ {P['b_min']}), C (rest).")
    cL, cR = st.columns(2)
    with cL:
        t = df_seg.groupby("tier").agg(HCPs=("hcp_id", "size"), Potential=("potential", "sum")).reset_index()
        fig = go.Figure(go.Bar(x=t["tier"], y=t["Potential"], marker_color="#22D3EE",
                               text=t["HCPs"], texttemplate="%{text} HCPs", textposition="outside"))
        fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Total potential", title="Tier by current scheme",
                          margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True, key="seg1")
    with cR:
        if P["compare"]:
            other = [s for s in SEG_SCHEMES if s != P["scheme"]][0]
            df_o = segment(df_raw, P["a_min"], P["b_min"], other)
            comp = pd.DataFrame({
                "Tier": ["A — High", "B — Medium", "C — Low"],
                P["scheme"]: [int((df_seg["tier"] == x).sum()) for x in ["A — High", "B — Medium", "C — Low"]],
                other: [int((df_o["tier"] == x).sum()) for x in ["A — High", "B — Medium", "C — Low"]],
            })
            fig = go.Figure()
            fig.add_trace(go.Bar(x=comp["Tier"], y=comp[P["scheme"]], name=P["scheme"], marker_color="#8B6CFF"))
            fig.add_trace(go.Bar(x=comp["Tier"], y=comp[other], name=other, marker_color="#22D3EE"))
            fig.update_layout(template="plotly_dark", height=300, barmode="group", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", title="Scheme comparison (HCPs per tier)",
                              margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True, key="segcmp")
        else:
            d = df_seg.groupby("decile").size().reset_index(name="HCPs")
            fig = go.Figure(go.Bar(x=d["decile"], y=d["HCPs"], marker_color="#8B6CFF"))
            fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Decile", yaxis_title="HCPs",
                              title="Decile distribution", margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True, key="segdec")

elif stage == STAGES[1]:
    st.caption("Reach = % of each tier covered; Frequency = calls/HCP/year.")
    st.dataframe(tgt_summary, use_container_width=True, hide_index=True)
    fig = go.Figure(go.Bar(x=tgt_summary["Tier"], y=tgt_summary["Calls demanded"], marker_color="#8B6CFF",
                           text=tgt_summary["Calls demanded"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Calls / year", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True, key="tgt")

elif stage == STAGES[2]:
    st.caption(f"Team structure: **{P['team_mode']}**. Rep capacity = {P['selling_days']}×{P['calls_per_day']} = "
               f"**{capacity:,} calls/yr**. Reps sized per team (workload build-up).")
    show = tm.rename(columns={"team": "Team", "calls": "Calls/yr", "reps": "Reps required"})
    st.dataframe(show, use_container_width=True, hide_index=True)
    fig = go.Figure(go.Bar(x=tm["team"], y=tm["reps"], marker_color="#22D3EE",
                           text=tm["reps"], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Reps required", title="Reps by team",
                      margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True, key="teams")
    verdict = ("Under-resourced — add capacity or tighten targeting." if gap > 0
               else "Headroom — reinvest into frequency or coverage.")
    glass(f'<div style="color:#dfe5fb">Total reps required: <b>{total_reps}</b> across {len(tm)} team(s). '
          f'Gap vs current: <b style="color:{gap_color}">{gap:+d}</b>. {verdict}</div>')

elif stage == STAGES[3]:
    st.caption(f"Field org from the sized force — {P['span_dm']} reps/District Manager, "
               f"{P['dm_per_rm']} districts/Regional Manager.")
    structs = [{"name": r["team"], "reps": int(r["reps"])} for _, r in tm.iterrows()]
    st.graphviz_chart(field_org_dot(structs, P["span_dm"], P["dm_per_rm"]), use_container_width=True)
    rows = []
    for s in structs:
        oc = org_counts(s["reps"], P["span_dm"], P["dm_per_rm"])
        rows.append({"Team": s["name"], "Reps": oc["reps"], "District mgrs": oc["district_mgrs"],
                     "Regional mgrs": oc["regional_mgrs"], "Mgr : rep ratio": oc["mgr_ratio"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

elif stage == STAGES[4]:
    sim = simulate_ic(total_reps, P["threshold"], P["target_pay"], P["accelerator"], P["cap_pct"])
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
        st.plotly_chart(fig, use_container_width=True, key="ic_curve")
    with cR:
        fig = go.Figure(go.Histogram(x=sim["attain"], nbinsx=24, marker_color="#8B6CFF"))
        fig.add_vline(x=P["threshold"], line_dash="dot", line_color="#F59E0B")
        fig.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Rep attainment %", yaxis_title="Reps",
                          title="Attainment distribution", margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True, key="ic_hist")
    if sim["vs_budget"] > 8:
        glass('<div style="color:#dfe5fb">⚠ Payout running over budget — flatten the curve above 100% or lower the cap.</div>')

else:  # Action plan
    st.caption("Call plan by target tier. Lists include the HCP identifier (and team) so the field can act.")
    targeted = df_t[df_t["targeted"]].copy()
    targeted["decile"] = targeted["decile"].astype(int)
    tier_defs = [
        {"label": "A — High", "accent": "#22D3EE", "icon": "★",
         "action": f"{P['freq_A']} calls/yr + digital + KAM. Defend share, deepen relationship."},
        {"label": "B — Medium", "accent": "#8B6CFF", "icon": "◆",
         "action": f"{P['freq_B']} calls/yr + email/webinar nurture. Grow adopters, convert spreaders."},
        {"label": "C — Low", "accent": "#6B7393", "icon": "○",
         "action": f"{P['freq_C']} calls/yr or digital/inside-sales. Maintain, don't over-invest."},
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
              f'<span style="color:#9AA6CC;font-size:.8rem">· {len(sub)} HCPs</span></div>'
              f'<div style="color:#c4b5ff;font-size:.9rem;margin-top:.3rem"><b>Action:</b> {td["action"]}</div></div>')
        cols_show = [c for c in ["hcp_id", "team", "specialty", "geo", "decile", "potential", "planned_calls"] if c in sub.columns]
        with st.expander(f"View & download {td['label']} call list ({len(sub)} HCPs)"):
            st.dataframe(sub[cols_show], use_container_width=True, hide_index=True, key=f"tb_{td['label']}")
            st.download_button(f"⬇ {td['label']} call list (CSV)", sub[cols_show].to_csv(index=False),
                               file_name=f"call_list_{td['label'][0]}.csv", mime="text/csv", key=f"dl_{td['label']}")

st.caption("AI-assisted SFE model (decile/access segmentation · workload build-up · multi-team sizing · org design · "
           f"goal-attainment IC). Directional planning tool. For a tailored engagement: {PROFILE['email']}.")
