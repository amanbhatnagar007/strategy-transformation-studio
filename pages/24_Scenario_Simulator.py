import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="Scenario Simulator", page_icon="🎚️", layout="wide")
page_header("🎚️ Scenario & Sensitivity Simulator",
            "Stress-test any business case: define a base outcome and its drivers, then see which assumptions move "
            "the answer most (tornado) and how downside/upside scenarios play out. All math, no guessing.")
st.markdown('<a href="/" target="_self" style="color:#22D3EE;text-decoration:none;font-size:.9rem">← Back to Studio</a>', unsafe_allow_html=True)

st.caption("Outcome is modeled as Base × ∏(1 + driver swing). Set each driver's low/high % swing and its weight.")

with st.sidebar:
    st.header("Base case")
    base = st.number_input("Base outcome (e.g. EBITDA $M)", 1.0, 1_000_000.0, 100.0, step=5.0)
    n = st.slider("Number of drivers", 2, 6, 4)

default_drivers = [("Volume", -15, 20, 1.0), ("Price", -8, 10, 1.0),
                   ("Cost inflation", -12, 6, 0.8), ("Mix", -6, 8, 0.6),
                   ("FX", -5, 5, 0.4), ("Churn", -10, 5, 0.7)]

drivers = []
st.markdown("#### Drivers")
for i in range(n):
    name0, lo0, hi0, w0 = default_drivers[i]
    with st.expander(f"Driver {i+1}: {name0}", expanded=i < 2):
        c = st.columns(4)
        name = c[0].text_input("Name", name0, key=f"n{i}")
        lo = c[1].number_input("Low swing %", -90, 0, lo0, key=f"lo{i}")
        hi = c[2].number_input("High swing %", 0, 200, hi0, key=f"hi{i}")
        w = c[3].slider("Weight", 0.0, 1.0, w0, key=f"w{i}")
        drivers.append({"name": name, "lo": lo, "hi": hi, "w": w})

def outcome(swings):
    o = base
    for d, s in zip(drivers, swings):
        o *= (1 + d["w"] * s / 100)
    return o

downside = outcome([d["lo"] for d in drivers])
upside = outcome([d["hi"] for d in drivers])

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">${downside:,.0f}</div><div class="l">Downside</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">${base:,.0f}</div><div class="l">Base</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">${upside:,.0f}</div><div class="l">Upside</div></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🌪️ Tornado (sensitivity)", "📋 Scenario table"])

with t1:
    st.markdown("#### Which assumption moves the answer most")
    rows = []
    for d in drivers:
        lo_o = base * (1 + d["w"] * d["lo"] / 100)
        hi_o = base * (1 + d["w"] * d["hi"] / 100)
        rows.append({"name": d["name"], "low": lo_o - base, "high": hi_o - base,
                     "range": abs(hi_o - lo_o)})
    rows.sort(key=lambda r: r["range"])
    fig = go.Figure()
    fig.add_trace(go.Bar(y=[r["name"] for r in rows], x=[r["low"] for r in rows], orientation="h",
                         name="Low", marker_color="#EC4899", base=0))
    fig.add_trace(go.Bar(y=[r["name"] for r in rows], x=[r["high"] for r in rows], orientation="h",
                         name="High", marker_color="#22D3EE", base=0))
    fig.update_layout(template="plotly_dark", height=320, barmode="overlay", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Δ outcome vs base",
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    top = max(rows, key=lambda r: r["range"])
    glass(f'<div style="color:#dfe5fb"><b>{top["name"]}</b> is the swing factor — it moves the outcome the most, '
          f'so it deserves the tightest estimate and the clearest mitigation.</div>')

with t2:
    df = pd.DataFrame([{"Scenario": "Downside (all low)", "Outcome": round(downside, 1),
                        "vs base %": round((downside/base-1)*100, 1)},
                       {"Scenario": "Base", "Outcome": round(base, 1), "vs base %": 0.0},
                       {"Scenario": "Upside (all high)", "Outcome": round(upside, 1),
                        "vs base %": round((upside/base-1)*100, 1)}])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("⬇ Download scenarios (CSV)", df.to_csv(index=False),
                       file_name="scenarios.csv", mime="text/csv")

st.caption("A transparent sensitivity model driven entirely by your inputs. "
           f"For a full business-case model: {PROFILE['email']}.")
