# Studio Rebuild Plan — 25 shallow apps → 15 deep "suites"

> Durable plan so work can resume across sessions. Read this first when continuing.
> Repo: /Users/vandanasharma/Downloads/Claude/aman-ai · venv: .venv · live: https://aman-bhatnagar-studio.streamlit.app/

## Goal & principles
- **3 apps per section (5×3 = 15).** Each app is a *suite* with **subsections (tabs)** that merge several of the old 25.
- **Real working prototypes:** upload data → get numbers → play with interactive levers.
- **Researched upload schemas:** every data app has a CSV template with **REQUIRED** and **OPTIONAL** columns, clear descriptions, and an **identifier** (e.g. NPI / HCP ID / contract ID) so outputs are actionable on named records.
- **Actionable output:** every analysis ends in an **action plan by tier** (e.g. High/Med/Low risk, or Target A/B/C) with a **downloadable targeted list that includes the identifier**.
- Keep the existing glassmorphism look, KPIs, plotly dark charts, board-ready summaries.

## The 15 suites (with merge mapping from the old 25)

### Section 1 — Commercial & GTM Strategy
- **1A · GTM & Market-Entry Strategy** — tabs: Route-to-Market · Market Prioritization · ROI Business Case. (merges old 1 GTM Builder)
- **1B · Sales Force Design & IC Suite** — tabs: Segmentation · Targeting · Sizing (workload build-up) · Structure & Alignment · Incentive Comp. (merges old 6 Sales Force Sizer + 8 Incentive Comp + new segmentation/targeting) **← PROTOTYPE (built first)**
- **1C · Pricing & Business Model Lab** — tabs: Pricing Corridor · Business Model Simulator · Value-based pricing. (merges old 7 Business Model + 9 Pricing/Market-Entry)

### Section 2 — Transactions & M&A
- **2A · Synergy & Deal Value Suite** — Cost synergies · Revenue synergies · Phasing · Planned-vs-actual tracker. (merges old 2 Synergy + 13 Deal Value Tracker)
- **2B · M&A Target Screener** — Target universe upload · Weighted scorecard · Ranking · Portfolio map. (old 10, enriched upload)
- **2C · Integration & Separation Suite** — Day-1 OM readiness · Carve-out / stranded cost · TSA mapping. (merges old 11 Day-1 + 12 Carve-out)

### Section 3 — Transformation & Value Creation
- **3A · Cost & Org Redesign Suite** — Cost takeout by lever · Spans & layers / de-layering · Org-roster upload. (merges old 3 Cost Takeout + 16 Spans & Layers)
- **3B · Operating Model Benchmark** — Diagnostic vs benchmark across dimensions. (old 15, enriched)
- **3C · Value Creation Planning** — EBITDA bridge · Initiative prioritization & roadmap (upload initiatives). (merges old 14 EBITDA + 17 Value Roadmap)

### Section 4 — Lifesciences & Healthcare Analytics
- **4A · HCP Engagement & Churn Suite** — Churn/retention prediction (NPI) · Omni-channel optimization · Next-best-action plan by risk tier. (merges old 4 HCP Churn + 18 Omni-channel) **← 2nd prototype (healthcare, NPI + tiered actions)**
- **4B · Payer & Reimbursement Suite** — Payer-contract profitability (CPT-level) · Medicare Advantage value. (merges old 19 Payer + 20 Medicare Advantage)
- **4C · Market Access & Sizing** — TAM/SAM/SOM · forecast & scenario. (old 21 Market Sizer, enriched)

### Section 5 — AI Decision Tools & Thought Leadership
- **5A · Aman's AI Agent** — frameworks chat (offline + optional key). (old 5)
- **5B · Strategy Toolkit** — Issue-tree / hypothesis · Scenario & sensitivity · Executive storyline. (merges old 23 + 24 + 25)
- **5C · MedTech Trends & Insights** — curated trends explorer. (old 22)

## Upload schemas (researched; REQUIRED vs OPTIONAL)
Convention: identifier is always REQUIRED. Optional columns unlock extra features but never block the run.

**1B Sales Force Design & IC — HCP/Account universe**
- REQUIRED: `hcp_id` (NPI or internal id — identity spine), `specialty`, `geo` (territory/ZIP/region), `potential` (Rx potential units or market value), `current_volume` (TRx/NRx or current sales)
- OPTIONAL: `decile` (1–10; else derived from potential), `taxonomy_code` (e.g. 207RE0101X), `behavior_segment` (loyalist/spreader/adopter), `access` (high/med/low/no-see), `current_calls`, `competitor_share`, `email_engagement`
- Sizing = workload build-up: Σ(reach×frequency by tier) ÷ rep capacity (selling days × calls/day). IC = payout curve (threshold/target/excellence + accelerator + cap) over a goal-attainment distribution.
- Action plan by **Target tier A/B/C**: call frequency, channel mix, do/don't — downloadable list **with hcp_id**.

**4A HCP Engagement & Churn — prescriber panel**
- REQUIRED: `hcp_id` (NPI), `rx_trend` (% change — trajectory, needs ≥2 periods), `current_volume` (or decile)
- OPTIONAL: `specialty`, `geo`, `calls_per_qtr`, `email_engagement`, `samples_used`, `tenure_months`, `competitor_share`, `tickets_open`, `payer_friction`
- Output: churn risk % + tier per NPI; **action plan by risk tier** (High = senior-rep save play on named NPIs; Med = nurture; Low = maintain); downloadable targeted list **with NPI**.

**4B Payer & Reimbursement — contract lines**
- REQUIRED: `contract_id`/`payer`, `service` (CPT/DRG or service line), `encounters`, `contracted_rate`, `cost_per_unit`
- OPTIONAL: `expected_rate`, `paid_rate` (underpayment), `denial_rate`, `days_to_pay`, `place_of_service`
- Output: margin by CPT/contract, loss-makers, **renegotiation target list with $ at stake**.

**2B M&A Target Screener — target universe**
- REQUIRED: `target`, scoring inputs `strategic_fit`,`financial`,`synergy`,`risk`,`market` (0–100)
- OPTIONAL: `revenue`,`ebitda_margin`,`growth`,`asking_price`
**3A Cost & Org — org roster**
- REQUIRED: `role`/`employee_id`, `layer`, `manager_id`; OPTIONAL: `function`, `cost`, `location`, `span`
**3C Value Creation — initiatives**
- REQUIRED: `initiative`, `value_m`, `effort`(1–10), `months_to_impact`; OPTIONAL: `owner`, `category`, `confidence`

## Shared building blocks
- `lib/uploads.py` — extended so `Col(..., required=False)` marks optional columns; template includes them; validation errors only on missing REQUIRED.
- `lib/actions.py` — `render_tiered_actions(df, id_col, value_col, tier_defs, ...)`: assigns tiers, renders summary cards + per-tier action cards, and offers a downloadable targeted list **including the identifier** per tier.

## Phased roadmap (each phase is self-contained & resumable)
- **Phase A — ✅ DONE:** extended `lib/uploads.py` (required/optional) + `lib/actions.py` + built **1B Sales Force Design & IC Suite** (`pages/26`) with **context-aware stage sidebar** (per-step controls + `locked_panel` showing upstream params). Pattern: `st.sidebar.radio` stage selector + `st.session_state` param dict so values persist across steps.
- **Phase B — ✅ DONE:** built **4A HCP Engagement & Churn Suite** (`pages/27`, NPI-keyed ML scoring + tiered action lists + omni-channel) and **4B Payer & Reimbursement Suite** (`pages/28`, CPT-level contract profitability + Medicare Advantage). Both use the stage-sidebar pattern. Lowered `churn_model` intercept to -1.6 (base churn ~31%, AUC ~0.84) for realistic demo risk.
- **TESTING NOTE:** AppTest stops at `st.page_link` (url_pathname KeyError) — so to test page BODIES, monkeypatch `streamlit.page_link = lambda *a,**k: None` BEFORE AppTest, then check `at.exception` (no filtering needed). This caught real bugs (duplicate plotly_chart IDs → add `key=`; itertuples on cols with spaces → use iterrows).
- **Phase C:** finish Section 1 — **1A GTM & Market-Entry** and **1C Pricing & Business Model Lab**; then **4C Market Access & Sizing**.
- **Phase D:** Section 2 — **2A, 2B, 2C**.
- **Phase E:** Section 3 — **3A, 3B, 3C**.
- **Phase F:** Section 5 — **5A, 5B, 5C**; then restructure Home `CATALOG` to the final 15, archive the superseded old `pages/1..25` into `legacy_pages/` (outside `pages/` so the sidebar is clean), final polish + redeploy.

## How to verify (every phase)
Use Streamlit's AppTest (curl gives false 200s — it serves the same shell for any route):
```
.venv/bin/python -c "from streamlit.testing.v1 import AppTest; \
 at=AppTest.from_file('pages/<FILE>.py',default_timeout=40).run(); \
 print([str(e.message) for e in at.exception if 'url_pathname' not in str(e.message)] or 'CLEAN')"
```
(`url_pathname` errors are an AppTest-only artifact of `st.page_link` and can be ignored.)

## Conventions (unchanged)
Page header via `page_header`; sidebar inputs; KPI row `<div class="glass metric">`; `st.tabs` for subsections; plotly `template="plotly_dark"`, transparent bg, accents #8B6CFF/#22D3EE; board-ready `glass(...)` summary; CSV downloads; caption ends with `PROFILE['email']`. Tune demo defaults so headline KPIs look compelling. Footer labels numbers as directional heuristics.
