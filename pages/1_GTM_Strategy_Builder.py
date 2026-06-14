import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from lib.theme import page_header, glass
from lib.profile import PROFILE

st.set_page_config(page_title="GTM Strategy Builder", page_icon="🚀", layout="wide")
page_header("🚀 GTM Strategy Builder",
            "Design a go-to-market plan from a few inputs — channel mix, segmentation, and a launch roadmap.")
st.page_link("Home.py", label="← Back to Studio")

# ---------------- Inputs ----------------
with st.sidebar:
    st.header("Inputs")
    product = st.text_input("Product / offering", "Next-gen CGM sensor")
    sector = st.selectbox("Sector", ["MedTech", "Pharma", "Provider / Hospital",
                                     "Payer / PBM", "Consumer", "Other"])
    stage = st.selectbox("Launch stage", ["New product launch", "New market entry",
                                          "Re-launch / reposition", "Portfolio expansion"])
    model = st.selectbox("Commercial model", ["Capital / one-time", "Subscription",
                                              "Pay-per-use", "Hybrid"])
    buyers = st.multiselect("Primary buyers",
                            ["Clinicians / HCPs", "Hospital procurement", "Payers",
                             "Patients / consumers", "Distributors", "Health systems (IDN)"],
                            default=["Clinicians / HCPs", "Hospital procurement"])
    market_size = st.number_input("Addressable market ($M)", 50, 100000, 2000, step=50)
    price = st.number_input("Avg. annual price / unit ($)", 10, 1_000_000, 1200, step=10)
    sales_cycle = st.slider("Sales cycle (months)", 1, 24, 6)
    differentiation = st.slider("Differentiation vs. competition (1–10)", 1, 10, 7)
    digital = st.slider("Digital maturity of buyers (1–10)", 1, 10, 6)

# ---------------- Logic (deterministic "AI") ----------------
def channel_mix(buyers, sales_cycle, digital, model):
    field = 35 + 2.5 * sales_cycle
    inside = 15 + (10 - digital) * 1.0
    dgtl = 8 + digital * 2.2                     # digital / e-commerce
    partner = 12 + (8 if "Distributors" in buyers else 0)
    kam = 10 + (12 if ("Health systems (IDN)" in buyers or "Hospital procurement" in buyers) else 0)
    if model in ("Subscription", "Pay-per-use"):
        dgtl += 8; inside += 6; field -= 8
    raw = {"Field sales": field, "Inside sales": inside, "Digital / self-serve": dgtl,
           "Channel / distributors": partner, "Key account mgmt": kam}
    tot = sum(raw.values())
    return {k: round(v / tot * 100) for k, v in raw.items()}

def segments(sector, buyers):
    base = [("Innovators / early adopters", "High differentiation receptivity", 15),
            ("Value-driven mainstream", "ROI & outcomes focused", 45),
            ("Late / price-sensitive", "Win on TCO & service", 40)]
    return base

def readiness(differentiation, digital, sales_cycle):
    score = 0.45 * differentiation * 10 + 0.30 * digital * 10 + 0.25 * max(0, (24 - sales_cycle)) / 24 * 100
    return round(min(99, score))

def revenue_ramp(market_size, price, differentiation):
    share_y3 = min(0.25, 0.02 + differentiation * 0.012)        # capped SOM
    peak = market_size * share_y3
    curve = [round(peak * f, 1) for f in (0.08, 0.22, 0.45, 0.72, 1.0)]
    return curve, round(share_y3 * 100, 1)

mix = channel_mix(buyers, sales_cycle, digital, model)
segs = segments(sector, buyers)
ready = readiness(differentiation, digital, sales_cycle)
ramp, som = revenue_ramp(market_size, price, differentiation)

# ---------------- Output ----------------
c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="glass metric"><div class="v">{ready}/100</div><div class="l">Launch readiness</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="glass metric"><div class="v">{som}%</div><div class="l">Est. Yr-3 market share</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="glass metric"><div class="v">${ramp[-1]:,.0f}M</div><div class="l">Yr-5 revenue potential</div></div>', unsafe_allow_html=True)

st.markdown("### Recommended channel mix")
left, right = st.columns([1, 1])
with left:
    fig = go.Figure(go.Bar(x=list(mix.values()), y=list(mix.keys()), orientation="h",
                           marker_color="#7C5CFF", text=[f"{v}%" for v in mix.values()],
                           textposition="outside"))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=20, t=10, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis_title="% of commercial effort")
    st.plotly_chart(fig, use_container_width=True)
with right:
    yrs = ["Y1", "Y2", "Y3", "Y4", "Y5"]
    fig2 = go.Figure(go.Scatter(x=yrs, y=ramp, mode="lines+markers", fill="tozeroy",
                                line=dict(color="#22D3EE", width=3)))
    fig2.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       yaxis_title="Revenue ($M)", title="Revenue ramp")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Target segments")
scols = st.columns(3)
for col, (name, why, pct) in zip(scols, segs):
    with col:
        glass(f'<div style="font-weight:600;color:#fff">{name}</div>'
              f'<div style="color:#9AA5C4;font-size:.8rem;margin:.2rem 0">{why}</div>'
              f'<div style="color:#22D3EE;font-weight:600">{pct}% of market</div>')

st.markdown("### 90-day launch roadmap")
roadmap = [
    ("Days 0–30 · Foundation", f"Lock value proposition for {product}; finalize segmentation; "
     f"stand up {max(mix, key=mix.get).lower()} as the lead channel; align pricing for the {model.lower()} model."),
    ("Days 31–60 · Mobilize", "Train field & inside teams; build KAM target list for top accounts; "
     "configure CRM, incentives and KPIs; launch digital demand-gen."),
    ("Days 61–90 · Scale", "Activate full channel mix; weekly funnel reviews; tune messaging by segment; "
     "set the value-tracking dashboard for the revenue ramp above."),
]
for title, body in roadmap:
    glass(f'<div style="font-weight:600;color:#c4b5ff">{title}</div>'
          f'<div style="color:#cdd5ee;font-size:.88rem;line-height:1.5;margin-top:.2rem">{body}</div>')

with st.expander("Download plan (CSV)"):
    df = pd.DataFrame({"channel": mix.keys(), "effort_pct": mix.values()})
    st.download_button("Download channel mix", df.to_csv(index=False),
                       file_name="gtm_channel_mix.csv", mime="text/csv")

st.caption("Heuristic model grounded in commercial-strategy frameworks. "
           f"For a tailored engagement: {PROFILE['email']}.")
