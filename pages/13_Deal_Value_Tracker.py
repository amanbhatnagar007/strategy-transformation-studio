import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.uploads import ColumnSchema, Col, data_input

st.set_page_config(page_title="Deal Value Tracker", page_icon="📈", layout="wide")
page_header("📈 Deal Value Tracker",
            "Track synergy capture against plan over time — cumulative planned vs actual, run-rate "
            "attainment, variance and a projected full-year landing — so value-creation stays on the rails.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Synergy plan")
    target = st.number_input("Full-year synergy target ($M)", 1, 100000, 120, step=5)
    curve = st.selectbox("Planned curve shape", ["S-curve (back-loaded)", "Linear", "Front-loaded"])
    n_periods = st.slider("Periods (quarters)", 4, 8, 4)

# planned cumulative fractions per period for the chosen curve
CURVES = {
    "Linear": [0.25, 0.50, 0.75, 1.00, 1.00, 1.00, 1.00, 1.00],
    "S-curve (back-loaded)": [0.12, 0.32, 0.65, 1.00, 1.00, 1.00, 1.00, 1.00],
    "Front-loaded": [0.40, 0.70, 0.90, 1.00, 1.00, 1.00, 1.00, 1.00],
}
frac = CURVES[curve][:n_periods]
# normalize so final period = 100% of target
frac = [f / frac[-1] for f in frac]
periods = [f"Q{i+1}" for i in range(n_periods)]
planned_cum = [round(target * f, 1) for f in frac]
planned_inc = [round(planned_cum[0], 1)] + [round(planned_cum[i] - planned_cum[i-1], 1) for i in range(1, n_periods)]

# demo actuals: slightly behind plan, gap widening
demo_actual_inc = [round(p * a, 1) for p, a in zip(planned_inc, [0.85, 0.92, 0.80, 0.88, 0.9, 0.9, 0.9, 0.9][:n_periods])]
demo_rows = [{"period": periods[i], "planned": planned_inc[i], "actual": demo_actual_inc[i]} for i in range(n_periods)]

schema = ColumnSchema([
    Col("period", "text", "Period label (e.g. Q1)", "Q1"),
    Col("planned", "num", "Planned synergy captured this period ($M)", "15"),
    Col("actual", "num", "Actual synergy captured this period ($M)", "12"),
])


def analyze(df):
    d = df.copy().reset_index(drop=True)
    d["Planned cum"] = d["planned"].cumsum().round(1)
    d["Actual cum"] = d["actual"].cumsum().round(1)
    d["Variance ($M)"] = (d["Actual cum"] - d["Planned cum"]).round(1)
    d["Variance %"] = (d["Variance ($M)"] / d["Planned cum"].replace(0, pd.NA) * 100).round(1)
    return d


def render(df, key=""):
    d = analyze(df)
    captured = d["Actual cum"].iloc[-1]
    pct_of_target = round(captured / target * 100, 1) if target else 0
    last_var = d["Variance %"].iloc[-1]
    last_var = 0.0 if pd.isna(last_var) else last_var
    # run-rate: latest period actual annualized vs target
    run_rate = round(d["actual"].iloc[-1] * 4, 1)
    rr_attain = round(run_rate / target * 100, 1) if target else 0
    # projected landing: scale planned full plan by current attainment ratio
    plan_total = d["planned"].sum()
    attain_ratio = (captured / d["Planned cum"].iloc[-1]) if d["Planned cum"].iloc[-1] else 0
    projected = round(plan_total * attain_ratio, 1)

    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="glass metric"><div class="v">{pct_of_target:.0f}%</div><div class="l">Of target captured</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="glass metric"><div class="v">{last_var:+.0f}%</div><div class="l">Variance to plan</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="glass metric"><div class="v">${projected:,.0f}M</div><div class="l">Projected full-year</div></div>', unsafe_allow_html=True)

    cL, cR = st.columns([3, 2])
    with cL:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d["period"], y=d["Planned cum"], name="Planned (cum)",
                                 mode="lines+markers", line=dict(color="#8B6CFF", width=3)))
        fig.add_trace(go.Scatter(x=d["period"], y=d["Actual cum"], name="Actual (cum)",
                                 mode="lines+markers", line=dict(color="#22D3EE", width=3)))
        fig.add_hline(y=target, line_dash="dot", line_color="#9AA6CC",
                      annotation_text=f"Target ${target}M", annotation_position="top left")
        fig.update_layout(template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Cumulative synergies ($M)",
                          margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True, key=f"cum_{key}")
    with cR:
        fig2 = go.Figure(go.Bar(x=d["period"], y=d["Variance ($M)"],
                                marker_color=["#34D399" if v >= 0 else "#F87171" for v in d["Variance ($M)"]],
                                text=[f"{v:+.0f}" for v in d["Variance ($M)"]], textposition="outside"))
        fig2.update_layout(template="plotly_dark", height=360, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Variance to plan ($M)",
                           margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True, key=f"var_{key}")

    st.dataframe(d.rename(columns={"period": "Period", "planned": "Planned ($M)", "actual": "Actual ($M)"}),
                 use_container_width=True, hide_index=True, key=f"tbl_{key}")
    return d, pct_of_target, last_var, projected, rr_attain


t1, tU, t2 = st.tabs(["📊 Capture vs plan", "📤 Upload your data", "📋 Executive summary"])

with t1:
    st.markdown("#### Cumulative synergy capture: planned vs actual")
    res = render(pd.DataFrame(demo_rows), "demo")

with tU:
    st.markdown("#### Track your own deal")
    st.caption("One row per period with planned and actual synergy captured that period ($M). Only the "
               "rows you provide are analyzed.")
    user_df = data_input(schema, demo_rows, key="dealtrack")
    if user_df is not None and not user_df.empty:
        render(user_df, "upload")

with t2:
    st.markdown("#### Board-ready read")
    d, pct_of_target, last_var, projected, rr_attain = res
    status = ("ahead of plan" if last_var > 2 else "broadly on plan" if last_var > -5 else "behind plan")
    gap_to_target = round(target - projected, 1)
    summary = (
        f"Through {d['period'].iloc[-1]}, the deal has captured <b>${d['Actual cum'].iloc[-1]:,.0f}M</b> of "
        f"synergies — <b>{pct_of_target:.0f}% of the ${target}M target</b> and <b>{last_var:+.0f}%</b> versus "
        f"the {curve.split(' (')[0].lower()} plan, i.e. <b>{status}</b>. Latest-period run-rate annualizes to "
        f"~{rr_attain:.0f}% of target. On the current attainment trajectory the deal is projected to land at "
        f"<b>${projected:,.0f}M</b>"
        f"{f', a ${gap_to_target:,.0f}M shortfall to target' if gap_to_target > 0 else ', at or above target'}. "
        "Figures are directional from the reported periods — close any negative variance with named "
        "initiative owners and a re-forecast before the next steering committee."
    )
    glass(f"<div style='font-size:.98rem;line-height:1.7;color:#dfe5fb'>{summary}</div>")
    st.download_button("⬇ Download capture tracker (CSV)",
                       d.rename(columns={"period": "Period"}).to_csv(index=False),
                       file_name="deal_value_tracker.csv", mime="text/csv")

st.caption("AI-assisted heuristic tracker for synergy-capture monitoring. Directional, not investment "
           f"advice. For deal support: {PROFILE['email']}.")
