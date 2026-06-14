import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Carve-out Readiness", page_icon="✂️", layout="wide")
page_header("✂️ Carve-out Readiness Analyzer",
            "Size the separation challenge for a divestiture or carve-out — stranded cost, one-time "
            "separation cost, the TSA exit path to standalone, and an entanglement-driven complexity rating.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Carve-out scope")
    tgt_rev = st.number_input("Carve-out revenue ($M)", 10, 100000, 800, step=10)
    shared_pct = st.slider("Shared-services cost (% of revenue)", 1, 40, 14)
    entanglement = st.slider("Entanglement complexity (1-10)", 1, 10, 6)
    n_tsa = st.number_input("# of TSAs needed", 0, 60, 12, step=1)
    tsa_months = st.slider("Expected TSA duration (months)", 1, 36, 12)

shared_cost = tgt_rev * shared_pct / 100  # $M of shared-services cost the unit consumed
# stranded cost: a fraction of shared cost can't be cleanly exited at separation; entanglement drives it up
stranded_frac = min(0.6, 0.18 + 0.04 * entanglement)
stranded_cost = round(shared_cost * stranded_frac, 1)
stranded_pct = round(stranded_cost / tgt_rev * 100, 1) if tgt_rev else 0

# one-time separation cost: scales with shared cost, entanglement and TSA count
separation_cost = round(shared_cost * (0.35 + 0.05 * entanglement) + n_tsa * 0.4, 1)

# months to standalone: TSA duration plus a wind-down tail driven by entanglement & TSA count
months_to_standalone = round(tsa_months + entanglement * 0.6 + n_tsa * 0.15)

if entanglement <= 3 and n_tsa <= 6:
    complexity = "Low"
elif entanglement <= 6 and n_tsa <= 18:
    complexity = "Moderate"
else:
    complexity = "High"

# TSA exit by function (illustrative split of the TSA portfolio)
TSA_FUNCTIONS = {
    "IT / applications": 1.4,
    "Finance / ERP": 1.2,
    "HR / payroll": 0.8,
    "Procurement": 0.9,
    "Facilities": 0.7,
}
fsum = sum(TSA_FUNCTIONS.values())
tsa_rows = []
for fn, factor in TSA_FUNCTIONS.items():
    exit_m = round(min(tsa_months * factor / (fsum / len(TSA_FUNCTIONS)),
                       tsa_months + entanglement))
    cnt = max(1, round(n_tsa * factor / fsum)) if n_tsa else 0
    tsa_rows.append({"Function": fn, "TSAs": cnt, "Exit month": exit_m})
tsa_df = pd.DataFrame(tsa_rows)

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${stranded_cost:,.0f}M</div><div class="l">Stranded cost ({stranded_pct}% of rev)</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${separation_cost:,.0f}M</div><div class="l">One-time separation cost</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">~{months_to_standalone}</div><div class="l">Months to standalone</div></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🧱 Cost bridge", "⏱️ TSA exit timeline", "📋 Executive summary"])

with t1:
    st.markdown("#### From shared-services cost to stranded & separation cost")
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Shared-services cost", "Cleanly exited", "Stranded (residual)", "Stranded cost"],
        y=[shared_cost, -(shared_cost - stranded_cost), 0, stranded_cost],
        text=[f"${shared_cost:.0f}M", f"-${shared_cost - stranded_cost:.0f}M", "", f"${stranded_cost:.0f}M"],
        connector={"line": {"color": "rgba(255,255,255,.2)"}},
        decreasing={"marker": {"color": "#22D3EE"}},
        totals={"marker": {"color": "#8B6CFF"}}))
    fig.update_layout(template="plotly_dark", height=340, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", yaxis_title="$M",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    glass('<div style="color:#aab4d6;font-size:.85rem">Stranded cost is the shared-services overhead the '
          'remaining business keeps but can no longer fully attribute to the divested unit. It must be removed '
          'through a dedicated stranded-cost program or it erodes RemainCo margin post-close.</div>')

with t2:
    st.markdown("#### TSA exit timeline by function")
    fig = go.Figure(go.Bar(
        x=tsa_df["Exit month"], y=tsa_df["Function"], orientation="h",
        marker_color="#8B6CFF",
        text=[f"{m} mo · {c} TSA" for m, c in zip(tsa_df["Exit month"], tsa_df["TSAs"])],
        textposition="outside"))
    fig.update_layout(template="plotly_dark", height=320, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Exit month",
                      yaxis=dict(autorange="reversed"), margin=dict(l=10, r=40, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(tsa_df, use_container_width=True, hide_index=True)

with t3:
    st.markdown("#### Board-ready read")
    summary = (
        f"On ${tgt_rev:,.0f}M of carve-out revenue with shared-services cost at {shared_pct}% of revenue, "
        f"the separation carries an estimated <b>${stranded_cost:,.0f}M of stranded cost</b> "
        f"(~{stranded_pct}% of revenue) and <b>${separation_cost:,.0f}M of one-time separation cost</b>. "
        f"Entanglement is rated {entanglement}/10 with {n_tsa} TSAs at ~{tsa_months} months each, giving an "
        f"overall complexity of <b>{complexity}</b> and an estimated <b>~{months_to_standalone} months to a "
        f"fully standalone operating model</b>. Priority: stand up a stranded-cost takeout program and a "
        "TSA-exit plan from Day-1 so dis-synergies do not become permanent. Figures are directional "
        "heuristics for separation framing — validate against a function-level separation blueprint."
    )
    glass(f"<div style='font-size:.98rem;line-height:1.7;color:#dfe5fb'>{summary}</div>")
    out = pd.DataFrame([
        {"Metric": "Carve-out revenue ($M)", "Value": tgt_rev},
        {"Metric": "Shared-services cost ($M)", "Value": round(shared_cost, 1)},
        {"Metric": "Stranded cost ($M)", "Value": stranded_cost},
        {"Metric": "Stranded cost (% rev)", "Value": stranded_pct},
        {"Metric": "Separation cost ($M)", "Value": separation_cost},
        {"Metric": "Months to standalone", "Value": months_to_standalone},
        {"Metric": "Complexity", "Value": complexity},
    ])
    st.download_button("⬇ Download carve-out summary (CSV)", out.to_csv(index=False),
                       file_name="carveout_readiness.csv", mime="text/csv")

st.caption("AI-assisted heuristic model for carve-out / separation framing. Directional, not investment "
           f"advice. For deal support: {PROFILE['email']}.")
