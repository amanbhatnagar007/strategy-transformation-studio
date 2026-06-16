import streamlit as st
import urllib.parse as _u
from pathlib import Path
from lib.theme import inject, glass, img_b64
from lib.profile import PROFILE, HIGHLIGHTS, LEADERSHIP, CASE_STUDIES, RECOMMENDATIONS, INSIGHTS
from lib.nav import NAV, build_pages

_RESUME = Path(__file__).resolve().parent / "assets" / PROFILE["resume_file"]
RESUME_BYTES = _RESUME.read_bytes() if _RESUME.exists() else None

GMAIL_LINK = ("https://mail.google.com/mail/?view=cm&fs=1&to=" + PROFILE["email"]
              + "&su=" + _u.quote("Let's work together")
              + "&body=" + _u.quote("Hi Aman,\n\nI came across your Strategy & Transformation Studio and would love to connect about "))
PHONE_DIGITS = PROFILE["phone"].replace("-", "").replace(" ", "")


def render_portfolio():
    st.set_page_config(page_title=f"{PROFILE['name']} — {PROFILE['studio']}",
                       page_icon="🧠", layout="wide")
    inject()

    # ---------- Hero ----------
    left, right = st.columns([1, 2.3], gap="large")
    with left:
        b64 = img_b64("aman.png")
        if b64:
            st.markdown(f'<div class="photo-wrap"><div class="photo-ring">'
                        f'<img src="data:image/png;base64,{b64}"/></div></div>', unsafe_allow_html=True)
    with right:
        st.markdown(
            f"""
            <p class="hero-name">{PROFILE['name']}</p>
            <p class="hero-sub">{PROFILE['studio']}</p>
            <p class="hero-tag">{PROFILE['tagline']}</p>
            <p class="hero-headline">{PROFILE['headline']}</p>
            <p class="hero-summary">{PROFILE['summary']}</p>
            <div style="margin-top:1rem">
              <a class="cta-btn" href="#apps-tools">Explore the apps ↓</a>
              <span style="display:inline-block;width:.6rem"></span>
              <a class="cta-btn" target="_blank" style="background:rgba(255,255,255,.07);box-shadow:none;border:1px solid rgba(255,255,255,.18)" href="{GMAIL_LINK}">✉ Get in touch</a>
            </div>
            """, unsafe_allow_html=True)

    # ---------- Quick links: résumé / LinkedIn / EY / video ----------
    bcols = st.columns(4)
    if RESUME_BYTES:
        bcols[0].download_button("⬇ Résumé (PDF)", RESUME_BYTES, file_name=PROFILE["resume_file"],
                                 mime="application/pdf", use_container_width=True)
    bcols[1].link_button("in · LinkedIn", PROFILE["linkedin"], use_container_width=True)
    bcols[2].link_button("EY profile", PROFILE["ey_profile"], use_container_width=True)
    if PROFILE.get("video_url"):
        bcols[3].link_button("▶ 60-sec intro", PROFILE["video_url"], use_container_width=True)

    # ---------- Metrics ----------
    st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
    cols = st.columns(len(PROFILE["metrics"]))
    for c, (v, l) in zip(cols, PROFILE["metrics"]):
        c.markdown(f'<div class="glass metric"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

    # ---------- Leadership & capability ----------
    st.markdown('<div class="sec-h">Leadership & capability</div>', unsafe_allow_html=True)
    lcols = st.columns(len(LEADERSHIP))
    for c, (icon, head, sub) in zip(lcols, LEADERSHIP):
        with c:
            glass(f'<div class="ic">{icon}</div>'
                  f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:.92rem;margin:.3rem 0 .15rem">{head}</div>'
                  f'<div style="color:#aab4d6;font-size:.78rem;line-height:1.4">{sub}</div>')

    # ---------- Skills ----------
    pills = "".join(f'<span class="pill">{s}</span>' for s in PROFILE["skills"])
    st.markdown(f'<div style="margin:1.1rem 0 .2rem">{pills}</div>', unsafe_allow_html=True)

    # ---------- Signature highlights ----------
    st.markdown('<div class="sec-h">Signature impact</div>', unsafe_allow_html=True)
    for i in range(0, len(HIGHLIGHTS), 3):
        cols = st.columns(3)
        for c, (icon, title, desc, src) in zip(cols, HIGHLIGHTS[i:i+3]):
            with c:
                glass(f'<div class="hl"><div class="ic">{icon}</div>'
                      f'<div class="t">{title}</div><div class="d">{desc}</div>'
                      f'<div class="src" style="margin-top:.5rem">{src}</div></div>')

    # ---------- Case studies ----------
    st.markdown('<div class="sec-h">Case studies</div>', unsafe_allow_html=True)
    st.caption("Selected engagements — anonymized. Situation → Action → Result → my role.")
    for i in range(0, len(CASE_STUDIES), 2):
        cols = st.columns(2)
        for c, cs in zip(cols, CASE_STUDIES[i:i+2]):
            with c:
                glass(f'<span class="pill pill-hc">{cs["tag"]}</span>'
                      f'<div style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:1.02rem;margin:.45rem 0 .35rem">{cs["title"]}</div>'
                      f'<div style="color:#9AA6CC;font-size:.82rem;margin:.15rem 0"><b style="color:#c4b5ff">Situation.</b> {cs["situation"]}</div>'
                      f'<div style="color:#9AA6CC;font-size:.82rem;margin:.15rem 0"><b style="color:#c4b5ff">Action.</b> {cs["action"]}</div>'
                      f'<div style="color:#cdd6f5;font-size:.82rem;margin:.15rem 0"><b style="color:#22D3EE">Result.</b> {cs["result"]}</div>'
                      f'<div style="color:#7e88a8;font-size:.76rem;margin-top:.35rem">{cs["role"]}</div>')

    # ---------- How I work ----------
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
        glass(f'<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:.4rem">'
              f'<div><span style="font-family:Space Grotesk;font-weight:600;color:#fff;font-size:1.15rem">{e["org"]}</span>'
              f'<span style="color:#c4b5ff;font-size:.95rem"> · {e["role"]}</span></div>'
              f'<div style="color:#9AA6CC;font-size:.82rem">{e["dates"]}</div></div>'
              f'<div style="color:#aab4d6;font-size:.9rem;margin:.4rem 0 .5rem;line-height:1.5">{e["blurb"]}</div>{bullets}')

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
        glass("".join(f'<div class="bullet">{r}</div>' for r in PROFILE["recognition"]))

    # ---------- Recommendations ----------
    if RECOMMENDATIONS:
        st.markdown('<div class="sec-h">What people say</div>', unsafe_allow_html=True)
        rcols = st.columns(len(RECOMMENDATIONS))
        for c, rec in zip(rcols, RECOMMENDATIONS):
            with c:
                note = (f'<div style="color:#7e88a8;font-size:.7rem;margin-top:.45rem">{rec["note"]}</div>'
                        if rec.get("note") else "")
                glass(f'<div style="font-size:1.6rem;color:#8B6CFF;line-height:.6">“</div>'
                      f'<div style="font-family:var(--font-serif),Georgia,serif;color:#dfe5fb;font-size:.92rem;line-height:1.55;font-style:italic">{rec["quote"]}</div>'
                      f'<div style="color:#c4b5ff;font-size:.82rem;font-weight:600;margin-top:.5rem">— {rec["author"]}</div>{note}')

    # ---------- Insights / thought leadership ----------
    st.markdown('<div class="sec-h">Insights & thought leadership</div>', unsafe_allow_html=True)
    st.caption("Published points of view and reports on EY.com.")
    icols = st.columns(len(INSIGHTS))
    for c, ins in zip(icols, INSIGHTS):
        with c:
            st.markdown(
                f'<a class="cardlink" target="_blank" href="{ins["url"]}">'
                f'<div class="glass app-card"><div class="ic">📄</div>'
                f'<div class="nm" style="font-size:.9rem">{ins["title"]}</div>'
                f'<div class="ds">{ins["desc"]}</div>'
                f'<div style="color:#22D3EE;font-size:.68rem;margin-top:.35rem;font-weight:600">Read on EY.com ↗</div></div></a>',
                unsafe_allow_html=True)

    # ---------- App launcher (from NAV: 5 sections x 3 suites) ----------
    st.markdown('<div class="sec-h" id="apps-tools">Apps & Tools</div>', unsafe_allow_html=True)
    st.caption("15 suites across 5 sections. Each suite has subsections inside — segment, size, score, plan. "
               "Majority Lifesciences & Healthcare, some cross-sector. Click any card to open it.")

    def card(e):
        pill_cls = "pill-hc" if e["sector"] == "LS&HC" else "pill-x"
        badge = ('<div style="color:#22D3EE;font-size:.68rem;margin-top:.35rem;font-weight:600">● Suite · open →</div>'
                 if e["built"] else '<div style="color:#9aa6cc;font-size:.68rem;margin-top:.35rem;font-weight:600">● Open →</div>')
        inner = (f'<div class="glass app-card"><div class="ic">{e["icon"]}</div>'
                 f'<div class="nm" style="font-size:.92rem">{e["title"]}</div>'
                 f'<div class="ds">{e["desc"]}</div>'
                 f'<div style="margin-top:.45rem"><span class="pill {pill_cls}">{e["sector"]}</span></div>{badge}</div>')
        return f'<a class="cardlink" target="_self" href="/{e["url"]}">{inner}</a>'

    for section, entries in NAV.items():
        st.markdown(f'<div class="sub-h">{section}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for c, e in zip(cols, entries):
            with c:
                st.markdown(card(e), unsafe_allow_html=True)

    # ---------- Closing CTA ----------
    st.markdown('<div style="height:2.4rem"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="cta-band">
          <div class="cta-band-h">Let's build your next wave of impact.</div>
          <div class="cta-band-s">Strategy, GTM, M&A and transformation for healthcare &amp; beyond — with the tools to prove it.</div>
          <div style="margin-top:1.1rem">
            <a class="cta-btn" target="_blank" href="{GMAIL_LINK}">✉ Email me</a>
            <span style="display:inline-block;width:.6rem"></span>
            <a class="cta-btn" style="background:rgba(255,255,255,.08);box-shadow:none;border:1px solid rgba(255,255,255,.2)" href="tel:{PHONE_DIGITS}">📞 {PROFILE['phone']}</a>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div style="height:1.2rem"></div>', unsafe_allow_html=True)
    st.caption(f"© {PROFILE['name']} · {PROFILE['email']} · {PROFILE['phone']} · Built with Streamlit")


# ---------- Router with collapsible section nav ----------
pages = build_pages(render_portfolio)
pg = st.navigation(pages, position="hidden")
with st.sidebar:
    st.page_link(pages[""][0], label="Studio Home", icon="🏠")
    st.markdown('<div style="color:#8b95ba;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;'
                'margin:.5rem 0 .2rem">Suites</div>', unsafe_allow_html=True)
    active_url = getattr(pg, "url_path", None)
    for section, plist in pages.items():
        if not section:
            continue
        is_active = any(getattr(p, "url_path", "") == active_url for p in plist)
        with st.expander(section, expanded=is_active):
            for p in plist:
                st.page_link(p)
    st.divider()
pg.run()
