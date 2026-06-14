import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.salesforce_logic import size_segments, size_from_df, sf_summary
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="Sales Force Sizer", page_icon="🧭", layout="wide")
page_header("🧭 Sales Force Sizer",
            "Size the field force and design territories from the bottom up — turn an account base and a "
            "call plan into required reps, coverage gaps and workload balance.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Account base by tier")
    a_acc = st.number_input("Tier A accounts", 0, 100000, 300, step=10)
    b_acc = st.number_input("Tier B accounts", 0, 100000, 800, step=10)
    c_acc = st.number_input("Tier C accounts", 0, 100000, 1500, step=10)
    st.header("Target calls / account / year")
    a_calls = st.slider("Tier A frequency", 0.0, 36.0, 18.0, 0.5)
    b_calls = st.slider("Tier B frequency", 0.0, 36.0, 10.0, 0.5)
    c_calls = st.slider("Tier C frequency", 0.0, 36.0, 4.0, 0.5)
    st.header("Rep capacity")
    selling_days = st.slider("Working selling days / year", 120, 240, 200)
    calls_per_day = st.slider("Calls / rep / day", 2.0, 12.0, 6.0, 0.5)
    current_reps = st.number_input("Current reps deployed", 0, 5000, 35, step=1)

segments = [
    {"tier": "Tier A", "accounts": a_acc, "calls_per_account": a_calls},
    {"tier": "Tier B", "accounts": b_acc, "calls_per_account": b_calls},
    {"tier": "Tier C", "accounts": c_acc, "calls_per_account": c_calls},
]
z = size_segments(segments, selling_days, calls_per_day, current_reps)

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="glass metric"><div class="v">{z["reps_required_ceil"]}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{z["coverage"]}%</div><div class="l">Coverage of demand</div></div>', unsafe_allow_html=True)
gap = z["gap"]
k3.markdown(f'<div class="glass metric"><div class="v">{"+" if gap>0 else ""}{gap}</div><div class="l">Reps gap vs current</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="glass metric"><div class="v">{z["capacity"]:,.0f}</div><div class="l">Calls / rep / yr capacity</div></div>', unsafe_allow_html=True)

t1, t2, tU, t3 = st.tabs(["📊 Demand & sizing", "⚖️ Coverage", "📤 Upload your data", "📋 Executive summary"])

with t1:
    st.markdown("#### Call demand by segment")
    df = pd.DataFrame(z["rows"])
    fig = go.Figure(go.Bar(x=df["Segment"], y=df["Annual calls"], marker_color="#8B6CFF",
                           text=[f"{v:,}" for v in df["Annual calls"]], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Annual calls",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div style="color:#aab4d6;font-size:.85rem">Assumptions: {selling_days} selling days × '
          f'{calls_per_day:.0f} calls/day = <b>{z["capacity"]:,.0f}</b> calls per rep per year. '
          f'Total call plan: <b>{z["total_calls"]:,.0f}</b> calls.</div>')
    st.dataframe(df, use_container_width=True, hide_index=True)

with t2:
    st.markdown("#### Reps required vs current")
    fig = go.Figure(go.Bar(x=["Required", "Current"],
                           y=[z["reps_required_ceil"], z["current_reps"]],
                           marker_color=["#8B6CFF", "#22D3EE"],
                           text=[z["reps_required_ceil"], z["current_reps"]], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Reps",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    wl = z["workload_per_current_rep"]
    wl_txt = f"{wl:,.0f} calls/rep" if wl != float("inf") else "n/a (no reps deployed)"
    glass(f'<div class="bullet">Workload at current staffing: {wl_txt} '
          f'(vs {z["capacity"]:,.0f} capacity)</div>'
          f'<div class="bullet">Coverage of the call plan: {z["coverage"]}%</div>')

with tU:
    st.markdown("#### Size from a real account list")
    schema = ColumnSchema([
        Col("account", "text", "Account / customer name", "Mercy General"),
        Col("segment", "text", "Tier / segment label", "Tier A"),
        Col("annual_potential", "num", "Estimated annual revenue potential ($)", "250000"),
        Col("calls_needed", "num", "Target calls/visits this account needs per year", "18"),
    ])
    demo = [
        {"account": "Mercy General", "segment": "Tier A", "annual_potential": 420000, "calls_needed": 20},
        {"account": "St. Luke's", "segment": "Tier A", "annual_potential": 380000, "calls_needed": 18},
        {"account": "Valley Health", "segment": "Tier A", "annual_potential": 350000, "calls_needed": 18},
        {"account": "Northside Clinic", "segment": "Tier B", "annual_potential": 180000, "calls_needed": 12},
        {"account": "Lakeshore Med", "segment": "Tier B", "annual_potential": 160000, "calls_needed": 10},
        {"account": "Pine Ridge", "segment": "Tier B", "annual_potential": 140000, "calls_needed": 10},
        {"account": "Eastgate Care", "segment": "Tier B", "annual_potential": 120000, "calls_needed": 9},
        {"account": "Riverbend GP", "segment": "Tier C", "annual_potential": 60000, "calls_needed": 5},
        {"account": "Maple Family", "segment": "Tier C", "annual_potential": 48000, "calls_needed": 4},
        {"account": "Sunset Practice", "segment": "Tier C", "annual_potential": 42000, "calls_needed": 4},
        {"account": "Oak Hollow", "segment": "Tier C", "annual_potential": 38000, "calls_needed": 4},
        {"account": "Birch Clinic", "segment": "Tier C", "annual_potential": 35000, "calls_needed": 3},
        {"account": "Cedar Health", "segment": "Tier C", "annual_potential": 30000, "calls_needed": 3},
        {"account": "Willow Care", "segment": "Tier C", "annual_potential": 28000, "calls_needed": 3},
    ]
    user_df = data_input(schema, demo, demo_label="Use demo account list", key="sfsize")
    if user_df is not None and not user_df.empty:
        zz = size_from_df(user_df, selling_days, calls_per_day, current_reps)
        a, b, cc = st.columns(3)
        a.markdown(f'<div class="glass metric"><div class="v">{zz["reps_required_ceil"]}</div><div class="l">Reps required</div></div>', unsafe_allow_html=True)
        b.markdown(f'<div class="glass metric"><div class="v">{zz["coverage"]}%</div><div class="l">Coverage</div></div>', unsafe_allow_html=True)
        g = zz["gap"]
        cc.markdown(f'<div class="glass metric"><div class="v">{"+" if g>0 else ""}{g}</div><div class="l">Gap vs current</div></div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(zz["rows"]), use_container_width=True, hide_index=True)
        st.caption(f"Sized from {len(user_df)} uploaded accounts ({zz['total_calls']:,.0f} total calls).")

with t3:
    st.markdown("#### Board-ready read")
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{sf_summary(z)}</div>')
    st.download_button("⬇ Download sizing by segment (CSV)", pd.DataFrame(z["rows"]).to_csv(index=False),
                       file_name="salesforce_sizing.csv", mime="text/csv")

st.caption("AI-assisted heuristic sizing model for territory & headcount framing. Directional, not a "
           f"deployment plan. For a tailored engagement: {PROFILE['email']}.")
