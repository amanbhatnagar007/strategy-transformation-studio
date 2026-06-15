"""Single source of truth for the Studio's information architecture.

The final product is 5 sections x 3 suites = 15. Suites that are already rebuilt point to
their suite file; the rest interim-point to the best existing legacy page until rebuilt.
Both the st.navigation router (Home.py) and the portfolio launcher read this.
"""
import streamlit as st

# section -> list of dicts: icon, title, desc, sector, file, url, built
NAV = {
    "Commercial & GTM Strategy": [
        {"icon": "🧭", "title": "Sales Force Design & IC Suite", "desc": "Upload HCPs → segment, target, size, align, IC",
         "sector": "LS&HC", "file": "pages/26_Sales_Force_Design_Suite.py", "url": "sales-force", "built": True},
        {"icon": "🚀", "title": "GTM & Market-Entry", "desc": "Route-to-market, market prioritization, ROI",
         "sector": "LS&HC", "file": "pages/1_GTM_Strategy_Builder.py", "url": "gtm-market-entry", "built": False},
        {"icon": "🏷️", "title": "Pricing & Business Model Lab", "desc": "Pricing corridor, business-model economics",
         "sector": "Cross", "file": "pages/7_Business_Model_Simulator.py", "url": "pricing-model", "built": False},
    ],
    "Transactions & M&A": [
        {"icon": "🔗", "title": "Synergy & Deal Value Suite", "desc": "Synergies, phasing, capture tracking",
         "sector": "LS&HC", "file": "pages/2_Synergy_Estimator.py", "url": "synergy-deal", "built": False},
        {"icon": "🔎", "title": "M&A Target Screener", "desc": "Weighted scorecard, ranking, portfolio map",
         "sector": "LS&HC", "file": "pages/10_MA_Target_Screener.py", "url": "target-screener", "built": False},
        {"icon": "🗂️", "title": "Integration & Separation Suite", "desc": "Day-1 readiness, carve-out, TSA",
         "sector": "Cross", "file": "pages/11_Day1_OM_Planner.py", "url": "integration-separation", "built": False},
    ],
    "Transformation & Value Creation": [
        {"icon": "🛠️", "title": "Cost & Org Redesign Suite", "desc": "Cost takeout, spans & layers, org chart",
         "sector": "LS&HC", "file": "pages/3_Cost_Takeout_Analyzer.py", "url": "cost-org", "built": False},
        {"icon": "📐", "title": "Operating Model Benchmark", "desc": "Diagnostic vs best-practice benchmarks",
         "sector": "LS&HC", "file": "pages/15_Operating_Model_Benchmark.py", "url": "om-benchmark", "built": False},
        {"icon": "🗺️", "title": "Value Creation Planning", "desc": "EBITDA bridge, initiative roadmap",
         "sector": "LS&HC", "file": "pages/14_EBITDA_Bridge.py", "url": "value-creation", "built": False},
    ],
    "Lifesciences & Healthcare Analytics": [
        {"icon": "🩺", "title": "HCP Engagement & Churn Suite", "desc": "NPI panel → risk, action plan, omni-channel",
         "sector": "LS&HC", "file": "pages/27_HCP_Engagement_Churn_Suite.py", "url": "hcp-engagement", "built": True},
        {"icon": "💵", "title": "Payer & Reimbursement Suite", "desc": "Contract profitability + Medicare Advantage",
         "sector": "LS&HC", "file": "pages/28_Payer_Reimbursement_Suite.py", "url": "payer-reimbursement", "built": True},
        {"icon": "📏", "title": "Market Access & Sizing", "desc": "TAM / SAM / SOM + forecast",
         "sector": "LS&HC", "file": "pages/21_MedTech_Market_Sizer.py", "url": "market-access", "built": False},
    ],
    "AI Decision Tools & Thought Leadership": [
        {"icon": "🤖", "title": "Aman's AI Agent", "desc": "Ask in my frameworks (offline + optional key)",
         "sector": "LS&HC", "file": "pages/5_Aman_AI_Agent.py", "url": "ai-agent", "built": True},
        {"icon": "💡", "title": "Strategy Toolkit", "desc": "Issue trees, scenarios, exec storyline",
         "sector": "Cross", "file": "pages/23_Hypothesis_Generator.py", "url": "strategy-toolkit", "built": False},
        {"icon": "📰", "title": "MedTech Trends & Insights", "desc": "Curated 2025 MedTech POV",
         "sector": "LS&HC", "file": "pages/22_MedTech_Trends.py", "url": "medtech-trends", "built": True},
    ],
}


def build_pages(home_fn):
    """Return the dict for st.navigation: portfolio home (default) + section-grouped suites."""
    pages = {"": [st.Page(home_fn, title="Studio Home", icon="🏠", default=True)]}
    for section, entries in NAV.items():
        pages[section] = [st.Page(e["file"], title=e["title"], icon=e["icon"], url_path=e["url"])
                          for e in entries]
    return pages
