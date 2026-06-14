# Aman.AI — Super-App Build Plan

## Vision
A single Streamlit web app that is **both a portfolio (your resume) and a launcher for many mini-apps**.
A visitor lands on a polished profile page (who you are, impact, expertise), then explores working
AI tools that demonstrate your functional expertise in Strategy, GTM, M&A, Transformation, and
Lifesciences & Healthcare.

**Brand:** `Aman Bhatnagar — Strategy & Transformation Studio`
**Tagline:** *LS&HC · M&A · GTM · Cross-Sector*
**Profile facts:** 11+ years · 100+ engagements · ~$1B cumulative client impact · 150+ mentored. Majority LS&HC, selective cross-sector.

## App catalog (25 apps = 5 sections x 5)
**1. Commercial & GTM Strategy:** GTM Strategy Builder (LS&HC) · Sales Force Sizer & Territory Designer (LS&HC) · Business Model Simulator (LS&HC) · Incentive Compensation Designer (LS&HC) · Pricing & Market-Entry Planner (Cross)
**2. Transactions & M&A:** Synergy Estimator (LS&HC) · M&A Target Screener (LS&HC) · Day-1 Commercial OM Planner (LS&HC) · Carve-out / Separation Readiness (Cross) · Deal Value-Creation Tracker (LS&HC)
**3. Transformation & Value Creation:** Cost Takeout / Org Redesign (LS&HC) · EBITDA Improvement Bridge (LS&HC) · Operating Model Benchmarking (LS&HC) · Spans & Layers Optimizer (Cross) · Value-Creation Roadmap Builder (LS&HC)
**4. Lifesciences & Healthcare Analytics:** HCP Churn Predictor ML (LS&HC) · Omni-channel Marketing Optimizer (LS&HC) · Payer Contract Profitability (LS&HC) · Medicare Advantage Value Estimator (LS&HC) · MedTech/CGM Market Sizer (LS&HC)
**5. AI Decision Tools & Thought Leadership:** AI Agent / frameworks chat (LS&HC) · 2025 MedTech Trends Explorer (LS&HC) · Strategy Hypothesis Generator (Cross) · Scenario / Sensitivity Simulator (LS&HC) · Executive Storyline Generator (Cross)

## Hard constraint: runs for anyone, no install
- Deployed free on **Streamlit Community Cloud** via your GitHub (already authed as amanbhatnagar007).
- Pure-Python dependencies only (`requirements.txt`). **No Ollama / no local model install for visitors.**
- AI is delivered in three offline tiers:
  1. **Deterministic AI** — your consulting frameworks as code (scorecards, optimizers, formulas).
  2. **Real ML (offline)** — scikit-learn models trained on bundled synthetic data (churn, segmentation).
  3. **Optional LLM** — a "paste your own API key" box unlocks narrative/chat features; never required.

## Architecture (Streamlit multipage)
```
aman-ai/
  Home.py                      # Portfolio landing + app launcher
  pages/
    1_GTM_Strategy_Builder.py
    2_Sales_Force_Sizer.py
    3_Business_Model_Simulator.py
    4_Synergy_Estimator.py
    5_HCP_Churn_Predictor.py
    6_Payer_Contract_Analyzer.py
    7_Medicare_Advantage_Estimator.py
    8_MedTech_Market_Sizer.py
    9_Aman_AI_Agent.py
  lib/                         # shared logic (models, frameworks, calculations)
  assets/                      # css (glassmorphism theme), images, resume PDF
  data/                        # bundled sample datasets for ML demos
  .streamlit/config.toml       # theme
  requirements.txt
  README.md
```

## UI/UX approach (modern look within Streamlit)
- Custom CSS injected for a **glassmorphism / frosted-glass** theme: translucent cards, soft shadows,
  gradient background, rounded corners, subtle blur.
- Dark theme by default with accent gradient; large hero, metric cards, app tiles in a grid.
- Each app: clean input panel (left) → results/visuals (right), consistent layout.

## App catalog (finalized)
**Commercial & GTM:** GTM Strategy Builder · Sales Force Sizer & Territory Designer · Business Model Simulator
**M&A:** Synergy Estimator · Day-1 Operating Model Planner · M&A Target Screener
**Transformation:** Cost Takeout / Org Redesign · EBITDA Improvement Calculator
**Lifesciences & Healthcare:** HCP Churn Predictor (ML) · Omni-channel Marketing Optimizer · Payer Contract Profitability · Medicare Advantage Value Estimator · MedTech Market Sizer
**Showpiece:** Aman.AI Agent (retrieval over your knowledge base; optional-key chat)

## Phased roadmap
- **Phase 1:** Repo + venv + theme + portfolio Home page + 1 flagship app (GTM Strategy Builder) end-to-end. Deploy to Streamlit Cloud → shareable link.
- **Phase 2:** Add 1 app per remaining section (4 more apps).
- **Phase 3:** Fill out catalog + Aman.AI Agent + polish.

## Deployment
Push to GitHub → connect repo on share.streamlit.io → public URL anyone can open.
