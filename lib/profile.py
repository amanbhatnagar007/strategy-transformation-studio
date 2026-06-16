"""Aman Bhatnagar profile data + the app catalog, used by Home and apps."""

PROFILE = {
    "name": "Aman Bhatnagar",
    "studio": "Strategy & Transformation Studio",
    "tagline": "LS&HC · M&A · GTM · Cross-Sector",
    "summary": (
        "Seasoned Strategy & Business Transformation Leader with 11+ years driving growth, "
        "go-to-market excellence, and enterprise-wide transformation. 100+ high-impact engagements "
        "across Lifesciences & Healthcare (MedTech, Payer/PBM, providers) and select cross-sector work, "
        "creating ~$500M of value for clients."
    ),
    "email": "amanbhatnagarmrt@gmail.com",
    "phone": "+91-9811186994",
    "headline": "I turn commercial strategy into measured value creation — ~$500M of it for clients, and counting.",
    "linkedin": "https://in.linkedin.com/in/amanbhatnagarstrategyconsultant",
    "ey_profile": "https://www.ey.com/en_us/people/aman-bhatnagar",
    "video_url": "",  # paste a Loom/YouTube intro URL to show a "Watch 60-sec intro" button
    "resume_file": "Aman_Bhatnagar_Resume.pdf",
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
        ("~$500M", "Client value created"),
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

# Leadership & capability-building strip
LEADERSHIP = [
    ("👥", "40-member team led", "directly, with 80+ guided indirectly at EY-Parthenon"),
    ("🎓", "150+ professionals mentored", "a people-first, capability-building leader"),
    ("🏅", "Certified SFE Trainer", "EY SFE Trainer · ZS IC Design Professional"),
    ("🌍", "US · EMEA · APAC", "delivery across global markets"),
]

# Anonymized case studies (Situation → Action → Result → Role), grounded in real engagements.
CASE_STUDIES = [
    {"tag": "M&A · Consumer/Health", "title": "$3B business separation — market-ready in 9 months",
     "situation": "A $3B unit was being carved out and needed a Day-1 commercial operating model with zero customer disruption.",
     "action": "Designed the Day-1 commercial OM across sales, marketing and support; sequenced readiness and TSA exits.",
     "result": "Both entities went market-ready within 9 months with continuity of customer experience.",
     "role": "Led the commercial separation workstream."},
    {"tag": "Transformation · Healthcare", "title": "~$150M cost improvement, Fortune-500 provider",
     "situation": "A Fortune-500 healthcare client was structurally too tall and too costly to run.",
     "action": "Ran an operating-model assessment — spans, layers, benchmarking and process — to size the takeout.",
     "result": "Identified ~$150M of cost improvement with a phased, self-funding roadmap.",
     "role": "Led the org-redesign and benchmarking analysis."},
    {"tag": "Analytics · Provider/Payer", "title": "+15% profitability via payer-contract analysis",
     "situation": "A large provider couldn't see which payer contracts made or lost money.",
     "action": "Analyzed encounter volumes, service/patient mix and reimbursement rates at the contract level.",
     "result": "Drove a ~15% profitability improvement and stronger payer relationships.",
     "role": "Led the contract-profitability analytics."},
    {"tag": "GTM · MedTech", "title": "~$0.5B growth unlocked for a $10B MedTech client",
     "situation": "A $10B MedTech client's commercial structure was misaligned to its growth opportunity.",
     "action": "Re-architected roles, territories and responsibilities against value and workload.",
     "result": "Unlocked ~$0.5B of growth through a redesigned commercial structure.",
     "role": "Designed the commercial structure & deployment."},
]

# What people say — REPLACE these placeholders with real, attributed recommendations
# (e.g. pulled from LinkedIn). Set to [] to hide the section until you have real ones.
RECOMMENDATIONS = [
    {"quote": "Aman pairs sharp commercial strategy with the rigor to actually quantify it — he reframed the problem and the team rallied behind a plan we could defend to the board.",
     "author": "Senior Partner, EY-Parthenon", "note": "‹ replace with a verified recommendation ›"},
    {"quote": "One of the most effective strategy leaders I've worked with — structured, data-grounded, and relentless about the decision the client actually has to make.",
     "author": "VP Commercial, Global MedTech client", "note": "‹ replace with a verified recommendation ›"},
]

# Thought leadership / external validation
INSIGHTS = [
    {"title": "EY.com author profile — Aman Bhatnagar", "desc": "My published insights & bylines on EY.com",
     "url": "https://www.ey.com/en_us/people/aman-bhatnagar"},
    {"title": "EY Pulse of the MedTech Industry", "desc": "Flagship MedTech report I've contributed to",
     "url": "https://www.ey.com/en_us/life-sciences/pulse-of-medtech-industry-outlook"},
    {"title": "Articles on the CGM market & AI-driven care", "desc": "Commercial models & AI in MedTech (EY.com)",
     "url": "https://www.ey.com/en_us/people/aman-bhatnagar"},
]

# section -> list of (icon, name, desc, sector, page_file or None)
CATALOG = {
    "Commercial & GTM Strategy": [
        ("🧭", "Sales Force Design & IC Suite", "Upload HCPs → segment, target, size, align, IC", "LS&HC", "26_Sales_Force_Design_Suite"),
        ("🚀", "GTM Strategy Builder", "Product → launch plan & channel mix", "LS&HC", "1_GTM_Strategy_Builder"),
        ("📊", "Business Model Simulator", "Capital vs subscription vs pay-per-use", "LS&HC", "7_Business_Model_Simulator"),
        ("🎯", "Incentive Comp Designer", "Quota & payout curve design", "LS&HC", "8_Incentive_Comp_Designer"),
        ("🏷️", "Pricing & Market-Entry Planner", "Price corridor & entry mode", "Cross", "9_Pricing_Market_Entry"),
    ],
    "Transactions & M&A": [
        ("🔗", "Synergy Estimator", "Two firms → revenue & cost synergies", "LS&HC", "2_Synergy_Estimator"),
        ("🔎", "M&A Target Screener", "Weighted scorecard ranking", "LS&HC", "10_MA_Target_Screener"),
        ("🗂️", "Day-1 OM Planner", "Separation readiness checklist", "LS&HC", "11_Day1_OM_Planner"),
        ("✂️", "Carve-out Readiness", "Stranded cost & TSA mapping", "Cross", "12_Carveout_Readiness"),
        ("📈", "Deal Value Tracker", "Synergy capture over time", "LS&HC", "13_Deal_Value_Tracker"),
    ],
    "Transformation & Value Creation": [
        ("🛠️", "Cost Takeout Analyzer", "Org → savings bridge", "LS&HC", "3_Cost_Takeout_Analyzer"),
        ("💹", "EBITDA Improvement Bridge", "Lever-by-lever margin walk", "LS&HC", "14_EBITDA_Bridge"),
        ("📐", "Operating Model Benchmark", "Spans, layers, cost ratios", "LS&HC", "15_Operating_Model_Benchmark"),
        ("🪜", "Spans & Layers Optimizer", "De-layering simulator", "Cross", "16_Spans_Layers_Optimizer"),
        ("🗺️", "Value-Creation Roadmap", "Initiative sequencing & ROI", "LS&HC", "17_Value_Creation_Roadmap"),
    ],
    "Lifesciences & Healthcare Analytics": [
        ("🩺", "HCP Engagement & Churn Suite", "Upload panel (NPI) → risk, action plan, omni-channel", "LS&HC", "27_HCP_Engagement_Churn_Suite"),
        ("💵", "Payer & Reimbursement Suite", "Contract profitability + Medicare Advantage value", "LS&HC", "28_Payer_Reimbursement_Suite"),
        ("📏", "MedTech Market Sizer", "TAM / SAM / SOM (e.g. CGM)", "LS&HC", "21_MedTech_Market_Sizer"),
    ],
    "AI Decision Tools & Thought Leadership": [
        ("🤖", "Aman's AI Agent", "Ask in my frameworks (optional key)", "LS&HC", "5_Aman_AI_Agent"),
        ("📰", "2025 MedTech Trends", "Explore trends & implications", "LS&HC", "22_MedTech_Trends"),
        ("💡", "Hypothesis Generator", "Structured issue trees", "Cross", "23_Hypothesis_Generator"),
        ("🎚️", "Scenario Simulator", "Sensitivity & what-ifs", "LS&HC", "24_Scenario_Simulator"),
        ("📝", "Executive Storyline", "Findings → board-ready story", "Cross", "25_Executive_Storyline"),
    ],
}
