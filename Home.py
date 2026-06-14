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
        <div style="margin-top:1rem">
          <a class="cta-btn" href="#apps-tools">Explore the apps ↓</a>
          <span style="display:inline-block;width:.6rem"></span>
          <a class="cta-btn" style="background:rgba(255,255,255,.07);box-shadow:none;border:1px solid rgba(255,255,255,.18)" href="mailto:{PROFILE['email']}">Get in touch</a>
        </div>
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

# ---------- About / approach ----------
st.markdown('<div class="sec-h">How I work</div>', unsafe_allow_html=True)
glass(f'<div style="font-size:.98rem;line-height:1.75;color:#dfe5fb">{PROFILE["about"]}</div>')
fcols = st.columns(len(PROFILE["focus"]))
for c, (icon, title, desc) in zip(fcols, PROFILE["focus"]):
    with c:
        glass(f'<div class="ic">{icon}</div>'
              f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:.92rem;margin:.3rem 0 .2rem">{title}</div>'
              f'<div style="color:#aab4d6;font-size:.8rem;line-height:1.45">{desc}</div>')

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

# ---------- Education & recognition ----------
ecol1, ecol2 = st.columns([1, 1.6])
with ecol1:
    st.markdown('<div class="sec-h">Education</div>', unsafe_allow_html=True)
    sch, deg, yr = PROFILE["education"]
    glass(f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:1.1rem">{sch}</div>'
          f'<div style="color:#c4b5ff;font-size:.9rem">{deg}</div>'
          f'<div style="color:#9AA6CC;font-size:.8rem;margin-top:.2rem">{yr}</div>')
with ecol2:
    st.markdown('<div class="sec-h">Recognition</div>', unsafe_allow_html=True)
    rec = "".join(f'<div class="bullet">{r}</div>' for r in PROFILE["recognition"])
    glass(rec)

# ---------- App launcher ----------
st.markdown('<div class="sec-h" id="apps-tools">Apps & Tools</div>', unsafe_allow_html=True)
live_count = sum(1 for apps in CATALOG.values() for *_, p in apps if p)
st.caption(f"{live_count} live · 25 planned. Majority Lifesciences & Healthcare, some cross-sector. "
           "Each tool takes inputs and returns insight — no setup, runs in your browser. Click any live card to open it.")

def card_html(icon, name, desc, sector, page):
    pill_cls = "pill-hc" if sector == "LS&HC" else "pill-x"
    badge = ('<div style="color:#22D3EE;font-size:.68rem;margin-top:.35rem;font-weight:600">● Live · open →</div>'
             if page else '<div style="color:#6f7aa0;font-size:.68rem;margin-top:.35rem">Coming soon</div>')
    inner = (f'<div class="glass app-card"><div class="ic">{icon}</div>'
             f'<div class="nm" style="font-size:.9rem">{name}</div>'
             f'<div class="ds">{desc}</div>'
             f'<div style="margin-top:.45rem"><span class="pill {pill_cls}">{sector}</span></div>{badge}</div>')
    if page:
        slug = page.split("_", 1)[1]   # Streamlit URL slug (filename without numeric prefix)
        return f'<a class="cardlink" target="_self" href="{slug}">{inner}</a>'
    return inner

for section, apps in CATALOG.items():
    st.markdown(f'<div class="sub-h">{section}</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for c, (icon, name, desc, sector, page) in zip(cols, apps):
        with c:
            st.markdown(card_html(icon, name, desc, sector, page), unsafe_allow_html=True)

st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
st.caption(f"© {PROFILE['name']} · {PROFILE['email']} · Built with Streamlit")
