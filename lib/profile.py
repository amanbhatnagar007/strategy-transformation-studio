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
    "about": (
        "I help healthcare and lifesciences leaders answer their hardest commercial questions — "
        "how to enter a market, where to play, how to take a product to market, what an acquisition is "
        "really worth, and how to transform the operating model to fund growth. I work the way the best "
        "consulting teams do: hypothesis-led, data-grounded, and relentlessly focused on the decision the "
        "CXO actually has to make. This studio turns the frameworks I use on engagements into interactive "
        "tools anyone can run."
    ),
    "focus": [
        ("🎯", "Go-to-market & commercial strategy", "Route-to-market, segmentation, salesforce & incentive design"),
        ("🤝", "Transactions (M&A)", "Synergy assessment, commercial due diligence, Day-1 operating models"),
        ("⚙️", "Transformation & value creation", "Cost takeout, org redesign, EBITDA improvement"),
        ("📊", "Commercial analytics & AI", "Churn prediction, omni-channel optimization, decision tooling"),
    ],
    "education": ("Thapar University", "B.E. · 9.3 / 10 CGPA", "2011 – 2015"),
    "recognition": [
        "EY Certified SFE Trainer · ZS Certified IC Design Professional",
        "Published on the CGM market & AI-driven care models on EY.com",
        "Project Championship Award (ZS) for a $3M M&A project",
        "Consistent top performer · multiple SPOT & Best All-rounder awards",
    ],
    "metrics": [
        ("11+ yrs", "Experience"),
        ("100+", "Engagements"),
        ("~$1B", "Client impact"),
        ("150+", "Mentored"),
    ],
    "skills": ["Strategy & Operations", "GTM Strategy", "Transactions (M&A)", "Transformation",
               "Commercial Analytics", "Power BI", "SQL", "Python", "R"],
    "experience": [
        {
            "org": "EY-Parthenon Global",
            "role": "Director, Strategy & Transaction",
            "dates": "Apr 2022 – Present  ·  3.5 yrs",
            "blurb": "Lead commercial & GTM strategy, M&A, and enterprise transformation for global "
                     "MedTech, Payer/PBM and healthcare providers. Run a 40-member team (80+ indirect).",
            "bullets": [
                "Redefined GTM & incentive design for a global MedTech client — 3–5% incremental revenue.",
                "Designed subscription & pay-per-use models now contributing ~10% of a top-20 MedTech's revenue.",
                "Identified ~$100M+ synergies across 6+ Payer & PBM transactions.",
                "Built the Day-1 commercial operating model for a $3B business separation.",
            ],
        },
        {
            "org": "ZS Associates",
            "role": "Decision Analytics Consultant",
            "dates": "Jul 2015 – Apr 2022  ·  7 yrs",
            "blurb": "Commercial strategy, salesforce design, omni-channel analytics and M&A for "
                     "Fortune-20 MedTech & pharma clients.",
            "bullets": [
                "Redesigned commercial structure for a $10B MedTech client — unlocked ~$0.5B growth.",
                "Pioneered the 2025 MedTech Trends publication — $5M opportunities for 5+ Fortune-20 clients.",
                "Built a predictive HCP churn model to trigger timely rep interventions.",
                "Automated quarterly targeting in SQL — cut effort 50%, saving ~$1M over 3 years.",
            ],
        },
    ],
}

# Signature engagements highlighted on the home page
HIGHLIGHTS = [
    ("🏥", "$3B business separation", "Designed the Day-1 commercial operating model — market-ready across both entities in 9 months.", "EY"),
    ("💊", "$100M+ M&A synergies", "Across 6+ Payer & PBM deals via pharmacy service models and class-of-trade pricing.", "EY"),
    ("📈", "$0.5B growth unlocked", "Re-architected the commercial structure of a $10B MedTech client.", "ZS"),
    ("🔁", "Pay-per-use models", "New business models now ~10% of a top-20 MedTech's total revenue.", "EY"),
    ("🩺", "+15% provider profitability", "Smarter payer-contract decisions via encounter & reimbursement analysis.", "EY"),
    ("📰", "2025 MedTech Trends", "Authored thought leadership showcased on the global stage and EY.com.", "ZS"),
]

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
        ("🔗", "Synergy Estimator", "Two firms → revenue & cost synergies", "LS&HC", "2_Synergy_Estimator"),
        ("🔎", "M&A Target Screener", "Weighted scorecard ranking", "LS&HC", None),
        ("🗂️", "Day-1 OM Planner", "Separation readiness checklist", "LS&HC", None),
        ("✂️", "Carve-out Readiness", "Stranded cost & TSA mapping", "Cross", None),
        ("📈", "Deal Value Tracker", "Synergy capture over time", "LS&HC", None),
    ],
    "Transformation & Value Creation": [
        ("🛠️", "Cost Takeout Analyzer", "Org → savings bridge", "LS&HC", "3_Cost_Takeout_Analyzer"),
        ("💹", "EBITDA Improvement Bridge", "Lever-by-lever margin walk", "LS&HC", None),
        ("📐", "Operating Model Benchmark", "Spans, layers, cost ratios", "LS&HC", None),
        ("🪜", "Spans & Layers Optimizer", "De-layering simulator", "Cross", None),
        ("🗺️", "Value-Creation Roadmap", "Initiative sequencing & ROI", "LS&HC", None),
    ],
    "Lifesciences & Healthcare Analytics": [
        ("🩺", "HCP Churn Predictor", "ML · at-risk physicians", "LS&HC", "4_HCP_Churn_Predictor"),
        ("📡", "Omni-channel Optimizer", "Channel mix → conversion lift", "LS&HC", None),
        ("💵", "Payer Contract Analyzer", "Service mix → profitability", "LS&HC", None),
        ("🏥", "Medicare Advantage Estimator", "Risk capture upside", "LS&HC", None),
        ("📏", "MedTech Market Sizer", "TAM / SAM / SOM (e.g. CGM)", "LS&HC", None),
    ],
    "AI Decision Tools & Thought Leadership": [
        ("🤖", "Aman's AI Agent", "Ask in my frameworks (optional key)", "LS&HC", "5_Aman_AI_Agent"),
        ("📰", "2025 MedTech Trends", "Explore trends & implications", "LS&HC", None),
        ("💡", "Hypothesis Generator", "Structured issue trees", "Cross", None),
        ("🎚️", "Scenario Simulator", "Sensitivity & what-ifs", "LS&HC", None),
        ("📝", "Executive Storyline", "Findings → board-ready story", "Cross", None),
    ],
}
