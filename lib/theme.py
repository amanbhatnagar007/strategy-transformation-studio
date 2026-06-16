"""Shared theme: premium glassmorphism CSS + reusable UI helpers for the Studio."""
import base64
from pathlib import Path
import streamlit as st

_ASSETS = Path(__file__).resolve().parent.parent / "assets"

GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root { --accent:#8B6CFF; --accent2:#22D3EE; --ink:#EAF0FF; --muted:#9AA6CC; }

html { scroll-behavior: smooth; }
html, body, [class*="css"]  { font-family:'Inter',sans-serif; }

.hero-headline { font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:600; line-height:1.35;
  color:#fff; margin:.7rem 0 0; max-width:640px;
  background: linear-gradient(92deg,#fff,#d7ccff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

/* Closing CTA band */
.cta-band { text-align:center; padding:2.4rem 1rem; border-radius:24px;
  background: linear-gradient(120deg, rgba(139,108,255,.18), rgba(34,211,238,.12));
  border:1px solid rgba(255,255,255,.12); backdrop-filter: blur(14px); }
.cta-band-h { font-family:'Space Grotesk',sans-serif; font-size:1.7rem; font-weight:700; color:#fff;
  background: linear-gradient(92deg,#fff,#bfb0ff,#22D3EE); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.cta-band-s { color:#c3ccec; font-size:1rem; margin-top:.5rem; }

/* Animated aurora background */
.stApp {
  background:
    radial-gradient(900px 520px at 8% -8%, rgba(139,108,255,.30), transparent 60%),
    radial-gradient(820px 460px at 105% 4%, rgba(34,211,238,.20), transparent 55%),
    radial-gradient(700px 700px at 50% 120%, rgba(236,72,153,.14), transparent 60%),
    linear-gradient(180deg,#080B16 0%, #070A14 100%);
  background-attachment: fixed;
}

/* Frosted glass cards */
.glass {
  position:relative;
  background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.03));
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 20px;
  padding: 1.15rem 1.3rem;
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 10px 34px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.glass:hover { transform: translateY(-4px); border-color: rgba(139,108,255,.6);
  box-shadow: 0 16px 44px rgba(139,108,255,.22), inset 0 1px 0 rgba(255,255,255,.08); }

/* Hero */
.hero-name { font-family:'Space Grotesk',sans-serif; font-size: 2.5rem; font-weight: 700;
  letter-spacing:-1px; margin:0; line-height:1.05;
  background: linear-gradient(92deg,#fff 10%,#c9bcff 55%,#22D3EE 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-sub { font-family:'Space Grotesk',sans-serif; color:#cdd6f5; font-weight:500; font-size:1.15rem; margin:.15rem 0 0; }
.hero-tag { color: var(--accent2); font-size:.95rem; margin:.5rem 0 0; letter-spacing:.04em; text-transform:uppercase; }
.hero-summary { color:#c3ccec; margin:.8rem 0 0; max-width:640px; line-height:1.65; font-size:.97rem; }

/* Photo ring */
.photo-wrap { display:flex; justify-content:center; align-items:center; }
.photo-ring {
  width:188px; height:188px; border-radius:50%; padding:5px;
  background: conic-gradient(from 180deg, #8B6CFF, #22D3EE, #EC4899, #8B6CFF);
  box-shadow: 0 0 38px rgba(139,108,255,.5);
  animation: spin 9s linear infinite;
}
.photo-ring img { width:100%; height:100%; border-radius:50%; object-fit:cover;
  border:4px solid #0a0e1c; background:#0a0e1c; animation: spin 9s linear infinite reverse; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Pills */
.pill { display:inline-block; padding:5px 13px; border-radius:999px; font-size:.74rem; font-weight:500;
  border:1px solid rgba(255,255,255,.16); color:#cfd6ee; margin:3px 7px 3px 0; background:rgba(255,255,255,.05); }
.pill-hc { border-color: rgba(34,211,238,.55); color:#9beaf6; background:rgba(34,211,238,.08); }
.pill-x  { border-color: rgba(139,108,255,.55); color:#c4b5ff; background:rgba(139,108,255,.08); }

/* Metrics */
.metric { text-align:center; display:flex; flex-direction:column; justify-content:center; min-height:92px; }
.metric .v { font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:700; line-height:1.1;
  background: linear-gradient(90deg,#fff,#b9a6ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.metric .l { font-size:.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; margin-top:.3rem; }

/* Section heading */
.sec-h { font-family:'Space Grotesk',sans-serif; font-size:1.25rem; font-weight:600; color:#fff;
  margin:1.8rem 0 .7rem; display:flex; align-items:center; gap:.55rem; }
.sec-h::before { content:""; width:9px; height:9px; border-radius:50%;
  background:linear-gradient(135deg,#8B6CFF,#22D3EE); box-shadow:0 0 12px #8B6CFF; }
.sub-h { font-size:1rem; font-weight:600; color:#dfe5fb; margin:1.3rem 0 .5rem; opacity:.95; }

/* Highlight + app cards */
.hl .ic, .app-card .ic { font-size:1.5rem; }
.hl .t { font-family:'Space Grotesk',sans-serif; font-weight:600; color:#fff; font-size:1.02rem; margin:.3rem 0 .2rem; }
.hl .d { color:#aab4d6; font-size:.83rem; line-height:1.45; }
.hl .src { color:#8B6CFF; font-size:.7rem; font-weight:600; letter-spacing:.05em; }
.app-card .nm { font-family:'Space Grotesk',sans-serif; font-weight:600; color:#fff; margin:.35rem 0 .15rem; }
.app-card .ds { color:var(--muted); font-size:.8rem; }

.bullet { color:#c3ccec; font-size:.86rem; line-height:1.5; margin:.28rem 0; padding-left:1.1rem; position:relative; }
.bullet::before { content:"▸"; position:absolute; left:0; color:#22D3EE; }

.block-container { padding-top: 2rem; max-width: 1140px; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
section[data-testid="stSidebar"] { background: rgba(10,14,28,.7); backdrop-filter: blur(10px); }

/* Clickable app card link */
a.cardlink { text-decoration:none !important; display:block; color:inherit; }
a.cardlink:hover .glass { transform: translateY(-4px); border-color: rgba(139,108,255,.6);
  box-shadow: 0 16px 44px rgba(139,108,255,.22), inset 0 1px 0 rgba(255,255,255,.08); }
.cta-btn { display:inline-block; text-decoration:none !important; font-family:'Space Grotesk',sans-serif;
  font-weight:600; font-size:.95rem; color:#fff !important; padding:.7rem 1.5rem; border-radius:14px;
  background: linear-gradient(92deg,#8B6CFF,#22D3EE); box-shadow:0 8px 26px rgba(139,108,255,.4);
  transition: transform .15s ease, box-shadow .15s ease; }
.cta-btn:hover { transform: translateY(-2px); box-shadow:0 12px 32px rgba(34,211,238,.45); }
</style>
"""

def inject():
    st.markdown(GLASS_CSS, unsafe_allow_html=True)

def glass(html: str):
    st.markdown(f'<div class="glass">{html}</div>', unsafe_allow_html=True)

def img_b64(name: str) -> str:
    p = _ASSETS / name
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode()

def locked_panel(items, title="Locked from earlier steps"):
    """Render a read-only sidebar panel of upstream params (list of (label, value))."""
    if not items:
        return
    rows = "".join(
        f'<div style="display:flex;justify-content:space-between;gap:8px;padding:3px 0;border-bottom:1px solid rgba(255,255,255,.06)">'
        f'<span style="color:#9AA6CC;font-size:.78rem">{lbl}</span>'
        f'<span style="color:#cdd6f5;font-size:.78rem;font-weight:500">{val}</span></div>'
        for lbl, val in items)
    st.sidebar.markdown(
        f'<div style="border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:.6rem .7rem;margin-top:.4rem;background:rgba(255,255,255,.03)">'
        f'<div style="color:#fff;font-size:.8rem;font-weight:600;margin-bottom:.3rem">🔒 {title}</div>{rows}</div>',
        unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    inject()
    st.markdown(
        f'<p class="hero-name" style="font-size:1.9rem">{title}</p>'
        f'<p class="hero-summary" style="margin-top:.3rem">{subtitle}</p>', unsafe_allow_html=True)
