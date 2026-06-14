import streamlit as st
import pandas as pd
import plotly.express as px
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.trends_data import TRENDS, THEMES

st.set_page_config(page_title="2025 MedTech Trends", page_icon="📰", layout="wide")
page_header("📰 2025 MedTech Trends Explorer",
            "A curated point of view on where MedTech is heading — and the commercial implication of each shift. "
            "Filter by theme and time horizon.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Filter")
    themes = st.multiselect("Theme", THEMES, default=THEMES)
    horizons = st.multiselect("Horizon", ["Now", "12–24m", "24m+"], default=["Now", "12–24m", "24m+"])
    min_impact = st.slider("Min. impact", 1, 5, 1)

flt = [t for t in TRENDS if t["theme"] in themes and t["horizon"] in horizons and t["impact"] >= min_impact]

k1, k2, k3 = st.columns(3)
k1.markdown(f'<div class="glass metric"><div class="v">{len(flt)}</div><div class="l">Trends shown</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="glass metric"><div class="v">{sum(1 for t in flt if t["horizon"]=="Now")}</div><div class="l">Act now</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="glass metric"><div class="v">{sum(1 for t in flt if t["impact"]>=4)}</div><div class="l">High impact</div></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🗂️ Trend cards", "📊 Impact map"])

with t1:
    if not flt:
        st.info("No trends match the filter — widen it in the sidebar.")
    for i in range(0, len(flt), 2):
        cols = st.columns(2)
        for c, t in zip(cols, flt[i:i+2]):
            with c:
                stars = "●" * t["impact"] + "○" * (5 - t["impact"])
                glass(f'<div style="display:flex;justify-content:space-between">'
                      f'<span class="pill pill-x">{t["theme"]}</span>'
                      f'<span style="color:#9AA6CC;font-size:.75rem">{t["horizon"]} · {stars}</span></div>'
                      f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:1.05rem;margin:.4rem 0 .2rem">{t["title"]}</div>'
                      f'<div style="color:#aab4d6;font-size:.85rem;line-height:1.5">{t["what"]}</div>'
                      f'<div style="color:#c4b5ff;font-size:.83rem;margin-top:.45rem"><b>Implication:</b> {t["implication"]}</div>')

with t2:
    df = pd.DataFrame(flt)
    if not df.empty:
        order = {"Now": 1, "12–24m": 2, "24m+": 3}
        df["h"] = df["horizon"].map(order)
        fig = px.scatter(df, x="h", y="impact", color="theme", text="title", size=[18]*len(df),
                         size_max=20, height=440)
        fig.update_traces(textposition="top center", textfont=dict(size=9, color="#cdd6f5"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(tickvals=[1, 2, 3], ticktext=["Now", "12–24m", "24m+"], title="Horizon"),
                          yaxis_title="Impact", legend_title="", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.download_button("⬇ Download trends (CSV)", pd.DataFrame(TRENDS).to_csv(index=False),
                       file_name="medtech_trends_2025.csv", mime="text/csv")

st.caption("Curated point of view for discussion — directional, not a forecast. "
           f"To pressure-test these against your portfolio: {PROFILE['email']}.")
