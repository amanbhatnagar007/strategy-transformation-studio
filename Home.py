import streamlit as st
from lib.theme import inject, glass, img_b64
from lib.profile import PROFILE, CATALOG, HIGHLIGHTS

st.set_page_config(page_title=f"{PROFILE['name']} — {PROFILE['studio']}",
                   page_icon="🧠", layout="wide")
inject()

# ---------- Hero: photo + intro ----------
left, right = st.columns([1, 2.3], gap="large")
with left:
    b64 = img_b64("aman.png")
    if b64:
        st.markdown(
            f'<div class="photo-wrap"><div class="photo-ring">'
            f'<img src="data:image/png;base64,{b64}"/></div></div>', unsafe_allow_html=True)
with right:
    st.markdown(
        f"""
        <p class="hero-name">{PROFILE['name']}</p>
        <p class="hero-sub">{PROFILE['studio']}</p>
        <p class="hero-tag">{PROFILE['tagline']}</p>
        <p class="hero-summary">{PROFILE['summary']}</p>
        """, unsafe_allow_html=True)

# ---------- Metrics ----------
st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
cols = st.columns(len(PROFILE["metrics"]))
for c, (v, l) in zip(cols, PROFILE["metrics"]):
    with c:
        st.markdown(f'<div class="glass metric"><div class="v">{v}</div><div class="l">{l}</div></div>',
                    unsafe_allow_html=True)

# ---------- Skills ----------
pills = "".join(f'<span class="pill">{s}</span>' for s in PROFILE["skills"])
st.markdown(f'<div style="margin:1.1rem 0 .2rem">{pills}</div>', unsafe_allow_html=True)

# ---------- Signature highlights ----------
st.markdown('<div class="sec-h">Signature impact</div>', unsafe_allow_html=True)
rows = [HIGHLIGHTS[i:i+3] for i in range(0, len(HIGHLIGHTS), 3)]
for row in rows:
    cols = st.columns(3)
    for c, (icon, title, desc, src) in zip(cols, row):
        with c:
            glass(f'<div class="hl"><div class="ic">{icon}</div>'
                  f'<div class="t">{title}</div><div class="d">{desc}</div>'
                  f'<div class="src" style="margin-top:.5rem">{src}</div></div>')

# ---------- Experience ----------
st.markdown('<div class="sec-h">Experience</div>', unsafe_allow_html=True)
for e in PROFILE["experience"]:
    bullets = "".join(f'<div class="bullet">{b}</div>' for b in e["bullets"])
    glass(
        f'<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:.4rem">'
        f'<div><span style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:1.15rem">{e["org"]}</span>'
        f'<span style="color:#c4b5ff;font-size:.95rem"> · {e["role"]}</span></div>'
        f'<div style="color:#9AA6CC;font-size:.82rem">{e["dates"]}</div></div>'
        f'<div style="color:#aab4d6;font-size:.9rem;margin:.4rem 0 .5rem;line-height:1.5">{e["blurb"]}</div>'
        f'{bullets}')

# ---------- App launcher ----------
st.markdown('<div class="sec-h">Apps & Tools</div>', unsafe_allow_html=True)
st.caption("Majority Lifesciences & Healthcare · some cross-sector. Each tool takes inputs and returns insight — no setup required.")

for section, apps in CATALOG.items():
    st.markdown(f'<div class="sub-h">{section}</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for c, (icon, name, desc, sector, page) in zip(cols, apps):
        with c:
            pill_cls = "pill-hc" if sector == "LS&HC" else "pill-x"
            live = "" if page else '<div style="color:#6f7aa0;font-size:.68rem;margin-top:.35rem">Coming soon</div>'
            glass(
                f'<div class="app-card"><div class="ic">{icon}</div>'
                f'<div class="nm" style="font-size:.9rem">{name}</div>'
                f'<div class="ds">{desc}</div>'
                f'<div style="margin-top:.45rem"><span class="pill {pill_cls}">{sector}</span></div>{live}</div>')
            if page:
                st.page_link(f"pages/{page}.py", label="Open →")

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
st.caption(f"© {PROFILE['name']} · {PROFILE['email']} · Built with Streamlit")
