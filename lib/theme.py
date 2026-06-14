"""Shared theme: glassmorphism CSS + reusable UI helpers for the Studio."""
import streamlit as st

GLASS_CSS = """
<style>
:root { --accent:#7C5CFF; --accent2:#22D3EE; --ink:#E8ECF5; --muted:#9AA5C4; }

/* Gradient app background */
.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(124,92,255,.22), transparent 60%),
    radial-gradient(1000px 500px at 110% 10%, rgba(34,211,238,.16), transparent 55%),
    linear-gradient(180deg, #0B1020 0%, #0A0E1C 100%);
  background-attachment: fixed;
}

/* Frosted glass cards */
.glass {
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  padding: 1.1rem 1.25rem;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 8px 30px rgba(0,0,0,.25);
  transition: transform .15s ease, border-color .15s ease;
}
.glass:hover { transform: translateY(-3px); border-color: rgba(124,92,255,.55); }

.hero-name { font-size: 2.0rem; font-weight: 700; letter-spacing:-.5px; margin:0;
  background: linear-gradient(90deg,#fff,#c9bcff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero-tag { color: var(--muted); font-size: 1.0rem; margin:.25rem 0 0; }

.pill { display:inline-block; padding:4px 12px; border-radius:999px; font-size:.72rem;
  border:1px solid rgba(255,255,255,.18); color:#cfd6ee; margin:2px 6px 2px 0; background:rgba(255,255,255,.04); }
.pill-hc { border-color: rgba(34,211,238,.5); color:#9beaf6; }
.pill-x  { border-color: rgba(124,92,255,.5); color:#c4b5ff; }

.metric { text-align:center; }
.metric .v { font-size:1.7rem; font-weight:700; color:#fff; }
.metric .l { font-size:.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; }

.sec-h { font-size:1.05rem; font-weight:600; color:#fff; margin:1.4rem 0 .5rem;
  border-left:3px solid var(--accent); padding-left:.6rem; }

.app-card { height:100%; }
.app-card .ic { font-size:1.4rem; }
.app-card .nm { font-weight:600; color:#fff; margin:.35rem 0 .15rem; }
.app-card .ds { color:var(--muted); font-size:.8rem; }

/* tighten default spacing */
.block-container { padding-top: 2.2rem; max-width: 1100px; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
</style>
"""

def inject():
    st.markdown(GLASS_CSS, unsafe_allow_html=True)

def glass(html: str):
    st.markdown(f'<div class="glass">{html}</div>', unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    inject()
    st.markdown(
        f'<p class="hero-name" style="font-size:1.5rem">{title}</p>'
        f'<p class="hero-tag">{subtitle}</p>', unsafe_allow_html=True)
