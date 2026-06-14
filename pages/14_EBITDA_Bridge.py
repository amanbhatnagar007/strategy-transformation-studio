import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="EBITDA Improvement Bridge", page_icon="💹", layout="wide")
page_header("💹 EBITDA Improvement Bridge",
            "Walk from today's EBITDA to a target, lever by lever — price, volume, COGS, SG&A and mix — "
            "and see the margin uplift the value-creation plan delivers.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Starting position")
    rev = st.number_input("Starting revenue ($M)", 10, 200000, 1200, step=10)
    margin_pct = st.slider("Starting EBITDA margin (%)", 1, 60, 14)
    st.header("Improvement levers")
    price_up = st.slider("Price uplift (%)", 0.0, 15.0, 2.0, 0.5,
                         help="Net realized price increase on existing volume.")
    vol_growth = st.slider("Volume growth (%)", 0.0, 25.0, 4.0, 0.5,
                           help="Incremental volume, earned at current margin.")
    cogs_red = st.slider("COGS reduction (%)", 0.0, 15.0, 3.0, 0.5,
                         help="Reduction in cost of goods as a % of revenue.")
    sga_red = st.slider("SG&A reduction (%)", 0.0, 15.0, 2.5, 0.5,
                        help="Reduction in SG&A as a % of revenue.")
    mix_up = st.slider("Mix improvement (%)", 0.0, 8.0, 1.0, 0.5,
                       help="Margin points gained from shifting to richer products/channels.")

start_ebitda = rev * margin_pct / 100.0

# Lever $ impacts (all $M). Price drops ~fully to EBITDA; volume at current margin.
price_impact = rev * price_up / 100.0
vol_impact = rev * (vol_growth / 100.0) * (margin_pct / 100.0)
cogs_impact = rev * cogs_red / 100.0
sga_impact = rev * sga_red / 100.0
mix_impact = rev * mix_up / 100.0

levers = {
    "Price uplift": round(price_impact, 1),
    "Volume growth": round(vol_impact, 1),
    "COGS reduction": round(cogs_impact, 1),
    "SG&A reduction": round(sga_impact, 1),
    "Mix improvement": round(mix_impact, 1),
}
total_uplift = round(sum(levers.values()), 1)
target_ebitda = round(start_ebitda + total_uplift, 1)
# new revenue grows with volume; price uplift also lifts revenue
new_rev = rev * (1 + vol_growth / 100.0) + price_impact
new_margin = target_ebitda / new_rev * 100.0 if new_rev else 0.0
margin_delta_bps = round((new_margin - margin_pct) * 100)

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${start_ebitda:,.0f}M</div><div class="l">Start EBITDA</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${target_ebitda:,.0f}M</div><div class="l">Target EBITDA</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">+{margin_delta_bps:,} bps</div><div class="l">Margin delta</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🧱 EBITDA bridge", "📊 Lever detail", "📋 Executive summary"])

with t1:
    st.markdown("#### From start to target EBITDA")
    measures = ["absolute"] + ["relative"] * len(levers) + ["total"]
    x = ["Start EBITDA"] + list(levers.keys()) + ["Target EBITDA"]
    y = [round(start_ebitda, 1)] + list(levers.values()) + [target_ebitda]
    text = [f"${round(start_ebitda,1)}M"] + [f"+${v}M" for v in levers.values()] + [f"${target_ebitda}M"]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=measures, x=x, y=y, text=text, textposition="outside",
        connector={"line": {"color": "rgba(255,255,255,.2)"}},
        increasing={"marker": {"color": "#22D3EE"}},
        decreasing={"marker": {"color": "#EC4899"}},
        totals={"marker": {"color": "#8B6CFF"}}))
    fig.update_layout(template="plotly_dark", height=380, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="EBITDA ($M)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass(f'<div style="color:#aab4d6;font-size:.85rem">Margin moves from <b style="color:#fff">{margin_pct}%</b> '
          f'to <b style="color:#fff">{new_margin:.1f}%</b> on a revenue base of ~${new_rev:,.0f}M. '
          'Price and cost levers drop close to fully to EBITDA; volume is credited only at the current '
          'margin and mix is a directional margin-point assumption — validate each before committing.</div>')

with t2:
    st.markdown("#### EBITDA impact by lever")
    df = pd.DataFrame([{"Lever": k, "EBITDA impact ($M)": v,
                        "% of total uplift": f"{(v/total_uplift*100 if total_uplift else 0):.0f}%"}
                       for k, v in levers.items()])
    fig = go.Figure(go.Bar(x=list(levers.values()), y=list(levers.keys()), orientation="h",
                           marker_color="#8B6CFF", text=[f"${v}M" for v in levers.values()],
                           textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="EBITDA impact ($M)",
                      yaxis=dict(autorange="reversed"), margin=dict(l=10, r=30, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    top = max(levers, key=levers.get)
    summary = (
        f"The plan lifts EBITDA from <b>${start_ebitda:,.0f}M</b> to <b>${target_ebitda:,.0f}M</b> "
        f"(+${total_uplift:,.0f}M), improving margin by <b>~{margin_delta_bps:,} bps</b> from "
        f"{margin_pct}% to {new_margin:.1f}%. The single largest contributor is <b>{top}</b> "
        f"(${levers[top]}M). Cost levers (COGS, SG&A) are higher-confidence and front-loadable; "
        f"price and mix require commercial proof points; volume growth should be underwritten against "
        f"a credible demand case. Treat these as directional heuristics for planning, then pressure-test "
        f"each lever's feasibility and timing before locking the target."
    )
    glass(f'<div style="font-size:.98rem;line-height:1.7;color:#dfe5fb">{summary}</div>')
    csv = pd.DataFrame(
        [{"Item": "Start EBITDA ($M)", "Value": round(start_ebitda, 1)}] +
        [{"Item": f"{k} ($M)", "Value": v} for k, v in levers.items()] +
        [{"Item": "Target EBITDA ($M)", "Value": target_ebitda},
         {"Item": "Start margin (%)", "Value": margin_pct},
         {"Item": "New margin (%)", "Value": round(new_margin, 1)},
         {"Item": "Margin delta (bps)", "Value": margin_delta_bps}]
    )
    st.download_button("⬇ Download EBITDA bridge (CSV)", csv.to_csv(index=False),
                       file_name="ebitda_bridge.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for EBITDA-improvement framing. Directional planning tool. "
           f"For a transformation engagement: {PROFILE['email']}.")
