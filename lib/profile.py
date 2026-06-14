"""Aman Bhatnagar profile data + the app catalog, used by Home and apps."""

PROFILE = {
    "name": "Aman Bhatnagar",
    "studio": "Strategy & Transformation Studio",
    "tagline": "LS&HC · M&A · GTM · Cross-Sector",
    "summary": (
        "Seasoned Strategy & Business Transformation Leader with 11+ years driving growth, "
        "go-to-market excellence, and enterprise-wide transformation. 100+ high-impact engagements "
        "across Lifesciences & Healthcare (MedTech, Payer/PBM, providers) and select cross-sector work, "
        "delivering ~$1B in cumulative client impact."
    ),
    "email": "amanbhatnagarmrt@gmail.com",
    "metrics": [
        ("11+ yrs", "Experience"),
        ("100+", "Engagements"),
        ("~$1B", "Client impact"),
        ("150+", "Mentored"),
    ],
    "skills": ["Strategy & Operations", "GTM Strategy", "Transactions (M&A)", "Transformation",
               "Commercial Analytics", "Power BI", "SQL", "Python", "R"],
    "experience": [
        ("EY-Parthenon Global", "Director, Strategy & Transaction", "Apr 2022 – Present",
         "Commercial & GTM strategy, M&A, and transformation for global MedTech, Payer/PBM and providers."),
        ("ZS Associates", "Decision Analytics Consultant", "Jul 2015 – Apr 2022",
         "Commercial strategy, salesforce design, omni-channel analytics and M&A for top MedTech & pharma."),
    ],
}

# section -> list of (icon, name, desc, sector, page_file or None)
CATALOG = {
    "Commercial & GTM Strategy": [
        ("🚀", "GTM Strategy Builder", "Product → launch plan & channel mix", "LS&HC", "1_GTM_Strategy_Builder"),
        ("🧭", "Sales Force Sizer", "Reps & accounts → territory design", "LS&HC", None),
        ("📊", "Business Model Simulator", "Capital vs subscription vs pay-per-use", "LS&HC", None),
        ("🎯", "Incentive Comp Designer", "Quota & payout curve design", "LS&HC", None),
        ("🏷️", "Pricing & Market-Entry Planner", "Price corridor & entry mode", "Cross", None),
    ],
    "Transactions & M&A": [
        ("🔗", "Synergy Estimator", "Two firms → revenue & cost synergies", "LS&HC", None),
        ("🔎", "M&A Target Screener", "Weighted scorecard ranking", "LS&HC", None),
        ("🗂️", "Day-1 OM Planner", "Separation readiness checklist", "LS&HC", None),
        ("✂️", "Carve-out Readiness", "Stranded cost & TSA mapping", "Cross", None),
        ("📈", "Deal Value Tracker", "Synergy capture over time", "LS&HC", None),
    ],
    "Transformation & Value Creation": [
        ("🛠️", "Cost Takeout Analyzer", "Org → savings bridge", "LS&HC", None),
        ("💹", "EBITDA Improvement Bridge", "Lever-by-lever margin walk", "LS&HC", None),
        ("📐", "Operating Model Benchmark", "Spans, layers, cost ratios", "LS&HC", None),
        ("🪜", "Spans & Layers Optimizer", "De-layering simulator", "Cross", None),
        ("🗺️", "Value-Creation Roadmap", "Initiative sequencing & ROI", "LS&HC", None),
    ],
    "Lifesciences & Healthcare Analytics": [
        ("🩺", "HCP Churn Predictor", "ML · at-risk physicians", "LS&HC", None),
        ("📡", "Omni-channel Optimizer", "Channel mix → conversion lift", "LS&HC", None),
        ("💵", "Payer Contract Analyzer", "Service mix → profitability", "LS&HC", None),
        ("🏥", "Medicare Advantage Estimator", "Risk capture upside", "LS&HC", None),
        ("📏", "MedTech Market Sizer", "TAM / SAM / SOM (e.g. CGM)", "LS&HC", None),
    ],
    "AI Decision Tools & Thought Leadership": [
        ("🤖", "Aman's AI Agent", "Ask in my frameworks (optional key)", "LS&HC", None),
        ("📰", "2025 MedTech Trends", "Explore trends & implications", "LS&HC", None),
        ("💡", "Hypothesis Generator", "Structured issue trees", "Cross", None),
        ("🎚️", "Scenario Simulator", "Sensitivity & what-ifs", "LS&HC", None),
        ("📝", "Executive Storyline", "Findings → board-ready story", "Cross", None),
    ],
}
