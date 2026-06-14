import streamlit as st
from lib.theme import inject, glass
from lib.profile import PROFILE, CATALOG

st.set_page_config(page_title=f"{PROFILE['name']} — {PROFILE['studio']}",
                   page_icon="🧠", layout="wide")
inject()

# ---------- Hero ----------
st.markdown(
    f"""
    <div class="glass" style="margin-bottom:1rem">
      <p class="hero-name">{PROFILE['name']} <span style="color:#9AA5C4;font-weight:500;font-size:1.1rem">— {PROFILE['studio']}</span></p>
      <p class="hero-tag">{PROFILE['tagline']}</p>
      <p style="color:#cdd5ee;margin:.6rem 0 .2rem;max-width:820px;line-height:1.6">{PROFILE['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- Metrics ----------
cols = st.columns(len(PROFILE["metrics"]))
for c, (v, l) in zip(cols, PROFILE["metrics"]):
    with c:
        st.markdown(f'<div class="glass metric"><div class="v">{v}</div><div class="l">{l}</div></div>',
                    unsafe_allow_html=True)

# ---------- Skills ----------
pills = "".join(f'<span class="pill">{s}</span>' for s in PROFILE["skills"])
st.markdown(f'<div style="margin:1rem 0">{pills}</div>', unsafe_allow_html=True)

# ---------- Experience ----------
st.markdown('<div class="sec-h">Experience</div>', unsafe_allow_html=True)
ecols = st.columns(len(PROFILE["experience"]))
for c, (org, role, dates, desc) in zip(ecols, PROFILE["experience"]):
    with c:
        glass(f'<div style="font-weight:600;color:#fff">{org}</div>'
              f'<div style="color:#c4b5ff;font-size:.9rem">{role}</div>'
              f'<div style="color:#9AA5C4;font-size:.78rem;margin:.2rem 0 .4rem">{dates}</div>'
              f'<div style="color:#cdd5ee;font-size:.85rem;line-height:1.5">{desc}</div>')

# ---------- App launcher ----------
st.markdown('<div class="sec-h">Apps & Tools</div>', unsafe_allow_html=True)
st.caption("Majority Lifesciences & Healthcare · some cross-sector. Each tool takes inputs and returns insight.")

for section, apps in CATALOG.items():
    st.markdown(f'<div class="sec-h" style="font-size:.95rem;opacity:.92">{section}</div>',
                unsafe_allow_html=True)
    cols = st.columns(5)
    for c, (icon, name, desc, sector, page) in zip(cols, apps):
        with c:
            pill_cls = "pill-hc" if sector == "LS&HC" else "pill-x"
            live = "" if page else '<div style="color:#7e88a8;font-size:.7rem;margin-top:.3rem">Coming soon</div>'
            glass(
                f'<div class="app-card"><div class="ic">{icon}</div>'
                f'<div class="nm" style="font-size:.92rem">{name}</div>'
                f'<div class="ds">{desc}</div>'
                f'<span class="pill {pill_cls}" style="margin-top:.4rem">{sector}</span>{live}</div>')
            if page:
                st.page_link(f"pages/{page}.py", label="Open →")

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
st.caption(f"© {PROFILE['name']} · {PROFILE['email']} · Built with Streamlit")
